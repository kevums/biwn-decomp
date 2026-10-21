"""Classify four-entry native bundle evidence; retain all differences."""
from pathlib import Path
import json
from check_biwn_native_button_digit import ROOT,sha,save
pfile=ROOT/'verification/native-bundle-disc-cold-boot-current.json';p=json.loads(pfile.read_text());out=Path(p['directory']);build=json.loads(Path(p['build_proof']).read_text());entry=json.loads(Path(p['entry_proof']).read_text());math=json.loads(Path(p['arithmetic_bundle_proof']).read_text())
assert sha(p['build_proof'])==p['build_proof_sha256']and sha(p['entry_proof'])==p['entry_proof_sha256']and sha(p['arithmetic_bundle_proof'])==p['arithmetic_bundle_proof_sha256']
for path,digest in {**build['source_sha256'],**entry['source_sha256'],**math['source_sha256'],**math['execution_dependencies_sha256'],**p['runtime_dependencies_sha256']}.items():assert sha(path)==digest,path
assert sha(build['derived_disc'])==build['derived_disc_sha256']
a=json.loads((out/'reference/report.json').read_text());b=json.loads((out/'candidate/report.json').read_text());fields=['raw_player_X','raw_player_Z','scene_word','player_mode_word','tile_word','equipped_word','movie_flag_words','movie_controller_state_word'];video=[];tracked=[]
for x,y in zip(a['frames'],b['frames']):
 if x['video_sha256']!=y['video_sha256']:video.append(x['frame'])
 if any(x[k]!=y[k]for k in fields):tracked.append(x['frame'])
def ranges(values):
 out=[]
 for v in values:
  if out and v==out[-1][1]+1:out[-1][1]=v
  else:out.append([v,v])
 return out
obs=p['observations']['candidate'];assert len(video)==178 and len(tracked)==19 and p['frames_per_lane']==24000
assert obs['arithmetic_original_steps']==0 and obs['arithmetic_entries']==[78694,59060,260]and p['all_call_boundaries_equal']
assert all(p['final_artifacts_equal'].values())and b['audio']['nonzero_samples']==0
analysis=dict(frames=24000,video_different_frames=len(video),video_difference_ranges=ranges(video),tracked_state_different_frames=len(tracked),tracked_state_difference_ranges=ranges(tracked),tracked_fields=fields,field_difference_counts={k:sum(x[k]!=y[k]for x,y in zip(a['frames'],b['frames']))for k in fields},strict_equivalence=False,final_video_equal=True,PCM_equal_but_silent=True,cause='Not fully isolated. Earlier two1000frame ablations locate previous125differences in startup/copy path, not heap-only changes. Current bundle additionally changes arithmetic execution and clears4096staging bytes; do not attribute all178differences to one cause.',actual_native_arithmetic_entry_events=sum(obs['arithmetic_entries']),arithmetic_events_by_entry={'E540_multiply':obs['arithmetic_entries'][0],'E588_division':obs['arithmetic_entries'][1],'E60A_remainder':obs['arithmetic_entries'][2]},original_arithmetic_body_instructions_on_candidate=0,counts_note='These are entries at three patched original addresses. Reference nested remainder-to-division calls and native C internal calls differ; totals are not direct original/native call-count equivalence.',resident_instructions_including_startup_and_all_components=obs['resident_steps'],natural_keypad_calls=p['native_component_calls'],keypad_boundary_equal=p['all_call_boundaries_equal'])
save(out/'comparison-analysis.json',analysis)
p.update(status='terminal_four_entry_native_disc_fresh_HLE_boot_with_video_and_state_differences',comparison_analysis=analysis,native_rebuilt_entries=4,native_resident_bytes=build['component_bytes'],native_reserved_bytes=build['heap_bytes_reserved'],native_entry_cases=entry['entry_cases'],relocated_keypad_cases=math['relocated_keypad_cases'],normal_arithmetic_cases=math['normal_cases'],zero_exception_cases=math['zero_exception_cases'],staging_bytes_cleared=4096,derived_disc=build['derived_disc'],source_built_whole_game=False,physical_console_verified=False,coordinator_authorship='Coordinator wrote native arithmetic ABI/CCR/zero-exception glue, staging finalizer, build and checks; recovered multiplication/division C reused. No new model-authored C or weights.',preview_promoted=False,new_training=False,new_native_Chat=False)
paths=[Path(__file__),out/'comparison-analysis.json',out/'reference/report.json',out/'candidate/report.json',out/'reference/native-observation.json',out/'candidate/native-observation.json',ROOT/'verification/native-math-reference-original-disc-current.json',ROOT/'verification/m68000-libgcc-current.json',ROOT/'verification/native-startup-video-isolation-current.json']
p['classification_artifacts_sha256']={str(path):sha(path)for path in paths};save(pfile,p);save(out/'protocol.json',p);save(ROOT/'verification/native-bundle-disc-cold-boot-active.json',p)
print(json.dumps({k:p[k]for k in ['status','native_rebuilt_entries','normal_arithmetic_cases','zero_exception_cases']}));print(json.dumps(analysis))
