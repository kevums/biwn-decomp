"""Keep exact native Chat scene-caller evidence and scope acceptance."""
import hashlib,json,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
def save(p,value):p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def main():
    now=datetime.now(timezone.utc).isoformat();checkpoint=read(ROOT/'verification/scene-draw-checkpoint.json')
    cpu=read(ROOT/'verification/biwn-scene-draw-cpu-checks.json');linked=read(ROOT/'verification/biwn-disc-world-scene-draw-checks.json')
    source=ROOT/'projects/black-ice-white-noise/restoration'
    for proof in [cpu,linked]:
        assert read(Path(proof['directory'])/'status.json')['status']=='terminal_pass'
        for name,expected in proof['source_sha256'].items():assert hashlib.sha256((source/name).read_bytes()).hexdigest()==expected
    mcp=read(ROOT/'verification/scene-draw-MCP-check.json');assert mcp['status']=='fresh_installed_scene_caller_and_eight_lower_script_scope_passed'
    native_path=Path.home()/'.lmstudio/conversations/1791930588865.conversation.json';native=read(native_path)
    assert native['name']=='Game Assistant — Live Queue Checkpoint'
    user,assistant=[m['versions'][m['currentlySelected']]for m in native['messages'][-2:]]
    assert user['role']=='user'and assistant['role']=='assistant'
    prompt=''.join(b.get('text','')for b in user['content']);assert prompt.startswith('Is 0x17E0E still a stub, or does the scene caller now execute?')
    blocks=[b for step in assistant['steps']for b in step.get('content',[])]
    calls=[b for b in blocks if b['type']=='toolCallRequest'];assert len(calls)==1 and calls[0]['name']=='project_evidence'and calls[0]['parameters']=={'topic':'rendering'}
    result=next(b for b in blocks if b['type']=='toolCallResult');evidence=json.loads(json.loads(result['content'])[0]['text'])
    assert evidence['scene_draw_caller']['scene_draw_caller_fullCPU_real']and evidence['scene_draw_full_CPU']['CPU_cases']==1024
    assert evidence['current_world_actors']['report']==str(ROOT/'verification/biwn-disc-world-scene-draw-checks.json')
    answer=''.join(b.get('text','')for b in blocks if b['type']=='text')
    assert 'no longer a stub'in answer and 'configured but unreached'in answer and 'No, this does not mean the full 3D viewport is working'in answer
    stats=[s['genInfo']['stats']for s in assistant['steps']if s.get('genInfo',{}).get('stats')]
    assert len(stats)==2 and all(v['stopReason']=='eosFound'for v in stats)
    models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True))
    assert len(models)==1 and models[0]['identifier']=='advertising-scholar'and models[0]['status']=='idle'and models[0]['queued']==0
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    workmap=session/'remaining-render-bodies-fullCPU-workmap.json';assert read(workmap)['status']=='mapped_not_new_fullCPU_implemented_or_live_linked'
    audit=ROOT/'verification/scene-draw-review'/Path(linked['directory']).name;audit.mkdir(parents=True,exist_ok=True)
    shutil.copy2(native_path,audit/'native-conversation-read-only-snapshot.json');shutil.copy2(workmap,audit/workmap.name)
    save(audit/'native-tool-evidence.json',evidence)
    system=next(f['value']for f in native['perChatPredictionConfig']['fields']if f['key']=='llm.prediction.systemPrompt')
    who=('Codex authored the full CPU scene/clear/rotation C and live integration. Original native CPU/GPU and independent standalone Unicorn validate scoped code effects; the pinned emulated blitter rasterizes actual clear submissions. The local27Bbase answered one ordinary question in native LM Studio Chat with one current rendering evidence call. No subagents, local-model-authored game code, new training, model switch or weight/default promotion. Eight lower rendering helper scripts remain explicit. Native chat files were read/copied only, never injected or edited.')
    limits=['Standalone1024cases/all102instructions/17guards and live16cases passed without C behavior repair. A Python preflight Device.write argument error was corrected before any comparison. Separate planning decode initially used an arbitrary17380endpoint; the next170A0body map now stops immediately after actualRTS17324 at17326.',
            'Scene caller17E0E,clearE03A,rotation17F14 each1008actualcalls; eight configured lower scripts/four reached1008each:181F8overlay,E0A6submission,170A0geometry and185B2display-list. E0F2/E148/E19E/E202 remain configured/unreached. No full geometry/viewport/scanout/audio/fullgame.',
            'Native UI showed the new question, evidence call and start of the answer. The Mac locked before the final visual check. Full answer and EOS are verified from the UI-created saved conversation, and the model is idle. No unlock requested. Current native provider adopted both the new scene-draw evidence fields and standalone proof.',
            'The148word answer correctly separates actual caller/clear/rotation from lower scripts and rejects a working full3Dviewport. It is longer than the requested brief response. One sample does not prove general ease/reliability or speed.',
            'Next source workmap is preparation only:10CPUsubmission,152geometry-record,254display-list and184overlayinstructions. Display-list jump table10bytes excluded from decode; unreachable instructions in its older proof retain their limits. GPU4D80body reconstruction remains a separate requirement.']
    review=dict(recorded_at=now,status='scene_caller_CPU_and_live_checks_passed_native_saved_scope_answer_correct_game_incomplete',who_did_what=who,
                prompt=prompt,answer=answer,word_count=len(answer.split()),tool_calls=calls,generation_stats=stats,verdict='bounded_facts_correct_but_verbose',
                native_UI_partial_response_observed=True,native_final_UI_visual_check='Mac locked; not performed',native_complete_saved_response_verified=True,native_current_provider_adoption_verified=True,
                native_conversation_source=str(native_path),native_chat_name=native['name'],new_training=False,default_promoted=False,model_idle=True,general_model_reliability_proved=False,limits=limits,directory=str(audit))
    save(audit/'review.json',review);save(ROOT/'verification/scene-draw-review.json',review)
    transcript='SCENE CALLER / LOCAL NATIVE INFERENCE AUDIT\n\nWHO DID WHAT\n'+who+'\n\nLIMITS / CORRECTIONS\n'+'\n'.join(limits)
    transcript+='\n\nEXACT NATIVE SYSTEM\n'+system+'\n\nUSER\n'+prompt+'\n\nTOOL CALL / RETURN\n'+json.dumps({'calls':calls,'evidence':evidence},ensure_ascii=False,indent=2)+'\n\nANSWER\n'+answer
    transcript+='\n\nREVIEW\n'+json.dumps(review,ensure_ascii=False,indent=2)+'\n\nNEXT\n'+checkpoint['next_work']+'\nFull goal active and incomplete.\n';(audit/'prompts-and-responses.txt').write_text(transcript)
    checkpoint.update(recorded_at=now,status=review['status'],native_current_checkpoint_response_verified=True,native_complete_saved_response_verified=True,native_current_provider_adoption_verified=True,
                      native_final_UI_visual_check=review['native_final_UI_visual_check'],model_idle=True,known_compute_jobs='terminal',new_training=False,default_promoted=False,
                      review=str(ROOT/'verification/scene-draw-review.json'),transcript=str(audit/'prompts-and-responses.txt'),next_source_workmap=str(workmap))
    checkpoint['evidence']+=['verification/scene-draw-MCP-check.json','verification/scene-draw-review.json',str((audit/'prompts-and-responses.txt').relative_to(ROOT))]
    save(ROOT/'verification/scene-draw-checkpoint.json',checkpoint)
    for name in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']:
        path=ROOT/'verification'/name;value=read(path);value.update(scene_draw_checkpoint=checkpoint,scene_draw_review=review)
        if name=='current-runtime-state.json':value.update(recorded_at=now,models=models,local_inference_jobs='Terminal: native current scene-caller answer correct but verbose; final UI observation locked. Everyday model idle.',latest_API_ease_review=str(ROOT/'verification/scene-draw-review.json'))
        save(path,value)
    note='\nNATIVE SCENE-CALLER REVIEW — '+now+'\n\n'+who+'\n\nRESULT\nCurrent148word saved native answer is factually correct but verbose. One rendering evidence call; current scene caller/clear/rotation and eightconfigured/fourreached scripts distinguished, completeviewport rejected. Question/tool/start of response visible; Mac locked before final visual check. EOS/savedcompleteanswer/currentproviderdata/modelidle verified. No new training/default promotion; no unlock requested.\n\nEXACT PROMPTS / TOOLS / RESPONSES\n'+str(audit/'prompts-and-responses.txt')+'\n\nNEXT SOURCE MAP\n'+str(workmap)+'\nFull goal active and incomplete.\n'
    for name in ['CURRENT DECOMPILATION.txt','POST REVIEW.txt','projects/black-ice-white-noise/restoration/READ ME.txt']:
        with(ROOT/name).open('a')as handle:handle.write(note)
    path=ROOT/'START HERE.txt';text=path.read_text();a=text.index('LOCAL INFERENCE RESULT\n');b=text.index('TRY ADVERTISING ASSISTANT\n',a)
    path.write_text(text[:a]+'LOCAL INFERENCE RESULT\nGame Assistant — Live Queue Checkpoint contains the native sprite image, role assessment and latest scene-caller answer. The latest answer correctly states that17E0E/clear/rotation are real while eightlower rendering scripts/fourreached remain; it is verbose. One current evidence call. Final visual check was locked, while savedcompleteanswer/EOS/providerdata/modelidle are verified. No new training/default promotion. Fullgame incomplete.\n\nTry: Is the scene caller still a stub, and is the full3Dviewport working?\n\nExact current exchange and review:\n'+str(audit/'prompts-and-responses.txt')+'\n\n'+text[b:])
    print(json.dumps(dict(status=review['status'],native_answer_words=len(answer.split()),model_idle=True,audit=str(audit),next_workmap=str(workmap))))
if __name__=='__main__':main()
