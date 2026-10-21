"""Complete string formatting helper: facts, native C, full CPU/RAM and bus order."""
import argparse
import copy
import ctypes as c
import hashlib
import json
import os
import random
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
from check_biwn_native_resource_release import REGS
from check_biwn_scheduler import Native
from check_fact_guided_candidate import DRIVER as OLD_DRIVER
import m68k_fact_packet_v2 as facts
from lower_m68k_facts_to_C_v2 import lower

ROOT = facts.ROOT
NATIVE = ROOT / 'projects/black-ice-white-noise/restoration/native-m68k'
BASE, ENTRY, END, SP, STOP = 0x148000, 0x1b1a8, 0x1b200, 0x1e0000, 0x1f0000
DEST, SOURCE, COUNT = 0x120000, 0x130000, 0x138000
DRIVER = OLD_DRIVER.replace('coverage[64]', 'coverage[256]').replace('entry+64', 'entry+88')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')


class Stats(c.Structure):
    _fields_ = [('status', c.c_uint32), ('pc', c.c_uint32), ('steps', c.c_uint64),
                ('cycles', c.c_uint64), ('coverage', c.c_uint8 * 256)]


def vectors():
    rng = random.Random(ENTRY)
    rows = []
    strings = ['null', 'empty', 'one', 'seven', 'high_bytes']
    for mode in (0, 0x2000):
        for flags in range(32):
            for i, (left, width) in enumerate((a, b) for a in [0, 1, 2, 7, 0x8000, 0xffff]
                                             for b in [0, 1, 3, 0x8000, 0xffff]):
                regs = [rng.getrandbits(32) for _ in range(15)]
                regs[2] = [0, 1, 0x80000000, 0x7fffffff][(flags+i) % 4]
                rows.append(dict(left=left, width=width, string=strings[(flags+i) % len(strings)],
                                 incoming=regs, sr=mode|flags))
        for flags in (0, 16):
            for left, width, string in [(0x7fff, 0x7fff, 'empty'), (0x7fff, 0x8000, 'one'),
                                        (0x7fff, 0, 'long'), (0x7fff, 0x7fff, 'long')]:
                rows.append(dict(left=left, width=width, string=string,
                                 incoming=[rng.getrandbits(32) for _ in range(15)], sr=mode|flags))
    # Defined overlapping source/destination ranges; no code/counter/stack alias.
    for offset in (-2, 0, 2):
        for flags in (0, 16, 31):
            rows.append(dict(left=16, width=8, string='seven', overlap=offset,
                             incoming=[rng.getrandbits(32) for _ in range(15)], sr=flags))
    return rows


def seed(image, case):
    ram = bytearray(image)
    ram[DEST:DEST+0x8000] = bytes([0xa5]) * 0x8000
    ram[SOURCE-16:SOURCE+0x8010] = bytes([0xa5]) * 0x8020
    content = {'null': b'', 'empty': b'', 'one': b'A', 'seven': b'abcdefg',
               'high_bytes': bytes([0x80, 0xff, 0x7f]), 'long': b'A'*0x7fff}[case['string']]
    ram[SOURCE:SOURCE+len(content)+1] = content+b'\0'
    ram[COUNT:COUNT+2] = case['left'].to_bytes(2, 'big')
    dest = SOURCE+case['overlap'] if 'overlap' in case else DEST
    source = 0 if case['string'] == 'null' else SOURCE
    args = (STOP.to_bytes(4, 'big') + dest.to_bytes(4, 'big') + source.to_bytes(4, 'big')
            + COUNT.to_bytes(4, 'big') + case['width'].to_bytes(2, 'big'))
    ram[SP:SP+len(args)] = args
    return bytes(ram)


def normalize(ram, reference, length):
    result = bytearray(ram)
    for start, size in [(BASE, length), (ENTRY, 8), (SP-8192, 8192-8)]:
        result[start:start+size] = reference[start:start+size]
    return bytes(result)


def allowed(pc, length, original):
    return ENTRY <= pc < END if original else pc == ENTRY or BASE <= pc < BASE+length


def native(engine, driver, image, case, length, original):
    engine.device.seed(seed(image, case), 0)
    lib = engine.lib
    lib.m68k_pulse_reset(); lib.m68k_set_irq(0)
    supervisor = bool(case['sr'] & 0x2000)
    lib.m68k_set_reg(17, 0x2000); lib.m68k_set_reg(15, SP if supervisor else 0x1ff000)
    lib.m68k_set_reg(17, 0); lib.m68k_set_reg(15, 0x1fe000 if supervisor else SP)
    lib.m68k_set_reg(17, case['sr'])
    for index, value in enumerate(case['incoming']+[SP]):
        lib.m68k_set_reg(index, value)
    lib.m68k_set_reg(16, ENTRY)
    stats = Stats()
    budget = min(50000000, 50000+1024*(case['left'] if case['left'] < 32768 else 0))
    status = driver.run(c.cast(lib.m68k_execute, c.c_void_p), c.cast(lib.m68k_get_reg, c.c_void_p),
                        STOP, SP, BASE, BASE+length, ENTRY, int(original), budget, c.byref(stats))
    assert status == 0, ('native instruction boundary/budget', original, status, hex(stats.pc), stats.steps)
    cpu = [lib.m68k_get_reg(None, index) for index in range(18)]
    cpu += [engine.prefix[16] if supervisor else cpu[15], cpu[15] if supervisor else engine.prefix[17]]
    ram = engine.device.ram()
    if not original:
        assert ram[BASE:BASE+length] == image[BASE:BASE+length], 'candidate modified executable bytes'
    return ram, cpu, {ENTRY+i for i, seen in enumerate(stats.coverage) if seen}, stats.steps


def trace(image, case, length, original, changing=None):
    cpu = Uc(UC_ARCH_M68K, UC_MODE_BIG_ENDIAN)
    cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000)
    cpu.mem_map(0, 0x200000); cpu.mem_write(0, seed(image, case))
    for reg, value in zip(REGS, case['incoming']+[SP]):
        cpu.reg_write(reg, value)
    cpu.reg_write(UC_M68K_REG_SR, case['sr']); cpu.reg_write(UC_M68K_REG_A7, SP)
    events, queues = [], copy.deepcopy(changing or {})
    def ignored(address, width):
        return SP-8192 <= address and address+width <= SP-8 or BASE <= address and address+width <= BASE+length
    def read(engine, access, address, width, value, _):
        if ignored(address, width): return
        queue = queues.get((address, width))
        if queue:
            engine.mem_write(address, queue.pop(0).to_bytes(width, 'big'))
        events.append(['r', address, width, int.from_bytes(engine.mem_read(address, width), 'big')])
    def write(engine, access, address, width, value, _):
        if not ignored(address, width):
            events.append(['w', address, width, value & ((1 << (8*width))-1)])
    def code(engine, address, width, _):
        assert allowed(address, length, original), hex(address)
    cpu.hook_add(UC_HOOK_CODE, code); cpu.hook_add(UC_HOOK_MEM_READ, read); cpu.hook_add(UC_HOOK_MEM_WRITE, write)
    cpu.emu_start(ENTRY, STOP, count=50000000, timeout=30000000)
    assert cpu.reg_read(UC_M68K_REG_PC) == STOP, 'ordered trace failed to return'
    ram = bytes(cpu.mem_read(0, 0x200000))
    if not original: assert ram[BASE:BASE+length] == image[BASE:BASE+length]
    return ram, events


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--limit', type=int)
    args = parser.parse_args()
    out = ROOT / 'verification/native-format-string' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True); print(out, flush=True)
    image_path = ROOT / 'render-assets/biwn-inventory-baseline.bin'
    assert sha(image_path) == 'f3f70dadee1b6241419da361460208337dbbf9333e2da977144e8c97923a20d3'
    image = image_path.read_bytes(); assert image[0x1b1a0:ENTRY] == b'(null)\0\0'
    packet = facts.packet(image, ENTRY, END)
    save(out/'instruction-facts.json', packet)
    source = args.source.resolve() if args.source else out/'format-string-lifted.c'
    if not args.source: source.write_text(lower(packet))
    snapshot = out/'source-snapshot'; snapshot.mkdir()
    for path in [source, Path(__file__), Path(facts.__file__), NATIVE/'format-string-native.h',
                 NATIVE/'format-string-shim.S', NATIVE/'m68k-fact-helpers-v2.h',
                 ROOT/'scripts/lower_m68k_facts_to_C_v2.py']:
        shutil.copy2(path, snapshot/path.name)
    state = dict(status='prepared', pid=os.getpid(), directory=str(out), source=str(source), source_sha256=sha(source),
                 source_origin='external_candidate' if args.source else 'deterministic_typed_instruction_lifter',
                 local_model_authored_C=False, packet_sha256=sha(out/'instruction-facts.json'),
                 source_accepted=False, whole_game_complete=False, game_frames=0)
    def mark():
        save(out/'protocol.json', state); save(ROOT/'verification/native-format-string-active.json', state)
    mark()
    try:
        prefix = str(ROOT/'tools/m68k-elf/bin/m68k-elf-')
        commands = [[prefix+'gcc', '-m68000', '-msoft-float', '-std=c99', '-Os', '-ffreestanding', '-fno-pie',
                     '-fno-common', '-Wall', '-Wextra', '-Werror', '-I'+str(NATIVE), '-c', str(source), '-o', str(out/'body.o')],
                    [prefix+'as', '-m68000', '-o', str(out/'shim.o'), str(NATIVE/'format-string-shim.S')],
                    [prefix+'ld', '-Ttext='+hex(BASE), '-e', 'biwn_native_format_string', '-o', str(out/'candidate.elf'), str(out/'shim.o'), str(out/'body.o')],
                    [prefix+'objcopy', '-O', 'binary', str(out/'candidate.elf'), str(out/'candidate.bin')]]
        (out/'driver.c').write_text(DRIVER)
        commands.append(['clang', '-std=c99', '-O2', '-dynamiclib', str(out/'driver.c'), '-o', str(out/'driver.dylib')])
        save(out/'commands.json', commands)
        with (out/'build.log').open('w') as log:
            for command in commands:
                result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
                assert result.returncode == 0, command
        payload = (out/'candidate.bin').read_bytes()
        candidate = bytearray(image); candidate[BASE:BASE+len(payload)] = payload
        candidate[ENTRY:ENTRY+8] = b'\x4e\xf9'+BASE.to_bytes(4, 'big')+b'\x4e\x71'
        driver = c.CDLL(str(out/'driver.dylib'))
        driver.run.argtypes = [c.c_void_p, c.c_void_p, *([c.c_uint32]*6), c.c_uint64, c.POINTER(Stats)]
        driver.run.restype = c.c_int
        cases = vectors()
        if args.limit: cases = cases[:args.limit]
        save(out/'fixtures.json', cases)
        engine = Native(); rows, coverage, changed = [], set(), 0
        state['status'] = 'running_facts_and_native_C_gates'; mark()
        try:
            for index, case in enumerate(cases):
                original = native(engine, driver, image, case, len(payload), True)
                compiled = native(engine, driver, candidate, case, len(payload), False)
                typed = facts.execute(packet, seed(image, case), case['incoming'], case['sr'], SP)
                fact_cpu = typed['registers']+[typed['pc'], typed['sr']]
                fact_cpu += [0x1fe000, typed['registers'][15]] if case['sr'] & 0x2000 else [typed['registers'][15], 0x1ff000]
                if original[1] != compiled[1] or normalize(compiled[0], original[0], len(payload)) != original[0]:
                    save(out/'mismatch.json', dict(case=index, parameters=case, original_CPU=original[1], compiled_CPU=compiled[1],
                        RAM_differences=[dict(address=hex(a), original=x, compiled=y) for a,(x,y) in enumerate(zip(original[0],normalize(compiled[0],original[0],len(payload)))) if x != y][:32]))
                    raise AssertionError('compiled CPU/RAM mismatch')
                assert fact_cpu == original[1] and typed['RAM'] == original[0], ('facts CPU/RAM mismatch', index, fact_cpu, original[1])
                left = trace(image, case, len(payload), True)
                right = trace(candidate, case, len(payload), False)
                assert left[1] == right[1] == typed['events'], ('ordered events mismatch', index)
                assert normalize(right[0],left[0],len(payload)) == left[0] == typed['RAM']
                coverage.update(original[2])
                rows.append(dict(case=index, original_steps=original[3], compiled_steps=compiled[3], events=len(left[1])))
                if index % 128 == 0:
                    state['completed'] = len(rows); mark(); print('String', len(rows), '/', len(cases), flush=True)
            for case in [x for x in cases if x['left'] in [2,7] and x['string'] in ['one','seven','high_bytes']][:16]:
                queues = {(COUNT,2):[2,4,2,1], (SOURCE,1):[ord('Q'),255]}
                left = trace(image,case,len(payload),True,queues); right = trace(candidate,case,len(payload),False,queues)
                typed = facts.execute(packet,seed(image,case),case['incoming'],case['sr'],SP,queues)
                assert left[1] == right[1] == typed['events'], 'changing-read event mismatch'
                assert normalize(right[0],left[0],len(payload)) == left[0] == typed['RAM']
                changed += 1
        finally:
            engine.close()
        expected = {row['pc'] for row in packet['instructions']}
        if not args.limit: assert coverage == expected
        save(out/'results.json', rows)
        state.update(status='terminal_native_format_string_preflight_pass' if args.limit else 'terminal_native_format_string_facts_CPU_RAM_ordered_pass',
                     native_cases=len(rows), stable_ordered_cases=len(rows), changing_read_cases=changed,
                     original_instruction_coverage=[len(coverage),len(expected)], binary_bytes=len(payload),
                     compiled_binary=str(out/'candidate.bin'), compiled_binary_sha256=sha(out/'candidate.bin'),
                     source_accepted=not bool(args.limit),
                     artifacts_sha256={str(path):sha(path) for path in [source, Path(__file__), Path(facts.__file__), ROOT/'scripts/lower_m68k_facts_to_C_v2.py', NATIVE/'format-string-native.h',NATIVE/'format-string-shim.S',NATIVE/'m68k-fact-helpers-v2.h']},
                     scope='Entire36instruction/88byte routine. Full native D/A/PC/SR/USP/SSP and2MB RAM, public A2/D2 saves, stable native-width ordered accesses plus changing source/count read traces. User/supervisor and all32CCR patterns, signed count/width edges, null/empty/high-byte/long strings and bounded overlapping source/destination fixtures. Private8KB stack below public8bytes and candidate/entry code excluded. Host only dispatches retained CPU. Original dependencies: CPU/device backend. No IRQ/fault/cycle equivalence, arbitrary stack/code/counter alias, livegame/disc integration or physical-console proof. Deterministic tool C is not model-authored.')
        mark()
        if not args.limit: save(ROOT/'verification/native-format-string-current.json',state)
        print(state['status'],len(rows),changed,state['original_instruction_coverage'],flush=True)
    except BaseException as error:
        state.update(status='terminal_failed',error=repr(error));mark();raise


if __name__ == '__main__':
    main()
