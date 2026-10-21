"""Original versus phased actor initializer/dispatch on Unicorn and pinned CPU.

Uses the existing ordered volatile-read fixtures and helper providers. Original
10520 and sprite bodies execute; outside geometry/task leaf services remain
prescribed. Only 384 bytes below root SP and 64 bytes at/above root SP are
excluded as private stack; parameters and return SP are independently checked.
This is component evidence, not real streaming/IRQ or full gameplay.
"""
import argparse
import importlib.util
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT, V, read, save, sha

SOURCE = ROOT / 'projects/black-ice-white-noise/restoration/native-m68k/actor-phased-v1'


def load_copy(name, original, out):
    source = original.read_text()
    assert 'SP-8192' in source
    source = source.replace('SP-8192', 'SP-384')
    path = out / (name + '.py')
    path.write_text(source)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int)
    args = ap.parse_args()
    out = V / 'actor-phased-v1' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    state = dict(status='running_actor_phased_component_pairs', directory=str(out), pid=os.getpid(), completed=0,
                 new_predictions=0, new_training=False, disc_integrated=False, private_stack_comparison_bytes=384)
    def mark():
        save(out / 'protocol.json', state)
        save(V / 'actor-phased-v1-current.json', state)
    mark()
    native = None
    try:
        inputs = [Path(__file__), *[p for p in SOURCE.iterdir() if p.is_file()]]
        artifacts = {}
        for name, address in [('dispatch', 0x190000), ('initialize', 0x180000)]:
            build = out / ('build-' + name)
            p = subprocess.run(['make', '-C', str(SOURCE), 'MODULE=' + name, 'ADDRESS=' + hex(address), 'BUILD=' + str(build)], capture_output=True, text=True)
            (out / (name + '-build.log')).write_text(p.stdout + p.stderr)
            assert p.returncode == 0, p.stderr
            binary, elf = build / 'native.bin', build / 'native.elf'
            symbols = {x[2]: int(x[0], 16) for line in (build / 'symbols.txt').read_text().splitlines() if len(x := line.split()) == 3}
            artifacts[name] = dict(binary=str(binary), ELF=str(elf), symbols=symbols, code_address=address, binary_bytes=binary.stat().st_size)
            inputs += [binary, elf]
        init, ipath = load_copy('phased_init_engine', ROOT / 'scripts/check_biwn_native_actor_initialize.py', out)
        joint, jpath = load_copy('phased_joint_engine', ROOT / 'scripts/check_biwn_native_actor_dispatch_initialize_joint.py', out)
        inputs += [ipath, jpath, Path(init.g.__file__), Path(init.g.prior.__file__), ROOT / 'scripts/check_biwn_scheduler.py',
                   ROOT / 'render-assets/biwn-inventory-baseline.bin', ROOT / 'tools/blitter-runtime/virtualjaguar_libretro.dylib']
        hashes = {str(p): sha(p) for p in inputs}
        snapshot = (ROOT / 'render-assets/biwn-inventory-baseline.bin').read_bytes()
        assert sha(ROOT / 'render-assets/biwn-inventory-baseline.bin') == 'f3f70dadee1b6241419da361460208337dbbf9333e2da977144e8c97923a20d3'
        joint.INIT_PAYLOAD = Path(artifacts['initialize']['binary']).read_bytes()
        joint.INIT_SYMBOLS = artifacts['initialize']['symbols']
        native = init.Native()
        results, summaries = [], {}
        for kind, engine, artifact in [('initialize', init, artifacts['initialize']), ('joint', joint, artifacts['dispatch'])]:
            payload, symbols = Path(artifact['binary']).read_bytes(), artifact['symbols']
            rows = engine.vectors()
            if args.limit:
                rows = rows[:args.limit]
            save(out / (kind + '-fixtures.json'), rows)
            coverage, maximum, original_maximum = set(), 0, 0
            for index, case in enumerate(rows):
                a = engine.execute(snapshot, case, payload, symbols, False)
                b = engine.execute(snapshot, case, payload, symbols, True)
                if any(a[k] != b[k] for k in ['ram', 'registers', 'trace']):
                    save(out / 'mismatch.json', dict(kind=kind, index=index, case=case, original_trace=a['trace'], compiled_trace=b['trace'],
                        original_regs=a['registers'], compiled_regs=b['registers'], RAM_equal=a['ram'] == b['ram']))
                    raise AssertionError('Ordered CPU/public RAM comparison failed')
                an = engine.replay(native, snapshot, case, payload, symbols, False, a)
                bn = engine.replay(native, snapshot, case, payload, symbols, True, b)
                if an != bn:
                    save(out / 'native-mismatch.json', dict(kind=kind, index=index, case=case, original=an, compiled=bn))
                    raise AssertionError('Pinned CPU/SR/banks/helper entry mismatch')
                assert b['private_depth'] <= 384
                coverage.update(a['coverage'])
                maximum = max(maximum, b['private_depth'])
                original_maximum = max(original_maximum, a['private_depth'])
                results.append(dict(kind=kind, index=index, original_steps=len(a['machine']), compiled_steps=len(b['machine']),
                    original_depth=a['private_depth'], compiled_depth=b['private_depth'], calls=len(an['events'])))
                state['completed'] = len(results)
                if index % 64 == 0:
                    mark()
                    print(kind, index + 1, '/', len(rows), flush=True)
            summaries[kind] = dict(cases=len(rows), maximum_stack_bytes=maximum, original_maximum_stack_bytes=original_maximum,
                                   original_sites=sorted(coverage), full_CPU_SR_banks_RAM_ordered_trace_equal=True)
        assert all(sha(p) == h for p, h in hashes.items())
        save(out / 'results.json', results)
        state.update(status='terminal_actor_phased_preflight_pass' if args.limit else 'terminal_actor_phased_component_pairs_pass',
            source_accepted=not bool(args.limit), completed=len(results), artifacts=artifacts, summaries=summaries,
            scope=__doc__, dependencies_sha256=hashes, all_global_stack_paths_proven=False, arbitrary_IRQ_qualified=False,
            original_bodies_delegated=False, new_unique_original_functions=0)
        mark()
        print(state['status'], {k: (v['cases'], v['maximum_stack_bytes']) for k, v in summaries.items()}, flush=True)
    except BaseException as error:
        state.update(status='terminal_actor_phased_component_failed', error=repr(error))
        mark()
        raise
    finally:
        if native:
            native.close()


if __name__ == '__main__':
    main()
