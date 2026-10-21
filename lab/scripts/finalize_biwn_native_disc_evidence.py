"""Classify recorded fresh-disc evidence without rerunning emulation."""
from pathlib import Path
import json
from check_biwn_native_button_digit import ROOT,sha,save
pfile=ROOT/'verification/native-disc-cold-boot-current.json';p=json.loads(pfile.read_text());out=Path(p['directory']);bpath=Path(p['build_proof']);b=json.loads(bpath.read_text());epath=Path(p['entry_proof']);e=json.loads(epath.read_text())
assert sha(bpath)==p['build_proof_sha256']and sha(epath)==p['entry_proof_sha256']
assert e['build_proof_sha256']==sha(bpath)
for path,digest in {**b['source_sha256'],**e['source_sha256'],**p['runtime_dependencies_sha256']}.items():assert sha(path)==digest,path
assert sha(b['derived_disc'])==b['derived_disc_sha256']and sha(b['original_disc'])==b['original_disc_sha256']
a=json.loads((out/'reference/report.json').read_text());c=json.loads((out/'candidate/report.json').read_text());assert a['executed_frames']==c['executed_frames']==24000
m=[x['frame']for x,y in zip(a['frames'],c['frames'])if x['video_sha256']!=y['video_sha256']];groups=[]
for f in m:
 if groups and f==groups[-1][1]+1:groups[-1][1]=f
 else:groups.append([f,f])
assert len(m)==125 and min(m)==177 and max(m)==657
assert p['game_state_frames_equal']==24000 and p['all_call_boundaries_equal']and p['native_component_calls']==1 and p['native_component_instructions']==11
assert all(p['final_artifacts_equal'].values())and a['audio']['nonzero_samples']==c['audio']['nonzero_samples']==0
assert p['observations']['candidate']['new_staging_entries']==p['observations']['candidate']['heap_inits']==1
assert p['observations']['candidate']['old_body_steps']==0
analysis=dict(total_frames=24000,video_matched_frames=23875,video_different_frames=len(m),video_difference_ranges=groups,first_difference=177,last_difference=657,all_video_after_frame657_matches=True,strict_whole_run_video_equivalence=False,cause_of_early_video_differences='Not isolated. Changed native startup timing is a hypothesis, not a verified cause.',tracked_game_state_fields_match_all_frames=True,tracked_fields=['raw_player_X','raw_player_Z','scene_word','player_mode_word','tile_word','equipped_word','movie_flag_words','movie_controller_state_word'],full_CPU_or_RAM_equivalence_claimed=False,final_video_match=True,frontend_PCM_match=True,PCM_nonzero_samples=0,audible_output_proved=False)
save(out/'comparison-analysis.json',analysis)
p.update(status='terminal_partial_native_disc_fresh_HLE_boot_verified_with_early_video_differences',coordinator_accepted_scope='Fresh emulator HLE boot, native code loading/reservation and one natural keypad call. Finite tracking; not strict video/CPU/RAM equivalence or full source-built game.',comparison_analysis=analysis,native_entry_cases=e['entry_cases'],resident_component_ABI_cases=e['component_cases'],native_resident_bytes=b['component_bytes'],native_reserved_bytes=b['heap_bytes_reserved'],source_built_whole_game=False,derived_disc=b['derived_disc'],original_disc_modified=False,new_native_Chat=False,new_training=False,coordinator_authorship='New native loader, explicit memory layout, build/observation/check scripts. Existing recovered C reused; earlier guided local-model shim adapted by coordinator.')
paths=[Path(__file__),out/'comparison-analysis.json',out/'reference/report.json',out/'candidate/report.json',out/'reference/native-observation.json',out/'candidate/native-observation.json',out/'call-comparison.json']
p['classification_artifacts_sha256']={str(path):sha(path)for path in paths};save(pfile,p);save(out/'protocol.json',p);save(ROOT/'verification/native-disc-cold-boot-active.json',p)
print(json.dumps({k:p[k]for k in ['status','native_component_calls','native_entry_cases','resident_component_ABI_cases']}))
