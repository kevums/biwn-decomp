"""Read actual entrance target actor records and source dispatch table."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from biwn_disc_backend import Disc, ROOT


def main():
    disc = Disc()
    base = (ROOT / 'render-assets/biwn-inventory-baseline.bin').read_bytes()
    inventory = json.loads((ROOT / 'verification/biwn-disc-gate-target-inventory.json').read_text())
    targets = sorted({gate['target'] for gate in inventory['directionally_enabled_gates']})
    rows = []
    invalid = []
    for target in targets:
        marker = disc.data.find((0x6000 + target).to_bytes(4, 'big') * 16)
        payload = disc.data[marker + 64:marker + 64 + 4704]
        u = lambda a, n: int.from_bytes(payload[a:a + n], 'big')
        texture = u(8, 4) + u(2, 2) * 6
        texture_count = u(texture, 2)
        actor_start = texture + 2 + texture_count * 2
        count = u(actor_start, 2)
        if marker < 0 or actor_start + 2 + count * 8 > 4704:
            invalid.append(target)
            continue
        actors = []
        for index in range(count):
            record = payload[actor_start + 2 + index * 8:actor_start + 10 + index * 8]
            actor_id = int.from_bytes(record[:2], 'big')
            table = 0x13620 + 2 * (actor_id - 4)
            delta = int.from_bytes(base[table:table + 2], 'big', signed=True) if 4 <= actor_id <= 118 else None
            destination = 0x13620 + delta if delta is not None else 0x137ca
            actors.append({'id': actor_id, 'record_hex': record.hex(), 'dispatch_target': hex(destination),
                           'requests_task': 0x13706 <= destination <= 0x137b6})
        rows.append({'interior': target, 'marker': marker, 'actor_count': count, 'actors': actors,
                     'payload_sha256': hashlib.sha256(payload).hexdigest()})
    active = [row for row in rows if any(actor['requests_task'] for actor in row['actors'])]
    result = {'recorded_at': datetime.now(timezone.utc).isoformat(),
              'status': 'read_only_actual_entrance_target_actor_dispatch_inventory', 'interiors': rows,
              'invalid_targets': invalid, 'source_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'limits': 'Source record/table inspection; no loading/task creation or natural input reachability proof.'}
    path = ROOT / 'verification/biwn-entrance-target-actor-dispatch-inventory.json'
    path.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'path': str(path), 'targets_inspected': len(rows),
                      'targets_with_scheduled_actors': len(active), 'sample': active[:6]}))


if __name__ == '__main__':
    main()
