"""Read-only OP slice trace in the original reference; no rebuilt claim."""
import ctypes as c,hashlib,json,struct
from pathlib import Path
from probe_biwn_gpu_projection import gpu_state

def install(runtime,label="startup",capture_states=True):
    assert runtime.mode=='native'
    core=runtime.core;directory=runtime.out/('OP-GPU-reference-slices'if label=='startup'else'world-OP-GPU-reference-slices');directory.mkdir();records=[];pending=None
    OWNER=c.CFUNCTYPE(c.c_int,c.c_int,c.c_int32);setter=core.BIWNSetOPGPUExecOwner;setter.argtypes=[OWNER];setter.restype=None;errors=[]
    def callback(phase,cycles):
        nonlocal pending
        try:
            raw=gpu_state(core)[0]
            if phase==0:
                assert pending is None
                index=len(records);stem=f'{index:06d}'
                pending=dict(index=index,cycles=cycles,before_PC=core.GPUGetPC(),before_GPU_sha256=hashlib.sha256(raw[:4396]).hexdigest(),counter_before=runtime.gpu_counter.value)
                if capture_states:(directory/(stem+'-before-GPU.bin')).write_bytes(raw)
                if capture_states and index<64:
                    (directory/(stem+'-before-RAM.bin')).write_bytes(runtime.device.ram())
            else:
                assert phase==1 and pending is not None
                pending.update(after_PC=core.GPUGetPC(),after_GPU_sha256=hashlib.sha256(raw[:4396]).hexdigest(),original_opcode_delta=(runtime.gpu_counter.value-pending['counter_before'])&0xffffffff)
                stem=f'{pending["index"]:06d}'
                if capture_states:(directory/(stem+'-after-GPU.bin')).write_bytes(raw)
                if capture_states and pending['index']<64:(directory/(stem+'-after-RAM.bin')).write_bytes(runtime.device.ram())
                records.append(pending);pending=None
        except BaseException as error:errors.append(repr(error))
        return 0
    owner=OWNER(callback);setter(owner)
    def finish():
        setter(OWNER());assert pending is None and not errors,(pending,errors)
        report=dict(status='original_OP_GPU_slice_trace_only',directory=str(directory),calls=len(records),original_GPU_opcodes=sum(v['original_opcode_delta']for v in records),records=records,errors=errors,raw_GPU_bytes=4416,logical_GPU_bytes=4396,first64_RAM_snapshots=capture_states,new_training=False,rebuilt_GPU_ownership=False)
        (directory/'report.json').write_text(json.dumps(report,indent=2)+'\n');return report
    runtime._OP_trace_owner=owner;runtime.finish_OP_GPU_trace=finish
