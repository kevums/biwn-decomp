"""Record verified polling, emulated-pad integration and rejected local drafts."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[1]

def read(path):
    return json.loads(path.read_text())

def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')

def main():
    now = datetime.now(timezone.utc).isoformat()
    checks = read(ROOT/'verification/biwn-input-poll-checks.json')
    linked = read(ROOT/'verification/biwn-task-input-runtime-checks.json')
    pad = read(ROOT/'verification/emulated-pad-mapping.json')
    drafts = read(ROOT/'verification/local-input-author-audit.json')
    assert checks['CPU_cases'] == 1024 and checks['CPU_instruction_coverage'] == [32,32] and checks['host_guards'] == 15
    assert pad['native_CPU_cases'] == 132 and len(pad['button_to_game_bit']) == 21
    assert linked['cases'] == 256 and linked['input_poll_calls'] == 584 and linked['raw_MMIO_reads'] == 2336
    assert linked['world_update_calls'] == 512 and linked['task_handoffs'] == 1572 and linked['world_inner_yields'] == 12
    assert linked['inventory_redraw_calls'] == 150 and len(linked['remaining_top_level_scripted_helpers']) == 4
    for name, digest in linked['source_sha256'].items():
        assert hashlib.sha256((ROOT/'projects/black-ice-white-noise/restoration'/name).read_bytes()).hexdigest() == digest
    assert drafts['accepted_code_drafts'] == 0 and drafts['reviewer_identical_to_author']
    assert [r['diagnostic_passed'] for r in drafts['roles']] == [0,0,234]
    assert read(ROOT/'verification/input-poll-MCP-check.json')['status'] == 'fresh_installed_input_poll_evidence_passed'
    path = Path(read(ROOT/'verification/easy-input-poll-current.json')['directory'])/'protocol.json'
    ease = read(path)
    assert ease['status'] == 'completed_pending_coordinator_review'
    rows = []
    for i, q in enumerate(ease['questions']):
        calls = [b['toolCallRequest'] for e in q['events'] if e['role']=='assistant' for b in e['content'] if b['type']=='toolCallRequest']
        texts = [b['text'] for e in q['events'] if e['role']=='assistant' for b in e['content'] if b['type']=='text']
        answer = texts[-1].strip()
        assert len(calls)==1 and calls[0]['name']=='project_evidence' and calls[0]['arguments']=={'topic':'input_poll'}
        assert len(answer.split()) <= [60,45,40][i]
        rows.append({'question':q['user'], 'answer':answer, 'seconds':q['SDK_reported_seconds'], 'tool_calls':calls, 'verdict':'matches original execution and explicit validation scope'})
    assert rows[0]['answer'].startswith('No.') and '18' in rows[0]['answer'] and 'four' in rows[0]['answer'].lower()
    assert rows[1]['answer'].startswith('No.') and 'no second' in rows[1]['answer'] and 'new edge' in rows[1]['answer']
    assert '584' in rows[2]['answer'] and '2336' in rows[2]['answer'].replace(',','') and 'not been validated' in rows[2]['answer']
    review = {'recorded_at':now, 'status':'three_plain_input_poll_questions_passed', 'directory':str(path.parent), 'questions':rows,
              'scope':'Local SDK factual answers/tool choice; installed MCP separately checked. Native Chat visual adoption unverified.'}
    save(path.parent/'coordinator-review.json', review)
    save(ROOT/'verification/easy-input-poll-review.json', review)
    models = json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'], cwd=Path.home()/'.lmstudio', text=True))
    assert len(models)==1 and models[0]['identifier']=='advertising-scholar' and models[0]['status']=='idle' and models[0]['contextLength']==32768
    with urllib.request.urlopen('http://127.0.0.1:1234/api/v1/models') as response:
        catalog = json.load(response)
    assert next(x for x in catalog['models'] if x['key']=='local/advertising-qwen38')['capabilities']['reasoning']['default']=='off'
    session = Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    assert read(session/'boot-slice-validation.json')['portable_C_component_count']==43
    game = (
        '43 checked C components: 41 CPU and two GPU. Controller polling is now reconstructed and linked. '
        'Its complete original CPU function matches 1,024 raw-register cases, all 32 instructions and 15 host guards. '
        'Another 132 native original-CPU/C comparisons cover the pinned emulator pad model, all 21 button mappings and press/hold/release/repress behavior. '
        'The connected three-task runtime passes 256 cases: 512 world updates, 1,572 task handoffs, 12 inner boundary yields, 584 polling calls, 2,336 raw row reads and 150 inventory redraw calls. '
        'Polling itself now derives held state and new press edges; it is no longer a return stub. Four other top-level helpers and two scene/texture services remain scripted. '
        'Only three of the 21 captured task bodies are implemented; 18 remain unported, with other game code beyond that captured ring still unfinished. '
        'Private stacks, formatter scratch, world caller-saved ABI and saved SR low-five CCR bits remain excluded in the connected proof. '
        'The pad backend and clock/button samples are test-environment inputs; physical controllers, complete scene/main loop/audio/game and hardware timing remain unverified. No rebuilt full-game frames executed.'
    )
    frontend = (
        'Game Assistant now has current input_poll evidence and a routing rule for held buttons, new press edges and pad-validation scope. '
        'Three ordinary questions used one evidence call each and answered correctly in 7.9–11.5 seconds. '
        'Everyday 27B remains thinking off, 32,768 context, one worker; native Chat visual adoption remains unverified while locked. API exchanges are saved outside native Chat history.'
    )
    quality = (
        'The installed 30B coding model produced Author and Reviewer drafts in 8.81 and 9.24 seconds, using separate contexts on the same weights. The drafts were identical. '
        'Both failed strict compilation. The inspected Author body was compiled with warnings allowed only for diagnosis and failed all 1,024 original-CPU value cases, while passing 15 host-error guards. '
        'One guided Remediator response took 9.47 seconds and fixed MOVEQ sign extension, but still failed strict compilation and 790 of 1,024 value cases. '
        'It left the previous held value in an unused variable rather than using it in the edge calculation. All three drafts were rejected; canonical C remains coordinator-authored. '
        'The Reviewer shares the Author failure result because its body is byte-identical, not because a second independent 1,024-case run occurred. '
        'Warning-only diagnostic builds never qualify for acceptance. This narrow task is not a general model ranking. No new weight training or default promotion occurred; everyday 27B was restored after both coding-model sessions.'
    )
    pending = (
        'Continue reconstructing the input/state dispatcher and remaining terrain/scene/entity and texture/scene-load services, plus the other 18 captured task bodies and other unported game code. '
        'Expand runtime and scene/audio/main-loop behavior and make the verified C path easier to launch through local tools. '
        'Native LM Studio Chat still needs visual verification when accessible. Advertising Source Pilot v1 remains trained, loadable and experimental; everyday base remains default. '
        'Future 256 GB hardware is unbenchmarked. Full goal active and incomplete.'
    )
    evidence = ['verification/biwn-input-poll-checks.json','verification/emulated-pad-mapping.json','verification/biwn-task-input-runtime-checks.json',
                'verification/local-input-author-audit.json','verification/input-poll-MCP-check.json','verification/easy-input-poll-review.json']
    for name in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']:
        target = ROOT/'verification'/name
        data = read(target)
        if name=='setup-status.json':
            data.update(updated_at_utc=now, game_work=game, frontend=frontend, pending=pending, latest_input_model_quality=quality)
        elif name=='current-runtime-state.json':
            data.update(recorded_at=now, models=models, model_state_refreshed_at=now, decomp_progress=game, visible_chat=frontend, MCP_updated_evidence=frontend,
                        local_inference_jobs='Author, Reviewer, one guided Remediator and three ordinary questions terminal. All code drafts rejected. Everyday27B idle; no background inference/training claimed.',
                        emulator_jobs='1,024 raw cases/15 guards,132 emulated-pad cases and256 connected input cases terminal. Strict/diagnostic local draft jobs terminal. Pinned core and old movement/render libraries unchanged.',
                        latest_API_ease_review=str(ROOT/evidence[5]), latest_local_code_review=str(ROOT/evidence[3]))
        elif name=='everyday-inference.json':
            data.update(updated_at=now, model=models, model_state_refreshed_at=now, frontend=frontend, latest_API_ease_review=str(ROOT/evidence[5]), latest_local_code_review=str(ROOT/evidence[3]))
        else:
            data.update(recorded_at_utc=now, previous_goal_turn_classification=data['this_goal_turn_classification'],
                        this_goal_turn_classification='progress: complete controller poll matches1024CPUcases/32instructions;132nativepadcases;584polls/2336rawreads in256connectedcases;three local code drafts rejected;three ordinary answers pass', next_safe_work=pending)
            for item in data['requirements']:
                if 'decompilation test' in item['requirement']:
                    item['state']=game
                    item['evidence']=list(dict.fromkeys(item['evidence']+evidence))
                elif 'Configure LM frontend' in item['requirement']:
                    item['state']=frontend
                    item['evidence']=list(dict.fromkeys(item['evidence']+evidence[4:]))
                elif 'Multiagent game' in item['requirement']:
                    item['state']+=' Actual local Author/Reviewer and one guided Remediator tested. Identical source drafts and partial correction rejected against strict compiler/original execution; no code/default promotion.'
                    item['evidence']=list(dict.fromkeys(item['evidence']+[evidence[3]]))
            data['post_review_evidence'].update({Path(e).name:str(ROOT/e) for e in evidence})
        save(target, data)
    config = read(ROOT/'config.json')
    config['chat_frontend']['game']['status']=game+' '+frontend
    config['models']['game']['latest_code_drafting_probe']=quality
    save(ROOT/'config.json', config)
    intake = read(ROOT/'corpus/game/project-intake.json')
    intake.update(latest_checked_at=now, latest_checked_status=game, latest_input_poll_runtime_check=str(ROOT/evidence[2]))
    save(ROOT/'corpus/game/project-intake.json', intake)
    (ROOT/'CURRENT DECOMPILATION.txt').write_text(
        'BLACK ICE WHITE NOISE — CURRENT RECONSTRUCTION\n\n'+game+'\n\nPOLLING SOURCE\n'+str(ROOT/'projects/black-ice-white-noise/restoration/biwn_input_poll.c')+'\n'+str(ROOT/'projects/black-ice-white-noise/restoration/biwn_input_poll.h')+
        '\n\nEVIDENCE\n'+'\n'.join(str(ROOT/e) for e in evidence)+'\n\nLOCAL CODE GENERATION\n'+quality+'\n\nEASY CHAT\n'+frontend+
        '\n\nApproximate CPU export: 18,306 decoded instructions and 206 entry candidates. Analyst labels are not original symbols. Backend/mapping/integration add no original components; counts imply no completion percentage.\n\n'+pending+'\n')
    (ROOT/'START HERE.txt').write_text(
        'LOCAL AI — DAILY USE\n\n1. Open LM Studio.\n2. Select Game Assistant — Quick Start or Advertising Assistant — Research & Teaching.\n3. Load the last used model if needed and type normally. Expand tool calls to inspect evidence.\n\n'
        'Everyday model: Advertising Qwen38; thinking off, 32,768 context, one worker.\n\nTRY IN GAME ASSISTANT\nShow the rebuilt inventory starting at position 1 with $200.\n'
        'Start at position 9, advance twice and show the resulting inventory panel.\nIf I hold the same button across two polls, is there another new press edge?\nWhere are we with Black Ice White Noise?\n\nCURRENT GAME RESULT\n'+game+
        '\n\nCHAT RESULTS\n'+frontend+'\n\nTRY IN ADVERTISING ASSISTANT\nUsing Lee & Koo (2016), was involvement measured or manipulated?\n'
        'Make a lesson on the involvement scale with an objective, hypothetical example, student question and independently scored answer key.\n\n'
        'Advertising Source Pilot v1 is trained, loadable and experimental; everyday base remains default. See TRY ADVERTISING PILOT.txt.\n\nLOCAL CODING TEST\n'+quality+
        '\n\nAUDIT\nPOST REVIEW.txt links exact prompts, responses, tools, errors and corrections. API work does not automatically appear in native Chat history.\n\n'
        'The verified CDI is internal; current checks do not require the external game drive. Eject it before unplugging.\n')
    target = ROOT/'projects/black-ice-white-noise/restoration/READ ME.txt'
    target.write_text(target.read_text()+'\nCONTROLLER POLLING — '+now+'\n'+game+
                      '\nReproduce: .venv/bin/python scripts/check_biwn_input_poll.py; scripts/check_emulated_pad_poll.py; scripts/check_biwn_task_runtime.py --with-input. '
                      'The ordinary pad mapping is observed from the pinned emulator model, not validated against physical hardware. Clock/button samples are external fixtures.\n')
    target = ROOT/'POST REVIEW.txt'
    target.write_text(target.read_text()+'\nCONTROLLER POLLING / LOCAL CODING ROLES — '+now+'\n'+game+
        '\nWHO DID WHAT: Codex coordinator translated the complete E4C0..E53C polling routine and preserved four ordered 16-bit selector writes/32-bit row reads, OR/rotation masks, old-held read and both 32-bit held/edge stores. '
        '32-case preflight and1,024-case full original-Unicorn run pass, covering all32instructions/15hostguards and alloriginalD/Aregisterpreservation. An initial else2spacing SyntaxError occurred before execution and was repaired. '
        'Codex then bound the existing pinned emulator pad API, tested all21single-button outputs plus combinations, and added an actual native/C press-hold-release-repress sequence.132cases pass; edges are10000000,0,0,10000000. '
        'Raw opaque MMIO can produce mask33ff33ff; the ordinary emulator pad maps to32ff22ff. These are different scopes, not a hardware-accuracy assertion.\n'
        'Codex removed E4C0 from the native task return-stub list and called reconstructed polling in the C callback path. Matching external pad/clock samples precede each actual poll. '
        'Eight-case preflight and256-case full connected run pass, including584polls/2,336rawreads. Old legacy fixtures included unreachablebit31; it is not fabricated by the ordinarypad model. '
        'Real held/edge behavior reduces redraw calls from the historical scripted-input332to150; original/C output still matches exactly under the new inputs. '
        'No core or old native movement/render library edits, no complete gameframes. The report initially retained a historical five-top-level limit sentence; metadata was corrected tofour. '
        'The terminal run harness and input mapping were snapshotted from files with modification times predating the run start.\n'+quality+
        '\nExact Author/Reviewer requests and responses:\n'+drafts['prompts_and_responses'][0]+'\nGuided correction request/response:\n'+drafts['prompts_and_responses'][1]+
        '\nCompiler/diagnostic reports and coordinator verdict:\n'+str(ROOT/evidence[3])+
        '\nThe local draft validator first rejected harmless assembly # immediates inside C comments; the harness guard was corrected to reject actual preprocessor directives. '
        'This was a harness error, not a model formatting fault. Initial drafts were safely inspected before private compilation/execution. '
        'Author/Reviewer both used0xffforMOVEQ#ffinstead ofsignextendedffffffff and did not feed the old-held read intoD0beforeXOR. '
        'Strict compilation failed for unusedstatus/oldheldvariables. A warnings-only diagnostic measured0/1024; the identical Reviewer body shares that result. '
        'The guided correction fixed onlysignextension, returned Markdown fences despite the requested format, and still leftoldheldunused. '
        'Fences were removed only for private diagnostic compilation;234/1024valuespass,15guards pass, strictcompile still fails. No generated body was substituted into canonical C.\n'
        'Latest connected fixtures/handoffs/input samples:\n'+str(Path(linked['directory'])/'fixtures.json')+'\nTerminal-run harness snapshot:\n'+linked['harness_snapshot']+
        '\n'+frontend+'\nExact ordinary prompts/tools/responses:\n'+str(path.parent/'prompts-and-responses.txt')+'\nCoordinator factual review:\n'+str(ROOT/evidence[5])+'\n'+pending+'\n')
    subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts/install_chat_runtime.py')], check=True)
    save(ROOT/'verification/input-poll-checkpoint.json', {
        'recorded_at':now, 'backup':read(ROOT/'verification/input-poll-checkpoint-backup.json')['directory'],
        'components':43, 'CPU_components':41, 'GPU_components':2, 'input_CPU_cases':1024, 'CPU_instruction_coverage':[32,32], 'host_guards':15,
        'emulated_pad_native_cases':132, 'connected_cases':256, 'input_poll_calls':584, 'raw_MMIO_reads':2336, 'world_updates':512, 'task_handoffs':1572,
        'inner_world_yields':12, 'inventory_redraw_calls':150, 'task_subset':[3,21], 'other_tasks_unported':18, 'remaining_top_level_scripted':4, 'remaining_nested_scripted':2,
        'local_code_drafts_accepted':0, 'local_diagnostic_value_passes':[0,0,234], 'local_diagnostic_case_count':1024, 'reviewer_identical_to_author':True,
        'plain_questions_passed':3, 'plain_question_seconds':[round(x['seconds'],1) for x in rows], 'known_compute_jobs':'terminal', 'models':models,
        'reasoning_default':'off', 'full_goal_status':'active incomplete', 'evidence':evidence, 'native_Chat_adoption':'unverified while locked', 'next_work':pending})
    print(json.dumps({'components':43, 'input_cases':1024, 'emulated_pad_cases':132, 'poll_calls':584, 'raw_reads':2336, 'local_code_accepted':0, 'plain_questions_passed':3, 'installed':True}))

if __name__=='__main__':
    main()
