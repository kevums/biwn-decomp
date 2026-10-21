"""Finish a live suspended resident GPU IRQ before command dispatch."""
import ctypes as c,types,json,hashlib
from pathlib import Path
import check_biwn_movie_GPU as GPU
from probe_biwn_gpu_projection import gpu_state
ROOT=Path(__file__).resolve().parents[1]
def install(runtime):
    parent=runtime.run_dispatch;library=c.CDLL(json.loads((ROOT/'verification/OP-GPU-slice-candidate.json').read_text())['library']);fn=library.biwn_gpu_OP_slice_run;fn.argtypes=[c.POINTER(type(runtime.boot_bus)),c.POINTER(GPU.State),c.c_uint32];fn.restype=c.c_int;records=[]
    def drain():
        steps=0;before=gpu_state(runtime.core)[0]if runtime.mode=='native'else GPU.logical(runtime.gpu)
        for _ in range(100000):
            if runtime.mode=='native':
                state=GPU.state_from_raw(gpu_state(runtime.core)[0])
                if not state.flags&8:break
                runtime.core.GPUExec(1)
            else:
                if not runtime.gpu.flags&8:break
                counter=runtime.gpu_counter.value
                saved_trace,saved_blocks=runtime.gpu_trace,runtime.gpu_blocks;runtime.gpu_trace=hashlib.sha256();runtime.gpu_blocks=0
                status=fn(c.byref(runtime.boot_bus),c.byref(runtime.gpu),1);runtime.gpu_trace,runtime.gpu_blocks=saved_trace,saved_blocks
                assert status==0 and runtime.gpu_counter.value==counter,('GPU pending source IRQ',status,hex(runtime.gpu.pc))
                raw=gpu_state(runtime.core)[0];assert runtime.core.GPUStateLoad(c.create_string_buffer(GPU.logical(runtime.gpu)+raw[4396:]))==4416
            steps+=1
        else:raise AssertionError('pending GPU IRQ source bound')
        if steps:records.append(dict(steps=steps,before_GPU_sha256=hashlib.sha256(before[:4396]).hexdigest(),after_GPU_sha256=hashlib.sha256(gpu_state(runtime.core)[0][:4396]if runtime.mode=='native'else GPU.logical(runtime.gpu)).hexdigest()))
    def dispatch(self,idle):drain();return parent(idle)
    render_parent=runtime.run_render_request
    def render(self,command):
        # Scene bridges require the resident dispatcher, just as movement does.
        # Resume the live interrupt frame before either reference or C routing;
        # retain its actual state rather than reseeding a dispatcher fixture.
        drain()
        return render_parent(command)
    runtime.run_dispatch=types.MethodType(dispatch,runtime)
    runtime.run_render_request=types.MethodType(render,runtime)
    runtime.world_GPU_IRQ_resumes=records
