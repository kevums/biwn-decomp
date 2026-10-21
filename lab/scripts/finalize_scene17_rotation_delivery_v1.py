"""Record native rotation delivery without closing the unfinished game/model goal."""
from datetime import datetime, timezone
from pathlib import Path
import shutil, sys
from publish_scene_reset_fresh_v1 import ROOT, V, P, read, save, sha, atomic
sys.path.insert(0,str(ROOT))
from native_deck_status_evidence_v1 import load


def main():
    packet=load(ROOT);scene=packet['native_scene_draw_progress'];candidate=packet['latest_native_candidate']
    assert scene['profile']=='deck-shared-v25-scene-rotation' and scene['native_rotation_returns']==5376
    assert scene['fresh_scene_native_returns']==6378 and scene['fresh_differing_video_frames']==4328
    publication=V/'native-scene17-rotation-fresh-reviewed-v1-current.json'
    root=read(V/'scene17-rotation-current-MCP-response.json');copied=read(V/'scene17-rotation-copied-MCP-response.json')
    assert root['result']['native_scene_draw_progress']['native_rotation_returns']==5376
    assert copied['status']=='terminal_copied_MCP_actual_status_returns_direct_poll_facts'
    # The checker name is historical; its v25 result is verified by decoded data.
    decoded=__import__('json').loads(copied['result']['content'][0]['text'])
    assert decoded['native_scene_draw_progress']['profile']=='deck-shared-v25-scene-rotation'
    for lane in ['root','copied']:
        text=(V/f'scene17-rotation-{lane}-status.txt').read_text()
        assert '5,376'in text and '4328video'in text and '444'in text and '201'in text
    audits=[]
    for path in P.glob('path-audit-*.json'):
        audit=read(path)
        if any('/native-scene17-rotation-fresh-reviewed-v1/'in name for name in audit.get('restored_paths',[])):
            assert not audit['denied'];audits.append(path)
    assert audits
    out=V/'scene17-rotation-delivery-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    for source in [V/'scene17-rotation-current-MCP-response.json',V/'scene17-rotation-copied-MCP-response.json',
                   V/'scene17-rotation-root-status.txt',V/'scene17-rotation-copied-status.txt',*audits]:
        shutil.copy2(source,out/source.name)
    scripts=set(ROOT.glob('scripts/*rotation*.py'))|{ROOT/'scripts/scene_rotation_observer_v1.inc.c',ROOT/'scripts/run_scene17_fixed_prefix_v3.py',ROOT/'scripts/show_native_status_v2.py'}
    for source in scripts:
        dest=P/'workbench'/source.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
    brief=ROOT/'reports/BIWN Buffer Rotation Progress.txt'
    brief.write_text('BIWN progress — native buffer rotation\n\n'
                     'The experimental v25 image now runs the buffer-rotation helper from readable C inside the native scene caller. It completed 5,376 rotation calls and 6,378 scene calls during a fresh test route. The original 185B2 display-list builder is still used. All monitors finished clear.\n\n'
                     'The candidate ran 24,974 frames and its original-scene control ran 24,969. Final video and selected game fields match. There are 4,328 intermediate video differences and 139 differing held-input samples. Both recordings are silent. The image is experimental and the installed Desktop preview is unchanged.\n\n'
                     'In a separate test with identical recorded inputs, 444 of 1,000 video frames differ. The larger v25 layout also changes 201 control video frames compared with the prior layout, so cross-build counts do not isolate the new helper. No fidelity or whole-game speed improvement is established.\n\n'
                     'The structured helper passes 256 host comparisons against the original CPU and Unicorn. The deployed module passes 770 scene cases and all eight final image gates, plus fallback, nesting, bus, alias and connected checks. The copied SDK produces the same 45,874-byte shared module. Peak component scene C stack is 156 of 208 bytes.\n\n'
                     'This is coordinator-authored integration of an already recovered routine. No new local predictions or training updates were made while the shared model runtime was busy. Full readable-source rebuilding, same-console validation, audio/IRQ fidelity and useful trained-model quality remain unfinished.\n\n'
                     'Next: replace the original E03A clear-submission helper while preserving its unbounded hardware wait, stack, flags and MMIO access order.\n\nDetailed evidence: '+scene['report']+'\n')
    watch=ROOT/'WATCH LOCAL AGENTS.txt';shutil.copy2(watch,out/'before-WATCH LOCAL AGENTS.txt')
    watch.write_text('CURRENT GAME WORK — native buffer rotation, v25\n\n'
                     'Codex coordinator reconstructed readable full-CPU 17F14 rotation and integrated it into a separate native scene image. Original 185B2 remains captured. This is one new native helper integration of an existing recovered reference; zero new unique original routines. No cloud subagents.\n\n'
                     'Deterministic tools completed original/Unicorn/host comparisons, real 68000 module tests, read-only monitor controls, copied compilation, fixed-input measurements and fresh candidate/control routes. Actual fresh results: 5,376 rotation returns; 6,378 scene returns; 37,730 helper returns; all monitors clear. Intermediate video/input differences remain.\n\n'
                     'Test-reader corrections are preserved: big-endian logical CPU decoding and reading the inactive bank from the physical CPU; recording native rotation helper boundaries in alias traces; observing the external helper entry before its declared component fixture effect. The initial alias case already matched final CPU/RAM. These test corrections did not modify game state or repair source behavior.\n\n'
                     'Local AI roles: no new model predictions, prompts sent for generation, optimizer updates or trained weights this continuation. The shared inference lease was busy. Earlier prompts and responses remain in the saved model-work viewer. Native Chat with the newest facts is not verified.\n\n'
                     'Current report: '+str(brief)+'\nDetailed source evidence: '+str(publication)+'\n\nHistorical notes below describe their recorded time.\n\n'+watch.read_text())
    for source in [brief,watch]:
        shutil.copy2(source,out/source.name);dest=P/'workbench'/source.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
    gp=V/'goal-continuation-current.json';goal=read(gp);save(out/'previous-goal-state.json',goal)
    goal.update(status='active_v25_native_rotation_fresh_pass_wholegame_and_model_quality_open',recorded_at=datetime.now(timezone.utc).isoformat(),
                previous_goal_turn_classification='Progress: v24 direct-poll full route and fixed-input differences published; corrected launcher and status headline; Root/copied MCP delivery passed.',
                current_turn_classification='Progress: structured17F14host256plus15guards; native/deployed770cases with156/208stack andzero originalrotation instructions. All8finalimage gates, fallback384/nesting64/bus14/inputbus13, aliases256+256+128/connected128, actual512shared/64geometry/reset64pairs plus rotation55calls/20faults pass. Copied45874byte module identical. Fresh24974/24969,6378scene/37730helpers/5376rotation returns, allmonitors clear. 4328paired video/139held-input differences remain; finalvideo/selectedfields equal. Fixed1000input prefix444video differences; prior-layout controls differ201. No inference or optimizer updates.',
                full_objective_complete=False,blocked=False,ongoing_finite_workers=[],new_training_this_turn=False,optimizer_updates_this_turn=0,
                completed_new_local_predictions_this_turn=0,newly_reviewed_actual_predictions=0,new_model_authored_complete_functions_this_turn=0,
                new_unique_original_functions_this_turn=0,new_coordinator_authored_routines_this_turn=1,new_internal_native_helper_integrations_this_turn=1,
                source_authorship_scope='One coordinator structured full-CPU body/native integration for already recovered17F14; no new unique original function, model-authored body or training update.',
                new_native_target_scheduling_corrections_this_turn=0,new_semantic_bus_fixes_this_turn=0,new_disc_built_this_turn=True,candidate_disc_built_this_turn=True,game_reruns_this_turn=4,
                candidate_disc=scene['experimental_disc'],candidate_final_gate_pointer=str(V/'native-Deck-scene17-rotation-final-v1-current.json'),candidate_scene_final_gate_pointer=str(V/'scene17-rotation-final-bridge-v1-current.json'),
                candidate_new_fresh_gameplay_verified=True,candidate_native_disc_fidelity_verified=False,candidate_new_nesting_verified=True,installed_preview_changed=False,experimental_game_model_adopted=False,
                latest_source_recovery_report=str(brief),source_recovery_review=str(publication),latest_source_recovery_review=str(publication),latest_fresh_candidate_review=str(publication),
                latest_component_source_review=str(V/'scene17-rotation-final-bridge-v1-current.json'),latest_frame_difference_analysis=str(V/'scene17-rotation-fixed-prefix-review-v1-current.json'),
                latest_delivery_review=str(V/'scene17-rotation-delivery-v1-current.json'),current_status_reader_live_generation_verified=False,current_status_reader_current_source_reply_approved=False,
                current_status_reader_scope='Root and copied checked status and actual MCP return current v25 facts and headline. Copied source/SDK compilation is byte-identical and origin guard has no denied access. No new model briefing or Native Chat output on these facts; older Reader35 remains separate.',
                next_game_source_target='Replace originalE03Aclear submission inside the native scene caller with structured full-CPU C while retaining the original unbounded F02238 hardware wait, MOVEM flag semantics, argument/private-stack effects and exact ordered MMIO writes. Existing recovered logical/static E03A references are not new unique routines.')
    goal['remaining_requirements']['game']='V25structured native rotation completes5376real185B2calls,6378scene and37730helper returns over24974frames; control24969. Allshared/rotation/geometry/outer/resetmonitors clear. Finalvideo/selectedfields agree but4328paired video/139held-input samples differ. Same-input1000prefix differs444frames; old/new control layouts differ201frames. Bothfullcaptures silent. Originalclear/geometry/projection/draw/displaylist/othergamecode,GPU/DSP/HLE/device dependencies remain. Fullreadable-source rebuild, complete same-console build, arbitrary IRQ/audio fidelity and physical Jaguar CD validation are incomplete.'
    goal['next_actions']=[goal['next_game_source_target'],'Continue fixed-input/phase-aligned diagnosis while preserving measured layout changes; do not claim the lower full-route difference count isolates a helper speedup or fixes fidelity.','Develop useful local model inference/training/evaluation when the shared model lease is available. Copied-weight Native Chat and future256GBcapacity/performance remain unverified.']
    goal['do_not_restart'] += ['Completedv25structured17F14host256CPU/Unicorn/order and15guards; native/deployed770scene156/208stack, zero originalrotationinstructions.','Completedv25all8imagegates/fallback384/nesting64/bus14/inputbus13/aliases256+256+128/connected128; copied45874byte module identical.','Completedv25read-only512shared/64geometry/reset64pairs plus newrotation55actual calls in64scene lanes and20hostfaultcontrols. Component185B2entry observed before fixture; actual return and markers at CPUstep boundaries.','Completedv25prefix1000candidate/control:444video differences; originalScenecontrols differ201versuspriorlayout. Live-cutoff arena/rotation pending values retained, not complete-route acceptance.','Completedv25freshcandidate24974/control24969,6378scene/37730helper/5376rotation returns, allmonitors clear;4328paired video and139heldinput differences, finalvideo/selectedfields equal; audio silent.','Completedv25Root/copiedcheckedstatus andactualMCP1.26(19/18tools),copiedorigin audit clear. No new local prediction/training/preview promotion.']
    atomic(gp,goal);shutil.copy2(gp,P/'workbench/verification'/gp.name);shutil.copy2(__file__,out/'finalizer-source.py')
    receipt=dict(status='terminal_v25_native_rotation_Root_copied_MCP_delivered_goal_active',directory=str(out),whole_objective_complete=False,
                 source_publication=str(publication),new_predictions=0,new_training=False,installed_preview_changed=False,
                 root_actual_MCP_tools=19,copied_actual_MCP_tools=18,copied_origin_guard_denied=0,
                 source_sha256={str(p):sha(p)for p in out.iterdir()if p.is_file()})
    save(V/'scene17-rotation-delivery-v1-current.json',receipt);shutil.copy2(V/'scene17-rotation-delivery-v1-current.json',P/'workbench/verification/scene17-rotation-delivery-v1-current.json')
    print(receipt['status'],str(brief),flush=True)


if __name__=='__main__':main()
