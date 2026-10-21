"""Execute the actual new image's wide startup, both arenas, and raised heap.

Startup uses pinned M68000 and Unicorn with independent complete-RAM oracle,
dirty resident/arena preconditions and saved stack bytes included. The heap
comparison uses original instructions with only five declared floor operands
changed. No game frame, arbitrary IRQ, audio or physical console is qualified.
"""
import hashlib
import os
import random
import struct
from datetime import datetime, timezone
from pathlib import Path
from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN
from unicorn.m68k_const import *
import check_biwn_scheduler as scheduler
from publish_scene_reset_fresh_v1 import ROOT, V, read, save, sha

REGS = [UC_M68K_REG_D0, UC_M68K_REG_D1, UC_M68K_REG_D2, UC_M68K_REG_D3, UC_M68K_REG_D4, UC_M68K_REG_D5, UC_M68K_REG_D6, UC_M68K_REG_D7, UC_M68K_REG_A0, UC_M68K_REG_A1, UC_M68K_REG_A2, UC_M68K_REG_A3, UC_M68K_REG_A4, UC_M68K_REG_A5, UC_M68K_REG_A6, UC_M68K_REG_A7]


def main():
    bp = V/'frame-acquire-phased-disc-build-v1-current.json'
    b = read(bp)
    for path, digest in b['source_sha256'].items():
        assert sha(path) == digest, path
    for key in ['component', 'derived_stage', 'derived_disc']:
        assert sha(b[key]) == b[key+'_sha256']
    assert b['startup_copy_width_bytes'] == b['startup_clear_width_bytes'] == 4
    assert b['copy_component_bytes'] > 131072 and b['staging_bytes_cleared'] > 131072
    out = V/'frame-acquire-phased-image-startup-heap-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    pointer = V/'frame-acquire-phased-image-startup-heap-v1-current.json'
    state = dict(status='running_actual_image_startup', pid=os.getpid(), directory=str(out), native_startup_cases=0, Unicorn_startup_cases=0, heap_initialize_cases=0, game_frames=0, new_predictions=0, optimizer_updates=0)

    def mark():
        save(out/'protocol.json', state)
        save(pointer, state)

    mark()
    print(out, flush=True)
    n = scheduler.Native()
    rng = random.Random(0x17c72422d8)
    startup_rows, init_rows = [], []
    session = Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    original_stage = (session/'nextstage-68000-candidate.bin').read_bytes()
    stage = Path(b['derived_stage']).read_bytes()
    payload = Path(b['component']).read_bytes()

    def setup(image, regs, sr, entry):
        n.device.seed(bytes(image), 0)
        assert n.device.ram() == image
        l = n.lib
        l.m68k_pulse_reset()
        l.m68k_set_irq(0)
        l.m68k_set_reg(17, 0x2000)
        l.m68k_set_reg(15, regs[15] if sr & 0x2000 else 0x1fd000)
        l.m68k_set_reg(17, 0)
        l.m68k_set_reg(15, 0x1fc000 if sr & 0x2000 else regs[15])
        l.m68k_set_reg(17, sr)
        for i, value in enumerate(regs):
            l.m68k_set_reg(i, value)
        l.m68k_set_reg(16, entry)

    def cpu():
        values = [n.lib.m68k_get_reg(None, i) for i in range(18)]
        sr = values[17]
        return values + [n.prefix[16] if sr & 0x2000 else values[15], values[15] if sr & 0x2000 else n.prefix[17]]

    def native_start(image, regs, sr, installed):
        setup(image, regs, sr, 0x4000)
        limit = 2*(b['copy_component_bytes']//4+b['staging_bytes_cleared']//4+b['deck_arena_bytes']//2+b['outer_arena_bytes']//2)+64*101+256 if installed else 128
        for step in range(limit):
            pc = n.lib.m68k_get_reg(None, 16)
            if pc == 0x400a:
                return cpu(), n.device.ram(), step
            assert pc in [0x4000,0x4004] or (installed and (b['staging_address'] <= pc < b['staging_address']+40 or b['resident_address'] <= pc < b['resident_address']+b['copy_component_bytes'])), hex(pc)
            n.lib.m68k_execute(1)
        raise AssertionError(('Startup bound', hex(n.lib.m68k_get_reg(None,16)),limit))

    try:
        for variant, dirty in enumerate([0xa7, 0x5c, 0xcc]):
            for flags in [0,31]:
                original = bytearray(0x200000)
                original[0x4000:0x100000] = original_stage
                original[b['resident_address']:b['heap_start']] = bytes([dirty]) * b['component_bytes']
                installed = bytearray(original)
                installed[0x4000:0x100000] = stage
                regs = [rng.getrandbits(32) for _ in REGS]
                regs[15] = 0x180000
                expected_cpu, _, _ = native_start(original, regs, 0x2000|flags, False)
                actual, ram, steps = native_start(installed, regs, 0x2000|flags, True)
                assert actual == expected_cpu
                expected = bytearray(installed)
                expected[b['resident_address']:b['heap_start']] = payload
                expected[b['staging_address']:b['staging_address']+b['staging_bytes_cleared']] = bytes(b['staging_bytes_cleared'])
                expected[0x1fffc4:0x200000] = struct.pack('>15I', *regs[:15])
                assert ram == expected, [(hex(i),a,z) for i,(a,z) in enumerate(zip(ram,expected)) if a != z][:24]
                assert ram[b['native_input_address']:b['native_input_address']+b['native_input_bytes']] == Path(b['native_input_payload']).read_bytes()
                assert ram[b['resource_arena_code_address']:b['resource_arena_code_address']+b['resource_arena_code_bytes']] == Path(b['resource_arena_payload']).read_bytes()
                state['native_startup_cases'] += 1
                mark()
                uc = Uc(UC_ARCH_M68K, UC_MODE_BIG_ENDIAN)
                uc.ctl_set_cpu_model(UC_CPU_M68K_M68000)
                uc.mem_map(0,0x200000)
                uc.mem_write(0,bytes(installed))
                uc.reg_write(UC_M68K_REG_SR,0)
                uc.reg_write(UC_M68K_REG_A7,0x1fc000)
                uc.reg_write(UC_M68K_REG_SR,0x2000|flags)
                for reg,value in zip(REGS,regs):
                    uc.reg_write(reg,value)
                uc.emu_start(0x4000,0x400a,count=1000000,timeout=20000000)
                assert uc.reg_read(UC_M68K_REG_PC) == 0x400a
                assert bytes(uc.mem_read(0,0x200000)) == expected
                assert [uc.reg_read(reg) for reg in REGS] == actual[:16]
                assert uc.reg_read(UC_M68K_REG_SR) == actual[17] == 0x2700
                uc.reg_write(UC_M68K_REG_SR,0)
                assert uc.reg_read(UC_M68K_REG_A7) == actual[18] == 0x1fc000
                state['Unicorn_startup_cases'] += 1
                startup_rows.append(dict(variant=variant,flags=flags,dirty_resident_byte=dirty,instructions=steps,CPU=actual,all_2MB_RAM_including_saved_stack_and_arenas_equal=True,expected_RAM_sha256=hashlib.sha256(expected).hexdigest(),both_CPU_cores=True))
                mark()
                print('startup',len(startup_rows),'/ 6',flush=True)
        baseline = (ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
        common = bytearray(baseline)
        common[0x4000:0x100000] = stage
        common[b['resident_address']:b['heap_start']] = payload
        block = bytearray(baseline[0x1557a:0x155c2])
        counts = []
        for delta,want in [(0,3),(4,1),(8,1)]:
            old = (0x15edc0+delta).to_bytes(4,'big')
            new = (b['heap_start']+delta).to_bytes(4,'big')
            indices = [i for i in range(len(block)-3) if block[i:i+4] == old]
            assert len(indices) == want
            for i in indices:
                block[i:i+4] = new
            counts.append(dict(delta=delta,operands=len(indices)))
        at = b['symbols']['biwn_native_heap_initialize']-b['resident_address']
        assert payload[at:at+len(block)] == block
        reference = bytearray(common)
        reference[0x1557a:0x155c2] = block
        sp, stop = 0x1e0000,0x1f0000
        for image in [reference,common]:
            image[sp:sp+4] = stop.to_bytes(4,'big')

        def initialize(image,regs,sr,new):
            setup(image,regs,sr,0x1557a)
            for steps in range(10000):
                pc = n.lib.m68k_get_reg(None,16)
                if pc == stop:
                    return cpu(),n.device.ram()
                assert (pc == 0x1557a or b['resident_address'] <= pc < b['resident_address']+b['copy_component_bytes']) if new else 0x1557a <= pc < 0x155c2
                n.lib.m68k_execute(1)
            raise AssertionError('Heap initializer bound')

        state['status'] = 'running_actual_image_heap_initialization'
        mark()
        for variant in range(3):
            for mode in [0,0x2000]:
                for flags in range(32):
                    regs = [rng.getrandbits(32) for _ in REGS]
                    regs[15] = sp
                    old, left = initialize(reference,regs,mode|flags,False)
                    actual, right = initialize(common,regs,mode|flags,True)
                    assert old == actual
                    comparable = bytearray(right)
                    comparable[0x1557a:0x155c2] = left[0x1557a:0x155c2]
                    assert comparable == left
                    floor = b['heap_start']
                    word = lambda address:int.from_bytes(right[address:address+4],'big')
                    assert word(0x112d60) == floor and word(0x112d64) == word(floor) == 0x1c0000-floor
                    assert word(floor+4) == word(floor+8) == 0 and not any(right[0x112960:0x112d60])
                    assert right[b['resident_address']:floor] == payload
                    init_rows.append(dict(variant=variant,mode=mode,flags=flags,CPU=actual,capacity=word(floor),complete_RAM_except_declared_reference_code_equal=True))
                    state['heap_initialize_cases'] = len(init_rows)
                    mark()
        save(out/'startup-cases.json',startup_rows)
        save(out/'heap-cases.json',init_rows)
        paths = [Path(__file__),bp,Path(b['component']),Path(b['derived_stage']),session/'nextstage-68000-candidate.bin',ROOT/'render-assets/biwn-inventory-baseline.bin',Path(scheduler.__file__),ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'tools/libbiwn-movement-device.dylib',out/'startup-cases.json',out/'heap-cases.json']
        state.update(status='terminal_actual_input_image_wide_startup_dual_CPU_and_heap_initialize_pass',original_heap_initializer_declared_operand_changes=counts,all_2MB_startup_RAM_checked=True,saved_stack_bytes_checked=True,dirty_arenas_cleared=True,input_payload_after_startup_exact=True,resource676_payload_after_startup_exact=True,heap_start=b['heap_start'],initial_heap_bytes=b['initial_heap_bytes'],heap_source_bytes_equal_after_five_operand_changes=True,source_sha256={str(p):sha(p) for p in paths},arbitrary_IRQ_qualified=False,gameplay_verified=False,physical_console_verified=False,scope=__doc__)
        mark()
        print({k:state[k] for k in ['status','native_startup_cases','Unicorn_startup_cases','heap_initialize_cases','initial_heap_bytes']},flush=True)
    except BaseException as error:
        save(out/'startup-completed-before-failure.json',startup_rows)
        save(out/'heap-completed-before-failure.json',init_rows)
        state.update(status='terminal_actual_input_image_startup_heap_failed',error=repr(error))
        mark()
        raise
    finally:
        n.close()


if __name__ == '__main__':
    main()
