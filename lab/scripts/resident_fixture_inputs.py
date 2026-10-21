"""Apply declared test inputs after original resident-entry preparation."""
import ctypes as c,struct
from probe_biwn_gpu_projection import gpu_state
def apply(device,core,inputs):
    for patch in inputs.get('RAM_patches',[]):device.direct(patch['address'],patch['width'],patch['value'])
    if inputs.get('register_patches'):
        raw=bytearray(gpu_state(core)[0])
        for patch in inputs['register_patches']:struct.pack_into('=I',raw,4139+patch['bank']*128+patch['register']*4,patch['value']&0xffffffff)
        buf=c.create_string_buffer(bytes(raw));assert core.GPUStateLoad(buf)==len(raw)
