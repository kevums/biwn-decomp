"""Publish finite nested/fresh evidence and the rejected isolated local trial."""
import json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 out=V/'native-Deck-deeper-validation-v2'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 fp=V/'native-Deck-deeper-gameplay-reviewed-v2-current.json';fresh=read(fp);assert fresh['status']=='terminal_fresh_deeper_geometry_candidate_observed_reviewed'
 assert fresh['candidate_frames']==24965 and fresh['control_frames']==24966 and fresh['differing_video_frames']==92 and fresh['final_video_equal']
 for p,h in fresh['source_sha256'].items():assert sha(p)==h,p
 hp=V/'native-source-isolated-handler-v2-current.json';handler=read(hp);assert handler['status']=='real_local_roles_and_prompt_blocks_complete_semantic_review_pending'
 session_dir=Path(handler['session']);session=read(session_dir/'session.json');assert session['source_role_context_isolated'] and len(session['roles'])==3
 assert [x['role']for x in session['roles']]==['Analyst','Restorer','Reviewer']and all(x['stats']['stopReason']=='eosFound'for x in session['roles'])
 assert sha(handler['installed_bundle'])==handler['installed_bundle_sha256']
 for i,role in enumerate(session['roles'],1):
  prompt=(session_dir/f'{i}-{role["role"]}-prompt.txt').read_text();assert 'OLD_HISTORY_SENTINEL'not in prompt and 'LEGACY_PRESET_SENTINEL'not in prompt
 assert sha(session_dir/'raw-Restorer.c')==hashlib.sha256(session['roles'][1]['response'].encode()).hexdigest()
 raw=V/'deck-geometry-helpers-v1/20261020T163202.313431Z';pre=read(raw/'protocol.json');diagnostics=read(raw/'root-diagnostics.json')
 assert pre['status']=='terminal_original_CPU_or_RAM_comparison_rejected'and pre['completed']==1 and len(diagnostics)==6 and sum(x['match']for x in diagnostics)==1
 transcript=['ACTUAL LOCAL SOURCE RECOVERY — ISOLATED ROLE CONTEXT','Three sequential passes on one local27B6bit model. No optimizer updates. UI controller is a test double; native Chat rendering is unverified.','']
 for i,role in enumerate(session['roles'],1):transcript +=['ACTUAL ROLE: '+role['role'],'EXACT PROMPT',(session_dir/f'{i}-{role["role"]}-prompt.txt').read_text(),'RAW RESPONSE',role['response'],'']
 (out/'prompts-and-responses.txt').write_text('\n'.join(transcript))
 analyst=json.loads(session['roles'][0]['response']);assert list(analyst)==['hazards']and len(analyst['hazards'])<=6
 local=dict(status='terminal_isolated_source_roles_mechanical_pass_raw_C_rejected',directory=str(out),session=str(session_dir),actual_predictions=3,optimizer_updates=0,same_weight_independent=False,native_Chat_verified=False,native_UI_verified=False,
  prompt_blocks_match_saved_prompts=True,legacy_history_excluded=True,Analyst_own_role_JSON=True,raw_source_compiles=True,preflight_passed_before_rejection=1,preflight_failed_case=dict(root='10968',variant=1),targeted_diagnostic_matches=1,targeted_diagnostic_cases=6,raw_source_adopted=False,
  coordinator_source_findings=['10968 uses a post-write unsigned loop test, clearing one extra byte; D1 is one too high, A0 is never committed and A1 final increment is not committed.','10BA4 omits positive timer decrement and uses result bits instead of the complete signed BGT condition; partial registers/flags are lost.','11384 pushes a word as4bytes, then cleans only the original10argumentbytes; A2 restoration and SP are wrong. Caller-saved/partial-register commits and CCR are also lost.'],
  coordinator_Reviewer_findings='Reviewer rejects overall but includes self-contradictory nondefects. Its BGT explanation is wrong: BGT requires Z clear and N equal V, not N unequal V. Its cleanup complaint incorrectly counts the JSR return word after RTS already consumed it. Word-as-long push is a real defect. No raw Reviewer judgment is accepted as verification.',
  actual_model_quality_verified=False,handler=str(hp),source_sha256={str(p):sha(p)for p in [hp,session_dir/'session.json',session_dir/'raw-Restorer.c',raw/'protocol.json',raw/'counterexample.json',raw/'root-diagnostics.json',out/'prompts-and-responses.txt']})
 save(out/'local-review.json',local);save(V/'deeper-Deck-helper-isolated-local-reviewed-v2-current.json',local)
 prior=read(V/'native-Deck-deeper-candidate-reviewed-v2-current.json');facts=read(prior['facts'])
 facts.update(status='terminal_deeper_candidate_nested_and_fresh_reviewed_fidelity_open',directory=str(out),new_outer_connected_matrix_verified=True,new_alias_matrix_verified=True,fresh_candidate_gameplay_verified=True,
  alias_cases=256,connected_cases=128,connected_task_slots=101,protected_component_frame_checks=2245,
  candidate_frames=fresh['candidate_frames'],control_frames=fresh['control_frames'],control_restores_only_geometry=True,control_redirect_bytes=8,
  real110D4_capture_and_return_count=18,compiled_helper_service_returns_each=18,real110D4_suspension_in_this_candidate_verified=False,
  differing_video_frames=92,final_video_equal=True,recorded_state_differing_frames=347,cycle_identity_verified=False,minimum_sampled_free_heap_while_outer_active=13680,final_heap_free=13832,
  new_model_predictions=3,workflow_live_model_retest_verified=True,workflow_live_model_retest_scope='Actual installed handler and local model;mock UI. Prompts/response blocks exact and legacy history absent. Raw code and Reviewer quality rejected.',new_optimizer_updates=0,
  new_local_source_adopted=False,default_promoted=False,installed_preview_changed=False,
  scope=fresh['scope']+' Finite component nesting:256alias cases,128connected cases across101slots,2245parent checks. New source-role isolation mechanically passes actual local generations,but raw code fails CPU oracle and Reviewer reasoning remains unreliable.',
  next_action='Analyze92video-different frames and trial timing/state differences;qualify the new checkpoint preview before replacing the installed GUI. Recover remaining110D4/1142E/10734 code and improve game model source/reviewer quality with held-out evaluation.')
 report=ROOT/'reports/Native Deeper Helpers Gameplay and Local Model Review.txt';facts['report']=str(report)
 report.write_text('BIWN — DEEPER NATIVE HELPERS: NESTING AND FRESH GAMEPLAY\n\n'
  'The separate geometry candidate now passes actual nested and fresh-boot checks. The installed Desktop preview remains the earlier six-caller build. This is three internal compiled helper implementations inside geometry,not three new public entry patches and not a full-game decompilation.\n\n'
  'Final-image coordinate/geometry and input/face shared-frame alias matrices pass128cases each. Each direction covers both stack banks/all32CCR values,four task slots and three guest stack depths. Busy inner calls execute their original bodies; suspended compiled frame/stack bytes remain unchanged. These are declared injected helper JSRs,not proof of natural reentry or IRQ safety.\n\n'
  'A128case connected comparison covers all101task slots. The six recovered callers and three helper bodies execute against original68000 CPU; nonarenaRAM,physical CPU/banks and ordered entry snapshots match. Native returns:coordinate832,input800,face485,scan112,geometry16. All three compiled helper markers appear16times each.2,245suspended-parent checks pass;outer stack peak356bytes.110D4 and remaining services are fixtures in this component matrix.\n\n'
  'The fresh candidate runs24,965frames; the same-layout original-geometry control runs24,966. Only eight bytes at11AD4are restored in the control; the other five public callers stay compiled in both. Geometry returns18times per lane. The candidate observes18actual compiled C service returns for each of10968,11384,10BA4and18real110D4capture/returns. The control executes all five original geometry helpers18times. Compiler helper completion is measured at the actual service C return before deck_call pops the logical RTS.\n\n'
  'All runtime errors,pending calls,stack-outside counts,arena fences and immutable code checks pass. Geometry uses144of176stackbytes,leaving32finite measured bytes. Outer peak356of416leaves60. Minimum sampled heap while outer active13,680bytes;final free13,832in both lanes. This is not a global heap minimum or arbitrary interrupt/suspension guarantee. New monitor passes two legal controls and rejects27faults;retained outer18fault and region88address controls pass.\n\n'
  '24,565pretrial recorded frames match after excluding staticRAM/stage hashes. During the trial92video frames differ;347recorded-state frames differ. Final video matches,while the control needs one extra frame to quiesce. Timing/visual equivalence is unproven. HLE/emulator/original dependencies,the13versus16frame restoration,audio and physical console fidelity remain open. No checkpoint restore or host guest-state injection is used in these fresh runs.\n\n'
  'Three actual local model passes retest installed revision7prompt isolation. The Analyst returns only its own four-hazard JSON; legacy preset/history sentinels are absent from all saved prompts and UI blocks match saved responses. The UI controller is a test double,so this does not establish visible native Chat rendering. Same weights are not independent review.\n\n'
  'Raw Restorer C compiles,passes the first clear-record fixture,and fails the second. Five of six targeted diagnostic cases fail. It clears an extra byte,loses A0/A1state,omits a timer decrement,uses a wrong signed condition,and pushes a word as4bytes. The Reviewer rejects overall but misstates BGT and stack cleanup and includes nondefects. Raw code and Reviewer reasoning remain rejected;zero optimizer updates.\n\n'
  'Next: '+facts['next_action']+' Full source rebuilding,broader game workflows,accepted game training and portable migration remain unfinished.\n\n'
  'Fresh proof: '+str(fp)+'\nExact local prompts/responses: '+str(out/'prompts-and-responses.txt')+'\nCandidate: '+facts['candidate_disc']+'\n')
 save(out/'facts.json',facts)
 deps=[fp,report,out/'facts.json',out/'local-review.json',V/'deeper-Deck-helper-isolated-local-reviewed-v2-current.json']
 publication=dict(status=facts['status'],directory=str(out),facts=str(out/'facts.json'),report=str(report),dependencies_sha256={str(p):sha(p)for p in deps},new_predictions=3,new_optimizer_updates=0,whole_goal_complete=False)
 pub=V/'native-Deck-deeper-validation-reviewed-v2-current.json';save(out/'publication.json',publication);save(pub,publication)
 sp=V/'native-Deck-current-status-v1-current.json';state=read(sp);shutil.copyfile(sp,out/'previous-current-publication.json');pp=Path(state['packet']);packet=read(pp);shutil.copyfile(pp,out/'previous-current-packet.json')
 packet['native_deeper_helper_candidate']=dict(facts,publication=str(pub));packet['checked_current_summary']='Installed BIWN Test Preview remains the fresh-reviewed six-caller build. A separate candidate adds three internal compiled geometry helpers and passes final-address,nested and fresh original-geometry control checks. Candidate24,965/control24,966frames;18geometry returns each.92video frames differ and final video matches;timing/fidelity remain open. New local prompt isolation passes actual generation checks,but raw model C and Reviewer reasoning remain rejected. Whole-game source rebuilding remains incomplete.';packet['checked_answer']=packet['checked_current_summary'];save(pp,packet)
 state['dependencies_sha256'][str(pp)]=sha(pp);state['dependencies_sha256'][str(pub)]=sha(pub);save(sp,state)
 config=ROOT/'config/current-model-work-sources.json';shutil.copyfile(config,out/'previous-model-sources.json');items=read(config);item=['deeper-Deck-helper-isolated-local-reviewed-v2-current.json','Actual local isolated source roles:prompts exact;raw C and Reviewer quality rejected']
 if not any(x[0]==item[0]for x in items):items.insert(0,item)
 save(config,items)
 gp=V/'goal-continuation-current.json';shutil.copyfile(gp,out/'previous-goal.json');g=read(gp);g.update(status='active_deeper_helpers_nested_and_fresh_pass_fidelity_and_training_open',recorded_at=datetime.now(timezone.utc).isoformat(),current_turn_classification='Progress:256alias/128connected cases passed;new monitor qualified;fresh geometry candidate/control reviewed;3actual isolated local predictions and raw C/Reviewer rejection audited.',current_turn_predictions=3,current_turn_actual_local_predictions=3,current_turn_optimizer_updates=0,current_turn_new_game_routines=0,current_turn_new_native_caller_integrations=0,current_turn_new_internal_helper_native_integrations=0,new_candidate_fresh_gameplay_verified=True,installed_preview_changed=False,local_team_new_source_context_live_model_retest_verified=True,local_team_live_model_code_quality_accepted=False,shared_model_resource_busy=False,full_objective_complete=False,blocked=False,ongoing_finite_workers=[],latest_source_recovery_report=str(report),native_deeper_validation_review=str(pub))
 g['remaining_requirements']['game']='Deeper candidate passes nested/fresh geometry controls;92video-frame differences and347recorded-state differences remain. Original110D4/1142E/10734,arbitrary suspension/IRQ,fidelity and whole-game source rebuilding remain incomplete;installed preview unchanged.'
 g['remaining_requirements']['local_frontend']='Revision7source-role isolation passes actual local generation/blocks checks withmockUI. Raw local C and Reviewer quality rejected. Visible new source Chat rendering and accepted game training remain unfinished.'
 g['next_actions']=[facts['next_action'],'Prepare accepted game training/evaluation with held-out cases;do not promote failed raw code or adapters.','Complete current portable runtime/config/native sources and verify migration readiness.'];save(gp,g)
 print(out,publication['status'],flush=True)
if __name__=='__main__':main()
