"""Reconcile current artifact references and publish the separate capacity prototype."""
from pathlib import Path
from datetime import datetime,timezone
import shutil
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
from publish_scene_gpu_family_component_v1 import clone

def main():
    wp=V/'native-Deck-current-status-v1-current.json';w=read(wp)
    for p,h in w['dependencies_sha256'].items():assert sha(p)==h,p
    out=V/'v30-fresh-and-outer-capacity-delivery-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    packet=read(w['packet']);save(out/'before-packet.json',packet)
    deps={str(Path(__file__)):sha(__file__)};proofs={}
    for name,count in [('native-Deck-outer-inplace-v1',1280),('native-Deck-outer-fallback-inplace-v1',384),('native-Deck-outer-waits-inplace-v1',192),('native-Deck-outer-inplace-connected-v1',128),('outer-inplace-copied-build-v1',None)]:
        pointer=V/(name+'-current.json');g=read(pointer)
        assert g['status'].startswith('terminal_') and 'failed'not in g['status']
        if count is not None:assert g['completed']==count
        for p,h in g['source_sha256'].items():assert sha(p)==h,p
        deps.update(g['source_sha256']);deps[str(pointer)]=sha(pointer);proofs[name]=g
        save(out/(name+'.json'),g)
    outer=proofs['native-Deck-outer-inplace-v1'];connected=proofs['native-Deck-outer-inplace-connected-v1']
    assert outer['code_bytes']==6060 and outer['maximum_C_stack_bytes']==connected['maximum_outer_C_stack_bytes']==164
    b=read(V/'native-scene17-gpu-family-disc-build-v1-current.json');scene=read(V/'scene17-gpu-family-final-bridge-v1-current.json');proto=read(V/'scene17-gpu-family-bridge-v2-current.json')
    d=packet['native_display_list_progress'];d.update(prototype_payload=proto['payload'],prototype_module_sha256=proto['payload_sha256'],final_deployed_payload=scene['payload'],module_address=b['shared_Deck_code_address'],module_sha256=scene['payload_sha256'])
    c=packet['latest_native_candidate'];c.update(directory=packet['native_scene_gpu_family_progress']['directory'],minimum_sampled_heap_while_outer_active=dict(candidate=560,control=560),native_scene_internal_helpers=['0x'+x for x in b['scene_internal_helper_entries']],total_internal_compiled_helpers=len(b['newly_compiled_helper_entries']))
    assert c['total_internal_compiled_helpers']==16 and sha(d['final_deployed_payload'])==d['module_sha256']==c['native_module_sha256']
    packet['latest_fresh_reviewed_candidate']=c
    packet['native_scene_draw_progress']['scope']=packet['native_scene_gpu_family_progress']['scope']+' V30 finite fresh route completes;8481 paired video differences and silent audio remain unresolved. Inherited global native GPU redirects are unchanged; the internal scene idle wait bypasses the inherited pending guard.'
    action='Integrate and qualify the persistent outer context, then reclaim its unused private arena capacity with explicit bounds and nesting checks. The prototype uses164 stack bytes versus356 in the deployed outer task, but its arena has not been reduced. Continue fixed-input/device-wait analysis,170A0 and whole-game CPU/GPU/DSP/HLE recovery, useful model training and copied-weight Native Chat usability.'
    facts=dict(status='terminal_outer_persistent_context_prototype_components_pass_unintegrated',profile='deck-outer-v31-inplace-v1',directory=str(out),authorship='Coordinator target specialization of the existing recovered outer algorithm',new_unique_original_functions=0,
        outer_cases=1280,fallback_cases=384,wait_resume_pairs=192,connected_cases=128,task_slots=101,
        previous_module_bytes=5798,module_bytes=6060,code_growth_bytes=262,previous_C_stack_bytes=356,C_stack_bytes=164,C_stack_reserved=416,
        copied_SDK_byte_identical=True,arena_bytes_reclaimed=0,disc_integrated=False,fresh_gameplay_verified=False,
        new_predictions=0,new_training=False,optimizer_updates=0,whole_game_complete=False,next_action=action,
        scope='Persistent private logical CPU replaces a copied local context. Original guest CPU commits and capture assembly remain. Intermediate private shadow writes differ; host recovery error atomicity is unchanged. Finite component and injected helper suspension tests are not arbitrary IRQ or complete scheduler proof. A first connected-checker run failed before execution because a generated save call had too many arguments; the failed source and protocol are preserved, and v2 passes128 cases.')
    packet['native_outer_inplace_progress']=facts
    # The newer source prototype is separate from the latest gameplay-tested disc.
    packet['latest_source_development']=facts
    for key in ['native_scene_draw_progress','native_scene_gpu_family_progress','native_scene_dispatch_headroom_progress','native_display_list_progress']:
        packet[key]['next_action']=action
    packet['current_copied_Reader_progress'].update(latest_source_changed_since_last_prediction=True,current_source_reply_verified=False)
    report=ROOT/'reports/BIWN Current Game and Capacity Progress.txt'
    report.write_text('BIWN — current game and memory-capacity progress\n\n'
        'The v30 experimental image completes 25,001 candidate and 24,969 control frames from CD boot. All 6,318 native scene calls and 5,304 captured geometry-record calls return. Display-list, rotation and clear helpers each return 5,304 times. All monitors finish clear and quiescent. There are 8,481 paired video differences and 460 input differences; final video and selected final game fields agree. Both audio captures are silent. These results support a finite route pass, not fidelity approval.\n\n'
        'The scene uses 168 of 208 reserved C-stack bytes. Free heap sampled while the outer task was active was 560 bytes in each lane; this is not the global minimum. The module is 48,738 bytes. Six already recovered GPU command CPU helpers now run directly inside the scene; geometry-record processing at 170A0 remains captured. Global GPU entries retain older native redirects. The internal scene wait bypasses their pending-command guard, which still needs broader device-schedule analysis. No identical-input v30 comparison has been reviewed.\n\n'
        'A separate outer-task prototype reuses its existing persistent CPU context. It passes 1,280 outer cases, 384 fallbacks, 192 wait/resume pairs and 128 connected cases across 101 task slots. Maximum observed C stack falls from 356 to 164 bytes; code grows from 5,798 to 6,060 bytes. The copied SDK rebuild is identical. No arena has been reduced and no heap bytes have been reclaimed yet. This prototype is not installed in the v30 image. Its first connected checker had a generated save-call error before execution; the corrected v2 result is preserved alongside the failure.\n\n'
        'The copied local model produced two rejected development responses: Author in 130.92 seconds and Repair in 125.76 seconds. Exact prompts and raw outputs are in the prompt viewer. The code in v30 and the capacity prototype is coordinator-authored. No model code was adopted or optimizer update performed. Earlier training capability and the failed quality pilot do not establish useful trained-model quality. Copied-weight Native Chat usability remains open.\n\n'
        'The Desktop checkpoint preview is unchanged. Complete readable-source and same-console rebuilding, remaining CPU/GPU/DSP/HLE/device/rendering recovery, audio/IRQ/physical-console fidelity, useful training quality and future 256 GB hardware performance remain incomplete.\n\nNext: '+action+'\n')
    facts['report']=str(report);save(out/'outer-capacity-facts.json',facts);save(out/'current-status-packet.json',packet);shutil.copy2(__file__,out/'publisher-source.py');shutil.copy2(report,out/report.name)
    deps.update({str(p):sha(p)for p in out.rglob('*')if p.is_file()});deps[str(report)]=sha(report)
    pub=V/'v30-fresh-and-outer-capacity-delivery-v1-current.json';atomic(pub,dict(status='terminal_v30_fresh_and_outer_capacity_prototype_delivered_goal_open',directory=str(out),report=str(report),new_predictions=0,new_training=False,whole_objective_complete=False,dependencies_sha256=deps))
    w.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**w['dependencies_sha256'],**deps,str(pub):sha(pub)});atomic(wp,w)
    goalp=V/'goal-continuation-current.json';goal=read(goalp);save(out/'before-goal-state-unhashed.json',goal)
    goal.update(status='active_v30_fresh_pass_outer_capacity_prototype_pass_full_goal_open',recorded_at=datetime.now(timezone.utc).isoformat(),
        previous_goal_turn_classification='Progress: prior work created v30 host/native prototypes and actual local Author/Repair attempts, recovered in this continuation.',
        previous_user_question_turn_classification='No decomp progress: answered the launcher question from verified local files.',
        current_turn_classification='Progress: v30 copied/exact-image gates, alias/nesting/observer qualification and fresh25001/24969 completed; global GPU inheritance and wait-guard difference audited. Separate outer persistent-context prototype passes1280/384/192pairs/128connected and copied rebuild; stack356to164, no arena reclamation yet.',
        completed_new_local_predictions_this_turn=0,new_local_predictions_started_this_turn=0,recovered_completed_predictions_from_prior_worker=2,newly_reviewed_actual_predictions=2,
        new_training_this_turn=False,optimizer_updates_this_turn=0,new_model_authored_complete_functions_this_turn=0,new_unique_original_functions_this_turn=0,
        new_internal_native_helper_integrations_this_turn=6,new_disc_internal_native_helper_integrations_this_turn=6,new_target_implementation_optimizations_this_turn=1,
        source_authorship_scope='Coordinator scene GPU CPU family and persistent outer-context specialization; two actual local coding attempts rejected and preserved. Zero new unique original routines.',
        ongoing_finite_workers=[],latest_gameplay_tested_profile='deck-shared-v30-scene-gpu-commands-v1',latest_new_component_profile=facts['profile'],latest_new_component_disc_integrated=False,latest_new_component_fresh_gameplay_verified=False,
        candidate_disc_built=True,candidate_disc=b['derived_disc'],candidate_initial_heap_bytes=120320,candidate_new_fresh_gameplay_verified=True,candidate_native_disc_fidelity_verified=False,
        candidate_new_nesting_verified=True,new_read_only_observers_qualified=True,latest_fresh_candidate_review=str(V/'scene-gpu-family-fresh-reviewed-v1-current.json'),latest_component_source_review=str(pub),latest_delivery_review=str(pub),latest_source_recovery_review=str(pub),latest_source_recovery_report=str(report),
        saved_prompt_or_transcript_records=187,portable_saved_prompt_or_transcript_records=188,full_objective_complete=False,blocked=False,installed_preview_changed=False,
        latest_outer_capacity_prototype=dict(module_bytes=6060,C_stack_bytes=164,arena_bytes_reclaimed=0,disc_integrated=False),next_game_source_target=action)
    goal['remaining_requirements']['game']='V30 finite fresh route passes, with8481 paired video/460 input differences and silent audio. Sampled outer-active heap560 bytes is narrow. Outer persistent-context prototype164-byte stack passes but is unintegrated, with zero reclaimed arena bytes. Whole-game readable source and same-console rebuilding, remaining CPU/GPU/DSP/HLE/device/rendering and audio/IRQ/physical-console fidelity remain incomplete.'
    goal['next_actions'][0]=action;goal['do_not_restart'] += ['Completed v30 host768/native768/retained4992/geometry256/prototype772/copied48738 and all8final gates, finalscene772/display1153/fallback384/nesting64/publicbus14/aliases256+256+128/outerconnected128.', 'Completed v30 51FUNC observer controls, actual shared512/geometry64/reset64pairs/displayrotation55/clear55; fresh25001/24969 with all guards clear. Do not restart terminal fresh jobs.', 'Completed outer persistent-context1280/384fallback/192waitpairs/128connected and copied6060-byte rebuild. Arena unchanged; capacity reclamation is next.']
    atomic(goalp,goal)
    for p,h in deps.items():
        src=Path(p);assert src.is_relative_to(ROOT);clone(src,P/'workbench'/src.relative_to(ROOT))
    clone(pub,P/'workbench/verification'/pub.name);clone(wp,P/'workbench/verification'/wp.name);clone(goalp,P/'workbench/verification'/goalp.name)
    for root in [ROOT,P/'workbench']:
        (root/'CURRENT DECOMPILATION.txt').write_text(report.read_text())
        (root/'WATCH LOCAL AGENTS.txt').write_text(report.read_text()+'\nUse Model Prompts and Responses.command for exact saved local prompts and outputs. Root/copied indexes contain187/188 records respectively; one new combined record contains both coding roles.\n')
    print('Delivered v30 fresh and outer capacity prototype; goal remains active:',report,flush=True)

if __name__=='__main__':main()
