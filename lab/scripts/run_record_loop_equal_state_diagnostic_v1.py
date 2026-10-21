"""Bounded saved-state diagnostic, never a fresh-boot or promotion gate.

Each origin has a native, original-scene and unchanged replica lane. Restore
the complete original snapshot before changing only the ten scene-entry code
bytes when needed. No player, camera, timer, GPU or task state is normalized.
"""
import argparse, ctypes as c, hashlib, json, os, subprocess
from datetime import datetime, timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT, V, read, save, sha
from probe_biwn_fresh_CD_boot import Game, Variable, write_video_PNG


class CPU(c.Structure):
    _fields_ = [('registers', c.c_uint32 * 16), ('pc', c.c_uint32),
                ('usp', c.c_uint32), ('ssp', c.c_uint32), ('sr', c.c_uint16)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--origin', choices=['candidate', 'control'], required=True)
    ap.add_argument('--lane', choices=['native', 'original', 'replica'], required=True)
    args = ap.parse_args()
    jp = V / f'record-loop-matrix-268-fresh-{args.origin}-current.json'
    job = read(jp)
    assert job['status'] == 'terminal_fresh_matrix_route_coverage_pass_pending_review'
    assert job['all_monitors_clear_and_quiescent']
    report = read(job['report'])
    base = Path(job['directory']) / 'measurement'
    bp = V / 'native-record-loop-image-disc-build-v1-current.json'
    build = read(bp)
    inputs = [Path(__file__), jp, bp, Path(job['report']), Path(report['core']),
              Path(report['disc']), base / 'state-final.bin', base / 'RAM-final.bin',
              base / 'video-final.xrgb8888', Path(build['derived_stage']),
              Path(build['component']), ROOT / 'render-assets/biwn-inventory-baseline.bin']
    assert sha(report['core']) == report['core_sha256']
    assert sha(report['disc']) == report['disc_sha256']
    assert sha(base / 'state-final.bin') == report['final_serialized_state_sha256']
    assert sha(base / 'RAM-final.bin') == report['final_RAM_sha256']
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out = V / 'record-loop-equal-state-diagnostic-v1' / (stamp + '-' + args.origin + '-' + args.lane)
    out.mkdir(parents=True)
    pointer = V / f'record-loop-equal-state-{args.origin}-{args.lane}-v1-current.json'
    state = dict(status='running_saved_state_diagnostic', directory=str(out), pid=os.getpid(),
                 origin=args.origin, lane=args.lane, frames=0, snapshot_restores=1,
                 fresh_boot=False, host_pose_or_timer_writes=0, host_code_bytes_changed=0,
                 new_predictions=0, new_training=False, gameplay_promotion=False,
                 source_sha256={str(p): sha(p) for p in inputs})
    def mark():
        save(out / 'protocol.json', state)
        save(pointer, state)
    mark()
    errors = []
    video = dict(raw=(base / 'video-final.xrgb8888').read_bytes(), **{
        k: report['video'][k] for k in ['width', 'height', 'pitch']})
    audio = dict(frames=0, nonzero_samples=0)
    system = out / 'empty-system'; system.mkdir()
    saves = out / 'private-saves'; saves.mkdir()
    paths = {9: str(system).encode(), 30: str(system).encode(), 31: str(saves).encode()}
    options = {k.encode(): v.encode() for k, v in report['requested_options'].items()}
    ENV = c.CFUNCTYPE(c.c_bool, c.c_uint, c.c_void_p)
    VIDEO = c.CFUNCTYPE(None, c.c_void_p, c.c_uint, c.c_uint, c.c_size_t)
    AUDIO = c.CFUNCTYPE(None, c.c_int16, c.c_int16)
    BATCH = c.CFUNCTYPE(c.c_size_t, c.c_void_p, c.c_size_t)
    POLL = c.CFUNCTYPE(None)
    INPUT = c.CFUNCTYPE(c.c_int16, c.c_uint, c.c_uint, c.c_uint, c.c_uint)
    def environment(cmd, data):
        try:
            cmd &= 255
            if cmd in paths:
                c.cast(data, c.POINTER(c.c_char_p))[0] = paths[cmd]; return True
            if cmd == 10: return c.cast(data, c.POINTER(c.c_uint))[0] == 1
            if cmd in [16, 67]: return True
            if cmd == 15:
                var = c.cast(data, c.POINTER(Variable)).contents
                var.value = options.get(var.key); return var.value is not None
            if cmd == 17:
                c.cast(data, c.POINTER(c.c_bool))[0] = False; return True
            return False
        except BaseException as error:
            errors.append(repr(error)); return False
    def refresh(data, width, height, pitch):
        if data and data != c.c_void_p(-1).value and width and height:
            assert pitch >= width * 4
            video.update(raw=c.string_at(data, pitch * height), width=width, height=height, pitch=pitch)
    def sample(left, right):
        audio['frames'] += 1
        audio['nonzero_samples'] += int(left != 0) + int(right != 0)
    def batch(data, count):
        audio['frames'] += count
        if data:
            raw = c.string_at(data, count * 4)
            audio['nonzero_samples'] += sum(raw[i:i+2] != b'\0\0' for i in range(0, len(raw), 2))
        return count
    callbacks = [ENV(environment), VIDEO(refresh), AUDIO(sample), BATCH(batch), POLL(lambda: None),
                 INPUT(lambda port, device, index, button: 0)]
    core = c.CDLL(report['core'])
    for name, callback in zip(['environment', 'video_refresh', 'audio_sample', 'audio_sample_batch', 'input_poll', 'input_state'], callbacks):
        getattr(core, 'retro_set_' + name)(callback)
    core.retro_load_game.argtypes = [c.POINTER(Game)]; core.retro_load_game.restype = c.c_bool
    core.retro_unserialize.argtypes = [c.c_void_p, c.c_size_t]; core.retro_unserialize.restype = c.c_bool
    core.retro_serialize_size.restype = c.c_size_t
    core.retro_serialize.argtypes = [c.c_void_p, c.c_size_t]; core.retro_serialize.restype = c.c_bool
    core.retro_get_memory_data.argtypes = [c.c_uint]; core.retro_get_memory_data.restype = c.c_void_p
    core.BIWNReadCPUState.argtypes = [c.POINTER(CPU)]
    native = Path(build['derived_stage']).read_bytes()[0x17e0e-0x4000:0x17e18-0x4000]
    original = (ROOT / 'render-assets/biwn-inventory-baseline.bin').read_bytes()[0x17e0e:0x17e18]
    assert len(native) == len(original) == 10 and native != original
    symbols = build['shared_Deck_symbols']
    addresses = [0x17e0e, symbols['biwn_v4_scene'], symbols['biwn_v4_scene_return'],
                 symbols['biwn_v33_records_begin'], symbols['biwn_v33_records_end'],
                 symbols['biwn_v4_capture_scene_record_matrix'], 0xe220]
    observer_source = out / 'observer.c'
    observer_source.write_text('#include <stdint.h>\nstatic uint64_t counts[7];\n'
        + 'static const uint32_t addresses[7]={' + ','.join(str(x) + 'u' for x in addresses) + '};\n'
        + 'int32_t observe(uint32_t pc){for(unsigned i=0;i<7;i++)if(pc==addresses[i])counts[i]++;return 0;}\n'
        + 'uint64_t stat(unsigned i){return i<7?counts[i]:0;}\n')
    library = out / 'observer.dylib'
    result = subprocess.run(['clang', '-dynamiclib', '-O2', '-std=c99', '-Wall', '-Wextra', '-Werror',
                             str(observer_source), '-o', str(library)], capture_output=True, text=True)
    (out / 'compiler.log').write_text(result.stdout + result.stderr)
    assert result.returncode == 0, result.stderr
    observer = c.CDLL(str(library)); observer.stat.argtypes = [c.c_uint]; observer.stat.restype = c.c_uint64
    OWNER = c.CFUNCTYPE(c.c_int32, c.c_uint32)
    owner = OWNER(('observe', observer)); core.BIWNSetCPUExecOwner.argtypes = [OWNER, c.c_int]
    def digest(name):
        fn = getattr(core, name + 'StateSave'); fn.argtypes = [c.c_void_p]; fn.restype = c.c_size_t
        data = c.create_string_buffer(65536); size = fn(data)
        assert 0 < size <= len(data)
        return hashlib.sha256(data.raw[:size]).hexdigest()
    def cpu():
        value = CPU(); core.BIWNReadCPUState(c.byref(value))
        return dict(registers=list(value.registers), pc=value.pc, usp=value.usp, ssp=value.ssp, sr=value.sr)
    def pose(memory):
        u = lambda a, w=2: int.from_bytes(memory[a:a+w], 'big')
        return dict(integer_XZ=[u(0x49c50,4), u(0x49c56,4)],
                    player_fraction_words=[u(a) for a in [0x49c5a,0x49c5c,0x49c5e]],
                    camera_words=[u(a) for a in [0x49b8c,0x49b8e,0x49b90]],
                    camera_fraction_words=[u(a) for a in [0x49b92,0x49b94,0x49b96]],
                    heading=u(0x49cba,1), scene=u(0x49c64), mode=u(0x49c60))
    loaded = False
    core.retro_init(); core.retro_set_controller_port_device(0, 1)
    try:
        assert core.retro_load_game(c.byref(Game(report['disc'].encode(), None, 0, None))); loaded = True
        rom = c.c_void_p.in_dll(core, 'jaguarMainROM').value
        assert hashlib.sha256(c.string_at(rom, 0x40000)).hexdigest() == report['staged_cart_ROM_sha256']
        blob = (base / 'state-final.bin').read_bytes()
        assert core.retro_unserialize(c.create_string_buffer(blob), len(blob))
        roundtrip = c.create_string_buffer(core.retro_serialize_size())
        assert core.retro_serialize(roundtrip, len(roundtrip)) and roundtrip.raw == blob
        ram = core.retro_get_memory_data(2); before = c.string_at(ram, 0x200000)
        assert before == (base / 'RAM-final.bin').read_bytes()
        start_cpu = cpu(); assert not 0x17e0e <= start_cpu['pc'] < 0x17e18
        start = dict(CPU=start_cpu, GPU=digest('GPU'), DSP=digest('DSP'), pose=pose(before),
                     RAM_sha256=hashlib.sha256(before).hexdigest(), video_sha256=sha(base / 'video-final.xrgb8888'))
        source_native = args.origin == 'candidate'
        target_native = source_native if args.lane == 'replica' else args.lane == 'native'
        expected, replacement = (native if source_native else original), (native if target_native else original)
        assert before[0x17e0e:0x17e18] == expected
        if expected != replacement:
            c.memmove(ram + 0x17e0e, replacement, 10)
            state['host_code_bytes_changed'] = 10
        after = c.string_at(ram, 0x200000)
        assert after == before[:0x17e0e] + replacement + before[0x17e18:]
        assert cpu() == start_cpu and digest('GPU') == start['GPU'] and digest('DSP') == start['DSP']
        save(out / 'initial-state.json', start)
        core.BIWNSetCPUExecOwner(owner, 0)
        rows = []
        for frame in range(1, 181):
            core.retro_run(); assert not errors, errors
            memory = c.string_at(ram, 0x200000)
            rows.append(dict(frame=frame, CPU=cpu(), GPU=digest('GPU'), DSP=digest('DSP'),
                             pose=pose(memory), video_sha256=hashlib.sha256(video['raw']).hexdigest(),
                             RAM_sha256=hashlib.sha256(memory).hexdigest(),
                             counters=[observer.stat(i) for i in range(7)]))
            if frame % 60 == 0:
                state['frames'] = frame; mark()
        core.BIWNSetCPUExecOwner(OWNER(), 0)
        component = Path(build['component']).read_bytes(); resident = build['resident_address']
        for lo, hi in [(resident, build['arena_address']), (build['arena_end'], build['deck_arena_address'])]:
            assert memory[lo:hi] == component[lo-resident:hi-resident]
        for address, count, stride, fences in [
                (build['arena_address'],102,256,[[0,16],[240,256]]),
                (build['deck_arena_address'],101,1024,build['deck_fences']),
                (build['outer_arena_address'],101,build['outer_arena_stride'],build['outer_fences'])]:
            for slot in range(count):
                at = address + slot * stride
                for lo, hi in fences:
                    assert memory[at+lo:at+hi] == component[at-resident+lo:at-resident+hi]
        assert rows[-1]['counters'][0] > 0, 'Scene entry never exercised'
        assert rows[-1]['counters'][1] > 0 if target_native else rows[-1]['counters'][1] == 0
        save(out / 'frames.json', rows)
        (out / 'RAM-final.bin').write_bytes(memory)
        (out / 'video-final.xrgb8888').write_bytes(video['raw'])
        write_video_PNG(out / 'final.png', video['raw'], video['width'], video['height'], video['pitch'])
        assert core.retro_serialize(roundtrip, len(roundtrip))
        (out / 'state-final.bin').write_bytes(roundtrip.raw)
        state.update(status='terminal_saved_state_equal_origin_diagnostic_pending_review', frames=len(rows),
                     restored_state_and_RAM_exact=True, target_native=target_native, pose_and_timer_untouched=True,
                     immutable_component_and_arena_fences_unchanged=True, counters=rows[-1]['counters'], audio=audio,
                     initial_state=start, final_state=rows[-1], video={k:video[k]for k in ['width','height','pitch']},
                     scope='180 zero-pad frames from an exact terminal matrix snapshot. Only the ten scene-entry code bytes may differ. Read-only instruction counts;no source CPU/GPU/DSP substitution. Snapshot and code intervention diagnostic only;not fresh gameplay,original-console fidelity or grounds to waive the failed matrix gate.')
        state['source_sha256'].update({str(p):sha(p) for p in [observer_source, library, out/'initial-state.json',
                                      out/'frames.json', out/'RAM-final.bin', out/'video-final.xrgb8888', out/'state-final.bin']})
        mark(); print(state['status'], args.origin, args.lane, state['counters'], flush=True)
    except BaseException as error:
        state.update(status='terminal_saved_state_diagnostic_failed', error=repr(error)); mark(); raise
    finally:
        if loaded: core.retro_unload_game()
        core.retro_deinit()


if __name__ == '__main__': main()
