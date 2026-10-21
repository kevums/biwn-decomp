"""Freeze prefix isolation and real-call evidence without asserting live equivalence."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def main():
 cp=ROOT/'verification/native-free-timing-controls-current.json';control=json.loads(cp.read_text());assert control['status']=='terminal_selective_restore_controls_pending_analysis';cd=Path(control['directory']);fp=ROOT/'verification/native-free-fixed-route-current.json';fixed=json.loads(fp.read_text());fd=Path(fixed['directory']);rp=ROOT/'verification/native-free-captured-calls-current.json';replay=json.loads(rp.read_text());assert replay['status']=='terminal_two_live_captured_free_calls_match_isolated_native_returns'and replay['control_proof_sha256']==sha(cp)
 fields=['raw_player_X','raw_player_Z','scene_word','player_mode_word','floor_word','tile_word','equipped_word','movie_flag_words','movie_controller_state_word','cumulative_nonzero_audio_samples','video_sha256','GPU','DSP','GPU_R31_banks','raw_word_49c5c']
 references={lane:json.loads((fd/lane/'report.json').read_text())['frames'][:6400]for lane in ['native23_fixed','native25_fixed']};results={};artifact_paths=[]
 for name,variant in control['variants'].items():
  assert variant['all_other_disc_bytes_identical']and sha(variant['disc'])==variant['sha256'];directory=cd/name;data=json.loads((directory/'report.json').read_text());rows=data['frames'];assert data['executed_frames']==len(rows)==6400
  obs=json.loads((directory/'gameplay-observation.json').read_text());assert not(obs['errors']or obs['copy_errors']or obs['repair_code_errors']);comparisons={}
  for lane,reference in references.items():
   assert all(a['input_pressed_mask']==b['input_pressed_mask']and a['input_seen_mask']==b['input_seen_mask']for a,b in zip(rows,reference))
   comparisons[lane]={field:sum(a[field]!=b[field]for a,b in zip(rows,reference))for field in fields}
  results[name]=dict(source_free=variant['source_free'],source_initializer=variant['source_initializer'],per_frame_differences=comparisons,free_public_entries=obs['free_entries'],old_free_body_instructions=obs['old_free_body_steps'],compiled_free_C_calls=obs['native_C_free_calls'],old_initializer_body_instructions=obs['old_initialize_body_steps'],source_initializer_calls=obs['native_initialize_calls'],actual_pad_callbacks_equal_both_references=True)
  for filename in ['report.json','gameplay-observation.json','gameplay-events.bin','RAM-final.bin','frontend-PCM.s16le']:artifact_paths.append(directory/filename)
  artifact_paths.append(Path(variant['disc']))
 assert all(v==0 for name in ['layout_only','initializer_only']for v in results[name]['per_frame_differences']['native23_fixed'].values())
 assert all(v==0 for v in results['free_only']['per_frame_differences']['native25_fixed'].values())
 events=Path(replay['directory'])/'fresh/gameplay-events.bin';import struct
 records=list(struct.iter_unpack('<28I',events.read_bytes()));free_frames=[row[0]for row in records if row[1]==0x1545c];assert free_frames==[5554,5554]
 report=dict(status='terminal_native25_free_change_isolates_first_prefix_divergence',recorded_at=datetime.now(timezone.utc).isoformat(),frames_per_control=6400,control_results=results,first_two_original_free_call_frames=free_frames,first_GPU_difference_frame=5554,captured_native_returns=replay['results'],captured_call_scope=replay['scope'],interpretation='Within these6400frame controls, new layout and source initializer retain the prior selected game/video/GPU/DSP rows when original free is restored. Source free alone reproduces native25selected rows. First two free calls occur at firstGPUdifference frame5554. Both captured inputs return identical native fullCPU/publicRAM in IRQ-disabled isolation and fit their current task stack, but cost404→1856and596→1964emulatedcycles. Timing/interleaving is the leading explanation, not proven live causation; no full29783frame selective-restore equivalence or arbitrary input/IRQ/physical conclusion.',strict_fixed_input_equivalence_still_failed=True,source_sha256={str(Path(__file__)):sha(__file__)})
 out=ROOT/'verification/native-free-prefix-isolation'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);save(out/'analysis.json',report)
 deps={};snapshots={}
 def pin(p,snapshot=False):
  p=Path(p).resolve();assert p.is_relative_to(ROOT);relative=str(p.relative_to(ROOT));digest=sha(p)
  if snapshot:
   dest=out/(hashlib.sha256(relative.encode()).hexdigest()[:12]+'-'+p.name);shutil.copy2(p,dest);deps[str(dest.relative_to(ROOT))]=digest;snapshots[relative]=str(dest.relative_to(ROOT))
  else:deps[relative]=digest
 for p in [cp,fp,rp,Path(__file__)]:pin(p,True)
 for obj in [control,replay]:
  for field in ['source_sha256','execution_dependencies_sha256']:
   for p,d in obj.get(field,{}).items():assert sha(p)==d;pin(p,True)
 for p in artifact_paths:pin(p)
 for p in Path(replay['directory']).rglob('*.bin'):pin(p)
 for name in ['report.json','gameplay-observation.json','frontend-PCM.s16le']:pin(Path(replay['directory'])/'fresh'/name)
 pin(Path(replay['directory'])/'isolated-results.json');pin(out/'analysis.json')
 parent=ROOT/'verification/native-free-fixed-followup-current.json';manifest=dict(status='published_native25_free_prefix_isolation',recorded_at=report['recorded_at'],directory=str(out),parent_fixed_followup_sha256=sha(parent),analysis=report,dependencies_sha256=deps,source_snapshots=snapshots,whole_game_complete=False)
 save(out/'publication.json',manifest);save(ROOT/'verification/native-free-prefix-isolation-current.json',manifest);print(json.dumps({'status':report['status'],'directory':str(out),'dependencies':len(deps),'cycle_pairs':[(x['original_cycles'],x['compiled_cycles'])for x in replay['results']]}),flush=True)
if __name__=='__main__':main()
