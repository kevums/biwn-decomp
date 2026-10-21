"""Original DEB6/DF7A task unlink/free/TRAP2 versus explicit C continuations."""
import argparse
import ctypes as c
import hashlib
import json
import os
import random
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_biwn_scheduler as scheduler

ROOT = scheduler.ROOT
cleanup = scheduler.cleanup
CPU = scheduler.CPU
STOP = scheduler.STOP
RANGES = {0xdeb6: 0xdee2, 0xdf7a: 0xdf7c, 0xde1c: 0xde5c, 0xdf66: 0xdf6c}
save = scheduler.save

class Native(scheduler.Native):
    def original(self, script, case, coverage):
        self.device.seed(bytes(script.memory), 0)
        self.lib.m68k_pulse_reset()
        self.lib.m68k_set_irq(0)
        self.lib.m68k_set_reg(17, 0x2000)
        self.lib.m68k_set_reg(15, case['ssp'])
        self.lib.m68k_set_reg(17, 0)
        self.lib.m68k_set_reg(15, case['usp'])
        self.lib.m68k_set_reg(17, case['sr'])
        for i, value in enumerate(case['registers']):
            self.lib.m68k_set_reg(i, value)
        self.lib.m68k_set_reg(16, case['entry'])
        steps = []
        for _ in range(10000):
            pc = self.lib.m68k_get_reg(None, 16)
            if STOP <= pc < STOP + 0x20:
                break
            assert any(a <= pc < b for a, b in RANGES.items()), hex(pc)
            obj = self.lib.m68k_get_reg(None, 8)
            address = {0xdeb6: 0xc0920, 0xdebc: obj, 0xdec0: 0xc0924,
                       0xdece: obj + 4, 0xde1c: obj, 0xde20: obj + 26,
                       0xde26: obj + 34, 0xde2c: obj + 22, 0xde32: obj + 22,
                       0xde36: 0x778cc, 0xde4c: obj + 16, 0xde50: obj + 20,
                       0xde54: obj + 12}.get(pc)
            for q in case.get('read_queues', []):
                if q['address'] == address:
                    value = script.read(address, q['width'])
                    self.device.direct(address, q['width'], value)
            coverage.add(pc)
            steps.append(pc)
            self.lib.m68k_execute(1)
            if pc == 0xde5a and case['entry'] == 0xdeb6:
                break
        else:
            raise AssertionError('Removal did not reach selected continuation')
        cpu = CPU()
        cpu.registers[:] = [self.lib.m68k_get_reg(None, i) for i in range(16)]
        cpu.pc = self.lib.m68k_get_reg(None, 16)
        cpu.sr = self.lib.m68k_get_reg(None, 17)
        cpu.usp = self.prefix[16] if cpu.sr & 0x2000 else cpu.registers[15]
        cpu.ssp = cpu.registers[15] if cpu.sr & 0x2000 else self.prefix[17]
        return self.device.ram(), cpu, steps

def prefix_original(script, case):
    cpu = Uc(UC_ARCH_M68K, UC_MODE_BIG_ENDIAN)
    cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000)
    cpu.mem_map(0, 0x200000)
    cpu.mem_write(0, bytes(script.memory))
    for i, reg in enumerate(cleanup.REGS):
        cpu.reg_write(reg, case['registers'][i])
    cpu.reg_write(UC_M68K_REG_SR, case['sr'])
    cpu.reg_write(UC_M68K_REG_A7, case['registers'][15])
    cpu.reg_write(UC_M68K_REG_CR_USP, case['usp'])
    def read(engine, access, a, w, v, _):
        engine.mem_write(a, script.read(a, w).to_bytes(w, 'big'))
    def write(engine, access, a, w, v, _):
        script.write(a, w, v & ((1 << (w * 8)) - 1))
    cpu.hook_add(UC_HOOK_MEM_READ, read)
    cpu.hook_add(UC_HOOK_MEM_WRITE, write)
    cpu.emu_start(0xdeb6, 0xde5a, count=10000, timeout=500000)
    assert cpu.reg_read(UC_M68K_REG_PC) == 0xde5a
    assert bytes(cpu.mem_read(0, 0x200000)) == script.memory
    return cpu

def bind(lib):
    functions = {0xdeb6: lib.biwn_scheduler_remove_dispatch, 0xdf7a: lib.biwn_scheduler_remove}
    for fn in functions.values():
        fn.argtypes = [c.POINTER(cleanup.world.Bus), c.POINTER(CPU), c.c_uint32]
        fn.restype = c.c_int
    return functions

def cases():
    rng = random.Random(0xdeb6df7a)
    rows = []
    for variant in range(512):
        for entry in [0xdeb6, 0xdf7a]:
            count = 2 + (variant // 12) % 5
            contexts = [0x100000 + i * 0x1000 for i in range(count)]
            current_index = variant % count
            current = contexts[current_index]
            next_ctx = contexts[(current_index + 1) % count]
            usp = 0x180900
            ssp = 0x1dfffa if entry == 0xdeb6 else 0x1e0000
            sr = rng.randrange(0x800) & 0x71f
            if entry == 0xdeb6:
                sr |= 0x2000
            regs = [rng.getrandbits(32) for _ in range(16)]
            regs[15] = ssp if entry == 0xdeb6 else usp
            case = {'entry': entry, 'variant': variant, 'kind': 'removal_' + str(variant % 12),
                    'params': [], 'registers': regs, 'usp': usp, 'ssp': ssp, 'sr': sr,
                    'current': current, 'contexts': contexts,
                    'initial': [[0x88, 4, 0xdeb6], [0xc0920, 4, current],
                                [0xc0924, 4, 0 if variant % 2 else 0x120000], [0x778cc, 4, 10]],
                    'default_helper_return': 0}
            for i, ctx in enumerate(contexts):
                warm = variant % 3 != 0 and i != current_index
                target_sr = rng.randrange(0x800) & 0x71f
                if not warm and variant % 7 == 0:
                    target_sr |= 0x2000
                stack = 0x181000 + i * 0x1000
                pc = 0xdf66 if warm else STOP + i * 2
                case['initial'] += [[ctx, 4, contexts[(i + 1) % count]],
                                    [ctx + 4, 4, contexts[(i - 1) % count]], [ctx + 8, 4, 0x55550000 + i],
                                    [ctx + 12, 4, stack], [ctx + 16, 4, pc], [ctx + 20, 2, target_sr],
                                    [ctx + 22, 4, 0], [ctx + 26, 4, 0], [ctx + 30, 4, i], [ctx + 34, 4, 0]]
                for j in range(11):
                    case['initial'].append([stack + j * 4, 4, rng.getrandbits(32)])
                case['initial'].append([stack + 44, 4, STOP + i * 2])
            if entry == 0xdeb6:
                case['initial'] += [[ssp, 2, variant & 0x71f], [ssp + 2, 4, 0xdf7c]]
            else:
                case['initial'].append([usp, 4, 0xf57c])
            # A two-context ring must leave its sole survivor runnable. With
            # three or more, exercise skipping flags and clock/deadline rereads.
            mode = variant % 12
            if count > 2:
                if mode == 1:
                    case['initial'].append([next_ctx + 26, 4, 0xffffffff])
                elif mode == 2:
                    case['initial'].append([next_ctx + 34, 4, 1])
                elif mode == 3:
                    case['initial'].append([next_ctx + 22, 4, 10])
                elif mode == 4:
                    case['initial'].append([next_ctx + 22, 4, 11])
                elif mode == 5:
                    pair = [(0x80000000, 0x7fffffff), (0xffffffff, 0), (1, 0xffffffff)][(variant // 12) % 3]
                    case['initial'] += [[next_ctx + 22, 4, pair[0]], [0x778cc, 4, pair[1]]]
                elif mode == 6:
                    case['read_queues'] = [{'address': next_ctx + 22, 'width': 4, 'values': [1, 20]}]
                elif mode == 7:
                    for ctx in contexts:
                        if ctx not in [next_ctx, current]:
                            case['initial'].append([ctx + 26, 4, 1])
                    case['initial'].append([next_ctx + 22, 4, 10])
                    case['read_queues'] = [{'address': 0x778cc, 'width': 4, 'values': [9, 10]}]
                elif mode == 8:
                    # Surviving predecessor remains runnable after the scan wraps.
                    previous = contexts[(current_index - 1) % count]
                    for ctx in contexts:
                        if ctx not in [previous, current]:
                            case['initial'].append([ctx + 26, 4, 1])
            rows.append(case)
    return rows

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int)
    options = parser.parse_args()
    out = ROOT / 'verification/biwn-task-removal' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    source = ROOT / 'projects/black-ice-white-noise/restoration'
    snapshot = (ROOT / 'render-assets/biwn-inventory-baseline.bin').read_bytes()
    session = Path(json.loads((ROOT / 'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    image = (session / 'nextstage-68000-candidate.bin').read_bytes()
    for a, b in RANGES.items():
        assert snapshot[a:b] == image[a-0x4000:b-0x4000]
    library = out / 'libtask-removal.dylib'
    command = ['clang', '-dynamiclib', '-std=c99', '-O2', '-Wall', '-Wextra', '-Werror', str(source / 'biwn_scheduler.c'), '-o', str(library)]
    run = subprocess.run(command, capture_output=True, text=True, env={**os.environ, 'DEVELOPER_DIR': '/Library/Developer/CommandLineTools'})
    (out / 'compiler.txt').write_text(run.stdout + run.stderr)
    assert run.returncode == 0, run.stderr
    functions = bind(c.CDLL(str(library)))
    vectors = cases()[:options.limit or None]
    rows, coverage = [], set()
    native = Native()
    try:
        for i, case in enumerate(vectors):
            save(out / 'status.json', {'status': 'running', 'case': i})
            left = cleanup.Script(snapshot, case)
            right = cleanup.Script(snapshot, case)
            before = bytes(right.memory)
            ram, expected, steps = native.original(left, case, coverage)
            status, actual = scheduler.translated(functions, right, case)
            if status or scheduler.cpu_dict(actual) != scheduler.cpu_dict(expected) or ram != right.memory:
                save(out / 'mismatch.json', {'case': case, 'status': status, 'CPU_original': scheduler.cpu_dict(expected),
                     'CPU_C': scheduler.cpu_dict(actual), 'steps': [hex(a) for a in steps], 'C_trace': right.trace,
                     'RAM_differences': [[j, ram[j], right.memory[j]] for j in range(len(ram)) if ram[j] != right.memory[j]][:100]})
                raise AssertionError(str(out / 'mismatch.json'))
            ctx = case['current']
            assert ram[ctx+8:ctx+38] == before[ctx+8:ctx+38]
            assert int.from_bytes(ram[0xc0924:0xc0928], 'big') == ctx
            assert int.from_bytes(ram[0xc0920:0xc0924], 'big') != ctx
            if case['entry'] == 0xdeb6:
                prefix = cleanup.Script(snapshot, case)
                uc = prefix_original(prefix, case)
                sp = uc.reg_read(UC_M68K_REG_A7)
                assert right.trace[:-2] == prefix.trace
                assert right.trace[-2:] == [['r', sp, 2, int.from_bytes(prefix.memory[sp:sp+2], 'big')],
                                           ['r', sp+2, 4, int.from_bytes(prefix.memory[sp+2:sp+6], 'big')]]
                assert prefix.memory == right.memory
            rows.append({'case': i, 'parameters': case, 'original_steps': [hex(a) for a in steps],
                         'CPU_state': scheduler.cpu_dict(actual), 'trace': right.trace,
                         'selected_context': int.from_bytes(ram[0xc0920:0xc0924], 'big'),
                         'removed_context_state_not_saved': True, 'whole_RAM_full_CPU_match': True,
                         'Unicorn_pre_RTE_bus_match': case['entry'] == 0xdeb6})
    except Exception as error:
        save(out / 'status.json', {'status': 'terminal_failed', 'error': repr(error)})
        raise
    finally:
        native.close()
    save(out / 'fixtures.json', rows)
    if options.limit:
        save(out / 'status.json', {'status': 'terminal_preflight', 'cases': len(rows)})
        print(json.dumps({'directory': str(out), 'cases': len(rows)}))
        return
    guards = []
    for entry in functions:
        case = next(x for x in vectors if x['entry'] == entry)
        for missing in range(4):
            script = cleanup.Script(snapshot, case)
            status, cpu = scheduler.translated(functions, script, case, missing=missing)
            assert status == 1 and bytes(cpu) == bytes(scheduler.make_cpu(case)) and not script.trace
            guards.append({'entry': hex(entry), 'missing_callback': missing})
        for kind in ['null_cpu', 'zero_limit', 'wrong_mode', 'wrong_PC']:
            wrong = dict(case)
            if kind == 'wrong_mode':
                wrong['sr'] ^= 0x2000
            if kind == 'wrong_PC':
                wrong['entry'] = entry + 2
                script = cleanup.Script(snapshot, wrong)
                status, cpu = scheduler.translated({entry+2: functions[entry]}, script, wrong)
                assert status == 1 and bytes(cpu) == bytes(scheduler.make_cpu(wrong)) and not script.trace
                guards.append({'entry': hex(entry), 'wrong_PC': True})
                continue
            script = cleanup.Script(snapshot, wrong)
            status, cpu = scheduler.translated(functions, script, wrong, null_cpu=kind == 'null_cpu', limit=0 if kind == 'zero_limit' else 64)
            assert status == 1 and bytes(cpu) == bytes(scheduler.make_cpu(wrong)) and not script.trace
            guards.append({'entry': hex(entry), 'argument': kind})
        for kind, address in [('fail_read', 0xc0920), ('fail_write', case['current'])]:
            script = cleanup.Script(snapshot, case)
            setattr(script, kind, (address, 4))
            status, cpu = scheduler.translated(functions, script, case)
            assert status == 3 and bytes(cpu) == bytes(scheduler.make_cpu(case))
            guards.append({'entry': hex(entry), 'callback_failure': kind, 'partial_trace': script.trace})
        wrong = dict(case)
        wrong['initial'] = list(case['initial']) + [[ctx + 26, 4, 1] for ctx in case['contexts']]
        script = cleanup.Script(snapshot, wrong)
        status, cpu = scheduler.translated(functions, script, wrong, limit=3)
        assert status == 2 and bytes(cpu) == bytes(scheduler.make_cpu(wrong))
        guards.append({'entry': hex(entry), 'scan_limit': 3, 'partial_trace': script.trace})
    case = next(x for x in vectors if x['entry'] == 0xdf7a)
    wrong = dict(case)
    wrong['initial'] = case['initial'] + [[0x88, 4, 0]]
    script = cleanup.Script(snapshot, wrong)
    status, cpu = scheduler.translated(functions, script, wrong)
    assert status == 4 and bytes(cpu) == bytes(scheduler.make_cpu(wrong))
    guards.append({'bad_vector': True, 'partial_trace': script.trace})
    save(out / 'guards.json', guards)
    decoded = []
    for a, b in RANGES.items():
        part, _ = cleanup.world.select.binary_tools.m68k_instructions(image[a-0x4000:b-0x4000], a)
        decoded += part
    missing = [x for x in decoded if x['address'] not in coverage]
    save(out / 'decode.json', {'instructions': decoded, 'uncovered': missing})
    assert not missing
    report = {'recorded_at': datetime.now(timezone.utc).isoformat(), 'status': 'original_TRAP2_removal_and_handler_match_C',
              'directory': str(out), 'native_CPU_cases': len(rows), 'handler_cases': 512, 'TRAP2_cases': 512,
              'Unicorn_pre_RTE_bus_cases': 512, 'CPU_instruction_coverage': [len(decoded), len(decoded)],
              'new_removal_entry_instructions': 10, 'new_removal_entry_bytes': 46,
              'shared_scheduler_and_yield_tail_reused': True, 'host_guards': len(guards),
              'task_context_range': [2, 6], 'removed_contexts_not_resumed': True, 'removed_state_not_saved': True,
              'original_TRAP2_RTE_executed': True, 'helper_stubs': 0,
              'source_sha256': {n: hashlib.sha256((source / n).read_bytes()).hexdigest() for n in ['biwn_scheduler.c', 'biwn_scheduler.h']},
              'matched': ['Complete2MBRAM, all16registers, PC, SR, USP/SSP and private exception/saved-yield frames match original native CPU.',
                          'Handler ordered bus widths/values/accesses also match original Unicorn up to RTE; final frame reads agree with native fullstate.',
                          'Free-list insertion, doubly-linked-ring unlink, blocked/suspended/deadline skips, unsigned high-bit deadlines, controlled clock rereads, fresh/saved-yield continuations and supervisor returns.'],
              'limits': ['Bounded synthetic2..6context layouts and SRbits0x271f, no external interrupts/tracing/timing/code-stack aliases. No full game/hardware proof.',
                         'Requires a remaining runnable context. Host scan/vector/bus/argument failures leave CPU unchanged and retain prior RAM effects; not original exceptions.',
                         'Actor integration and context reuse are separate proofs. No original GPU/gameframes run on C side.'],
              'core_sha256': cleanup.world.select.binary_tools.sha(ROOT / 'tools/blitter-runtime/virtualjaguar_libretro.dylib'), 'compiler': command}
    save(out / 'report.json', report)
    save(out / 'status.json', {'status': 'terminal_pass', 'cases': len(rows)})
    save(ROOT / 'verification/biwn-task-removal-checks.json', report)
    print(json.dumps(report))

if __name__ == '__main__':
    main()
