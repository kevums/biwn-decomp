"""Second read-only replay: GPU bundle plus CPU pre/post trace, no ownership."""
import inspect
from pathlib import Path
import diagnose_fast_formatter_first_corruption as base

def main():
    trace=base.TRACE
    trace=trace.replace('static const unsigned char *trace_blitter;', 'static const unsigned char *trace_blitter;\nstatic const uint32_t *trace_bank0,*trace_bank1;\nvoid configure_GPU_trace(const void *a,const void *b){trace_bank0=a;trace_bank1=b;}')
    trace=trace.replace('unsigned char world[16],opcode[8],blitter[256];', 'unsigned char world[16],opcode[8],blitter[256];uint32_t gpu_registers[64];')
    trace=trace.replace('if(frame<1400u||trace_captured)return;', 'if(frame<1428u||trace_captured)return;')
    trace=trace.replace('memcpy(v->blitter,trace_blitter,256);trace_count++;', 'memcpy(v->blitter,trace_blitter,256);memcpy(v->gpu_registers,trace_bank0,128);memcpy(v->gpu_registers+32,trace_bank1,128);trace_count++;')
    trace=trace.replace("trace_hex(f,row->blitter,256);fputc('}',f);", 'trace_hex(f,row->blitter,256);fprintf(f,",\\\"GPU_registers\\\":[");for(unsigned j=0;j<64;j++)fprintf(f,"%s%u",j?",":"",row->gpu_registers[j]);fprintf(f,"]}");')
    trace+='\nint trace_GPU_bundle(uint32_t pc,uint16_t opcode,uint32_t hazards){(void)hazards;trace_memory(2u,pc,(int32_t)opcode);return 0;}\n'
    base.TRACE=trace
    source=inspect.getsource(base.main)
    source=source.replace("'native-fast-core-first-corruption", "'native-fast-core-GPU-corruption")
    source=source.replace("'verification/native-fast-core-first-corruption", "'verification/native-fast-core-GPU-corruption")
    marker='        core.BIWNSetCPURetiredObserver(retired_trace)'
    assert source.count(marker)==1
    source=source.replace(marker,marker+'''
        observer.configure_GPU_trace.argtypes=[c.c_void_p,c.c_void_p]
        banks=[(c.c_uint32*32).in_dll(core,'gpu_reg_bank_'+str(i))for i in range(2)]
        observer.configure_GPU_trace(c.addressof(banks[0]),c.addressof(banks[1]))
        GPU_TRACE=c.CFUNCTYPE(c.c_int,c.c_uint32,c.c_uint16,c.c_uint32)
        gpu_trace=GPU_TRACE(('trace_GPU_bundle',observer))
        core.BIWNSetGPUBundleOwner.argtypes=[GPU_TRACE]
        core.BIWNSetGPUBundleOwner(gpu_trace)
''')
    source=source.replace("'after68000instruction_before_remainingCycle_update'", "'after68000instruction_before_remainingCycle_update','2':'beforeGPUbundle;cyclesfield_contains_GPUopcode'")
    source=source.replace('Afterframe1400','Afterframe1428')
    source=source.replace('core_binary_modified=False,', 'core_binary_modified=False,GPU_callback_return=0,GPU_instruction_ownership=False,')
    source=source.replace("[Path(__file__),source_proof", "[Path(__file__),Path(base.__file__),source_proof")
    namespace=dict(vars(base),base=base,__file__=__file__)
    exec(compile(source,__file__+'::derived_driver','exec'),namespace)
    namespace['main']()

if __name__=='__main__':main()
