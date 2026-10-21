"""Continue fresh disc-derived game entry toDD40 using checked C helpers."""
import ctypes as c
import hashlib,json,types
from pathlib import Path
import biwn_live_source_prefix as prefix
import check_biwn_media_setup_cpu as media
import check_biwn_dsp_media_audio as DSP

ROOT=Path(__file__).resolve().parents[1]


def run(core,ram_pointer,out,mode):
    for name in ['GPUGetRAM','DSPGetRAM']:getattr(core,name).restype=c.c_void_p
    proof=json.loads((ROOT/'verification/source-runtime-rebuild-current.json').read_text())
    library=Path(proof['library']);functions=c.CDLL(str(library))
    fn=functions.biwn_entry_setup_cpu_call
    world=media.scheduler.cleanup.world
    fn.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU),media.W8,media.world_cpu.SERVICE,c.c_void_p,c.c_uint32,c.c_int]
    runtime=types.SimpleNamespace(core=core,mode=mode,fn=fn,cpu=core._biwn_read_CPU,
        gpu=core._biwn_fresh_entry_GPU,C_DSP=None)
    runtime.device=types.SimpleNamespace(pointer=ram_pointer,ram=lambda:c.string_at(ram_pointer,0x200000))
    runtime.read=lambda a,w:getattr(core,'m68k_read_memory_'+str(w*8))(a)
    runtime.write=lambda a,w,v:getattr(core,'m68k_write_memory_'+str(w*8))(a,v)
    counters_before={name:c.c_uint32.in_dll(core,name).value for name in ['gpu_exec_opcode_count','dsp_exec_opcode_count']}
    result=prefix.run(runtime,library,mode,initial_CPU=core._biwn_fresh_entry_CPU,
        platform_API=core._biwn_HLE_API_body)
    core._biwn_fresh_prefix_CPU=runtime.entry_CPU
    core._biwn_fresh_prefix_GPU=runtime.gpu
    core._biwn_fresh_prefix_DSP=runtime.C_DSP
    counters_after={name:c.c_uint32.in_dll(core,name).value for name in counters_before}
    if mode=='C':assert counters_after==counters_before, (counters_before,counters_after)
    hardware={}
    for name in ['TOM','JERRY','DAC','CDROM','CDROMStateExt','Joystick','UART','Event']:
        symbol=name+'StateSave' if name!='CDROMStateExt' else 'CDROMStateExtSave'
        fn=getattr(core,symbol);fn.argtypes=[c.c_void_p];fn.restype=c.c_size_t
        raw=c.create_string_buffer(200000);size=fn(raw);assert 0<size<=len(raw)
        hardware[name]={'bytes':size,'sha256':hashlib.sha256(raw.raw[:size]).hexdigest()}
    result['shared_hardware']=hardware
    result['original_GPU_DSP_opcode_counts']={name:counters_after[name]-counters_before[name] for name in counters_before}
    (out/(mode+'-prefix-RAM.bin')).write_bytes(runtime.device.ram())
    result.update(initial_capture_loaded=False,platform_HLE_API_retained=True,
                  source_fresh_entry_retained=True,whole_game_complete=False)
    return result
