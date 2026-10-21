"""Observe original GPU52E0 from the actual E19E live-scene call boundary.

Preserves the preceding GPU4D80 state and real CPU170A0 records. No GPU reset
between these programs. Existing assisted-startup/device/script limits remain.
"""
import argparse,ctypes as c,hashlib,json,struct,sys
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_disc_scene_actors as scene
ROOT=scene.ROOT
read=lambda p:json.loads(p.read_text())
save=scene.save
sha=lambda data:hashlib.sha256(data).hexdigest()
class PrefixCaptured(Exception):pass
class Runtime(scene.Runtime):
    def render_fixture(self,state,target):
        if target==0xe19e:
            self.prefix_CPU=scene.live.prior.scheduler.cpu_dict(state)
            raise PrefixCaptured()
        return super().render_fixture(state,target)
def gpu_state(core):
    buf=c.create_string_buffer(8192)
    size=core.GPUStateSave(buf);assert 4396<size<8192,size
    raw=buf.raw[:size]
    fields=struct.unpack_from('=10I',raw,4096)
    z,n,carry=raw[4136:4139]
    regs=struct.unpack_from('=64I',raw,4139)
    return raw,dict(zip(['pc','accumulator','remainder','hidata','flags_raw','matrix_control','matrix_pointer','data_organization','control','division_control'],fields),z=z,n=n,c=carry,registers=[list(regs[:32]),list(regs[32:])],active_bank=raw[4395])
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opt=ap.parse_args()
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);folder=session/'gpu-render-52e0-overlay';mapping=read(folder/'initial-linear-decode.json');decoded={r['address']:r for r in mapping['rows']}
    out=folder/'live-prefix-original-probes'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    proof=read(ROOT/'verification/biwn-disc-world-gpu-geometry-checks.json');capture=Path(proof['startup_capture_directory'])
    runtime=Runtime(Path(proof['directory'])/'libdisc-world-yields.dylib',ROOT/'tools/libbiwn-projection-probe.dylib')
    for name in ['animation','camera','targeting','dispatch']:getattr(runtime,'enable_'+name)()
    runtime.enable_resource_fixture([[17,18],[],[17,18],[]])
    for name in ['resource_memory','resource_disc','cd_cpu','loading_yields','render_queue','scene_draw','geometry_records','GPU_geometry']:getattr(runtime,'enable_'+name)()
    lib=runtime.device.lib;core=runtime.core
    core.GPUStateSave.argtypes=[c.c_void_p];core.GPUStateSave.restype=c.c_size_t
    lib.lab_projection_prepare.restype=c.c_int;lib.lab_projection_original.restype=c.c_int
    lib.lab_projection_steps.restype=c.c_uint32;lib.lab_projection_PC.argtypes=[c.c_uint32];lib.lab_projection_PC.restype=c.c_uint32
    lib.lab_movement_event_count.restype=c.c_uint64;lib.lab_movement_event.argtypes=[c.c_uint64,c.POINTER(c.c_uint32)];lib.lab_movement_event.restype=c.c_int
    vectors=[(p,step,index)for p in sorted(capture.glob('startup-C-*.bin'))for step in [8,30]for index in [1,2]][:opt.limit or None]
    rows=[];direct=set();delays=set()
    try:
        for number,(path,step,index)in enumerate(vectors):
            save(out/'status.json',dict(status='running',case=number));metadata=read(capture/f'startup-capture-{path.stem.split("-")[-1]}.json');ram=bytearray(path.read_bytes());assert sha(ram)==metadata['C_RAM_sha256']
            for ctx in scene.startup.CONTEXTS:ram[ctx+26:ctx+30]=(0 if ctx in scene.RUNNABLE|{0xc2128,scene.startup.RENDER}else 1).to_bytes(4,'big')
            for a in [0x49d54,0x49d56]:ram[a:a+2]=index.to_bytes(2,'big')
            cpu=scene.CPU();cpu.registers[:]=metadata['CPU']['registers']
            for field in ['pc','sr','usp','ssp']:setattr(cpu,field,metadata['CPU'][field])
            cpu.ssp=0x1ff000;runtime.enable_world(step)
            try:runtime.native(bytes(ram),cpu,64)
            except PrefixCaptured:pass
            else:raise AssertionError('E19E not reached')
            prefix=runtime.device.ram();raw,state=gpu_state(core)
            assert state['pc']==0xf031be and state['active_bank']==0,state
            assert runtime.GPU_geometry_CPU_calls and runtime.geometry_record_calls
            stem=f'case-{number:02d}'
            (out/f'{stem}-prefix-RAM.bin').write_bytes(prefix);(out/f'{stem}-prefix-GPU-state.bin').write_bytes(raw)
            assert lib.lab_projection_prepare()==0
            before=runtime.device.ram();before_raw,before_state=gpu_state(core)
            (out/f'{stem}-before-RAM.bin').write_bytes(before);(out/f'{stem}-before-GPU-state.bin').write_bytes(before_raw)
            status=lib.lab_projection_original();steps=[lib.lab_projection_PC(i)for i in range(lib.lab_projection_steps())]
            after=runtime.device.ram();after_raw,after_state=gpu_state(core)
            (out/f'{stem}-after-RAM.bin').write_bytes(after);(out/f'{stem}-after-GPU-state.bin').write_bytes(after_raw)
            events=[]
            for i in range(lib.lab_movement_event_count()):
                ev=(c.c_uint32*5)();assert lib.lab_movement_event(i,ev)==0
                if ev[1]==3 and ev[0]in [11,12]:events.append(list(ev))
            direct.update(steps)
            for pc in steps:
                assert pc in decoded,hex(pc)
                if int(decoded[pc]['bytes'][:4],16)>>10 in [52,53]:delays.add(pc+2)
            row=dict(case=number,capture=str(path),capture_sha256=metadata['C_RAM_sha256'],clock_step=step,inventory_index=index,prefix_CPU=runtime.prefix_CPU,prefix_GPU=state,before_GPU=before_state,after_GPU=after_state,record_count=scene.get(prefix,0x49b88),status=status,steps=steps,events=events,completion_before=scene.get(before,0x10a684),completion_after=scene.get(after,0x10a684),changed_RAM_bytes=sum(a!=b for a,b in zip(before,after)),prefix_RAM_sha256=sha(prefix),before_RAM_sha256=sha(before),after_RAM_sha256=sha(after),prefix_GPU_state_sha256=sha(raw),before_GPU_state_sha256=sha(before_raw),after_GPU_state_sha256=sha(after_raw),preceding_GPU_calls=len(runtime.GPU_geometry_CPU_calls),preceding_record_builder_calls=sum(r['target']==0x170a0 for r in runtime.geometry_record_calls),device=runtime.device.stats())
            rows.append(row);save(out/'cases.json',rows)
            # 10A684 becomes the sorted-list head/count here. The later draw
            # chain consumes and clears it; projection alone need not clear it.
            assert status==0 and after_state['pc']==0xf031be,dict(case=number,status=status,final_PC=hex(after_state['pc']),completion=row['completion_after'])
            print(json.dumps(dict(case=number,records=row['record_count'],steps=len(steps),changed_RAM_bytes=row['changed_RAM_bytes'],completion=row['completion_after'])),flush=True)
        covered=direct|delays;candidate={pc for pc in decoded if pc<0xf0362c};assert covered<=candidate,[hex(pc)for pc in covered-candidate]
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='original_GPU52E0_live_prefix_probes_returned_C_unimplemented',directory=str(out),cases=len(rows),record_counts=sorted({r['record_count']for r in rows}),projection_list_head_values=sorted({r['completion_after']for r in rows}),candidate_instructions=len(candidate),direct_PC_addresses=len(direct),derived_delay_addresses=len(delays-direct),observed_instruction_addresses=len(covered),unobserved_candidate_addresses=[hex(pc)for pc in sorted(candidate-covered)],payload_sha256=mapping['payload_SHA256'],probe_source_sha256=sha(Path(__file__).read_bytes()),bridge_source_sha256=sha((ROOT/'scripts/biwn_projection_probe_bridge.c').read_bytes()),library_sha256=sha((ROOT/'tools/libbiwn-projection-probe.dylib').read_bytes()),C_projection_reconstructed=False,GPU_reset_between_geometry_and_projection=False,CPU_E19E_executed=False,dispatcher_executed=False,full_viewport_proved=False,scope='Original GPU52E0 entry with source E19E arguments over actual live prefix including originalGPU4D80 and realCPU170A0 records. Host loads overlay and supplies E19E stores; preceding assisted-startup/script/clock/synchronous-device limits retained. GPUStateSave is read-only observation of pinned core state. Watch read values are placeholders; PC/external read shape/stores and before/after full RAM/state retained. Projection may leave nonzero sorted-list head at10A684; later draw chain must consume/clear it. No C or full renderer claim.')
        save(out/'report.json',report);save(out/'status.json',dict(status='terminal_preflight'if opt.limit else'terminal_pass'))
        if not opt.limit:save(folder/'live-prefix-original-current.json',report);save(ROOT/'verification/biwn-gpu-projection-original-probes.json',report)
        print(json.dumps(report))
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:runtime.device.close()
if __name__=='__main__':main()
