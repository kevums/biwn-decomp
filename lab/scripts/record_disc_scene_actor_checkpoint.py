"""Freeze disc-scene integration and two real native inference samples."""
import hashlib,json,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def native_turn(path):
    chat=read(path);version=chat['messages'][-1]['versions'][chat['messages'][-1]['currentlySelected']]
    blocks=[c for s in version['steps']for c in s.get('content',[])]
    calls=[c for c in blocks if c['type']=='toolCallRequest'];results=[c for c in blocks if c['type']=='toolCallResult']
    text='\n'.join(c['text']for c in blocks if c['type']=='text')
    stats=[s['genInfo']['stats']for s in version['steps']if 'genInfo'in s]
    assert len(calls)==len(results)==1 and calls[0]['name']=='project_evidence'
    assert all(s['stopReason']=='eosFound'for s in stats)and all(t in results[0]['content']for t in ['2064','cases_with_position_change'])
    assert len(text.split())<100 and all(t in text for t in ['2,064','12','0','30','blocked','synchronous'])
    return chat,{'tool_calls':calls,'answer':text,'generation_stats':stats,'word_count':len(text.split()),'native_context_tokens':chat['tokenCount']}

def main():
    now=datetime.now(timezone.utc).isoformat();proof=read(ROOT/'verification/biwn-disc-scene-actors-checks.json');out=Path(proof['directory']);assert read(out/'status.json')['status']=='terminal_pass'
    assert (proof['cases'],proof['actor_iterations'],proof['task_handoffs'],proof['full_helper_return_CPU_comparisons'])==(16,1024,2064,1108)
    assert proof['cases_with_position_change']==12 and proof['original_collision_entry_counts']=={'0x13b5a':40,'0x13bb0':0}
    source=ROOT/'projects/black-ice-white-noise/restoration'
    for name,digest in proof['source_sha256'].items():assert hashlib.sha256((source/name).read_bytes()).hexdigest()==digest
    old_path=Path.home()/'.lmstudio/conversations/1791916630539.conversation.json';fresh_path=Path.home()/'.lmstudio/conversations/1791918561154.conversation.json'
    old,legacy=native_turn(old_path);fresh,focused=native_turn(fresh_path)
    assert legacy['tool_calls'][0]['parameters']=={'topic':'scene_loading'}and focused['tool_calls'][0]['parameters']=={'topic':'actor_scene'}
    assert len(old['messages'])==8 and len(fresh['messages'])==2 and fresh['name']=='Game Assistant — Disc Scene Checkpoint'
    assert fresh['preset']=='@local:game-assistant-2' and fresh['tokenCount']<6500
    preset_path=Path.home()/'.lmstudio/config-presets/Game Assistant (2).preset.json';preset=read(preset_path)
    system=next(f['value']for f in preset['operation']['fields']if f['key']=='llm.prediction.systemPrompt')
    assert system.strip()==(ROOT/'presets/Game Assistant.system.txt').read_text().strip()
    mcp=read(ROOT/'verification/disc-scene-actor-MCP-check.json');assert mcp['status']=='fresh_installed_disc_scene_actor_evidence_passed'
    models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True))
    assert len(models)==1 and models[0]['identifier']=='advertising-scholar'and models[0]['status']=='idle'and models[0]['queued']==0
    audit=ROOT/'verification/disc-scene-actor-review'/out.name;audit.mkdir(parents=True,exist_ok=True)
    for path,name in [(old_path,'native-history.json'),(fresh_path,'native-focused-chat.json'),(preset_path,'native-preset.json')]:shutil.copy2(path,audit/name)
    who=('Codex authored the startup capture and two-actor scene integration harnesses, inspected original opcodes, reviewed all native/C comparisons and added focused actor_scene evidence routing. '
         'Accepted game C bodies are unchanged and reused from earlier checkpoints. Original pinned CPU/GPU execution decides acceptance. '
         'The local27Bbase answered the same ordinary scene question in the existing native history, then in a fresh native chat after the payload/routing change. Both used one tool call and answered correctly. '
         'No local-model code was accepted this turn; no new training/default promotion. Earlier Analyst/Reviewer roles remain correlated same-model roles, not independent code verification. Native conversations were operated through UI and only read/copied for audit.')
    corrections=['First actor bridge incorrectly assumed17DC2wasJSRDF60; source inspection showed MOVE.Lclock,D2 at17DC2thenJSRat17DC8/return17DCE. Corrected C prefix and native interval before a passing comparison. Failed preflight retained.',
                 'First actual-scene baseline matched but did not move: startup clears movementtimestep4C24C. Retainedzero-step baseline and added explicit0/1/8/30hostinputs; twelvepositive-time cases move, with40outdoorcollisionentries. World task remains blocked; its generation of timestep is not claimed.',
                 'Legacy native response wascorrect but history reached86percent context. Addedactor_scene focused payload4257bytesversus11852actor_taskbytes; refreshedprovider andsavedstate-freeprompt. Freshnativequestion selectedactor_sceneautomatically, answeredcorrectly, andendedat17percentcontext. Differenthistory/cachemeansnotacontrolledspeedbenchmark.',
                 'A stale CUA elementindex failed while updatingpreset. Reboundwindow, verifiedfocus, pasted/savedthroughUI andcheckednativepresetexactlymatchesroot. No conversationfileinjection.']
    review={'recorded_at':now,'status':'disc_scene_and_focused_native_answers_correct_one_call_each','who_did_what':who,
            'native_history':legacy,'native_focused_chat':focused,'native_focused_chat_name':fresh['name'],
            'native_focused_chat_path':str(fresh_path),'native_UI_visible_final_verified':True,
            'native_saved_preset_current':True,'focused_payload_bytes':mcp['focused_payload_bytes'],'actor_task_payload_bytes':mcp['actor_task_payload_bytes'],
            'corrections':corrections,'directory':str(audit),'scope':'Bounded evidence-grounded native samples; not unaided accuracy, independent agents, new training, causal performance benchmark or full-game completion.'}
    save(audit/'review.json',review);save(ROOT/'verification/disc-scene-actor-review.json',review)
    transcript='DISC SCENE / EASY NATIVE CHAT CHECKPOINT\n\nWHO DID WHAT\n'+who+'\n\nCURRENT SYSTEM\n'+system
    transcript+='\n\nLEGACY NATIVE MESSAGES / TOOLS / RESULTS\n'+json.dumps(old['messages'],ensure_ascii=False,indent=2)
    transcript+='\n\nFRESH NATIVE MESSAGES / TOOLS / RESULTS\n'+json.dumps(fresh['messages'],ensure_ascii=False,indent=2)
    transcript+='\n\nCORRECTIONS\n'+'\n'.join(corrections)+'\n\nCURRENT SCOPE\n'+read(ROOT/'config.json')['actor_disc_scene_progress']+'\nFull goal active and incomplete.\n'
    (audit/'prompts-and-responses.txt').write_text(transcript)
    evidence=['verification/biwn-disc-scene-actors-checks.json','verification/disc-scene-actor-MCP-check.json','verification/disc-scene-actor-review.json',str((audit/'prompts-and-responses.txt').relative_to(ROOT))]
    checkpoint={'recorded_at':now,'published_components':106,'processor_components':{'CPU':104,'GPU':2},'new_components':0,
                'disc_scene_cases':16,'actor_iterations':1024,'task_handoffs':2064,'full_helper_return_CPU_comparisons':1108,
                'cases_with_position_change':12,'outdoor_collision_entries':40,'indoor_collision_entries':0,
                'created_contexts_preserved':21,'runnable_actor_and_idle_contexts':4,'blocked_contexts':17,
                'geometry_replaced_by_synthetic_grid':False,'actor_helper_scripts':0,'shared_time_step_host_inputs':[0,1,8,30],
                'world_generates_timestep_in_this_proof':False,'startup_C_scene_task_state_linked':True,'uninterrupted_startup_actor_execution':False,
                'actor_phase_allCPU_complete2MBRAM_privateframes_compared':True,'startup_private_stack_formatter_exclusions_retained':True,
                'synchronous_GPU_completion':True,'removal_reuse_in_disc_scene':False,'separate_synthetic_scene_removal_reuse_checked':True,
                'native_chat':fresh['name'],'native_history_preserved':old['name'],'native_current_prompt_tools_verified':True,
                'native_answers_correct':2,'native_tools_per_answer':1,'native_fresh_context_tokens':fresh['tokenCount'],'native_context_percent_observed':17,
                'model_idle':True,'known_compute_jobs':'terminal','new_training':False,'model_defaults_unchanged':True,'full_goal_status':'active incomplete','evidence':evidence,
                'next_work':'Reconstruct full CPU world timing/input continuation and connect it with the actual-scene actor task ring; then render, actual loading switches, remaining task bodies and game systems.'}
    save(ROOT/'verification/disc-scene-actor-checkpoint.json',checkpoint)
    for name in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']:
        path=ROOT/'verification'/name;value=read(path);value.update(disc_scene_actor_checkpoint=checkpoint,disc_scene_actor_review=review)
        if name=='current-runtime-state.json':value.update(recorded_at=now,models=models,local_inference_jobs='Terminal: native history and fresh focused scene questions passed, one evidence call each; model idle.',emulator_jobs='Terminal: four new startup captures and16actual-scene actor cases/2064handoffs pass.',latest_native_ease_review=str(ROOT/'verification/disc-scene-actor-review.json'))
        if name=='requirements-audit.json':
            value.update(recorded_at_utc=now,previous_goal_turn_classification='Progress: TRAP2removal, actor exit/reuse, nativeChatverification;count106.',this_goal_turn_classification='Progress: actualCstartupdiscscene/taskstatebridgedtotwoactors,16cases/2064handoffs; suppliedtimingexplicit, nativefocusedanswercorrectand17percentcontext;count106unchanged.',next_safe_work=checkpoint['next_work'])
            for item in value['requirements']:
                if 'decompilation test'in item['requirement']:item['evidence']=list(dict.fromkeys(item['evidence']+evidence))
        save(path,value)
    note='\nDISC-SCENE ACTOR CHECKPOINT — '+now+'\n\n'+read(ROOT/'config.json')['actor_disc_scene_progress']+'\n\nWHO DID WHAT\n'+who+'\n\nEXACT PROMPTS / RESPONSES / TOOLS / CORRECTIONS\n'+str(audit/'prompts-and-responses.txt')+'\n\nNEXT\n'+checkpoint['next_work']+'\nFull goal active and incomplete.\n'
    for name in ['POST REVIEW.txt','projects/black-ice-white-noise/restoration/READ ME.txt','CURRENT DECOMPILATION.txt']:
        with(ROOT/name).open('a')as handle:handle.write(note)
    path=ROOT/'START HERE.txt';text=path.read_text().replace('Choose Game Assistant — Live Actor Checkpoint or','Choose Game Assistant — Disc Scene Checkpoint or');a=text.index('LOCAL INFERENCE RESULT\n');b=text.index('TRY ADVERTISING ASSISTANT\n',a)
    text=text[:a]+('LOCAL INFERENCE RESULT\nOpen Game Assistant — Disc Scene Checkpoint and type normally. It answered the actual-scene/timing/remaining-work question correctly with one focused evidence call and uses17percentcontext. Previoushistory/roles remain in Game Assistant — Live Actor Checkpoint. These samples are not a general accuracy/speed benchmark.\n\nTry: Have actors now run on the disc scene, and does the world task supply their movement time?\n\n')+text[b:];path.write_text(text)
    print(json.dumps({'components':106,'disc_scene_cases':16,'handoffs':2064,'native_focused_topic':'actor_scene','native_chat':fresh['name'],'context_tokens':fresh['tokenCount'],'model_idle':True,'audit':str(audit)}))

if __name__=='__main__':main()
