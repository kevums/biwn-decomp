"""Full boundary CPU/private frames versus native and Unicorn; scripted helpers.

Explicitly a caller ABI proof, not a connected cleanup/loading transition.
"""
import ctypes as c
import hashlib
import json
import os
import random
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import check_biwn_doorway_cpu as doorway
import check_biwn_boundary_handlers as legacy

queue = doorway.queue
ROOT, SP, STOP = queue.ROOT, queue.SP, queue.STOP
queue.SCRIPTS = set(legacy.HELPERS)
queue.ENTRIES = set()
queue.RETURNS = set()


class Runtime(doorway.Runtime):
    def __init__(self, library, rows):
        # The shared leaf runtime binds doorway symbols; this library includes
        # that unchanged implementation solely for initialization, then selects
        # the transition symbols below. No doorway source executes in this test.
        super().__init__(library, rows)
        self.fn = self.lib.biwn_transition_cpu_body
        self.call = self.lib.biwn_transition_cpu_call
        for fn in [self.fn, self.call]:
            fn.argtypes = [c.POINTER(queue.world.Bus), c.POINTER(queue.CPU), queue.cd.dispatch.W8,
                           queue.cd.world_cpu.SERVICE, c.c_void_p, c.c_uint32, c.c_int]
            fn.restype = c.c_int
        # The native core exposes no data-read hook here. Inject declared
        # mutable fixture values immediately before the two explicit rereads.
        # This changes only reference inputs; C executes through its bus.
        native_execute = self.core.m68k_execute

        def execute(count):
            pc = self.core.m68k_get_reg(None, 16)
            if pc in [0x1a05a, 0x1a06c]:
                self.inject(self.core.m68k_get_reg(None, 9) + 0x16, 2)
            elif pc in [0x1a088, 0x1a0d6]:
                self.inject(self.core.m68k_get_reg(None, 8) + 4, 2)
            return native_execute(count)

        self.core.m68k_execute = execute

    def scripted(self, state, target):
        frame = {'target': target, 'actual_body': False, 'incoming': queue.cd.scheduler.cpu_dict(state)}
        state.registers[0] = self.case.get('helper_returns', {}).get(str(target), self.case['default_helper_return']) & 0xffffffff
        seed = (target + self.case['id'] * 1234567) & 0xffffffff
        for reg in [1, 8, 9]:
            state.registers[reg] = (seed * (reg + 1) + 0xaabbccdd) & 0xffffffff
        state.sr = (state.sr & 0xffe0) | (seed & 31)
        for helper, address, width, value in self.case.get('helper_effects', []):
            if helper == target:
                self.device.direct(address, width, value)
        frame['return'] = queue.cd.scheduler.cpu_dict(state)
        self.calls.append(frame)


def cases(snapshot):
    rows = legacy.make_cases(snapshot)
    rng = random.Random(0x1a0f8)
    for mode in [0, 1, 2, 0xffff]:
        for room in [0, 1, 0x7fff, 0x8000, 0xffff]:
            for buttons in [0, 0x10, 0x20, 0x30]:
                for flags in [0, 0x40, 0x4000, 0x8000, 0x8040, 0xc000]:
                    rows.append({'entry': 0x1a0f8, 'params': [], 'kind': 'interior_level_buttons',
                         'incoming': [rng.getrandbits(32) for _ in range(15)], 'default_helper_return': rng.getrandbits(32),
                         'initial': [[0x49c60, 2, mode], [0x49c78, 4, 0x81000], [0x81000, 2, room],
                                     [0x49ba5, 1, buttons], [0x49c18, 4, 0x82000], [0x8200c, 2, flags],
                                     [0x49c62, 2, rng.choice([0, 0x7fff, 0x8000, 0xffff])],
                                     [0x49c64, 2, rng.choice([0, 0x7fff, 0x8000, 0xffff])]]})
    for number, case in enumerate(rows):
        sup = number % 2
        case.update(id=number, registers=case['incoming'] + [SP],
                    SR=(0x2000 if sup else 0) | ((number % 8) << 8) | rng.randrange(32),
                    usp=0x170000 if sup else SP, ssp=SP if sup else 0x1d0000,
                    body=False, render=False, outer_RTS=0)
        case.setdefault('read_queues', [])
        initial = [[SP, 4, STOP]]
        cursor = SP + 4
        for index, value in enumerate(case['params']):
            width = 4 if case['entry'] == 0x19fda and index == 0 else 2
            initial.append([cursor, width, value])
            cursor += width
        case['initial'] += initial
    return rows


def main():
    out = ROOT / 'verification/biwn-boundary-fullCPU' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    source = ROOT / 'projects/black-ice-white-noise/restoration'
    library = out / 'libboundary-fullCPU.dylib'
    command = ['clang', '-dynamiclib', '-std=c99', '-O2', '-Wall', '-Wextra', '-Werror',
               str(source / 'biwn_transition_cpu.c'), str(source / 'biwn_doorway_cpu.c'), '-o', str(library)]
    build = subprocess.run(command, capture_output=True, text=True,
                           env={**os.environ, 'DEVELOPER_DIR': '/Library/Developer/CommandLineTools'})
    (out / 'compiler.txt').write_text(build.stdout + build.stderr)
    assert build.returncode == 0, build.stderr
    session = Path(queue.read(ROOT / 'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    mapping = queue.read(session / 'transition-fullCPU-generation.json')
    snapshot = (ROOT / 'render-assets/biwn-inventory-baseline.bin').read_bytes()
    vectors = cases(snapshot)
    runtime = Runtime(library, mapping['instructions_decoded'])
    results, coverage = [], set()
    try:
        for case in vectors:
            queue.save(out / 'status.json', {'status': 'running', 'case': case['id'], 'total': len(vectors)})
            ram = doorway.fixture(snapshot, case)
            left, native_cpu, native = runtime.native(ram, case, coverage)
            seen, unicorn_cpu, independent = runtime.unicorn(ram, case, coverage)
            right, actual, rebuilt = runtime.translated(ram, case)
            if (rebuilt['status'] or bytes(native_cpu) != bytes(actual) or bytes(unicorn_cpu) != bytes(actual)
                    or left != right or seen != right or independent['trace'] != rebuilt['trace']
                    or native['calls'] != rebuilt['calls']):
                queue.save(out / 'mismatch.json', {'case': case, 'native_CPU': queue.cd.scheduler.cpu_dict(native_cpu),
                     'Unicorn_CPU': queue.cd.scheduler.cpu_dict(unicorn_cpu), 'C_CPU': queue.cd.scheduler.cpu_dict(actual),
                     'native': native, 'Unicorn': independent, 'C': rebuilt,
                     'RAM_diff': [hex(i) for i, (a, b) in enumerate(zip(left, right)) if a != b][:40]})
                raise AssertionError(str(out / 'mismatch.json'))
            assert not rebuilt['device']['original_GPUExec1_calls'] and not rebuilt['device']['game_frames_executed']
            results.append({'case': case, 'CPU': queue.cd.scheduler.cpu_dict(actual),
                            'native_steps': native['steps'], 'helper_calls': rebuilt['calls'],
                            'C_trace': rebuilt['trace'], 'RAM_sha256': hashlib.sha256(right).hexdigest()})
        decoded = [row for row in mapping['instructions_decoded'] if 0x19f2c <= row['address'] < 0x1a188]
        missing = [row for row in decoded if row['address'] not in coverage]
        queue.save(out / 'coverage.json', {'instructions': mapping['instructions_decoded'],
                                         'boundary_uncovered': missing,
                                         'cleanup_verified_by_this_test': False})
        assert not missing, [hex(row['address']) for row in missing]
        guards = []
        probe = vectors[0]
        ram = doorway.fixture(snapshot, probe)
        for options in [{'missing': i} for i in range(6)] + [{'null_bus': True}, {'null_cpu': True},
                      {'null_service': True}, {'budget': 0}, {'stop_flag': 2}, {'bad_pc': True}, {'budget': 1}]:
            _, _, result = runtime.translated(ram, probe, **options)
            expected = 7 if options.get('bad_pc') else 4 if options.get('budget') == 1 else 1
            assert result['status'] == expected and result['CPU_unchanged'], (options, result)
            guards.append(options)
        for target in legacy.HELPERS:
            case = next(row['case'] for row in results if any(frame['target'] == target for frame in row['helper_calls']))
            _, _, result = runtime.translated(doorway.fixture(snapshot, case), case, fail=('helper', target))
            assert result['status'] == 3 and result['CPU_unchanged'], (target, result)
            guards.append({'helper_failure': hex(target)})
        for fail in [('read', 1), ('read', 2), ('read', 4), ('write', 2), ('write', 4)]:
            case = next((row['case'] for row in results if any(trace[0] == ('r' if fail[0] == 'read' else 'w')
                         and trace[2] == fail[1] for trace in row['C_trace'])), None)
            if case is None:
                continue
            _, _, result = runtime.translated(doorway.fixture(snapshot, case), case, fail=fail)
            assert result['status'] == 2 and result['CPU_unchanged'], (fail, result)
            guards.append({'bus_failure': fail})
        # Stop at the real DF60 call with all caller arguments/private frames,
        # without pretending that the scheduler or loader has executed.
        case = next(row['case'] for row in results if any(frame['target'] == 0xdf60 for frame in row['helper_calls']))
        ram = doorway.fixture(snapshot, case)
        yield_case = {**case, 'render': True}
        left, expected, native = runtime.native(ram, yield_case, set())
        right, actual, rebuilt = runtime.translated(ram, yield_case)
        assert rebuilt['status'] == 6 and bytes(expected) == bytes(actual) and left == right
        guards.append({'actual_DF60_boundary_fullCPU_privateframes_preserved': True})
        queue.save(out / 'fixtures.json', results)
        queue.save(out / 'guards.json', guards)
        report = {'recorded_at': datetime.now(timezone.utc).isoformat(),
                  'status': 'three_boundary_callers_native_Unicorn_C_fullCPU_RAM_bus_match', 'directory': str(out),
                  'CPU_cases': len(results), 'source_instruction_coverage': [len(decoded), len(decoded)],
                  'generated_group_instructions': mapping['instructions'], 'cleanup_fullCPU_verified': False,
                  'host_guards': len(guards), 'source_sha256': mapping['source_sha256'],
                  'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'compiler': command,
                  'new_published_components': 0, 'source_boundary_loading_pipeline_verified': False,
                  'whole_game_complete': False,
                  'limits': ['19F2C,19FDA,1A0F8 complete caller CPU/private frames, full 2 MB RAM, nested scripted helper incoming/return states and ordered Unicorn/C data bus. Both stack banks and one DF60 stop checkpoint match.',
                             'Geometry/cleanup/DF60/texture/scene helpers are declared return/mutation/register/CCR scripts, not actual functions or scheduler execution in this test.',
                             'Cleanup source blocks in this generated group remain unverified here. Connected actual doorway transition, actor removal/reuse and scheduled loading remain required.',
                             'Coordinator authored fixed blocks; no new local-model instruction acceptance or training.']}
        queue.save(out / 'report.json', report)
        queue.save(out / 'status.json', {'status': 'terminal_pass'})
        queue.save(ROOT / 'verification/biwn-boundary-fullCPU-checks.json', report)
        print(json.dumps(report))
    except Exception as error:
        queue.save(out / 'status.json', {'status': 'terminal_failed', 'error': repr(error)})
        raise
    finally:
        runtime.close()


if __name__ == '__main__':
    main()
