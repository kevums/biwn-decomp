"""Audit completed original/C lifecycle proof and visible native inference."""
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
read = lambda p: json.loads(p.read_text())
def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def main():
    now = datetime.now(timezone.utc).isoformat()
    names = ['biwn-task-removal-checks.json','biwn-actor-lifecycle-runtime-checks.json',
             'biwn-scheduler-checks.json','biwn-actor-full-movement-runtime-checks.json']
    proofs = {n:read(ROOT / 'verification' / n) for n in names}
    removal, lifecycle, scheduler, actor = proofs.values()
    assert removal['native_CPU_cases'] == 1024 and removal['CPU_instruction_coverage'] == [29,29]
    assert lifecycle['cases'] == 256 and lifecycle['task_handoffs'] == 3840
    assert scheduler['native_CPU_cases'] == 512 and actor['helper_return_CPU_comparisons_total'] == 2671
    source = ROOT / 'projects/black-ice-white-noise/restoration'
    for proof in proofs.values():
        assert read(Path(proof['directory']) / 'status.json')['status'] == 'terminal_pass'
        for name,digest in proof['source_sha256'].items():
            assert hashlib.sha256((source / name).read_bytes()).hexdigest() == digest
    mcp = read(ROOT / 'verification/actor-lifecycle-MCP-check.json')
    assert mcp['status'] == 'fresh_installed_lifecycle_evidence_passed'
    native_path = Path.home() / '.lmstudio/conversations/1791916630539.conversation.json'
    native = read(native_path)
    preset_path = Path.home() / '.lmstudio/config-presets/Game Assistant (2).preset.json'
    preset = read(preset_path)
    system = next(f['value'] for f in preset['operation']['fields'] if f['key'] == 'llm.prediction.systemPrompt')
    assert system.strip() == (ROOT / 'presets/Game Assistant.system.txt').read_text().strip()
    assert native['name'] == 'Game Assistant — Live Actor Checkpoint' and native['preset'] == '@local:game-assistant-2'
    assert len(native['messages']) == 6
    user_version = native['messages'][-2]['versions'][native['messages'][-2]['currentlySelected']]
    user = '\n'.join(c['text'] for c in user_version['content'] if c['type'] == 'text')
    version = native['messages'][-1]['versions'][native['messages'][-1]['currentlySelected']]
    blocks = [c for s in version['steps'] for c in s.get('content',[])]
    calls = [c for c in blocks if c['type'] == 'toolCallRequest']
    results = [c for c in blocks if c['type'] == 'toolCallResult']
    answer = '\n'.join(c['text'] for c in blocks if c['type'] == 'text')
    stats = [s['genInfo']['stats'] for s in version['steps'] if 'genInfo' in s]
    assert len(calls) == len(results) == 1 and calls[0]['name'] == 'project_evidence'
    assert calls[0]['parameters']['topic'] in ['actor_task','task_removal']
    assert all(t in results[0]['content'] for t in ['3840','106','context_reuses'])
    assert all(s['stopReason'] == 'eosFound' for s in stats)
    assert all(t in answer for t in ['256','3,840','boundary-checked only','not rebuilt','blocked','F360'])
    assert len(answer.split()) < 95
    models = json.loads(subprocess.check_output([str(Path.home() / '.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home() / '.lmstudio',text=True))
    assert len(models) == 1 and models[0]['identifier'] == 'advertising-scholar' and models[0]['status'] == 'idle' and models[0]['queued'] == 0
    audit = ROOT / 'verification/actor-lifecycle-review' / Path(lifecycle['directory']).name
    audit.mkdir(parents=True,exist_ok=True)
    shutil.copy2(native_path,audit / 'native-conversation.json')
    shutil.copy2(preset_path,audit / 'native-preset.json')
    who = ('Codex authored the C task-removal implementation and native/C comparison harnesses, refactored the shared scheduler, and connected the actor removal/reuse test. '
           'The original pinned CPU/GPU decides code acceptance. Existing actor/navigation/movement/collision/geometry/RNG/GPU/creation routines are reused. '
           'The local27Bbase model answered one genuine native Chat question using one evidence call; it did not author accepted C this turn. Earlier visible Analyst/Reviewer turns remain same-model correlated roles, not independent agents. '
           'No new training or model-default promotion. Native Chat was operated only through the UI; its saved conversation is read/copied for audit and never injected or edited.')
    corrections = [
        'Initial new test script had a missing bracket; fixed before any native comparison ran. All subsequent preflight/full removal checks passed.',
        'Extended the lifecycle proof to execute the reused idle body and corrected the F57C assertion to check only execution after TRAP2; F57C legitimately occurs in earlier regular iterations. Final256-case run passes with3840handoffs.',
        'Initial MCP check found a mismatched field name host_guards versus actor-boundary host_guard_checks. Corrected the adapter and reran allnineinstalledtopics successfully; no C behavior changed.',
        'Corrected task counting: captured21contexts contain20distinctentryaddresses. Five implemented entrybodies cover six contexts becauseF4D8 occurs twice. Fifteen entries/contexts remain; actors still blocked in startup.',
        'Native systemPrompt setValue was rejected and the first paste did not apply. Rebound window, verified focus, pasted and saved throughUI; saved native preset matches root exactly. Reconnected provider and verified current106/3840evidence in actualnativecall.']
    review = {'recorded_at':now,'status':'native_lifecycle_update_answer_correct_one_evidence_call',
              'who_did_what':who,'question':user,'answer':answer,'tool_calls':calls,'native_generation_stats':stats,
              'native_UI_visible_final_verified':True,'native_chat':native['name'],'native_preset':native['preset'],
              'native_conversation_path':str(native_path),'native_conversation_sha256':hashlib.sha256(native_path.read_bytes()).hexdigest(),
              'corrections':corrections,'directory':str(audit),
              'scope':'One ordinary evidence-grounded native sample with existing history. Per-generation statistics are not measured end-to-end latency or general accuracy. Code acceptance comes from original CPU/GPU comparisons.'}
    save(audit / 'review.json',review)
    save(ROOT / 'verification/actor-lifecycle-review.json',review)
    transcript = 'ACTOR LIFECYCLE / NATIVE CHAT CHECKPOINT\n\nWHO DID WHAT\n'+who+'\n\nNATIVE SYSTEM\n'+system+'\n\nLATEST USER\n'+user+'\n\nLATEST RESPONSE\n'+answer
    transcript += '\n\nEXACT NATIVE MESSAGES / TOOLS / RESULTS / GENERATION METADATA\n'+json.dumps(native['messages'],ensure_ascii=False,indent=2)
    transcript += '\n\nCORRECTIONS\n'+'\n'.join(corrections)+'\n\nCURRENT SCOPE\n'+read(ROOT / 'config.json')['actor_lifecycle_progress']+'\nFull goal active and incomplete.\n'
    (audit / 'prompts-and-responses.txt').write_text(transcript)
    evidence = ['verification/'+n for n in names]+['verification/actor-lifecycle-MCP-check.json','verification/actor-lifecycle-review.json',str((audit / 'prompts-and-responses.txt').relative_to(ROOT))]
    checkpoint = {'recorded_at':now,'published_components':106,'processor_components':{'CPU':104,'GPU':2},
                  'new_counted_entries':['0xdeb6','0xdf7a','0xf4d8'],'pending_actor_caller_components':0,
                  'removal_native_CPU_cases':1024,'removal_instruction_coverage':[29,29],'removal_host_guards':23,
                  'scheduler_regression_cases':512,'regular_actor_regression_cases':128,
                  'actor_lifecycle_cases':256,'actor_iterations':1024,'task_handoffs':3840,
                  'actual_actor_removals':256,'context_reuses':256,'reused_idle_body_executions':256,
                  'actor_helper_scripts':0,'complete_RAM_privateframes_and_allCPU_compared':True,
                  'startup_actor_bodies_executed':0,'startup21context_fixture_linked':False,
                  'synthetic_scene_geometry':True,'synchronous_GPU_completion':True,'reused_context_entry':'idleF360; not actor respawn',
                  'task_entry_coverage':read(ROOT / 'verification/actor-lifecycle-checked-examples.json')['task_entry_coverage'],
                  'native_UI':'Current preset/provider and one visible native scope answer verified.',
                  'model_idle':True,'known_compute_jobs':'terminal','new_training':False,'model_defaults_unchanged':True,
                  'full_goal_status':'active incomplete','evidence':evidence,
                  'next_work':'Connect actual actor task bodies with original startup scene/geometry/assets and scheduler, then join compatible world/render task paths, loading continuations and remaining task/game systems.'}
    save(ROOT / 'verification/actor-lifecycle-checkpoint.json',checkpoint)
    for name in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']:
        path = ROOT / 'verification' / name
        value = read(path)
        value.update(actor_lifecycle_checkpoint=checkpoint,actor_lifecycle_review=review)
        if name == 'current-runtime-state.json':
            value.update(recorded_at=now,models=models,local_inference_jobs='Terminal: one native lifecycle update answer passed with one evidence call. Model idle.',emulator_jobs='Terminal: removal1024/lifecycle256/scheduler512/regularactor128comparisons passed.',latest_native_ease_review=str(ROOT / 'verification/actor-lifecycle-review.json'))
        if name == 'requirements-audit.json':
            value.update(recorded_at_utc=now,previous_goal_turn_classification='Progress: connected real actor movement/collision and verified native Chat/roles.',this_goal_turn_classification='Progress: actualTRAP2removal, liveactor exit/contextreuse/idleexecution verified, count106; native ordinary answer updated from oldpendingstatus correctly.',next_safe_work=checkpoint['next_work'])
            for item in value['requirements']:
                if 'decompilation test' in item['requirement']:item['evidence'] = list(dict.fromkeys(item['evidence']+evidence))
        save(path,value)
    note = '\nACTOR LIFECYCLE CHECKPOINT — '+now+'\n\n'+read(ROOT / 'config.json')['actor_lifecycle_progress']+'\n\nWHO DID WHAT\n'+who+'\n\nEXACT PROMPTS / TOOLS / RESPONSES / CORRECTIONS\n'+str(audit / 'prompts-and-responses.txt')+'\n\nNEXT\n'+checkpoint['next_work']+'\nFull goal active and incomplete.\n'
    for name in ['POST REVIEW.txt','projects/black-ice-white-noise/restoration/READ ME.txt','CURRENT DECOMPILATION.txt']:
        with (ROOT / name).open('a') as handle:handle.write(note)
    path = ROOT / 'START HERE.txt'
    text = path.read_text();a = text.index('LOCAL INFERENCE RESULT\n');b = text.index('TRY ADVERTISING ASSISTANT\n',a)
    text = text[:a]+('LOCAL INFERENCE RESULT\nNative Game Assistant — Live Actor Checkpoint now contains a correct removal/context-reuse update with one evidence call, alongside the earlier movement question and Analyst/Reviewer role exchange. Current native preset/provider verified. These evidence-grounded samples are not general unaided accuracy or speed benchmarks.\n\nTry: Can actors now actually exit and reuse a task slot, and is the game rebuilt?\n\n')+text[b:]
    path.write_text(text)
    print(json.dumps({'components':106,'lifecycle_cases':256,'handoffs':3840,'native_answer_correct':True,'model_idle':True,'audit':str(audit)}))

if __name__ == '__main__':
    main()
