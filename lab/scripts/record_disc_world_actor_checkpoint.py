"""Record verified world/actor connection and failed ordinary-model scope samples."""
import hashlib,json,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def samples(protocol):
    rows=[]
    for q in protocol['questions']:
        calls=[c['toolCallRequest']for e in q['events']for c in e['content']if c['type']=='toolCallRequest']
        answer='\n'.join(c['text'].strip()for e in q['events']for c in e['content']if c['type']=='text'and c['text'].strip())
        rows.append({'question':q['user'],'answer':answer,'word_count':len(answer.split()),'tool_calls':calls,'SDK_reported_seconds':q['SDK_reported_seconds']})
    return rows
def main():
    now=datetime.now(timezone.utc).isoformat();names=['biwn-world-cpu-checks.json','biwn-world-input-cpu-checks.json','biwn-disc-world-actors-checks.json'];proofs={n:read(ROOT/'verification'/n)for n in names};world,inputs,linked=proofs.values()
    assert world['CPU_cases']==inputs['CPU_cases']==1035 and linked['task_handoffs']==2576 and linked['world_updates']==512
    source=ROOT/'projects/black-ice-white-noise/restoration'
    for proof in proofs.values():
        assert read(Path(proof['directory'])/'status.json')['status']=='terminal_pass'
        for n,h in proof['source_sha256'].items():assert hashlib.sha256((source/n).read_bytes()).hexdigest()==h
    mcp=read(ROOT/'verification/disc-world-actor-MCP-check.json');assert mcp['status']=='fresh_installed_world_actor_timing_evidence_passed'
    first_path=ROOT/'verification/easy-disc-world-actors/20261013T193140.242679Z/protocol.json'
    revised_path=ROOT/'verification/easy-disc-world-actors/20261013T193435.443838Z/protocol.json'
    coder_path=ROOT/'verification/easy-disc-world-coder/20261013T193638.013202Z/protocol.json'
    first,revised,coder=[read(p)for p in [first_path,revised_path,coder_path]]
    assert all(p['status']=='completed_pending_coordinator_review'for p in [first,revised,coder])and coder['everyday_model_restored']
    base_samples=samples(first);revised_samples=samples(revised);coder_samples=samples(coder)
    assert len(base_samples)==len(coder_samples)==2 and len(revised_samples)==1
    assert all(len(s['tool_calls'])==1 for group in [base_samples,revised_samples,coder_samples]for s in group)
    base_samples[0].update(verdict='incomplete_rejected',reason='Correct timestep source, but omitted all seven remaining world helper scripts, including four executed scripts.')
    base_samples[1].update(verdict='bounded_evidence_review_correct',reason='Copied negative/upper clock examples and signed-only upper clamp correctly; identified seven world helper scripts and controlled-input/device/fullgame limits. Same-model Analyst/Reviewer roles are not independent verification.')
    revised_samples[0].update(verdict='incomplete_rejected',reason='After prompt and tool-list refinement, named three unreached scripts but still omitted four reached world-helper scripts.')
    coder_samples[0].update(verdict='factual_and_format_failure_rejected',reason='Incorrectly called disc-loaded scene geometry synthetic and stated real actor bodies were not C implementations;149words exceeds under100. Retrieved actor_movement with historical proofs despite current fields.')
    coder_samples[1].update(verdict='scope_and_format_incomplete_rejected',reason='Correct signed-clock arithmetic, but omitted world-helper scripts and used115words rather than under110.')
    models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True))
    assert len(models)==1 and models[0]['identifier']=='advertising-scholar'and models[0]['contextLength']==32768 and models[0]['status']=='idle'and models[0]['queued']==0
    native_path=Path.home()/'.lmstudio/conversations/1791918561154.conversation.json';native=read(native_path)
    assert len(native['messages'])==2 and native['name']=='Game Assistant — Disc Scene Checkpoint'
    native_preset_path=Path.home()/'.lmstudio/config-presets/Game Assistant (2).preset.json';native_preset=read(native_preset_path)
    native_system=next(f['value']for f in native_preset['operation']['fields']if f['key']=='llm.prediction.systemPrompt')
    current_system=(ROOT/'presets/Game Assistant.system.txt').read_text().strip()
    native_updated=native_system.strip()==current_system
    audit=ROOT/'verification/disc-world-actor-review'/Path(linked['directory']).name;audit.mkdir(parents=True,exist_ok=True)
    for path,name in [(first_path,'base-original-SDK.json'),(revised_path,'base-revised-SDK.json'),(coder_path,'coder-SDK.json'),(native_path,'native-history-read-only.json'),(native_preset_path,'native-preset-read-only.json')]:shutil.copy2(path,audit/name)
    who=('Codex authored the new complete CPU world/digit and input-poll interfaces, comparison harnesses and world-to-actor task-ring integration. Original pinned CPU/GPU execution decides acceptance. '
         'Existing actor/navigation/RNG/movement/collision/geometry/scheduler/GPU bodies are reused. No local-model code was accepted this turn. '
         'The everyday27Bbase answered two SDK questions, then one revised ordinary question; the installed30B-A3Bcoding model answered the same two questions in separate contexts. '
         'Both ordinary base answers are incomplete and rejected; base signed-clock role review is correct within its evidence scope. Both coding samples are rejected for facts/scope/length. '
         'Analyst/Reviewer labels within one response use the same model and are not independent verification. No new training or default promotion. Everyday27Bbase is restored,32k/oneworker/idle. '
         'API/SDK logs are separate from native Chat. Native history/preset files were only read/copied, never injected or edited.')
    corrections=['Initial1024fullCPUcaller cases allmatchedCPU/RAM/bus, but digit instructioncoverage wasincomplete. Added ten singledigit fixtures and one controlled inputreread; final1035cases coverall281caller/digit instructions. No Cbehavior fix wasneeded.',
                 'Realinput extension adds all32E4C0instructions, actualpinnedjoystickrows,1317polls/5268reads; full1035cases coverall313instructions. Clock/buttons remainexternalinputs; no physicalcontrollerclaim.',
                 'Connected actualworldtask/fullCPUcaller/inputpoll andworldGPUmath withtwodisc-sceneactors/twoidles. Actualworld nowwrites sharedtimestep; externalclockincrementsreplace prior directtimestepfixtures. Seven worldhelperscriptsconfigured,fourreached; noneactorhelper.',
                 'CUAgetApp initiallytimedout120seconds, inventorytimedout20seconds/reset; thirdgetAppsucceeded. Latercontrolactionsdidnotproduceconsistentvisiblechange andonehiddenelementreportednoFrame. Inspection/screenshotworked. No screenlockwasconfirmed andnounlockrequested. Current native prompt/provider adoption and new answers remainunverified.',
                 'Afterbaseordinaryansweromittedscripts, added explicitremaining-scriptlist tofocusedtoolandpromptinstructiontoincludeconfigured/reachedhelperbodies. RevisedSDKanswerstillomittedfourreachedscripts; rejectedratherthanclaimedfixed.',
                 'CodingweightscomparisonwasfasteronreportedSDKsamplesbutansweredincorrectly/overlength. Differenttoolchoices/outputlengths/cachemeanthisisnotageneral speed/qualityranking. Base restoredaftercomparison.']
    review={'recorded_at':now,'status':'code_connection_passed_local_scope_answers_have_rejected_failures','who_did_what':who,
            'base_original':base_samples,'base_revised':revised_samples,'coding_model':coder_samples,
            'native_UI':'Inspection recovered, input controls unreliable; no new native generation verified. Saved history retains previous host-timestep checkpoint.',
            'native_prompt_matches_latest_root':native_updated,'native_new_world_scope_verified':False,
            'model_default_promoted':False,'everyday_model_restored':True,'corrections':corrections,'directory':str(audit),
            'scope':'Bounded project evidence/role questions through localhost SDK. Typed MCP facts and original CPU/GPU checks pass; prose failures are retained. Not general model ranking, independent review, new training or fullgame completion.'}
    save(audit/'review.json',review);save(ROOT/'verification/disc-world-actor-review.json',review)
    transcript='WORLD GENERATES ACTOR TIMING — CHECKPOINT\n\nWHO DID WHAT\n'+who+'\n\nCORRECTIONS / LIMITS\n'+'\n'.join(corrections)
    for label,protocol in [('BASE ORIGINAL',first),('BASE REVISED',revised),('CODING MODEL',coder)]:transcript+='\n\n'+label+' — EXACT SYSTEM / USER / TOOL / RESPONSES\n'+json.dumps(protocol,ensure_ascii=False,indent=2)
    transcript+='\n\nCOORDINATOR RESPONSE VERDICTS\n'+json.dumps({'base_original':base_samples,'base_revised':revised_samples,'coder':coder_samples},ensure_ascii=False,indent=2)
    transcript+='\n\nCURRENT CODE SCOPE\n'+read(ROOT/'config.json')['disc_world_actor_progress']+'\nFull goal active and incomplete.\n'
    (audit/'prompts-and-responses.txt').write_text(transcript)
    evidence=['verification/'+n for n in names]+['verification/disc-world-actor-MCP-check.json','verification/disc-world-actor-review.json',str((audit/'prompts-and-responses.txt').relative_to(ROOT))]
    checkpoint={'recorded_at':now,'published_components':106,'processor_components':{'CPU':104,'GPU':2},'new_components':0,
                'world_fullCPU_cases':1035,'world_digit_instruction_coverage':[281,281],'world_host_guards':23,
                'real_input_fullCPU_cases':1035,'world_digit_input_instruction_coverage':[313,313],'input_poll_calls':1317,'raw_pad_reads':5268,
                'combined_disc_scene_cases':16,'world_updates':512,'actor_iterations':1024,'task_handoffs':2576,
                'world_generates_actor_timestep':True,'timestep_directly_scripted':False,'world_helper_scripts_configured':7,'world_helper_scripts_reached':4,'actor_helper_scripts':0,
                'world_and_actor_GPU_math_real':True,'original_GPU_submit_entries':1536,'completeCPU_2MBRAM_privateframes_compared':True,
                'preserved_contexts':21,'runnable_contexts':5,'blocked_contexts':16,'phased_Cstartup_bridge':True,'synchronous_GPU_completion':True,
                'external_clock_button_inputs':True,'synthetic_geometry_replacement':False,'actual_scene_removal_reuse_stimulated':False,
                'base_ordinary_answers_incomplete_rejected':2,'base_signed_clock_role_review_correct':1,'coding_samples_rejected':2,
                'native_new_world_scope_verified':False,'native_prompt_update_pending':not native_updated,'model_idle':True,'known_compute_jobs':'terminal','new_training':False,'model_defaults_unchanged':True,'full_goal_status':'active incomplete','evidence':evidence,
                'next_work':'Replace reached world helper scripts with fullCPU interfaces, beginning input dispatch/camera/animation/targeting, and connect real boundary yields/render/loading/remaining tasks. Continue local model scope-completeness evaluation; verify latest prompt/provider and answers in native Chat when controls work.'}
    save(ROOT/'verification/disc-world-actor-checkpoint.json',checkpoint)
    for name in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']:
        path=ROOT/'verification'/name;value=read(path);value.update(disc_world_actor_checkpoint=checkpoint,disc_world_actor_review=review)
        if name=='current-runtime-state.json':value.update(recorded_at=now,models=models,local_inference_jobs='Terminal: two ordinary base answers incomplete/rejected; bounded signed-clock roles correct; two coding samples rejected. Everyday base restored/idle. Native new world-scope generation unverified.',emulator_jobs='Terminal:1035fullworldCPU,1035realinputCPU,16world/actorcases with512updates/2576handoffs passed.',latest_API_ease_review=str(ROOT/'verification/disc-world-actor-review.json'))
        if name=='requirements-audit.json':
            value.update(recorded_at_utc=now,previous_goal_turn_classification='Progress: actualdiscscene/twoactors,16cases/2064handoffs;timeinputdirect;freshnativeChatverified.',this_goal_turn_classification='Progress: completeworld/inputfullCPUproofs andactualworld-generatedactortimingconnected,512worldupdates/2576handoffs;sevenworldscriptsremain. Localmodelscopefailuresdocumented;UIinputunreliable,fullgoalactive.',next_safe_work=checkpoint['next_work'])
            for item in value['requirements']:
                if 'decompilation test'in item['requirement']:item['evidence']=list(dict.fromkeys(item['evidence']+evidence))
        save(path,value)
    note='\nWORLD / ACTOR TIMING CHECKPOINT — '+now+'\n\n'+read(ROOT/'config.json')['disc_world_actor_progress']+'\n\nWHO DID WHAT\n'+who+'\n\nMODEL REVIEW\nTwo ordinarybaseanswers incomplete/rejected; bounded signedclockreviewcorrect. Codingcomparison2samplesrejected; everydaybase restored/idle. Nativeupdatedprompt/provider/newresponsependingbecauseinputcontrols unreliable.\n\nEXACT PROMPTS / TOOLS / RESPONSES / CORRECTIONS\n'+str(audit/'prompts-and-responses.txt')+'\n\nNEXT\n'+checkpoint['next_work']+'\nFull goal active and incomplete.\n'
    for name in ['POST REVIEW.txt','projects/black-ice-white-noise/restoration/READ ME.txt','CURRENT DECOMPILATION.txt']:
        with(ROOT/name).open('a')as handle:handle.write(note)
    path=ROOT/'START HERE.txt';text=path.read_text();a=text.index('LOCAL INFERENCE RESULT\n');b=text.index('TRY ADVERTISING ASSISTANT\n',a)
    text=text[:a]+('LOCAL INFERENCE RESULT\nGame Assistant — Disc Scene Checkpoint retains the previous verified native scene question. The newest world-timing evidence is installed in the backend, but current native prompt/provider adoption and a new response remain unverified because UI input controls were unreliable. API/SDK transcripts are saved separately. Two ordinarybaseanswers omitted important world scripts and are rejected; the signed-clock role review was correct. Two coding-model samples failed scope/facts/length. Everydaybase was restored. No new default promotion or training.\n\nTry: Does the world now supply actors\' movement time, and which world helpers still use scripts? Check the tool result if the answer omits helpers.\n\n')+text[b:];path.write_text(text)
    print(json.dumps({'components':106,'world_updates':512,'handoffs':2576,'model_scope_failures_retained':4,'base_restored_idle':True,'native_update_verified':False,'audit':str(audit)}))
if __name__=='__main__':main()
