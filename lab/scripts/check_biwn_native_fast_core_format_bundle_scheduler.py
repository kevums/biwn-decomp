"""Target compiled scheduler vs native original trap/RTE and ordered memory.

Synchronous stable-RAM native CPU fixtures compare full state. Separate
Unicorn supervisor prefixes test changing read queues and bus order before
RTE (Unicorn is not the RTE/full-SR oracle). IRQ/cycle equivalence unclaimed.
"""
from datetime import datetime,timezone
from pathlib import Path
import argparse,json,os,subprocess,random
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_scheduler as sched
import check_biwn_task_removal as removal
from check_biwn_native_button_digit import ROOT,sha,save
BASE=0x140000;STOP=sched.STOP
ORIGINAL_RANGES=[(0xde08,0xde5c),(0xdeb6,0xdee2),(0xdf60,0xdf6c),(0xdf7a,0xdf7c)]

def end_ssp(case):return case['ssp']+(6 if case['entry']in[0xde08,0xdeb6]else 0)
def private(a,w,case):return end_ssp(case)-0x1000<=a and a+w<=end_ssp(case)-6
def normalize(ram,reference,case,length):
    data=bytearray(ram);data[BASE:BASE+length]=reference[BASE:BASE+length]
    for a in [0xde08,0xdeb6]:data[a:a+6]=reference[a:a+6]
    top=end_ssp(case);data[top-0x1000:top-6]=reference[top-0x1000:top-6]
    return data
def native(n,image,case,length,symbols,original):
    n.device.seed(image,0);l=n.lib;l.m68k_pulse_reset();l.m68k_set_irq(0)
    l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,case['ssp']);l.m68k_set_reg(17,0);l.m68k_set_reg(15,case['usp']);l.m68k_set_reg(17,case['sr'])
    for i,v in enumerate(case['registers']):l.m68k_set_reg(i,v)
    l.m68k_set_reg(16,case['entry']);steps=[];cycles=0;rte=0xde5a if original else symbols['biwn_native_scheduler_rte']
    for _ in range(20000):
        pc=l.m68k_get_reg(None,16)
        if STOP<=pc<STOP+0x20:break
        allowed=any(lo<=pc<hi for lo,hi in ORIGINAL_RANGES)if original else(BASE<=pc<BASE+length or any(lo<=pc<hi for lo,hi in [(0xde08,0xde0e),(0xdeb6,0xdebc),(0xdf60,0xdf6c),(0xdf7a,0xdf7c)]))
        assert allowed,hex(pc);steps.append(pc);cycles+=l.m68k_execute(1)
        if pc==rte and case['entry']in[0xde08,0xdeb6]:break
    else:raise AssertionError('Scheduler did not reach selected continuation')
    cpu=dict(registers=[l.m68k_get_reg(None,i)for i in range(16)],PC=l.m68k_get_reg(None,16),SR=l.m68k_get_reg(None,17))
    cpu['usp']=n.prefix[16]if cpu['SR']&0x2000 else cpu['registers'][15];cpu['ssp']=cpu['registers'][15]if cpu['SR']&0x2000 else n.prefix[17]
    return n.device.ram(),cpu,steps,cycles
def trace(image,case,length,symbols,original):
    script=sched.cleanup.Script(image,case);u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000);u.mem_map(0,0x200000);u.mem_write(0,bytes(script.memory))
    for reg,v in zip(sched.cleanup.REGS,case['registers']):u.reg_write(reg,v)
    u.reg_write(UC_M68K_REG_SR,case['sr']);u.reg_write(UC_M68K_REG_A7,case['registers'][15]);u.reg_write(UC_M68K_REG_CR_USP,case['usp'])
    stop=0xde5a if original else symbols['biwn_native_scheduler_rte'];steps=[]
    def code(e,a,w,_):
        assert any(lo<=a<hi for lo,hi in ORIGINAL_RANGES)if original else(BASE<=a<BASE+length or a in [0xde08,0xdeb6]),hex(a)
        steps.append(a)
    def read(e,t,a,w,v,_):
        if not private(a,w,case):e.mem_write(a,script.read(a,w).to_bytes(w,'big'))
    def write(e,t,a,w,v,_):
        if not private(a,w,case):script.write(a,w,v&((1<<(8*w))-1))
    u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write)
    u.emu_start(case['entry'],stop,count=20000,timeout=2000000);assert u.reg_read(UC_M68K_REG_PC)==stop
    return script.trace,bytes(u.mem_read(0,0x200000)),steps
def cases():
    rows=sched.cases()+removal.cases()
    # Both handlers across all CCR values and selected user/supervisor SR,
    # with explicit unsigned wraparound boundary and expired/equal deadlines.
    rng=random.Random(0xde08deb6)
    for entry in [0xde08,0xdeb6]:
        base=next(x for x in rows if x['entry']==entry and len(x.get('contexts',[]))>=3)if entry==0xdeb6 else next(x for x in rows if x['entry']==entry and x['kind']=='scheduler_3'and any(a==0x101016 for a,w,v in x['initial']))
        for mode in [0,0x2000]:
            for ccr in range(32):
                q={**base,'read_queues':[],'initial':list(base['initial']),'registers':[rng.getrandbits(32)for _ in range(16)],'sr':0x2000|ccr}
                q['registers'][15]=q['ssp']
                # Every possible selected node gets the requested target SR.
                nodes=base.get('contexts',[0x100000,0x101000])
                for node in nodes:q['initial'].append([node+20,2,mode|ccr])
                rows.append(q)
    return rows
def main():
    p=argparse.ArgumentParser();p.add_argument('--limit',type=int);p.add_argument('--bundle',action='store_true');args=p.parse_args()
    global BASE
    if args.bundle:BASE=0x15edc0
    author_path=ROOT/'verification/local-native-scheduler-current.json';author=json.loads(author_path.read_text());source=Path(author['candidate']);assert sha(source)==author['candidate_sha256']
    name='native-fast-core-format-bundle-scheduler'if args.bundle else'native-scheduler';out=ROOT/'verification'/name/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),limit=args.limit,source_accepted=False,game_frames=0,whole_game_complete=False,author_proof=str(author_path),author_proof_sha256=sha(author_path))
    def mark():save(out/'protocol.json',state);save(ROOT/'verification'/(name+'-active.json'),state)
    mark()
    try:
        nsource=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';build=out/'build';stem='native-format-bundle'if args.bundle else'native-scheduler'
        cmd=['make','-f','/Users/kevin/Documents/Codex/2026-10-10/i-now-am-using-the-following/outputs/local-ai-lab/verification/native-fast-core-bundle/20261018T220820.261448Z/Makefile'if args.bundle else'Makefile.scheduler','format-bundle'if args.bundle else'scheduler','BUILD='+str(build),'SCHEDULER_SOURCE='+str(source)]
        if args.bundle:cmd += [str(build/'scheduler-yield.bin'),str(build/'scheduler-remove.bin')]
        p=subprocess.run(cmd,cwd=nsource,capture_output=True,text=True);(out/'make.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
        prefix=str(ROOT/'tools/m68k-elf/bin/m68k-elf-');elf=build/(stem+'.elf');binary=build/(stem+'.bin');payload=binary.read_bytes();symbols={}
        assert sha(binary)=='35a80f52ff4bdede73aa8ec84abd8fa94a1e8c2bea9e3c85349318ded41a509a', "Wrong relocated bundle bytes"
        for line in subprocess.check_output([prefix+'nm','--defined-only',str(elf)],text=True).splitlines():
            t=line.split()
            if len(t)==3:symbols[t[2]]=int(t[0],16)
        save(out/'symbols.json',symbols);(out/'disassembly.txt').write_text(subprocess.check_output([prefix+'objdump','-dr',str(elf)],text=True))
        image=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();candidate=bytearray(image);candidate[BASE:BASE+len(payload)]=payload
        for a,name2 in [(0xdf60,'scheduler-yield.bin'),(0xdf7a,'scheduler-remove.bin')]:
            b=(build/name2).read_bytes();assert b==image[a:a+len(b)];candidate[a:a+len(b)]=b
        for a,key in [(0xde08,'biwn_native_scheduler_dispatch'),(0xdeb6,'biwn_native_scheduler_remove')]:candidate[a:a+6]=b'\x4e\xf9'+symbols[key].to_bytes(4,'big')
        vectors=cases();vectors=vectors[:args.limit]if args.limit else vectors;save(out/'fixtures.json',vectors);rows=[];coverage=set();n=sched.Native();state['status']='native_trap_RTE_full_CPU_and_RAM';mark()
        try:
            for i,vector in enumerate(vectors):
                case={**vector,'read_queues':[]};a=sched.cleanup.Script(image,case);b=sched.cleanup.Script(candidate,case)
                left,lc,pcs,cy=native(n,bytes(a.memory),case,len(payload),symbols,True);right,rc,newpcs,newcy=native(n,bytes(b.memory),case,len(payload),symbols,False)
                if lc!=rc or normalize(right,left,case,len(payload))!=left:
                    save(out/'mismatch.json',dict(case=i,parameters=case,original_CPU=lc,compiled_CPU=rc,RAM_differences=[hex(j)for j,(x,y)in enumerate(zip(left,normalize(right,left,case,len(payload))))if x!=y][:32]));raise AssertionError(str(out/'mismatch.json'))
                assert right[BASE:BASE+len(payload)]==payload;coverage.update(pcs)
                rows.append(dict(case=i,entry=hex(case['entry']),CPU=rc,selected_context=int.from_bytes(right[0xc0920:0xc0924],'big'),original_cycles=cy,compiled_cycles=newcy,full_CPU_public_RAM_and_exception_frame_match=True))
                if i%256==0:state['native_cases_completed']=len(rows);mark();print('Native',len(rows),'/',len(vectors),flush=True)
        finally:n.close()
        save(out/'native-results.json',rows);traces=[];state['status']='ordered_memory_with_changing_reads_pre_RTE';mark()
        for i,case in enumerate(vectors):
            if case['entry']not in [0xde08,0xdeb6]:continue
            a,ar,_=trace(image,case,len(payload),symbols,True);b,br,_=trace(bytes(candidate),case,len(payload),symbols,False)
            if a!=b or normalize(br,ar,case,len(payload))!=ar:
                save(out/'trace-mismatch.json',dict(case=i,parameters=case,original=a,compiled=b));raise AssertionError(str(out/'trace-mismatch.json'))
            traces.append(dict(case=i,entry=hex(case['entry']),ordered_public_bus=a,read_queues=case.get('read_queues',[])))
            if len(traces)%128==0:state['trace_cases_completed']=len(traces);mark();print('Trace',len(traces),flush=True)
        save(out/'trace-results.json',traces)
        paths=[Path(__file__),ROOT/'scripts/check_biwn_scheduler.py',ROOT/'scripts/check_biwn_task_removal.py',source,*[nsource/n for n in ['scheduler-shims.S','scheduler-traps.S','scheduler-traps.ld','scheduler.ld','Makefile.scheduler','Makefile']]]
        if args.bundle:paths+=list(nsource.glob('Makefile*'))+list(nsource.glob('*.ld'))+list(nsource.glob('*.S'))+list(nsource.glob('*.c'))+list(nsource.glob('*.h'))
        state.update(status='terminal_native_scheduler_preflight_pass'if args.limit else'terminal_native_scheduler_CPU_RAM_trap_RTE_ordered_bus_pass',native_cases=len(rows),trace_cases=len(traces),entry_case_counts={hex(e):sum(v['entry']==e for v in vectors)for e in [0xde08,0xdf60,0xdeb6,0xdf7a]},original_instruction_locations=len(coverage),original_instruction_coverage=sorted(hex(x)for x in coverage),candidate=str(source),candidate_sha256=sha(source),compiled_binary=str(binary),compiled_binary_sha256=sha(binary),compiled_ELF=str(elf),binary_bytes=len(payload),symbols=symbols,source_accepted=not args.limit,source_sha256={str(p):sha(p)for p in paths},execution_dependencies_sha256={str(p):sha(p)for p in [ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'tools/libbiwn-movement-device.dylib',ROOT/'render-assets/biwn-inventory-baseline.bin']},recorded_at=datetime.now(timezone.utc).isoformat(),scope='Native synchronous IRQ-disabled stableRAM fullD/A/PC/SR/USP/SSP, public2MBRAM and six-byte selected RTE frame. Yield/removal user traps and warm/fresh selected tasks run through real nativeCPU. Separate Unicorn supervisor prefixes compare ordered public reads/writes including changing deadline/clock rereads before RTE. Private supervisor scratch below the original exception frame and new code/entry JMPs excluded from RAM identity. No IRQ concurrency, cycle equivalence, all-blocked idle behavior, bus faults, game frames or physical console claim.')
        mark();save(ROOT/'verification'/(name+'-current.json'),state);print(state['status'],len(rows),len(traces),len(payload),flush=True)
    except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
