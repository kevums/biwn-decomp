"""Map full original-route addresses onto one static main-stage listing.

Original execution reachability, compiled coverage, and original/C validation
are separate claims. This inventory is not a game completion percentage.
"""
import hashlib
import json
import re
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]


def main():
    previous = json.loads((ROOT/'verification/main_CPU_execution_coverage-current.json').read_text())
    previous_detail = json.loads((Path(previous['directory'])/'report.json').read_text())
    candidate = json.loads((ROOT/'verification/fresh-merchant-CPU-experimental-candidate.json').read_text())
    provenance_path = Path(candidate['provenance'])
    provenance = json.loads(provenance_path.read_text())
    reference = Path(provenance['reference'])
    original = json.loads((reference/'report.json').read_text())
    trace = reference/'CPU-before-instructions.bin'
    assert not original['errors'] and original['mode'] == 'reference'
    assert len(original['frames']) == original['requested_frames'] == 22939
    assert trace.stat().st_size == provenance['frozen_prefix_bytes'] == provenance['frozen_prefix_records']*78
    assert provenance['frozen_prefix_records'] == original['CPU_before_instructions']
    assert hashlib.sha256((reference/'warm-RAM.bin').read_bytes()).hexdigest() == provenance['warm_RAM_sha256']
    manifest_path = Path(previous['static_manifest'])
    assert hashlib.sha256(manifest_path.read_bytes()).hexdigest() == previous['static_manifest_sha256']
    manifest = json.loads(manifest_path.read_text())
    listing = manifest_path.parent/'listing.asm'
    static = {int(match[1], 16) for match in re.finditer(r'^([0-9a-fA-F]{8}):', listing.read_text(), re.M)}
    assert provenance.get('inventory_kind','runtime_trace')=='runtime_trace', 'A static listing does not establish runtime execution coverage'
    reached = set(provenance['observed_PC'])
    earlier = {int(pc, 16) for pc in previous_detail['matched_static_PC_addresses']}
    compiled = {int(pc, 16) for pc in candidate['selected_case_sources']}
    functions = []
    for function in manifest['functions']:
        pc = int(function['address'], 16)
        functions.append(dict(function, original_route_entry_reached=pc in reached,
                              earlier_accepted_entry_reached=pc in earlier,
                              compiled_entry_case=pc in compiled,
                              high_level_source_recovery_verified=False))
    result = dict(status='full_original_route_address_inventory',
                  recorded_at=datetime.now(timezone.utc).isoformat(),
                  static_manifest=str(manifest_path), static_listing_sha256=hashlib.sha256(listing.read_bytes()).hexdigest(),
                  original_reference=str(reference), original_frames_after599=22939,
                  original_CPU_trace_records=provenance['frozen_prefix_records'],
                  address_inventory_source=str(provenance_path),
                  address_inventory_sha256=hashlib.sha256(provenance_path.read_bytes()).hexdigest(),
                  unique_original_route_PCs=len(reached), static_instruction_addresses=len(static),
                  static_addresses_reached_by_original_route=len(static & reached),
                  static_addresses_reached_union_earlier_and_route=len(static & (earlier | reached)),
                  static_addresses_unreached_by_union=len(static-(earlier | reached)),
                  original_route_function_entries_reached=sum(f['original_route_entry_reached'] for f in functions),
                  function_entries_reached_union=sum(f['original_route_entry_reached'] or f['earlier_accepted_entry_reached'] for f in functions),
                  static_functions=len(functions), compiled_instruction_cases=len(compiled),
                  original_route_addresses_without_compiled_case=[hex(pc) for pc in sorted(reached-compiled)],
                  functions=functions, unreached_static_addresses=[hex(pc) for pc in sorted(static-(earlier | reached))],
                  whole_game_complete=False, full_fresh_C_comparison_verdict='pending',
                  limits=['One main-stage static snapshot and one recorded original input route; other disc code and assets excluded.',
                          'Reaching an entry does not verify all branches or recover original high-level source.',
                          'Compiled source cases remain subject to runtime byte fences and original/C comparisons.',
                          'Cached address inventory was produced from the complete frozen original trace by the route builder; counts and warm-RAM hash rechecked here.',
                          'No overall decomp completion percentage can be derived.'])
    path = ROOT/'verification/main-CPU-route-coverage-current.json'
    path.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({key:value for key,value in result.items() if isinstance(value,(str,int,bool))}))


if __name__ == '__main__':
    main()
