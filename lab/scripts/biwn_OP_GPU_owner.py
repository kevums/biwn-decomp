"""C-owned live OP GPU slices; original trace only compares, never seeds."""
import ctypes as c,json,hashlib,struct
from pathlib import Path
from probe_biwn_gpu_projection import gpu_state
import check_biwn_movie_GPU as GPU
ROOT=Path(__file__).resolve().parents[1]

def install(runtime,compare_reference=True,label="startup"):
    assert runtime.mode=='C';core=runtime.core
    origin=Path((ROOT/'runs/OP-GPU-native-slice-trace.log').read_text().splitlines()[0])/'OP-GPU-reference-slices';reference=json.loads((origin/'report.json').read_text());candidate=json.loads((ROOT/'verification/OP-GPU-slice-candidate.json').read_text());library=c.CDLL(candidate['library']);fn=library.biwn_gpu_OP_slice_run;fn.argtypes=[c.POINTER(type(runtime.boot_bus)),c.POINTER(type(runtime.gpu)),c.c_uint32];fn.restype=c.c_int
    assert (c.c_uint8*5).in_dll(core,'vjs')[4]==0,'GPU pipeline timing unsupported by unit-cost slice candidate'
    errors=[];pending=None;records=[]
    OWNER=c.CFUNCTYPE(c.c_int,c.c_int,c.c_int32);setter=core.BIWNSetOPGPUExecOwner;setter.argtypes=[OWNER];setter.restype=None
    runtime.OP_GPU_owner_errors=errors
    def callback(phase,cycles):
        nonlocal pending
        if errors:return 1
        try:
            raw=gpu_state(core)[0];digest=hashlib.sha256(raw[:4396]).hexdigest()
            if phase==0:
                assert pending is None
                index=len(records);witness=reference['records'][index]if compare_reference else None
                assert not compare_reference or(cycles==witness['cycles']and digest==witness['before_GPU_sha256']),('OP input mismatch',index,hex(core.GPUGetPC()),hex(witness['before_PC']),digest,witness['before_GPU_sha256'])
                state=GPU.state_from_raw(raw);count=runtime.gpu.instructions;state.instructions=count
                opcode_counter=runtime.gpu_counter.value
                saved_trace,saved_blocks=runtime.gpu_trace,runtime.gpu_blocks
                runtime.gpu_trace=hashlib.sha256();runtime.gpu_blocks=0
                status=fn(c.byref(runtime.boot_bus),c.byref(state),cycles)
                runtime.gpu_trace,runtime.gpu_blocks=saved_trace,saved_blocks
                assert status==0,('owned OP GPU slice',index,status,hex(state.pc))
                assert runtime.gpu_counter.value==opcode_counter,'original GPU executed inside C slice'
                c.memmove(c.byref(runtime.gpu),c.byref(state),c.sizeof(state));image=GPU.logical(state)+raw[4396:]
                assert core.GPUStateLoad(c.create_string_buffer(image))==4416
                pending=dict(index=index,cycles=cycles,before_GPU_sha256=digest,source_instructions=state.instructions-count,original_counter_before=opcode_counter)
            else:
                assert phase==1 and pending is not None
                witness=reference['records'][pending['index']]if compare_reference else None
                assert not compare_reference or digest==witness['after_GPU_sha256'],('OP output mismatch',pending['index'],hex(core.GPUGetPC()),hex(witness['after_PC']),digest,witness['after_GPU_sha256'])
                assert runtime.gpu_counter.value==pending['original_counter_before'],'original GPU execution escape'
                pending['after_GPU_sha256']=digest;records.append(pending);pending=None
        except BaseException as error:
            (runtime.out/'OP-GPU-owner-failure-GPU.bin').write_bytes(gpu_state(core)[0])
            errors.append(repr(error));(runtime.out/'OP-GPU-owner-errors.json').write_text(json.dumps(errors,indent=2)+'\n')
        # Never allow original execution on the reconstructed side, including
        # after a failed ownership gate. OP's existing guard keeps it bounded.
        return 1
    owner=OWNER(callback);setter(owner)
    def finish():
        setter(OWNER());assert not errors and pending is None,(errors[:3],pending);assert not compare_reference or len(records)==reference['calls'],(len(records),reference['calls'])
        report=dict(status='all_live_OP_GPU_slices_match_original_without_original_GPU_execution'if compare_reference else'C_owned_world_OP_GPU_slices_pending_paired_reference_comparison',reference=str(origin),calls=len(records),source_instructions=sum(v['source_instructions']for v in records),records=records,original_GPU_opcodes_on_C_side=0,source_component_library=candidate['library'],captured_GPU_or_RAM_loaded_into_live_game=False,reference_before_after_comparison=compare_reference,global_cycle_scheduling_verified=False)
        (runtime.out/('C-OP-GPU-owner.json'if label=='startup'else 'C-world-OP-GPU-owner.json')).write_text(json.dumps(report,indent=2)+'\n');return report
    runtime._OP_GPU_owner=owner;runtime.finish_OP_GPU_owner=finish
