"""Measure address reachability added by the accepted route; no decomp percent."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def main():
    proof_path = ROOT / 'verification/source-checkpoint-route532-current.json'
    proof = json.loads(proof_path.read_text())
    assert proof['status'] == 'source_checkpoint_ordinary_route_to_building532_match'
    comparison = json.loads(Path(proof['comparison']).read_text())
    assert [key for key, passed in comparison['checks'].items() if not passed] == ['DSP_owned_positive']
    old_path = ROOT / 'verification/main-CPU-multi-route-coverage-current.json'
    old = json.loads(old_path.read_text())
    manifest_path = Path(old['static_manifest'])
    manifest = json.loads(manifest_path.read_text())
    assert hashlib.sha256((manifest_path.parent / 'listing.asm').read_bytes()).hexdigest() == old['static_listing_sha256']
    static = {int(row['address'], 16) for row in manifest['instructions']}
    assert len(static) == old['static_instruction_addresses'] == 18306
    unreached = {int(value, 16) for value in old['unreached_static_addresses']}
    previous = static - unreached
    assert len(previous) == old['static_addresses_reached_union']
    trace = Path(proof['directory']) / 'C/CPU-before-instructions.bin'
    assert trace.stat().st_size == proof['CPU_instructions'] * 78
    observed = set()
    digest = hashlib.sha256()
    count = 0
    with trace.open('rb') as stream:
        while block := stream.read(78 * 1000000):
            assert len(block) % 78 == 0
            digest.update(block)
            records = len(block) // 78
            addresses = np.ndarray(shape=(records,), dtype='>u4', buffer=block, offset=64, strides=(78,))
            observed.update(map(int, np.unique(addresses)))
            count += records
    assert count == proof['CPU_instructions']
    assert comparison['sha256']['CPU-before-instructions.bin'] == [digest.hexdigest()] * 2
    added = (observed & static) - previous
    union = previous | (observed & static)
    functions = {int(row['address'], 16): row['name'] for row in manifest['functions']}
    new_entries = sorted(set(functions) & added)
    report = dict(status='accepted_route532_static_address_coverage_measured', recorded_at=datetime.now(timezone.utc).isoformat(),
                  route_proof=str(proof_path), route_proof_sha256=hashlib.sha256(proof_path.read_bytes()).hexdigest(),
                  previous_inventory=str(old_path), previous_inventory_sha256=hashlib.sha256(old_path.read_bytes()).hexdigest(),
                  static_manifest=str(manifest_path), static_manifest_sha256=hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
                  trace=str(trace), trace_sha256=digest.hexdigest(), trace_records=count, route_unique_PCs=len(observed),
                  static_instruction_addresses=len(static), previous_reached_static_addresses=len(previous),
                  added_static_addresses=len(added), combined_reached_static_addresses=len(union),
                  combined_unreached_static_addresses=len(static-union),
                  static_function_entries=len(functions), previous_reached_function_entries=len(set(functions)&previous),
                  added_function_entries=[dict(address=hex(pc), name=functions[pc]) for pc in new_entries],
                  combined_reached_function_entries=len(set(functions)&union), added_addresses=list(map(hex, sorted(added))),
                  whole_game_complete=False, source_semantic_completion_percentage=None,
                  scope='Actual source trace, freshly hashed and bound to the full original comparison, adds reachability to the prior original-route inventory. One main-stage Ghidra snapshot only: not all disc programs, branch/input coverage, recovered readable functions or a whole-game decompilation percentage. Scene/data coverage can improve even when no new instruction address is reached.')
    (ROOT / 'verification/source-route532-coverage-current.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: value for key, value in report.items() if key not in ['added_addresses']}, indent=2), flush=True)


if __name__ == '__main__':
    main()
