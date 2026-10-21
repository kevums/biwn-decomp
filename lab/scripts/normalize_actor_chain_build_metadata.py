"""Supersede inherited standalone-wrapper fields without rewriting as-run proof."""
import json
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save


def main():
    raw=ROOT/'verification/native-actor-chain-disc-build-current.json'
    state=json.loads(raw.read_text())
    assert state['linked_component_bytes']==28448 and state['actor_chain_private_reserve']==320
    out=ROOT/'verification/actor-chain-build-metadata'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    snapshot=out/'build-as-recorded.json';snapshot.write_bytes(raw.read_bytes())
    changes={}
    for name in ['collision_start','collision_end','collision_helper_returns','actor_move_component_gate']:
        if name in state:changes[name]=dict(previous=state.pop(name),action='removed_obsolete_standalone_field')
    for name,value in [('collision_private_reserve',320),('appended_bytes',68),('parent_resident_prefix_byte_identical',False),('source',state['sources'][0])]:
        changes[name]=dict(previous=state.get(name),current=value);state[name]=value
    state['actor_move_range_scope']='actor_move_start/end span the entire shared group, not a movement-only code interval'
    state['calling_convention']='Original-facing public roots; source-owned C ABI for movement-to-collision; remaining physical helper captures'
    state['superseded_build_metadata']=str(snapshot);state['superseded_build_metadata_sha256']=sha(snapshot)
    state['metadata_correction']='Standalone collision interval/helper-return fields from the predecessor do not describe the new shared group. Use actor_chain_* fields and actor_chain_helpers. Original image/startup receipts remain unchanged.'
    state['source_sha256']={**state['source_sha256'],str(Path(__file__)):sha(Path(__file__)),str(snapshot):sha(snapshot)}
    save(out/'changes.json',changes);state['source_sha256'][str(out/'changes.json')]=sha(out/'changes.json')
    save(out/'normalized-build.json',state)
    save(ROOT/'verification/native-actor-chain-build-normalized-current.json',state)
    print(json.dumps(dict(status='terminal_actor_chain_metadata_normalized',image_bytes_changed=False,proof=str(out/'normalized-build.json'))))


if __name__=='__main__':main()
