"""Complete native1AE56 routine versus original CPU/RAM and ordered accesses."""
import argparse,json,os,random,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_native_format_pad as common
from check_biwn_native_resource_release import REGS
from check_biwn_native_button_digit import ROOT,sha,save
Native=common.Native
BASE,ENTRY,END,SP,STOP=0x148000,0x1ae56,0x1ae88,0x1e0000,0x1f0000
def vectors():
    rng=random.Random(ENTRY);rows=[]
    for mode in [0,0x2000]:
        for flags in range(32):
            for wanted in [0,1,0x7fff,0x8000,0xffff]:
                for pattern in ['none','first','last','multiple']:
                    incoming=[rng.getrandbits(32)for _ in range(15)];incoming[2]=[0,1,0x80000000,0xffffffff][(flags+wanted)%4]
                    rows.append(dict(wanted=wanted,pattern=pattern,refs=[0,1,2,0x7fff,0x8000,0xffff][(flags+wanted)%6],incoming=incoming,sr=mode|flags))
    for i in range(96):rows.append(dict(wanted=rng.randrange(65536),pattern='at',match_index=i%36,refs=rng.randrange(65536),incoming=[rng.getrandbits(32)for _ in range(15)],sr=rng.choice([0,0x2000])|rng.randrange(32)))
    return rows
def seed(image,case):
    b=bytearray(image);wanted=case['wanted'];pattern=case['pattern']
    for i in range(36):
        match=pattern in ['first','all']and i==0 or pattern=='last'and i==35 or pattern=='multiple'and i in [0,4,35]or pattern=='at'and i==case['match_index']
        tag=wanted if match else(wanted+1)&0xffff;refs=case.get('refs',1);a=0x15b4a0+i*4;b[a:a+4]=tag.to_bytes(2,'big')+refs.to_bytes(2,'big')
    b[SP:SP+8]=STOP.to_bytes(4,'big')+wanted.to_bytes(2,'big')+b'\xa5\xa5';return bytes(b)
def normalize(ram,ref,length):
    b=bytearray(ram)
    for a,z in [(BASE,length),(ENTRY,8),(SP-8192,8192-4)]:b[a:a+z]=ref[a:a+z]
    return bytes(b)
def native(n,image,case,length,original):
    n.device.seed(seed(image,case),0);l=n.lib;l.m68k_pulse_reset();l.m68k_set_irq(0);supervisor=bool(case['sr']&0x2000)
    l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,SP if supervisor else 0x1ff000);l.m68k_set_reg(17,0);l.m68k_set_reg(15,0x1fe000 if supervisor else SP);l.m68k_set_reg(17,case['sr'])
    for i,v in enumerate(case['incoming']+[SP]):l.m68k_set_reg(i,v)
    l.m68k_set_reg(16,ENTRY);coverage=set();changes=list(case.get('_external_changes',[]))
    for _ in range(10000):
        pc=l.m68k_get_reg(None,16)
        if pc==STOP and l.m68k_get_reg(None,15)==SP+4:break
        assert allowed(pc,length,original),hex(pc)
        if changes and pc==changes[0][0]:_,value=changes.pop(0);n.device.direct(0x15b4a2,2,value)
        coverage.add(pc);l.m68k_execute(1)
    else:raise AssertionError('Single release did not return')
    assert not changes,'Declared changing read was not reached'
    cpu=[l.m68k_get_reg(None,i)for i in range(18)];cpu.extend([n.prefix[16]if supervisor else cpu[15],cpu[15]if supervisor else n.prefix[17]]);ram=n.device.ram();assert original or ram[BASE:BASE+length]==image[BASE:BASE+length]
    return ram,cpu,coverage
def allowed(pc,length,original):return ENTRY<=pc<END if original else pc==ENTRY or BASE<=pc<BASE+length
def trace(image,case,length,original):
    u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000);u.mem_map(0,0x200000);u.mem_write(0,seed(image,case))
    for reg,value in zip(REGS,case['incoming']+[SP]):u.reg_write(reg,value)
    u.reg_write(UC_M68K_REG_SR,case['sr']);u.reg_write(UC_M68K_REG_A7,SP);events=[];queue=list(case.get('read_queue',[1,0]if case.get('changing')else[]));changes=[];current_pc=ENTRY
    def ignored(a,w):return SP-8192<=a and a+w<=SP-4 or BASE<=a and a+w<=BASE+length
    def read(e,access,a,w,v,_):
        if ignored(a,w):return
        if a==0x15b4a2 and w==2 and queue:
            value=queue.pop(0);e.mem_write(a,value.to_bytes(2,'big'));changes.append([current_pc,value])
        events.append(['r',a,w,int.from_bytes(e.mem_read(a,w),'big')])
    def write(e,access,a,w,v,_):
        if not ignored(a,w):events.append(['w',a,w,v&((1<<(w*8))-1)])
    def code(e,a,w,_):
        nonlocal current_pc
        assert allowed(a,length,original),hex(a);current_pc=a
    u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write)
    u.emu_start(ENTRY,STOP,count=10000,timeout=1000000);assert u.reg_read(UC_M68K_REG_PC)==STOP;ram=bytes(u.mem_read(0,0x200000));assert original or ram[BASE:BASE+length]==image[BASE:BASE+length]
    return ram,events,changes
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int);args=parser.parse_args();nd=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
    out=ROOT/'verification/native-frame-reference-single'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),source_accepted=False,game_frames=0,new_training=False,local_model_authored=False,whole_game_complete=False)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-frame-reference-single-active.json',state)
    mark()
    try:
        paths=[Path(__file__),Path(common.__file__),*[nd/name for name in ['frame-reference-single-native.c','frame-reference-single-native.h','frame-reference-single-shim.S','Makefile.frame-reference-single']]];snapshots=out/'source-snapshot';snapshots.mkdir()
        for p in paths:shutil.copy2(p,snapshots/p.name)
        built=subprocess.run(['make','-f',str(nd/'Makefile.frame-reference-single'),'frame-reference-single','BUILD='+str(out/'build')],capture_output=True,text=True);(out/'build.log').write_text(built.stdout+built.stderr);assert built.returncode==0
        binary=out/'build/frame-reference-single.bin';payload=binary.read_bytes();baseline=ROOT/'render-assets/biwn-inventory-baseline.bin';assert sha(baseline)=='f3f70dadee1b6241419da361460208337dbbf9333e2da977144e8c97923a20d3';image=baseline.read_bytes();candidate=bytearray(image);candidate[BASE:BASE+len(payload)]=payload;candidate[ENTRY:ENTRY+8]=b'\x4e\xf9'+BASE.to_bytes(4,'big')+b'\x4e\x71'
        cases=vectors()
        if args.limit:cases=cases[:args.limit]
        save(out/'fixtures.json',cases);n=Native();coverage=set();results=[];traces=0;dynamic=[]
        try:
            for i,case in enumerate(cases):
                a=native(n,image,case,len(payload),True);b=native(n,candidate,case,len(payload),False);normalized=normalize(b[0],a[0],len(payload))
                if a[1]!=b[1]or normalized!=a[0]:save(out/'mismatch.json',dict(case=i,parameters=case,original_CPU=a[1],compiled_CPU=b[1],RAM_differences=[dict(address=hex(k),original=x,compiled=y)for k,(x,y)in enumerate(zip(a[0],normalized))if x!=y][:32]));raise AssertionError('Full CPU/RAM mismatch')
                x=trace(image,case,len(payload),True);y=trace(candidate,case,len(payload),False)
                if x[1]!=y[1]or normalize(y[0],x[0],len(payload))!=x[0]:save(out/'ordered-mismatch.json',dict(case=i,original=x[1],compiled=y[1]));raise AssertionError('Ordered bus/RAM mismatch')
                coverage.update(a[2]);traces+=1;results.append(dict(case=i,CPU=b[1],ordered_events=len(x[1])))
                if i%256==0:state['completed']=len(results);mark();print('Single frame release',len(results),'/',len(cases),flush=True)
            for mode in [0,0x2000]:
                for flags in range(32):
                    for queue in [[1,0],[0,1],[0xffff,0],[0x8000,0xffff]]:
                        case=dict(wanted=0xffff,pattern='first',refs=1,incoming=[0x80000000]*15,sr=mode|flags,read_queue=queue)
                        a=trace(image,case,len(payload),True);b=trace(candidate,case,len(payload),False);assert a[1]==b[1]and normalize(b[0],a[0],len(payload))==a[0]
                        left=native(n,image,dict(case,_external_changes=a[2]),len(payload),True);right=native(n,candidate,dict(case,_external_changes=b[2]),len(payload),False);assert left[1]==right[1]and normalize(right[0],left[0],len(payload))==left[0]
                        assert left[1][17]&16==(16 if len(queue)>1 and queue[0]!=0 and queue[1]==0 else 0),'Wrong X flag for controlled test/RMW race'
                        traces+=1;dynamic.append(dict(mode=mode,CCR=flags,read_queue=queue,ordered_events=a[1],native_CPU=left[1],native_source_read_changes=a[2],native_compiled_read_changes=b[2]))
        finally:n.close()
        save(out/'results.json',results);save(out/'changing-read-cases.json',dynamic);prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-');asm=subprocess.check_output([prefix+'objdump','-D','-b','binary','-m','m68k:68000',f'--start-address={ENTRY}',f'--stop-address={END}',str(baseline)],text=True);(out/'original.asm').write_text(asm)
        expected={int(line.split(':',1)[0].strip(),16)for line in asm.splitlines()if ':'in line and len(line.split('\t'))>=3 and line.split('\t')[2].strip()}
        if not args.limit:assert expected<=coverage,sorted(expected-coverage)
        state.update(status='terminal_native_frame_reference_single_preflight_pass'if args.limit else'terminal_native_frame_reference_single_CPU_RAM_ordered_pass',source_accepted=not args.limit,native_cases=len(results),trace_cases=traces,changing_read_cases=len(dynamic),changing_read_full_native_CPU_cases=len(dynamic),original_instruction_coverage=[len(expected&coverage),len(expected)],binary_bytes=len(payload),compiled_binary=str(binary),compiled_binary_sha256=sha(binary),source_sha256=sha(nd/'frame-reference-single-native.c'),artifacts_sha256={str(p):sha(p)for p in paths},scope='Complete original1AE56 routine compiled for68000;fullD/A/PC/SR/USP/SSP and2MBpublicRAM including original4byte D2 save. All32CCR/two stack modes,first/last/no/multiple matches,negative ID/reference words,and256controlled TST/RMWread variations checked in ordered Unicorn plus full nativeCPU/RAM with declared external updates before the corresponding read instructions. First-match semantics and no negative-ID repair. Private8KBstack,code/entry excluded. No arbitraryalias/fault/IRQ/concurrency/cycles/gameplay/physical/whole-game proof. Coordinator native adaptation,not new local-model authorship or training.')
        mark()
        if not args.limit:save(ROOT/'verification/native-frame-reference-single-current.json',state)
        print(state['status'],len(results),traces,state['original_instruction_coverage'],flush=True)
    except BaseException as error:state.update(status='terminal_failed',error=repr(error));mark();raise
if __name__=='__main__':main()
