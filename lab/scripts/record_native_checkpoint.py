"""Reconcile the completed native-chat/runtime checkpoint; retain prior records."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

R = Path(__file__).resolve().parent.parent
V = R / 'verification'
S = Path(json.loads((R / 'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
NOW = datetime.now(timezone.utc).isoformat()
BACKUP = R / 'config-backups' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ') / 'progress-records'


def load(path):
    return json.loads(path.read_text())


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def artifact(path):
    return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size}


def main():
    transcript = V / 'transcripts/game-native-record4-20261012.md'
    text = transcript.read_text()
    assert text.rstrip().endswith('reconstruction.')
    turns = [{'prompt': m[1].strip(), 'response_and_tools': m[2].strip()}
             for m in re.finditer(r'### User\n(.*?)\n\n### Assistant\n(.*?)(?=\n### User|\Z)', text, re.S)]
    assert len(turns) == 7
    native = Path.home() / '.lmstudio/config-presets/Game Assistant.preset.json'
    portable = R / 'presets/Game Assistant.preset.json'
    assert native.read_bytes() == portable.read_bytes()
    names = ['verification/setup-status.json', 'verification/requirements-audit.json',
             'verification/current-runtime-state.json', 'verification/everyday-inference.json',
             'START HERE.txt', 'projects/black-ice-white-noise/analysis/' + S.name + '/boot-slice-validation.json']
    for name in names:
        target = BACKUP / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(R / name, target)
    review = {
        'time': NOW, 'status': 'visible_native_tests_completed_with_model_errors',
        'chat': 'Game Assistant — BIWN', 'model': 'advertising-scholar / local/advertising-qwen38',
        'context': 32768, 'parallel': 1, 'temperature': 0.2,
        'reasoning': 'off verified in native Chat', 'transcript': artifact(transcript),
        'prior_status_transcript': artifact(V / 'transcripts/game-native-runtime-20261012.md'),
        'native_preset': artifact(native), 'portable_preset': artifact(portable), 'turns': turns,
        'native_context_usage_percent': 33.34045,
        'tool_behavior': 'Automatic project_evidence(status) and inspect_boot(0xeac4,64,m68k); exact calls/results in native export. Followups reuse context. No external inference API dispatch.',
        'quality_limits': [
            'Earlier turns retain old evidence. Latest dated evidence/corrections supersede earlier unrecovered-stage claims.',
            'Initial status conflated original-game execution with rebuilt C and left exact mapping pending; followup corrected both.',
            'Routine draft failed signed guard, capacity arithmetic, argument order and full-path D0 behavior; same-model Reviewer missed errors. Draft not promoted.',
            'Coordinator independently translated and checked original CPU bytes, then showed corrections in Chat. Model acknowledgement is not independent verification.',
            'AX preview clipped final status; saved Markdown verifies its complete final sentence.',
            'Latest model correction calls argument mapping store order; actual writes are arg2,arg1,arg3,arg4. Host translation excludes intermediate ordering.'],
        'accepted_reconstruction': str(R / 'projects/black-ice-white-noise/restoration/biwn_record4.c'),
        'CPU_check': artifact(V / 'biwn-record4-checks.json'),
        'scope': 'Five isolated checked components; not a reconstructed full game.'}
    save(V / 'game-native-runtime-review.json', review)
    checked = load(S / 'boot-slice-validation.json')
    checked['portable_C_component_count'] = 5
    checked['nextstage_record_C'] = {'report': str(V / 'biwn-record4-checks.json'), 'fixture_count': 192,
                                    'host_guard_count': 4, 'original_interval': '[0xeac4,0xeb04)',
                                    'scope': 'Isolated original CPU comparison; negative count rejected by host.'}
    checked['record_component_added_at'] = NOW
    save(S / 'boot-slice-validation.json', checked)
    decomp = ('Original-game HLE captures show character/street/HUD and controller-dependent viewpoint changes after identical pre-input RAM/framebuffers. '
              'Entire 1,032,192-byte stage matched assisted BIOS-mode RAM at frame899. HLE audio silent; BIOS injects boot/trampoline/TOC and ends in GPU wait. '
              'Sampled static entry addresses:27 HLE,30 with input; incomplete coverage. Five portable C components checked; latest record routine passed192 CPU fixtures and4 host guards. '
              'Separate DIVU candidate passed592 p-code fixtures and296 verbatim-C comparisons. Full reconstructed game, unmodified BIOS and hardware accuracy remain unverified.')
    frontend = ('Two named everyday native chats saved and tested at32k, one worker: Game Assistant — BIWN and Advertising Assistant — Research & Teaching. '
                'Normal questions automatically retrieve scoped evidence. Latest generations terminal/exported. Visible roles share one model/context, not independent agents.')
    status = load(V / 'setup-status.json')
    status.update(updated_at_utc=NOW, frontend=frontend, game_work=decomp,
                  advertising_model='27B Qwen3.8 loaded at32768 context, one worker. Five-turn native test completed without overflow at approximately20tokens/sec. Numeric/causal/length review required.',
                  pending='Unlock resolved. Improved trained default, broader workflow evaluation and full-game reconstruction incomplete; no advertising adapter trained.',
                  models='Pinned installed models retained;27B Qwen3.8 provisional for both everyday chats. Larger coding candidate unselected after resource guard rejection.')
    save(V / 'setup-status.json', status)
    models = json.loads(subprocess.run([str(Path.home() / '.lmstudio/bin/lms'), 'ps', '--json'],
                                     cwd=Path.home() / '.lmstudio', check=True, capture_output=True, text=True).stdout)
    runtime = load(V / 'current-runtime-state.json')
    runtime.update(recorded_at=NOW, models=models, visible_chat=frontend, decomp_progress=decomp,
                   local_inference_jobs='Native generations terminal; CLI model idle, queued0. No external inference API dispatch.',
                   MCP_updated_evidence='Fresh native connection verified after restart/reconnect. Native status evidence7735 JSON bytes. Selected snapshot includes runtime mapping/input/PC observations.',
                   emulator_jobs='Smoke, RAM/video/input captures and PC observers terminal. HLE audio capture exits1 for fully silent audio; failure retained.')
    save(V / 'current-runtime-state.json', runtime)
    save(V / 'everyday-inference.json', {
        'updated_at': NOW, 'status': 'provisional_supervised_daily_chat_ready_with_quality_limits',
        'frontend': frontend, 'model': models,
        'game_review': str(V / 'game-native-runtime-review.json'),
        'advertising_review': str(V / 'advertising-native-32k-review.json'),
        'game_transcript': artifact(transcript),
        'advertising_transcript': artifact(V / 'transcripts/advertising-native-32k-20261012.md'),
        'configuration': {'context': 32768, 'parallel': 1, 'reasoning': 'off', 'temperature': 0.2,
                          'game_max_tokens': 1024, 'advertising_max_tokens': 2048},
        'speed': 'Approximately20–21tokens/sec in recorded native generations; not comprehensive benchmark.',
        'memory': 'Swap177.94MiB at two snapshots, unchanged; peak memory pressure unmeasured.',
        'limitations': ['Same-model roles are not independent verification.',
                        'Game code generation still has numerical/ABI errors; CPU comparisons required.',
                        'Advertising statistics, causal wording and length need review.',
                        'No improved trained default promoted or advertising adapter trained.'],
        'screen_unlock': 'resolved; native tests complete',
        'historical_record': str(BACKUP / 'verification/everyday-inference.json'),
        'full_goal_status': 'incomplete'})
    audit = load(V / 'requirements-audit.json')
    audit.update(recorded_at_utc=NOW, goal_status='active incomplete; disc and unlock blockers resolved',
                 previous_goal_turn_classification=audit['this_goal_turn_classification'],
                 this_goal_turn_classification='progress: native32k Chat tests/exports, exact assisted stage mapping/input response, CPU-PC observations and fifth checked portable component.',
                 next_safe_work='Guide separate disassembly with observed PC addresses, reconstruct further routines against CPU checks, investigate silent HLE audio/BIOS GPU wait, expand source-backed training/evaluation.')
    for req in audit['requirements']:
        name = req['requirement']
        if 'LM frontend' in name:
            req['state'] = frontend
            req['evidence'] += ['verification/game-native-runtime-review.json', 'verification/advertising-native-32k-review.json', 'START HERE.txt']
        elif 'Black Ice' in name:
            req['state'] = decomp
            req['evidence'] += [str(S / 'emulator-runtime/capture-review.json'), str(S / 'emulator-runtime/pc-observer-summary.json'), 'verification/biwn-record4-checks.json']
        elif 'Multiagent game' in name:
            req['state'] = 'Native Chat retrieves evidence/displays roles. Separate-context advanced workflow retained. Same-model routine draft failed; CPU-checked corrections visible. No autonomous end-to-end pass.'
            req['evidence'] += ['verification/game-native-runtime-review.json']
        elif 'Advertising research' in name:
            req['state'] = 'Saved named Chat passed five-turn32k source-grounded test. Supervised drafting; numeric/causal/length errors remain. Same-model roles exercised; no weight adapter trained.'
            req['evidence'] += ['verification/advertising-native-32k-review.json']
    save(V / 'requirements-audit.json', audit)
    (R / 'START HERE.txt').write_text('''LOCAL AI — DAILY USE

1. Open LM Studio.
2. Choose Game Assistant — BIWN or Advertising Assistant — Research & Teaching from Chats.
3. Click Reload last used model if needed, then ask normally.

Examples:
  Where are we with Black Ice White Noise?
  How many bytes does the boot loader copy, and where?
  Using Lee & Koo (2016), was involvement measured or manipulated?
  Make a short classroom activity based on that paper.

The assistant gathers saved project evidence or sources automatically. Expand tool calls to inspect evidence. Prompts, responses and specialist roles stay in Chat; no report-pasting or manual role assignment needed.

Both chats tested with local27B model at32k context, one worker, roughly20–21tokens/sec. Advertising completed five turns without overflow. Supervised use: generated code, statistics, causal wording and word limits still need checking. Roles share one model/context and are not independent verification.

Original BIWN showed character/street/HUD and responded to controller inputs in an assisted emulator. Five portable C components checked; full reconstructed game and improved trained default remain in progress. Larger coding candidate retained for future evaluation after this Mac resource guard rejected its load.

Exact prompts/responses and quality reviews: verification/transcripts and verification/*native*review.json.
''')
    event = {'time': NOW, 'actor': 'Codex coordinator, native LM Studio27B model and deterministic CPU/file tools; no Codex subagents',
             'action': 'Complete visible Chat tests after unlock; record emulator mapping/input/PC observations and fifth portable component',
             'game_prompts_and_responses': str(transcript),
             'advertising_prompts_and_responses': str(V / 'transcripts/advertising-native-32k-20261012.md'),
             'model_draft_promoted': False, 'results': decomp,
             'development_failures': ['Initial visual-probe make implicit shared-link failed; documented explicit C99 compile succeeded.',
                                      'Native model draft failed capacity, signed guard, argument order and upper D0 behavior; rejected/corrected visibly.'],
             'full_goal': 'active incomplete'}
    with (S / 'activity.jsonl').open('a') as f:
        f.write(json.dumps(event) + '\n')
    with (S / 'workflow.txt').open('a') as f:
        f.write('\n\n' + NOW + ' — CURRENT CHECKPOINT (supersedes earlier pending-unlock/static-mapping notes)\n' + frontend + '\n' + decomp + '\nExact native prompts/responses: ' + str(transcript) + '\nTraining and full restoration remain incomplete.\n')
    print(json.dumps({'status': 'reconciled', 'backup': str(BACKUP), 'native_user_turns': len(turns), 'portable_components': 5}))


if __name__ == '__main__':
    main()
