"""Review finite v30 fresh routes; retain unresolved restoration, audio and timing differences."""
import shutil
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
from publish_scene_gpu_family_component_v1 import clone

def main():
    wp=V/'native-Deck-current-status-v1-current.json';w=read(wp)
    for p,h in w['dependencies_sha256'].items():assert sha(p)==h,p
    packet=read(w['packet']);prior=packet['native_scene_gpu_family_progress']
    out=V/'scene-gpu-family-fresh-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    save(out/'before-wrapper.json',w);save(out/'before-packet.json',packet)
    jobs={};reports={};dependencies={str(Path(__file__)):sha(__file__)}
    for lane in ['candidate','control']:
        jp=V/f'native-scene17-gpu-family-fresh-v2-{lane}-current.json';j=read(jp)
        assert j['status']=='terminal_fresh_scene17_route_pending_review'
        assert j['snapshot_restores']==j['host_guest_RAM_writes']==j['host_CPU_or_task_seeds']==0
        for p,h in j['source_sha256'].items():assert sha(p)==h,p
        dependencies.update(j['source_sha256']);dependencies[str(jp)]=sha(jp)
        report=Path(j['report']);assert sha(report)==j['report_sha256'];dependencies[str(report)]=sha(report)
        folder=Path(j['directory'])/'candidate'
        for name in ['shared','face','geometry','outer','reset','rotation','clear','display','gameplay']:
            p=folder/(name+'-observation.json');dependencies[str(p)]=sha(p)
        save(out/(lane+'-job.json'),j);jobs[lane]=j;reports[lane]=read(report)
    a,c=reports['candidate']['frames'],reports['control']['frames']
    keys=['video_sha256','held_buttons','raw_player_X','raw_player_Z','scene_word','player_mode_word','tile_word','floor_word','locomotion_state']
    comparisons={}
    for key in keys:
        indices=[i+1 for i,(x,y)in enumerate(zip(a,c))if x[key]!=y[key]]
        comparisons[key]=dict(count=len(indices),first_frame=indices[0]if indices else None,last_frame=indices[-1]if indices else None,final_equal=a[-1][key]==c[-1][key])
    assert len(a)==25001 and len(c)==24969
    assert comparisons['video_sha256']['count']==8481 and comparisons['held_buttons']['count']==460
    assert all(x['final_equal']for x in comparisons.values())
    sampled_heap={lane:j['outer_observation']['minimum_heap_free_while_outer_active']for lane,j in jobs.items()}
    assert sampled_heap==dict(candidate=560,control=560)
    candidate=jobs['candidate'];assert candidate['shared_observation']['native_returns'][5]==6318
    assert candidate['shared_observation']['helper_returns'][5]==5304
    rotation=read(Path(candidate['directory'])/'candidate/rotation-observation.json')
    assert rotation['returns']==5304
    compare=dict(fields=comparisons,frames={k:len(v['frames'])for k,v in reports.items()},audio={k:v['audio']for k,v in reports.items()},
        final_video_equal=True,final_selected_fields_equal=True,identical_frontend_inputs=False,
        same_feedback_policy=True,global_GPU_native_redirects_inherited_in_both=True,
        original_pinned_GPU_wait_equivalence_is_not_inherited_restoration_wait_equivalence=True,
        scope='Control restores only ten original scene-entry bytes. Both retain inherited global native GPU wrappers. Candidate scene bypasses the inherited pending-command guard with its pinned-original idle-only wait. Changed feedback inputs, code layout and restoration behavior prevent attributing differences to a single speed or logic cause. No fixed-input v30 prefix was run in this review.')
    save(out/'fresh-comparison.json',compare)
    report=ROOT/'reports/BIWN Scene GPU Family Fresh Route Review.txt'
    action='Reclaim private outer-task stack/arena capacity before adding larger source blocks. Review identical-input v30 differences and the scene-internal wait that bypasses the inherited pending-command guard. Continue170A0 geometry records and remaining CPU/GPU/DSP/HLE recovery; useful training quality, copied-weight Native Chat, whole-game rebuilding, audio and physical-console fidelity remain open.'
    facts=dict(prior);facts.update(status='terminal_v30_scene_gpu_family_fresh_route_pass_fidelity_open',directory=str(out),report=str(report),fresh_gameplay_verified=True,fresh_review_pending=False,
        candidate_frames=len(a),control_frames=len(c),fresh_scene_native_returns=6318,fresh_scene_helper_returns=5304,
        native_display_returns=5304,native_rotation_returns=5304,native_clear_returns=5304,
        video_differences=8481,held_input_differences=460,final_video_equal=True,final_selected_game_fields_equal=True,
        minimum_sampled_heap_while_outer_active=sampled_heap,live_heap_headroom_measured=True,global_heap_minimum_measured=False,
        game_fidelity_verified=False,new_predictions=0,new_training=False,optimizer_updates=0,
        fresh_internal_GPU_helper_counts_measured=False,all_monitors_clear_and_quiescent=True,
        snapshot_restores=0,host_guest_RAM_writes=0,host_CPU_or_task_seeds=0,
        current_fixed_input_v30_comparison_verified=False,comparison=str(out/'fresh-comparison.json'),next_action=action)
    report.write_text('BIWN v30 — fresh route passes; fidelity and capacity remain open\n\n'
        'Fresh HLE CD boot completes25001 candidate and24969 control frames. All6318 native scene calls and5304 captured geometry-record calls return. Display-list, rotation and clear helpers each return5304 times. Retained/shared/face/geometry/outer/reset/display/clear/rotation monitors finish clear and quiescent. No checkpoint restoration or host RAM/CPU/task repair was used. Individual internal GPU helper counts were not instrumented in this fresh route.\n\n'
        'There are8481 paired video differences and460 held-input differences. Selected positions and scene fields differ during the routes; final video and selected final fields agree. Audio is silent in both captures. Their feedback inputs differ, so these counts do not isolate a timing, logic or speed cause. No v30 identical-input prefix has been reviewed. Earlier fixed-prefix445 differences belong to v29.\n\n'
        'Module48738 bytes; connected scene stack168/208. Initial heap120320 bytes; minimum sampled free heap while the outer task was active is560 bytes in each lane, not a measured global minimum. The old outer C stack uses356 bytes in component tests; a separate persistent-context prototype uses164 but has not changed this disc or its arena. Memory reclamation is the next priority before adding larger recovered source blocks.\n\n'
        'Six already recovered GPU command CPU helpers execute directly inside the scene C provider;170A0 remains its only captured service. Global GPU entries were redirected by earlier work and remain inherited in both lanes. The internal E098 idle-only wait bypasses the inherited global wait guard for pending commands. Passing this finite route does not prove that restoration behavior is equivalent under other device schedules. Older metadata saying the global GPU entries were original is corrected by the byte audit in the component review. GPU programs, other original CPU/DSP/rendering/device/HLE dependencies remain.\n\n'
        'This is coordinator source. The local Author/Repair attempts remain rejected, with exact prompts and responses saved. No optimizer update, model-source adoption, new training-quality result or copied-weight Native Chat rendering claim follows. The Desktop checkpoint preview is unchanged; whole-game source rebuilding and physical-console/audio/IRQ fidelity remain unproven.\n\n'+action+'\n\nComparison: '+str(out/'fresh-comparison.json')+'\n')
    packet['native_scene_gpu_family_progress']=packet['latest_source_development']=facts
    scene=dict(packet['native_scene_draw_progress'])
    scene.update(status=facts['status'],profile=facts['profile'],experimental_disc=facts['candidate_disc'],experimental_disc_sha256=facts['candidate_disc_sha256'],
        prototype_module_bytes=48738,final_module_bytes=48738,native_code_bytes=89568,initial_heap_bytes=120320,
        fresh_scene_native_entries=6318,fresh_scene_native_returns=6318,fresh_scene_helper_returns=5304,
        native_display_returns=5304,native_rotation_returns=5304,native_clear_returns=5304,
        candidate_frames=len(a),control_frames=len(c),fresh_differing_video_frames=8481,held_input_differing_frames=460,
        final_video_equal=True,final_selected_game_fields_equal=True,new_disc_fresh_gameplay_tested=True,
        new_disc_fresh_route_completed=True,latest_fresh_result_is_passing_route=True,new_disc_fidelity_verified=False,
        minimum_sampled_heap_while_outer_active=sampled_heap,gpu_family_prototype=facts,report=str(report),next_action=action)
    for key in ['current_fixed_input_video_comparison','fixed_input_control_layout_changes','fixed_input_comparison']:
        if key in scene:scene['historical_v29_'+key]=scene.pop(key)
    scene['current_fixed_input_comparison_pending']=True;packet['native_scene_draw_progress']=scene
    display=dict(packet['native_display_list_progress']);display.update(status=facts['status'],module_bytes=48738,module_sha256=facts['module_sha256'],prototype_profile=facts['profile'],experimental_disc=facts['candidate_disc'],fresh_gameplay_verified=True,fresh_route_completed=True,game_fidelity_verified=False,final_native_display_returns=5304,candidate_frames=len(a),control_frames=len(c),report=str(report),next_action=action)
    packet['native_display_list_progress']=display
    old=packet['latest_native_candidate'];packet['previous_native_candidate_before_scene_gpu_family']=old
    latest=dict(old);latest.update(status=facts['status'],variant='v30 readable scene and direct GPU CPU command family plus retained native callers',candidate_disc=facts['candidate_disc'],candidate_disc_sha256=facts['candidate_disc_sha256'],native_module=str(V/'scene17-gpu-family-final-bridge-v1-current.json'),native_module_sha256=facts['module_sha256'],native_module_bytes=48738,native_code_bytes=89568,total_reservation_bytes=277568,candidate_initial_heap_bytes=120320,candidate_frames=len(a),control_frames=len(c),differing_video_frames=8481,final_video_equal=True,native_disc_fidelity_verified=False,new_fresh_gameplay_verified=True,fresh_route_completed=True,report=str(report),next_action=action,control_scope=compare['scope'],scope=compare['scope'])
    latest['native_module']=read(V/'scene17-gpu-family-final-bridge-v1-current.json')['payload']
    packet['latest_native_candidate']=packet['latest_fresh_reviewed_candidate']=latest
    packet.pop('pending_native_candidate',None)
    packet['native_scene_dispatch_headroom_progress']['next_action']=action
    packet['current_copied_Reader_progress'].update(latest_source_changed_since_last_prediction=True,current_source_reply_verified=False)
    packet['checked_current_summary']='V30 finite fresh route passes25001/24969 frames;6318 native scene and5304 captured geometry returns; display/rotation/clear5304 each. All monitors clear.8481 paired video/460 input differences; final video and selected fields agree; silent audio. Scene stack168/208; sampled outer-active heap560 bytes. Original global GPU redirects are inherited; internal scene wait bypasses their pending-command guard. No fixed-input v30 comparison, full-game or fidelity approval; checkpoint preview unchanged.'
    save(out/'facts.json',facts);save(out/'current-status-packet.json',packet);shutil.copy2(report,out/report.name);shutil.copy2(__file__,out/'publisher-source.py')
    dependencies.update({str(p):sha(p)for p in out.rglob('*')if p.is_file()});dependencies[str(report)]=sha(report)
    pub=V/'scene-gpu-family-fresh-reviewed-v1-current.json';atomic(pub,dict(status=facts['status'],directory=str(out),report=str(report),facts=str(out/'facts.json'),new_predictions=0,new_training=False,whole_objective_complete=False,dependencies_sha256=dependencies))
    w.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**w['dependencies_sha256'],**dependencies,str(pub):sha(pub)});atomic(wp,w)
    for p,h in dependencies.items():
        src=Path(p);assert src.is_relative_to(ROOT);clone(src,P/'workbench'/src.relative_to(ROOT))
    clone(pub,P/'workbench/verification'/pub.name);clone(wp,P/'workbench/verification'/wp.name)
    for root in [ROOT,P/'workbench']:(root/'CURRENT DECOMPILATION.txt').write_text(report.read_text())
    print(facts['status'],report,flush=True)

if __name__=='__main__':main()
