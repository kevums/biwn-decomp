"""Connect readable coordinate entry to input, panel, text and raw controller C.

An isolated controls variant keeps existing libraries/preview recipes intact.
First recheck the previous controls fixtures, discover actual coordinate-call
sites, then execute the real original coordinate body on the oracle side.
No model writes code or executes tests in this coordinator integration.
"""
import argparse
import copy
import ctypes as c
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

import check_biwn_game_controls as base

ROOT = base.ROOT
RESTORE = ROOT / 'projects/black-ice-white-noise/restoration'
LEGACY_FALLBACK = list(base.FALLBACK)
ORIGINAL_SCRIPT = base.Script
NAMES = ['biwn_input_dispatch.c', 'biwn_attack_effect.c', 'biwn_rng.c', 'biwn_signed_division.c',
         'biwn_camera.c', 'biwn_animation.c', 'biwn_memory.c', 'biwn_transition_cleanup.c',
         'biwn_resources.c', 'biwn_elevator_input.c', 'biwn_elevator_display.c',
         'biwn_elevator_formatter.c', 'biwn_formatter_cpu.c', 'biwn_panel_refresh.c',
         'biwn_text.c', 'biwn_input_poll.c', 'biwn_coordinate_entry.c', 'biwn_inventory_select.c']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


class Recorder(ORIGINAL_SCRIPT):
    def __init__(self, snapshot, case):
        super().__init__(snapshot, case)
        self.coordinate_prefix = None
        self.clock_pcs = []

    def observe_read(self, pc, address, width):
        if (address, width) == (0x778cc, 4):
            self.clock_pcs.append(pc)

    def call(self, address, args):
        if address == 0x18e92:
            assert self.coordinate_prefix is None
            self.coordinate_prefix = dict(raw_poll_calls=self.poll_reads // 4,
                clock_values=[x[3] for x in self.trace if x[:3] == ['r', 0x778cc, 4]],
                clock_pcs=self.clock_pcs[:])
        return super().call(address, args)


class ConnectedScript(Recorder):
    def before_native_instruction(self, runtime, pc):
        if self.case.get('coordinate_connected') and pc in self.case['native_clock_read_PCs']:
            value = self.read(0x778cc, 4)
            runtime.device.direct(0x778cc, 4, value)

    def read_native(self, runtime, address, width):
        if address == 0xf14000:
            return self.read(address, width)
        if self.case.get('coordinate_connected') and (address, width) == (0x778cc, 4):
            value = self.read(address, width)
            runtime.device.direct(address, width, value)
            return value
        return getattr(runtime.core, 'm68k_read_memory_' + str(width * 8))(address)


def build(out):
    previous = RESTORE / 'biwn_game_controls.c'
    text = previous.read_text()
    assert text.count(' case 0x20f0cu:') == 1
    text = text.replace('#include "biwn_game_controls.h"',
        '#include "biwn_game_controls_coordinate.h"\n#include "biwn_coordinate_entry.h"\n#include "biwn_inventory_select.h"')
    text = text.replace(' case 0x20f0cu:', ''' case 0x18e92u:
  if(count||!result)return BIWN_COORDINATE_BAD_ARGUMENT;
  return biwn_coordinate_entry_with_result(&ctx->inner,write8,100000u,*result,result);
 case 0x1b718u:
  if(count!=1u||!args||!result)return BIWN_COORDINATE_BAD_ARGUMENT;
  *result=biwn_button_digit(args[0],*result);return 0;
 case 0x20f0cu:''')
    text = text.replace('biwn_game_controls_with_scratch(', 'biwn_game_controls_coordinate_with_scratch(')
    text = text.replace('biwn_game_controls(', 'biwn_game_controls_coordinate(')
    source = out / 'biwn_game_controls_coordinate.c'
    source.write_text('/* Coordinator variant: original readable controls plus real coordinate entry. */\n' + text)
    header = out / 'biwn_game_controls_coordinate.h'
    header.write_text('''#ifndef BIWN_GAME_CONTROLS_COORDINATE_H
#define BIWN_GAME_CONTROLS_COORDINATE_H
#include "biwn_game_controls.h"
/* Coordinate18E92, digit1B718, raw controllerE4C0 and panel/text12620/149AE
 * execute source C in this variant. Scene20E8C/20F78 and scheduler services
 * remain external. Same logical D0/bus contract as existing controls.
 * Coordinate work has an added100000callback limit; nested errors become
 * dispatcher dependency errors with prior effects and unchanged outD0.
 * Other CPU registers/private stack, live frames and timing are excluded.
 */
enum biwn_dispatch_status biwn_game_controls_coordinate(struct biwn_world_bus *,
 biwn_input_write8,uint32_t,uint32_t,uint32_t *);
enum biwn_dispatch_status biwn_game_controls_coordinate_with_scratch(struct biwn_world_bus *,
 biwn_input_write8,uint32_t,uint32_t,uint32_t,uint32_t *);
#endif
''')
    library = out / 'libcoordinate-controls.dylib'
    command = ['clang', '-std=c99', '-dynamiclib', '-O2', '-Wall', '-Wextra', '-Werror',
               '-I', str(RESTORE), str(source)] + [str(RESTORE / name) for name in NAMES] + ['-o', str(library)]
    result = subprocess.run(command, capture_output=True, text=True,
                            env={**os.environ, 'DEVELOPER_DIR': '/Library/Developer/CommandLineTools'})
    (out / 'compiler.log').write_text(result.stdout + result.stderr)
    assert result.returncode == 0, result.stderr
    raw = c.CDLL(str(library)).biwn_game_controls_coordinate_with_scratch
    raw.argtypes = [c.POINTER(base.world.Bus), base.dispatch.W8, c.c_uint32, c.c_uint32, c.c_uint32, c.POINTER(c.c_uint32)]
    raw.restype = c.c_int
    def function(bus, write8, budget, incoming, output):
        return raw(bus, write8, base.DISPLAY_SCRATCH, budget, incoming, output)
    return function, command, source, header, library


def add_coordinate_inputs(case, prefix, actions):
    row = copy.deepcopy(case)
    row['coordinate_connected'] = True
    row['coordinate_actions'] = actions
    row['native_clock_read_PCs'] = sorted(set(prefix['clock_pcs'] + [0x18f24, 0x18f2a]))
    values = row.get('poll_values', [0x10000000])
    preserved = [values[min(i, len(values) - 1)] for i in range(prefix['raw_poll_calls'])]
    row['poll_values'] = preserved + [value for action in actions for value in [0, action]]
    if 'raw_poll_rows' in row:
        old = row['raw_poll_rows']
        row['raw_poll_rows'] = [old[min(i, len(old) - 1)] for i in range(prefix['raw_poll_calls'])] + [base.raw_rows(v) for action in actions for v in [0, action]]
    clocks = prefix['clock_values'][:]
    for i in range(len(actions)):
        start = 1000 * (i + 1)
        clocks += [start, start + 1, start + 74, start + 75]
    row['read_queues'] = [q for q in row.get('read_queues', []) if (q['address'], q['width']) != (0x778cc, 4)]
    row['read_queues'].append(dict(address=0x778cc, width=4, values=clocks))
    # Source panel1 uses a mutable coordinate string, unlike panel4 used by
    # the earlier elevator fixtures. Its original source layout is retained.
    row['initial'] += [[0x40ffc, 4, 0xb1202]]
    row['initial'] += [[0x410cc + i * 2, 2, v] for i, v in enumerate([55, 50, 150, 61, 4])]
    row['initial'] += [[0x410d6, 4, 0xb1200]]
    row['initial'] += [[0xb1200 + i, 1, v] for i, v in enumerate(b'\x05\x05 ___ ___\0\0')]
    return row


def digit_mapping(snapshot):
    from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN
    from unicorn.m68k_const import UC_CPU_M68K_M68000, UC_M68K_REG_SR, UC_M68K_REG_A7, UC_M68K_REG_D0
    cpu = Uc(UC_ARCH_M68K, UC_MODE_BIG_ENDIAN)
    cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000); cpu.mem_map(0, 0x200000); cpu.mem_write(0, snapshot)
    mapping = {}
    for bit in range(32):
        cpu.reg_write(UC_M68K_REG_SR, 0x2000); cpu.reg_write(UC_M68K_REG_A7, base.SP)
        cpu.mem_write(base.SP, base.STOP.to_bytes(4, 'big') + (1 << bit).to_bytes(4, 'big'))
        cpu.emu_start(0x1b718, base.STOP, count=128)
        digit = cpu.reg_read(UC_M68K_REG_D0) & 65535
        if digit <= 9:
            assert digit not in mapping; mapping[digit] = 1 << bit
    assert set(mapping) == set(range(10))
    return mapping


def integration_guards(function, snapshot, case, out):
    """Check new nested error routing without assigning original timeouts."""
    baseline = ConnectedScript(snapshot, case)
    base.original(baseline, case, set(), {})
    requests = [('r', 0x40ffc, 4), ('w', 0xb1202, 1), ('r', 0xf14000, 4),
                ('w', 0xf02200, 4), ('r', 0xb1202, 1)]
    targets = [0x20e8c, 0xdf60, 0xdf22, 0x20f78, 0xdf3e]
    points = []
    for kind, address, width in requests:
        points.append((next(i for i, x in enumerate(baseline.trace) if x[:3] == [kind, address, width]), (kind, address, width)))
    for target in targets:
        points.append((next(i for i, x in enumerate(baseline.trace) if x[:2] == ['call', target]), ('call', target)))
    guards = []
    for index, failure in points:
        failed = ConnectedScript(snapshot, case)
        if failure[0] == 'call': failed.fail_call = failure[1]
        elif failure[0] == 'r': failed.fail_read = failure[1:]
        else: failed.fail_write = failure[1:]
        status, output = base.dispatch.translated(function, failed, case, budget=1024)
        assert status == 3 and output == 0xa5a55a5a and failed.trace == baseline.trace[:index], (failure, status)
        prefix = ConnectedScript(snapshot, case)
        for event in baseline.trace[:index]:
            if event[0] == 'r': assert prefix.read(event[1], event[2]) == event[3]
            elif event[0] == 'w': prefix.write(*event[1:])
            else: prefix.call(event[1], event[2])
        assert failed.memory == prefix.memory and failed.MMIO == prefix.MMIO, failure
        guards.append(dict(failure=list(failure), status=status, public_RAM_and_MMIO_prefix_retained=True,
                           output_unchanged=True, matched_trace_prefix_events=index))
    frozen = copy.deepcopy(case)
    frozen['read_queues'] = [q for q in frozen['read_queues'] if q['address'] != 0x778cc]
    frozen['read_queues'].append(dict(address=0x778cc, width=4, values=[1000]))
    stopped = ConnectedScript(snapshot, frozen)
    status, output = base.dispatch.translated(function, stopped, frozen, budget=1024)
    assert status == 3 and output == 0xa5a55a5a and len(stopped.trace) >= 100000
    guards.append(dict(nonadvancing_clock=True, coordinate_callback_limit=100000, status=status,
                       output_unchanged=True, original_completion_claimed=False))
    save(out / 'coordinate-integration-guards.json', guards)
    return guards


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--preflight', action='store_true'); args = ap.parse_args()
    out = ROOT / 'verification/coordinate-controls' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True); print(out, flush=True)
    proof = json.loads((ROOT / 'verification/readable-coordinate-entry-current.json').read_text())
    assert sha(proof['source']) == proof['source_sha256']
    prior = json.loads((ROOT / 'verification/game-controls-current.json').read_text())
    snapshot = (ROOT / 'verification/zero-warm-startup-instruction-atlas.bin').read_bytes()
    vectors = base.cases(snapshot)
    old_results = json.loads((Path(prior['directory']) / 'results.json').read_text())
    assert len(vectors) == len(old_results) == prior['cases']
    state = dict(status='checking_previous_original_fixture_baseline', pid=os.getpid(), directory=str(out),
                 prior_proof=str(ROOT / 'verification/game-controls-current.json'), previous_cases=len(vectors),
                 main_preview_changed=False, new_training=False, whole_game_complete=False)
    def mark():
        save(out / 'protocol.json', state); save(ROOT / 'verification/coordinate-controls-active.json', state)
    mark()
    try:
        discovered = []
        for index, case in enumerate(vectors):
            observed = Recorder(snapshot, case)
            d0, steps = base.original(observed, case, set(), {})
            expected = old_results[index]
            assert d0 == expected['D0'] and hashlib.sha256(json.dumps(observed.trace).encode()).hexdigest() == expected['trace_sha256'] and hashlib.sha256(observed.memory).hexdigest() == expected['RAM_sha256'], index
            if observed.coordinate_prefix is not None:
                discovered.append(dict(index=index, kind=case['kind'], prefix=observed.coordinate_prefix,
                                       mode=int.from_bytes(observed.memory[0x49c60:0x49c62], 'big')))
            if index % 200 == 0:
                state['previous_baseline_checked'] = index + 1; mark()
                print('previous original baseline', index + 1, flush=True)
        assert discovered
        save(out / 'coordinate_call_discovery.json', discovered)
        for item in discovered:
            vectors[item['index']] = add_coordinate_inputs(vectors[item['index']], item['prefix'], [0x2000])
        seed = next(x for x in discovered if x['mode'] == 1)
        original_seed = base.cases(snapshot)[seed['index']]
        mapping = digit_mapping(snapshot); save(out / 'original_digit_mapping.json', mapping)
        def digits(text): return [mapping[int(x)] for x in text]
        actions = [('cancel', [0x2000]), ('backspace_at_start', [0x02000000, 0x2000]),
                   ('delete_first', digits('123') + [0x02000000] + digits('4') + [0x2000]),
                   ('delete_second', digits('123456') + [0x02000000] + digits('7') + [0x2000]),
                   ('ignore_extra_digits', digits('12345678') + [0x2000]),
                   ('early_confirm', digits('12') + [0x20000000, 0x2000])]
        for x, z in [(31, 32), (32, 31), (32, 32), (966, 719), (967, 719), (966, 720), (123, 456)]:
            actions.append((f'confirm_{x}_{z}', digits(f'{x:03}{z:03}') + [0x20000000, 0x2000]))
        for name, sequence in actions:
            row = add_coordinate_inputs(original_seed, seed['prefix'], sequence)
            row['kind'] = 'coordinate_' + name
            vectors.append(row)
        base.FALLBACK = [a for a in LEGACY_FALLBACK if a != 0x18e92] + [0x20e8c]
        base.SOURCE = dict(base.SOURCE)
        base.SOURCE.update({0x18e92: 0x190b8, 0x1b718: 0x1b780})
        base.EXTRA_SERVICES[0x20e8c] = []
        base.WIDTHS[0x20e8c] = []
        base.Script = ConnectedScript
        function, compiler, source, header, library = build(out)
        state.update(status='checking_connected_original_and_C', compiler=compiler, source=str(source),
                     source_sha256=sha(source), library=str(library), coordinate_call_sites=discovered,
                     remaining_fixture_targets=list(map(hex, base.FALLBACK)))
        mark()
        selected = [x for x in vectors if x['kind'].startswith('coordinate_')] if args.preflight else vectors
        coverage, entries, rows, native_vectors, native_skipped = set(), {}, [], [], []
        for index, case in enumerate(selected):
            original, rebuilt = ConnectedScript(snapshot, case), ConnectedScript(snapshot, case)
            seen = {}
            expected, steps = base.original(original, case, coverage, seen)
            status, actual = base.dispatch.translated(function, rebuilt, case, budget=1024)
            public_RAM_match = (rebuilt.memory[:base.SP - 0x1000] == original.memory[:base.SP - 0x1000]
                                and rebuilt.memory[base.SP + 8:] == original.memory[base.SP + 8:])
            if status or rebuilt.errors or actual != expected or rebuilt.trace != original.trace or not public_RAM_match or rebuilt.MMIO != original.MMIO:
                save(out / 'mismatch.json', dict(index=index, case=case, status=status, errors=rebuilt.errors,
                    original_D0=expected, C_D0=actual, original_trace=original.trace, C_trace=rebuilt.trace,
                    RAM_differences=[hex(i) for i, (a, b) in enumerate(zip(original.memory, rebuilt.memory)) if a != b][:30]))
                raise AssertionError(out / 'mismatch.json')
            for address, count in seen.items(): entries[address] = entries.get(address, 0) + count
            rows.append(dict(index=index, kind=case['kind'], state=case['state'], D0=actual, original_steps=steps,
                source_entries={hex(a): n for a, n in seen.items()}, trace_sha256=hashlib.sha256(json.dumps(original.trace).encode()).hexdigest(),
                RAM_sha256=hashlib.sha256(original.memory).hexdigest()))
            if case['kind'].startswith('coordinate_') or (not args.preflight and case.get('coordinate_connected')):
                unsupported = [q for q in case.get('read_queues', []) if (q['address'], q['width']) != (0x778cc, 4)]
                if unsupported:
                    native_skipped.append(dict(kind=case['kind'], queued_reads=unsupported,
                        reason='Like the existing controls native lane, this adapter does not inject arbitrary queued RAM reads. Full Unicorn/C trace/RAM/D0 comparison passed; native clock and raw controller injection only.'))
                else:
                    native_vectors.append((case, expected, original.memory))
            if index % 200 == 0:
                state['connected_cases_checked'] = index + 1; mark(); print('connected original/C', index + 1, flush=True)
        coordinate_coverage = sorted(x for x in coverage if 0x18e92 <= x < 0x190b8)
        assert len(coordinate_coverage) == 166, list(map(hex, coordinate_coverage))
        save(out / 'case-results.json', rows)
        save(out / 'fixtures.json', selected)
        save(out / 'native-scope-exclusions.json', native_skipped)
        state.update(connected_cases_checked=len(rows), all_original_C_cases_passed=True,
                     coordinate_instruction_locations=len(coordinate_coverage)); mark()
        native_rows = []
        core = Path(json.loads((ROOT / 'verification/DSP-music-context-experimental-candidate.json').read_text())['core_path'])
        oracle = base.media.scheduler.Native(diagnostic_core=core)
        runtime = base.media.Runtime.__new__(base.media.Runtime)
        runtime.oracle, runtime.device, runtime.core = oracle, oracle.device, oracle.lib
        try:
            for case, expected, memory in native_vectors:
                state.update(status='checking_native_CPU_and_real_blitter', native_case=case['kind']); mark()
                native_rows.append(base.native_check(runtime, function, snapshot, case, expected, memory, out))
                print('native/blitter', case['kind'], flush=True)
        finally:
            oracle.close()
        guard_case = next(case for case in selected if case['kind'] == 'coordinate_confirm_123_456')
        guards = integration_guards(function, snapshot, guard_case, out)
        report = dict(status='coordinate_input_panel_poll_digit_controls_match', recorded_at=datetime.now(timezone.utc).isoformat(),
            directory=str(out), previous_original_baseline_cases=len(old_results), cases=len(rows), coordinate_instruction_locations=len(coordinate_coverage),
            source_entry_counts={hex(a): n for a, n in entries.items()}, native_cases=len(native_rows),
            native_scope_exclusions=native_skipped,
            native_actual_blitter_commands=sum(x['actual_blitter_commands'] for x in native_rows),
            integration_error_and_budget_guards=len(guards),
            source=str(source), header=str(header), source_sha256=sha(source), header_sha256=sha(header),
            library=str(library), library_sha256=sha(library), compiler=compiler,
            sources_sha256={str(RESTORE / name): sha(RESTORE / name) for name in NAMES + ['biwn_game_controls.c']},
            remaining_fixture_helpers=list(map(hex, base.FALLBACK)),
            coordinate_remaining_fixture_helpers=['0x20e8c', '0xdf60', '0xdf22', '0x20f78', '0xdf3e'],
            full_D0=True, ordered_public_bus_and_RAM=True, source_panel_text_poll_digit_linked=True,
            coordinate_helper_result_supplied=False, raw_controller_rows_supplied=True, clock_read_values_supplied=True,
            physical_controller_or_timing_verified=False, live_frame_runtime_changed=False, new_training=False,
            code_authorship='Coordinator integration/source; existing recovered C components reused. No new local-model code.',
            whole_game_complete=False, preflight_only=args.preflight,
            scope='Readable input/item dispatcher calls actual C coordinate entry, which uses real C digit decoding, panel/text and raw controller polling. Original oracle executes the corresponding instructions. Full public D0/ordered logical bus/external RAM match; selected native CPU plus actual pinned blitter compare RAM/framebuffer and raw I/O/helper trace. Clock values and four raw controller rows are supplied, five coordinate scene/scheduler services remain fixture bodies. Private CPU stack/CCR/other caller-saved registers, live frames and physical timing excluded. Prior default controls and P/O recipes unchanged.')
        save(out / 'case-results.json', rows); save(out / 'native-cases.json', native_rows)
        save(out / 'fixtures.json', selected); save(out / 'report.json', report)
        state.update(status='terminal_coordinate_controls_match', proof=str(out / 'report.json')); mark()
        if not args.preflight: save(ROOT / 'verification/coordinate-controls-current.json', report)
        print(report['status'], len(rows), 'native', len(native_rows), flush=True)
    except BaseException as error:
        state.update(status='terminal_failed', error=repr(error)); mark(); raise


if __name__ == '__main__':
    main()
