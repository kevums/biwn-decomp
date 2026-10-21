"""Readable rotation versus original pinned M68000 and Unicorn; display service is a fixture."""
import ctypes as c
import json, os, random, subprocess
from pathlib import Path
from datetime import datetime, timezone
import check_scene17_structured_host_v2 as base
from publish_scene_reset_fresh_v1 import ROOT, V, read, save, sha


def main():
    source = ROOT/'projects/black-ice-white-noise/restoration/experimental/scene-rotation-structured-v1'
    out = V/'scene-rotation-structured-host-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    pointer = V/'scene-rotation-structured-host-v1-current.json'
    state = dict(status='building', directory=str(out), pid=os.getpid(), completed=0, new_predictions=0, new_training=False)
    def mark():
        save(out/'protocol.json', state)
        save(pointer, state)
    mark()
    runtime = None
    try:
        library = out/'rotation.dylib'
        command = ['clang', '-dynamiclib', '-std=c99', '-O2', '-Wall', '-Wextra', '-Werror', str(source/'host-wrapper.c'), '-o', str(library)]
        result = subprocess.run(command, capture_output=True, text=True)
        (out/'compiler.log').write_text(result.stdout+result.stderr)
        assert result.returncode == 0, result.stderr
        session = Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
        mapping = read(session/'scene-draw-fullCPU-generation.json')
        legacy_library = V/'scene17-structured-host-v1/20261020T230553.352177Z/libscene-draw-cpu.dylib'
        runtime = base.Runtime(legacy_library, mapping['instructions_decoded'])
        runtime.lib = c.CDLL(str(library))
        runtime.fn = runtime.lib.biwn_scene_rotation_body
        runtime.call = runtime.lib.biwn_scene_rotation_call
        for fn in [runtime.fn, runtime.call]:
            fn.argtypes = [c.POINTER(base.cd.world.Bus), c.POINTER(base.CPU), base.cd.dispatch.W8,
                           base.cd.world_cpu.SERVICE, c.c_void_p, c.c_uint32, c.c_int]
            fn.restype = c.c_int
        old = [x for x in base.cases() if x['entry'] == 0x17f14]
        assert len(old) == 128
        snapshot = (ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
        rows, coverage, cases = [], set(), []
        rng = random.Random(0x17f14025)
        addresses = {0xbd830, 0xbd834, 0xbd838, 0xbd83c, 0xbd840, 0xbd844}
        for i in range(256):
            case = json.loads(json.dumps(old[i%len(old)]))
            supervisor = bool((i//32)%2)
            case.update(id=i, SR=(0x2000 if supervisor else 0)|((i//64)<<8)|(i%32), body=bool((i//64)%2))
            sp = case['registers'][15]
            case['usp'] = 0x170000 if supervisor else sp
            case['ssp'] = sp if supervisor else 0x1d0000
            if i >= 128:
                for item in case['initial']:
                    if item[0] in addresses:
                        item[2] = [0, 0xffffffff, 0x80000000, rng.getrandbits(32)][i%4]
            cases.append(case)
            ram = base.fixture(snapshot, case)
            left, expected, original = runtime.native(ram, case, coverage)
            independent, other, unicorn = runtime.unicorn(ram, case, coverage)
            right, actual, rebuilt = runtime.translated(ram, case)
            valid = (not rebuilt['status'] and not rebuilt['errors'] and bytes(expected)==bytes(other)==bytes(actual)
                     and left==independent==right and unicorn['trace']==rebuilt['trace'] and original['calls']==rebuilt['calls'])
            if not valid:
                save(out/'counterexample.json', dict(case=case, original_CPU=base.cd.scheduler.cpu_dict(expected),
                     Unicorn_CPU=base.cd.scheduler.cpu_dict(other), rebuilt_CPU=base.cd.scheduler.cpu_dict(actual),
                     original=original, Unicorn=unicorn, rebuilt=rebuilt,
                     RAM_differences=[hex(j) for j,(a,b) in enumerate(zip(left,right)) if a!=b][:32]))
            assert valid, out/'counterexample.json'
            rows.append(dict(case=i, body=case['body'], CCR=i%32, supervisor=supervisor,
                             complete_CPU_RAM_helper_states_order_match=True, ordered_accesses=len(rebuilt['trace'])))
            state.update(status='checking', completed=len(rows))
            mark()
        expected_pcs = {x['address'] for x in mapping['instructions_decoded'] if 0x17f14<=x['address']<=0x17f66}
        assert coverage == expected_pcs, (coverage^expected_pcs)
        guards = []
        case = cases[0]
        ram = base.fixture(snapshot, case)
        for options, expected in [(dict(null_bus=True),1),(dict(null_cpu=True),1),(dict(null_service=True),1),
                                  (dict(budget=0),1),(dict(bad_pc=True),7),(dict(stop_flag=1),1),
                                  (dict(fail=('read',4)),2),(dict(fail=('write',4)),2),(dict(fail=('helper',0x185b2)),3)]:
            _, _, result = runtime.translated(ram, case, **options)
            assert result['status']==expected and result['CPU_unchanged'], (options, result)
            guards.append(dict(options=options, expected=expected))
        for missing in range(6):
            _, _, result = runtime.translated(ram, case, missing=missing)
            assert result['status']==1 and result['CPU_unchanged'] and not result['trace']
            guards.append(dict(missing_callback=missing, expected=1))
        save(out/'cases.json', rows)
        save(out/'vectors.json', cases)
        save(out/'guards.json', guards)
        state.update(status='terminal_structured_rotation_dual_CPU_RAM_order_match', host_guards=len(guards),
                     original_instruction_coverage=[len(coverage),len(expected_pcs)], library=str(library),
                     source_sha256={str(p):sha(p) for p in [Path(__file__), Path(base.__file__), legacy_library, session/'scene-draw-fullCPU-generation.json', *source.glob('*'), library, out/'cases.json', out/'vectors.json', out/'guards.json']},
                     scope=__doc__+' All256complete CPU/2MB RAM/private guest frames and ordered Unicorn/C bus comparisons. All32CCR and both banks; body/full-call; edge-valued pointer triples. No target machine code, real185B2, fresh game, IRQ or console proof. No new unique original routine.')
        mark()
        print(state['status'], state['completed'], state['host_guards'], flush=True)
    except BaseException as error:
        state.update(status='terminal_failed', error=repr(error))
        mark()
        raise
    finally:
        if runtime:
            runtime.close()


if __name__ == '__main__':
    main()
