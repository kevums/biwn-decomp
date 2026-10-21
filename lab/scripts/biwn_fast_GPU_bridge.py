"""Native GPU callback adapter; trace files remain byte-compatible with Python bridge."""
import ctypes as c,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OWNER=c.CFUNCTYPE(c.c_int,c.c_uint32,c.c_uint16,c.c_uint32)
class Host(c.Structure):
    _fields_=[(name,c.c_void_p)for name in ['save','load','read16','read32','write16','write32','read8','RAM','counter']]
class Stats(c.Structure):
    _fields_=[(name,c.c_uint64)for name in ['callbacks','known','uncovered','instructions','errors']]+[(name,c.c_uint32)for name in ['error_PC','error_code']]
def install(core,out,mode,full_trace=True,candidate=None):
    source=json.loads((candidate or ROOT/'verification/fast-GPU-bridge-candidate.json').read_text());library=c.CDLL(source['library'])
    library.biwn_fast_GPU_host_size.restype=c.c_size_t;library.biwn_fast_GPU_stats_size.restype=c.c_size_t
    assert library.biwn_fast_GPU_host_size()==c.sizeof(Host)and library.biwn_fast_GPU_stats_size()==c.sizeof(Stats)
    addresses=[c.cast(getattr(core,name),c.c_void_p)for name in ['GPUStateSave','GPUStateLoad','GPUReadWord','GPUReadLong','GPUWriteWord','GPUWriteLong','JaguarReadByte','GPUGetRAM']]
    counter=c.c_uint32.in_dll(core,'gpu_exec_opcode_count');host=Host(*addresses,c.addressof(counter))
    directory=out/'regular-GPU-bundles';directory.mkdir()
    names=['before-state-hashes.bin','C-after-state-hashes.bin','PC-stream.bin'];paths=[str(directory/name).encode()for name in names]if full_trace else[None,None,None]
    library.biwn_fast_GPU_begin.argtypes=[c.POINTER(Host),c.c_int,c.c_char_p,c.c_char_p,c.c_char_p];library.biwn_fast_GPU_begin.restype=c.c_int
    assert library.biwn_fast_GPU_begin(c.byref(host),1 if mode=='trace'else 2,*paths)==0
    if source.get('capture_unknown'):
        library.biwn_fast_GPU_capture_unknown.argtypes=[c.c_char_p];library.biwn_fast_GPU_capture_unknown.restype=c.c_int
        assert library.biwn_fast_GPU_capture_unknown(str(directory/'unknown-instructions.bin').encode())==0
        library.biwn_fast_GPU_unknown_count.restype=c.c_uint64
    owner=OWNER(('biwn_fast_GPU_owner',library));core.BIWNSetGPUBundleOwner.argtypes=[OWNER];core.BIWNSetGPUBundleOwner(owner)
    for name in ['Owned','Original','Rejected']:getattr(core,'BIWNGPU'+name+'BundleCount').restype=c.c_uint64
    library.biwn_fast_GPU_end.restype=c.POINTER(Stats);errors=[];started=time.monotonic()
    def finish():
        elapsed=time.monotonic()-started;stats=library.biwn_fast_GPU_end().contents;values={name:getattr(stats,name)for name,_ in Stats._fields_}
        counts={name:getattr(core,'BIWNGPU'+name+'BundleCount')()for name in ['Owned','Original','Rejected']};core.BIWNSetGPUBundleOwner(OWNER())
        if values['errors']:errors.append('Native GPU rejection '+str(values))
        report=dict(status='rejected'if errors or counts['Rejected']else'completed_uncompared',mode=mode,counts=counts,C_source_instructions=values['instructions'],stats=values,errors=errors,library=source['library'],native_bridge=True,elapsed_seconds=elapsed,whole_game_complete=False,full_instruction_trace=full_trace,trace_scope=('Same4396logicalGPUbefore hashes, PCstream and after hashes as original Python bridge'if full_trace else'Per-frame/final machine checks only; GPUinstruction state hashes not recorded'))
        (directory/'report.json').write_text(json.dumps(report,indent=2)+'\n');return report
    return owner,[host,counter],library,errors,finish
