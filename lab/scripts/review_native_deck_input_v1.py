"""Review new input/coordinate disc, exact fixtures and matched-layout control."""
from datetime import datetime,timezone
import json
from pathlib import Path
import shutil
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def main():
 out=V/'native-Deck-input-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 bp=V/'native-Deck-input-disc-build-current.json';b=read(bp);bound=[Path(__file__),bp];assert sha(b['derived_disc'])==b['derived_disc_sha256']
 assert sha(b['derived_stage'])==b['derived_stage_sha256'];component=Path(b['component']).read_bytes();assert sha(b['component'])==b['component_sha256']
 for name,wanted in [('native-deck-input-v1-current.json',2048),('native-deck-input-nesting-v1-current.json',128),('native-Deck-input-final-input-current.json',2048),('native-Deck-input-final-coordinate-current.json',576),('native-input-fallback-ABI-v1-current.json',384)]:
  p=V/name;x=read(p);assert x['completed' if 'completed'in x else 'cases']==wanted
  for path,h in x['source_sha256'].items():assert sha(path)==h,path;bound.append(Path(path))
  bound.extend([p,Path(x['directory'])/'cases.json'])
  if 'deployed_module_byte_identity'in x:assert x['deployed_module_byte_identity']
 for name in ['native-Deck-input-startup-heap-current.json','native-Deck-input-capacity-current.json','native-Deck-input-region-check-current.json']:
  p=V/name;x=read(p)
  for path,h in x['source_sha256'].items():assert sha(path)==h,path;bound.append(Path(path))
  bound.append(p)
 assert read(V/'native-Deck-input-startup-heap-current.json')['heap_initialize_cases']==192
 assert read(V/'native-Deck-input-capacity-current.json')['cases']==36
 assert len(read(V/'native-Deck-input-region-check-current.json')['negative_controls'])==18
 reports={};jobs={};observations={};inputs={};used={}
 for lane in ['candidate','control']:
  p=V/('native-Deck-input-'+lane+'-current.json');job=read(p);assert job['status']=='terminal_fresh_input_route_pending_review';jobs[lane]=job
  assert sha(job['build'])==job['build_sha256']
  for path,h in job['source_sha256'].items():assert sha(path)==h,path;bound.append(Path(path))
  report_path=Path(job['report']);r=read(report_path);reports[lane]=r;folder=report_path.parent;o=read(folder/'gameplay-observation.json');i=read(folder/'input-observation.json');observations[lane]=o;inputs[lane]=i
  assert not r['captured_state_input']and not r['host_CPU_or_GPU_register_seed'];assert len(r['frames'])==25010 and r['ordinary_Deck_input_trial']['start_frame']==24610
  assert len(r['ordinary_Deck_input_trial']['inputs'])==400
  errors={k:v for k,v in o.items()if isinstance(v,(int,float))and any(s in k for s in ['error','pending','outside','corruption','collision'])};assert errors and not any(errors.values()),errors
  assert o['mb_entries']==o['mb_native']==o['mb_returns'] and min(o['mb_entries'])>0
  assert o['deck_entries']==o['deck_native_entries']==o['deck_native_returns']
  assert o['deck_source_steps']==o['deck_invalid_entries']==0
  assert not any(i[k]for k in ['errors','pending','C_stack_outside','fallback_entries'])
  final=r['frames'][-1];assert final['scene_word']==312 and final['player_mode_word']==1 and final['movie_flag_words']==[0,0]
  raw=folder/'RAM-final.bin';ram=raw.read_bytes();base=b['resident_address']
  for lo,hi in [(base,b['arena_address']),(b['arena_end'],b['deck_arena_address'])]:assert ram[lo:hi]==component[lo-base:hi-base]
  used[lane]=[]
  for slot in range(101):
   at=b['deck_arena_address']+slot*1024
   for lo in [0,128,256,704,1008]:assert ram[at+lo:at+lo+16]==component[at-base+lo:at-base+lo+16]
   assert ram[at+244:at+248]==bytes(4)
   if ram[at:at+1024]!=component[at-base:at-base+1024]:used[lane].append(slot)
  for slot in range(102):
   at=b['arena_address']+slot*256
   for lo in [0,240]:assert ram[at+lo:at+lo+16]==component[at-base+lo:at-base+lo+16]
  bound.extend([p,report_path,folder/'gameplay-observation.json',folder/'input-observation.json',raw,folder/'state-final.bin',folder/'original-emulator-final-frame.png'])
 cand=inputs['candidate'];control=inputs['control'];assert cand['public_entries']==cand['native_entries']==cand['native_returns']==128
 assert cand['original_body_steps']==0 and cand['helper_entries']==cand['helper_returns']==130
 assert control['public_entries']==140 and control['native_entries']==control['native_returns']==0 and control['original_body_steps']>0
 assert observations['candidate']['deck_native_returns']==128 and observations['control']['deck_native_returns']==140
 ignored={'full_RAM_sha256','stage_sha256'}
 for left,right in zip(reports['candidate']['frames'][:24610],reports['control']['frames'][:24610]):assert {k:v for k,v in left.items()if k not in ignored}=={k:v for k,v in right.items()if k not in ignored},left['frame']
 assert reports['candidate']['frames'][-1]['video_sha256']==reports['control']['frames'][-1]['video_sha256']
 # Independently check that the same-layout control changes only public input.
 session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);mapping=session/'nextstage-mapping.json';offset=read(mapping)['payload_raw_cdi_offset']+0x11b4c-0x4000
 control_disc=Path(jobs['control']['command'][jobs['control']['command'].index('--disc')+1]);changed=0;pos=0
 with Path(b['derived_disc']).open('rb')as a,control_disc.open('rb')as c:
  while True:
   left,right=a.read(1048576),c.read(1048576);assert len(left)==len(right)
   if not left:break
   for j,(x,y)in enumerate(zip(left,right)):
    if x!=y:assert offset<=pos+j<offset+6;changed+=1
   pos+=len(left)
 assert 0<changed<=6
 for path,h in b['source_sha256'].items():assert sha(path)==h,path;bound.append(Path(path))
 bound.extend([Path(b['derived_stage']),Path(b['component']),mapping,control_disc])
 proof=dict(status='terminal_fresh_native_input_and_coordinate_disc_reviewed',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),build=str(bp),build_sha256=sha(bp),disc=b['derived_disc'],disc_sha256=b['derived_disc_sha256'],native_code_bytes=b['linked_component_bytes'],input_module_bytes=b['input_code_bytes'],coordinate_module_bytes=b['deck_code_bytes'],coordinator_bootstrap_bytes=b['deck_finalizer_bytes'],installed_recovered_Deck_entries=['11b4c','11d1a'],remaining_hosted_only_Deck_entries=['11828','11ad4','11e6c','1186a'],frames=25010,ordinary_trial_frames=400,ordinary_input_calls=128,ordinary_input_returns=128,ordinary_coordinate_calls=128,ordinary_coordinate_returns=128,ordinary_input_helpers=130,ordinary_input_helper_returns=130,native_GPU_roots=8,native_GPU_returns=observations['candidate']['mb_returns'],original_input_body_steps=0,input_fallbacks=0,all_observed_monitor_errors_pending_outside_zero=True,all101_Deck_outer_and3internal_fences_pass=True,all102_GPU_fences_pass=True,Deck_used_slots=used,immutable_code_unchanged=True,pre_input_recorded_fields_equal_frames=24610,pre_input_RAM_and_stage_hashes_excluded_for_static_redirect=True,same_layout_control_original_input_calls=140,same_layout_control_native_coordinate_calls=140,control_declared_redirect_bytes=6,control_changed_disc_bytes=changed,final_video_equal=True,timing_cycle_identity_verified=False,performance_limit='Native input and coordinate calls are128 versus140 in the400frame control trial. Entry count and rendered-time behavior are not cycle-identical; no timing/physical equivalence claim.',component_input_cases=2048,final_address_input_cases=2048,final_address_coordinate_cases=576,controlled_nested_cases=128,fallback_ABI_cases=384,MOVEM_flag_counterexamples=360,startup_cases=6,heap_initialize_cases=192,capacity_cases=36,initial_heap_bytes=0x1c0000-b['heap_start'],native_region_fault_controls=18,selector13_restoration_retained=True,restoration_changes_original_behavior=True,original_disc_matching_trial_verified=False,new_gameplay_code_authorship='Coordinator qualified input source and native ABI. Local model ABI analysis was rejected; no generated code adopted.',native_keyboard_default_updated=False,new_training=False,whole_game_complete=False,physical_console_verified=False,scope='Fresh ordinary HLE/emulator boot of a separate repaired native disc and a six-byte same-layout original-input control. No snapshot restore, CPU/task/GPU seed, or host guest-RAM repair. Input and coordinate source compiled to real68000; retained original helpers, emulator/devices and other existing native modules remain dependencies. One-level nesting witnesses use declared helper JSR fixtures; arbitrary reentrancy/suspension/IRQ, cycle/audio/physical fidelity and full same-console source rebuild remain incomplete.',source_sha256={str(p):sha(p)for p in set(bound)})
 save(out/'review.json',proof);save(V/'native-Deck-input-reviewed-current.json',proof)
 for name in ['candidate','control']:shutil.copy2(V/('native-Deck-input-'+name+'-current.json'),out/(name+'-protocol.json'))
 print(proof['status'],128,proof['initial_heap_bytes'],flush=True)

if __name__=='__main__':main()
