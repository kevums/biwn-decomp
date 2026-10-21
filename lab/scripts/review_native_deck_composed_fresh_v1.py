"""Re-read the composed native evidence and bind raw artifacts for context."""
from datetime import datetime, timezone
from pathlib import Path
import check_native_deck_fresh_restore_v1 as common
ROOT=common.ROOT; V=ROOT/'verification'; read=common.read; save=common.save; sha=common.sha

def main():
    out=V/'native-Deck-composed-fresh-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    pointer=V/'native-Deck-composed-fresh-current.json';proof=read(pointer)
    assert proof['status']=='terminal_restored_fresh_native_coordinate_and_GPU_family_controlled_roundtrip_match'
    for path,digest in proof['source_sha256'].items():assert sha(path)==digest,path
    restore=read(proof['restore_proof']);assert sha(proof['restore_proof'])==proof['restore_proof_sha256']
    for key in ['core','disc','state','RAM','build']:assert sha(restore[key+'_path'])==restore[key+'_sha256']
    directory=Path(proof['proof_directory']);report_path=directory/'report.json';report=read(report_path)
    assert report['status']==proof['status']and len(report['phases'])==proof['paired_checkpoints']==46
    bound=[pointer,Path(proof['directory'])/'protocol.json',Path(proof['runner']),Path(proof['directory'])/'pipeline.log',Path(proof['restore_proof']),report_path]
    for name,pair in report['phases'].items():
        assert pair['native']==pair['C'],name
        for lane in ['native','C']:
            path=directory/(lane+'-'+name+'.json');assert read(path)==pair[lane];bound.append(path)
    left=directory/'native-final-RAM.bin';right=directory/'C-final-RAM.bin'
    assert len(left.read_bytes())==2097152 and left.read_bytes()==right.read_bytes();bound.extend([left,right])
    a,b=report['results'];assert a['CPU']==b['CPU']and a['RAM']==b['RAM']==sha(left)
    assert a['events']==b['events']and len(a['events'])==149
    assert a['native_coordinate_entries']==a['native_coordinate_returns']==0 and a['coordinate_original_steps']>0
    assert b['native_coordinate_entries']==b['native_coordinate_returns']==b['nested_coordinate_GPU4720_entries']==17 and b['coordinate_original_steps']==0
    assert all(r['native_GPU4720_entries']==r['native_GPU4720_returns']==113 and r['GPU4720_original_steps']==0 for r in [a,b])
    assert a['original_GPU_opcodes']==b['original_GPU_opcodes']>0
    assert a['restored_active_cache_slots']==b['restored_active_cache_slots']==list(range(15,33))
    assert b['native_helper_yields']==0
    drain=[directory/(lane+'-restored-GPU-drain.json')for lane in ['native','C']]
    assert read(drain[0])==read(drain[1])and read(drain[0])['instructions_requested']==100312
    bound.extend(drain);bound.extend(Path(p)for p in proof['source_sha256'])
    bound.append(Path(__file__))
    state=dict(status='terminal_composed_native_Deck_raw_artifacts_reviewed',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),raw_proof=str(pointer),raw_proof_sha256=sha(pointer),raw_report=str(report_path),raw_report_sha256=sha(report_path),native_coordinate_calls=17,nested_coordinate_GPU4720_calls=17,native_GPU4720_calls_per_lane=113,GPU_commands_per_lane=149,paired_checkpoints=46,active_cache_slots_restored=18,active_helper_yields=0,initial_pending_GPU_instructions=100312,source_sha256={str(p):sha(p)for p in set(bound)},natural_Deck_activation=False,whole_game_complete=False,native_disc_changed=False,new_training=False,scope=report['scope'],test_harness_corrections=['Follow actual scheduler JSR return address; compiled loader does not resume at original1B0DA.','Execute restored pending GPU work to idle instead of assuming old fixture idle state; no GPU register/mailbox seed.','Require restored original display mode from fresh baseline, rather than merchant-only literal2.','Allow bounded extra instructions for compiled native routines; keep all CPU/RAM/hardware/command/guard comparisons.'])
    save(out/'report.json',state);save(V/'native-Deck-composed-fresh-reviewed-current.json',state);print(state['status'],len(state['source_sha256']))

if __name__=='__main__':main()
