"""Compare the complete readable coordinate-entry caller with original CPUs.

Global read/write order and logical calls are compared against Unicorn.
Selected cases also compare final external RAM with the pinned native core.
The eight helper bodies, CPU private stack/register outputs and real task
scheduling remain outside this semantic caller's contract.
"""
import argparse
import ctypes as c
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import re
import subprocess

from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *

import check_biwn_boundary_handlers as boundary
import check_biwn_media_setup_cpu as media

ROOT, SP, STOP = boundary.ROOT, boundary.SP, boundary.STOP
ENTRY, END = 0x18e92, 0x190b8
HELPERS = {0x12620: [2], 0xe4c0: [], 0x1b718: [4], 0x20e8c: [],
           0xdf60: [], 0xdf22: [], 0x20f78: [2], 0xdf3e: []}
W8 = c.CFUNCTYPE(c.c_int, c.c_void_p, c.c_uint32, c.c_uint8)


def save(p, v):
    p.write_text(json.dumps(v, indent=2) + '\n')


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class Script(boundary.Script):
    def __init__(self, snapshot, case, fail=None):
        super().__init__(snapshot, case)
        self.action = -1
        self.clock_index = 0
        self.fail = fail
        self.events = 0
        self.digit_function = None
        self.digit_coverage = set()

    def tick(self):
        if self.events == self.fail:
            raise RuntimeError('Injected callback failure')
        self.events += 1

    def read(self, a, w):
        self.tick()
        if (a, w) == (0x778cc, 4):
            values = self.case.get('clock', [1000, 1001, 1074, 1075])
            self.put(a, w, values[min(self.clock_index, len(values) - 1)])
            self.clock_index += 1
        return super().read(a, w)

    def write(self, a, w, v):
        self.tick()
        return super().write(a, w, v)

    def call(self, a, args):
        self.tick()
        assert a in HELPERS
        self.changed = []
        if a == 0x12620:
            assert args == [1]
            self.action += 1
            assert self.action < len(self.case['actions']), self.case
            self.clock_index = 0
            self.put(0x49ba4, 4, self.case['actions'][self.action].get('initial_held', 0))
        elif a == 0xe4c0:
            # A nonzero initial held word exercises the release loop; after
            # release, the next poll supplies this cycle's recorded input.
            phase = getattr(self, 'release_action', -1)
            if self.case['actions'][self.action].get('initial_held', 0) and phase != self.action:
                self.put(0x49ba4, 4, 0)
                self.release_action = self.action
            else:
                self.put(0x49ba4, 4, self.case['actions'][self.action]['held'])
        elif a == 0x1b718:
            assert args == [self.case['actions'][self.action]['held']]
        else:
            assert args == ([1] if a == 0x20f78 else [])
        for target, address, width, value in self.case.get('helper_effects', []):
            if target == a:
                self.put(address, width, value)
        self.trace.append(['call', a, args])
        if a == 0x1b718:
            if self.case.get('linked_digit'):
                return self.digit_function(args[0], getattr(self, 'incoming_call_d0', 0)) if self.digit_function else 0
            return self.case['actions'][self.action].get('digit', -1) & 0xffffffff
        return 0x12340000


def original(script, case, coverage):
    cpu = Uc(UC_ARCH_M68K, UC_MODE_BIG_ENDIAN)
    cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000)
    cpu.mem_map(0, 0x200000)
    cpu.mem_write(0, bytes(script.memory))
    cpu.mem_write(SP, STOP.to_bytes(4, 'big'))
    for reg, value in zip(boundary.REGS, case['incoming']):
        cpu.reg_write(reg, value)
    cpu.reg_write(UC_M68K_REG_SR, 0x2000)
    cpu.reg_write(UC_M68K_REG_A7, SP)
    for target in HELPERS:
        if target == 0x1b718 and case.get('linked_digit'):
            continue
        cpu.mem_write(target, b'\x4e\x75')

    def code(engine, a, width, _):
        if a in HELPERS:
            sp = engine.reg_read(UC_M68K_REG_A7)
            offset, args = 4, []
            for w in HELPERS[a]:
                args.append(int.from_bytes(engine.mem_read(sp + offset, w), 'big'))
                offset += w
            result = script.call(a, args)
            for address, w, value in script.changed:
                engine.mem_write(address, value.to_bytes(w, 'big'))
            if a != 0x1b718 or not case.get('linked_digit'):
                engine.reg_write(UC_M68K_REG_D0, result)
            return
        if case.get('linked_digit') and 0x1b718 <= a < 0x1b780:
            script.digit_coverage.add(a)
            return
        assert ENTRY <= a < END, hex(a)
        coverage.add(a)

    def read(engine, access, a, w, value, _):
        if SP - 0x1000 <= a < SP + 4:
            return
        engine.mem_write(a, script.read(a, w).to_bytes(w, 'big'))

    def write(engine, access, a, w, value, _):
        if SP - 0x1000 <= a < SP + 4:
            return
        script.write(a, w, value & ((1 << (w * 8)) - 1))

    cpu.hook_add(UC_HOOK_CODE, code)
    cpu.hook_add(UC_HOOK_MEM_READ, read)
    cpu.hook_add(UC_HOOK_MEM_WRITE, write)
    cpu.emu_start(ENTRY, STOP, count=100000, timeout=3000000)
    assert cpu.reg_read(UC_M68K_REG_PC) == STOP
    assert cpu.reg_read(UC_M68K_REG_A7) == SP + 4
    memory = bytearray(cpu.mem_read(0, 0x200000))
    for target in HELPERS:
        memory[target:target + 2] = script.memory[target:target + 2]
    assert memory[:SP - 0x1000] == script.memory[:SP - 0x1000]
    assert memory[SP + 4:] == script.memory[SP + 4:]
    return cpu.reg_read(UC_M68K_REG_D0)


def bind(source, out):
    restore = ROOT / 'projects/black-ice-white-noise/restoration'
    for directive in re.findall(r'(?m)^\s*#([^\n]+)', source.read_text()):
        # Expanded macro bodies are inspected in the compiler AST below.
        if re.match(r'\s*define\s+[A-Za-z_]\w*', directive):
            continue
        match = re.fullmatch(r'\s*include\s*[<"]([^>"\n]+)[>"]\s*', directive)
        assert match and match[1] in ['biwn_coordinate_entry.h', 'biwn_world_update.h', 'stdint.h'], directive
    command = ['clang', '-std=c99', '-I', str(source.parent), '-I', str(restore)]
    syntax = subprocess.run(command + ['-fsyntax-only', '-Xclang', '-ast-dump=json', str(source)], capture_output=True, text=True)
    (out / 'syntax.log').write_text(syntax.stderr)
    assert syntax.returncode == 0, syntax.stderr
    tree = json.loads(syntax.stdout)
    functions = [n for n in tree['inner'] if n['kind'] == 'FunctionDecl' and any(x['kind'] == 'CompoundStmt' for x in n.get('inner', []))]
    names = {n['name'] for n in functions}
    assert 'biwn_coordinate_entry' in names
    assert all(n['name'] in ['biwn_coordinate_entry', 'biwn_coordinate_entry_with_result'] or n.get('storageClass') == 'static' for n in functions)
    assert not any(n['kind'] in ['VarDecl', 'FileScopeAsmDecl'] for n in tree['inner'])

    def inspect(n):
        if not n:
            return
        assert n['kind'] not in ['GCCAsmStmt', 'MSAsmStmt']
        assert n.get('castKind') not in ['IntegralToPointer', 'PointerToIntegral', 'BitCast']
        if n['kind'] in ['BinaryOperator', 'CompoundAssignOperator'] and n.get('opcode') in ['>>', '>>=']:
            left = n['inner'][0]
            kind = left['type']
            unsigned = 'unsigned' in kind.get('desugaredQualType', kind['qualType'])
            if not unsigned and left.get('castKind') == 'IntegralCast':
                narrow = left['inner'][0]['type']
                unsigned = narrow.get('desugaredQualType', narrow['qualType']) in ['unsigned short', 'unsigned char']
            assert unsigned, 'Signed shift is outside the portable contract'
        if n['kind'] == 'CallExpr':
            target = n['inner'][0]
            while target['kind'] in ['ImplicitCastExpr', 'ParenExpr']:
                target = target['inner'][0]
            byte_callback = target.get('type', {}).get('qualType') == 'biwn_coordinate_write8'
            assert byte_callback or (target['kind'] == 'MemberExpr' and target['name'] in ['read8', 'read16', 'read32', 'write16', 'write32', 'call']) or (target['kind'] == 'DeclRefExpr' and target['referencedDecl']['name'] in names), target
        for child in n.get('inner', []):
            inspect(child)
    for n in functions:
        inspect(n)
    library = out / 'libcoordinate-entry.dylib'
    command += ['-dynamiclib', '-O2', '-Wall', '-Wextra', '-Werror', str(source), str(restore / 'biwn_inventory_select.c'), '-o', str(library)]
    result = subprocess.run(command, capture_output=True, text=True, env={**os.environ, 'DEVELOPER_DIR': '/Library/Developer/CommandLineTools'})
    (out / 'compiler.log').write_text(result.stdout + result.stderr)
    assert result.returncode == 0, result.stderr
    lib = c.CDLL(str(library))
    function = lib.biwn_coordinate_entry
    function.digit_function = lib.biwn_button_digit
    function.digit_function.argtypes = [c.c_uint32, c.c_uint32]
    function.digit_function.restype = c.c_uint32
    function.argtypes = [c.POINTER(boundary.world.Bus), W8, c.c_uint32]
    function.restype = c.c_int
    if hasattr(lib, 'biwn_coordinate_entry_with_result'):
        function.with_result = lib.biwn_coordinate_entry_with_result
        function.with_result.argtypes = [c.POINTER(boundary.world.Bus), W8, c.c_uint32, c.c_uint32, c.POINTER(c.c_uint32)]
        function.with_result.restype = c.c_int
    return function


def translated(fn, script, limit=10000, missing=None, null_bus=False, null_out=False):
    script.digit_function = fn.digit_function
    def reader(w):
        def cb(_, a, result):
            try:
                result[0] = script.read(a, w); return 0
            except Exception as error:
                script.errors.append(repr(error)); return 1
        return cb
    def writer(w):
        def cb(_, a, v):
            try:
                script.write(a, w, v); return 0
            except Exception as error:
                script.errors.append(repr(error)); return 1
        return cb
    def call(_, a, args, count, result):
        try:
            script.incoming_call_d0 = result[0]
            result[0] = script.call(a, list(args[:count])); return 0
        except Exception as error:
            script.errors.append(repr(error)); return 1
    w = boundary.world
    cb = [w.R8(reader(1)), w.R16(reader(2)), w.R32(reader(4)), w.W16(writer(2)), w.W32(writer(4)), w.CALL(call), W8(writer(1))]
    if missing is not None:
        cb[missing] = type(cb[missing])()
    bus = w.Bus(*cb[:6], None, 0)
    if script.case.get('with_result'):
        output = c.c_uint32(0xa55aa55a)
        status = fn.with_result(None if null_bus else c.byref(bus), cb[6], limit,
                                script.case['incoming'][0], None if null_out else c.byref(output))
        script.result_d0 = output.value
        return status
    return fn(None if null_bus else c.byref(bus), cb[6], limit)


def fixtures():
    rng = random.Random(ENTRY)
    cases = []
    cancel = dict(held=0x2000)
    def add(name, actions, **extra):
        cases.append(dict(name=name, actions=actions, initial=[[0x49c60, 2, extra.pop('mode', 1)], [0x40ffc, 4, 0x80000]], incoming=[rng.getrandbits(32) for _ in boundary.REGS], **extra))
    def digits(text):
        return [dict(held=1, digit=int(x)) for x in text]
    add('non_outdoor_zero', [], mode=0)
    add('non_outdoor_two', [], mode=2)
    add('cancel', [cancel])
    add('held_release', [dict(cancel, initial_held=0x10000000)])
    add('clock_wrap', [cancel], clock=[0xfffffffe])
    add('cursor_minimum_backspace', [dict(held=0x02000000), cancel])
    add('delete_first_coordinate', digits('123') + [dict(held=0x02000000)] + digits('4') + [cancel])
    add('delete_second_coordinate', digits('123456') + [dict(held=0x02000000)] + digits('7') + [cancel])
    add('extra_digits_ignored', digits('12345678') + [cancel])
    add('confirm_before_complete', digits('12') + [dict(held=0x20000000), cancel])
    for x, z in [(31, 32), (32, 31), (32, 32), (966, 719), (967, 719), (966, 720), (999, 999), (123, 456)]:
        add(f'confirm_{x}_{z}', digits(f'{x:03}{z:03}') + [dict(held=0x20000000), cancel])
    # Rereads of the same global pointer must remain separate bus events.
    add('initial_pointer_changes', [cancel], read_queues=[dict(address=0x40ffc, width=4, values=[0x80000 + 16 * i for i in range(7)])])
    for i in range(48):
        actions = []
        for j in range(rng.randrange(1, 16)):
            actions.append(dict(held=0x02000000) if rng.randrange(4) == 0 else dict(held=1, digit=rng.randrange(10)))
        add('mixed_digits_backspaces_' + str(i), actions + [cancel])
    for value in [0x7fff, 0x4000, 0x100, 0x8000]:
        add('external_decoder_word_' + hex(value),
            [dict(held=1, digit=value)] * 6 + [dict(held=0x02000000), cancel])
    add('nested_service_effects_retained', digits('123456') + [dict(held=0x20000000)],
        helper_effects=[[a, 0x90000 + i * 4, 4, 0x12345678 + i] for i, a in enumerate([0x20e8c, 0xdf60, 0xdf22, 0x20f78, 0xdf3e])])
    add('backspace_and_cancel_first', digits('123') + [dict(held=0x02002000)])
    add('backspace_and_cancel_second', digits('123456') + [dict(held=0x02002000)])
    for value in [0x7fff, 0x4000, 0x100]:
        add('external_decoder_backspace_cancel_' + hex(value), [dict(held=1, digit=value)] * 3 + [dict(held=0x02002000)])
    return cases


def native_cases(snapshot, cases, expected, expected_d0, out):
    core_path = Path(json.loads((ROOT / 'verification/DSP-music-context-experimental-candidate.json').read_text())['core_path'])
    oracle = media.scheduler.Native(diagnostic_core=core_path)
    runtime = media.Runtime.__new__(media.Runtime)
    runtime.oracle, runtime.device, runtime.core = oracle, oracle.device, oracle.lib
    writers = {}
    for width in [1, 2, 4]:
        fn = getattr(runtime.core, 'm68k_write_memory_' + str(width * 8))
        fn.argtypes, fn.restype = [c.c_uint32, c.c_uint32], None
        writers[width] = fn
    rows = []
    try:
        for index in list(range(18)) + list(range(len(cases) - 5, len(cases))):
            case = cases[index]
            script = Script(snapshot, case)
            memory = bytearray(script.memory)
            memory[SP:SP + 4] = STOP.to_bytes(4, 'big')
            for target in HELPERS:
                if target == 0x1b718 and case.get('linked_digit'):
                    continue
                memory[target:target + 2] = b'\x4e\x75'
            cpu = media.CPU()
            cpu.registers[:15] = case['incoming']
            cpu.registers[15], cpu.pc, cpu.sr, cpu.usp, cpu.ssp = SP, ENTRY, 0x2000, 0x180000, SP
            runtime.device.seed(bytes(memory), 0)
            runtime.seed_cpu(cpu)
            steps = 0
            while runtime.cpu().pc != STOP and steps < 100000:
                cpu = runtime.cpu()
                if cpu.pc in HELPERS:
                    ram = runtime.device.ram()
                    offset, args = 4, []
                    for width in HELPERS[cpu.pc]:
                        args.append(int.from_bytes(ram[cpu.registers[15] + offset:cpu.registers[15] + offset + width], 'big'))
                        offset += width
                    result = script.call(cpu.pc, args)
                    if cpu.pc != 0x1b718 or not case.get('linked_digit'):
                        cpu.registers[0] = result
                    for address, width, value in script.changed:
                        writers[width](address, value)
                    runtime.seed_cpu(cpu)
                if cpu.pc in [0x18f24, 0x18f2a]:
                    writers[4](0x778cc, script.read(0x778cc, 4))
                runtime.core.m68k_execute(1)
                steps += 1
            cpu = runtime.cpu()
            assert cpu.pc == STOP and cpu.registers[15] == SP + 4
            actual = bytearray(runtime.device.ram())
            wanted = expected[index]
            for target in HELPERS:
                actual[target:target + 2] = wanted[target:target + 2]
            assert actual[:SP - 0x1000] == wanted[:SP - 0x1000] and actual[SP + 4:] == wanted[SP + 4:], case['name']
            assert cpu.registers[0] == expected_d0[index], (case['name'], cpu.registers[0], expected_d0[index])
            rows.append(dict(name=case['name'], steps=steps, external_RAM_match=True, native_and_Unicorn_full_D0=cpu.registers[0]))
    finally:
        oracle.close()
    save(out / 'native-cases.json', rows)
    return rows, core_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', type=Path)
    ap.add_argument('--original-only', action='store_true')
    ap.add_argument('--linked-digit', action='store_true')
    ap.add_argument('--authorship', choices=['local-model', 'coordinator'], default='local-model')
    ap.add_argument('--with-result', action='store_true')
    args = ap.parse_args()
    out = ROOT / 'verification/local-coordinate-entry' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    print(out, flush=True)
    source = args.source
    if not args.original_only and source is None:
        source = Path(json.loads((ROOT / 'verification/local-coordinate-entry-author-current.json').read_text())['directory']) / 'biwn_coordinate_entry.c'
    fn = bind(source, out) if source else None
    if args.with_result and fn:
        assert hasattr(fn, 'with_result')
    snapshot_path = ROOT / 'verification/zero-warm-startup-instruction-atlas.bin'
    snapshot = snapshot_path.read_bytes()
    cases, coverage, rows, expected, expected_d0 = fixtures(), set(), [], [], []
    if args.linked_digit:
        # Derive digit button masks by executing the original helper. Do not
        # copy the C helper's lookup into its own comparison fixtures.
        digit_cpu = Uc(UC_ARCH_M68K, UC_MODE_BIG_ENDIAN)
        digit_cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000)
        digit_cpu.mem_map(0, 0x200000); digit_cpu.mem_write(0, snapshot)
        mapping = {}
        for bit in range(32):
            digit_cpu.reg_write(UC_M68K_REG_SR, 0x2000); digit_cpu.reg_write(UC_M68K_REG_A7, SP)
            digit_cpu.mem_write(SP, STOP.to_bytes(4, 'big') + (1 << bit).to_bytes(4, 'big'))
            digit_cpu.emu_start(0x1b718, STOP, count=128)
            digit = digit_cpu.reg_read(UC_M68K_REG_D0) & 65535
            if digit <= 9:
                assert digit not in mapping; mapping[digit] = 1 << bit
        assert set(mapping) == set(range(10))
        cases = [x for x in cases if not x['name'].startswith(('external_decoder_word_', 'external_decoder_backspace_cancel_'))]
        for case in cases:
            case['linked_digit'] = True
            for action in case['actions']:
                if action.get('digit', -1) >= 0:
                    action['held'] = mapping[action['digit']]
        save(out / 'original_digit_button_mapping.json', mapping)
    digit_coverage = set()
    for index, case in enumerate(cases):
        case['with_result'] = args.with_result
        original_script = Script(snapshot, case)
        d0 = original(original_script, case, coverage)
        expected_d0.append(d0)
        digit_coverage.update(original_script.digit_coverage)
        expected.append(original_script.memory)
        if fn:
            rebuilt = Script(snapshot, case)
            status = translated(fn, rebuilt)
            if status or rebuilt.errors or rebuilt.trace != original_script.trace or rebuilt.memory != original_script.memory or (args.with_result and rebuilt.result_d0 != d0):
                save(out / 'mismatch.json', dict(case=index, parameters=case, status=status, errors=rebuilt.errors, original_trace=original_script.trace, C_trace=rebuilt.trace))
                raise AssertionError(out / 'mismatch.json')
        rows.append(dict(name=case['name'], full_D0=d0, trace_events=len(original_script.trace), trace_sha256=hashlib.sha256(json.dumps(original_script.trace).encode()).hexdigest(), RAM_sha256=hashlib.sha256(original_script.memory).hexdigest()))
    import capstone
    decoder = capstone.Cs(capstone.CS_ARCH_M68K, capstone.CS_MODE_BIG_ENDIAN | capstone.CS_MODE_M68K_000)
    decoded = {x.address for x in decoder.disasm(snapshot[ENTRY:END], ENTRY)}
    save(out / 'coverage.json', dict(decoded=list(map(hex, sorted(decoded))), reached=list(map(hex, sorted(coverage))), unreached=list(map(hex, sorted(decoded - coverage)))))
    assert coverage == decoded, list(map(hex, sorted(decoded - coverage)))
    guards, native = [], []
    if fn:
        for missing in range(7):
            script = Script(snapshot, cases[2]); assert translated(fn, script, missing=missing) == 1 and not script.trace
            guards.append(dict(missing_callback=missing))
        for options in [dict(limit=0), dict(null_bus=True)]:
            script = Script(snapshot, cases[2]); assert translated(fn, script, **options) == 1 and not script.trace
            guards.append(options)
        if args.with_result:
            script = Script(snapshot, cases[2]); assert translated(fn, script, null_out=True) == 1 and not script.trace
            guards.append(dict(null_out=True))
        probe_case = cases[17]
        script = Script(snapshot, probe_case); original(script, probe_case, set())
        prefix = Script(snapshot, probe_case)
        for index, event in enumerate(script.trace):
            failed = Script(snapshot, probe_case, fail=index)
            status = translated(fn, failed)
            assert status == (3 if event[0] == 'call' else 2) and failed.trace == script.trace[:index], (index, event, status)
            assert failed.memory == prefix.memory, ('failure RAM effects', index)
            if args.with_result:
                assert failed.result_d0 == 0xa55aa55a
            if event[0] == 'r':
                assert prefix.read(event[1], event[2]) == event[3]
            elif event[0] == 'w':
                prefix.write(*event[1:])
            else:
                prefix.call(event[1], event[2])
            limited = Script(snapshot, probe_case)
            assert translated(fn, limited, limit=index + 1) == (4 if index + 1 < len(script.trace) else 0) and limited.trace == script.trace[:index + 1], (index, event)
            assert limited.memory == prefix.memory, ('budget RAM effects', index)
            if args.with_result and index + 1 < len(script.trace):
                assert limited.result_d0 == 0xa55aa55a
            guards.append(dict(callback_failure=index, prior_effects_retained=True, next_callback_budget_checked=True))
    native, core = native_cases(snapshot, cases, expected, expected_d0, out)
    report = dict(status='original_coordinate_entry_preflight_pass' if fn is None else 'local_coordinate_entry_original_CPU_match', recorded_at=datetime.now(timezone.utc).isoformat(), directory=str(out), source=str(source) if source else None, source_sha256=sha(source) if source else None, original_atlas=str(snapshot_path), original_atlas_sha256=sha(snapshot_path), cases=len(cases), instruction_coverage=[len(coverage), len(decoded)], native_cases=native, native_core=str(core) if core else None, native_core_sha256=sha(core) if core else None, guards=guards, helper_bodies_external=list(map(hex, HELPERS)), natural_gameplay_integration_verified=False, full_CPU_state_verified=False, new_training=False, native_Chat_verified=False, whole_game_complete=False, scope=__doc__)
    report.update(linked_readable_digit_helper=args.linked_digit, digit_source_locations_reached=list(map(hex, sorted(digit_coverage))))
    report['source_authorship'] = args.authorship if fn else 'original-CPU preflight only'
    report['full_D0_matches_original'] = args.with_result and fn is not None
    if args.linked_digit:
        report['helper_bodies_external'].remove('0x1b718')
        report['linked_digit_source_sha256'] = sha(ROOT / 'projects/black-ice-white-noise/restoration/biwn_inventory_select.c')
        report['scope'] += ' In this connected lane1B718 is original CPU on the oracle and the existing readable C decoder on the source side. Seven other helper bodies remain controlled fixtures; clock/poll/scheduling effects are supplied.'
    save(out / 'fixtures.json', cases); save(out / 'case-results.json', rows); save(out / 'report.json', report)
    pointer = ('coordinator-coordinate-entry-' if fn and args.authorship == 'coordinator' else 'local-coordinate-entry-') + ('linked-digit-' if args.linked_digit else '') + ('preflight-current.json' if fn is None else 'checks-current.json')
    save(ROOT / 'verification' / pointer, report)
    print(report['status'], len(cases), 'coverage', report['instruction_coverage'], 'native', len(native), 'guards', len(guards), flush=True)


if __name__ == '__main__':
    main()
