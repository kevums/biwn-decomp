"""Review directional native scan and original-scan control at quiescent ends."""
from datetime import datetime,timezone
import json
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
import check_native_deck_shared_v2 as kernel
V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def main():
 out=V/'native-Deck-face-review-v2'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 bp=V/'native-Deck-shared-disc-build-v2-current.json';build=read(bp);component=Path(build['component']).read_bytes();assert sha(build['component'])==build['component_sha256']and sha(build['derived_disc'])==build['derived_disc_sha256'];bound=[Path(__file__),bp,Path(kernel.__file__)];jobs={};reports={};faces={}
 for lane in ['candidate','control']:
  p=V/('native-Deck-face-v2-'+lane+'-current.json');j=read(p);jobs[lane]=j;assert j['status']=='terminal_fresh_face_route_pending_review'and j['child_pid']is None;assert j['snapshot_restores']==j['host_guest_RAM_writes']==j['host_CPU_or_task_seeds']==0;assert sha(j['build'])==j['build_sha256']
  for path,h in j['source_sha256'].items():assert sha(path)==h,path;bound.append(Path(path))
  r=read(j['report']);reports[lane]=r;folder=Path(j['report']).parent;face=read(folder/'face-observation.json');faces[lane]=face;s=read(folder/'shared-observation.json');o=read(folder/'gameplay-observation.json')
  assert not r['captured_state_input']and not r['host_CPU_or_GPU_register_seed'];trial=r['ordinary_Deck_input_trial'];assert 400<=len(trial['inputs'])<=912 and len(r['frames'])==trial['start_frame']+len(trial['inputs'])
  for row in trial['inputs']:
   n=row['offset'];expected=['1']if 1<=n<9 else ['B','C']if 25<=n<34 else ['U']if 50<=n<130 else ['U','L']if 145<=n<185 else ['0']if 225<=n<234 else [];assert row['buttons']==expected
  errors={k:v for k,v in o.items()if isinstance(v,(int,float))and any(word in k for word in ['error','pending','outside','corruption','collision'])};assert errors and not any(errors.values()),errors
  assert not any(s[k]for k in ['errors','pending','C_stack_outside'])and s['fallback_entries']==[0,0,0];assert s['native_entries']==s['native_returns'] and s['helper_entries']==s['helper_returns'];assert o['mb_entries']==o['mb_native']==o['mb_returns']and min(o['mb_returns'])>0
  assert face['entries']==face['returns']==face['positive_speed_entries']==19 and face['helpers']==2 and face['errors']==face['pending']==0
  if lane=='candidate':assert face['native_parent_returns']==face['suspended_native_parent_checks']==19 and s['native_returns']==[19,19,19]and s['original_body_steps']==[0,0,0]
  else:assert face['original_parent_returns']==19 and face['native_parent_returns']==face['suspended_native_parent_checks']==0 and s['native_returns']==[19,19,0]and s['original_body_steps'][2]>0
  ram_path=folder/'RAM-final.bin';ram=ram_path.read_bytes();base=build['resident_address']
  for lo,hi in [(base,build['arena_address']),(build['arena_end'],build['deck_arena_address'])]:assert ram[lo:hi]==component[lo-base:hi-base]
  for slot in range(101):
   at=build['deck_arena_address']+slot*1024
   for lo,hi in kernel.FENCES:assert ram[at+lo:at+hi]==component[at-base+lo:at-base+hi]
   for _,offset,_,_ in kernel.LAYOUT.values():assert ram[at+offset+114:at+offset+118]==bytes(4)
  for slot in range(102):
   at=build['arena_address']+slot*256
   for lo in [0,240]:assert ram[at+lo:at+lo+16]==component[at-base+lo:at-base+lo+16]
  final=r['frames'][-1];assert final['scene_word']==312 and final['player_mode_word']==1 and final['movie_flag_words']==[0,0]
  bound.extend([p,Path(j['report']),folder/'face-observation.json',folder/'shared-observation.json',folder/'gameplay-observation.json',ram_path,folder/'state-final.bin',folder/'original-emulator-final-frame.png'])
 start=reports['candidate']['ordinary_Deck_input_trial']['start_frame'];assert start==reports['control']['ordinary_Deck_input_trial']['start_frame']==24608
 for a,b in zip(reports['candidate']['frames'][:start],reports['control']['frames'][:start]):assert {k:v for k,v in a.items()if k not in ['full_RAM_sha256','stage_sha256']}=={k:v for k,v in b.items()if k not in ['full_RAM_sha256','stage_sha256']},a['frame']
 assert reports['candidate']['frames'][-1]['video_sha256']==reports['control']['frames'][-1]['video_sha256']
 session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);mapping=session/'nextstage-mapping.json';offset=read(mapping)['payload_raw_cdi_offset']+0x11828-0x4000;control_disc=Path(jobs['control']['command'][jobs['control']['command'].index('--disc')+1]);changed=position=0
 with Path(build['derived_disc']).open('rb')as a,control_disc.open('rb')as b:
  while True:
   x,y=a.read(1048576),b.read(1048576);assert len(x)==len(y)
   if not x:break
   if x!=y:
    for i,(u,v)in enumerate(zip(x,y)):
     if u!=v:assert offset<=position+i<offset+6;changed+=1
   position+=len(x)
 assert 0<changed<=6;bound.extend([mapping,control_disc,Path(build['component'])])
 proof=dict(status='terminal_natural_optional_face_native_scan_control_reviewed',directory=str(out),recorded_at=datetime.now(timezone.utc).isoformat(),build=str(bp),build_sha256=sha(bp),candidate_frames=len(reports['candidate']['frames']),control_frames=len(reports['control']['frames']),candidate_trial_frames=len(reports['candidate']['ordinary_Deck_input_trial']['inputs']),control_trial_frames=len(reports['control']['ordinary_Deck_input_trial']['inputs']),common_prescribed_input_frames=400,pre_trial_recorded_fields_match=24608,pre_trial_RAM_stage_hashes_excluded_for_redirect=True,natural_face_calls_each_lane=19,natural_face_returns_each_lane=19,face_helper_entries_each_lane=2,native_scan_parent_frame_and_stack_preserved_cases=19,all_monitored_errors_pending_outside_zero=True,all101_Deck_seven_fences_pass=True,all102_GPU_fences_pass=True,immutable_code_matches=True,final_video_equal=True,control_only_original_scan_redirect_bytes=6,control_changed_disc_bytes=changed,face_body_is_original_CPU_code=True,new_native_callers=0,new_algorithms=0,new_training=False,whole_game_complete=False,physical_console_verified=False,scope=__doc__+' Same reviewed three-caller image. Ordinary U then U+L activates positive-speed original face contact and two helper entries. Endpoints settle with released input:401candidate/402control input frames. Does not establish full cross-lane CPU-state or cycle identity, arbitrary suspension/reentry/IRQ, audio/physical fidelity, or full-game rebuilding.',source_sha256={str(p):sha(p)for p in set(bound)})
 save(out/'review.json',proof);save(V/'native-Deck-natural-face-reviewed-v2-current.json',proof);print(proof['status'],flush=True)
if __name__=='__main__':main()
