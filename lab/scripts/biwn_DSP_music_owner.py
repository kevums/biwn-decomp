"""Experimental bank-aware source music owner; original device/IRQ scheduling retained."""
import ctypes as c,hashlib,json,time
from pathlib import Path
from check_biwn_music_DSP_engine import State
ROOT=Path(__file__).resolve().parents[1]
OWNER=c.CFUNCTYPE(c.c_int,c.c_uint32,c.c_uint16,c.c_uint32)
class Host(c.Structure):_fields_=[(n,c.c_void_p)for n in ['save','commit','read8','read32','write32','operands','write16','context']]
class Stats(c.Structure):_fields_=[(n,c.c_uint64)for n in ['calls','owned','uncovered','errors']]+[(n,c.c_uint32)for n in ['error_PC','error_code']]
def install(core,out):
    candidate=json.loads((ROOT/'verification/DSP-music-owner-experimental-candidate.json').read_text())
    assert hashlib.sha256(Path(core._name).read_bytes()).hexdigest()==candidate['required_core_sha256']
    lib=c.CDLL(candidate['library'])
    for n in ['host','stats','state']:getattr(lib,'biwn_DSP_music_'+n+'_size').restype=c.c_size_t
    assert lib.biwn_DSP_music_host_size()==c.sizeof(Host) and lib.biwn_DSP_music_stats_size()==c.sizeof(Stats) and lib.biwn_DSP_music_state_size()==c.sizeof(State)
    names=['DSPStateSave','BIWNDSPWriteLogicalState','DSPReadByte','DSPReadLong','DSPWriteLong','BIWNDSPSetLastOperands','DSPWriteWord','BIWNDSPReadRetirementContext'];host=Host(*[c.cast(getattr(core,n),c.c_void_p)for n in names])
    lib.biwn_DSP_music_begin.argtypes=[c.POINTER(Host)];lib.biwn_DSP_music_begin.restype=c.c_int;assert lib.biwn_DSP_music_begin(c.byref(host))==0
    callback=OWNER(('biwn_DSP_music_owner',lib));core.BIWNSetDSPInstructionOwner.argtypes=[OWNER];core.BIWNSetDSPInstructionOwner(callback)
    for n in ['Owned','Original','Rejected']:getattr(core,'BIWNDSP'+n+'InstructionCount').restype=c.c_uint64
    lib.biwn_DSP_music_stats.restype=c.POINTER(Stats);started=time.monotonic()
    def finish():
        values=lib.biwn_DSP_music_stats().contents;report={n:getattr(values,n)for n,_ in Stats._fields_};report['core_counts']={n:getattr(core,'BIWNDSP'+n+'InstructionCount')()for n in ['Owned','Original','Rejected']};report.update(library=candidate['library'],elapsed_seconds=time.monotonic()-started,status='rejected'if report['errors']or report['core_counts']['Rejected']else'completed_uncompared',whole_game_complete=False);core.BIWNSetDSPInstructionOwner(OWNER());(out/'DSP-owner-report.json').write_text(json.dumps(report,indent=2)+'\n');return report
    return callback,lib,host,finish
