"""Review finite fresh v34 route;keep fidelity and unexercised paths explicit."""
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha

def main():
 out=V/'frame-phased-image-fresh-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);jobs={};reports={};deps={str(Path(__file__)):sha(__file__)}
 for lane in ['candidate','control']:
  p=V/f'native-frame-phased-image-fresh-v2-{lane}-current.json';j=read(p);assert j['status']=='terminal_fresh_scene17_route_pending_review'
  assert j['snapshot_restores']==j['host_guest_RAM_writes']==j['host_CPU_or_task_seeds']==0
  for f,h in j['source_sha256'].items():assert sha(f)==h,f
  deps.update(j['source_sha256']);deps[str(p)]=sha(p);report=Path(j['report']);assert sha(report)==j['report_sha256'];deps[str(report)]=sha(report)
  for observation in (Path(j['directory'])/'candidate').glob('*-observation.json'):
   deps[str(observation)]=sha(observation)
  jobs[lane]=j;reports[lane]=read(report);save(out/(lane+'-job.json'),j)
 a,c=reports['candidate']['frames'],reports['control']['frames'];assert all(x['frame']==y['frame']for x,y in zip(a,c))
 fields={}
 for key in ['video_sha256','held_buttons','raw_player_X','raw_player_Z','scene_word','player_mode_word','tile_word','floor_word','locomotion_state']:
  ids=[x['frame']for x,y in zip(a,c)if x[key]!=y[key]];fields[key]=dict(count=len(ids),first_frame=ids[0]if ids else None,final_equal=a[-1][key]==c[-1][key])
 frontend=sum((x.get('navigation')or{}).get('buttons',[])!=(y.get('navigation')or{}).get('buttons',[])for x,y in zip(a,c));heap={lane:j['outer_observation']['minimum_heap_free_while_outer_active']for lane,j in jobs.items()}
 candidate=jobs['candidate'];records=candidate['records_observation'];scene=candidate['shared_observation'];outer=candidate['outer_observation']
 assert 0<len(a)<=30000 and 0<len(c)<=30000 and all(v>0 for v in heap.values())
 nr=records['returns'];cp=records['copy_returns'];mx=records['matrix_returns'];sc=scene['native_returns'][5];original_scene=jobs['control']['shared_observation']['public_entries'][5]
 assert records['entries']==nr>0 and records['copy_entries']==cp and records['matrix_entries']==mx
 assert scene['native_entries'][5]==sc>0 and scene['helper_entries'][5]==scene['helper_returns'][5]==cp+mx
 assert all(candidate[name]['returns']==nr for name in ['rotation_observation','clear_observation','display_observation'])
 assert all(x['final_equal']for x in fields.values())
 for lane,j in jobs.items():
  for name in ['shared_observation','face_observation','geometry_observation','outer_observation','reset_observation','rotation_observation','clear_observation','display_observation','records_observation']:
   obs=j[name];bad={k:v for k,v in obs.items()if any(tag in k for tag in ['errors','pending','outside'])and isinstance(v,(int,float))};assert not any(bad.values()),(lane,name,bad)
 comparison=dict(frames=dict(candidate=len(a),control=len(c)),paired_frames=min(len(a),len(c)),fields=fields,frontend_button_schedule_differences=frontend,game_latched_button_RAM_differences=fields['held_buttons']['count'],field_meanings=dict(held_buttons='Game-latched controller RAM long0x49ba4,not the frontend input schedule.'),audio={lane:r['audio']for lane,r in reports.items()},final_video_equal=fields['video_sha256']['final_equal'],final_selected_fields_equal=all(x['final_equal']for x in fields.values()),minimum_sampled_heap_while_outer_active=heap,global_heap_minimum_measured=False,same_feedback_policy=True,identical_frontend_inputs=frontend==0,control_scope=candidate['observer_geometry_completion_scope'],scope='Paired frame-index comparison under the same feedback policy. Different actual input schedules prevent causal speed/fidelity inference. Control restores the whole original scene entry,so differences do not isolate new170A0 from earlier scene changes. E220record-matrix capture returns='+str(mx)+'. This is the observed count,not assumed branch coverage.')
 save(out/'comparison.json',comparison)
 facts=dict(status='terminal_v40_fresh_scene_and_records_route_reviewed_fidelity_open',directory=str(out),comparison=str(out/'comparison.json'),candidate_frames=len(a),control_frames=len(c),native_scene_returns=sc,control_original_scene_calls=original_scene,native_record_returns=nr,native_record_copy_returns=cp,native_record_matrix_returns=mx,native_record_matrix_fresh_path_verified=mx>0,native_display_returns=nr,native_rotation_returns=nr,native_clear_returns=nr,video_differences=fields['video_sha256']['count'],game_latched_button_RAM_differences=fields['held_buttons']['count'],frontend_button_schedule_differences=frontend,final_video_equal=True,final_selected_fields_equal=True,minimum_sampled_heap_while_outer_active=heap,global_heap_minimum_measured=False,scene_C_stack_bytes=816-scene['C_stack_low_offsets'][5],scene_C_stack_reserved=208,outer_C_stack_bytes=368-outer['C_stack_low_offset'],outer_C_stack_reserved=224,all_monitors_clear_and_quiescent=True,snapshot_restores=0,host_guest_RAM_writes=0,host_CPU_or_task_seeds=0,fresh_gameplay_verified=True,whole_game_complete=False,game_fidelity_verified=False,installed_preview_changed=False,new_training=False,new_predictions=0,source_sha256=deps)
 save(out/'review.json',facts);save(V/'frame-phased-image-fresh-reviewed-v1-current.json',facts);print({k:facts[k]for k in ['status','candidate_frames','control_frames','video_differences','game_latched_button_RAM_differences','frontend_button_schedule_differences','native_record_returns','native_record_matrix_returns','scene_C_stack_bytes','outer_C_stack_bytes']},flush=True)
if __name__=='__main__':main()
