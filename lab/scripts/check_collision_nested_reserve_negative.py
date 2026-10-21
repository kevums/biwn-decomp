"""Demonstrate why standalone collision tests cannot qualify nested stack use."""
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import check_native_movement_collision_joint as joint
import check_biwn_native_actor_collision_v2 as direct

ROOT = joint.e.ROOT
ND = joint.e.ND


def main():
    out = ROOT / 'verification/collision-nested-reserve-negative' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    snapshot, movement, symbols, parent, gate = joint.prepare(ROOT / 'verification/native-actor-collision-final-current.json')
    e = joint.e
    shim = (ND / 'actor-collision-shim.S').read_text()
    assert shim.count('.equ COLLISION_PRIVATE_RESERVE,704') == 1
    (out / 'actor-collision-shim.S').write_text(shim.replace('.equ COLLISION_PRIVATE_RESERVE,704', '.equ COLLISION_PRIVATE_RESERVE,512'))
    for name in ['actor-collision-native.h', 'actor-collision.ld']:
        (out / name).write_bytes((ND / name).read_bytes())
    command = ['make', '-f', str(ND / 'Makefile.actor-collision'), 'actor-collision', 'ROOT=' + str(ROOT), 'SOURCE_DIR=' + str(out) + '/', 'BUILD=' + str(out / 'build'), 'COLLISION_SOURCE=' + str(ND / 'actor-collision-reference.c'), 'ADDRESS=' + hex(e.COLLBASE)]
    p = subprocess.run(command, capture_output=True, text=True)
    (out / 'build.log').write_text(p.stdout + p.stderr)
    assert p.returncode == 0, p.stderr
    payload = (out / 'build/actor-collision.bin').read_bytes()
    nm = subprocess.check_output([str(ROOT / 'tools/m68k-elf/bin/m68k-elf-nm'), '-n', str(out / 'build/actor-collision.elf')], text=True)
    names = {x[2]: int(x[0], 16) for line in nm.splitlines() if len(x := line.split()) == 3}
    assert len(payload) == len(e.COLL_PAYLOAD)
    direct.BASE, direct.PARENT_RANGE = e.COLLBASE, e.PARENT_RANGE
    vectors = direct.vectors()
    standalone = sum([[c for c in vectors if c['entry'] == entry][:16] for entry in direct.g.PATCH_WIDTHS], [])
    native = e.Native()
    try:
        for case in standalone:
            a = direct.execute(snapshot, case, payload, names, False)
            b = direct.execute(snapshot, case, payload, names, True)
            assert all(a[k] == b[k] for k in ['ram', 'registers', 'trace'])
            assert direct.replay(native, snapshot, case, payload, names, False, a) == direct.replay(native, snapshot, case, payload, names, True, b)
        proof = direct.g.read(ROOT / 'verification/native-movement-collision-joint-current.json')
        rows = direct.g.read(Path(proof['directory']) / 'results.json')
        fixtures = e.vectors()
        index = max(range(len(rows)), key=lambda i: rows[i]['compiled_depth'])
        case = fixtures[index]
        a = e.execute(snapshot, case, movement, symbols, False)
        b = e.execute(snapshot, case, movement, symbols, True)
        assert all(a[k] == b[k] for k in ['ram', 'registers', 'trace'])
        assert e.replay(native, snapshot, case, movement, symbols, False, a) == e.replay(native, snapshot, case, movement, symbols, True, b)
        e.COLL_PAYLOAD, e.COLL_SYMBOLS = payload, names
        rejection = None
        try:
            bad = e.execute(snapshot, case, movement, symbols, True)
        except Exception as error:
            rejection = dict(reason='Nested execution failed', error=repr(error))
        else:
            fields = [k for k in ['ram', 'registers', 'trace'] if a[k] != bad[k]]
            if fields:
                rejection = dict(reason='Nested result mismatch', fields=fields, original_registers=a['registers'], defective_registers=bad['registers'])
        assert rejection, 'Insufficient nested reserve escaped the joint gate'
        direct.g.save(out / 'witness.json', dict(index=index, case=case, rejection=rejection, correct_reserve=704, defective_reserve=512, correct_max_depth=b['private_depth']))
    finally:
        native.close()
    paths = [Path(__file__), out / 'actor-collision-shim.S', out / 'actor-collision-native.h', out / 'actor-collision.ld', out / 'build/actor-collision.bin', out / 'build/actor-collision.elf', out / 'witness.json']
    state = dict(status='terminal_smaller_collision_reserve_rejected_in_composition', directory=str(out), standalone_cases_passed=len(standalone), joint_positive_pass=True, defective_joint_rejected=True, correct_reserve=704, defective_reserve=512, rejection=rejection, source_sha256={str(p): direct.g.sha(p) for p in paths}, scope=__doc__)
    direct.g.save(out / 'protocol.json', state)
    direct.g.save(ROOT / 'verification/collision-nested-reserve-negative-current.json', state)
    print(json.dumps(state))


if __name__ == '__main__':
    main()
