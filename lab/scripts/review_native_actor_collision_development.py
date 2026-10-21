"""Audit original instruction coverage and reject concrete collision defects.

These controls qualify the finite original-facing component oracle. They do not
establish live task-stack safety, GPU timing, physical hardware or a full game.
"""
import copy
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import capstone
import check_biwn_native_actor_collision_v2 as engine

ROOT = engine.ROOT
ND = engine.ND


def main():
    proof = engine.g.read(ROOT / 'verification/native-actor-collision-prototype-current.json')
    joint = engine.g.read(ROOT / 'verification/native-movement-collision-joint-current.json')
    assert proof['status'] == 'terminal_original_ABI_actor_collision_pass'
    assert joint['status'] == 'terminal_native_movement_collision_joint_pass'
    for record in [proof, joint]:
        for name, digest in record['source_sha256'].items():
            assert engine.g.sha(name) == digest, name
    out = ROOT / 'verification/actor-collision-development-review' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    engine.g.save(out / 'component-proof.json', proof)
    engine.g.save(out / 'joint-proof.json', joint)
    snapshot = (ROOT / 'render-assets/biwn-inventory-baseline.bin').read_bytes()
    decoder = capstone.Cs(capstone.CS_ARCH_M68K, capstone.CS_MODE_BIG_ENDIAN | capstone.CS_MODE_M68K_000)
    sites = {ins.address for ins in decoder.disasm(snapshot[0x13b5a:0x13c9a], 0x13b5a)}
    covered = set(proof['original_sites'])
    assert covered <= sites, sorted(covered - sites)
    missing = sites - covered
    engine.g.save(out / 'instruction-coverage.json', dict(decoded=sorted(sites), executed=sorted(covered), missing=sorted(missing)))
    assert not missing, [hex(x) for x in sorted(missing)]
    payload = Path(proof['binary']).read_bytes()
    symbols = proof['symbols']
    engine.BASE = proof['code_address']
    cases = engine.vectors()
    cache = {}
    native = engine.Native()

    def original(index):
        if index not in cache:
            a = engine.execute(snapshot, cases[index], payload, symbols, False)
            cache[index] = (a, engine.replay(native, snapshot, cases[index], payload, symbols, False, a))
        return cache[index]

    source = (ND / 'actor-collision-reference.c').read_text()
    controls = []
    defects = [
        ('missing_body', source.replace('s.r=r;entry=r[18];', 's.r=r;entry=r[18];return;')),
        ('helper_X_cleared', source.replace('(void)ret;switch(target)', '(void)ret;s->r[16]&=~0x10u;switch(target)')),
        ('full_D0_clear_instead_of_low_word', source.replace('word(&s,0,0);', 's.r[0]=0;')),
    ]
    try:
        for name, body in defects:
            assert body != source
            variant = out / name
            variant.mkdir()
            cfile = variant / 'actor-collision-defect.c'
            cfile.write_text(body)
            command = ['make', '-f', str(ND / 'Makefile.actor-collision'), 'actor-collision', 'BUILD=' + str(variant / 'build'), 'COLLISION_SOURCE=' + str(cfile), 'ADDRESS=' + hex(engine.BASE)]
            p = subprocess.run(command, capture_output=True, text=True)
            (variant / 'build.log').write_text(p.stdout + p.stderr)
            assert p.returncode == 0, p.stderr
            bad = (variant / 'build/actor-collision.bin').read_bytes()
            nm = subprocess.check_output([str(ROOT / 'tools/m68k-elf/bin/m68k-elf-nm'), '-n', str(variant / 'build/actor-collision.elf')], text=True)
            names = {x[2]: int(x[0], 16) for line in nm.splitlines() if len(x := line.split()) == 3}
            witness = None
            for index, case in enumerate(cases):
                a, an = original(index)
                b = engine.execute(snapshot, case, bad, names, True)
                bn = engine.replay(native, snapshot, case, bad, names, True, b)
                fields = [k for k in ['ram', 'registers', 'trace'] if a[k] != b[k]]
                native_fields = [k for k in an if an[k] != bn[k]]
                if fields or native_fields:
                    witness = dict(defect=name, rejected=True, fixture=index, entry=hex(case['entry']), ordered_differences=fields, native_differences=native_fields, original_native=an, defective_native=bn)
                    engine.g.save(variant / 'witness.json', dict(case=case, **witness))
                    break
            assert witness, 'Defect escaped component comparison: ' + name
            controls.append(witness)
            print(name, 'rejected at', witness['fixture'], witness['native_differences'], flush=True)
        for entry, label in [(0x13b5a, 'outdoor'), (0x13bb0, 'indoor')]:
            names = dict(symbols)
            root = 'biwn_native_actor_collision_' + label
            # An alleged replacement delegating the original body must fail the
            # execution guard, even if its ultimate result would match.
            names[root] = entry + engine.g.PATCH_WIDTHS[entry]
            index = next(i for i, c in enumerate(cases) if c['entry'] == entry)
            rejected = None
            try:
                engine.execute(snapshot, cases[index], payload, names, True)
            except AssertionError as error:
                assert 'Original collision instruction reached' in str(error), repr(error)
                rejected = repr(error)
            assert rejected, 'Original-body delegation was accepted'
            controls.append(dict(defect=label + '_original_delegation', rejected=True, fixture=index, error=rejected))
    finally:
        native.close()
    engine.g.save(out / 'negative-controls.json', controls)
    inputs = [Path(__file__), out / 'component-proof.json', out / 'joint-proof.json', out / 'instruction-coverage.json', out / 'negative-controls.json']
    inputs += list(out.rglob('*.c')) + list(out.rglob('*.bin')) + list(out.rglob('*.elf')) + list(out.rglob('witness.json'))
    record = dict(status='terminal_actor_collision_development_review_pass', directory=str(out), cases=proof['cases'], per_root_cases=proof['per_root_cases'], original_instruction_sites=len(sites), native_bytes=proof['binary_bytes'], component_max_private=proof['max_private_depth'], joint_cases=joint['cases'], joint_max_private=joint['max_private_depth'], outdoor_joint_entries=joint['outdoor_entries'], indoor_joint_entries=joint['indoor_entries'], negative_controls=len(controls), source_sha256={str(p): engine.g.sha(p) for p in inputs}, disc_integrated=False, live_task_stack_verified=False, scope=__doc__)
    engine.g.save(out / 'protocol.json', record)
    engine.g.save(ROOT / 'verification/actor-collision-development-reviewed-current.json', record)
    print(json.dumps({k: record[k] for k in ['status', 'original_instruction_sites', 'negative_controls', 'joint_cases']}))


if __name__ == '__main__':
    main()
