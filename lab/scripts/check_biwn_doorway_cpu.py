"""Native M68000/Unicorn/fixed C entrance check, actual CD gates plus edges.

Relocated records and controlled object coordinates are declared fixtures.
No loading, cleanup, scheduler or natural route reachability is implied.
"""
import ctypes as c
import hashlib
import json
import os
import random
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import check_biwn_render_queue_cpu as queue
import generate_biwn_doorway_cpu as generator

ROOT = queue.ROOT
CPU = queue.CPU
SP, STOP = queue.SP, queue.STOP
queue.ENTRIES = set()
queue.RETURNS = set()
queue.SCRIPTS = set()


class Runtime(queue.Runtime):
    def __init__(self, library, rows):
        self.native_oracle = queue.cd.scheduler.Native()
        self.device = self.native_oracle.device
        self.core = self.native_oracle.lib
        self.prefix = self.native_oracle.prefix
        self.lib = c.CDLL(str(library))
        self.rows = {row['address']: row for row in rows}
        self.fn = self.lib.biwn_doorway_cpu_body
        self.call = self.lib.biwn_doorway_cpu_call
        for fn in [self.fn, self.call]:
            fn.argtypes = [c.POINTER(queue.world.Bus), c.POINTER(CPU), queue.cd.dispatch.W8,
                           queue.cd.world_cpu.SERVICE, c.c_void_p, c.c_uint32, c.c_int]
            fn.restype = c.c_int


def cases(inventory):
    rng = random.Random(0x10430291)
    rows = []
    obj, tile, table = 0x80000, 0x82000, 0x100000

    def add(record, direction, match, provenance=None, index=0, count=None, tile_index=0):
        sup = len(rows) % 2
        registers = [rng.getrandbits(32) for _ in range(15)] + [SP]
        initial = [[SP, 4, STOP], [SP + 4, 4, obj], [SP + 8, 2, index],
                   [SP + 10, 2, direction], [obj + 0x40, 2, tile_index],
                   [0x49bb4 + (tile_index if tile_index < 32768 else tile_index - 65536) * 4, 4, tile],
                   [tile + 2, 2, index + 1 if count is None else count], [tile + 12, 4, table]]
        for offset in range(0, 0x5a, 2):
            if offset != 0x40:
                initial.append([obj + offset, 2, rng.randrange(65536)])
        signed_index = index if index < 32768 else index - 65536
        record_address = table + signed_index * 28
        for offset, value in enumerate(record):
            initial.append([record_address + offset, 1, value])
        if direction < 4:
            key = record[[11, 13, 15, 17][direction]]
            nibble = key if match else (key + 1) & 15
            # The source uses a signed difference, ASR.W 6 and AND.W 15.
            left, right = [(6, 0x4e), (0x4a, 6), (0x52, 12), (12, 0x56)][direction]
            initial += [[obj + left, 2, nibble * 64], [obj + right, 2, 0]]
        else:
            key = rng.randrange(16)
            registers[1] = (registers[1] & 0xffff0000) | (key << 6)
            registers[3] = (registers[3] & 0xffff0000) | (key if match else (key + 1) & 15)
        rows.append({'id': len(rows), 'entry': 0x10430, 'outer_RTS': 0x1051e,
                     'body': len(rows) % 3 == 1, 'render': False, 'registers': registers,
                     'SR': (0x2000 if sup else 0) | ((len(rows) % 8) << 8) | rng.randrange(32),
                     'usp': 0x170000 if sup else SP, 'ssp': SP if sup else 0x1d0000,
                     'read_queues': [], 'initial': initial, 'source_gate': provenance,
                     'direction': direction, 'position_match_requested': match,
                     'index': index, 'count': index + 1 if count is None else count})

    for gate in inventory['directionally_enabled_gates']:
        record = bytes.fromhex(gate['record_hex'])
        for direction in gate['directions']:
            for match in [True, False]:
                add(record, direction, match, gate, index=gate['cell'][2])
    disabled = [gate for gate in inventory['gates']
                if all(bytes.fromhex(gate['record_hex'])[offset] >= 16 for offset in [11, 13, 15, 17])]
    for gate in disabled[:64]:
        for direction in range(4):
            add(bytes.fromhex(gate['record_hex']), direction, True, gate)
    for i in range(192):
        record = bytearray(rng.getrandbits(8) for _ in range(28))
        for offset in [11, 13, 15, 17]:
            record[offset] = rng.choice([0, 1, 15, 16, 127, 128, 255])
        record[26:28] = (0xffff if i % 7 == 0 else rng.randrange(65535)).to_bytes(2, 'big')
        direction = [0, 1, 2, 3, 4, 0xffff][i % 6]
        index = [0, 1, 2, 0xffff, 0xfffe, 0x7fff, 0x8000][i % 7]
        count = [0, 1, 2, 3, 0x7fff, 0x8000, 0xffff][i // 7 % 7]
        add(record, direction, i % 3 == 0, index=index, count=count,
            tile_index=[0, 1, 0xffff, 0x7fff, 0x8000][i % 5])
    return rows


def fixture(snapshot, case):
    ram = bytearray(snapshot)
    for address, width, value in case['initial']:
        assert 0 <= address <= len(ram) - width
        ram[address:address + width] = (value & ((1 << (width * 8)) - 1)).to_bytes(width, 'big')
    return bytes(ram)


def main():
    out = ROOT / 'verification/biwn-doorway-cpu' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    session = Path(queue.read(ROOT / 'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    mapping = queue.read(session / 'doorway-fullCPU-generation.json')
    source = ROOT / 'projects/black-ice-white-noise/restoration'
    library = out / 'libdoorway-cpu.dylib'
    command = ['clang', '-dynamiclib', '-std=c99', '-O2', '-Wall', '-Wextra', '-Werror',
               str(source / 'biwn_doorway_cpu.c'), '-o', str(library)]
    build = subprocess.run(command, capture_output=True, text=True,
                           env={**os.environ, 'DEVELOPER_DIR': '/Library/Developer/CommandLineTools'})
    (out / 'compiler.txt').write_text(build.stdout + build.stderr)
    assert build.returncode == 0, build.stderr
    inventory = queue.read(ROOT / 'verification/biwn-disc-gate-target-inventory.json')
    snapshot = (ROOT / 'render-assets/biwn-inventory-baseline.bin').read_bytes()
    vectors = cases(inventory)
    runtime = Runtime(library, mapping['instructions_decoded'])
    coverage, results = set(), []
    try:
        for case in vectors:
            queue.save(out / 'status.json', {'status': 'running', 'case': case['id'], 'total': len(vectors)})
            ram = fixture(snapshot, case)
            left, native_cpu, native = runtime.native(ram, case, coverage)
            observed, unicorn_cpu, independent = runtime.unicorn(ram, case, coverage)
            right, actual, rebuilt = runtime.translated(ram, case)
            if (rebuilt['status'] or bytes(native_cpu) != bytes(actual) or bytes(unicorn_cpu) != bytes(actual)
                    or left != right or observed != right or independent['trace'] != rebuilt['trace']):
                queue.save(out / 'mismatch.json', {'case': case, 'native_CPU': queue.cd.scheduler.cpu_dict(native_cpu),
                    'Unicorn_CPU': queue.cd.scheduler.cpu_dict(unicorn_cpu), 'C_CPU': queue.cd.scheduler.cpu_dict(actual),
                    'native': native, 'Unicorn': independent, 'C': rebuilt,
                    'RAM_diff': [hex(i) for i, (a, b) in enumerate(zip(left, right)) if a != b][:40]})
                raise AssertionError(str(out / 'mismatch.json'))
            assert not rebuilt['device']['original_GPUExec1_calls'] and not rebuilt['device']['game_frames_executed']
            results.append({'case': case, 'CPU': queue.cd.scheduler.cpu_dict(actual),
                            'native_steps': native['steps'], 'C_trace': rebuilt['trace'],
                            'RAM_sha256': hashlib.sha256(right).hexdigest(), 'three_way_fullCPU_RAM_bus_match': True})
        missing = [row for row in mapping['instructions_decoded'] if row['address'] not in coverage]
        queue.save(out / 'coverage.json', {'instructions': mapping['instructions_decoded'], 'uncovered': missing})
        assert not missing, [hex(row['address']) for row in missing]
        guards = []
        probe = vectors[0]
        ram = fixture(snapshot, probe)
        for options in [{'missing': i} for i in range(6)] + [{'null_bus': True}, {'null_cpu': True},
                    {'null_service': True}, {'budget': 0}, {'stop_flag': 2}, {'bad_pc': True}, {'budget': 1}]:
            _, _, rebuilt = runtime.translated(ram, probe, **options)
            expected = 7 if options.get('bad_pc') else 4 if options.get('budget') == 1 else 1
            assert rebuilt['status'] == expected and rebuilt['CPU_unchanged'], (options, rebuilt)
            guards.append(options)
        for fail in [('read', 1), ('read', 2), ('read', 4), ('write', 2), ('write', 4)]:
            _, _, rebuilt = runtime.translated(ram, probe, fail=fail)
            assert rebuilt['status'] == 2 and rebuilt['CPU_unchanged'], (fail, rebuilt)
            guards.append({'bus_failure': fail})
        queue.save(out / 'fixtures.json', results)
        queue.save(out / 'guards.json', guards)
        report = {'recorded_at': datetime.now(timezone.utc).isoformat(), 'status': 'native_Unicorn_C_doorway_fullCPU_RAM_bus_match',
                  'directory': str(out), 'CPU_cases': len(results), 'source_instruction_coverage': [75, 75],
                  'actual_gate_records': len(inventory['directionally_enabled_gates']), 'host_guards': len(guards),
                  'source_sha256': mapping['source_sha256'], 'generator_sha256': mapping['generator_sha256'],
                  'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'compiler': command,
                  'new_published_components': 0, 'source_boundary_transition_verified': False,
                  'original_CPU_or_GPU_execution_on_C_side': False, 'whole_game_complete': False,
                  'limits': ['291 directionally enabled actual CD gate records relocated into declared tile/record fixtures with controlled object coordinates; disabled records and synthetic signed-index/count/direction cases added.',
                             'Native M68000 and Unicorn match fixed C full registers/SR/USP/SSP, complete 2 MB RAM, MOVEM/RTS frames; Unicorn also matches ordered data bus.',
                             'No real boundary caller, cleanup, scheduler yield, CD loading, actor task reuse, natural doorway reachability, arbitrary pointer aliases or hardware timing proof.',
                             'This upgrades an already-counted logical geometry function; coordinator authored, no new local-model instruction authorship or training.']}
        queue.save(out / 'report.json', report)
        queue.save(out / 'status.json', {'status': 'terminal_pass'})
        queue.save(ROOT / 'verification/biwn-doorway-cpu-checks.json', report)
        print(json.dumps(report))
    except Exception as error:
        queue.save(out / 'status.json', {'status': 'terminal_failed', 'error': repr(error)})
        raise
    finally:
        runtime.close()


if __name__ == '__main__':
    main()
