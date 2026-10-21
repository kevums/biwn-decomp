"""Install the pinned compiled decision and prior portable exception entry."""
import ctypes as c
import hashlib
import json
from pathlib import Path
import biwn_CPU_IRQ_owner as entry

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def install_selector(core):
    manifest = json.loads((ROOT / 'verification/local-CPU-IRQ-selector-author-current.json').read_text())
    assert sha(Path(manifest['library'])) == manifest['library_sha256']
    assert sha(Path(manifest['source'])) == manifest['source_sha256']
    library = c.CDLL(manifest['library'])
    callback = library.biwn_cpu_irq_select
    callback.argtypes = [c.c_uint] * 4
    callback.restype = c.c_int
    core.BIWNSetCPUInterruptSelector.argtypes = [c.c_void_p]
    core.BIWNSetCPUInterruptSelector(c.cast(callback, c.c_void_p))
    for name in ['Owned', 'Original', 'Rejected']:
        getattr(core, 'BIWNCPUInterrupt' + name + 'Count').restype = c.c_uint64
    return library, callback


def install(core, out, candidate=None):
    manifest = json.loads((ROOT / 'verification/CPU-IRQ-selection-core-experimental-candidate.json').read_text())
    assert sha(Path(core._name)) == manifest['core_sha256'], 'Use only the isolated checked selector core'
    old = candidate or json.loads((ROOT / 'verification/CPU-IRQ-bridge-experimental-candidate.json').read_text())
    for name, digest in old['source_sha256'].items():
        assert sha(Path(name)) == digest
    library = c.CDLL(old['library'])
    library.biwn_CPU_IRQ_host_size.restype = c.c_uint
    assert library.biwn_CPU_IRQ_host_size() == c.sizeof(entry.Host)
    names = ['BIWNReadCPUState', 'm68k_read_memory_32', 'm68k_write_memory_16', 'm68k_write_memory_32', 'BIWNCommitCPUIRQEntry']
    host = entry.Host(*(c.cast(getattr(core, name), c.c_void_p) for name in names))
    library.biwn_CPU_IRQ_begin.argtypes = [c.POINTER(entry.Host)]
    library.biwn_CPU_IRQ_begin.restype = c.c_int
    assert library.biwn_CPU_IRQ_begin(c.byref(host)) == 0
    callback = entry.OWNER(('biwn_CPU_IRQ_owner', library))
    core.BIWNSetCPUIRQOwner.argtypes = [c.c_void_p]
    core.BIWNSetCPUIRQOwner(c.cast(callback, c.c_void_p))
    selector_keep = install_selector(core)
    library.biwn_CPU_IRQ_stats.restype = c.POINTER(entry.Stats)
    for name in ['Owned', 'Original', 'Rejected']:
        getattr(core, 'BIWNCPUIRQ' + name + 'Count').restype = c.c_uint64

    def snapshot():
        stats = library.biwn_CPU_IRQ_stats().contents
        return dict(source={name: getattr(stats, name) for name, _ in entry.Stats._fields_},
                    core={name: getattr(core, 'BIWNCPUIRQ' + name + 'Count')() for name in ['Owned', 'Original', 'Rejected']},
                    selection={name: getattr(core, 'BIWNCPUInterrupt' + name + 'Count')() for name in ['Owned', 'Original', 'Rejected']})

    def finish():
        row = snapshot()
        row.update(scope='Source level/mask/NMI decision and portable IRQ entry. Queue/line provider, ACK/vector resolution, commit/prefetch, cycle charge, HLE/devices remain original. Pinned-emulator compatibility only.',
                   whole_game_complete=False, local_model_authored_selector=True, coordinator_authored_entry_and_integration=True)
        (out / 'CPU-IRQ-owner-report.json').write_text(json.dumps(row, indent=2) + '\n')
        return row

    return (callback, selector_keep), host, library, snapshot, finish
