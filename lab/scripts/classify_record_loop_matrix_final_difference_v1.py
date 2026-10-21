"""Keep the failed final-video gate;record branch coverage and expanded pose."""
import collections
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha

def main():
    out=V/'record-loop-matrix-final-difference-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    jobs={};reports={};memories={};raws={};poses={};deps={str(Path(__file__)):sha(__file__)}
    for lane in ['candidate','control']:
        pointer=V/f'record-loop-matrix-268-fresh-{lane}-current.json';j=read(pointer)
        assert j['status']=='terminal_fresh_matrix_route_coverage_pass_pending_review'and j['all_monitors_clear_and_quiescent']
        assert j['snapshot_restores']==j['guest_RAM_writes']==0
        for p,h in j['source_sha256'].items():assert sha(p)==h,p
        deps.update(j['source_sha256']);deps[str(pointer)]=sha(pointer)
        d=Path(j['directory'])/'measurement';report=read(j['report']);m=(d/'RAM-final.bin').read_bytes();raw=(d/'video-final.xrgb8888').read_bytes();last=report['frames'][-1]
        assert sha(d/'video-final.xrgb8888')==last['video_sha256']
        u=lambda a,w=2:int.from_bytes(m[a:a+w],'big')
        mr=j['matrix_observation'];assert mr['errors']==mr['pending']==0
        assert mr['native_entries']==mr['native_returns']and mr['original_entries']==mr['original_returns']
        assert j['observations']['records']['matrix_returns']==mr['native_returns']
        assert mr['native_returns']>0 and not mr['original_returns']if lane=='candidate'else mr['original_returns']>0 and not mr['native_returns']
        assert u(0x49c60)==2 and u(0x49c64)==268 and u(0x49c76)==4
        assert u(0x4bd9c)==114 and u(0x4bd9c+16)==4 and u(0x4bd9c+12,1)==0
        pose=dict(integer_X=u(0x49c50,4),integer_Y=u(0x49c54),integer_Z=u(0x49c56,4),player_fraction_words=[u(a)for a in [0x49c5a,0x49c5c,0x49c5e]],camera_words=[u(a)for a in [0x49b8c,0x49b8e,0x49b90]],camera_fraction_words=[u(a)for a in [0x49b92,0x49b94,0x49b96]],heading_byte=u(0x49cba,1),scene=u(0x49c64),floor=u(0x49c62),player_region=u(0x49c76),render_batch_region=u(0x49c1c,4),record_count=u(0x49b88,4),final_free_heap_word=u(0x112d64,4))
        assert j['observations']['outer']['C_stack_observations']==0
        for p in [Path(j['report']),d/'RAM-final.bin',d/'video-final.xrgb8888',d/'original-emulator-final-frame.png',*d.glob('*-observation.json'),*d.glob('consumed-controls-*.json')]:deps[str(p)]=sha(p)
        save(out/(lane+'-job.json'),j);save(out/(lane+'-expanded-pose.json'),pose)
        jobs[lane]=j;reports[lane]=report;memories[lane]=m;raws[lane]=raw;poses[lane]=pose
    a,b=[r['frames']for r in reports.values()];left,right=raws.values();video=reports['candidate']['video'];other=reports['control']['video']
    assert all(video[k]==other[k]for k in ['width','height','pitch'])
    width,height,pitch=[video[k]for k in ['width','height','pitch']];assert pitch==width*4 and len(left)==len(right)==pitch*height
    changed=[(i%pitch//4,i//pitch)for i in range(0,len(left),4)if left[i:i+4]!=right[i:i+4]]
    box=[min(x for x,y in changed),min(y for x,y in changed),max(x for x,y in changed)+1,max(y for x,y in changed)+1]
    assert len(changed)==22858 and box==[1,38,225,218]
    assert poses['candidate']['player_fraction_words']==[3225,0,4172]and poses['control']['player_fraction_words']==[3534,0,74]
    assert poses['candidate']['camera_words']==[88,65504,1696]and poses['control']['camera_words']==[88,65504,1697]
    selected=['raw_player_X','raw_player_Z','scene_word','player_mode_word','floor_word']
    assert all(a[-1][k]==b[-1][k]for k in selected)and poses['candidate']['heading_byte']==poses['control']['heading_byte']==189
    fields={k:dict(count=sum(x.get(k)!=y.get(k)for x,y in zip(a,b)),final_equal=a[-1].get(k)==b[-1].get(k))for k in ['video_sha256',*selected,'held_buttons','full_GPU_state_sha256','full_DSP_state_sha256']}
    histories={lane:r['matrix_route_trial']['controls_history']for lane,r in reports.items()};assert len(histories['candidate'])==len(histories['control'])==1 and histories['candidate'][0]['sha256']==histories['control'][0]['sha256']
    stable={}
    for lane,rows in [('candidate',a),('control',b)]:
        final=rows[-1]['video_sha256'];n=0
        for r in reversed(rows):
            if r['video_sha256']!=final:break
            n+=1
        opposite=b[-1]['video_sha256']if lane=='candidate'else a[-1]['video_sha256']
        stable[lane]=dict(final_hash_consecutive_frames=n,opposite_final_hash_occurrences_last500=sum(x['video_sha256']==opposite for x in rows[-500:]))
    sources=[ROOT/'projects/black-ice-white-noise/restoration/biwn_world_update.c',ROOT/'projects/black-ice-white-noise/restoration/biwn_world_flow_cpu.c',ROOT/'scripts/review_record_loop_matrix_268_fresh_v1.py']
    deps.update({str(p):sha(p)for p in sources})
    c=jobs['candidate'];o=jobs['control']
    facts=dict(status='terminal_matrix_path_observed_final_video_gate_failed_expanded_pose_differs',directory=str(out),candidate_frames=len(a),control_frames=len(b),candidate_entry_frame=c['entered_frame'],control_entry_frame=o['entered_frame'],native_record_matrix_returns=c['matrix_observation']['native_returns'],original_record_matrix_returns=o['matrix_observation']['original_returns'],native_record_returns=c['observations']['records']['returns'],native_copy_returns=c['observations']['records']['copy_returns'],native_scene_returns=c['observations']['shared']['native_returns'][5],
        fresh_record_matrix_path_verified=True,all_monitors_clear_and_quiescent=True,baseline_final_video_gate_pass=False,final_video_equal=False,final_integer_XZ_scene_floor_heading_equal=True,final_full_pose_equal=False,expanded_final_pose=poses,final_differing_pixels=len(changed),final_differing_pixel_bbox_xyxy=box,image_size=[width,height],fields=fields,final_hash_stability=stable,
        frontend_button_schedule_differences=sum((x.get('navigation')or{}).get('buttons',[])!=(y.get('navigation')or{}).get('buttons',[])for x,y in zip(a,b)),same_indoor_waypoints_consumed=True,controls_sha256=histories['candidate'][0]['sha256'],
        source_target_scene=268,instantiated_type=114,instantiated_region=4,static_angle=0,observer_synthetic_fault_controls=1152,observer_actual_CPU_lanes=128,scene_C_stack_bytes=816-c['observations']['shared']['C_stack_low_offsets'][5],scene_C_stack_reserved=208,outer_active_heap_measured=False,outer_active_heap_bytes=None,outer_C_stack_measured=False,global_heap_minimum_measured=False,
        video_differences=fields['video_sha256']['count'],game_latched_button_RAM_differences=fields['held_buttons']['count'],audio={lane:r['audio']for lane,r in reports.items()},cause_resolved=False,render_algorithm_fault_isolated=False,pose_difference_masked=False,gameplay_or_fidelity_promoted=False,
        game_fidelity_verified=False,whole_game_complete=False,physical_console_verified=False,installed_preview_changed=False,snapshot_restores=0,host_guest_RAM_writes=0,new_predictions=0,new_training=False,
        scope='v37same-layout original-scene control;global nativecopy/matrix/waitproviders retained. Positive201native/266originalrecord-matrixreturns are branch coverage,not a passed final-video comparison. Integerplayercoordinates/heading agree but14bitfractional player state and camera words/fractions differ. Finalvideo differs22858pixels in left viewport;last500frames have no match to the opposite finalhash. Different adaptive inputs and fullposes prevent isolating a rendering-code cause. Failed exact-video reviewer is retained;no mask,wipe,checkpoint or replay was used to obtain equality.',source_sha256=deps)
    save(out/'review.json',facts);save(V/'record-loop-matrix-final-difference-v1-current.json',facts)
    print('Matrix path201/266observed;final-video gate remains FAILED:22858pixels,expanded poses differ.',flush=True)

if __name__=='__main__':main()
