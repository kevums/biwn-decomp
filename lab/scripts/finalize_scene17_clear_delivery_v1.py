"""Save v26 clear plus local native-code progress; preserve the full active goal."""
import json,shutil,sys
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
sys.path.insert(0,str(ROOT))
from native_deck_status_evidence_v1 import load

def main():
    packet=load(ROOT);s=packet['native_scene_draw_progress'];local=packet['local_scene_clear_development_progress']
    assert s['profile']=='deck-shared-v26-scene-clear' and s['native_clear_returns']==s['native_rotation_returns']==5360
    assert s['fresh_scene_native_returns']==6361 and s['fresh_scene_helper_returns']==32256
    assert s['candidate_frames']==24984 and s['control_frames']==24963
    assert s['fresh_differing_video_frames']==8160 and s['held_input_differing_frames']==349
    assert local['accepted_complete_functions']==1 and local['target_native_cases']==772 and not local['model_source_installed']
    root=read(V/'scene17-clear-current-MCP-response.json');copied=read(V/'scene17-clear-copied-MCP-response.json')
    decoded=json.loads(copied['result']['content'][0]['text'])
    assert root['result']['local_scene_clear_development_progress']['target_native_cases']==772
    assert decoded['native_scene_draw_progress']['native_clear_returns']==5360 and decoded['local_scene_clear_development_progress']['target_native_cases']==772
    assert root['result']['proof_sha256']==sha(V/'native-Deck-current-status-v1-current.json')
    assert decoded['proof_sha256']==sha(P/'workbench/verification/native-Deck-current-status-v1-current.json')
    assert len(root['metadata']['tools'])==19 and len(copied['tools'])==18
    for lane in ['root','copied']:
        text=(V/f'scene17-clear-{lane}-status.txt').read_text()
        assert '5,360' in text and '8160video' in text and '279' in text and '33 frames' in text
        assert '772 native cases' in text and '19.33' in text
    indices={lane:read(base/'verification/current-model-work-index-v4-current.json')for lane,base in [('root',ROOT),('copied',P/'workbench')]}
    assert indices['root']['saved_prompt_or_transcript_records']==185 and indices['copied']['saved_prompt_or_transcript_records']==186
    def canonical(x):return {str(row.get('path')or row.get('prompt')).replace(str(P/'workbench'),str(ROOT))for row in x['files']}
    assert canonical(indices['root'])<=canonical(indices['copied'])
    extra=canonical(indices['copied'])-canonical(indices['root'])
    assert extra=={str(ROOT/'runs/Deck-status-live-v29-20261020T202328.173767Z/prompts-and-responses.txt')}
    audits=[]
    for path in P.glob('path-audit-*.json'):
        audit=read(path)
        if any('/local-clear-native-progress-v1/'in name for name in audit.get('restored_paths',[])):
            assert not audit['denied'];audits.append(path)
    assert audits
    out=V/'scene17-clear-delivery-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    for source in [V/'scene17-clear-current-MCP-response.json',V/'scene17-clear-copied-MCP-response.json',V/'scene17-clear-root-status.txt',V/'scene17-clear-copied-status.txt',V/'scene17-clear-source-context-check.json',ROOT/'native_deck_source_context_v13.py',*audits]:
        shutil.copy2(source,out/source.name)
    for key,index in indices.items():save(out/(key+'-prompt-index.json'),index)
    brief=ROOT/'reports/BIWN Clear Submission Progress.txt'
    brief.write_text('BIWN progress — native clear submission and local coding\n\n'
       'The experimental v26 image now executes the clear-submission helper from readable native code inside the scene caller, preserving the original unbounded hardware wait and MMIO store order. Native clear and buffer rotation each return 5,360 times in a fresh route. All 6,361 native scene and 32,256 captured-helper calls return; monitors finish clear. The original global helper entries and remaining original game services stay intact.\n\n'
       'Candidate/control run 24,984/24,963 frames. Final video and selected fields agree, but 8,160 paired video frames and 349 held-input samples differ. Both captures are silent. The identical-input 1,000-frame prefix has 279 video differences. The new original-scene control also differs from the prior layout on 33 frames. Neither timing nor fidelity improvement is established.\n\n'
       'Host clear proof: 256 comparisons plus 14 guards. Exact deployed scene proof: 772 cases, all eight final-image gates, fallback, nesting, bus, alias and connected checks; scene stack 156/208 bytes. Copied sources and SDK rebuild the 46,578-byte module exactly.\n\n'
       'Local inference: the first three-role trial failed compile/CPU checks. With explicit primitive declarations and stack-addressing guidance, the second Author produced a complete body in 19.33 seconds. It passes 256 host and 772 native component cases unchanged. Repair returned identical code after a harness import-path failure; correcting PYTHONPATH allowed the native test. The model module is 46,562 bytes and is outside the game image. Six predictions were reviewed across both trials; no optimizer updates or trained-weight improvement. Native Chat with these copied weights remains unverified.\n\n'
       'The installed Desktop Python GUI stays on its existing six-caller outdoor checkpoint. Whole-game decompilation, a complete same-console source rebuild, audio/IRQ fidelity and physical Jaguar CD validation remain incomplete. The full goal is active.\n\n'
       'Game review: '+s['report']+'\nLocal model review: '+local['report']+'\nExact successful-trial prompts: '+local['transcript']+'\n')
    watch=ROOT/'WATCH LOCAL AGENTS.txt';shutil.copy2(watch,out/'before-WATCH LOCAL AGENTS.txt')
    prior_watch=watch.read_text()
    if prior_watch.startswith('CURRENT GAME WORK — v26 clear and local code trial'):
        prior_watch=prior_watch.split('Historical notes below describe their recorded time.\n\n',1)[1]
    watch.write_text('CURRENT GAME WORK — v26 clear and local code trial\n\n'
       'Codex coordinator integrated the already recovered E03A clear helper into native scene code. This adds one structured native helper integration and zero newly discovered original functions. The game image uses coordinator code. No cloud subagents.\n\n'
       'Deterministic tools: host original-CPU/Unicorn comparisons, exact native execution, final-image/alias/connected/fault checks, read-only fresh-route monitors and copied compilation. Fresh candidate/control: 24,984/24,963 frames; 5,360 clear/rotation returns each; all monitors clear. 8,160 video differences and silent audio remain.\n\n'
       'Local model: copied daily 27B 6-bit model, sequential Author/check/Repair/advisory Reviewer. Trial1: compile then CPU/stack failures. Trial2: explicit primitive declarations and stack-addressing guidance; unedited Author body passes host256 and native772 after a harness import-path correction. Repair identical; one unique passing function. The unnecessary Repair was triggered by infrastructure, not incorrect model code. Reviewer predates the corrected native execution and is not independent.\n\n'
       'Six actual predictions across both trials, zero optimizer updates. Exact system/user prompts, raw responses, feedback and initial tool failures are preserved. These roles ran through the local SDK, not verified live in LM Studio Chat. Model code remains outside the game image. The next worker version sets the native harness PYTHONPATH and refuses to request semantic Repair for a missing import; it has not generated another prediction.\n\n'
       'Successful raw transcript: '+local['transcript']+'\nCurrent concise report: '+str(brief)+'\n\nHistorical notes below describe their recorded time.\n\n'+prior_watch)
    for source in [brief,watch]:
        shutil.copy2(source,out/source.name);dest=P/'workbench'/source.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
    scripts=set(ROOT.glob('scripts/*scene17*clear*.py'))|set(ROOT.glob('scripts/*scene_clear*.py'))|set(ROOT.glob('scripts/*scene17_clear*.py'))|{ROOT/'scripts/scene_clear_observer_v1.inc.c',ROOT/'scripts/run_scene17_fixed_prefix_v4.py',ROOT/'scripts/show_native_status_v2.py'}
    for source in scripts:
        dest=P/'workbench'/source.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
    gp=V/'goal-continuation-current.json';goal=read(gp);save(out/'previous-goal-state.json',goal)
    goal.update(status='active_v26_native_clear_and_local_component_pass_whole_goal_open',recorded_at=datetime.now(timezone.utc).isoformat(),
      previous_user_question_turn_classification='No goal implementation progress: checked existing Python GUI paths and explained launch/controls. This continuation revalidated existing workers from terminal outputs instead of restarting them.',
      previous_goal_turn_classification='Progress: reconstructed clear source and completed component/final-address gates; fresh routes and the first local worker were pending review. Their terminal files and exact source hashes were recovered.',
      current_turn_classification='Progress: reviewed completed v26 fresh candidate/control 24984/24963,6361 scene/32256 helper/5360 clear and rotation returns, all monitors clear. Published honest 8160video/349held-input differences and fixed-input279/layout33. First local trial3predictions rejected; second trial3predictions produces one unchanged scaffolded body passing host256/14guards and native772/156stack after correcting a harness import path. Root/copied status/MCP and prompt exports185/186 verified; copied-only Reader29 preserved.',
      full_objective_complete=False,blocked=False,ongoing_finite_workers=[],new_training_this_turn=False,optimizer_updates_this_turn=0,
      completed_new_local_predictions_this_turn=3,recovered_completed_predictions_from_prior_worker=3,newly_reviewed_actual_predictions=6,new_model_authored_complete_functions_this_turn=1,
      new_unique_original_functions_this_turn=0,new_internal_native_helper_integrations_this_turn=1,new_coordinator_authored_routines_this_turn=1,
      source_authorship_scope='Game image uses coordinator structured clear. One unedited local body passes separate native components with supplied wait/MMIO/flags and explicit addressing guidance; identical Author/Repair count as one unique function. Not in game image or untouched evaluation.',
      candidate_disc=s['experimental_disc'],candidate_final_gate_pointer=str(V/'native-Deck-scene17-clear-final-v1-current.json'),candidate_scene_final_gate_pointer=str(V/'scene17-clear-final-bridge-v1-current.json'),
      candidate_new_fresh_gameplay_verified=True,candidate_native_disc_fidelity_verified=False,candidate_new_nesting_verified=True,installed_preview_changed=False,experimental_game_model_adopted=False,
      source_recovery_review=str(V/'native-scene17-clear-fresh-reviewed-v2-current.json'),latest_source_recovery_review=str(V/'native-scene17-clear-fresh-reviewed-v2-current.json'),latest_fresh_candidate_review=str(V/'native-scene17-clear-fresh-reviewed-v2-current.json'),latest_source_recovery_report=str(brief),
      latest_component_source_review=str(V/'scene17-clear-final-bridge-v1-current.json'),latest_frame_difference_analysis=str(V/'scene17-clear-fixed-prefix-review-v1-current.json'),latest_delivery_review=str(V/'scene17-clear-delivery-v1-current.json'),
      latest_local_source_review=str(V/'local-scene-clear-worker-reviewed-v2-current.json'),latest_local_source_report=local['report'],local_model_native_module_bytes=46562,local_model_source_installed_in_game=False,
      current_status_reader_live_generation_verified=False,current_status_reader_current_source_reply_approved=False,current_status_reader_scope='Actual Root/copied MCP1.26 returns v26 and local component progress. Native Chat with copied weights/new facts not verified. Compact source context includes new facts. New local roles are SDK coding trials, not Reader briefings.',
      saved_prompt_or_transcript_records=185,portable_saved_prompt_or_transcript_records=186,next_game_source_target='Reconstruct retained scene dependencies such as185B2display-list construction while diagnosing fixed-input/video differences; preserve normal-call, bus, stack and actual-device behavior. Do not count existing-reference integrations as newly discovered original functions.')
    goal['remaining_requirements']['game']='V26 native clear/rotation each5360returns, scene6361/helpers32256 in24984fresh frames; control24963. All monitors clear; finalvideo/selectedfields agree. 8160paired video/349held-input samples differ; identical-input prefix279,control-layout33. Audio silent. Original scene/display-list/geometry/projection/draw/otherCPU,GPU/DSP/HLE/device dependencies remain. Whole readable source, complete same-console source rebuild, arbitrary IRQ/intermediate-state/audio fidelity and physical JaguarCD validation remain incomplete.'
    goal['remaining_requirements']['local_frontend']='Local SDK copied27B6bit scaffolded Author19.33s now produces one unedited body passing host256 and native772; prompts/feedback/raw source preserved. Initial tool import failure corrected. Installed easy reset workflow and GUI remain separate. Native Chat with copied weights/current facts and broader usability/quality remain unverified.'
    goal['next_actions']=[goal['next_game_source_target'],'Use the corrected future worker import environment; do not replay the completed six predictions or native matrices merely for receipts. Local clear module needs final-image/alias/fresh qualification before any game adoption.','Develop useful training/evaluation with untouched holdouts; existing64updatepilot remains0/4base/adapter and unpromoted. Two-update copied capability is not quality. Finish copied-weight nativeChat usability and future256GBcapacity/concurrency checks when applicable.']
    goal['do_not_restart'] += ['Completedv26clear host256/14guards; native/deployed772scene156/208stack, zero original clear/rotation component instructions; all8final-image gates, fallback/nesting/bus/alias/connected checks.','Completedv26fresh24984/24963; scene6361/helpers32256/nativeclear5360/rotation5360, all monitors clear. 8160video/349heldinput differences; final equal; silent audio.','Completedv26fixed-input1000prefix279video/layout33differences; live-cutoff raw monitors retained.','Completedlocalclearv1threepredictions rejected; v2threepredictions with identical Author/Repair,host256+14guards pass, exactAuthornative772passes after PYTHONPATH correction; do not regenerate or rerun native for identicalRepair.','CompletedRoot/copiedMCP1.26(19/18tools), checkedstatus, compactcontext and185/186prompt records; copied-onlyReader29 preserved.','Withdrawnfirstv26report-path collision restored v25original report/wrapper before correctedv2publication. All frozen prior dependencies validate; raw diagnostic preserved.']
    atomic(gp,goal);shutil.copy2(gp,P/'workbench/verification'/gp.name);shutil.copy2(__file__,out/'finalizer-source.py')
    receipt=dict(status='terminal_v26_clear_and_local_native_Root_copied_delivered_goal_active',directory=str(out),source_publication=str(V/'native-scene17-clear-fresh-reviewed-v2-current.json'),local_publication=str(V/'local-clear-native-progress-v1-current.json'),whole_objective_complete=False,new_predictions_started_this_continuation=3,recovered_completed_predictions=3,newly_reviewed_predictions=6,new_training=False,optimizer_updates=0,installed_preview_changed=False,root_actual_MCP_tools=19,copied_actual_MCP_tools=18,root_saved_records=185,copied_saved_records=186,copied_origin_guard_denied=0,source_sha256={str(p):sha(p)for p in out.iterdir()if p.is_file()})
    atomic(V/'scene17-clear-delivery-v1-current.json',receipt);shutil.copy2(V/'scene17-clear-delivery-v1-current.json',P/'workbench/verification/scene17-clear-delivery-v1-current.json')
    print(receipt['status'],str(brief),flush=True)
if __name__=='__main__':main()
