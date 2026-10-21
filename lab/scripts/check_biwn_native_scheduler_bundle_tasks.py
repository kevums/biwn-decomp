"""New target-compiled task creator vs original native ABI and ordered bus.

Stable-RAM native tests are the full SR/stack-bank oracle. Separate Unicorn
tests vary public read values; Unicorn flags do not prove SR equivalence.
This is an isolated component, not an installed disc or full scheduler.
"""
import argparse, ctypes as c, json, os, random, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_task_create as old
from check_biwn_native_button_digit import ROOT,save,sha
BASE=0x140000;STOP=old.STOP;REGS=old.world.REGS

def private(a,w,case):
    sp=case['registers'][15]
    return sp-0x1000<=a and a+w<=sp

def normalized(ram,reference,case,length):
    data=bytearray(ram);sp=case['registers'][15]
    data[BASE:BASE+length]=reference[BASE:BASE+length]
    data[sp-0x1000:sp]=reference[sp-0x1000:sp]
    return data

def native_run(n,ram,case,entry,length,original):
    n.device.seed(ram,0);l=n.lib;l.m68k_pulse_reset();l.m68k_set_irq(0)
    l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,case['ssp'])
    l.m68k_set_reg(17,0);l.m68k_set_reg(15,case['usp']);l.m68k_set_reg(17,case['sr'])
    for i,v in enumerate(case['registers']):l.m68k_set_reg(i,v)
    l.m68k_set_reg(16,entry);steps=[];cycles=0
    for _ in range(1500):
        pc=l.m68k_get_reg(None,16)
        if pc==STOP:break
        assert (any(lo<=pc<hi for lo,hi in old.RANGES.items()) if original else BASE<=pc<BASE+length or pc==0xdeb4),hex(pc)
        steps.append(pc);cycles+=l.m68k_execute(1)
    else:raise AssertionError('Native task creator did not return/trap')
    cpu=dict(registers=[l.m68k_get_reg(None,i)for i in range(16)],PC=l.m68k_get_reg(None,16),SR=l.m68k_get_reg(None,17))
    cpu['usp']=n.prefix[16]if cpu['SR']&0x2000 else cpu['registers'][15]
    cpu['ssp']=cpu['registers'][15]if cpu['SR']&0x2000 else n.prefix[17]
    result=n.device.ram()
    frame=result[cpu['ssp']:cpu['ssp']+6].hex()if case['no_free']else None
    return result,cpu,steps,cycles,frame

def trace_run(ram,case,entry,length,original):
    script=old.boundary.Script(ram,case)
    u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000);u.mem_map(0,0x200000);u.mem_write(0,bytes(script.memory))
    for reg,value in zip(REGS,case['registers']):u.reg_write(reg,value)
    u.reg_write(UC_M68K_REG_SR,case['sr']);u.reg_write(UC_M68K_REG_A7,case['registers'][15]);steps=[]
    def code(e,a,w,_):
        if a==0xdeb4:e.emu_stop();return
        assert (any(lo<=a<hi for lo,hi in old.RANGES.items())if original else BASE<=a<BASE+length),hex(a)
        steps.append(a)
    def read(e,t,a,w,v,_):
        if private(a,w,case):return
        e.mem_write(a,script.read(a,w).to_bytes(w,'big'))
    def write(e,t,a,w,v,_):
        if private(a,w,case):return
        script.write(a,w,v&((1<<(8*w))-1))
    u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write)
    u.emu_start(entry,STOP,count=1500,timeout=1000000)
    assert u.reg_read(UC_M68K_REG_PC)==(0xdeb4 if case['no_free']else STOP)
    return script.trace,bytes(u.mem_read(0,0x200000)),steps

def vectors():
    cases=old.cases()[:1024]
    for i,case in enumerate(cases):
        delta=(i%8)*2
        def shifted(v):return v+delta if 0x110000<=v<0x114000 else v
        case['initial']=[[shifted(a),w,shifted(v)]for a,w,v in case['initial']]
        case['read_queues']=[{**q,'address':shifted(q['address']),'values':[shifted(v)for v in q['values']]}for q in case['read_queues']]
    # Explicitly cover full CCR and both ABI entries/stack banks, including
    # empty pool exception frames. Nonzero low-word-zero free pointer is the
    # default; alternate addresses cover arbitrary nonzero low words.
    rng=random.Random(0xde5c1400)
    for mode in [0,0x2000]:
        for ccr in range(32):
            for entry in [0xde5c,0xdf6c]:
                for empty in [False,True]:
                    base=cases[(ccr*7)%1024]
                    case={**base,'entry':entry,'sr':mode|ccr,'read_queues':[],'no_free':empty,'initial':list(base['initial']),'registers':[rng.getrandbits(32)for _ in range(16)]}
                    sp=case['ssp']if mode else case['usp'];case['registers'][15]=sp
                    case['initial'] += [[sp,4,STOP],[sp+4,4,rng.getrandbits(32)],[sp+8,4,rng.getrandbits(32)]]
                    if empty:case['initial'].append([0xc0924,4,0])
                    cases.append(case)
    return cases

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);ap.add_argument('--candidate');ap.add_argument('--bundle',action='store_true');opts=ap.parse_args()
    global BASE
    if opts.bundle:BASE=0x15edc0
    author_path=ROOT/'verification/local-native-task-create-repair-current.json'
    if opts.candidate:
        author_path=ROOT/'verification/local-native-task-create-current.json'
    else:
        assert author_path.exists(), 'Wait for the targeted repair result; no fallback to the rejected Author source'
    author=json.loads(author_path.read_text());source=Path(opts.candidate or author['candidate']);assert sha(source)==author['candidate_sha256']
    native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
    name='native-scheduler-bundle-tasks'if opts.bundle else'native-task-create'
    out=ROOT/'verification'/name/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),limit=opts.limit,source_accepted=False,whole_game_complete=False,disc_installed=False,game_frames=0,author_proof=str(author_path),author_proof_sha256=sha(author_path))
    def mark():save(out/'protocol.json',state);save(ROOT/'verification'/(name+'-active.json'),state)
    mark()
    try:
        build=out/'build';cmd=['make','-f','Makefile.scheduler-bundle'if opts.bundle else'Makefile.task-create','scheduler-bundle'if opts.bundle else'task-create','BUILD='+str(build),'TASK_CREATE_SOURCE='+str(source)]
        p=subprocess.run(cmd,cwd=native,capture_output=True,text=True);(out/'build.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
        prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-');stem='native-scheduler-bundle'if opts.bundle else'native-task-create';elf=build/(stem+'.elf');binary=build/(stem+'.bin');payload=binary.read_bytes()
        (out/'disassembly.txt').write_text(subprocess.check_output([prefix+'objdump','-dr',str(elf)],text=True))
        symbols={}
        for line in subprocess.check_output([prefix+'nm','--defined-only',str(elf)],text=True).splitlines():
            t=line.split()
            if len(t)==3:symbols[t[2]]=int(t[0],16)
        save(out/'symbols.json',symbols)
        original=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();candidate=bytearray(original);candidate[BASE:BASE+len(payload)]=payload
        cases=vectors();cases=cases[:opts.limit]+cases[-4:]if opts.limit else cases
        save(out/'fixtures.json',cases);n=old.scheduler.Native();rows=[];coverage=set();state['status']='native_full_CPU_and_RAM';mark()
        try:
            for i,vector in enumerate(cases):
                case={**vector,'read_queues':[]}
                left=old.boundary.Script(original,case);right=old.boundary.Script(candidate,case)
                a,ac,pcs,acycles,af=native_run(n,bytes(left.memory),case,case['entry'],len(payload),True)
                entry=symbols['biwn_native_task_create'if case['entry']==0xde5c else'biwn_native_task_create_stack']
                b,bc,newpcs,bcycles,bf=native_run(n,bytes(right.memory),case,entry,len(payload),False)
                if ac!=bc or normalized(b,a,case,len(payload))!=a or af!=bf:
                    save(out/'mismatch.json',dict(case=i,parameters=case,original_CPU=ac,compiled_CPU=bc,original_frame=af,compiled_frame=bf,RAM_differences=[hex(j)for j,(x,y)in enumerate(zip(a,normalized(b,a,case,len(payload))))if x!=y][:32]));raise AssertionError(str(out/'mismatch.json'))
                assert b[BASE:BASE+len(payload)]==payload;coverage.update(pcs)
                rows.append(dict(case=i,CPU=bc,original_cycles=acycles,compiled_cycles=bcycles,exception_frame=bf,full_CPU_and_public_RAM_match=True))
                if i%256==0:state['native_cases_completed']=len(rows);mark();print('Native',len(rows),'/',len(cases),flush=True)
        finally:n.close()
        save(out/'native-results.json',rows);state['status']='ordered_bus_and_controlled_rereads';mark();traces=[]
        for i,case in enumerate(cases):
            entry=symbols['biwn_native_task_create'if case['entry']==0xde5c else'biwn_native_task_create_stack']
            a,aram,_=trace_run(original,case,case['entry'],len(payload),True);b,bram,_=trace_run(bytes(candidate),case,entry,len(payload),False)
            if a!=b or normalized(bram,aram,case,len(payload))!=aram:
                save(out/'trace-mismatch.json',dict(case=i,parameters=case,original=a,compiled=b));raise AssertionError(str(out/'trace-mismatch.json'))
            traces.append(dict(case=i,ordered_public_bus=a,controlled_read_queues=case.get('read_queues',[])))
            if i%256==0:state['trace_cases_completed']=len(traces);mark();print('Trace',len(traces),'/',len(cases),flush=True)
        save(out/'trace-results.json',traces)
        paths=[Path(__file__),ROOT/'scripts/check_biwn_task_create.py',source,*[native/n for n in ['task-create-shim.S','task-create.ld','Makefile.task-create','Makefile']]]
        if opts.bundle:paths+=list(native.glob('Makefile*'))+list(native.glob('*.ld'))+[native/n for n in ['controller-native.c','controller-lean-shim.S','rng-native.c','rng-native.h','rng-shims.S','rng-fast-math.S','startup-finalize.S','button-digit-movable-shim.S','runtime-original.S']]+[native.parent/'biwn_inventory_select.c',native.parent/'biwn_inventory_select.h']
        state.update(status='terminal_native_task_create_preflight_pass'if opts.limit else'terminal_native_task_create_full_CPU_RAM_exception_and_bus_pass',native_cases=len(rows),trace_cases=len(traces),successful_cases=sum(not x['no_free']for x in cases),empty_pool_exception_cases=sum(x['no_free']for x in cases),original_instruction_locations=len(coverage),original_instruction_coverage=sorted(hex(x)for x in coverage),candidate=str(source),candidate_sha256=sha(source),compiled_binary=str(binary),compiled_binary_sha256=sha(binary),compiled_ELF=str(elf),binary_bytes=len(payload),symbols=symbols,source_sha256={str(p):sha(p)for p in paths},execution_dependencies_sha256={str(p):sha(p)for p in [ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'tools/libbiwn-movement-device.dylib',ROOT/'render-assets/biwn-inventory-baseline.bin']},recorded_at=datetime.now(timezone.utc).isoformat(),scope='Stable-RAM native CPU: full D0-D7/A0-A7/PC/SR/USP/SSP, nonprivate 2MB RAM, and original ILLEGAL exception frame. Ordered public target bus/controlled rereads separately checked in Unicorn. New code window and 4KB private working stack excluded, exception frame checked explicitly. Synchronous IRQ-disabled components only: no timing equivalence, concurrency, game frames, whole scheduler or physical-console proof.')
        state['source_accepted']=not opts.limit
        mark();save(ROOT/'verification'/(name+'-current.json'),state);print(state['status'],len(rows),len(traces),len(payload),flush=True)
    except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
