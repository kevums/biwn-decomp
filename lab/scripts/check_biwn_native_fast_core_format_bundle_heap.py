"""Target allocator+compactor: full native ABI/device, separate ordered bus.

Native runs execute actual target-compiled copy+emulatedblitter. Unicorn ordered-access runs
use an explicitly scripted E3E0 dependency, with varied caller regs/CCR;
they do not prove the blitter. No host CPU-state owner or game-frame claim.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,os,subprocess,random
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_memory as old
import check_biwn_scheduler as sched
from check_biwn_native_button_digit import ROOT,sha,save
BASE=0x140000;SP=0x1e0000;STOP=0x1f0000
def private(a,w):return SP-0x2000<=a and a+w<=SP
def normalize(ram,reference,length):
    b=bytearray(ram);b[BASE:BASE+length]=reference[BASE:BASE+length]
    for a in [0x15200,0x152a2,0xe3e0,0xe3ee]:b[a:a+6]=reference[a:a+6]
    b[SP-0x2000:SP]=reference[SP-0x2000:SP];return b
def native(n,image,case,length,original):
    n.device.seed(image,1)
    for address in range(0xf02200,0xf022a0,4):
        if address!=0xf02238:n.device.write(address,0)
    l=n.lib;l.m68k_pulse_reset();l.m68k_set_irq(0)
    l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,SP if case['sr']&0x2000 else 0x1fc000)
    l.m68k_set_reg(17,0);l.m68k_set_reg(15,0x1fd000 if case['sr']&0x2000 else SP);l.m68k_set_reg(17,case['sr'])
    for i,v in enumerate(case['incoming']+[SP]):l.m68k_set_reg(i,v)
    l.m68k_set_reg(16,case['entry']);steps=[];cycles=0;calls=[]
    for _ in range(50000):
        pc=l.m68k_get_reg(None,16)
        if pc==STOP:break
        if not original and 0xe3e0<=pc<0xe4aa:assert pc in [0xe3e0,0xe3ee],("original copy body executed",hex(pc))
        assert (0x15200<=pc<0x1545c or 0xe3e0<=pc<0xe4aa)if original else(BASE<=pc<BASE+length or pc in [0x15200,0x152a2]or 0xe3e0<=pc<0xe4aa),hex(pc)
        if pc==0x15200 and case['entry']!=pc:calls.append(['compact'])
        if pc==0xe3e0:
            sp=l.m68k_get_reg(None,15);calls.append(['copy',*[n.device.read(sp+4+i*4,4)for i in range(3)]])
        steps.append(pc);cycles+=l.m68k_execute(1)
    else:raise AssertionError('Native heap routine did not return')
    cpu=dict(registers=[l.m68k_get_reg(None,i)for i in range(16)],PC=l.m68k_get_reg(None,16),SR=l.m68k_get_reg(None,17));cpu['usp']=n.prefix[16]if cpu['SR']&0x2000 else cpu['registers'][15];cpu['ssp']=cpu['registers'][15]if cpu['SR']&0x2000 else n.prefix[17]
    assert cpu['registers'][15]==SP+4
    hardware=[n.device.read(a,4)for a in [0xf02200,0xf02204,0xf0220c,0xf02224,0xf02228,0xf02230,0xf0223c]]
    return n.device.ram(),cpu,steps,cycles,calls,hardware,n.device.stats()
def trace(image,case,length,original):
    script=old.Script(image,case);u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000);u.mem_map(0,0x200000);u.mem_write(0,bytes(script.memory));u.mem_write(0xe3e0,b'\x4e\x75')
    for reg,v in zip(old.world.REGS,case['incoming']):u.reg_write(reg,v)
    u.reg_write(UC_M68K_REG_SR,case['sr']);u.reg_write(UC_M68K_REG_A7,SP)
    def code(e,a,w,_):
        assert (0x15200<=a<0x1545c or a==0xe3e0)if original else(BASE<=a<BASE+length or a in [0x15200,0x152a2,0xe3e0]),hex(a)
        if a==0x15200 and case['entry']!=a:script.trace.append(['compact'])
        if a==0xe3e0:
            sp=e.reg_read(UC_M68K_REG_A7);args=[int.from_bytes(e.mem_read(sp+4+i*4,4),'big')for i in range(3)];script.changed=[];d0=script.call_copy(args,e.reg_read(UC_M68K_REG_D0))
            for addr,width,value in script.changed:e.mem_write(addr,value.to_bytes(width,'big'))
            for reg,value in zip([UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_A0,UC_M68K_REG_A1],[d0,*case['helper_registers']]):e.reg_write(reg,value)
            e.reg_write(UC_M68K_REG_SR,(e.reg_read(UC_M68K_REG_SR)&~0x1f)|case['helper_CCR'])
    def read(e,t,a,w,v,_):
        if not private(a,w):e.mem_write(a,script.read(a,w).to_bytes(w,'big'))
    def write(e,t,a,w,v,_):
        if not private(a,w):script.write(a,w,v&((1<<(w*8))-1))
    u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start(case['entry'],STOP,count=50000,timeout=3000000);assert u.reg_read(UC_M68K_REG_PC)==STOP
    return script.trace,bytes(u.mem_read(0,0x200000)),[u.reg_read(reg)for reg in old.world.REGS]
def vectors(floor):
    cases=[x for x in old.cases()if x['entry']in[0x15200,0x152a2]];rng=random.Random(0x152a215200)
    for x in cases:
        x['sr']=0x2000;x['initial']=[[a,w,floor if v==0x15edc0 else v]for a,w,v in x['initial']]
    base=list(cases)
    chosen=[next(x for x in base if x['entry']==0x152a2 and x['kind']==k)for k in [0,1,2,3,4,5,6,7,8,12]]+[next(x for x in base if x['entry']==0x15200 and x['kind']==k)for k in range(5)]
    for sample in chosen:
        for mode in [0,0x2000]:
            for ccr in range(32):cases.append({**sample,'sr':mode|ccr,'incoming':[rng.getrandbits(32)for _ in range(15)],'initial':list(sample['initial'])})
    ordinary=next(x for x in base if x['entry']==0x152a2 and x['kind']==0)
    for requested in [0x7ffffff0,0x7fffffff,0x80000000,0x80000001,0xffffff00]:
        for mode in [0,0x2000]:
            for ccr in range(32):cases.append({**ordinary,'params':[requested],'sr':mode|ccr,'read_queues':[],'incoming':[rng.getrandbits(32)for _ in range(15)],'initial':old.allocation_initial(0,requested,255),'kind':'raw_signed_request'})
    for available in [0,1,0x7fffffff,0x80000000,0xffffffff]:
        for mode in [0,0x2000]:
            for ccr in range(32):cases.append({**ordinary,'sr':mode|ccr,'read_queues':[],'incoming':[rng.getrandbits(32)for _ in range(15)],'initial':list(ordinary['initial'])+[[0x112d64,4,available]],'kind':'available_counter_flags'})
    for x in cases:
        x['initial']=list(x['initial'])+[[SP,4,STOP]]+[[SP+4+i*4,4,v]for i,v in enumerate(x['params'])]
        x['helper_registers']=[rng.getrandbits(32)for _ in range(3)];x['helper_CCR']=rng.randrange(32)
    return cases
def main():
    p=argparse.ArgumentParser();p.add_argument('--limit',type=int);p.add_argument('--bundle',action='store_true');p.add_argument('--phase',choices=['native','trace','both'],default='both');args=p.parse_args()
    global BASE
    if args.bundle:BASE=0x15edc0
    ap=ROOT/'verification/local-native-heap-current.json';author=json.loads(ap.read_text());sources=author['sources']
    for x in sources.values():assert sha(x['path'])==x['sha256']
    name='native-fast-core-format-bundle-heap'if args.bundle else'native-heap';out=ROOT/'verification'/name/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    state=dict(status='prepared',directory=str(out),pid=os.getpid(),limit=args.limit,phase=args.phase,source_accepted=False,game_frames=0,whole_game_complete=False,author_proof=str(ap),author_proof_sha256=sha(ap))
    def mark():save(out/'protocol.json',state);save(ROOT/'verification'/(name+'-active.json'),state)
    mark()
    try:
        source=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';build=out/'build';stem='native-format-bundle'if args.bundle else'native-heap';command=['make','-f','/Users/kevin/Documents/Codex/2026-10-10/i-now-am-using-the-following/outputs/local-ai-lab/verification/native-fast-core-bundle/20261018T220820.261448Z/Makefile'if args.bundle else'Makefile.heap','format-bundle'if args.bundle else'heap','BUILD='+str(build),'ALLOCATE_SOURCE='+sources['allocate']['path'],'COMPACT_SOURCE='+sources['compact']['path']]
        b=subprocess.run(command,cwd=source,capture_output=True,text=True);(out/'make.log').write_text(b.stdout+b.stderr);assert b.returncode==0,b.stderr
        prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-');elf=build/(stem+'.elf');binary=build/(stem+'.bin');payload=binary.read_bytes();symbols={}
        assert sha(binary)=='35a80f52ff4bdede73aa8ec84abd8fa94a1e8c2bea9e3c85349318ded41a509a', "Wrong relocated bundle bytes"
        for line in subprocess.check_output([prefix+'nm','--defined-only',str(elf)],text=True).splitlines():
            t=line.split()
            if len(t)==3:symbols[t[2]]=int(t[0],16)
        floor=symbols['biwn_native_heap_start'];save(out/'symbols.json',symbols);(out/'disassembly.txt').write_text(subprocess.check_output([prefix+'objdump','-dr',str(elf)],text=True))
        image=bytearray((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes())
        for a in [0x1521c,0x1526c]:assert image[a:a+4]==(0x15edc0).to_bytes(4,'big');image[a:a+4]=floor.to_bytes(4,'big')
        candidate=bytearray(image);candidate[BASE:BASE+len(payload)]=payload
        for a,key in [(0x15200,'biwn_native_heap_compact'),(0x152a2,'biwn_native_heap_allocate')]:candidate[a:a+6]=b'\x4e\xf9'+symbols[key].to_bytes(4,'big')
        for a,key in [(0xe3e0,'biwn_native_copy_source_first'),(0xe3ee,'biwn_native_copy_destination_first')]:candidate[a:a+6]=b'\x4e\xf9'+symbols[key].to_bytes(4,'big')
        cases=vectors(floor)
        if args.limit:cases=[x for e in [0x152a2,0x15200]for x in cases if x['entry']==e][:args.limit]+[x for x in cases if x['entry']==0x15200][:args.limit]
        save(out/'fixtures.json',cases);rows=[];coverage=set()
        if args.phase in ['native','both']:
            n=sched.Native();state['status']='native_full_CPU_RAM_actual_blitter';mark()
            try:
                for i,vector in enumerate(cases):
                    case={**vector,'read_queues':[]};a=old.Script(image,case);b=old.Script(candidate,case)
                    left,lc,pcs,cy,calls,hw,stats=native(n,bytes(a.memory),case,len(payload),True);right,rc,newpcs,newcy,ncalls,nhw,nstats=native(n,bytes(b.memory),case,len(payload),False)
                    if lc!=rc or normalize(right,left,len(payload))!=left or calls!=ncalls or hw!=nhw:
                        save(out/'mismatch.json',dict(case=i,parameters=case,original_CPU=lc,compiled_CPU=rc,original_calls=calls,compiled_calls=ncalls,original_hardware=hw,compiled_hardware=nhw,RAM_differences=[hex(j)for j,(x,y)in enumerate(zip(left,normalize(right,left,len(payload))))if x!=y][:32]));raise AssertionError(str(out/'mismatch.json'))
                    assert right[BASE:BASE+len(payload)]==payload;coverage.update(pcs);rows.append(dict(case=i,entry=hex(case['entry']),CPU=rc,original_cycles=cy,compiled_cycles=newcy,calls=calls,hardware=hw,original_device=stats,compiled_device=nstats,full_CPU_and_public_RAM_hardware_calls_match=True))
                    if i%128==0:state['native_cases_completed']=len(rows);mark();print('Native',len(rows),'/',len(cases),flush=True)
            finally:n.close()
            save(out/'native-results.json',rows)
        traces=[]
        if args.phase in ['trace','both']:
            state['status']='ordered_public_access_scripted_copy_boundary';mark()
            for i,case in enumerate(cases):
                a,ar,regs=trace(bytes(image),case,len(payload),True);b,br,nregs=trace(bytes(candidate),case,len(payload),False)
                if a!=b or normalize(br,ar,len(payload))!=ar or regs!=nregs:
                    save(out/'trace-mismatch.json',dict(case=i,parameters=case,original=a,compiled=b,original_regs=regs,compiled_regs=nregs));raise AssertionError(str(out/'trace-mismatch.json'))
                traces.append(dict(case=i,entry=hex(case['entry']),trace=a,read_queues=case.get('read_queues',[]),scripted_copy_CCR=case['helper_CCR']))
                if i%128==0:state['trace_cases_completed']=len(traces);mark();print('Trace',len(traces),'/',len(cases),flush=True)
            save(out/'trace-results.json',traces)
        paths=[Path(__file__),ROOT/'scripts/check_biwn_memory.py',ROOT/'scripts/check_biwn_scheduler.py',*[Path(x['path'])for x in sources.values()],*[source/n for n in ['heap-native.h','heap-shims.S','heap.ld','Makefile.heap','Makefile']]]
        if args.bundle:paths+=list(source.glob('Makefile*'))+list(source.glob('*.ld'))+list(source.glob('*.S'))+list(source.glob('*.c'))+list(source.glob('*.h'))
        state.update(status='terminal_native_heap_preflight_pass'if args.limit else'terminal_native_heap_CPU_RAM_blitter_and_ordered_access_pass',native_cases=len(rows),trace_cases=len(traces),entry_case_counts={hex(e):sum(x['entry']==e for x in cases)for e in [0x152a2,0x15200]},original_instruction_locations=len(coverage),original_instruction_coverage=sorted(hex(x)for x in coverage),compiled_binary=str(binary),compiled_binary_sha256=sha(binary),compiled_ELF=str(elf),binary_bytes=len(payload),heap_floor=floor,symbols=symbols,source_accepted=not args.limit and args.phase=='both',source_sha256={str(p):sha(p)for p in paths},execution_dependencies_sha256={str(p):sha(p)for p in [ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'tools/libbiwn-movement-device.dylib',ROOT/'render-assets/biwn-inventory-baseline.bin']},recorded_at=datetime.now(timezone.utc).isoformat(),scope='StableRAM/nativeCPU fullD/A/PC/SR/USP/SSP, public2MBRAM, ordered nested compactor/copy args and seven blitter registers with actual target-compiled copy+emulatedblitter. Separate Unicorn public ordered reads/writes/controlled rereads and caller regs use explicit scripted copy effects and varied helperCCR. Private8KBworkingstack/newcode/entryJMPs excluded; originalRTS/arguments included. No IRQ/concurrency/busfault/physical timing/general malformedheap or gameframe proof. Candidate original copy body is forbidden; emulatedCPU/blitter remain providers.')
        mark();save(ROOT/'verification'/(name+'-current.json'),state);print(state['status'],len(rows),len(traces),len(payload),flush=True)
    except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
