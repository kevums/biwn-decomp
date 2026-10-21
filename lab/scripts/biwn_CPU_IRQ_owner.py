"""Install the isolated portable IRQ-entry body over explicit core host services."""
import ctypes as c
import hashlib
import json
import os
import subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OWNER=c.CFUNCTYPE(c.c_int,c.c_uint32,c.c_uint32)
class Host(c.Structure):
    _fields_=[(name,c.c_void_p)for name in ['read_cpu','read32','write16','write32','commit']]
class Stats(c.Structure):
    _fields_=[(name,c.c_uint64)for name in ['calls','owned','errors']]+[(name,c.c_uint32)for name in ['error_level','error_vector','error_code']]
def build():
    source=ROOT/'projects/black-ice-white-noise/restoration'
    out=ROOT/'verification/CPU-IRQ-bridge-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    library=out/'libCPU-IRQ-owner.dylib'
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(source),str(source/'biwn_cpu_irq_entry.c'),str(ROOT/'scripts/biwn_CPU_IRQ_owner_bridge.c'),'-o',str(library)]
    result=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
    candidate=dict(status='compiled_pending_comparisons',directory=str(out),library=str(library),source_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in [source/'biwn_cpu_irq_entry.c',source/'biwn_cpu_irq_entry.h',ROOT/'scripts/biwn_CPU_IRQ_owner_bridge.c']},whole_game_complete=False)
    (ROOT/'verification/CPU-IRQ-bridge-experimental-candidate.json').write_text(json.dumps(candidate,indent=2)+'\n');return candidate
def install(core,out,candidate=None):
    pinned=json.loads((ROOT/'verification/CPU-IRQ-owner-experimental-candidate.json').read_text())
    assert hashlib.sha256(Path(core._name).read_bytes()).hexdigest()==pinned['core_sha256'],'IRQ handoff requires the tested diagnostic core'
    manifest=candidate or json.loads((ROOT/'verification/CPU-IRQ-bridge-experimental-candidate.json').read_text())
    lib=c.CDLL(manifest['library']);lib.biwn_CPU_IRQ_host_size.restype=c.c_uint
    assert lib.biwn_CPU_IRQ_host_size()==c.sizeof(Host)
    names=['BIWNReadCPUState','m68k_read_memory_32','m68k_write_memory_16','m68k_write_memory_32','BIWNCommitCPUIRQEntry']
    host=Host(*(c.cast(getattr(core,n),c.c_void_p)for n in names))
    lib.biwn_CPU_IRQ_begin.argtypes=[c.POINTER(Host)];lib.biwn_CPU_IRQ_begin.restype=c.c_int
    assert lib.biwn_CPU_IRQ_begin(c.byref(host))==0
    owner=OWNER(('biwn_CPU_IRQ_owner',lib));core.BIWNSetCPUIRQOwner.argtypes=[c.c_void_p];core.BIWNSetCPUIRQOwner(c.cast(owner,c.c_void_p))
    lib.biwn_CPU_IRQ_stats.restype=c.POINTER(Stats)
    for name in ['Owned','Original','Rejected']:getattr(core,'BIWNCPUIRQ'+name+'Count').restype=c.c_uint64
    def snapshot():
        stats=lib.biwn_CPU_IRQ_stats().contents
        return dict(source={name:getattr(stats,name)for name,_ in Stats._fields_},core={name:getattr(core,'BIWNCPUIRQ'+name+'Count')()for name in ['Owned','Original','Rejected']})
    def finish():
        row=snapshot();row.update(scope='Source IRQ-entry arithmetic/vector lookup/stack writes; original device ACK, host CPUcommit/prefetch and cycle charge remain. No standalone or hardware proof.',whole_game_complete=False)
        (out/'CPU-IRQ-owner-report.json').write_text(json.dumps(row,indent=2)+'\n');return row
    return owner,host,lib,snapshot,finish
if __name__=='__main__':print(json.dumps(build()))
