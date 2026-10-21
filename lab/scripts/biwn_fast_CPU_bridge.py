"""Native CPU callback wiring over accepted fixed C code and timing metadata."""
import ctypes as c,hashlib,json,time
from pathlib import Path
import check_biwn_media_setup_cpu as media
ROOT=Path(__file__).resolve().parents[1]
OWNER=c.CFUNCTYPE(c.c_int32,c.c_uint32);RETIRED=c.CFUNCTYPE(None,c.c_uint32,c.c_int32)
class Host(c.Structure):
    _fields_=[(x,c.c_void_p)for x in ['read_cpu','write_cpu','read8','read16','read32','write8','write16','write32','RAM']]
class PrivateHost(c.Structure):
    _fields_=Host._fields_+[(x,c.c_void_p)for x in ['CPU_private','set_reg']]
class Stats(c.Structure):
    _fields_=[(x,c.c_uint64)for x in ['calls','steps','HLE','retired','errors']]+[(x,c.c_uint32)for x in ['error_PC','error_code']]
def install(core,out,mode,RAM,candidate=None,trace=True):
    source=json.loads((candidate or ROOT/'verification/fast-CPU-bridge-candidate.json').read_text());lib=c.CDLL(source['library'])
    for name in ['host','stats','cpu']:getattr(lib,'biwn_fast_CPU_'+name+'_size').restype=c.c_size_t
    host_type=PrivateHost if source.get('private_CPU_state')else Host
    assert lib.biwn_fast_CPU_host_size()==c.sizeof(host_type)and lib.biwn_fast_CPU_stats_size()==c.sizeof(Stats)and lib.biwn_fast_CPU_cpu_size()==c.sizeof(media.CPU)
    names=['BIWNReadCPUState','BIWNWriteCPUState','m68k_read_memory_8','m68k_read_memory_16','m68k_read_memory_32','m68k_write_memory_8','m68k_write_memory_16','m68k_write_memory_32'];values=[c.cast(getattr(core,n),c.c_void_p)for n in names]+[RAM]
    if source.get('private_CPU_state'):
        assert hashlib.sha256(Path(core._name).read_bytes()).hexdigest()==source['required_core_sha256'],'Private CPU layout requires the pinned core binary'
        private=(c.c_uint8*1).in_dll(core,'regs')
        values.extend([c.cast(private,c.c_void_p),c.cast(core.m68k_set_reg,c.c_void_p)])
    host=host_type(*values)
    lib.biwn_fast_CPU_begin.argtypes=[c.POINTER(host_type),c.c_int,c.c_char_p,c.c_char_p];lib.biwn_fast_CPU_begin.restype=c.c_int
    assert lib.biwn_fast_CPU_begin(c.byref(host),1 if mode=='reference'else 2,str(out/'CPU-before-instructions.bin').encode()if trace else None,str(out/'retired-instruction-costs.bin').encode()if trace else None)==0
    owner=OWNER(('biwn_fast_CPU_owner',lib));retired=RETIRED(('biwn_fast_CPU_retired',lib));core.BIWNSetCPUExecOwner(owner,int(mode=='C'));core.BIWNSetCPURetiredObserver(retired)
    lib.biwn_fast_CPU_end.restype=c.POINTER(Stats);started=time.monotonic()
    def finish():
        stats=lib.biwn_fast_CPU_end().contents;row={name:getattr(stats,name)for name,_ in Stats._fields_};row.update(native_CPU_bridge=True,elapsed_seconds=time.monotonic()-started,library=source['library'],instruction_trace_recorded=trace,whole_game_complete=False)
        (out/'native-CPU-bridge-report.json').write_text(json.dumps(row,indent=2)+'\n');return row
    return owner,retired,lib,host,finish
