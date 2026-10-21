"""Original DD40 setup/render creation/TRAP0 first handoff versus fixed C."""
import ctypes as c,json,os,random,subprocess,hashlib
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_startup_rng_cpu as base
import generate_biwn_system_cpu as gen
ROOT=gen.ROOT;CPU=base.CPU;save=base.save;sha=base.sha
def main():
    out=ROOT/'verification/BIWN-system-source-bootstrap'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);src=ROOT/'projects/black-ice-white-noise/restoration';names=['biwn_system_cpu.c','biwn_actor_factory_cpu.c','biwn_scheduler.c'];library=out/'libsystem-bootstrap.dylib'
    cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror']+[str(src/n)for n in names]+['-o',str(library)];built=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(built.stdout+built.stderr);assert not built.returncode,built.stderr
    lib=c.CDLL(str(library));fn=lib.biwn_system_cpu_body;fn.argtypes=[c.POINTER(base.queue.world.Bus),c.POINTER(CPU),base.queue.cd.dispatch.W8,base.queue.cd.world_cpu.SERVICE,c.c_void_p,c.c_uint32,c.c_int];fn.restype=c.c_int;factory=lib.biwn_actor_factory_cpu_body;factory.argtypes=fn.argtypes;factory.restype=c.c_int;dispatch=lib.biwn_scheduler_dispatch;dispatch.argtypes=[c.POINTER(base.queue.world.Bus),c.POINTER(CPU),c.c_uint32];dispatch.restype=c.c_int
    native=base.queue.cd.scheduler.Native();device=native.device;core=native.lib
    class Oracle:
        pass
    oracle=Oracle();oracle.core=core;oracle.prefix=native.prefix
    oracle.cpu=lambda:base.queue.cd.Runtime.cpu(oracle)
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'system-fullCPU-generation.json').read_text());rows={r['address']:r for r in mapping['instructions_decoded']}
    for a,b in [(0xde5c,0xdeb4),(0xde08,0xde5c)]:rows.update({r['address']:r for r in gen.loader.base.binary_tools.m68k_instructions((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()[a:b],a)[0]})
    snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rng=random.Random(0xdd40c);results=[];coverage=set()
    try:
        for case_id in range(4):
            s=CPU();s.registers[:]=[rng.getrandbits(32)for _ in range(15)]+[0x200000];s.registers[1]=0;s.pc=0xdd40;s.ssp=0x200000;s.usp=0x180000;s.sr=[0x2000,0x2100,0x2700,0x271f][case_id]
            outputs={}
            for mode in ['native','C']:
                device.seed(snapshot,0 if mode=='native'else 1);cpu=CPU.from_buffer_copy(bytes(s));clock_ticks=0;ops=0;errors=[]
                def clock():
                    nonlocal clock_ticks
                    value=device.read(0x778cc,4);device.direct(0x778cc,4,(value+1)&0xffffffff);clock_ticks+=1
                if mode=='native':
                    base.queue.lifecycle.seed_cpu(oracle,cpu)
                    for _ in range(10000):
                        pc=core.m68k_get_reg(None,16)
                        if pc==0x17c40:break
                        assert pc in rows,hex(pc);coverage.add(pc)
                        if pc==0xddd8:clock()
                        core.m68k_execute(1);ops+=1
                    else:raise AssertionError(('native system worklimit',hex(pc)))
                    cpu=oracle.cpu()
                else:
                    def rd(w):
                        def cb(_,a,v):v[0]=device.read(a,w);return 0
                        return cb
                    def wr(w):
                        def cb(_,a,v):device.direct(a,w,v);return 0
                        return cb
                    callbacks=[base.queue.world.R8(rd(1)),base.queue.world.R16(rd(2)),base.queue.world.R32(rd(4)),base.queue.world.W16(wr(2)),base.queue.world.W32(wr(4)),base.queue.cd.dispatch.W8(wr(1))];bus=base.queue.world.Bus(*callbacks[:5],base.queue.world.CALL(),None,0)
                    def service(_,passed,state,target):
                        if target==0xddf2:return fn(passed,state,callbacks[5],callback,None,1000,0)
                        if target==0xde5c:return factory(passed,state,callbacks[5],callback,None,1000,0)
                        if target==0xde08:return dispatch(passed,state,128)
                        errors.append(hex(target));return 1
                    callback=base.queue.cd.world_cpu.SERVICE(service)
                    for _ in range(10000):
                        if cpu.pc==0x17c40:break
                        if cpu.pc==0xddd8:clock()
                        status=fn(c.byref(bus),c.byref(cpu),callbacks[5],callback,None,1,0);assert status in [4,6]and not errors,(status,hex(cpu.pc),errors);ops+=1
                    else:raise AssertionError(('C system worklimit',hex(cpu.pc)))
                final=device.ram();outputs[mode]=dict(CPU=base.queue.cd.scheduler.cpu_dict(cpu),RAM_sha256=sha(final),clock_ticks=clock_ticks)
                (out/f'case-{case_id}-{mode}-RAM.bin').write_bytes(final)
            if outputs['native']!=outputs['C']:save(out/'mismatch.json',outputs);raise AssertionError(str(out/'mismatch.json'))
            get=lambda a:int.from_bytes(final[a:a+4],'big');assert get(0xc0920)==0xc0d28 and get(0xc0924)==0xc1128 and get(0xc0d30)==0x17c40 and get(0xc0938)==0xddec
            results.append(dict(case=case_id,initial_CPU=base.queue.cd.scheduler.cpu_dict(s),first_handoff=outputs['C'],full_CPU_stack_banks_private_RAM_and_source_TRAP_RTE_match=True));save(out/'cases.json',results)
        selected={r['address']for r in mapping['instructions_decoded']};report=dict(status='source_DD40_system_setup_render_creation_TRAP_RTE_first_handoff_native_C_match',directory=str(out),recorded_at=datetime.now(timezone.utc).isoformat(),cases=4,source_instruction_coverage=[len(selected&coverage),len(selected)],uncovered_instructions=[r for r in mapping['instructions_decoded']if r['address']not in coverage],source_freepool_records=100,source_render_context_created=True,initial_context_ring_or_freepool_supplied=False,source_TRAP0_dispatch_RTE_verified=True,all_CPU_SR_USP_SSP_private_2MB_RAM_compared=True,source_sha256={n:sha((src/n).read_bytes())for n in names+[n.replace('.c','.h')for n in names]},script_sha256=sha(Path(__file__).read_bytes()),compiler=cmd,whole_game_complete=False,limits=['Starts at sourceDD40 with supplied FrozenRAM/CPU/supervisorstack, not4000 boot/globalprocessors/firmware. One externally supplied clock tick at sourceDDD8 guarantees system-loop progress.','Source setsvectors,100recordfreepool,systemcontext,USP/SR transition,createsrender thenactualTRAP0/dispatch/RTE reaches17C40. Subsequent rendering/loading/scheduling and other tasks are not executed by this first-handoff proof. CompleteRAM/CPU/privateframes compare; no graphics/hardware timing claim.'])
        save(out/'report.json',report);save(out/'coverage.json',dict(covered=sorted(coverage)));save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/system-source-bootstrap-checks.json',report);print(json.dumps({k:v for k,v in report.items()if k not in ['source_sha256','compiler','uncovered_instructions']}))
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:native.close()
if __name__=='__main__':main()
