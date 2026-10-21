"""Review actual original/native record-matrix calls reached with fresh ordinary controls."""
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha

def main():
 out=V/'record-matrix-268-fresh-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);jobs={};reports={};memories={};deps={str(Path(__file__)):sha(__file__)}
 for lane in ['candidate','control']:
  p=V/f'record-matrix-268-fresh-{lane}-current.json';j=read(p);assert j['status']=='terminal_fresh_matrix_route_coverage_pass_pending_review'and j['all_monitors_clear_and_quiescent']and j['snapshot_restores']==j['guest_RAM_writes']==0
  for source,h in j['source_sha256'].items():assert sha(source)==h,source
  deps.update(j['source_sha256']);deps[str(p)]=sha(p);d=Path(j['directory'])/'measurement';report=read(j['report']);memory=(d/'RAM-final.bin').read_bytes();mr=j['matrix_observation'];assert mr['errors']==mr['pending']==0 and mr['native_entries']==mr['native_returns'] and mr['original_entries']==mr['original_returns']
  assert j['observations']['records']['matrix_returns']==mr['native_returns']
  u=lambda a,w=2:int.from_bytes(memory[a:a+w],'big');assert u(0x49c60)==2 and u(0x49c64)==268 and u(0x49c76)==4
  objects=[dict(slot=i,type=u(a),flags=memory[0x4208c+u(a)],x=u(a+4),z=u(a+10),region=u(a+16),angle=memory[a+12])for i in range(40)for a in [0x4bd9c+i*30]if u(a)]
  assert objects==[dict(slot=0,type=114,flags=2,x=6368,z=35356,region=4,angle=0)]
  assert mr['native_returns']>0 and mr['original_returns']==0 if lane=='candidate'else mr['original_returns']>0 and mr['native_returns']==0
  outer=j['observations']['outer'];assert outer['native_returns']==outer['C_stack_observations']==0 and outer['minimum_heap_free_while_outer_active']==0xffffffff
  save(out/(lane+'-objects.json'),objects);save(out/(lane+'-job.json'),j);jobs[lane]=j;reports[lane]=report;memories[lane]=memory
  for f in [Path(j['report']),d/'RAM-final.bin',d/'indoor-observation.json',d/'matrix-route-observation.json',*d.glob('*-observation.json'),*d.glob('consumed-controls-*.json')]:deps[str(f)]=sha(f)
 a,b=reports['candidate']['frames'],reports['control']['frames'];c=jobs['candidate'];o=jobs['control'];assert c['frames']==22536 and o['frames']==22363 and c['matrix_observation']['native_returns']==190 and o['matrix_observation']['original_returns']==266
 assert c['observations']['records']['returns']==12700 and c['observations']['records']['copy_returns']==22566
 fields={}
 for key in ['video_sha256','raw_player_X','raw_player_Z','scene_word','player_mode_word','floor_word','held_buttons','full_GPU_state_sha256','full_DSP_state_sha256']:
  ids=[x['frame']for x,y in zip(a,b)if x.get(key)!=y.get(key)];fields[key]=dict(count=len(ids),first_frame=ids[0]if ids else None,final_equal=a[-1].get(key)==b[-1].get(key))
 frontend=sum((x.get('navigation')or{}).get('buttons',[])!=(y.get('navigation')or{}).get('buttons',[])for x,y in zip(a,b));u=lambda lane,addr,width=2:int.from_bytes(memories[lane][addr:addr+width],'big')
 assert all(fields[k]['final_equal']for k in ['video_sha256','raw_player_X','raw_player_Z','scene_word','player_mode_word','floor_word']) and memories['candidate'][0x49cba]==memories['control'][0x49cba]==189
 histories={lane:r['matrix_route_trial']['controls_history']for lane,r in reports.items()};assert len(histories['candidate'])==len(histories['control'])==1 and histories['candidate'][0]['sha256']==histories['control'][0]['sha256']
 render_region={lane:u(lane,0x49c1c,4)for lane in jobs};assert render_region==dict(candidate=3,control=4)
 comparison=dict(fields=fields,frontend_button_schedule_differences=frontend,identical_frontend_inputs=frontend==0,same_controller_algorithm_and_waypoints=True,consumed_indoor_controls_sha256=histories['candidate'][0]['sha256'],final_player_region=4,final_heading=189,final_render_batch_region=render_region,final_heap_free_bytes={lane:u(lane,0x112d64,4)for lane in jobs},global_heap_minimum_measured=False,audio={lane:r['audio']for lane,r in reports.items()},scope='Same v34layout;control restores only original17E0Esceneentry10bytes. Both retain inherited native globalE220/E098/copy providers,not pristine original game. Actual adaptive inputs differ. Finalvideo/playerstate agree,but final render-batch region differs3/4 and intermediate frames differ. No cycle/fullRAM/wholegamefidelity claim.')
 save(out/'comparison.json',comparison)
 proof=dict(status='terminal_fresh_native_and_original_record_matrix_path_covered_fidelity_open',directory=str(out),candidate_frames=len(a),control_frames=len(b),candidate_entry_frame=c['entered_frame'],control_entry_frame=o['entered_frame'],native_record_matrix_entries=190,native_record_matrix_returns=190,original_record_matrix_entries=266,original_record_matrix_returns=266,native_record_returns=12700,native_copy_returns=22566,native_scene_returns=c['observations']['shared']['native_returns'][5],fresh_record_matrix_path_verified=True,all_monitors_clear_and_quiescent=True,source_target_scene=268,instantiated_type=114,instantiated_region=4,static_angle=0,raw_catalogue_last_word=4,raw_catalogue_last_word_is_not_assumed_angle=True,observer_synthetic_fault_controls=1152,observer_actual_CPU_lanes=128,scene_C_stack_bytes=816-c['observations']['shared']['C_stack_low_offsets'][5],scene_C_stack_reserved=208,outer_active_heap_measured=False,outer_active_heap_bytes=None,outer_C_stack_measured=False,video_differences=fields['video_sha256']['count'],frontend_button_schedule_differences=frontend,game_latched_button_RAM_differences=fields['held_buttons']['count'],final_video_equal=True,final_player_XZ_scene_floor_heading_equal=True,final_render_batch_region_equal=False,final_heap_free_bytes=comparison['final_heap_free_bytes'],global_heap_minimum_measured=False,game_fidelity_verified=False,physical_console_verified=False,whole_game_complete=False,installed_preview_changed=False,snapshot_restores=0,host_guest_RAM_writes=0,new_predictions=0,new_training=False,comparison=str(out/'comparison.json'),source_sha256=deps,scope=comparison['scope'])
 save(out/'review.json',proof);save(V/'record-matrix-268-fresh-reviewed-v1-current.json',proof);print({k:proof[k]for k in ['status','native_record_matrix_returns','original_record_matrix_returns','video_differences','frontend_button_schedule_differences','scene_C_stack_bytes','final_heap_free_bytes']},flush=True)
if __name__=='__main__':main()
