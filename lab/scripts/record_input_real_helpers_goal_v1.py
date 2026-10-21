"""Record actual-helper/brief-frontend progress and retain the complete goal."""
import subprocess
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
from publish_geometry_records_progress_v1 import clone


def main():
    target=V/'goal-continuation-current.json';old=read(target)
    names=['native-input-real-animation-caller-v3','native-input-real-animation-caller-v4',
        'native-input-real-camera-caller-v3','local-input-helpers-reviewer-v1','local-input-helpers-reviewer-v2']
    jobs={name:read(V/(name+'-current.json'))for name in names}
    assert jobs[names[0]]['completed']==312 and jobs[names[1]]['completed']==318 and jobs[names[2]]['completed']==78
    assert sum(jobs[name]['new_predictions']for name in names[3:])==2
    actual_transports=[]
    for name in ['input-helpers-brief-delivered-current-MCP-response.json','input-helpers-brief-delivered-copied-MCP-response.json']:
        path=V/name;r=read(path);assert r['status'].startswith('terminal_actual_');actual_transports.append(path)
    cli=[]
    for lane in ['Root','copied']:
        path=V/f'input-helpers-brief-{lane}-status-cli.txt';text=path.read_text()
        assert len(text.splitlines())==12 and 'animation/equipment 318' in text and 'original GPU 78' in text
        assert '432 measured' in text and '512-byte entry reserve remains provisional' in text
        assert 'response unapproved' in text and 'Complete source-only Jaguar rebuild remains unfinished' in text
        cli.append(path)
    wp=V/'native-Deck-current-status-v1-current.json';wrapper=read(wp);packet=read(wrapper['packet'])
    h=packet['current_input_real_helpers_progress'];component=packet['current_native_input_prototype_progress']
    assert component==packet['latest_source_development']and component['module_bytes']==10580
    assert h['maximum_connected_caller_stack']==432 and not h['broader_scripted_837_D1_differences_waived']
    out=V/'input-real-helpers-goal-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    save(out/'previous-goal-state.json',old);audit=[]
    for name,job in jobs.items():
        result=subprocess.run(['ps','-p',str(job['pid']),'-o','pid=,command='],capture_output=True,text=True)
        script=('run_'+name.replace('-','_')+'.py')if name.startswith('local-')else('check_'+name.replace('-','_')+'.py')
        # Actual script names include run_local_input_helpers_reviewer and
        # check_native_input_real_*_caller, matching the job stems above.
        assert script not in result.stdout,(name,result.stdout)
        audit.append(dict(job=name,pid=job['pid'],status=job['status'],matching_live_process=False))
    save(out/'own-worker-audit.json',dict(status='terminal_all_own_helpers_and_reviewers_finished',jobs=audit,
        Root_and_copied_brief_CLI_exit_zero=True,Root_and_copied_MCP_terminal=True,
        unrelated_jobs_inspected=False))
    frontend=read(V/'input-helpers-brief-frontend-v1-current.json')
    frontend.update(status='terminal_Root_and_copied_12line_status_and_actual_MCP_verified',
        CLI_logs=[str(p)for p in cli],actual_MCP_reviews=[str(p)for p in actual_transports],
        command_outputs_verified=True,game_or_model_results_changed=False)
    atomic(V/'input-helpers-brief-frontend-v1-current.json',frontend)
    state=dict(
        status='active_real_helpers_animation318_cameraGPU78_stack432_brief17_full_goal_open',
        recorded_at=datetime.now(timezone.utc).isoformat(),objective=old['objective'],goal_status='active',
        full_objective_complete=False,blocked=False,previous_goal_state=str(out/'previous-goal-state.json'),
        previous_goal_turn_classification=old['current_turn_classification'],
        current_turn_classification='Progress:connectedactualoriginalanimation/queue318fixturesincluding6equipmentsupplement;78camera/math/originalGPUfixturespass. Newconnectedfullcallerstack432bytes. TwoactualRevieweroutputs15.88/5.05secondsremainunapproved;no weights. Defaultstatusshortenedto12lines;Root/copiedstatus17entry30andactualMCPverified. Binary10580unchanged;no newdisc/preview.',
        current_status_manifest=str(wp),current_status_packet=wrapper['packet'],report=h['report'],
        new_predictions_this_turn=2,optimizer_updates_this_turn=0,new_training_this_turn=False,
        new_unique_original_functions_recovered_this_turn=0,new_model_authored_source_blocks_this_turn=0,
        new_disc_built=False,installed_preview_changed=False,ongoing_finite_workers=[],
        own_finite_worker_terminal_audit=str(out/'own-worker-audit.json'),
        current_source_component=dict(profile=component['profile'],module_bytes=10580,component_bytes_changed=False,
            prior_local_C_predicate_bytes=120,prior_coordinator_assembly_guard_bytes=156,
            inherited_admission_route_cases=20188,inherited_scripted_full_caller_cases=6945,
            animation_fixture_cases=318,animation_native_calls=106,animation_original_fallbacks=212,
            actual_animation_CPU_calls=324,actual_queue_CPU_calls=312,
            actual_input_animation_calls=6,actual_input_native_bridge_animation_calls=2,
            camera_fixture_cases=78,camera_native_calls=26,camera_original_fallbacks=52,
            actual_camera_CPU_calls=78,camera_actual_animation_CPU_calls=78,camera_actual_queue_CPU_calls=72,
            original_GPU_both_lanes=True,original_GPUExec1_callback_invocations_candidate=40758,
            synchronous_GPU_completion=True,CPU_GPU_RAM_coherence_verified=True,
            native_entry_reserve_bytes=512,native_reserve_global_bound_proven=False,
            maximum_connected_full_caller_stack_bytes=432,animation_fallback_stack_bytes=120,
            camera_native_stack_bytes=352,camera_fallback_stack_bytes=122,
            inherited_real_task_yield_stack_bytes=392,fenced_task_stack_capacity=960,
            real_resources_collision_targeting_qualified=False,arbitrary_IRQ_qualified=False,
            universal_raw_ABI_qualified=False,installed_in_game=False,copied10580bytebuild_proof_inherited=True),
        current_context_limits=dict(
            broader6945_scripted_caller_upper_D1_differences=837,broader_differences_waived=False,
            animation318_upper_D1_differences=8,animation_D1_low_word_equal=True,
            camera78_raw_final_context_differences=0,camera78_all_final_registers_and_SR_equal=True,
            fixture_sets_distinct_not_improvement_metric=True,
            resource_collision_targeting_helpers_still_scripted=True,
            GPU_execution='OriginalGPU4320onbothlanes,synchronouspinnedemulatordevice;notnewsource-onlyGPU.',
            connected_CPU_comparison='Original68000instructionsandcompilednativeinputinUnicorn;existingseparatefullCPUhelperproofsnotrerun.',
            helper_DF60_in_equipment_fixture_scripted=True,arbitrary_IRQ_or_physical_console_claim=False,
            logical_native_error_still_fixture_ILLEGAL=True),
        new_game_execution_this_turn=dict(fresh_routes=0,new_discs=0,
            distinct_completed_animation_paired_fixtures=318,distinct_completed_camera_GPU_paired_fixtures=78,
            completed_total_distinct_paired_fixtures=396,actual_original_task_switch_trials=0),
        current_gameplay_baseline=old['current_gameplay_baseline'],pending_candidate=old['pending_candidate'],
        current_status_renderer=str(ROOT/'scripts/show_native_status_v17.py'),portable_entry_version=30,
        current_status_default_lines=12,current_frontend_actual_review=str(V/'input-helpers-brief-frontend-v1-current.json'),
        current_native_Chat_verified=False,native_Chat_observation=old['native_Chat_observation'],
        new_native_UI_attempt_this_turn=False,current_default_Reader_version=43,
        current_default_Reader_current_source_approved=False,
        local_model_review='Twoactualownedcopied27B6bitReviewerresponses,notindependentreviewers.15.88s/213wordsfactualsnapshotcheckedbut160wordlimitfailed. Oneexplicitlengthcorrection5.05s/63wordswithin120limit,butoneparagraphnotthreeandmeasured432versusprovisional512wordingunclear;unapproved/notdefault. Exactprompts/rawrepliesretained. No optimizerupdates/newweights;priorCoder120bytefunctionremainsunedited. NativeChatnotattemptedagainafterpriorobservationtimeout;headlessauthorized.',
        local_Reviewer_trials=h['local_Reviewer_trials'],
        completed_pilot_optimizer_updates_total=old['completed_pilot_optimizer_updates_total'],
        existing_pilot_review=old['existing_pilot_review'],
        remaining_requirements=dict(
            local_frontend='DefaultRoot/copiedstatus17entry30now12lines;actualCLI/MCPverified. RealReviewerbriefingstillunapprovedforlength/format/precision. DefaultReader43historical,notnewfacts. NativeLMStudioChatvisibility/currentcopiedmodelusabilityunverified;headlessallowed/no unlockrequest.',
            training='No newweightsoroptimizerupdates. ActuallocalCoderfunctionpasses,butusefulgainonuntouchedgameporting/modding/restorationtasksunproven. Earlierbase0/4adapter0/4qualitypilotunpromoted;exposedlessonsnotheldout.',
            game='Unchanged10580byteguardedprototypegains318realanimation/queueand78camera/math/originalGPUfixtureevidence. Needrealresource/collision/targetingcontracts,broader837D1contextresolution,provenstackreserve/error/IRQ/reentry,allocatedimage/startup/heap/alias/observerandfreshqualification. Fullsource-onlysame-console game/CPU/GPU/DSP/audiovisual/physicalvalidationunfinished;v37matrixgatefailed.',
            future_hardware=old['remaining_requirements']['future_hardware']),
        next_actions=[
            'Connectactualresource/collision/targetingbodiesunderbothoriginalandguardedcaller. ExistingstandalonefullCPUimplementationsarepresent;reuseproofsbuttestnewconnections. Keepbroader837D1differencesopen;78casezerorawcontextisnotuniversalABI.',
            'Extendactualhelpernestingandcooperative/IRQ/reentrycoverage. Newfullcaller432bytesisgreaterthanprior392real-yieldmeasurement;scopesdiffer.512entryreserveprovisional. ProductionlogicalCerrorhandlingstillnotqualified.',
            'Inspectallocatedimage/startupcopywidth/heap/alias/observercontractsbeforepatching1A266inagameimage.1C0000isfixtureonly;191F4globalentrystaysoriginal. Preservev34baseline,v37failedmatrixandoldDesktoppreview. No pose/timer/controllernormalizationtoforceimagefidelity.',
            'ContinuefullCPU/GPU/DSPsource-onlysame-consolerebuild,fidelity/audio,andrepresentativeuntouched-tasktrainingquality. KeepcurrentusefulCoderfunctionattributiondistinctfromunapprovedRevieweroutputs;no redundantinferencewithoutchangedtask/prompt.',
            'Keepdefaultstatusbriefandreviewabledetailslinked;improveordinarylocalChatwhenUIavailablewithoutunlockrequests. Sharedlease/catalogownershiprequiredforanynewinference;preserveunrelatedjobs.'
        ],
        completion_audit='Notachieved:actualretainedhelperconnectionsandclearerfrontendareprogress,notfullgame/source-onlyGPUorhardwareproof. Realremaininghelpers,IRQ/imagequalification,fidelity/audio,usefultrainedgain,nativeChat easeandfuturecapacityremainunfinished. Goal staysactive.',
        do_not_restart=old.get('do_not_restart',[])+[
            'Completed312realEB04/EAC4fullcallerbasecasesand6equipmentsupplement=318;324animation/312queuecalls,sixinputanimationcalls(two nativebridge),432stack',
            'Completed78camera/animation/originalGPUfullcallerfixtures;26native/52fallback,40758GPUExec1callbacks notsubmissions,allfinalCPU/publicstateagree',
            'Animationv1loggingfailureafter3andv2reuse-reviewfailurebeforetrialsretained;v3explicitD1lowgate/v4supplementcomplete',
            'Camera v1coherenceandv2nestedmathclassificationfailuresretained;v3coherentCPU/GPUmappingpasseswithoutresultmasking',
            'CompletedtwoactualReviewer15.88s213words/5.05s63words;bothunapprovedfordeliveryconstraints;no default/weightchange',
            'CompletedRoot/copiedstatus16entry29thenconcise12linestatus17entry30andactualMCPafterfrontendchange;nogametestreceiptreplay'
        ])
    save(out/'goal-state.json',state);assert str(target)not in wrapper['dependencies_sha256'];atomic(target,state)
    for source in [target,V/'input-helpers-brief-frontend-v1-current.json',*actual_transports,*cli,*[p for p in out.iterdir()if p.is_file()]]:
        clone(source,P/'workbench'/source.relative_to(ROOT))
    print(state['status'],flush=True)


if __name__=='__main__':main()
