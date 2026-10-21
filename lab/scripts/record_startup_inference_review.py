"""Record coordinator review of the exact local startup scope answer."""
import hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
save=lambda p,v:p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    raw=Path(read(ROOT/'verification/easy-startup-caller-scope-scope-pointer.json')['directory']);protocol=read(raw/'protocol.json');item=protocol['results'][0]
    assert protocol['status']=='completed_pending_coordinator_review'and not item['quality_flags']and item['words']<120
    assert all(p['stats']['stopReason']=='eosFound'for p in item['prediction_stats'])
    cp=read(ROOT/'verification/startup-CPU-progress-checkpoint.json');assert cp['caller_instruction_coverage']==[82,82]and cp['earlier_startup_capture_still_supplied']
    answer=item['answer'];assert all(t in answer for t in ['not removed','82','8 cases','16 task','128','Eight caller helpers','earlier startup capture','Full boot and playability remain unverified'])
    assert all(target in answer for target in cp['scripted_caller_helpers'])
    requests=[block['toolCallRequest']for event in item['events']for block in event['content']if block['type']=='toolCallRequest']
    assert len(requests)==1 and requests[0]['name']=='project_evidence'and requests[0]['arguments']=={'topic':'render_startup'}
    contracts=read(ROOT/'verification/startup-CPU-host-contracts.json');assert contracts['status']=='startup_CPU_host_contracts_pass'and contracts['cases']==20
    now=datetime.now(timezone.utc);out=ROOT/'verification/startup-inference-review'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    files=[raw/'protocol.json',raw/'prompts-and-responses.txt',ROOT/'scripts/test_startup_caller_scope.py',ROOT/'scripts/check_startup_cpu_contracts.py',ROOT/'verification/startup-CPU-host-contracts.json',ROOT/'verification/startup-CPU-progress-checkpoint.json',ROOT/'verification/startup-CPU-progress-MCP-check.json',ROOT/'chat_tools.py',Path(__file__)]
    manifest=[]
    for p in files:
        target=out/p.name;shutil.copy2(p,target);assert sha(p)==sha(target);manifest.append(dict(source=str(p),snapshot=str(target),sha256=sha(p)))
    review=dict(status='accepted_scoped_startup_caller_answer',recorded_at=now.isoformat(),directory=str(out),model=protocol['model'],interface=protocol['interface'],words=item['words'],seconds=item['seconds'],quality_flags=item['quality_flags'],tool_calls=requests,coordinator_semantic_review='Exact answer correctly states standalone caller coverage/case and source-creation counts, complete state comparison, all eight ABI-script addresses, retained startup capture and unverified boot/playability. It does not summarize the separate56 RNG cases; accepted for the requested caller/capture/helper scope, not as a complete progress inventory or general reliability proof.',native_Chat_verified=False,new_training=False,model_defaults_changed=False,local_model_authored_new_C=False,whole_goal_complete=False,files=manifest)
    save(out/'review.json',review);save(ROOT/'verification/startup-inference-review.json',review)
    note='LATEST LOCAL QUESTION — STARTUP CALLER SCOPE\n'+now.isoformat()+'\n\nEveryday27B6bit/32K/one-worker model:77 words in15.98seconds, one project_evidence(render_startup) call, natural completion and no output quality flags. Coordinator accepted the scoped caller/helper/capture facts. Separate56-case RNG proof remains in the decompilation checkpoint. No new training/model default changes. Backend SDK tested; native LM Studio Chat remains unverified.\n\nUSER PROMPT\n'+protocol['questions'][0]['user']+'\n\nEXACT LOCAL ANSWER\n'+answer+'\n\nEXACT SYSTEM PROMPT, TOOL CALL AND RESPONSE\n'+str(out/'prompts-and-responses.txt')+'\n\nREVIEW\n'+str(out/'review.json')+'\n\n'
    p=ROOT/'CURRENT LOCAL INFERENCE.txt';p.write_text(note+p.read_text())
    p=ROOT/'START HERE.txt';p.write_text('Latest separate startup progress:56 RNG cases/fullCPU-privateRAM match;8 caller cases/all82 caller instructions/16 source task creations per case. Eight caller helper providers remain scripts; earlier startup capture still required by connected game run. Full boot/playability remain unverified.20 host guard/observation/supplied-suspension contracts pass.\nLocal assistant:77 words/15.98seconds with one evidence tool call, accepted scoped answer and saved exact prompt/response. Backend SDK, not verified native Chat.\nAudit: '+str(out)+'\n\n'+p.read_text())
    (out/'readable-results.txt').write_text(note)
    print(json.dumps({k:review[k]for k in ['status','directory','seconds','words']}))
if __name__=='__main__':main()
