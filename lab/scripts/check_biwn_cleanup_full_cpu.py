"""Actual nested C cleanup/free functions versus native and Unicorn CPUs.

Independent Unicorn records declared mutable-read stimuli by instruction step;
the native core receives those same inputs before each corresponding read.
No helper scripts, scheduling or disc loading occurs in this proof.
"""
import ctypes as c
import hashlib
import os
import random
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import check_biwn_doorway_cpu as doorway
import check_biwn_transition_cleanup as legacy

queue = doorway.queue
ROOT, SP, STOP, CPU = queue.ROOT, queue.SP, queue.STOP, queue.CPU
queue.SCRIPTS = set()
queue.ENTRIES = {0x1545c, 0x1ae56, 0x20cc4, 0x20e40, 0x20e8c, 0x20f0c}
queue.RETURNS = set()


class Runtime(doorway.Runtime):
    def __init__(self, library, rows):
        super().__init__(library, rows)
        functions = {}
        for name in ['transition', 'resource']:
            for suffix in ['body', 'call']:
                fn = getattr(self.lib, 'biwn_' + name + '_cpu_' + suffix)
                fn.argtypes = self.fn.argtypes
                fn.restype = c.c_int
                functions[name, suffix] = fn

        def choose(suffix):
            def invoke(bus, state, *args):
                pc = c.cast(state, c.POINTER(CPU)).contents.pc if state else 0
                name = 'resource' if 0x1545c <= pc < 0x1557a else 'transition'
                return functions[name, suffix](bus, state, *args)
            return invoke

        self.fn, self.call = choose('body'), choose('call')

    def unicorn(self, ram, case, coverage):
        self.reset(ram, case, 0)
        engine = queue.Uc(queue.UC_ARCH_M68K, queue.UC_MODE_BIG_ENDIAN)
        engine.ctl_set_cpu_model(queue.UC_CPU_M68K_M68000)
        engine.mem_map(0, 0x200000)
        engine.mem_write(0, ram)
        engine.reg_write(queue.UC_M68K_REG_SR, case['SR'])
        for reg, value in zip(queue.cd.REGS, case['registers']):
            engine.reg_write(reg, value)
        steps, plan = [], []

        def code(cpu, pc, width, _):
            assert pc in self.rows, hex(pc)
            coverage.add(pc)
            steps.append(pc)

        def read(cpu, access, address, width, value, _):
            values = self.queues.get((address, width))
            if values:
                plan.append({'step': len(steps) - 1, 'PC': steps[-1],
                             'address': address, 'width': width, 'value': values[0]})
            cpu.mem_write(address, self.read(address, width).to_bytes(width, 'big'))

        def write(cpu, access, address, width, value, _):
            self.write(address, width, value & ((1 << (8 * width)) - 1))

        hook = engine.hook_add(queue.UC_HOOK_CODE, code)
        engine.hook_add(queue.UC_HOOK_MEM_READ, read)
        engine.hook_add(queue.UC_HOOK_MEM_WRITE, write)
        engine.emu_start(case['entry'], STOP, count=200000, timeout=30000000)
        state = queue.make_cpu(case)
        state.registers[:] = [engine.reg_read(reg) for reg in queue.cd.REGS]
        state.pc = engine.reg_read(queue.UC_M68K_REG_PC)
        assert state.pc == STOP
        if case['SR'] & 0x2000:
            state.ssp = state.registers[15]
        else:
            state.usp = state.registers[15]
        output, trace = self.device.ram(), list(self.trace)
        engine.hook_del(hook)
        engine.mem_write(STOP, b'\x40\xc7')
        engine.emu_start(STOP, STOP + 2, count=1)
        state.sr = engine.reg_read(queue.UC_M68K_REG_D7) & 65535
        return output, state, {'trace': trace, 'steps': steps, 'mutable_read_plan': plan}

    def native(self, ram, case, coverage, plan):
        self.reset(ram, case, 0)
        queue.lifecycle.seed_cpu(self, queue.make_cpu(case))
        steps, stack = [], []
        pending = None
        remaining = iter(plan)
        change = next(remaining, None)
        for _ in range(200000):
            pc = self.core.m68k_get_reg(None, 16)
            if pc == STOP:
                break
            assert pc in self.rows, hex(pc)
            while change is not None and change['step'] == len(steps):
                assert change['PC'] == pc
                self.device.direct(change['address'], change['width'], change['value'])
                change = next(remaining, None)
            if pending == pc:
                frame = {'target': pc, 'actual_body': True, 'incoming': queue.cd.scheduler.cpu_dict(self.cpu())}
                self.calls.append(frame)
                stack.append(frame)
                pending = None
            row = self.rows[pc]
            if row['assembly'] == 'rts' and stack:
                assert self.core.m68k_get_reg(None, 15) == stack[-1]['incoming']['registers'][15]
                stack.pop()['return'] = queue.cd.scheduler.cpu_dict(self.cpu())
            if row['assembly'].startswith('jsr '):
                pending = int(row['assembly'].split('$')[1].split('.')[0], 16)
                assert pending in queue.ENTRIES, hex(pending)
            steps.append(pc)
            coverage.add(pc)
            self.core.m68k_execute(1)
        else:
            raise AssertionError('Cleanup reference exceeded source work bound')
        assert not stack and change is None
        return self.device.ram(), self.cpu(), {'steps': steps, 'calls': self.calls}


def cases(snapshot):
    rng = random.Random(0x20e8c308)
    rows = legacy.cases(snapshot)
    for number, case in enumerate(rows):
        sup = number % 2
        case.update(id=number, registers=case['incoming'] + [SP],
                    SR=(0x2000 if sup else 0) | ((number % 8) << 8) | rng.randrange(32),
                    usp=0x170000 if sup else SP, ssp=SP if sup else 0x1d0000,
                    body=False, render=False, outer_RTS=0)
        case.setdefault('read_queues', [])
        case['initial'].append([SP, 4, STOP])
        cursor = SP + 4
        for value in case['params']:
            width = 2 if case['entry'] == 0x1ae56 else 4
            case['initial'].append([cursor, width, value])
            cursor += width
    return rows


def main():
    out = ROOT / 'verification/biwn-cleanup-fullCPU' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    source = ROOT / 'projects/black-ice-white-noise/restoration'
    library = out / 'libcleanup-fullCPU.dylib'
    names = ['biwn_transition_cpu.c', 'biwn_resource_cpu.c', 'biwn_doorway_cpu.c']
    command = ['clang', '-dynamiclib', '-std=c99', '-O2', '-Wall', '-Wextra', '-Werror'] + [str(source / name) for name in names] + ['-o', str(library)]
    build = subprocess.run(command, capture_output=True, text=True,
                           env={**os.environ, 'DEVELOPER_DIR': '/Library/Developer/CommandLineTools'})
    (out / 'compiler.txt').write_text(build.stdout + build.stderr)
    assert build.returncode == 0, build.stderr
    session = Path(queue.read(ROOT / 'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    mapping = queue.read(session / 'transition-fullCPU-generation.json')
    free_rows = [row for row in queue.read(session / 'resource-fullCPU-generation.json')['instructions_decoded']
                 if 0x1545c <= row['address'] < 0x1557a]
    all_rows = mapping['instructions_decoded'] + free_rows
    snapshot = (ROOT / 'render-assets/biwn-inventory-baseline.bin').read_bytes()
    vectors, results, coverage = cases(snapshot), [], set()
    runtime = Runtime(library, all_rows)
    try:
        for case in vectors:
            queue.save(out / 'status.json', {'status': 'running', 'case': case['id'], 'total': len(vectors)})
            ram = doorway.fixture(snapshot, case)
            seen, independent_cpu, independent = runtime.unicorn(ram, case, coverage)
            left, expected, native = runtime.native(ram, case, coverage, independent['mutable_read_plan'])
            right, actual, rebuilt = runtime.translated(ram, case, budget=200000)
            if (rebuilt['status'] or bytes(expected) != bytes(actual) or bytes(independent_cpu) != bytes(actual)
                    or left != right or seen != right or independent['trace'] != rebuilt['trace']
                    or native['calls'] != rebuilt['calls'] or native['steps'] != independent['steps']):
                queue.save(out / 'mismatch.json', {'case': case, 'native_CPU': queue.cd.scheduler.cpu_dict(expected),
                        'Unicorn_CPU': queue.cd.scheduler.cpu_dict(independent_cpu), 'C_CPU': queue.cd.scheduler.cpu_dict(actual),
                        'native': native, 'Unicorn': independent, 'C': rebuilt,
                        'RAM_diff': [hex(i) for i, (a, b) in enumerate(zip(left, right)) if a != b][:40]})
                raise AssertionError(str(out / 'mismatch.json'))
            assert not rebuilt['device']['original_GPUExec1_calls'] and not rebuilt['device']['game_frames_executed']
            results.append({'case': case, 'CPU': queue.cd.scheduler.cpu_dict(actual),
                            'native_steps': native['steps'], 'helper_calls': rebuilt['calls'],
                            'mutable_read_plan': independent['mutable_read_plan'], 'C_trace': rebuilt['trace'],
                            'RAM_sha256': hashlib.sha256(right).hexdigest()})
        decoded = [row for row in mapping['instructions_decoded'] if row['address'] < 0x19f2c or row['address'] >= 0x1a188]
        decoded += free_rows
        missing = [row for row in decoded if row['address'] not in coverage]
        queue.save(out / 'coverage.json', {'instructions': decoded, 'uncovered': missing})
        assert not missing, [hex(row['address']) for row in missing]
        guards = []
        probe = next(case for case in vectors if case['entry'] == 0x20e8c)
        ram = doorway.fixture(snapshot, probe)
        for options in [{'missing': i} for i in range(6)] + [{'null_bus': True}, {'null_cpu': True},
                        {'null_service': True}, {'budget': 0}, {'stop_flag': 2}, {'bad_pc': True}, {'budget': 1}]:
            _, _, result = runtime.translated(ram, probe, **options)
            expected = 7 if options.get('bad_pc') else 4 if options.get('budget') == 1 else 1
            assert result['status'] == expected and result['CPU_unchanged'], (options, result)
            guards.append(options)
        for target in [0x1545c, 0x1ae56, 0x20cc4, 0x20e40]:
            probe = next(row['case'] for row in results if any(frame['target'] == target for frame in row['helper_calls']))
            _, _, result = runtime.translated(doorway.fixture(snapshot, probe), probe, fail=('helper', target))
            assert result['status'] == 3 and result['CPU_unchanged'], (target, result)
            guards.append({'helper_failure': hex(target)})
        for fail in [('read', 2), ('read', 4), ('write', 2), ('write', 4)]:
            probe = next(row['case'] for row in results if any(trace[0] == ('r' if fail[0] == 'read' else 'w')
                         and trace[2] == fail[1] for trace in row['C_trace']))
            _, _, result = runtime.translated(doorway.fixture(snapshot, probe), probe, fail=fail)
            assert result['status'] in [2, 3] and result['CPU_unchanged'], (fail, result)
            guards.append({'bus_failure': fail})
        queue.save(out / 'fixtures.json', results)
        queue.save(out / 'guards.json', guards)
        report = {'recorded_at': datetime.now(timezone.utc).isoformat(),
                  'status': 'six_actual_cleanup_functions_native_Unicorn_C_fullCPU_RAM_bus_match',
                  'directory': str(out), 'CPU_cases': len(results), 'source_instruction_coverage': [len(decoded), len(decoded)],
                  'transition_group_cleanup_instruction_coverage': [139, 139],
                  'host_guards': len(guards), 'source_sha256': {name: hashlib.sha256((source / name).read_bytes()).hexdigest() for name in names},
                  'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'compiler': command,
                  'nested_helper_scripts': 0, 'original_CPU_or_GPU_execution_on_C_side': False,
                  'new_published_components': 0, 'source_boundary_loading_pipeline_verified': False,
                  'whole_game_complete': False,
                  'limits': ['Six actual functions: resource free1545C, release texture1AE56, release room20CC4, release region20E40,25-room reset20E8C and region reset20F0C. Complete CPU/SR/USP/SSP,2MBRAM/private frames,nestedhelper incoming/return states, native/Unicorn source PC sequence and ordered Unicorn/C data bus match.',
                             'Independent Unicorn records explicit queued fixture changes at architectural reads; native inputs receive them at those same instruction steps. These are declared mutations, not asynchronous hardware behavior.',
                             'Finite supplied tables/free lists. Cleanup marks actors dead but does not run those tasks or remove/reuse contexts. Boundary callers,disc loading,scheduler transitions remain separate.',
                             'Coordinator authored; upgrades already-selected logical functions, no new local-model instruction authorship/training.']}
        queue.save(out / 'report.json', report)
        queue.save(out / 'status.json', {'status': 'terminal_pass'})
        queue.save(ROOT / 'verification/biwn-cleanup-fullCPU-checks.json', report)
        print(__import__('json').dumps(report))
    except Exception as error:
        queue.save(out / 'status.json', {'status': 'terminal_failed', 'error': repr(error)})
        raise
    finally:
        runtime.close()


if __name__ == '__main__':
    main()
