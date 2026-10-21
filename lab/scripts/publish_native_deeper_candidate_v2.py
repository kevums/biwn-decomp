"""Publish native helper/candidate gates without claiming new fresh gameplay."""
import json,hashlib,shutil,fcntl,subprocess
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    names=['native-Deck-deeper-v2-current.json','native-deck-retained-deeper-v2-current.json','shared-Deck-fallback-deeper-v2-current.json','native-Deck-deeper-disc-build-v2-current.json','native-Deck-deeper-final-v2-current.json',
        'native-Deck-deeper-final-geometry-v2-current.json','native-deck-retained-deeper-final-v2-current.json','shared-Deck-fallback-deeper-final-v2-current.json','native-Deck-deeper-startup-heap-v2-current.json','native-Deck-deeper-capacity-v2-current.json',
        'native-Deck-outer-deeper-final-v2-current.json','native-Deck-outer-fallback-deeper-final-v2-current.json','native-Deck-outer-waits-deeper-final-v2-current.json']
    proofs={n:read(V/n)for n in names};checked={}
    for n,p in proofs.items():
        assert p['status'].startswith('terminal_')and 'failed'not in p['status']and 'wrong_target'not in p['status'],n
        for path,h in p['source_sha256'].items():assert sha(path)==h,path;checked[path]=h
    proto=proofs[names[0]];retained=proofs[names[1]];b=proofs[names[3]];final=proofs[names[4]];geo=proofs[names[5]]
    assert proto['completed']==geo['completed']==256 and proto['maximum_C_stack_bytes']==geo['maximum_C_stack_bytes']==144
    assert retained['completed']==proofs[names[6]]['completed']==4992 and retained['code_bytes']==proto['code_bytes']==35664
    assert proofs[names[2]]['completed']==proofs[names[7]]['completed']==1280
    assert proofs[names[8]]['startup_cases']==6 and proofs[names[8]]['heap_initialize_cases']==192 and proofs[names[9]]['cases']==36
    assert proofs[names[10]]['completed']==1280 and proofs[names[11]]['completed']==384 and proofs[names[12]]['completed']==192
    assert final['status']=='terminal_deeper_candidate_final_component_startup_heap_gates_pass'and not final['new_outer_connected_matrix_verified']and not final['fresh_gameplay_verified']
    assert sha(b['derived_disc'])==b['derived_disc_sha256']and sha(b['component'])==b['component_sha256']
    assert geo['deployed_module_byte_identity']and b['newly_compiled_helper_entries']==['10968','10ba4','11384']
    out=V/'native-Deck-deeper-candidate-review-v2'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    for n in names:shutil.copyfile(V/n,out/n)
    save(out/'verified-dependencies.json',checked)
    workflow_path=V/'source-role-context-install-v2-current.json';workflow=read(workflow_path)
    assert workflow['status']=='terminal_source_role_context_v2_vendor_installed_mechanical_checks_pass'and workflow['source_map_matches_staged_TS']and not workflow['actual_model_output_quality_verified']
    for p,h in workflow['source_sha256'].items():assert sha(p)==h,p
    construction_path=V/'source-role-context-unit-v2-current.json';construction=read(construction_path);assert len(construction['checks'])==3 and construction['actual_predictions']==0
    assert sha(construction['bundle'])==construction['bundle_sha256'];shutil.copyfile(workflow_path,out/'workflow-install.json');shutil.copyfile(construction_path,out/'workflow-construction-check.json')
    with(ROOT/'runs/.inference.lock').open('a')as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);busy=False;fcntl.flock(lock,fcntl.LOCK_UN)
        except BlockingIOError:busy=True
    ownership=subprocess.run(['lsof',str(ROOT/'runs/.inference.lock')],capture_output=True,text=True).stdout
    save(out/'shared-model-resource-state.json',dict(observed_at=datetime.now(timezone.utc).isoformat(),inference_lock_busy=busy,lock_file_owners=ownership,
        new_model_predictions_this_turn=0,note='Separate workspace job retains the shared resource; no interruption, duplicate load or new training by this goal continuation.'))
    facts=dict(status='terminal_native_deeper_candidate_final_components_reviewed_new_nesting_fresh_pending',directory=str(out),
        candidate_disc=b['derived_disc'],candidate_disc_sha256=b['derived_disc_sha256'],installed_preview_changed=False,public_native_Deck_callers=6,
        internal_helper_entries=['10968','10ba4','11384'],helper_global_entries_redirected=False,helpers_native_inside_geometry_only=True,original110D4_still_dependency=True,
        native_code_bytes=b['linked_component_bytes'],total_reservation_bytes=b['component_bytes'],initial_heap_bytes=b['initial_heap_bytes'],native_module_bytes=proto['code_bytes'],
        native_geometry_cases_each_address=256,retained_four_caller_cases_each_address=4992,full_CPU_full_RAM_fallback_cases_each_address=1280,
        maximum_observed_geometry_C_stack_bytes=144,geometry_C_stack_region=[832,1008],minimum_observed_geometry_C_stack_offset=864,observed_geometry_C_stack_margin_bytes=32,
        startup_cases=6,heap_initialize_cases=192,capacity_cases=36,outer_final_cases=1280,outer_final_fallback_cases=384,outer_final_wait_resume_pairs=192,
        new_outer_connected_matrix_verified=False,new_alias_matrix_verified=False,fresh_candidate_gameplay_verified=False,real110D4_suspension_in_this_candidate_verified=False,
        new_model_predictions=0,new_optimizer_updates=0,authorship='Coordinator native bus specialization and pre/post-call factoring; recovered algorithms retained. No new raw model C adopted.',
        workflow_revision=7,workflow_prompt_construction_checks=3,workflow_live_model_retest_verified=False,
        whole_game_complete=False,physical_console_verified=False,default_promoted=False,
        scope='Native68000 executes geometry and three recovered helpers in finite component matrices.110D4,1142E,10734 remain declared fixtures there;real110D4call is preserved in candidate code. New helpers are internal geometry implementations,not three additional patched public entries. Inactive shadow bank supplied from unchanged physical bank at virtual markers; final physicalCPU/both banks and nonarenaRAM exact. Final image module bytes match. No fresh/nested new-image/IRQ/timing/audio/physical equivalence claim.',
        next_action='Qualify new alias/nested six-caller plus three-helper execution and real-helper observers,then run fresh candidate/control and resource/video/state review before preview promotion.')
    save(out/'candidate-facts.json',facts)
    report=ROOT/'reports/Native Deeper Geometry Candidate Review.txt'
    report.write_text('BIWN — NATIVE DEEPER GEOMETRY CANDIDATE\n\n'
        'Three recovered helpers now execute as compiled68000code inside geometry11AD4:10968record clearing,10BA4animated texture selection and11384matrix setup. Six public Deck callers remain patched; the three original helper entry addresses are not globally redirected. The working desktop preview stays on the previous fresh-reviewed six-caller disc.\n\n'
        'Prototype and final-address checks each pass256geometry/helper cases,4,992retained four-caller cases and1,280fullCPU/fullRAM invalid/busy fallback cases. Geometry includes ordered helper-entry CPU/RAM comparisons;110D4,1142E,10734are declared fixtures. All101task slots are represented across the geometry matrix,with both stack banks and all32CCR values in aggregate. Private arenas and external capture return words are the declared normalization; final physicalCPU/both banks and nonarenaRAM match exactly. This is finite coverage,not every input/flag cross-product or a new-image whole-game proof.\n\n'
        'The first native matrix passed256cases but used all176geometry stack bytes. Callback rearrangement reduced that to172; omitting frame pointers did not help. Direct bus specialization initially used184bytes and crossed a guard; that rejected build is retained. Factoring matrix setup into before/after stages around the original110D4call reduced peak use to144bytes. The qualified source statements are retained,with the matrix-setup C frames returned before that helper call. Final lowest offset864 leaves32bytes above lower bound832; this is measured finite headroom,not arbitrary interrupt safety.\n\n'
        'A path substitution mistake first ran the retained matrix against the old31,374byte module. Module-size comparison blocked the build before disc creation. That result and its old-module fallback run are explicitly marked wrong-target. Corrected checks run the35,664byte deeper module; prototype/final deployed-byte identity and all new counts above pass.\n\n'
        'The separate candidate has76,494native code bytes,reserves264,448bytes,copies102,848bytes and starts with133,440heap bytes. Six startup,192heap-initialization and36capacity cases pass. Relocated outer code passes1,280semantic cases,384fullCPU/RAM fallback cases and192wait/resume pairs. These do not replace the pending new alias/nested matrix,fresh gameplay,real helper/scheduler and resource-peak checks.\n\n'
        'The visible local team plugin is updated to revision7. Source recovery roles receive only the current request,original source packet and explicitly labeled earlier drafts;unrelated conversation/preset history is excluded. Three actual SDK prompt-construction checks pass on staged and installed code. Vendor production source map matches the staged TypeScript. Existing controller-check compatibility entrypoint is preserved. No new model prediction or optimizer update occurred:the shared workspace is occupied by a separate job. Live model compliance,code quality and native UI rendering of the new revision remain unverified.\n\n'
        'Next: '+facts['next_action']+' Whole-game source rebuilding,game-model training acceptance,porting/modding/restoration workflow breadth and current portable migration remain incomplete.\n\n'
        'Candidate: '+b['derived_disc']+'\nSHA-256: '+b['derived_disc_sha256']+'\nFinal gates: '+str(V/names[4])+'\nWorkflow install: '+str(workflow_path)+'\n')
    publication=dict(status=facts['status'],directory=str(out),facts=str(out/'candidate-facts.json'),report=str(report),dependencies_sha256={str(p):sha(p)for p in [out/'candidate-facts.json',report,out/'verified-dependencies.json',out/'workflow-install.json',out/'workflow-construction-check.json',*[out/n for n in names]]},new_predictions=0,new_optimizer_updates=0,whole_goal_complete=False)
    save(out/'publication.json',publication);save(V/'native-Deck-deeper-candidate-reviewed-v2-current.json',publication)
    sp=V/'native-Deck-current-status-v1-current.json';state=read(sp);shutil.copyfile(sp,out/'previous-current-status-publication.json');pp=Path(state['packet']);packet=read(pp);shutil.copyfile(pp,out/'previous-current-status-packet.json')
    packet['native_deeper_helper_candidate']=dict(facts,report=str(report),publication=str(V/'native-Deck-deeper-candidate-reviewed-v2-current.json'))
    packet['checked_current_summary']+=' A separate candidate now executes the three deeper helper algorithms natively and passes final-address component/startup/heap gates;new nesting and fresh-gameplay validation remain pending. The preview is unchanged.'
    packet['checked_answer']=packet['checked_current_summary'];save(pp,packet);state['dependencies_sha256'][str(pp)]=sha(pp);state['dependencies_sha256'][str(V/'native-Deck-deeper-candidate-reviewed-v2-current.json')]=sha(V/'native-Deck-deeper-candidate-reviewed-v2-current.json');save(sp,state)
    gp=V/'goal-continuation-current.json';g=read(gp);shutil.copyfile(gp,out/'previous-goal.json')
    g.update(status='active_native_deeper_candidate_final_components_pass_new_nesting_fresh_pending',recorded_at=datetime.now(timezone.utc).isoformat(),
        previous_goal_turn_classification='Progress:three helper algorithms recovered and qualified in772hostC/256connectedcases;rawlocalC rejected.',
        current_turn_classification='Progress:three helpers execute natively in geometry;256prototype/final cases,4992retainedcases,1280fallbackcases each pass;separate candidate built and startup/heap/capacity/relocatedouter gates pass.Prompt isolation revision7 installed and mechanically checked.',
        current_turn_predictions=0,current_turn_actual_local_predictions=0,current_turn_optimizer_updates=0,current_turn_new_game_routines=0,current_turn_new_native_caller_integrations=0,current_turn_new_internal_helper_native_integrations=3,
        native_deeper_candidate_review=str(V/'native-Deck-deeper-candidate-reviewed-v2-current.json'),latest_source_recovery_report=str(report),new_candidate_fresh_gameplay_verified=False,
        installed_preview_native_Deck_callers=6,installed_preview_changed=False,local_team_plugin_revision=7,local_team_new_source_context_live_model_retest_verified=False,shared_model_resource_busy=busy,
        full_objective_complete=False,blocked=False,ongoing_finite_workers=[])
    g['remaining_requirements']['game']='Three deeper helpers now pass native prototype/final-address matrices inside a separate geometry candidate. New aliases/fullsixcaller+threehelper nesting,realhelper/scheduler and fresh/control resource/fidelity remain pending;workingpreview unchanged. Full-game source rebuilding and fidelity remain incomplete.'
    g['remaining_requirements']['local_frontend']='Source-role prompt isolation installed,3construction checks pass. Live-model behavior/new UI rendering,code/reviewer source fidelity and accepted game-model training remain unfinished;shared model resource currentlybusy.'
    g['next_actions']=[facts['next_action'],'Run actual isolated local-role output and training/evaluation when the shared resource is available;preserve rejected source and do not interrupt the separate worker.','Complete broader game recovery/workflows and migrate current runtime/plugin/native-source additions into the portable package.']
    save(gp,g);print(out,publication['status'],flush=True)
if __name__=='__main__':main()
