"""Audit actual GPU4D80 integration, corrections, and two local SDK replies."""
import hashlib,json,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
from record_disc_camera_animation_checkpoint import samples
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
def save(p,value):p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def main():
    now=datetime.now(timezone.utc).isoformat();checkpoint=read(ROOT/'verification/GPU-geometry-checkpoint.json');gpu=read(ROOT/'verification/biwn-gpu-geometry-checks.json');linked=read(ROOT/'verification/biwn-disc-world-gpu-geometry-checks.json');source=ROOT/'projects/black-ice-white-noise/restoration'
    for proof in [gpu,linked]:
        assert read(Path(proof['directory'])/'status.json')['status']=='terminal_pass'
        for name,expected in proof['source_sha256'].items():assert hashlib.sha256((source/name).read_bytes()).hexdigest()==expected
    regression=read(ROOT/'verification/biwn-disc-world-geometry-records-checks.json');assert regression['cases']==16 and read(Path(regression['directory'])/'status.json')['status']=='terminal_pass'
    mcp=read(ROOT/'verification/GPU-geometry-MCP-check.json');assert mcp['status']=='fresh_installed_GPU4D80_scope_counters_and_lower_scripts_passed'
    path=Path(read(ROOT/'verification/easy-gpu-geometry-current.json')['directory'])/'protocol.json';protocol=read(path);assert protocol['status']=='completed_pending_coordinator_review';reviewed=samples(protocol);assert len(reviewed)==2
    reviewed[0].update(verdict='bounded_current_GPU_geometry_and_viewport_scope_correct',reason='63words, one rendering evidence call. Correctly says GPU4D80/E0A6 reconstructed C runs1008times and distinguishes six remaining renderer scripts,15blockedcontexts and absent completeviewport. Opening No answers the viewport part explicitly; following sentence confirms C execution.')
    reviewed[1].update(verdict='bounded_same_model_counter_and_script_review_correct_but_overlapping_retrieval',reason='88words, correct GPU0/55 plus4builderaddition gives absolute4/59. Sixconfigured/fourreached scripts exact. Analyst/Reviewer shareone model. Two evidence calls display_list+rendering overlap; no general ease/reliability claim.')
    models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True));assert len(models)==1 and models[0]['identifier']=='advertising-scholar'and models[0]['status']=='idle'and models[0]['queued']==0 and models[0]['contextLength']==32768
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);workmap=session/'remaining-draw-GPU-workmap.json';assert read(workmap)['status']=='next_two_reached_GPU_programs_extracted_not_reconstructed_or_dynamically_verified'
    audit=ROOT/'verification/GPU-geometry-review'/Path(linked['directory']).name;audit.mkdir(parents=True,exist_ok=True);shutil.copy2(path,audit/'SDK-protocol.json');shutil.copy2(workmap,audit/workmap.name);shutil.copy2(ROOT/'verification/GPU-geometry-MCP-check.json',audit/'installed-MCP.json')
    # Keep terminal failures and the exact old C/header whose hashes were
    # recovered before correction; successful program sources are separate.
    failures=[]
    for parent in [ROOT/'verification/biwn-gpu-geometry',ROOT/'verification/biwn-disc-world-gpu-geometry']:
        for status_path in sorted(parent.glob('*/status.json')):
            status=read(status_path)
            if status['status']=='terminal_failed':failures.append(dict(directory=str(status_path.parent),status=status))
    assert failures
    save(audit/'retained-failures.json',failures)
    who=('Codex authored the 434-instruction fixed C GPU4D80 program, full CPU E0A6 wrapper, isolated device bridge, comparison tests and live integration. Original pinned GPU validates standalone full registers/flags/scratch/RAM/PC/bus effects; original native CPU/GPU validates integrated full CPU/private frames/main RAM and all handoffs. A prior16case rendering configuration was rerun after the bus adapter correction. The local27Bbase answered two localhost SDK questions, using Analyst/Reviewer roles on the same model for the second. No subagents or local-model-authored source, new training, system-prompt/model/weight/default promotion. Tool documentation was updated for GPU4D80 rendering versus GPU4320 movement topics. A fresh CUA session still timed out opening LM Studio after120.8128seconds despite a15second request. No new native prompt/response/provider adoption or unlock request; native conversation files were not injected or edited.')
    corrections=[
        'Initial C generator had a Python string-assembly syntax error before any C generation; corrected. First GPU comparison already matched all register banks/flags, main RAM, PC sequence and external bus/stores, but untouched GPU RAM differed because native GPUReset randomizes it. Corrected the C initializer contract to accept actual pre-execution GPU RAM; all128cases/all434instructions/13guards passed. Initial and final4KBfiles/hashes retained percase; reset/bootRAM not reconstructed.',
        'First integrated run failed in an actor helper reading logical8015CCD8. The original Jaguar bus masks physical addresses to24bits. Corrected only CPU bus adapter normalization while preserving32bitregister/pointer values; physical15CCD8 is valid RAM.870aliased accesses nowexecute. Full16case integrated proof and prior16caseconfiguration regression pass. No game integer/program behavior repair was required.',
        'GPU4D80 and fullCPU E0A6 each run1008times. CPUwrapper10/10instructions exercised, completeCPU/privateframes/main2MBRAM and6144fullCPUhandoffs match original. Strengthened before/after record-counter logging and repeated16cases successfully. GPUcounter0/55 plus4builderrecords gives final4/59;59 is not59newrecords.',
        'World720updates, actors2048iterations,160sprite decodes,32disc payloads/3080416bytes retained. GPU4320movement3488whole-scene calls is separate fromGPU4D80geometry; buildernestedE220linkedbutunreached0. Sixlower renderer scripts configured;fourreached1008each:181F8,E19E,E202,185B2. E0F2/E148unreached. GPUprograms52E0/57A0,display-list/overlay,15blockedcontexts,main-scene synchronization,audio/boot/fullviewport/game remain incomplete.',
        'Standalone GPU proof compares64registers,Z/C/N,matrixcontrol/pointer,dividerremainder,all4KBGPUlocalRAM,2MBmainRAM,exactdirectPCorder andexternalbusreadshape/actualstores. Native watch readvalues may beplaceholders, never treated as independent measured readvalues. Derived mandatorydelay slots are distinguished from directly observed PCs. Cside executes no originalGPU/coregame instructions.',
        'The integrated device uses explicit synchronous completion and suppliedGPUentry/seed/dividermode. Cshader copies its scratch/banks/control back and retains remainder internally; the core read-only remainder and fullcross-kernelGPUcontextcontinuity are not proved. CurrentCPU/mainRAMintegration is verified; originaldispatcher/async/physicaltiming/fullboot is not.',
        'Two bounded local replies are factually correct:63words/onecall/about21.73SDKseconds and88words/twooverlappingcalls/about35.12seconds. Roles shareone model; these samples do not prove general reliability/speed/ease. Native UI timeout leaves latest native response and provider adoption unverified. Everydaybaseidle.',
        'Next GPU52E0payload1200bytes andGPU57A0payload232bytes are extracted from original source headers, but only linearly decoded. Code/data boundaries and execution/C behavior remain unverified; no new component counted for them. Aggregate114selectedcomponents=111CPU/3GPU, onlyGPU4D80new; not a completion percentage.'
    ]
    review=dict(recorded_at=now,status='GPU4D80_standalone_and_live_integration_plus_bounded_local_answers_passed_game_incomplete',who_did_what=who,samples=reviewed,corrections=corrections,failures=failures,
                native_new_response_verified=False,native_current_provider_adoption_verified=False,native_UI_observation='Fresh CUA session getApp timed out after120.8128seconds; current lock state unknown',
                model_idle=True,new_training=False,system_prompt_changed=False,tool_topic_description_updated=True,default_promoted=False,general_model_reliability_proved=False,directory=str(audit),next_GPU_workmap=str(workmap))
    save(audit/'review.json',review);save(ROOT/'verification/GPU-geometry-review.json',review)
    transcript='GPU4D80 / LOCAL INFERENCE — FULL AUDIT\n\nWHO DID WHAT\n'+who+'\n\nCORRECTIONS / LIMITS\n'+'\n'.join(corrections)+'\n\nEXACT SYSTEM / USER / TOOLS / RESPONSES\n'+json.dumps(protocol,ensure_ascii=False,indent=2)+'\n\nCOORDINATOR REVIEW\n'+json.dumps(review,ensure_ascii=False,indent=2)+'\n\nNEXT\n'+checkpoint['next_work']+'\nFull goal active and incomplete.\n';(audit/'prompts-and-responses.txt').write_text(transcript)
    concise='LOCAL API CHAT — GPU GEOMETRY CHECKPOINT\n\nModel: advertising-scholar (27B base), thinking off, one worker,32768context. These are SDK exchanges, not new native Chat messages. Analyst/Reviewer are roles on one model.\n\n'
    for i,sample in enumerate(reviewed,1):
        concise+=f'QUESTION {i}\n'+sample['prompt']+'\n\nTOOLS\n'+json.dumps(sample['tool_calls'],ensure_ascii=False,indent=2)+'\n\nLOCAL RESPONSE\n'+sample['answer']+f'\n\nSDK reported: {sample["SDK_reported_seconds"]:.2f}seconds.\n\n'
    concise+='Full system prompt, evidence returns, code tests, failures and review:\n'+str(audit/'prompts-and-responses.txt')+'\nFull game and general model reliability remain incomplete/unproved.\n';(audit/'readable-chat-transcript.txt').write_text(concise)
    checkpoint.update(recorded_at=now,status=review['status'],model_idle=True,known_compute_jobs='terminal',native_new_response_verified=False,native_UI_observation=review['native_UI_observation'],new_training=False,system_prompt_changed=False,default_promoted=False,
                      local_bounded_answers_correct=2,ordinary_answer_words=63,role_answer_words=88,SDK_reported_seconds=[s['SDK_reported_seconds']for s in reviewed],role_two_overlapping_tools_remain=True,general_model_reliability_proved=False,
                      review=str(ROOT/'verification/GPU-geometry-review.json'),transcript=str(audit/'prompts-and-responses.txt'),readable_chat_transcript=str(audit/'readable-chat-transcript.txt'),next_GPU_workmap=str(workmap))
    checkpoint['evidence']+=['verification/GPU-geometry-MCP-check.json','verification/GPU-geometry-review.json',str((audit/'prompts-and-responses.txt').relative_to(ROOT))]
    save(ROOT/'verification/GPU-geometry-checkpoint.json',checkpoint)
    for name in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']:
        p=ROOT/'verification'/name;v=read(p);v.update(GPU_geometry_checkpoint=checkpoint,GPU_geometry_review=review)
        if name=='current-runtime-state.json':v.update(recorded_at=now,models=models,local_inference_jobs='Terminal: two bounded GPUgeometry replies correct. Native UI unavailable. Everydaybaseidle.',latest_API_ease_review=str(ROOT/'verification/GPU-geometry-review.json'))
        if name=='requirements-audit.json':
            for item in v['requirements']:
                if 'decompilation test'in item['requirement']:item['evidence']=list(dict.fromkeys(item['evidence']+checkpoint['evidence']))
        save(p,v)
    note='\nGPU GEOMETRY / LOCAL INFERENCE REVIEW — '+now+'\n\n'+who+'\n\n'+'\n'.join(corrections)+'\n\nREADABLE LOCAL CHAT\n'+str(audit/'readable-chat-transcript.txt')+'\n\nEXACT SYSTEM / TOOL RETURNS / RESPONSES\n'+str(audit/'prompts-and-responses.txt')+'\nFull goal active and incomplete.\n'
    for name in ['CURRENT DECOMPILATION.txt','POST REVIEW.txt','projects/black-ice-white-noise/restoration/READ ME.txt']:
        with(ROOT/name).open('a')as f:f.write(note)
    p=ROOT/'START HERE.txt';text=p.read_text();a=text.index('LOCAL INFERENCE RESULT\n');b=text.index('TRY ADVERTISING ASSISTANT\n',a)
    p.write_text(text[:a]+'LOCAL INFERENCE RESULT\nThe existing native Game Assistant — Live Queue Checkpoint retains earlier visible exchanges. Latest native access timed out; current GPU questions used the local API. Both answers are factually correct: the GPU geometry program runs in C, but a complete viewport remains unfinished;59 is55 from the GPU step plus4 records added. Ordinary reply:63words,one evidence call,about22seconds. Role reply:88words,two overlapping calls,about35seconds. General reliability/ease remains unproved. Everyday base idle; no new training, system-prompt or model/weight promotion.\n\nTry: Is the GPU geometry routine really running as C, and is the complete3Dviewport working?\n\nReadable exact user/tool/answer transcript:\n'+str(audit/'readable-chat-transcript.txt')+'\n\nFull system/evidence/code audit:\n'+str(audit/'prompts-and-responses.txt')+'\n\n'+text[b:])
    print(json.dumps(dict(status=review['status'],components=114,live_GPU_geometry_calls=1008,local_bounded_answers_correct=2,native_verified=False,model_idle=True,audit=str(audit),readable_chat=str(audit/'readable-chat-transcript.txt'))))
if __name__=='__main__':main()
