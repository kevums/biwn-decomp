"""Review final-address components and fresh same-layout scan control."""
from datetime import datetime,timezone
import json
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
import check_native_deck_shared_v2 as kernel
V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def main():
 out=V/'native-Deck-shared-review-v2'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 bp=V/'native-Deck-shared-disc-build-v2-current.json';build=read(bp);bound=[Path(__file__),bp,Path(kernel.__file__)];assert sha(build['derived_disc'])==build['derived_disc_sha256'];assert sha(build['derived_stage'])==build['derived_stage_sha256'];assert sha(build['component'])==build['component_sha256'];component=Path(build['component']).read_bytes()
 for name,count in [('native-deck-shared-v2-current.json',2880),('native-deck-shared-connected-v2-current.json',128),('native-deck-shared-final-v2-current.json',2880),('native-deck-shared-connected-final-v2-current.json',128),('shared-Deck-fallback-ABI-v2-current.json',768)]:
  path=V/name;proof=read(path);assert proof['completed']==count
  for p,h in proof['source_sha256'].items():assert sha(p)==h,p;bound.append(Path(p))
  bound.extend([path,Path(proof['directory'])/'cases.json'])
  if name=='native-deck-shared-final-v2-current.json':assert proof['deployed_module_byte_identity']
 for name in ['native-Deck-shared-startup-heap-v2-current.json','native-Deck-shared-capacity-v2-current.json','shared-Deck-region-check-v2-current.json']:
  path=V/name;proof=read(path)
  for p,h in proof['source_sha256'].items():assert sha(p)==h,p;bound.append(Path(p))
  bound.append(path)
 assert read(V/'native-Deck-shared-startup-heap-v2-current.json')['startup_cases']==6
 assert read(V/'native-Deck-shared-startup-heap-v2-current.json')['heap_initialize_cases']==192
 assert read(V/'native-Deck-shared-capacity-v2-current.json')['cases']==36
 assert len(read(V/'shared-Deck-region-check-v2-current.json')['negative_controls'])==56
 reports={};jobs={};observed={};shared={};used={}
 for lane in ['candidate','control']:
  path=V/('native-Deck-shared-v2-'+lane+'-current.json');job=read(path);assert job['status']=='terminal_fresh_shared_route_pending_review';jobs[lane]=job;assert sha(job['build'])==job['build_sha256']
  for p,h in job['source_sha256'].items():assert sha(p)==h,p;bound.append(Path(p))
  folder=Path(job['report']).parent;report=read(job['report']);reports[lane]=report;observed[lane]=o=read(folder/'gameplay-observation.json');shared[lane]=s=read(folder/'shared-observation.json')
  assert not report['captured_state_input']and not report['host_CPU_or_GPU_register_seed'];assert len(report['ordinary_Deck_input_trial']['inputs'])==400 and report['ordinary_Deck_input_trial']['start_frame']>20000 and len(report['frames'])==report['ordinary_Deck_input_trial']['start_frame']+400
  errors={k:v for k,v in o.items()if isinstance(v,(int,float))and any(word in k for word in ['error','pending','outside','corruption','collision'])};assert errors and not any(errors.values()),errors
  assert not any(s[k]for k in ['errors','pending','C_stack_outside']);assert s['native_entries']==s['native_returns'] and s['helper_entries']==s['helper_returns'];assert s['fallback_entries']==[0,0,0]
  assert o['mb_entries']==o['mb_native']==o['mb_returns']and min(o['mb_returns'])>0;assert o['deck_entries']==o['deck_native_entries']==o['deck_native_returns']>0;assert o['deck_source_steps']==o['deck_invalid_entries']==0
  final=report['frames'][-1];assert final['scene_word']==312 and final['player_mode_word']==1 and final['movie_flag_words']==[0,0]
  ram_path=folder/'RAM-final.bin';ram=ram_path.read_bytes();base=build['resident_address']
  for lo,hi in [(base,build['arena_address']),(build['arena_end'],build['deck_arena_address'])]:assert ram[lo:hi]==component[lo-base:hi-base]
  used[lane]=[]
  for slot in range(101):
   at=build['deck_arena_address']+slot*1024
   for lo,hi in kernel.FENCES:assert ram[at+lo:at+hi]==component[at-base+lo:at-base+hi]
   for _,offset,_,_ in kernel.LAYOUT.values():assert ram[at+offset+114:at+offset+118]==bytes(4)
   if ram[at:at+1024]!=component[at-base:at-base+1024]:used[lane].append(slot)
  for slot in range(102):
   at=build['arena_address']+slot*256
   for lo in [0,240]:assert ram[at+lo:at+lo+16]==component[at-base+lo:at-base+lo+16]
  bound.extend([path,Path(job['report']),folder/'gameplay-observation.json',folder/'shared-observation.json',ram_path,folder/'state-final.bin',folder/'original-emulator-final-frame.png'])
 candidate=shared['candidate'];control=shared['control'];assert candidate['public_entries']==candidate['native_entries']==candidate['native_returns'];assert min(candidate['native_returns'])>0 and candidate['original_body_steps']==[0,0,0]
 assert control['native_returns'][2]==0 and control['original_body_steps'][2]>0
 start=reports['candidate']['ordinary_Deck_input_trial']['start_frame'];assert start==reports['control']['ordinary_Deck_input_trial']['start_frame']
 ignored={'full_RAM_sha256','stage_sha256'}
 for left,right in zip(reports['candidate']['frames'][:start],reports['control']['frames'][:start]):assert {k:v for k,v in left.items()if k not in ignored}=={k:v for k,v in right.items()if k not in ignored},left['frame']
 assert reports['candidate']['frames'][-1]['video_sha256']==reports['control']['frames'][-1]['video_sha256']
 session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);mapping=session/'nextstage-mapping.json';offset=read(mapping)['payload_raw_cdi_offset']+0x11828-0x4000
 control_disc=Path(jobs['control']['command'][jobs['control']['command'].index('--disc')+1]);changed=0;position=0
 with Path(build['derived_disc']).open('rb')as a,control_disc.open('rb')as b:
  while True:
   left,right=a.read(1048576),b.read(1048576);assert len(left)==len(right)
   if not left:break
   if left!=right:
    for i,(x,y)in enumerate(zip(left,right)):
     if x!=y:assert offset<=position+i<offset+6;changed+=1
   position+=len(left)
 assert 0<changed<=6
 for p,h in build['source_sha256'].items():assert sha(p)==h,p;bound.append(Path(p))
 bound.extend([Path(build['derived_disc']),Path(build['derived_stage']),Path(build['component']),mapping,control_disc])
 proof=dict(status='terminal_fresh_three_native_Deck_callers_reviewed',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),build=str(bp),build_sha256=sha(bp),disc=build['derived_disc'],disc_sha256=build['derived_disc_sha256'],native_code_bytes=build['linked_component_bytes'],shared_module_bytes=build['shared_Deck_code_bytes'],total_reservation_bytes=build['component_bytes'],initial_heap_bytes=0x1c0000-build['heap_start'],installed_recovered_Deck_entries=build['installed_Deck_entries'],remaining_hosted_only_Deck_entries=build['remaining_hosted_Deck_entries'],frames=len(reports['candidate']['frames']),ordinary_trial_frames=400,ordinary_native_returns=dict(zip(kernel.LAYOUT,candidate['native_returns'])),ordinary_native_helper_returns=dict(zip(kernel.LAYOUT,candidate['helper_returns'])),same_layout_control_returns=dict(zip(kernel.LAYOUT,control['native_returns'])),same_layout_control_original_scan_calls=control['public_entries'][2],native_GPU_returns=observed['candidate']['mb_returns'],all_observed_monitor_errors_pending_outside_zero=True,all101_Deck_seven_fences_pass=True,all102_GPU_fences_pass=True,Deck_used_slots=used,immutable_code_unchanged=True,pre_input_recorded_fields_equal_frames=start,pre_input_RAM_and_stage_hashes_excluded_for_static_redirect=True,control_declared_redirect_bytes=6,control_changed_disc_bytes=changed,final_video_equal=True,timing_cycle_identity_verified=False,component_cases=2880,final_address_cases=2880,nested_cases=128,final_address_nested_cases=128,suspended_frame_comparisons_per_nested_matrix=1600,startup_cases=6,heap_initialize_cases=192,capacity_cases=36,native_region_fault_controls=56,selector13_restoration_retained=True,restoration_changes_original_behavior=True,native_keyboard_default_updated=False,new_training=False,whole_game_complete=False,physical_console_verified=False,scope='Fresh ordinary HLE/emulator boot of separate three-caller repaired native disc and six-byte same-layout original-scan control. No checkpoint restore, host guest-RAM repair or CPU/task/GPU seed. Native scan/input/coordinate execute with retained original input/GPU/scheduler dependencies in this finite route. Scan252helper returns equal126input plus126coordinate returns: optional face contact was not reached naturally and remains fixture-qualified only. Arbitrary suspension/reentrancy/IRQ, cycle/audio/physical fidelity and full same-console source rebuild remain incomplete.',source_sha256={str(p):sha(p)for p in set(bound)})
 save(out/'review.json',proof);save(V/'native-Deck-shared-reviewed-v2-current.json',proof);print(proof['status'],proof['ordinary_native_returns'],flush=True)
if __name__=='__main__':main()
