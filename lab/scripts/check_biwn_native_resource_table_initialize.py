"""Complete 1AEDA initializer:full native CPU/RAM and ordered WORD writes."""
import json,os,random,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
from check_biwn_scheduler import Native
from check_biwn_native_resource_release import REGS
from check_biwn_native_button_digit import ROOT,sha,save
ENTRY,END,BASE,SP,STOP=0x1aeda,0x1af04,0x148000,0x1e0000,0x1f0000
ND=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
def vectors():
    rng=random.Random(ENTRY);rows=[]
    for variant in range(3):
        for mode in [0,0x2000]:
            for flags in range(32):rows.append(dict(incoming=[rng.getrandbits(32) for _ in range(15)],sr=mode|flags|(variant*3<<8),table=rng.randbytes(600).hex()))
    return rows
def seed(image,c):
    b=bytearray(image);b[SP:SP+4]=STOP.to_bytes(4,'big');b[0x15b534:0x15b534+600]=bytes.fromhex(c['table']);return bytes(b)
def normalize(ram,ref,length):
    b=bytearray(ram)
    for lo,hi in [(BASE,BASE+length),(ENTRY,ENTRY+8),(SP-8192,SP)]:b[lo:hi]=ref[lo:hi]
    return bytes(b)
def allowed(pc,length,original):return ENTRY<=pc<END if original else pc==ENTRY or BASE<=pc<BASE+length
def native(n,image,c,length,original):
    n.device.seed(seed(image,c),0);l=n.lib;l.m68k_pulse_reset();l.m68k_set_irq(0);l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,0x1ff000);l.m68k_set_reg(17,0);l.m68k_set_reg(15,0x1fd000);l.m68k_set_reg(17,c['sr'])
    for i,v in enumerate(c['incoming']+[SP]):l.m68k_set_reg(i,v)
    l.m68k_set_reg(16,ENTRY);coverage=set();cycles=0;minimum=SP
    for steps in range(10000):
        pc=l.m68k_get_reg(None,16)
        if pc==STOP:break
        assert allowed(pc,length,original),hex(pc);coverage.add(pc);minimum=min(minimum,l.m68k_get_reg(None,15));cycles+=l.m68k_execute(1)
    else:raise AssertionError('Initializer instruction limit')
    cpu=[l.m68k_get_reg(None,i) for i in range(18)];cpu += [n.prefix[16] if cpu[17]&0x2000 else cpu[15],cpu[15] if cpu[17]&0x2000 else n.prefix[17]]
    return n.device.ram(),cpu,coverage,steps,cycles,minimum
def trace(image,c,length,original):
    u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000);u.mem_map(0,0x200000);u.mem_write(0,seed(image,c));u.reg_write(UC_M68K_REG_SR,c['sr'])
    for r,v in zip(REGS,c['incoming']+[SP]):u.reg_write(r,v)
    events=[]
    def ignored(a,w):return SP-8192<=a and a+w<=SP or BASE<=a and a+w<=BASE+length
    def code(e,pc,w,_):assert allowed(pc,length,original),hex(pc)
    def read(e,t,a,w,v,_):
        if not ignored(a,w):events.append(['r',a,w,int.from_bytes(e.mem_read(a,w),'big')])
    def write(e,t,a,w,v,_):
        if not ignored(a,w):events.append(['w',a,w,v&((1<<(8*w))-1)])
    u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start(ENTRY,STOP,count=10000);assert u.reg_read(UC_M68K_REG_PC)==STOP
    return bytes(u.mem_read(0,0x200000)),events
def main():
    out=ROOT/'verification/native-resource-table-initialize'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    state=dict(status='building',pid=os.getpid(),directory=str(out),source_accepted=False,game_frames=0,default_promoted=False,new_training=False,local_model_authored=False,whole_game_complete=False)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-resource-table-initialize-active.json',state)
    mark();n=None
    try:
        sources=[Path(__file__),*[ND/name for name in ['resource-table-initialize.c','resource-table-initialize-shim.S','Makefile.resource-table-initialize']]];snap=out/'source-snapshot';snap.mkdir()
        for p in sources:shutil.copy2(p,snap/p.name)
        result=subprocess.run(['make','-f',str(ND/'Makefile.resource-table-initialize'),'resource-table-initialize','BUILD='+str(out/'build')],capture_output=True,text=True);(out/'build.log').write_text(result.stdout+result.stderr);assert result.returncode==0
        binary=out/'build/resource-table-initialize.bin';payload=binary.read_bytes();baseline=ROOT/'render-assets/biwn-inventory-baseline.bin';assert sha(baseline)=='f3f70dadee1b6241419da361460208337dbbf9333e2da977144e8c97923a20d3';image=baseline.read_bytes();candidate=bytearray(image);candidate[BASE:BASE+len(payload)]=payload;candidate[ENTRY:ENTRY+8]=b'\x4e\xf9'+BASE.to_bytes(4,'big')+b'\x4e\x71'
        cases=vectors();save(out/'fixtures.json',cases);n=Native();rows=[];coverage=set();minimum=SP;state['status']='checking_native_and_ordered';mark()
        for i,c in enumerate(cases):
            a=native(n,image,c,len(payload),True);b=native(n,candidate,c,len(payload),False);assert a[1]==b[1] and normalize(b[0],a[0],len(payload))==a[0],('Full CPU/RAM',i)
            expected=c['incoming']+[SP+4,STOP,c['sr']&0xffe0];expected[0]=588;expected[1]=(expected[1]&0xffff0000)|50;expected[8]=0x15b534;assert b[1][:18]==expected,('Independent return contract',i)
            x=trace(image,c,len(payload),True);y=trace(candidate,c,len(payload),False);assert x[1]==y[1] and normalize(y[0],x[0],len(payload))==x[0],('Ordered writes',i)
            expected_writes=[['w',0x15b534+12*j+k,2,value] for j in range(50) for k,value in [(0,0xffff),(6,0),(10,0),(8,0)]];assert [e for e in x[1] if e[0]=='w']==expected_writes
            assert b[0][BASE:BASE+len(payload)]==payload;coverage.update(a[2]);minimum=min(minimum,b[5]);rows.append(dict(case=i,CPU=b[1],original_steps=a[3],native_steps=b[3],original_cycles=a[4],native_cycles=b[4],ordered_WORD_writes=200))
        save(out/'results.json',rows);prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-');asm=subprocess.check_output([prefix+'objdump','-D','-b','binary','-m','m68k:68000','--start-address='+hex(ENTRY),'--stop-address='+hex(END),str(baseline)],text=True);(out/'original.asm').write_text(asm);expected={int(line.split(':',1)[0].strip(),16) for line in asm.splitlines() if ':' in line and len(line.split('\t'))>=3 and line.split('\t')[2].strip()};assert expected<=coverage
        state.update(status='terminal_native_resource_table_initialize_CPU_RAM_ordered_pass',source_accepted=True,native_cases=len(rows),ordered_cases=len(rows),original_instruction_coverage=[len(expected&coverage),len(expected)],binary=str(binary),binary_sha256=sha(binary),binary_bytes=len(payload),max_private_stack_bytes=SP-minimum,dependencies_sha256={str(p):sha(p) for p in sources},scope='Whole original1AEDA..1AF02 initializer versus native68000 C. All D/A/PC/SR/USP/SSP,2MBpublicRAM,192randomized-table/three upperSR profiles/two stack modes/all32CCR cases,200orderedWORDwrites per case. Untouched handle bytes retained. Private8KB below entrySP/new code/entryJMP excluded;original returnaddress read checked. No arbitraryalias/busfault/IRQ/timing/linked/disc/gameplay/physical proof. Coordinator port of already-recovered host algorithm;no new logical function orlocal model authorship/training.');mark();save(ROOT/'verification/native-resource-table-initialize-current.json',state);print(state['status'],len(rows),len(payload),state['original_instruction_coverage'],SP-minimum,flush=True)
    except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
    finally:
        if n:n.close()
if __name__=='__main__':main()
