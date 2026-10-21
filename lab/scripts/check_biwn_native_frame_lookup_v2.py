"""Whole1AC3Clookup versus original CPU/RAM/publicsave/ordered volatile reads."""
import argparse,json,os,shutil,subprocess
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_native_frame_reference_single_lean as fixtures
from check_biwn_native_resource_release import REGS
from check_biwn_native_button_digit import ROOT,sha,save
Native=fixtures.Native
BASE,ENTRY,END,SP,STOP=0x148000,0x1ac3c,0x1ac68,0x1e0000,0x1f0000
ND=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
def vectors():
    rows=fixtures.vectors()
    return rows
def seed(image,case):return fixtures.seed(image,case)
def normalize(ram,reference,length):
    b=bytearray(ram)
    for lo,hi in [(BASE,BASE+length),(ENTRY,ENTRY+8),(SP-8192,SP-4)]:b[lo:hi]=reference[lo:hi]
    return bytes(b)
def allowed(pc,length,original):return ENTRY<=pc<END if original else pc==ENTRY or BASE<=pc<BASE+length
def trace(image,c,length,original):
    u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000);u.mem_map(0,0x200000);u.mem_write(0,seed(image,c));u.reg_write(UC_M68K_REG_SR,c['sr'])
    for r,v in zip(REGS,c['incoming']+[SP]):u.reg_write(r,v)
    events=[];changes=[];visits=Counter();current=ENTRY;external=dict(c.get('changing_tags',[]))
    def internal(a,w):return SP-8192<=a and a+w<=SP-4 or BASE<=a and a+w<=BASE+length
    def code(e,pc,w,_):
        nonlocal current
        assert allowed(pc,length,original),hex(pc);current=pc;visits[pc]+=1
    def read(e,t,a,w,v,_):
        if internal(a,w):return
        if a in external:
            assert w==2;value=external.pop(a);e.mem_write(a,value.to_bytes(2,'big'));changes.append([current,visits[current],a,w,value])
        events.append(['r',a,w,int.from_bytes(e.mem_read(a,w),'big')])
    def write(e,t,a,w,v,_):
        if not internal(a,w):events.append(['w',a,w,v&((1<<(8*w))-1)])
    u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start(ENTRY,STOP,count=20000);assert u.reg_read(UC_M68K_REG_PC)==STOP
    return bytes(u.mem_read(0,0x200000)),events,changes
def native(n,image,c,length,original,changes=()):
    l=n.lib;n.device.seed(seed(image,c),0);l.m68k_pulse_reset();l.m68k_set_irq(0);supervisor=bool(c['sr']&0x2000)
    l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,SP if supervisor else 0x1ff000);l.m68k_set_reg(17,0);l.m68k_set_reg(15,0x1fe000 if supervisor else SP);l.m68k_set_reg(17,c['sr'])
    for i,v in enumerate(c['incoming']+[SP]):l.m68k_set_reg(i,v)
    l.m68k_set_reg(16,ENTRY);coverage=set();visits=Counter();pending=list(changes);minimum=SP;cycles=0
    for steps in range(20000):
        pc=l.m68k_get_reg(None,16)
        if pc==STOP:break
        assert allowed(pc,length,original),hex(pc);coverage.add(pc);visits[pc]+=1;minimum=min(minimum,l.m68k_get_reg(None,15))
        if pending and [pc,visits[pc]]==pending[0][:2]:_,_,a,w,v=pending.pop(0);n.device.direct(a,w,v)
        cycles+=l.m68k_execute(1)
    else:raise AssertionError('Lookup instruction limit')
    assert not pending,pending;cpu=[l.m68k_get_reg(None,i) for i in range(18)];cpu.extend([n.prefix[16] if supervisor else cpu[15],cpu[15] if supervisor else n.prefix[17]]);assert cpu[15]==SP+4
    return n.device.ram(),cpu,coverage,steps,cycles,minimum
def expected(c):
    wanted=c['wanted'];pattern=c['pattern'];index=0 if pattern in ['first','multiple'] else 35 if pattern=='last' else c['match_index'] if pattern=='at' else 36
    regs=c['incoming']+[SP+4,STOP,(c['sr']&0xffe0)|(4 if c['incoming'][2]==0 else 8 if c['incoming'][2]&0x80000000 else 0)]
    regs[0]=index if index<36 else 0;regs[1]=(regs[1]&0xffff0000)|index;regs[8]=0x15b4a0
    return regs
def main():
    p=argparse.ArgumentParser();p.add_argument('--source',required=True,type=Path);p.add_argument('--limit',type=int);p.add_argument('--no-publish',action='store_true');a=p.parse_args();source=a.source.resolve()
    out=ROOT/'verification/native-frame-lookup'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    state=dict(status='building',pid=os.getpid(),directory=str(out),source=str(source),source_sha256=sha(source),source_accepted=False,game_frames=0,new_training=False,default_promoted=False,whole_game_complete=False)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-frame-lookup-active.json',state)
    mark();n=None
    try:
        paths=[Path(__file__),Path(fixtures.__file__),source,ND/'frame-lookup-shim.S',ND/'Makefile.frame-lookup'];snap=out/'source-snapshot';snap.mkdir()
        for path in paths:shutil.copy2(path,snap/path.name)
        result=subprocess.run(['make','-f',str(ND/'Makefile.frame-lookup'),'frame-lookup','BUILD='+str(out/'build'),'LOOKUP_SOURCE='+str(source)],capture_output=True,text=True);(out/'build.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
        binary=out/'build/frame-lookup.bin';payload=binary.read_bytes();baseline=ROOT/'render-assets/biwn-inventory-baseline.bin';assert sha(baseline)=='f3f70dadee1b6241419da361460208337dbbf9333e2da977144e8c97923a20d3';image=baseline.read_bytes();candidate=bytearray(image);candidate[BASE:BASE+len(payload)]=payload;candidate[ENTRY:ENTRY+8]=b'\x4e\xf9'+BASE.to_bytes(4,'big')+b'\x4e\x71';cases=vectors();cases=cases[:a.limit] if a.limit else cases;save(out/'fixtures.json',cases)
        n=Native();rows=[];dynamic=[];coverage=set();minimum=SP;state.update(status='checking_native_ordered',planned=len(cases));mark()
        def compare(c,index,stable):
            nonlocal minimum
            x=trace(image,c,len(payload),True);y=trace(candidate,c,len(payload),False)
            if x[1]!=y[1] or normalize(y[0],x[0],len(payload))!=x[0]:
                save(out/'ordered-mismatch.json',dict(case=index,parameters=c,original=x[1],candidate=y[1]));raise AssertionError(('Ordered reads/RAM',index))
            left=native(n,image,c,len(payload),True,x[2]);right=native(n,candidate,c,len(payload),False,y[2]);normalized=normalize(right[0],left[0],len(payload))
            if left[1]!=right[1] or normalized!=left[0]:save(out/'mismatch.json',dict(case=index,parameters=c,original_CPU=left[1],compiled_CPU=right[1],RAM_differences=[hex(i) for i,(a,b) in enumerate(zip(left[0],normalized)) if a!=b][:30]));raise AssertionError('Full CPU/RAM')
            if stable:assert right[1][:18]==expected(c),('Independent return contract',index)
            assert right[0][BASE:BASE+len(payload)]==payload;coverage.update(left[2]);minimum=min(minimum,right[5]);return dict(case=index,CPU=right[1],ordered_events=len(x[1]),original_steps=left[3],native_steps=right[3],original_cycles=left[4],native_cycles=right[4],source_read_updates=x[2],compiled_read_updates=y[2])
        for i,c in enumerate(cases):
            rows.append(compare(c,i,True))
            if i%256==0:state['completed']=len(rows);mark();print('Lookup',len(rows),'/',len(cases),flush=True)
        for mode in [0,0x2000]:
            for flags in range(32):
                for kind in range(4):
                    c=dict(wanted=0xffff,pattern='first' if kind==1 else 'last' if kind==2 else 'none',refs=0xa55a,incoming=[0x80000000]*15,sr=mode|flags)
                    c['changing_tags']=[(0x15b4a0,0xffff)] if kind==0 else [(0x15b4a0,0),(0x15b4b0,0xffff)] if kind==1 else [(0x15b52c,0)] if kind==2 else [(0x15b4a8,0xffff)]
                    dynamic.append(compare(c,len(dynamic),False))
        save(out/'results.json',rows);save(out/'changing-tag-results.json',dynamic);prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-');asm=subprocess.check_output([prefix+'objdump','-D','-b','binary','-m','m68k:68000','--start-address='+hex(ENTRY),'--stop-address='+hex(END),str(baseline)],text=True);(out/'original.asm').write_text(asm);locations={int(line.split(':',1)[0].strip(),16) for line in asm.splitlines() if ':' in line and len(line.split('\t'))>=3 and line.split('\t')[2].strip()};assert locations<=coverage
        state.update(status='terminal_native_frame_lookup_preflight_pass' if a.limit else 'terminal_native_frame_lookup_CPU_RAM_ordered_pass',source_accepted=not a.limit,native_cases=len(rows),changing_tag_cases=len(dynamic),ordered_cases=len(rows)+len(dynamic),original_instruction_coverage=[len(locations&coverage),len(locations)],binary=str(binary),binary_sha256=sha(binary),binary_bytes=len(payload),max_private_stack_bytes=SP-minimum,dependencies_sha256={str(p):sha(p) for p in paths},scope='Complete original1AC3C..1AC66 lookup including WORD argument,first-match semantics,ambiguous zero/miss D0,full D/A/PC/SR/USP/SSP,public4byte D2 save and2MBRAM. Separate ordered public reads/writes.256controlled tag updates replayed at exact corresponding load PC visit;no actual IRQ injection. Private8KB below publicsave,entry/code excluded. Coordinator ABI shim handles scalar Ckernel index-or36 return;scalar author provenance belongs to separate receipt. No arbitraryalias/fault/IRQ/timing/linked/disc/gameplay/physical orwhole-game proof.');mark()
        if not a.no_publish and not a.limit:save(ROOT/'verification/native-frame-lookup-current.json',state)
        print(state['status'],len(rows),len(dynamic),len(payload),state['original_instruction_coverage'],flush=True)
    except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
    finally:
        if n:n.close()
if __name__=='__main__':main()
