"""Preserve this checkpoint and refresh scoped current evidence; no inference jobs."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent.parent


def read(path):
    return json.loads(path.read_text())


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    now = datetime.now(timezone.utc).isoformat()
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    backup = ROOT / 'config-backups' / stamp / 'gpu-command-checkpoint'
    backup.mkdir(parents=True)
    session = Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    checks = read(ROOT/'verification/biwn-gpu-commands-checks.json')
    assert checks['status'] == 'CPU_protocol_and_portable_C_match_scripted_bus'
    assert (checks['completed_CPU_cases'], checks['host_guard_cases']) == (528, 13)
    native = read(ROOT/'verification/native-chat-fixture-review.json')
    loss = read(ROOT/'verification/advertising-pilot-package-loss.json')
    assert native['tool_result']['final_registers']['D0'] == '0xffffffff'
    assert loss['within_frozen_tolerance']
    paths = ['POST REVIEW.txt', 'START HERE.txt', 'config.json',
             'verification/setup-status.json', 'verification/current-runtime-state.json',
             'verification/requirements-audit.json', 'verification/everyday-inference.json',
             'verification/biwn-gpu-command-local-review.json', 'corpus/game/project-intake.json',
             'projects/black-ice-white-noise/restoration/READ ME.txt']
    for name in paths:
        dest = backup/name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT/name, dest)
    shutil.copy2(session/'boot-slice-validation.json', backup/'boot-slice-validation.json')
    review_path = ROOT/'verification/biwn-gpu-command-local-review.json'
    review = read(review_path)
    for role in review['roles']:
        role['word_count'] = len(role['text'].split())
        role['under_200_words'] = role['word_count'] < 200
    review.update(status='coordinator_reviewed_translation_contract_rejected', recorded_at=now,
                  decisions=['All three roles omit the final E098 wait from both submit contracts. Reject those proposed contracts; coordinator C includes the final wait.',
                             'Accept only supported observations: initial zero poll, ordered writes/dynamic reads, unequal acknowledgement can be nonzero, host budget is additional behavior.',
                             'All three responses exceed the requested under200word limit. Reviewer closely repeats restorer; separate contexts do not provide independent verification.',
                             'Drafts were static analysis before CPU comparison; their no-execution wording does not describe the later coordinator tests.'],
                  checked_implementation=str(ROOT/'projects/black-ice-white-noise/restoration/biwn_gpu_commands.c'),
                  CPU_comparison=str(ROOT/'verification/biwn-gpu-commands-checks.json'))
    save(review_path, review)
    save(ROOT/'verification/biwn-gpu-command-test-iterations.json', {
        'recorded_at': now, 'iterations': [
            {'directory': str(ROOT/'verification/biwn-gpu-commands/20261013T023946.431166Z'), 'result': '528 CPU cases passed; guard mislabeled post_failure actually failed initial poll. Do not use as post-poll coverage.'},
            {'directory': str(ROOT/'verification/biwn-gpu-commands/20261013T024012.945157Z'), 'result': 'Failed guard after phase correction: read budget2 exhausted before post callback, yielding READ_LIMIT rather than expected BUS_ERROR. Partial outputs retained.'},
            {'directory': checks['directory'], 'result': 'Corrected post_failure budget128 and asserted post phase, one ack read and five writes. All528 CPU comparisons and13host guards passed.'}],
        'validator_sha256': hashlib.sha256((ROOT/'scripts/check_biwn_gpu_commands.py').read_bytes()).hexdigest()})
    validation = read(session/'boot-slice-validation.json')
    validation.update(portable_C_component_count=10,
                      component_count_scope='Seven earlier isolated components plus wait-idle and two GPU-command CPU protocols; no whole-game equivalence.',
                      nextstage_GPU_command_C=checks,
                      latest_aggregate_update=now)
    save(session/'boot-slice-validation.json', validation)
    game = ('Ten isolated portable C components checked. New wait-idle and two GPU-command CPU protocols match528 original68000/scripted-bus fixtures and13host guards. Both submit routines preserve the final wait; actual GPU command completion/purpose, CCR and full-game integration remain unverified. Separate approximate Ghidra export has18225instructions and206entry candidates. Controlled assisted-BIOS GPU stack experiment reaches character/street/HUD with input response; this is a guest-state experiment, not a hardware/core fix. Game audio remains silent; complete reconstruction remains unfinished.')
    frontend = ('Two saved native32k chats use the existing27B model. Updated Game Assistant preset and all four tools observed active in nativeUI. One ordinary CPU-fixture question completed with one tool call and correct D0=ffffffff; final answer verified in app-saved conversation after screen locked. Long-history turn39.916seconds, first token33.481seconds. Fresh-chat timing, updated advertising preset adoption and experimental candidate nativeUI test remain pending. API work while locked is authorized and saved separately from native Chat history.')
    package = ('Packaging fidelity check completed on three frozen held-out paper examples: adapter loss1.343908, hybrid1.343177; absolute difference0.000731 within prior0.01 tolerance. Numerical preservation only; generated-answer errors remain and no default promotion.')
    models = json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'), 'ps', '--json'], cwd=Path.home()/'.lmstudio', text=True))
    for name in ['setup-status.json', 'current-runtime-state.json', 'everyday-inference.json', 'requirements-audit.json']:
        path = ROOT/'verification'/name
        value = read(path)
        if name == 'setup-status.json':
            value.update(updated_at_utc=now, game_work=game, frontend=frontend,
                         pending='Full goal active and incomplete: whole-game reconstruction/game audio, improved trained defaults, broader advertising evaluation, fresh-chat timing and advertising nativeUI checks remain outstanding.',
                         advertising_package_fidelity=package)
        elif name == 'current-runtime-state.json':
            value.update(recorded_at=now, models=models, model_state_refreshed_at=now,
                         local_inference_jobs='All known jobs terminal: advertising package-loss check and three local GPU-command role passes completed. No background inference/training job claimed.',
                         ghidra_jobs='All logged jobs terminal; ten isolated portable components checked; approximate exports remain unverified.',
                         visible_chat=frontend, decomp_progress=game,
                         MCP_updated_evidence='Ten isolated components, GPU-command CPU comparisons and controlled stack summary refreshed; native game four-tool activation observed.',
                         advertising_package_fidelity=package)
        elif name == 'everyday-inference.json':
            value.update(updated_at=now, frontend=frontend, model=models, model_state_refreshed_at=now,
                         latest_native_fixture_review=str(ROOT/'verification/native-chat-fixture-review.json'),
                         latest_advertising_package_loss=str(ROOT/'verification/advertising-pilot-package-loss.json'))
            value['limitations'] = [x.replace(' or advertising adapter trained', '') for x in value['limitations']]
        else:
            value.update(recorded_at_utc=now,
                         previous_goal_turn_classification=value['this_goal_turn_classification'],
                         this_goal_turn_classification='progress: native game tool activation and saved fixture completion, advertising package loss fidelity, three checked CPU protocols and rejected correlated local-role contracts')
            for item in value['requirements']:
                title=item['requirement']
                if 'Configure LM frontend' in title:
                    item['state']=frontend
                    item['evidence'].append('verification/native-chat-fixture-review.json')
                elif 'decompilation test' in title:
                    item['state']=game
                    item['evidence'] += ['verification/biwn-gpu-commands-checks.json','verification/biwn-gpu-command-local-review.json']
                elif 'Advertising research' in title:
                    item['state'] += ' '+package
                    item['evidence'].append('verification/advertising-pilot-package-loss.json')
        save(path,value)
    config = read(ROOT/'config.json')
    config['chat_frontend']['game']['status']=frontend+' '+game
    save(ROOT/'config.json',config)
    intake = read(ROOT/'corpus/game/project-intake.json')
    intake['latest_checked_status'] = game
    intake['latest_checked_at'] = now
    intake['latest_GPU_command_check'] = checks
    save(ROOT/'corpus/game/project-intake.json',intake)
    guide = ROOT/'START HERE.txt'
    text = guide.read_text().replace('seven isolated', 'ten isolated')
    text = text.replace('Updated preset/tool activation still requires a nativeUI check; the API guard has not been proved in nativeChat.', 'Updated Game Assistant preset and all four tools were observed active in native Chat. One CPU fixture returned the correct answer with one tool call; the long-history turn took about40seconds. Fresh-chat timing and updated advertising preset/candidate UI checks remain pending. The API guard has not been proved generally in native Chat.')
    guide.write_text(text)
    restore = ROOT/'projects/black-ice-white-noise/restoration/READ ME.txt'
    restore.write_text(restore.read_text()+'\nGPU COMMAND CPU PROTOCOLS — '+now+'\nbiwn_gpu_commands.c/.h add three isolated components: wait for F03200==0; submit4D80; submit6AE0. Both submit routines preserve ordered writes, unequal-command acknowledgement (possibly nonzero), and final F03200==0 wait.528 CPU scripted-bus fixtures and13host guards pass. Every read consumes the added host budget; callback failures retain prior writes. No original timeout, D0 return, GPU command purpose/completion or full-game equivalence is inferred. Reproduce: .venv/bin/python scripts/check_biwn_gpu_commands.py. See verification/biwn-gpu-commands-checks.json. Total checked isolated components:10.\n')
    post=ROOT/'POST REVIEW.txt'
    text=post.read_text().replace('Updated preset/MCP activation remains untested in nativeUI.', 'Historical checkpoint: native activation was pending; later native fixture result below supersedes this.')
    text=text.replace('Activate/test four tools in nativeChat when UI available.', 'Game four-tool activation completed below; fresh-chat and advertising UI checks remain.')
    text=text.replace('verify experimental package fusion loss;', 'experimental package fusion loss completed below;')
    text+='\nCPU PROTOCOL / NATIVE CHAT / PACKAGE CHECKPOINT — '+now+'\n'+game+'\n'+frontend+'\n'+package+'\nWHO DID WHAT: Codex wrote the callback-based C translation and CPU comparison harness, corrected two test-guard mistakes, reviewed exact bus traces and rejected all three incomplete local-role contracts. Actual local analyst→restorer→reviewer used separate contexts on the same27B weights, each omitted the final wait and exceeded200words; reviewer repeated restorer. No Codex subagents.\nExact local-role prompts/responses: '+str(Path(review['directory'])/'prompts-and-responses.txt')+'\nNative Chat prompt/tool/answer: '+str(Path(native['conversation_snapshot']).parent/'prompts-and-responses.txt')+'\nLocal-role coordinator review: '+str(review_path)+'\nCPU checks: '+str(ROOT/'verification/biwn-gpu-commands-checks.json')+'\nFailed test iterations: '+str(ROOT/'verification/biwn-gpu-command-test-iterations.json')+'\nPackage loss: '+str(ROOT/'verification/advertising-pilot-package-loss.json')+'\nNext: broader source-grounded advertising quality tests; original GPU stack provenance/game audio; continued checked CPU reconstruction; fresh native Chat timing and advertising preset/candidate UI checks when available. All known compute jobs terminal at this checkpoint; full goal remains active and incomplete.\n'
    post.write_text(text)
    save(ROOT/'verification/gpu-command-checkpoint.json', {'recorded_at':now,'backup':str(backup),'models':models,'full_goal_status':'active incomplete','known_compute_jobs':'terminal','CPU_components':10,'package_fidelity':package,'native_fixture':str(ROOT/'verification/native-chat-fixture-review.json')})
    print(json.dumps({'checkpoint':now,'CPU_components':10,'model_status':[m.get('status') for m in models],'backup':str(backup)}))


if __name__ == '__main__':
    main()
