"""Finalize code acceptance, exact local inference transcripts and known limits."""
import hashlib,json,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def samples(protocol):
    rows=[]
    for q in protocol['questions']:
        calls=[b['toolCallRequest']for e in q['events']for b in e['content']if b['type']=='toolCallRequest']
        answer='\n'.join(b['text'].strip()for e in q['events']for b in e['content']if b['type']=='text'and b['text'].strip())
        tool_bytes=sum(len(json.dumps(b).encode())for e in q['events']for b in e['content']if b['type']=='toolCallResult')
        rows.append({'prompt':q['user'],'answer':answer,'word_count':len(answer.split()),'tool_calls':calls,'tool_result_bytes':tool_bytes,'SDK_reported_seconds':q['SDK_reported_seconds']})
    return rows
def main():
    now=datetime.now(timezone.utc).isoformat();linked=read(ROOT/'verification/biwn-disc-world-camera-checks.json');checkpoint=read(ROOT/'verification/disc-camera-animation-checkpoint.json');mcp=read(ROOT/'verification/disc-camera-animation-MCP-check.json')
    assert mcp['status']=='fresh_installed_camera_animation_and_script_scope_passed'
    source=ROOT/'projects/black-ice-white-noise/restoration'
    for name in ['biwn-animation-cpu-checks.json','biwn-camera-cpu-checks.json','biwn-disc-world-camera-checks.json']:
        proof=read(ROOT/'verification'/name);assert read(Path(proof['directory'])/'status.json')['status']=='terminal_pass'
        for n,h in proof['source_sha256'].items():assert hashlib.sha256((source/n).read_bytes()).hexdigest()==h
    first_path=ROOT/'verification/easy-disc-camera-animation/20261013T200102.113494Z/protocol.json';revised_path=ROOT/'verification/easy-disc-camera-animation/20261013T200249.833673Z/protocol.json'
    first,revised=read(first_path),read(revised_path);assert first['status']==revised['status']=='completed_pending_coordinator_review'
    original,refined=samples(first),samples(revised);assert len(original)==2 and len(refined)==1 and original[0]['prompt']==refined[0]['prompt']
    assert len(original[0]['tool_calls'])==len(refined[0]['tool_calls'])==3 and all(x['word_count']<130 for x in original+refined)
    original[0].update(verdict='scope_incomplete_and_historical_scope_mixture_rejected',reason='Camera/animation execution and unplayable conclusion correct, but omitted five configured/two reached world scripts and imported15nestedservices from an older pipeline into the current test limitations.')
    original[1].update(verdict='bounded_script_inventory_review_correct',reason='All five configured helpers, two reached counts, three unreached and missing queueconsumer stated correctly. Same-model roles do not provide independent review.')
    refined[0].update(verdict='bounded_current_evidence_answer_correct',reason='Unchanged ordinary question, same model and three topic choices. Compact current reports now yield accurate current five/two script scope, actual camera/animation, controlled inputs, blockedrender/missingconsumer and unplayable/fullgame limits, within130words.')
    models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True));assert len(models)==1 and models[0]['identifier']=='advertising-scholar'and models[0]['status']=='idle'and models[0]['queued']==0 and models[0]['contextLength']==32768
    audit=ROOT/'verification/disc-camera-animation-review'/Path(linked['directory']).name;audit.mkdir(parents=True,exist_ok=True)
    for path,name in [(first_path,'original-SDK.json'),(revised_path,'compact-evidence-SDK.json')]:shutil.copy2(path,audit/name)
    who=('Codex authored the full CPU animation and camera interfaces, differential tests, world-task integration and bounded evidence tools. Original pinned CPU/GPU execution is the acceptance oracle; a second Unicorn CPU checks standalone CPU/bus effects. '
         'The local27Bbase answered ordinary questions and Analyst/Reviewer role prompts through LM Studio localhost SDK. Those roles share weights; no independent local-model vote or local-model-authored code was accepted. '
         'No new training, downloaded weights, model switch or default promotion occurred. Everyday27Bmodel remains loaded at32k with one worker, now idle. '
         'Native LM Studio getApp timed out in this checkpoint; no new native Chat prompt/response or provider adoption is verified. Conversation files were not injected or edited.')
    corrections=['Animation fullCPU1538cases/all101instructions and actualnestedqueue passed. Combined world proof created16realqueue requests;consumer/render remainblocked.',
                 'Camera fullCPU768cases/all144instructions withactualmultiply/direction/GPU and twoCPUoracles passed; no behavioral source repair wasneeded. Removed unused localvariables before compilation.',
                 'Combined16disc-scene cases now execute actualcamera andanimation:512worldupdates/1024actoriterations/2576handoffs,2048originalGPUsubmissions,3584worldhelperCPUincoming/returns. Fiveworldscriptsconfigured/tworeached. Count106unchanged.',
                 'Initial ordinary model reply read three reports totaling109200serializedbytes and mixed historical scope; rejected. Replaced broad status/camera/animation reports with bounded current facts, kept detailed historical topics separately, and repeated the same ordinary question. Correct bounded revised answer retained. These few samples are not a general speed or reliability benchmark.',
                 'Native UI request timed out despite a requested15second tooltimeout; returned after120seconds. No unlock requested; SDK fallback allowed by user.']
    review={'recorded_at':now,'status':'code_passed_bounded_revised_local_answer_correct_native_unverified','who_did_what':who,'original_samples':original,'compact_evidence_samples':refined,'corrections':corrections,
            'native_new_response_verified':False,'native_provider_adoption_verified':False,'new_training':False,'default_promoted':False,'everyday_model_idle':True,'general_model_reliability_proved':False,'directory':str(audit),'tool_payload_bytes_by_topic':mcp['payload_bytes_by_topic']}
    # Use measured byte totals; they include serialized tool envelope overhead.
    review['corrections'][3]=review['corrections'][3].replace('109200serializedbytes',str(original[0]['tool_result_bytes'])+'serializedbytes')
    save(audit/'review.json',review);save(ROOT/'verification/disc-camera-animation-review.json',review)
    transcript='CAMERA / ANIMATION IN ACTUAL DISC WORLD — AUDIT\n\nWHO DID WHAT\n'+who+'\n\nCORRECTIONS / LIMITS\n'+'\n'.join(review['corrections'])
    transcript+='\n\nORIGINAL — EXACT SYSTEM / USER / TOOL / RESPONSES\n'+json.dumps(first,ensure_ascii=False,indent=2)
    transcript+='\n\nCOMPACT CURRENT EVIDENCE — SAME ORDINARY QUESTION\n'+json.dumps(revised,ensure_ascii=False,indent=2)
    transcript+='\n\nCOORDINATOR VERDICTS\n'+json.dumps({'original':original,'compact_evidence':refined},ensure_ascii=False,indent=2)
    transcript+='\n\nCURRENT CODE SCOPE\n'+read(ROOT/'config.json')['disc_world_actor_progress']+'\nFull goal active and incomplete.\n'
    (audit/'prompts-and-responses.txt').write_text(transcript)
    checkpoint.update(recorded_at=now,status=review['status'],first_ordinary_answer_rejected=True,same_model_role_review_bounded_correct=True,revised_ordinary_answer_bounded_correct=True,original_ordinary_seconds=original[0]['SDK_reported_seconds'],revised_ordinary_seconds=refined[0]['SDK_reported_seconds'],local_model_general_reliability_proved=False,native_new_response_verified=False,known_compute_jobs='terminal',model_idle=True,new_training=False,default_promoted=False,review=str(ROOT/'verification/disc-camera-animation-review.json'),transcript=str(audit/'prompts-and-responses.txt'))
    checkpoint['evidence']+=['verification/disc-camera-animation-MCP-check.json','verification/disc-camera-animation-review.json',str((audit/'prompts-and-responses.txt').relative_to(ROOT))]
    save(ROOT/'verification/disc-camera-animation-checkpoint.json',checkpoint)
    for name in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']:
        path=ROOT/'verification'/name;value=read(path);value.update(disc_camera_animation_checkpoint=checkpoint,disc_camera_animation_review=review)
        if name=='current-runtime-state.json':value.update(recorded_at=now,models=models,local_inference_jobs='Terminal: first ordinary answer rejected; same-model role inventory correct; compact-current-evidence ordinary answer correct. Model idle. Native response unverified.',latest_API_ease_review=str(ROOT/'verification/disc-camera-animation-review.json'))
        if name=='requirements-audit.json':
            for item in value['requirements']:
                if 'decompilation test'in item['requirement']:item['evidence']=list(dict.fromkeys(item['evidence']+checkpoint['evidence']))
        save(path,value)
    note='\nLOCAL INFERENCE REVIEW — '+now+'\n\n'+who+'\n\nRESULT\nInitial ordinary answer rejected for current helper omissions and mixed historical scope. Role inventory correct. Same ordinary question after bounded evidence change answered correctly; SDKreported'+str(round(original[0]['SDK_reported_seconds'],2))+'s before/'+str(round(refined[0]['SDK_reported_seconds'],2))+'s after. Different response lengths/cache and small sample prevent a general benchmark claim. Native Chat remains unverified.\n\nEXACT PROMPTS / TOOLS / RESPONSES\n'+str(audit/'prompts-and-responses.txt')+'\nFull goal active and incomplete.\n'
    for name in ['POST REVIEW.txt','CURRENT DECOMPILATION.txt','projects/black-ice-white-noise/restoration/READ ME.txt']:
        with(ROOT/name).open('a')as handle:handle.write(note)
    path=ROOT/'START HERE.txt';text=path.read_text();a=text.index('LOCAL INFERENCE RESULT\n');b=text.index('TRY ADVERTISING ASSISTANT\n',a)
    text=text[:a]+('LOCAL INFERENCE RESULT\nThe newest camera/animation evidence is installed. Native Chat access timed out; current native provider and responses remain unverified. SDK fallback logs are separate. The first ordinary answer mixed historical limitations and was rejected. After shrinking evidence reports, the same ordinary question answered the current scope correctly. The same-model Analyst/Reviewer inventory was also correct. This is a bounded sample, not general reliability proof. Everyday base remains loaded and idle; no new training or default promotion.\n\nTry: Are camera and animation really running now? What is still mocked, and can I play the rebuilt game?\n\nExact prompts, tool calls, answers and reviews:\n'+str(audit/'prompts-and-responses.txt')+'\n\n')+text[b:];path.write_text(text)
    subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts/install_chat_runtime.py')],check=True)
    print(json.dumps({'components':106,'camera_cases':768,'animation_cases':1538,'combined_cases':16,'configured_world_scripts':5,'reached_world_scripts':2,'revised_bounded_answer_correct':True,'native_verified':False,'model_idle':True,'audit':str(audit)}))
if __name__=='__main__':main()
