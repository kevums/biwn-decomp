"""Measure accepted natural coordinate source traces against prior address inventory.

Reachability in one main-stage listing is not readable-source completion,
branch/input coverage, all-disc coverage or hardware accuracy.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    previous_path = ROOT / 'verification/source-route532-coverage-current.json'
    previous = json.loads(previous_path.read_text())
    old_path = Path(previous['previous_inventory'])
    assert sha(old_path) == previous['previous_inventory_sha256']
    old = json.loads(old_path.read_text())
    manifest_path = Path(previous['static_manifest'])
    assert sha(manifest_path) == previous['static_manifest_sha256']
    listing = manifest_path.parent / 'listing.asm'
    assert sha(listing) == old['static_listing_sha256']
    addresses = {int(x, 16) for x in re.findall(r'^([0-9a-fA-F]{8}):', listing.read_text(), re.M)}
    assert len(addresses) == old['static_instruction_addresses'] == 18306
    reached = addresses - {int(x, 16) for x in old['unreached_static_addresses']}
    reached |= {int(x, 16) for x in previous['added_addresses']}
    assert len(reached) == previous['combined_reached_static_addresses'] == 6579
    manifest = json.loads(manifest_path.read_text())
    functions = {int(x['address'], 16) for x in manifest['functions']}
    assert len(functions) == 206
    import capstone
    atlas = ROOT / 'verification/zero-warm-startup-instruction-atlas.bin'
    decoder = capstone.Cs(capstone.CS_ARCH_M68K, capstone.CS_MODE_BIG_ENDIAN | capstone.CS_MODE_M68K_000)
    coordinate = {x.address for x in decoder.disasm(atlas.read_bytes()[0x18e92:0x190b8], 0x18e92)}
    assert len(coordinate) == 166
    union, coordinate_union, rows = set(), set(), []
    dtype = np.dtype({'names': ['pc'], 'formats': ['>u4'], 'offsets': [64], 'itemsize': 78})
    for case in ['cancel', 'confirm', 'edit']:
        path = ROOT / ('verification/natural-coordinate-' + case + '-current.json')
        proof = json.loads(path.read_text())
        assert proof['status'] == 'natural_coordinate_' + case + '_source_runtime_match'
        comparison = json.loads(Path(proof['comparison']).read_text())
        trace = Path(proof['directory']) / 'C/CPU-before-instructions.bin'
        digest = sha(trace)
        assert comparison['sha256']['CPU-before-instructions.bin'] == [digest, digest]
        assert trace.stat().st_size == proof['CPU_instructions'] * 78
        records = np.memmap(trace, mode='r', dtype=dtype)
        pcs = set(map(int, np.unique(records['pc'])))
        union |= pcs & addresses
        coordinate_union |= pcs & coordinate
        rows.append(dict(case=case, proof=str(path), proof_sha256=sha(path), trace=str(trace),
            trace_sha256=digest, trace_records=len(records), unique_PCs=len(pcs),
            coordinate_instruction_locations_reached=len(pcs & coordinate),
            added_static_addresses_over_previous=len((pcs & addresses) - reached)))
        print(case, 'coordinate locations', len(pcs & coordinate), flush=True)
    added = union - reached
    combined = reached | union
    out = ROOT / 'verification/natural-coordinate-coverage' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    report = dict(status='natural_coordinate_source_address_inventory_measured', recorded_at=datetime.now(timezone.utc).isoformat(),
        directory=str(out), previous_inventory=str(previous_path), previous_inventory_sha256=sha(previous_path),
        static_manifest=str(manifest_path), static_manifest_sha256=sha(manifest_path), static_listing_sha256=sha(listing),
        runs=rows, static_instruction_addresses=18306, previous_reached_static_addresses=len(reached),
        added_static_addresses=len(added), combined_reached_static_addresses=len(combined),
        combined_unreached_static_addresses=len(addresses - combined), static_function_entries=206,
        previous_reached_function_entries=len(reached & functions), added_function_entries=list(map(hex, sorted((combined - reached) & functions))),
        combined_reached_function_entries=len(combined & functions), coordinate_original_instruction_locations=166,
        natural_coordinate_instruction_locations_reached=len(coordinate_union),
        natural_coordinate_unreached_instruction_locations=list(map(hex, sorted(coordinate - coordinate_union))),
        added_addresses=list(map(hex, sorted(added))), inherited_repair_bytes=18, new_game_byte_repair=False,
        high_level_coordinate_API_in_live_frames=False, source_semantic_completion_percentage=None,
        whole_game_complete=False, scope=__doc__ + ' Each source trace is freshly hashed against its complete original comparison. Three ordinary-input continuations inherit18bytes from the earlier verified source outdoor checkpoint; they add no patch. Address hits do not by themselves establish original instruction semantics at repaired locations. Coordinate entry itself is unmodified. The independent readable166location caller proof remains distinct from the live instruction-compatible frame runtime.')
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    (ROOT / 'verification/natural-coordinate-coverage-current.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], 'added static', len(added), 'coordinate', len(coordinate_union), flush=True)


if __name__ == '__main__':
    main()
