"""Offline frame/timeline review; replaces inherited prior-image counters."""
import json,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
def main():
 manifest=V/'native-Deck-current-status-v1-current.json';w=read(manifest)
 for p,h in w['dependencies_sha256'].items():assert sha(p)==h,p
 packet=read(w['packet']);out=V/'scene-reset-timeline-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 save(out/'before-packet.json',packet)
 jobs={k:read(V/f'native-Deck-scene-reset-early-reset-v3-{k}-current.json')for k in ['candidate','control']};reports={k:read(x['report'])for k,x in jobs.items()};a,b=[reports[k]['frames']for k in jobs]
 keys=['raw_player_X','raw_player_Z','scene_word','player_mode_word','tile_word','equipped_word','movie_flag_words','cumulative_nonzero_audio_samples','movie_controller_state_word','navigation','floor_word','raw_word_49c5c','locomotion_state','held_buttons']
 diff={k:[x['frame']for x,y in zip(a,b)if x.get(k)!=y.get(k)]for k in keys};transitions={}
 for key in ['movie_flag_words','held_buttons']:
  rows={}
  for lane,r in reports.items():
   z=r['frames'];start=r['ordinary_Deck_input_trial']['start_frame'];rows[lane]=[dict(frame=x['frame'],offset=x['frame']-start,old=z[i-1].get(key),value=x.get(key))for i,x in enumerate(z)if i and x['frame']>start and x.get(key)!=z[i-1].get(key)]
  same=[x['value']for x in rows['candidate']]==[x['value']for x in rows['control']]
  rows['same_observed_value_sequence']=same;rows['candidate_minus_control_frame_shifts']=[x['frame']-y['frame']for x,y in zip(rows['candidate'],rows['control'])]if same else None;transitions[key]=rows
 videos=[]
 for i,(x,y)in enumerate(zip(a,b)):
  if x['video_sha256']!=y['video_sha256']:
   videos.append(dict(frame=x['frame'],candidate_CPU=x['CPU'],control_CPU=y['CPU'],candidate_matches_control_offsets=[j-i for j in range(max(0,i-4),min(len(b),i+5))if b[j]['video_sha256']==x['video_sha256']]))
 data=dict(status='terminal_offline_same_layout_input_timing_review',new_game_execution=False,new_predictions=0,new_training=False,selected_recorded_fields=keys,differences=diff,selected_state_differing_frame_union=len(set().union(*map(set,diff.values()))),transitions=transitions,video_differences=videos,pretrial_video_differences=sum(x['video_sha256']!=y['video_sha256']for x,y in zip(a[:24567],b[:24567])),scope='Frame-boundary samples only. Same-layout original-input control;compiled geometry in both. Timing differences are observed,not an isolated reset-cost attribution. Full RAM/CPU/GPU snapshots differ and do not prove equal final machine state. No claim of resolved older original-geometry fidelity differences.')
 save(out/'timeline.json',data);c=dict(packet['latest_native_candidate'])
 for key in ['final_heap_free','clear_cast_cpu_cost_comparisons','local_model_review','prior_instruction_timeline_applies_to','new_instruction_timeline_collected']:c.pop(key,None)
 c.update(recovered_entry='0x1102a',candidate_geometry_returns=jobs['candidate']['geometry_observation']['returns'],control_geometry_returns=jobs['control']['geometry_observation']['returns'],native_face_GPU_returns=jobs['candidate']['geometry_observation']['native_GPU_returns'],control_face_GPU_returns=jobs['control']['geometry_observation']['native_GPU_returns'],recorded_state_differing_frames=data['selected_state_differing_frame_union'],recorded_state_fields=keys,frame_observed_transitions=transitions,fresh_debug_active_calls={k:j['geometry_observation']['debug_active_entries']for k,j in jobs.items()},fresh_debug_dependency_calls={k:j['geometry_observation']['native_debug_dependency_entries']for k,j in jobs.items()},latest_timeline_review=str(out/'timeline.json'))
 report=ROOT/'reports/Scene Reset Input Timing Review.txt';report.write_text('BIWN reset route — offline timing review\n\n'
  'No game or model was rerun. All24967pairedframe records were compared. Fourteen video differences start at24629and end24793;pretrialvideo is equal. Recorded position,scene,mode,tile,floor,equipment,locomotion,navigation and movie-controller fields agree. Movie flags differ on3frames;held buttons differ on3otherframes. The candidate movie-flag transitions are2and1frames later;three held-button transitions are1frame later. These are frame-boundary observations,not instruction-level timing or isolated reset-cost attribution.\n\n'
  'Twenty native geometry returns and120GPUhelper returns occur in each lane;the control retains compiled geometry and restores original input. Both audio streams contain0nonzerosamples. FullCPU/RAM/GPU snapshots differ;finalvideoequality is not full-state fidelity.\n\n'
  'Current candidate counters now come from this exact run. Prior-image transition/cost/heap/model-review details remain in the historical packet instead of being inherited as current results. Experimental fidelity and whole-game rebuilding remain incomplete.\n\n'+str(out/'timeline.json')+'\n')
 packet['latest_native_candidate']=packet['latest_fresh_reviewed_candidate']=c
 packet['current_frame_difference_analysis']=dict(status=data['status'],report=str(report),comparison=str(out/'timeline.json'),differing_video_frames=14,held_button_differing_frames=3,movie_flag_differing_frames=3,pretrial_video_differences=0,original_geometry_control=False,scope=data['scope'])
 save(out/'current-status-packet.json',packet);shutil.copy2(__file__,out/'publisher-source.py');deps={str(x):sha(x)for x in out.rglob('*')if x.is_file()};deps[str(report)]=sha(report)
 pub=V/'scene-reset-timeline-reviewed-v1-current.json';atomic(pub,dict(status=data['status'],directory=str(out),report=str(report),facts=str(out/'timeline.json'),new_predictions=0,new_training=False,dependencies_sha256=deps))
 w.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**w['dependencies_sha256'],**deps,str(pub):sha(pub)});atomic(manifest,w)
 index=ROOT/'config/current-model-work-sources.json';items=read(index);items=[x for x in items if x[0]!=pub.name];items.append([pub.name,'BIWN offline reset timing and exact current-image counters']);atomic(index,items)
 for p,h in w['dependencies_sha256'].items():
  src=Path(p);assert src.is_relative_to(ROOT);dest=P/'workbench'/src.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True)
  if not dest.is_file()or sha(dest)!=h:subprocess.run(['/bin/cp','-c',str(src),str(dest)],check=True,capture_output=True)
 shutil.copy2(manifest,P/'workbench/verification'/manifest.name);shutil.copy2(index,P/'workbench/config'/index.name)
 print(json.dumps(dict(status=data['status'],state_differing_frame_union=data['selected_state_differing_frame_union'],movie_shifts=transitions['movie_flag_words']['candidate_minus_control_frame_shifts'],held_shifts=transitions['held_buttons']['candidate_minus_control_frame_shifts'],report=str(report)),indent=2))
if __name__=='__main__':main()
