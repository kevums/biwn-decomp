"""Pinned byte-fenced DSP music/media program router wiring."""
import ctypes as c
import hashlib
import json
import time
from pathlib import Path
from biwn_DSP_music_owner import Host, Stats, OWNER

ROOT = Path(__file__).resolve().parents[1]


class Profiles(c.Structure):
    _fields_ = [(n, c.c_uint64) for n in ['music', 'media', 'switches']]+[('last', c.c_uint32)]


def install(core, out, candidate_path=None):
    candidate = json.loads(Path(candidate_path or ROOT/'verification/DSP-program-router-experimental-candidate.json').read_text())
    assert hashlib.sha256(Path(core._name).read_bytes()).hexdigest() == candidate['required_core_sha256']
    lib = c.CDLL(candidate['library'])
    for name, structure in [('host', Host), ('stats', Stats), ('profiles', Profiles)]:
        fn = getattr(lib, 'biwn_DSP_router_'+name+'_size')
        fn.restype = c.c_size_t
        assert fn() == c.sizeof(structure), name
    names = ['DSPStateSave', 'BIWNDSPWriteLogicalState', 'DSPReadByte', 'DSPReadLong',
             'DSPWriteLong', 'BIWNDSPSetLastOperands', 'DSPWriteWord', 'BIWNDSPReadRetirementContext']
    host = Host(*[c.cast(getattr(core, name), c.c_void_p) for name in names])
    if candidate.get('compact_live_RAM'):
        core.DSPGetRAM.restype=c.c_void_p
        lib.biwn_DSP_router_bind_compact.argtypes=[c.c_void_p,c.c_void_p,c.c_void_p]
        lib.biwn_DSP_router_bind_compact.restype=c.c_int
        assert lib.biwn_DSP_router_bind_compact(
            c.cast(core.BIWNDSPStateSaveWithoutRAM,c.c_void_p),
            c.cast(core.BIWNDSPWriteLogicalStateWithoutRAM,c.c_void_p),core.DSPGetRAM())==0
    lib.biwn_DSP_router_begin.argtypes = [c.POINTER(Host)]
    lib.biwn_DSP_router_begin.restype = c.c_int
    assert lib.biwn_DSP_router_begin(c.byref(host)) == 0
    callback = OWNER(('biwn_DSP_router_owner', lib))
    core.BIWNSetDSPInstructionOwner.argtypes = [OWNER]
    core.BIWNSetDSPInstructionOwner(callback)
    for name in ['Owned', 'Original', 'Rejected']:
        getattr(core, 'BIWNDSP'+name+'InstructionCount').restype = c.c_uint64
    lib.biwn_DSP_router_stats.restype = c.POINTER(Stats)
    lib.biwn_DSP_router_profiles.restype = c.POINTER(Profiles)
    started = time.monotonic()

    def finish():
        stats = lib.biwn_DSP_router_stats().contents
        profiles = lib.biwn_DSP_router_profiles().contents
        report = {name: getattr(stats, name) for name, _ in Stats._fields_}
        report['profiles'] = {name: getattr(profiles, name) for name, _ in Profiles._fields_}
        report['profile_scope'] = 'Per-instruction kernel selection; shared instruction identities may match both programs. Switch count is not a count of DSP program reloads.'
        lib.biwn_DSP_external_stats.restype=c.POINTER(Stats)
        external=lib.biwn_DSP_external_stats().contents
        report['external_program']={name:getattr(external,name)for name,_ in Stats._fields_}
        report['profiles']['external']=external.owned
        report['core_counts'] = {name: getattr(core, 'BIWNDSP'+name+'InstructionCount')()
                                 for name in ['Owned', 'Original', 'Rejected']}
        report.update(library=candidate['library'], elapsed_seconds=time.monotonic()-started,
                      status='rejected' if report['errors'] or report['core_counts']['Rejected'] else 'completed_uncompared',
                      whole_game_complete=False)
        if report['uncovered']:
            lib.biwn_DSP_router_unknown_state.argtypes=[c.c_void_p]
            lib.biwn_DSP_router_unknown_state.restype=c.c_size_t
            buffer=c.create_string_buffer(32768)
            size=lib.biwn_DSP_router_unknown_state(buffer)
            assert 8496 <= size <= len(buffer)
            path=out/'DSP-first-uncovered-state.bin'
            path.write_bytes(buffer.raw[:size])
            report['first_uncovered_state']=str(path)
        core.BIWNSetDSPInstructionOwner(OWNER())
        (out/'DSP-owner-report.json').write_text(json.dumps(report, indent=2)+'\n')
        return report

    return callback, lib, host, finish
