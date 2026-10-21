"""Round-trip the actual fresh native-disc machine before controlled tests."""
import ctypes as c
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import check_biwn_world_movement_pipeline as hardware

ROOT = hardware.ROOT
V = ROOT / 'verification'
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_text())
def save(path, value): Path(path).write_text(json.dumps(value, indent=2) + '\n')

def main():
    out = V / 'native-Deck-fresh-machine-restore' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    print(out, flush=True)
    route_path = V / 'native-Deck-coordinate-v2-quiescent-candidate-current.json'
    route = read(route_path)
    assert route['status'].startswith('terminal_') and route['live_monitor_pass']
    folder = Path(route['directory']) / 'candidate'
    report_path = folder / 'report.json'
    report = read(report_path)
    core_path = Path(report['core'])
    disc = Path(report['disc'])
    state_path = folder / 'state-final.bin'
    ram_path = folder / 'RAM-final.bin'
    assert sha(core_path) == report['core_sha256']
    assert sha(disc) == report['disc_sha256']
    assert sha(state_path) == report['final_serialized_state_sha256']
    assert sha(ram_path) == report['final_RAM_sha256']
    device_build = read(V / 'mode3-world-render-device-build-current.json')
    device = hardware.Device(Path(device_build['library']), core=core_path)
    core = c.CDLL(str(core_path))
    try:
        class Game(c.Structure):
            _fields_ = [('path', c.c_char_p), ('data', c.c_void_p), ('size', c.c_size_t), ('meta', c.c_char_p)]
        core.retro_load_game.argtypes = [c.POINTER(Game)]
        core.retro_load_game.restype = c.c_bool
        assert core.retro_load_game(c.byref(Game(str(disc).encode(), None, 0, None)))
        blob = state_path.read_bytes()
        core.retro_unserialize.argtypes = [c.c_void_p, c.c_size_t]
        core.retro_unserialize.restype = c.c_bool
        assert core.retro_unserialize(c.create_string_buffer(blob), len(blob))
        core.retro_serialize_size.restype = c.c_size_t
        core.retro_serialize.argtypes = [c.c_void_p, c.c_size_t]
        core.retro_serialize.restype = c.c_bool
        copy = c.create_string_buffer(core.retro_serialize_size())
        assert core.retro_serialize(copy, len(copy)) and copy.raw == blob
        device.pointer = device.lib.lab_device_ram()
        assert device.ram() == ram_path.read_bytes()
        build_path = V / 'native-Deck-coordinate-disc-build-current.json'
        build = read(build_path)
        component = Path(build['component']).read_bytes()
        base = build['resident_address']
        # Entire immutable copy prefix outside the mutable GPU arena, plus
        # the never-used Deck arena, must still be exactly the installed image.
        ram = device.ram()
        ranges = [(base, build['arena_address']),
                  (build['arena_end'], build['deck_arena_address'])]
        for lo, hi in ranges:
            assert ram[lo:hi] == component[lo-base:hi-base], (hex(lo), hex(hi))
        lo = build['deck_arena_address']; hi = lo + build['deck_arena_bytes']
        assert ram[lo:hi] == component[lo-base:hi-base]
        core.GPUGetPC.restype = c.c_uint32
        core.GPUReadLong.argtypes = [c.c_uint32, c.c_uint32]
        core.GPUReadLong.restype = c.c_uint32
        state = dict(status='terminal_fresh_native_disc_machine_byte_exact_restore_verified',
                     recorded_at=datetime.now(timezone.utc).isoformat(), directory=str(out),
                     route=str(route_path), route_sha256=sha(route_path),
                     checkpoint_report=str(report_path), checkpoint_report_sha256=sha(report_path),
                     core_path=str(core_path), core_sha256=sha(core_path),
                     disc_path=str(disc), disc_sha256=sha(disc),
                     state_path=str(state_path), state_sha256=sha(state_path),
                     RAM_path=str(ram_path), RAM_sha256=sha(ram_path),
                     build_path=str(build_path), build_sha256=sha(build_path),
                     GPU_PC=hex(core.GPUGetPC()),
                     GPU_mailbox={hex(a): hex(core.GPUReadLong(a, 0)) for a in [0xf03200, 0xf03204, 0xf03208]},
                     immutable_resident_ranges=ranges, installed_unused_Deck_arena_exact=True,
                     new_instructions_executed=False, new_training=False,
                     whole_game_complete=False, source_sha256={str(Path(__file__)): sha(__file__)},
                     scope='Actual fresh candidate-disc run final machine, matching core and mounted derived CDI. Full serialized state roundtrip and 2MB RAM exact before any controlled test edits. No continuation or coordinate activation claim.')
        save(out / 'report.json', state)
        save(V / 'native-Deck-fresh-machine-restore-current.json', state)
        print(state['status'], state['GPU_PC'], state['GPU_mailbox'], flush=True)
    finally:
        device.close()

if __name__ == '__main__': main()
