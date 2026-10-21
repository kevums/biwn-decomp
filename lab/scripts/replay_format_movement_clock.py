"""Controlled offline original input-routine replay from fresh captured RAM.

This supplies CPU entry and elapsed ticks in an isolated fixture. It never
changes the live disc/game; no GPU/firmware/task execution is claimed here.
"""
import ctypes as c,json,sys,subprocess
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from check_biwn_scheduler import Native,cpu_dict,CPU,cleanup
import check_biwn_world_cpu as world_cpu
from run_biwn_native_fast_gameplay_route import sha,save


def read(path):return json.loads(Path(path).read_text())


def main():
    parent_path=ROOT/'verification/native-format-movement-diagnostic-current.json';parent=read(parent_path)
    assert parent['status']=='terminal_fresh_movement_diagnostic_prefixes_repeat_with_identical_buttons'
    old=Path(parent['directory']);out=ROOT/'verification/native-format-movement-clock-replay'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    lanes={lane:[json.loads(line)for line in (old/lane/'gameplay-events.bin.movement.jsonl').read_text().splitlines()]for lane in ['base','optimized']}
    report=read(old/'base/report.json');core=Path(report['core']);assert sha(core)==report['core_sha256']
    src=ROOT/'projects/black-ice-white-noise/restoration'
    source_files=[src/name for name in ['biwn_input_dispatch_cpu.c','biwn_startup_rng_math_cpu.c','biwn_signed_division.c','biwn_camera.c']]
    library=out/'librecovered-input.dylib'
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(src),*[str(p)for p in source_files],'-o',str(library)]
    compiled=subprocess.run(command,capture_output=True,text=True);(out/'compile.log').write_text(compiled.stdout+compiled.stderr);assert compiled.returncode==0,compiled.stderr
    code=c.CDLL(str(library));Bus=cleanup.world.Bus;W8=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.c_uint8)
    recovered=code.biwn_input_dispatch_cpu_body;recovered.argtypes=[c.POINTER(Bus),c.POINTER(CPU),W8,world_cpu.SERVICE,c.c_void_p,c.c_uint32,c.c_int];recovered.restype=c.c_int
    math_body=code.biwn_startup_rng_math_cpu_body;math_body.argtypes=[c.POINTER(Bus),c.POINTER(CPU)];math_body.restype=c.c_int
    engine=Native(diagnostic_core=core);results=[];sources={str(parent_path):sha(parent_path),str(core):sha(core),str(Path(__file__)):sha(__file__),str(library):sha(library)}
    for p in source_files:sources[str(p)]=sha(p)
    dependency_run=subprocess.run(['clang','-MM','-I',str(src),*[str(p)for p in source_files]],capture_output=True,text=True)
    assert dependency_run.returncode==0,dependency_run.stderr
    (out/'compile-dependencies.txt').write_text(dependency_run.stdout)
    for line in dependency_run.stdout.replace('\\\n',' ').splitlines():
        for name in line.split(':',1)[1].split():
            p=Path(name).resolve();assert p.is_file()and p.is_relative_to(ROOT)
            sources[str(p)]=sha(p)
    for module in tuple(sys.modules.values()):
        name=getattr(module,'__file__',None)
        if name:
            p=Path(name).resolve()
            if p.is_file()and p.is_relative_to(ROOT):sources[str(p)]=sha(p)
    state=dict(status='running_offline_original_dispatch_clock_replay',directory=str(out),cases=results,
               fixture_entry_PC='0x191F4',stop_before_original_RTS='0x19F2A',
               explicit_fixture_inputs=['Captured2MBRAM and CPU registers','PCset to original input-routine entry','Elapsed-time word4C24Cset to4or5','IRQdisabled for isolated execution'],
               gameplay_or_IRQ_execution=False,guest_live_game_changed=False,coordinator_added_new_game_source=False,
               existing_recovered_C_compared=True,compiler=command,
               new_training=False,whole_game_complete=False,source_sha256=sources)
    def mark():save(out/'protocol.json',state)
    mark()
    try:
        for lane in ['base','optimized']:
            initial=next(r for r in lanes[lane]if r['world_sequence']==6812 and r['pc']==0x1a188)
            observed=next(r for r in lanes[lane]if r['world_sequence']==6812 and r['pc']==0x1a26c)
            memory=Path(initial['RAM']);original=memory.read_bytes();assert sha(memory)==parent['results'][lane]['snapshots_sha256'][str(memory)]
            sources[str(memory)]=sha(memory)
            before=int.from_bytes(original[0x49cc8:0x49ccc],'big');assert before==44514
            observed_ram=Path(observed['RAM']).read_bytes();sources[observed['RAM']]=sha(observed['RAM'])
            for dt in [4,5]:
                ram=bytearray(original);ram[0x4c24c:0x4c250]=dt.to_bytes(4,'big')
                engine.device.seed(bytes(ram),0);lib=engine.lib;lib.m68k_pulse_reset();lib.m68k_set_irq(0)
                lib.m68k_set_reg(17,0x2000);lib.m68k_set_reg(15,initial['ssp']);lib.m68k_set_reg(17,0);lib.m68k_set_reg(15,initial['usp']);lib.m68k_set_reg(17,initial['sr'])
                for i,v in enumerate(initial['registers']):lib.m68k_set_reg(i,v)
                lib.m68k_set_reg(16,0x191f4);trace=[]
                for _ in range(20000):
                    pc=lib.m68k_get_reg(None,16)
                    if pc==0x19f2a:break
                    if not(0x191f4<=pc<0x19f2c or 0xe540<=pc<0xe61c):
                        save(out/'unexpected-native-boundary.json',dict(lane=lane,dt=dt,pc=hex(pc),last_PC=list(map(hex,trace[-24:]))));raise AssertionError(('Unexpected original helper boundary',hex(pc)))
                    trace.append(pc);assert lib.m68k_execute(1)>0
                else:raise AssertionError('Original dispatcher instruction limit')
                result=engine.device.ram();amount=int.from_bytes(result[0x49cc4:0x49cc8],'big');fraction=int.from_bytes(result[0x49cc8:0x49ccc],'big')
                native_cpu=CPU();native_cpu.registers[:]=[lib.m68k_get_reg(None,i)for i in range(16)];native_cpu.pc=lib.m68k_get_reg(None,16);native_cpu.sr=lib.m68k_get_reg(None,17)
                native_cpu.usp=engine.prefix[16]if native_cpu.sr&0x2000 else native_cpu.registers[15]
                native_cpu.ssp=native_cpu.registers[15]if native_cpu.sr&0x2000 else engine.prefix[17]
                memory_c=bytearray(ram);accesses=[];errors=[];helper_calls=[]
                def reader(width):
                    def callback(_,address,value):
                        if address+width>len(memory_c):errors.append(('read',address,width));return 1
                        value[0]=int.from_bytes(memory_c[address:address+width],'big');accesses.append(['read',address,width,value[0]]);return 0
                    return callback
                def writer(width):
                    def callback(_,address,value):
                        if address+width>len(memory_c):errors.append(('write',address,width));return 1
                        memory_c[address:address+width]=(value&((1<<(8*width))-1)).to_bytes(width,'big');accesses.append(['write',address,width,value]);return 0
                    return callback
                callbacks=[cleanup.world.R8(reader(1)),cleanup.world.R16(reader(2)),cleanup.world.R32(reader(4)),cleanup.world.W16(writer(2)),cleanup.world.W32(writer(4)),W8(writer(1))]
                bus=Bus(*callbacks[:5],cleanup.world.CALL(),None,0)
                def service(_,passed,cpu,target):
                    helper_calls.append(target)
                    if target!=0xe588:errors.append(('unexpected-helper',target));return 1
                    return math_body(passed,cpu)
                provider=world_cpu.SERVICE(service);translated=CPU();translated.registers[:]=initial['registers'];translated.pc=0x191f4;translated.sr=initial['sr'];translated.usp=initial['usp'];translated.ssp=initial['ssp']
                c_status=recovered(c.byref(bus),c.byref(translated),callbacks[5],provider,None,20000,1)
                if c_status or errors or cpu_dict(translated)!=cpu_dict(native_cpu) or bytes(memory_c)!=result:
                    save(out/'recovered-C-mismatch.json',dict(lane=lane,dt=dt,status=c_status,errors=errors,native_CPU=cpu_dict(native_cpu),C_CPU=cpu_dict(translated),RAM_differences=[hex(i)for i,(a,b)in enumerate(zip(result,memory_c))if a!=b][:32]));raise AssertionError('Recovered C differs from original CPU')
                numerator=((3*dt*8)&0xffff)<<16;expected=before+numerator//300
                assert amount==expected>>16 and fraction==expected&0xffff
                if dt==observed['delta_clock']:
                    assert amount==observed['speed'] and fraction==int.from_bytes(observed_ram[0x49cc8:0x49ccc],'big')
                row=dict(lane=lane,frame=9920,world_sequence=6812,elapsed_ticks=dt,initial_fraction=before,
                         original_CPU_movement_amount=amount,original_CPU_fraction=fraction,
                         original_instructions=len(trace),native_PC_trace=list(map(hex,trace)),
                         observed_elapsed_ticks=observed['delta_clock'],matches_own_observed_pair=dt==observed['delta_clock'],
                         full_recovered_C_CPU_and_2MB_RAM_equal=True,recovered_C_helper_calls=list(map(hex,helper_calls)),
                         helper_results_stubbed=False,C_public_accesses=accesses,native_final_CPU=cpu_dict(native_cpu),
                         expected_formula='(44514+floor(((3*dt*8)&65535)*65536/300)) -> high16movement,low16fraction',
                         RAM_sha256=__import__('hashlib').sha256(result).hexdigest())
                results.append(row);save(out/(lane+'-dt'+str(dt)+'.json'),row);mark()
        state.update(status='terminal_original_dispatch_clock_counterfactual_matches_observed_movement',cases=results,
                     results_identical_for_same_dt_across_captured_build_RAM=True,
                     dt4=dict(amount=0,fraction=65485),dt5=dict(amount=1,fraction=5192),
                     scope='Four isolated original191F4..19F2Aroutine replays from captured RAM plus unchanged recovered hostC input routine and real recoveredC signed division. Full CPU and all2MBRAM match; no helper-result stubs. Original source-assembled division executes on retained CPU. Elapsed time is explicitly supplied in the offline fixture. No IRQ/fault/order-trace timing,live source substitution,earlier scheduling cause or whole-game equivalence proof.')
        mark();save(ROOT/'verification/native-format-movement-clock-replay-current.json',state)
        print(state['status'],[(r['lane'],r['elapsed_ticks'],r['original_CPU_movement_amount'],r['original_CPU_fraction'])for r in results],flush=True)
    except BaseException as error:state.update(status='terminal_failed',error=repr(error));mark();raise
    finally:engine.close()


if __name__=='__main__':main()
