"""Review the exact local pool/GPU/scheduling scope answer."""
import hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
save=lambda p,v:p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    raw=Path(read(ROOT/'verification/easy-system-retained-startup-scope-pointer.json')['directory']);protocol=read(raw/'protocol.json');item=protocol['results'][0];answer=item['answer']
    assert protocol['status']=='completed_pending_coordinator_review'and not item['quality_flags']and item['words']<150
    assert all(p['stats']['stopReason']=='eosFound'for p in item['prediction_stats'])
    assert all(t in answer for t in ['100','19','20 total','21 contexts','80 free','GPU state is inherited','DF60','connect startup','earlier captured startup boundary','playability remain unverified'])
    calls=[b['toolCallRequest']for e in item['events']for b in e['content']if b['type']=='toolCallRequest'];assert len(calls)==1 and calls[0]['name']=='project_evidence'and calls[0]['arguments']=={'topic':'render_startup'}
    cp=read(ROOT/'verification/system-retained-startup-checkpoint.json');assert cp['source_system_first_handoff_verified']and not cp['source_startup_scheduler_switching_verified']and cp['earlier_startup_capture_still_supplied_to_connected_game']
    now=datetime.now(timezone.utc);out=ROOT/'verification/system-retained-startup-inference-review'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    files=[raw/'protocol.json',raw/'prompts-and-responses.txt',ROOT/'scripts/test_system_retained_startup_scope.py',ROOT/'scripts/check_system_retained_startup_mcp.py',ROOT/'verification/system-retained-startup-MCP-check.json',ROOT/'verification/system-retained-startup-checkpoint.json',ROOT/'verification/system-CPU-host-contracts.json',ROOT/'chat_tools.py',Path(__file__)]
    manifest=[]
    for p in files:
        target=out/p.name;shutil.copy2(p,target);assert sha(p)==sha(target);manifest.append(dict(source=str(p),snapshot=str(target),sha256=sha(p)))
    review=dict(status='accepted_scoped_system_pool_retained_GPU_and_next_work_answer',recorded_at=now.isoformat(),directory=str(out),model=protocol['model'],interface=protocol['interface'],words=item['words'],seconds=item['seconds'],quality_flags=[],tool_calls=calls,coordinator_semantic_review='Correct source100-record pool,19 startup creations/20includingrender/21contexts/80free, inheritedGPU without reset, and pending startupCDscheduler/health wrapper/actor continuations/connection to later captured boundary. Full4000/globalboot/firmware/tasks/modalbranch/scanout/playability remain unverified. The concise answer implies the older connected capture through pending connection work; it does not explicitly label two separate proof runs or disclose all FrozenRAM/CPU/processor-setup/clock/button/BIOS/blitter providers. Accepted for core pool/GPU/scheduler/connection facts; not complete provider inventory or general reliability.',complete_provider_disclosure=False,native_Chat_verified=False,new_training=False,model_defaults_changed=False,local_model_authored_new_C=False,whole_goal_complete=False,source_review=cp['audit'],files=manifest)
    save(out/'review.json',review);save(ROOT/'verification/system-retained-startup-inference-review.json',review)
    note='LATEST LOCAL QUESTION — SYSTEM POOL / RETAINED STARTUP\n'+now.isoformat()+'\n\nEveryday27B6bit/32K/one-worker model:81 words in15.09seconds, one project_evidence(render_startup) call, natural completion/no mechanical output flags. Coordinator accepted core pool/GPU/scheduler/connection facts. Complete provider inventory remains in source checkpoint; answer omits several supplied initialization/timing/device categories. No new training/default changes. Backend SDK; native Chat unverified.\n\nUSER PROMPT\n'+protocol['questions'][0]['user']+'\n\nEXACT LOCAL ANSWER\n'+answer+'\n\nEXACT SYSTEM PROMPT, TOOL CALL AND RESPONSE\n'+str(out/'prompts-and-responses.txt')+'\n\nREVIEW\n'+str(out/'review.json')+'\n\n'
    p=ROOT/'CURRENT LOCAL INFERENCE.txt';p.write_text(note+p.read_text())
    p=ROOT/'START HERE.txt';p.write_text('Latest system-to-startup check:sourceDD40 builds100free records andsystemcontext, DDF2createsrender and actualTRAP0/RTE enters17C40.19 moretaskcreations form21contexts/80free. Two Native/C runs match retainedGPU/DSP/fullCPU/RAM/peripherals/disc/traces;5 sprite requests percase withno intermediateGPUreset. Context/freepool/17DC2capture are not supplied here. InitialFrozenRAM/CPU/processorsetup/systemclocktick/buttons/BIOS/synchronousDF60completion/blitter/GPUcompletion remain. StartupCDscheduler switching and connection to later movie/world are pending; that later proof stillusesearlierstartupcapture. Fullboot/playability unverified.\nLocal question:81words/15.09seconds, accepted core scoped facts, incomplete provider inventory. SDK, notverifiednativeChat.\nAudit: '+str(out)+'\n\n'+p.read_text())
    (out/'readable-results.txt').write_text(note);print(json.dumps({k:review[k]for k in ['status','directory','seconds','words','complete_provider_disclosure']}))
if __name__=='__main__':main()
