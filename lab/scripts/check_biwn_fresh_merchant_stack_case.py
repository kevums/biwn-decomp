"""Compare the fresh-route missing MOVE instruction with the pinned native CPU.

Vary all CCR combinations and both stack banks. This is an instruction gate,
not a full-route or whole-game result.
"""
import ctypes as c
import json
import random
from pathlib import Path
from datetime import datetime, timezone
import check_biwn_media_setup_cpu as media

ROOT = Path(__file__).resolve().parents[1]


def main():
    candidate = json.loads((ROOT/'verification/fresh-merchant-CPU-experimental-candidate.json').read_text())
    owner = json.loads((ROOT/'verification/DSP-owner-experimental-candidate.json').read_text())
    core = Path(owner['directory'])/'source/virtualjaguar_libretro.dylib'
    # The owner manifest may already identify the source directory.
    if not core.exists():
        core = Path(owner['directory'])/'virtualjaguar_libretro.dylib'
    assert core.exists(), core
    oracle = media.scheduler.Native(diagnostic_core=core)
    runtime = media.Runtime.__new__(media.Runtime)
    runtime.oracle, runtime.device, runtime.core = oracle, oracle.device, oracle.lib
    lib = c.CDLL(candidate['library'])
    fn = getattr(lib, candidate['function'])
    fn.argtypes = [c.POINTER(media.Bus), c.POINTER(media.CPU), media.W8, media.world_cpu.SERVICE, c.c_void_p]
    fn.restype = c.c_int
    warm = Path(candidate['warm_RAM_source']).read_bytes()
    assert warm[0x1a402:0x1a406] == bytes.fromhex('3f3c0002')
    rng = random.Random(0x1a402)
    cases = 0
    for sr in list(range(32)) + list(range(0x2000, 0x2020)):
        initial = media.CPU()
        initial.registers[:] = [rng.getrandbits(32) for _ in range(16)]
        initial.usp, initial.ssp, initial.sr, initial.pc = 0x180800, 0x1e0000, sr, 0x1a402
        initial.registers[15] = initial.ssp if sr & 0x2000 else initial.usp
        runtime.device.seed(warm, 0)
        runtime.seed_cpu(initial)
        runtime.core.m68k_execute(1)
        native_cpu, native_ram = runtime.cpu(), runtime.device.ram()
        memory = bytearray(warm)
        def reader(width):
            def read(_, address, out):
                if address + width > len(memory): return 1
                out[0] = int.from_bytes(memory[address:address+width], 'big')
                return 0
            return read
        def writer(width):
            def write(_, address, value):
                if address + width > len(memory): return 1
                memory[address:address+width] = value.to_bytes(width, 'big')
                return 0
            return write
        world = media.scheduler.cleanup.world
        callbacks = [world.R8(reader(1)), world.R16(reader(2)), world.R32(reader(4)),
                     world.W16(writer(2)), world.W32(writer(4)), media.W8(writer(1))]
        bus = media.Bus(*callbacks[:5], world.CALL(), None, 0)
        translated = media.CPU.from_buffer_copy(bytes(initial))
        status = fn(c.byref(bus), c.byref(translated), callbacks[5], media.world_cpu.SERVICE(), None)
        assert status == 0, (sr, status)
        assert media.scheduler.cpu_dict(translated) == media.scheduler.cpu_dict(native_cpu), sr
        assert bytes(memory) == native_ram, sr
        cases += 1
    oracle.close()
    result = dict(status='original_instruction_comparison_pass', cases=cases,
                  PC='0x1a402', instruction='MOVE.W #2,-(A7)',
                  checked=['all CCR combinations', 'user and supervisor stack banks', 'all CPU registers', 'full main RAM'],
                  candidate=candidate['library'], core=str(core),
                  recorded_at=datetime.now(timezone.utc).isoformat(), whole_game_complete=False)
    (ROOT/'verification/fresh-merchant-stack-case-checks.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
