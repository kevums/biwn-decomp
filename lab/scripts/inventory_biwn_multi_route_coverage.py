"""Merge checked original trace inventories without calling reachability decomp."""
import hashlib
import json
import re
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    previous=json.loads((ROOT/'verification/main-CPU-route-coverage-current.json').read_text())
    manifest_path=Path(previous['static_manifest']);manifest=json.loads(manifest_path.read_text())
    listing=manifest_path.parent/'listing.asm';assert hashlib.sha256(listing.read_bytes()).hexdigest()==previous['static_listing_sha256']
    static={int(x,16)for x in re.findall(r'^([0-9a-fA-F]{8}):',listing.read_text(),re.M)}
    prior_reached=static-{int(x,16)for x in previous['unreached_static_addresses']}
    reached=set(prior_reached);routes=[]
    for name,expected_frames in [('fresh-merchant-CPU-experimental-candidate.json',22939),
                                  ('zero-warm-startup-CPU-experimental-candidate.json',600),
                                  ('scene17-route-CPU-experimental-candidate.json',15484)]:
        candidate=json.loads((ROOT/'verification'/name).read_text());path=Path(candidate['provenance']);provenance=json.loads(path.read_text())
        folder=Path(provenance['reference']);report=json.loads((folder/'report.json').read_text())
        assert report['mode']=='reference' and not report['errors'] and report['requested_frames']==len(report['frames'])==expected_frames
        assert provenance['frozen_prefix_records']==report['CPU_before_instructions']
        assert (folder/'CPU-before-instructions.bin').stat().st_size==provenance['frozen_prefix_bytes']==provenance['frozen_prefix_records']*78
        assert hashlib.sha256((folder/'warm-RAM.bin').read_bytes()).hexdigest()==provenance['warm_RAM_sha256']
        assert provenance.get('inventory_kind','runtime_trace')=='runtime_trace', 'A static listing does not establish runtime execution coverage'
        pcs=set(provenance['observed_PC']);reached.update(pcs)
        routes.append(dict(reference=str(folder),frames=expected_frames,original_instruction_records=provenance['frozen_prefix_records'],unique_PCs=len(pcs),provenance=str(path),provenance_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),scope='Cached original PC inventory from the complete frozen trace; sizes and original report counts rechecked. No new whole-trace hash or source semantics claim.'))
    functions=[dict(address=f['address'],name=f['name'],original_entry_reached=int(f['address'],16)in reached,
                    high_level_source_verified_by_this_inventory=False)for f in manifest['functions']]
    report=dict(status='multiple_original_routes_address_inventory',recorded_at=datetime.now(timezone.utc).isoformat(),static_manifest=str(manifest_path),static_listing_sha256=previous['static_listing_sha256'],static_instruction_addresses=len(static),static_functions=len(functions),static_addresses_reached_union=len(static&reached),static_addresses_unreached=len(static-reached),function_entries_reached_union=sum(f['original_entry_reached']for f in functions),new_static_addresses_over_previous=len((static&reached)-prior_reached),new_function_entries_over_previous=sum(f['original_entry_reached']and int(f['address'],16)not in prior_reached for f in functions),routes=routes,functions=functions,unreached_static_addresses=[hex(x)for x in sorted(static-reached)],whole_game_complete=False,source_semantic_completion_percentage=None,scope='Original reachability across merchant/startup/scene17 traces plus earlier inventoried traces, limited to one main-stage static listing. This inventory does not prove source semantics, all branches, other disc code, or a decomp percentage.')
    (ROOT/'verification/main-CPU-multi-route-coverage-current.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items()if not isinstance(v,(dict,list))}))
if __name__=='__main__':main()
