"""Record verified v24 delivery and retain the full unfinished game/model goal."""
from datetime import datetime, timezone
from pathlib import Path
import shutil, sys
from publish_scene_reset_fresh_v1 import ROOT, V, P, read, save, sha, atomic
sys.path.insert(0, str(ROOT))
from native_deck_status_evidence_v1 import load


def main():
    packet = load(ROOT)
    scene = packet['native_scene_draw_progress']
    assert scene['fresh_scene_native_returns'] == 6473 and scene['fresh_differing_video_frames'] == 7374
    root_response = V/'scene17-direct-poll-current-MCP-response.json'
    copied_response = V/'scene17-direct-poll-copied-MCP-response.json'
    root_call, copied_call = read(root_response), read(copied_response)
    assert '7,374' in root_call['result']['checked_current_summary']
    assert copied_call['status'] == 'terminal_copied_MCP_actual_status_returns_direct_poll_facts'
    assert len(root_call['metadata']['tools']) == 19 and len(copied_call['tools']) == 18
    audits = []
    for path in P.glob('path-audit-*.json'):
        audit = read(path)
        if any('/scene17-current-summary-v1/' in name for name in audit.get('restored_paths', [])):
            assert not audit['denied'], path
            audits.append(path)
    assert audits, 'No copied server origin-guard audit for the new summary'
    out = V/'scene17-direct-poll-delivery-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    for source in [root_response, copied_response, *audits]:
        shutil.copy2(source, out/source.name)
    files = set(ROOT.glob('scripts/*scene17*direct_poll*.py'))
    files |= {ROOT/'scripts/run_scene17_fixed_prefix_v2.py', ROOT/'scripts/review_scene17_fixed_prefix_v1.py'}
    for source in files:
        dest = P/'workbench'/source.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
    for name in ['START HERE.txt', 'WATCH LOCAL AGENTS.txt']:
        shutil.copy2(ROOT/name, out/('before-'+name))
    start = ROOT/'START HERE.txt'
    text = start.read_text()
    a = text.index('CURRENT GAME WORK\n')
    z = text.index('\nREAD THESE', a)
    text = text[:a]+'''CURRENT GAME WORK
Readable native scene candidates and their full-route comparisons are documented in CURRENT DECOMPILATION.txt. Use BIWN Current Status.command for the checked current result; the command and local evidence tools work without generating a model answer.
The installed preview is the tested six-caller checkpoint build. Full readable game reconstruction, a complete source-only same-console build and physical Jaguar CD validation remain unfinished. Experimental training results and local model responses are recorded separately from source verification.
'''+text[z:]
    start.write_text(text)
    watch = ROOT/'WATCH LOCAL AGENTS.txt'
    watch.write_text('''CURRENT GAME WORK — v24 direct polling review

Codex coordinator: checked the direct physical GPU polling variant, fixed-input comparisons, final-address/native/fallback/nesting/bus/stack guards, copied source rebuilding and fresh gameplay. No cloud subagents were spawned. This is source and deterministic tool work, not model training.

Deterministic emulator/test jobs: completed candidate24,978/control24,962fresh frames; all6,473native scene calls and38,424helper calls returned with clear monitors. There are7,374paired video differences and323held-input differences. Final video and selected fields agree. Identical-input1,000frame tests still differ194video frames versus189previously. Full-game fidelity is incomplete. All finite decompilation workers in this continuation are terminal.

Local model roles: no new predictions or optimizer updates in this continuation. The prepared local Analyst/Reviewer proposal review was busy and generated no responses. Earlier complete-scene Author/Repair prompts and raw responses remain separate and both were rejected. The wire audit confirms distinct complete requests; identical replies are not an accepted repair. Native LM Studio Chat was not newly verified; UI inspection timed out.

User frontend: Desktop BIWN Test Preview remains the same tested game. The menu P launcher now selects that v4 Python GUI; startup validation passes. Shift+Up and C+Up send run input. Game code, disc and checkpoint are unchanged.

Portability: current status commands and actual MCP replies checked. Root has19tools; this copied package retains18. Both return current v24 facts. The stale headline was corrected with immutable prior evidence retained. These tool lookups do not load a model or train weights.

Detailed report:
'''+scene['report']+'\n\nCurrent exact tool/source evidence:\n'+str(V/'native-scene17-direct-poll-fresh-reviewed-v1-current.json')+'\n'+str(V/'scene17-current-summary-v1-current.json')+'\n\nPrepared local review and wire audit:\n'+str(V/'local-scene-poll-review-v1-current.json')+'\n'+str(V/'scene17-local-feedback-wire-audit-v1-current.json')+'\n\nHistorical notes follow. Running/pending statements below describe their recorded time.\n\n'+watch.read_text())
    for source in [start, watch, ROOT/'reports/BIWN GUI Quick Start.txt']:
        shutil.copy2(source, out/source.name)
        dest = P/'workbench'/source.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
    gp = V/'goal-continuation-current.json'
    goal = read(gp)
    save(out/'previous-goal-state.json', goal)
    goal.update(status='active_v24_scene_fresh_pass_fixed_input_fidelity_and_wholegame_open',
                recorded_at=datetime.now(timezone.utc).isoformat(),
                previous_goal_turn_classification='Progress: verified the installed Python GUI launcher and controls; recovered prior v24 component evidence.',
                current_turn_classification='Progress: finished256cross-root aliases,128connected cases,64geometry observer lanes and64reset pairs; v24 fresh candidate24978/control24962 completes with6473scene and38424helper returns and clear monitors. Reviewed identical-input1000frame replays:189v23/194v24video differences. Full feedback routes differ7374video/323held-input samples; final selected fields/video agree. Corrected menu launcher/docs and stale status headline; Root and copied actual MCP facts checked.',
                full_objective_complete=False, blocked=False, ongoing_finite_workers=[],
                new_training_this_turn=False, optimizer_updates_this_turn=0,
                completed_new_local_predictions_this_turn=0, newly_reviewed_actual_predictions=0,
                new_unique_original_functions_this_turn=0, new_coordinator_authored_routines_this_turn=0,
                new_native_target_scheduling_corrections_this_turn=0, new_disc_built_this_turn=False,
                candidate_disc_built_this_turn=False, game_reruns_this_turn=2,
                candidate_disc=scene['experimental_disc'], candidate_final_gate_pointer=str(V/'native-Deck-scene17-direct-poll-final-v1-current.json'),
                candidate_scene_final_gate_pointer=str(V/'scene17-direct-poll-final-bridge-v1-current.json'),
                candidate_new_fresh_gameplay_verified=True, candidate_native_disc_fidelity_verified=False,
                installed_preview_changed=False, experimental_game_model_adopted=False,
                latest_source_recovery_report=scene['report'], source_recovery_review=str(V/'native-scene17-direct-poll-fresh-reviewed-v1-current.json'),
                latest_source_recovery_review=str(V/'native-scene17-direct-poll-fresh-reviewed-v1-current.json'),
                latest_delivery_review=str(V/'scene17-direct-poll-delivery-v1-current.json'),
                latest_frame_difference_analysis=str(V/'scene17-fixed-prefix-review-v1-current.json'),
                current_status_reader_live_generation_verified=False, current_status_reader_current_source_reply_approved=False,
                current_status_reader_scope='Root actual MCP1.26/19tools and copied MCP1.26/18tools return current v24 details and headline; copied origin-guard audit has no denied access. Saved Reader35 predates this source work. No new model briefing or native Chat output verified.',
                next_game_source_target='Replace the original17F14 buffer-rotation dependency with readable full-CPU native source, preserving stack/flags/bus order and the original185B2 display-list service. This is native integration of an already recovered reference, not a new unique original routine.')
    goal['remaining_requirements']['game'] = ('V24 completes a fresh24978/24962frame feedback route with6473scene and38424helper returns and clear monitors. Final selected fields/video agree;7374paired video and323held-input samples differ. Fixed identical-input1000frame tests retain194v24video differences versus189v23. Polling alone does not resolve fidelity. Both full captures are silent. Whole readable-source game rebuilding, complete same-console build, original helper/GPU/DSP/HLE/device removal, arbitrary IRQ and physical console validation remain incomplete.')
    goal['next_actions'] = [goal['next_game_source_target'],
                            'Diagnose persistent scene/presentation differences under identical recorded inputs or aligned logical events; preserve the prefix and complete route receipts. Do not replay terminal tests merely to generate receipts.',
                            'Develop useful local fine-tuning and untouched-task evaluation when the shared model runtime is available. Copied-weight native Chat and256GBcapacity/performance remain unverified.']
    goal['do_not_restart'] += ['Completedv24deployed770scene/all8image/fallback384/nested64/bus14/aliases256+256+128/connected128/actual512shared+64geometry/reset64pairs/copied44108byteidentity.',
                               'Completed1000framev23/v24candidate/control fixed-input measurements and explicit live-boundary guard classification;189/194video differences, first549. Prior v1 control end-active failure retained.',
                               'Completedv24fresh24978candidate/24962control,6473nativeScene/38424helpers,7374paired video differences/323held-input differences; finalvideo/selectedfields equal, audio silent.',
                               'Completed launcher menu v4startup validation, current controls refresh, Root/copy status and actual MCP headline correction. Initial checker19tool expectation failed; package18tool behavior retained and raw failure preserved.']
    atomic(gp, goal)
    shutil.copy2(gp, P/'workbench/verification'/gp.name)
    shutil.copy2(__file__, out/'finalizer-source.py')
    receipt = dict(status='terminal_v24_fresh_fixed_input_Root_copied_MCP_delivery_complete_goal_active',
                   directory=str(out), installed_preview_changed=False, launcher_menu_updated=True,
                   new_predictions=0, new_training=False, whole_objective_complete=False,
                   root_status_command_exit_code=0, copied_status_command_exit_code=0,
                   root_actual_MCP_tools=19, copied_actual_MCP_tools=18, copied_origin_guard_denied=0,
                   source_sha256={str(p):sha(p) for p in out.iterdir() if p.is_file()})
    save(V/'scene17-direct-poll-delivery-v1-current.json', receipt)
    shutil.copy2(V/'scene17-direct-poll-delivery-v1-current.json', P/'workbench/verification/scene17-direct-poll-delivery-v1-current.json')
    print(receipt['status'], flush=True)


if __name__ == '__main__':
    main()
