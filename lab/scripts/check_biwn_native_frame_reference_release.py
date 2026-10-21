"""Compile recovered1AE88 routine and compare full CPU/RAM plus ordered accesses."""
import argparse,json,os,random,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
from check_biwn_native_resource_release import REGS
from check_biwn_scheduler import Native
from check_biwn_native_button_digit import ROOT,sha,save
BASE,ENTRY,END,SP,STOP=0x148000,0x1ae88,0x1aeda,0x1e0000,0x1f0000
def vectors():
    rng=random.Random(ENTRY);rows=[]
    patterns=[(-32768,0,0,'none'),(-1,0xffff,1,'all'),(0,1,1,'all'),(1,2,2,'all'),(0,0x7fff,36,'all'),(0,0x7fff,0x7fff,'all'),(0,32767,36,'alternate'),(0,3,1,'last'),(0,3,36,'duplicate'),(0,3,36,'none'),(0,3,0xffff,'all'),(0,3,0x8000,'all')]
    for srmode in [0,0x2000]:
        for flags in range(32):
            for mode,wanted,count,pattern in patterns:
                incoming=[rng.getrandbits(32)for _ in range(15)];incoming[3]=[0,1,0x80000000,0xffffffff][flags%4]
                rows.append(dict(mode=mode&0xffff,wanted=wanted,count=count,pattern=pattern,incoming=incoming,sr=srmode|flags))
    for _ in range(96):
        rows.append(dict(mode=rng.choice([0,1,32767,32768,65535]),wanted=rng.randrange(65536),count=rng.choice([0,1,2,18,36,32767,32768,65535]),pattern=rng.choice(['all','alternate','last','duplicate','none']),incoming=[rng.getrandbits(32)for _ in range(15)],sr=rng.choice([0,0x2000])|rng.randrange(32)))
    return rows
def seed(image,case):
    b=bytearray(image);wanted=case['wanted'];mode=case['mode'];offset=((mode if mode<32768 else mode-65536)*2)&0xffffffff
    b[0x15b530:0x15b532]=mode.to_bytes(2,'big');address=(0x464a0+offset)&0xffffffff;b[address:address+2]=case['count'].to_bytes(2,'big')
    for i in range(36):
        pattern=case['pattern'];tag=0xffff
        if pattern=='all':tag=(wanted+i)&0xffff
        elif pattern=='alternate'and i%2==0:tag=(wanted+i//2)&0xffff
        elif pattern=='last'and i==35:tag=wanted
        elif pattern=='duplicate':tag=wanted
        refs=[0,1,2,32767,32768,65535][i%6]
        if case.get('changing'):refs=1
        a=0x15b4a0+i*4;b[a:a+4]=tag.to_bytes(2,'big')+refs.to_bytes(2,'big')
    args=STOP.to_bytes(4,'big')+wanted.to_bytes(2,'big')+b'\xa5\xa5';b[SP:SP+len(args)]=args
    return bytes(b)
def normalize(ram,ref,length):
    b=bytearray(ram)
    for a,z in [(BASE,length),(ENTRY,8),(SP-8192,8192-8)]:b[a:a+z]=ref[a:a+z]
    return bytes(b)
def allowed(pc,length,original):return ENTRY<=pc<END if original else pc==ENTRY or BASE<=pc<BASE+length
def native(n,image,case,length,original):
    n.device.seed(seed(image,case),0);l=n.lib;l.m68k_pulse_reset();l.m68k_set_irq(0);supervisor=bool(case['sr']&0x2000)
    l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,SP if supervisor else 0x1ff000);l.m68k_set_reg(17,0);l.m68k_set_reg(15,0x1fe000 if supervisor else SP);l.m68k_set_reg(17,case['sr'])
    for i,v in enumerate(case['incoming']+[SP]):l.m68k_set_reg(i,v)
    l.m68k_set_reg(16,ENTRY);coverage=set()
    for _ in range(10000):
        pc=l.m68k_get_reg(None,16)
        if pc==STOP and l.m68k_get_reg(None,15)==SP+4:break
        assert allowed(pc,length,original),hex(pc);coverage.add(pc);l.m68k_execute(1)
    else:raise AssertionError('Frame reference release did not return')
    cpu=[l.m68k_get_reg(None,i)for i in range(18)];cpu.extend([n.prefix[16]if supervisor else cpu[15],cpu[15]if supervisor else n.prefix[17]]);ram=n.device.ram()
    if not original:assert ram[BASE:BASE+length]==image[BASE:BASE+length]
    return ram,cpu,coverage
def trace(image,case,length,original):
    u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000);u.mem_map(0,0x200000);u.mem_write(0,seed(image,case))
    for reg,value in zip(REGS,case['incoming']+[SP]):u.reg_write(reg,value)
    u.reg_write(UC_M68K_REG_SR,case['sr']);u.reg_write(UC_M68K_REG_A7,SP);events=[];queue=[2,0]if case.get('changing')else[]
    def ignored(a,w):return SP-8192<=a and a+w<=SP-8 or BASE<=a and a+w<=BASE+length
    def read(e,access,a,w,v,_):
        if ignored(a,w):return
        if a==0x15b4a2 and w==2 and queue:e.mem_write(a,queue.pop(0).to_bytes(2,'big'))
        events.append(['r',a,w,int.from_bytes(e.mem_read(a,w),'big')])
    def write(e,access,a,w,v,_):
        if not ignored(a,w):events.append(['w',a,w,v&((1<<(8*w))-1)])
    def code(e,a,w,_):assert allowed(a,length,original),hex(a)
    u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write)
    u.emu_start(ENTRY,STOP,count=10000,timeout=1000000);assert u.reg_read(UC_M68K_REG_PC)==STOP
    ram=bytes(u.mem_read(0,0x200000))
    if not original:assert ram[BASE:BASE+length]==image[BASE:BASE+length]
    return ram,events
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int);args=parser.parse_args();nd=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
    out=ROOT/'verification/native-frame-reference-release'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),source=str(nd/'frame-reference-release-native.c'),source_accepted=False,whole_game_complete=False,game_frames=0,local_model_authored=False,new_training=False)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-frame-reference-release-active.json',state)
    mark()
    try:
        paths=[Path(__file__),*[nd/name for name in ['frame-reference-release-native.c','frame-reference-release-native.h','frame-reference-release-shim.S','Makefile.frame-reference-release']]];snapshots=out/'source-snapshot';snapshots.mkdir()
        for p in paths:shutil.copy2(p,snapshots/p.name)
        command=['make','-f',str(nd/'Makefile.frame-reference-release'),'frame-reference-release','BUILD='+str(out/'build')]
        built=subprocess.run(command,capture_output=True,text=True);(out/'build.log').write_text(built.stdout+built.stderr);assert built.returncode==0
        binary=out/'build/frame-reference-release.bin';payload=binary.read_bytes();baseline=ROOT/'render-assets/biwn-inventory-baseline.bin';assert sha(baseline)=='f3f70dadee1b6241419da361460208337dbbf9333e2da977144e8c97923a20d3'
        image=baseline.read_bytes();candidate=bytearray(image);candidate[BASE:BASE+len(payload)]=payload;candidate[ENTRY:ENTRY+8]=b'\x4e\xf9'+BASE.to_bytes(4,'big')+b'\x4e\x71'
        cases=vectors()
        if args.limit:cases=cases[:args.limit]
        save(out/'fixtures.json',cases);n=Native();coverage=set();results=[];traces=0
        try:
            for i,case in enumerate(cases):
                a=native(n,image,case,len(payload),True);b=native(n,candidate,case,len(payload),False);normalized=normalize(b[0],a[0],len(payload))
                if a[1]!=b[1]or normalized!=a[0]:
                    save(out/'mismatch.json',dict(case=i,parameters=case,original_CPU=a[1],compiled_CPU=b[1],RAM_differences=[dict(address=hex(k),original=x,compiled=y)for k,(x,y)in enumerate(zip(a[0],normalized))if x!=y][:32]));raise AssertionError('Full CPU/RAM mismatch')
                x=trace(image,case,len(payload),True);y=trace(candidate,case,len(payload),False)
                if x[1]!=y[1]or normalize(y[0],x[0],len(payload))!=x[0]:save(out/'ordered-mismatch.json',dict(case=i,original=x[1],compiled=y[1]));raise AssertionError('Ordered bus/RAM mismatch')
                coverage.update(a[2]);traces+=1;results.append(dict(case=i,CPU=b[1],ordered_events=len(x[1])))
                if i%128==0:state['completed']=len(results);mark();print('Frame release',len(results),'/',len(cases),flush=True)
            for sr in [0,16,0x2000,0x201f]:
                case=dict(mode=0,wanted=0,count=1,pattern='all',incoming=[0x80000000]*15,sr=sr,changing=True)
                x=trace(image,case,len(payload),True);y=trace(candidate,case,len(payload),False);assert x[1]==y[1]and normalize(y[0],x[0],len(payload))==x[0];traces+=1
        finally:n.close()
        prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-');asm=subprocess.check_output([prefix+'objdump','-D','-b','binary','-m','m68k:68000',f'--start-address={ENTRY}',f'--stop-address={END}',str(baseline)],text=True);(out/'original.asm').write_text(asm)
        expected={int(line.split(':',1)[0].strip(),16)for line in asm.splitlines()if ':'in line and len(line.split('\t'))>=3 and line.split('\t')[2].strip()}
        if not args.limit:assert expected<=coverage,sorted(expected-coverage)
        save(out/'results.json',results)
        state.update(status='terminal_native_frame_reference_release_preflight_pass'if args.limit else'terminal_native_frame_reference_release_CPU_RAM_ordered_pass',source_accepted=not args.limit,native_cases=len(results),trace_cases=traces,original_instruction_coverage=[len(expected&coverage),len(expected)],binary_bytes=len(payload),compiled_binary=str(binary),compiled_binary_sha256=sha(binary),source_sha256=sha(nd/'frame-reference-release-native.c'),artifacts_sha256={str(p):sha(p)for p in paths},scope='Native68000 compiled complete1AE88routine; fullD/A/PC/SR/USP/SSP and2MB publicRAM including original8byte D3/D2 save. Two stack modes/all32CCR,negativeIDs,negative/zero/positive counts,36slots,matching patterns and signed reference counts. Ordered accesses in Unicorn and4changing TST/RMWread cases. Private8KBstack,code/entry excluded. Stable validRAM; no arbitraryalias/fault/IRQ/concurrency/cycles/gameplay/physical or complete-game proof. Coordinator adaptation, not local-model output or a training gain.')
        mark()
        if not args.limit:save(ROOT/'verification/native-frame-reference-release-current.json',state)
        print(state['status'],len(results),traces,state['original_instruction_coverage'],flush=True)
    except BaseException as error:state.update(status='terminal_failed',error=repr(error));mark();raise
if __name__=='__main__':main()
