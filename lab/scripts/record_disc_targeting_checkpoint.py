"""Finalize targeting code/oracle scope and reviewed local-chat samples."""
import hashlib,json,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
from record_disc_camera_animation_checkpoint import samples
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def main():
    now=datetime.now(timezone.utc).isoformat();linked=read(ROOT/'verification/biwn-disc-world-targeting-checks.json');checkpoint=read(ROOT/'verification/disc-targeting-checkpoint.json');mcp=read(ROOT/'verification/disc-targeting-MCP-check.json')
    assert mcp['status']=='fresh_installed_targeting_fullCPU_and_live_scan_scope_passed'
    source=ROOT/'projects/black-ice-white-noise/restoration'
    for name in ['biwn-targeting-cpu-checks.json','biwn-disc-world-targeting-checks.json']:
        proof=read(ROOT/'verification'/name);assert read(Path(proof['directory'])/'status.json')['status']=='terminal_pass'
        for n,h in proof['source_sha256'].items():assert hashlib.sha256((source/n).read_bytes()).hexdigest()==h
    protocol_path=ROOT/'verification/easy-disc-targeting/20261013T201156.948261Z/protocol.json';protocol=read(protocol_path);assert protocol['status']=='completed_pending_coordinator_review'
    reviewed=samples(protocol);assert len(reviewed)==2 and all(s['word_count']<130 and len(s['tool_calls'])==1 for s in reviewed)
    reviewed[0].update(verdict='bounded_current_scope_correct',reason='Distinguishes actual fullCPU targeting from512scan/filter-only calls, zero math/activeflags and eligibilityword0; lists four configured scripts/sole reachedinputdispatcher and missingconsumer/render/crosshair. No live acquisition claim.')
    reviewed[1].update(verdict='bounded_same_model_role_review_correct',reason='Standalone1026case/183instruction scoring/projection/radius evidence does not prove live acquisition. Current four/one helper scope correct. Roles share weights and are not independent verification.')
    models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True));assert len(models)==1 and models[0]['identifier']=='advertising-scholar'and models[0]['status']=='idle'and models[0]['queued']==0 and models[0]['contextLength']==32768
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);workmap=read(session/'input-dispatch-fullCPU-workmap.json');assert workmap['instruction_count']==816 and len(workmap['jump_table']['states'])==13 and len(workmap['yield_instructions'])==2
    eligibility=[]
    for path in sorted(Path(linked['startup_capture_directory']).glob('startup-C-*.bin')):
        ram=path.read_bytes()
        for i in range(40):
            obj=0x49d6c+i*206;active=int.from_bytes(ram[obj:obj+2],'big')
            if active:eligibility.append({'capture':str(path),'RAM_sha256':hashlib.sha256(ram).hexdigest(),'slot':i,'active_word':active,'targeting_gate_offset':'0x6c','targeting_gate_word':int.from_bytes(ram[obj+0x6c:obj+0x6e],'big')})
    assert len(eligibility)==8 and all(r['targeting_gate_word']==0 for r in eligibility)
    save(ROOT/'verification/targeting-live-eligibility.json',{'scope':'Initial phased Cstartup records. Offset6C is the source targeting eligibility test, an analyst label; no original symbol recovered. Live trace separately proves zero directmath/activeflags.','records':eligibility})
    audit=ROOT/'verification/disc-targeting-review'/Path(linked['directory']).name;audit.mkdir(parents=True,exist_ok=True);shutil.copy2(protocol_path,audit/'SDK-protocol.json')
    who=('Codex authored biwn_targeting_cpu.c/h, the differential tests and live world integration, plus current evidence publication. Original native CPU and independent Unicorn observer decide code acceptance. '
         'The local27Bbase answered one ordinary question and one Analyst/Reviewer role prompt via LM Studio localhost SDK. No local-model code was accepted; same-model roles are not independent checks. '
         'Both answers are correct within the supplied evidence. Two samples do not prove general reliability. No new training, model switch or default promotion. Everyday base remains32k/oneworker and idle. '
         'Native Chat remains unverified after prior getApp timeout; no fresh native prompt/provider adoption claim, no conversation-file injection and no unlock request.')
    corrections=['Initial1026cases andall183instructioncoverage passed. Guard failure selectedE588inside13440 instead of a direct20820division callback. Correctedfixtureto20950JSR; final1026cases/18guards pass. Cbehavior didnotchange.',
                 'Combined16cases/512worldupdates/1024actoriterations/2576handoffs pass with realtargeting. Fourworldscriptsconfigured; onlyinputdispatch191F4reached512times. Existing106componentcountunchanged.',
                 'Actualscene targetingscan/filter only:512calls,zero directmath/activeflags. Eight initialactiveactorrecords acrossfourcaptures allhave6Cword0. Standalone syntheticcandidate/matrix tests coveracquisition/projection/radius; no liveacquisition or visiblecrosshair proved.',
                 'Generic camera CPU-oracle harness now supports per-entry instructionranges/readqueues; camera debug/normal preflight rerun passed. AcceptedcameraC unchanged.',
                 'Mapped inputdispatcher816sourceinstructions/13states/twoDF60yieldcalls fromverifiedstage bytes; this is preparation, not fullCPU/continuationcompletion.']
    review={'recorded_at':now,'status':'code_passed_two_bounded_local_answers_correct_live_acquisition_unproved','who_did_what':who,'samples':reviewed,'corrections':corrections,'native_new_response_verified':False,'live_acquisition_proved':False,'general_model_reliability_proved':False,'new_training':False,'default_promoted':False,'model_idle':True,'directory':str(audit),'payload_bytes_by_topic':mcp['payload_bytes_by_topic']}
    save(audit/'review.json',review);save(ROOT/'verification/disc-targeting-review.json',review)
    transcript='TARGETING FULL CPU / LIVE SCAN — AUDIT\n\nWHO DID WHAT\n'+who+'\n\nCORRECTIONS / LIMITS\n'+'\n'.join(corrections)+'\n\nEXACT SYSTEM / USER / TOOLS / RESPONSES\n'+json.dumps(protocol,ensure_ascii=False,indent=2)+'\n\nCOORDINATOR VERDICTS\n'+json.dumps(reviewed,ensure_ascii=False,indent=2)+'\n\nCURRENT CODE SCOPE\n'+read(ROOT/'config.json')['disc_world_actor_progress']+'\nFull goal active and incomplete.\n'
    (audit/'prompts-and-responses.txt').write_text(transcript)
    checkpoint.update(recorded_at=now,status=review['status'],local_answers_bounded_correct=2,SDK_reported_seconds=[s['SDK_reported_seconds']for s in reviewed],known_compute_jobs='terminal',model_idle=True,new_training=False,default_promoted=False,review=str(ROOT/'verification/disc-targeting-review.json'),transcript=str(audit/'prompts-and-responses.txt'),input_dispatch_workmap=str(session/'input-dispatch-fullCPU-workmap.json'))
    checkpoint['evidence']+=['verification/disc-targeting-MCP-check.json','verification/disc-targeting-review.json','verification/targeting-live-eligibility.json',str((audit/'prompts-and-responses.txt').relative_to(ROOT))]
    save(ROOT/'verification/disc-targeting-checkpoint.json',checkpoint)
    for name in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']:
        path=ROOT/'verification'/name;value=read(path);value.update(disc_targeting_checkpoint=checkpoint,disc_targeting_review=review)
        if name=='current-runtime-state.json':value.update(recorded_at=now,models=models,local_inference_jobs='Terminal: two bounded targeting answers correct, live acquisition unproved, native response unverified; model idle.',latest_API_ease_review=str(ROOT/'verification/disc-targeting-review.json'))
        if name=='requirements-audit.json':
            for item in value['requirements']:
                if 'decompilation test'in item['requirement']:item['evidence']=list(dict.fromkeys(item['evidence']+checkpoint['evidence']))
        save(path,value)
    note='\nLOCAL TARGETING REVIEW — '+now+'\n\n'+who+'\n\nRESULT\nBoth localanswers correctly distinguish standalonefullCPUproof from livescan/filter. SDKreportedseconds: '+', '.join(str(round(s['SDK_reported_seconds'],2))for s in reviewed)+'. No generalbenchmarkclaim. NativeChat unverified.\n\nEXACT PROMPTS / TOOLS / RESPONSES\n'+str(audit/'prompts-and-responses.txt')+'\n\nNEXT\n'+checkpoint['next_work']+'\nFull goal active and incomplete.\n'
    for name in ['POST REVIEW.txt','CURRENT DECOMPILATION.txt','projects/black-ice-white-noise/restoration/READ ME.txt']:
        with(ROOT/name).open('a')as handle:handle.write(note)
    path=ROOT/'START HERE.txt';text=path.read_text();a=text.index('LOCAL INFERENCE RESULT\n');b=text.index('TRY ADVERTISING ASSISTANT\n',a)
    text=text[:a]+('LOCAL INFERENCE RESULT\nCurrent targeting evidence is installed. Two SDK fallback answers correctly distinguish rebuilt fullCPU targeting from actual scene scan/filter; live acquisition/crosshair is unproved. One evidence call each, SDKreported about12/13seconds. Same-model Analyst/Reviewer roles are correlated. These are bounded samples, not general reliability proof. Native Chat/provider adoption remains unverified after prior access timeout. Everyday base is idle; no new training/default promotion.\n\nTry: Is targeting working in the real disc scene now, and what is still scripted? Can I see the crosshair selecting an actor?\n\nExact prompts, tools, answers and reviews:\n'+str(audit/'prompts-and-responses.txt')+'\n\n')+text[b:];path.write_text(text)
    subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts/install_chat_runtime.py')],check=True)
    print(json.dumps({'components':106,'targeting_cases':1026,'instructions':183,'combined_cases':16,'configured_world_scripts':4,'reached_world_scripts':1,'bounded_local_answers_correct':2,'live_acquisition':False,'native_verified':False,'model_idle':True,'audit':str(audit)}))
if __name__=='__main__':main()
