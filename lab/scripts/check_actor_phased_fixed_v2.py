"""Compare fixed-address actor phases and guarded captured-depth task fixtures."""
import argparse
import copy
import ctypes as c
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT, V, read, save, sha
from check_actor_phased_v1 import load_copy
from review_v40_actor_initialize_header_fault_v1 import Row

SOURCE = ROOT / 'projects/black-ice-white-noise/restoration/native-m68k/actor-phased-fixed-v2'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int)
    args = ap.parse_args()
    prior_path = V / 'actor-phased-v1-current.json'
    prior = read(prior_path)
    assert prior['source_accepted'] and prior['summaries']['initialize']['cases'] == 1024 and prior['summaries']['joint']['cases'] == 856
    for p, h in prior['dependencies_sha256'].items():
        assert sha(p) == h, p
    out = V / 'actor-phased-fixed-v2' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    state = dict(status='running_fixed_actor_source_and_task_layout', directory=str(out), pid=os.getpid(), completed=0,
        new_predictions=0, new_training=False, disc_integrated=False)
    def mark():
        save(out / 'protocol.json', state)
        save(V / 'actor-phased-fixed-v2-current.json', state)
    mark()
    native = None
    try:
        artifacts = {}
        inputs = [Path(__file__), ROOT / 'scripts/check_actor_phased_v1.py', prior_path, *[p for p in SOURCE.iterdir() if p.is_file()]]
        prototype = SOURCE.with_name('actor-phased-v1')
        for name in ['dispatch.c', 'initialize.c', 'dispatch.S', 'initialize.S', 'native.h', 'Makefile']:
            assert (SOURCE / name).read_bytes() == (prototype / name).read_bytes()
        for name, address, entry, end in [('dispatch', 0x163788, 0x1638c8, 0x1639c4), ('initialize', 0x1639c4, 0x163eec, 0x164014)]:
            build = out / ('build-' + name)
            p = subprocess.run(['make', '-C', str(SOURCE), 'MODULE=' + name, 'BUILD=' + str(build)], capture_output=True, text=True)
            (out / (name + '-build.log')).write_text(p.stdout + p.stderr)
            assert p.returncode == 0, p.stderr
            binary, elf = build / 'native.bin', build / 'native.elf'
            symbols = {x[2]: int(x[0], 16) for line in (build / 'symbols.txt').read_text().splitlines() if len(x := line.split()) == 3}
            assert symbols['biwn_native_actor_' + name] == entry and address + binary.stat().st_size <= end
            artifacts[name] = dict(binary=str(binary), ELF=str(elf), symbols=symbols, code_address=address, binary_bytes=binary.stat().st_size, entry=entry)
            inputs += [binary, elf]
        init, ipath = load_copy('fixed_init_engine', ROOT / 'scripts/check_biwn_native_actor_initialize.py', out)
        joint, jpath = load_copy('fixed_joint_engine', ROOT / 'scripts/check_biwn_native_actor_dispatch_initialize_joint.py', out)
        init.BASE = joint.INITBASE = artifacts['initialize']['code_address']
        joint.BASE = artifacts['dispatch']['code_address']
        joint.INIT_PAYLOAD = Path(artifacts['initialize']['binary']).read_bytes()
        joint.INIT_SYMBOLS = artifacts['initialize']['symbols']
        inputs += [ipath, jpath, ROOT / 'scripts/review_v40_actor_initialize_header_fault_v1.py', Path(init.g.__file__), Path(init.g.prior.__file__),
            ROOT / 'scripts/check_biwn_scheduler.py', ROOT / 'render-assets/biwn-inventory-baseline.bin', ROOT / 'tools/blitter-runtime/virtualjaguar_libretro.dylib']
        trace_path = V / 'v40-input-transition-fault-trace-v2-current.json'
        trace = read(trace_path)
        ring_path = Path(trace['directory']) / 'instruction-ring.bin'
        memory_path = Path(trace['directory']) / 'first-watch-RAM.bin'
        raw = ring_path.read_bytes()
        ring = [Row.from_buffer_copy(raw[i:i+c.sizeof(Row)]) for i in range(0, len(raw), c.sizeof(Row))]
        captured = {}
        memory = memory_path.read_bytes()
        baseline = (ROOT / 'render-assets/biwn-inventory-baseline.bin').read_bytes()
        for kind, entry, offset in [('initialize', 0x134dc, 520), ('joint', 0x13ae0, 556)]:
            row = next(x for x in ring if x.pc == entry)
            assert row.frame == 8978 and row.cpu.registers[15] == row.task + offset
            stack, params = row.cpu.registers[15], []
            at = stack + 4
            for width in init.g.prior.WIDTHS[entry]:
                params.append(int.from_bytes(memory[at:at+width], 'big'))
                at += width
            captured[kind] = dict(entry=entry, params=params, incoming=list(row.cpu.registers)[:15], sr=row.cpu.sr,
                initial=[], read_queues=[], default_helper_return=0, helper_returns={str(0x152a2): 0x110000})
        save(out / 'captured-entry-fixtures.json', captured)
        inputs += [trace_path, ring_path, memory_path, out / 'captured-entry-fixtures.json']
        hashes = {str(p): sha(p) for p in inputs}
        native = init.Native()
        results, summaries = [], {}

        def compare(kind, engine, artifact, case, snapshot, slot=None):
            payload, symbols = Path(artifact['binary']).read_bytes(), artifact['symbols']
            a = engine.execute(snapshot, case, payload, symbols, False)
            b = engine.execute(snapshot, case, payload, symbols, True)
            if any(a[k] != b[k] for k in ['ram', 'registers', 'trace']):
                save(out / 'mismatch.json', dict(kind=kind, slot=slot, case=case, original_trace=a['trace'], compiled_trace=b['trace'],
                    original_regs=a['registers'], compiled_regs=b['registers'], RAM_equal=a['ram'] == b['ram']))
                raise AssertionError('Fixed-address comparison failed')
            an = engine.replay(native, snapshot, case, payload, symbols, False, a)
            bn = engine.replay(native, snapshot, case, payload, symbols, True, b)
            assert an == bn, (kind, slot, 'Pinned CPU/SR/banks/helper entries differ')
            assert b['private_depth'] <= 384
            if slot is not None:
                task = 0xc0928 + slot * 1024
                assert a['ram'][task:task+64] == b['ram'][task:task+64] == snapshot[task:task+64], (kind, slot, 'protected guard')
                assert engine.SP - b['private_depth'] >= task + 64
            result = dict(kind=kind, slot=slot, root_SP=engine.SP, compiled_depth=b['private_depth'], original_depth=a['private_depth'],
                calls=len(an['events']), original_sites=sorted(a['coverage']), CPU_SR_banks_ordered_RAM_equal=True)
            results.append(result)
            state['completed'] = len(results)
            return result

        for kind, engine, artifact in [('initialize', init, artifacts['initialize']), ('joint', joint, artifacts['dispatch'])]:
            rows = engine.vectors()
            if args.limit:
                rows = rows[:args.limit]
            maximum = 0
            for i, case in enumerate(rows):
                result = compare(kind, engine, artifact, case, baseline)
                maximum = max(maximum, result['compiled_depth'])
                if i % 64 == 0:
                    mark()
                    print('fixed', kind, i + 1, '/', len(rows), flush=True)
            summaries[kind] = dict(cases=len(rows), maximum_stack_bytes=maximum)
            task_cases = [copy.deepcopy(rows[i]) for i in sorted(set([0, min(4, len(rows)-1), min(5, len(rows)-1), min(6, len(rows)-1)]))]
            # The captured parameter/register case uses the baseline's valid
            # geometry/provider data; no live gameplay snapshot is resumed.
            captured_case = copy.deepcopy(captured[kind])
            captured_case['initial'] = copy.deepcopy(rows[0]['initial'])
            task_cases.append(captured_case)
            plans = [(slot, i) for slot in [0, 50, 100] for i in range(len(task_cases))] + [(slot, slot % len(task_cases)) for slot in range(101)]
            for i, (slot, case_index) in enumerate(plans):
                task = 0xc0928 + slot * 1024
                engine.SP = task + (520 if kind == 'initialize' else 556)
                snapshot = bytearray(baseline)
                snapshot[task:task+64] = bytes((j*37 + slot*11 + i) % 256 for j in range(64))
                snapshot[0xc0920:0xc0924] = task.to_bytes(4, 'big')
                compare(kind, engine, artifact, task_cases[case_index], bytes(snapshot), slot)
            summaries[kind]['task_layout_pairs'] = len(plans)
            summaries[kind]['captured_entry_SP_above_task'] = 520 if kind == 'initialize' else 556
            engine.SP = init.g.SP
        assert all(sha(p) == h for p, h in hashes.items())
        save(out / 'results.json', results)
        state.update(status='terminal_fixed_actor_phased_preflight_pass' if args.limit else 'terminal_fixed_actor_phased_components_and101taskslots_pass',
            source_accepted=not bool(args.limit), artifacts=artifacts, summaries=summaries, completed=len(results), task_slots=101,
            protected_task_bytes=64, physical_metadata_bytes=38, new_per_task_arena_bytes=0,
            captured_fixture_uses_baseline_geometry=True, captured_gameplay_resumed=False,
            lower_helpers_prescribed=True, arbitrary_IRQ_qualified=False, global_stack_bound_proven=False,
            dependencies_sha256=hashes, new_unique_original_functions=0)
        mark()
        print(state['status'], summaries, flush=True)
    except BaseException as error:
        state.update(status='terminal_fixed_actor_phased_failed', error=repr(error))
        mark()
        raise
    finally:
        if native:
            native.close()


if __name__ == '__main__':
    main()
