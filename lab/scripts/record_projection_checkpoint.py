"""Publish bounded projection progress and complete local prompt audit."""
import hashlib,json,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
def save(p,value):p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def main():
    proof=read(ROOT/'verification/biwn-gpu-projection-checks.json');native=read(ROOT/'verification/biwn-gpu-projection-original-probes.json');mcp=read(ROOT/'verification/projection-MCP-check.json')
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);workmap=session/'remaining-draw-GPU-workmap.json'
    path=Path(read(ROOT/'verification/easy-gpu-projection-current.json')['directory'])/'protocol.json';protocol=read(path);assert protocol['status']=='completed_pending_coordinator_review'
    samples=[]
    for question in protocol['questions']:
        texts=[];calls=[]
        for event in question['events']:
            if event['role']=='assistant':
                for block in event['content']:
                    if block['type']=='text'and block['text']:texts.append(block['text'])
                    if block['type']=='toolCallRequest':calls.append(block['toolCallRequest'])
        assert len(texts)==1 and len(calls)==1 and calls[0]['name']=='project_evidence'and calls[0]['arguments']=={'topic':'rendering'}
        samples.append(dict(user=question['user'],answer=texts[0],answer_words=len(texts[0].split()),tool_calls=calls,SDK_reported_seconds=question['SDK_reported_seconds']))
    assert len(samples)==2 and all(s['answer_words']==56 for s in samples)
    assert '47'in samples[1]['answer']and '114'in samples[1]['answer']and 'not playable'in samples[0]['answer']
    models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True));assert len(models)==1 and models[0]['identifier']=='advertising-scholar'and models[0]['status']=='idle'and models[0]['queued']==0
    audit=ROOT/'verification/projection-review'/Path(proof['directory']).name;audit.mkdir(parents=True,exist_ok=True)
    files=['scripts/generate_biwn_gpu_projection.py','scripts/check_biwn_gpu_projection.py','scripts/probe_biwn_gpu_projection.py','scripts/biwn_projection_probe_bridge.c','scripts/biwn_render_geometry_device_bridge.c','scripts/biwn_geometry_probe_bridge.c','scripts/biwn_movement_device_bridge.c','scripts/biwn_inventory_device_bridge.c','scripts/generate_biwn_gpu_geometry.py','scripts/check_projection_mcp.py','scripts/test_projection_questions.py','scripts/record_projection_checkpoint.py','chat_tools.py','tools/libbiwn-projection-probe.dylib','projects/black-ice-white-noise/restoration/biwn_gpu_projection.c','projects/black-ice-white-noise/restoration/biwn_gpu_projection.h','verification/biwn-gpu-projection-checks.json','verification/biwn-gpu-projection-original-probes.json','verification/projection-probe-device-build.json','verification/projection-MCP-check.json']
    snapshots=[]
    for name in files:
        source=ROOT/name;target=audit/'snapshots'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target);snapshots.append(dict(source=str(source),snapshot=str(target),sha256=hashlib.sha256(source.read_bytes()).hexdigest()))
    shutil.copy2(path,audit/'SDK-protocol.json');shutil.copy2(workmap,audit/workmap.name)
    failures=[]
    for folder in Path(native['directory']).parent.iterdir():
        status=read(folder/'status.json')
        if status['status']=='terminal_failed':failures.append(dict(directory=str(folder),status=status,kind='original probe assertion wrongly expected projection list head zero; corrected contract, no game code repair'))
    for folder in(ROOT/'verification/easy-gpu-projection').iterdir():
        review=folder/'semantic-review.json'
        if review.exists():failures.append(dict(directory=str(folder),review=read(review),kind='rejected local role answer; incorrect evidence topic, unsupported scope and word limit failure'))
    concise='LOCAL API CHAT — GPU52E0 PROJECTION CHECKPOINT\n\nOne local27Bbase,32k context,oneworker,thinkingoff. Analyst/Reviewer are roles on one model, not independent agents. NativeChat UI timed out120.6164seconds; these SDK messages were not injected into native conversations.\n\n'
    for sample in samples:concise+='USER:\n'+sample['user']+'\n\nTOOL: project_evidence(rendering)\n\nASSISTANT:\n'+sample['answer']+'\n\nWords: '+str(sample['answer_words'])+'; SDK seconds: '+str(sample['SDK_reported_seconds'])+'\n\n'
    concise+='Rejected earlier role answer: chose targeting, falsely called52E0 unrelated toprojection, asserted no10A684constraint,135finalwords plus13preamblewords. Corrected tool routing documentation and added pending GPUprojection evidence to camera/targeting fallback topics. Systemprompt/weights/default unchanged. Retained exact rejected protocol/source/semanticreview. These bounded samples do not prove general reliability, ease or independent multiagent validation.\n'
    (audit/'readable-chat-transcript.txt').write_text(concise)
    details='WHO DID WHAT\nCodex reconstructed450fixed GPU52E0 C blocks, wrote original-state observer/comparison/guards, inspected57A0 chain, extracted58A0/6380, corrected a test expectation, updated local evidence/routing and reviewed outputs. Pinned originalGPU is the oracle; Cside executes no originalGPUinstructions. Local27B answered status/scope questions only. No Codex subagents, local-model-authoredsource, newtraining, model/default/preset/systemprompt promotion.\n\n'
    details+='VALIDATED SCOPE\n'+json.dumps(proof,indent=2)+'\n\nORIGINAL PROBES\n'+json.dumps(native,indent=2)+'\n\nRETAINED FAILURES\n'+json.dumps(failures,indent=2)+'\n\nEXACT SDK SYSTEM / TOOL RETURNS / RESPONSES\n'+json.dumps(protocol,ensure_ascii=False,indent=2)+'\n'
    (audit/'prompts-and-responses.txt').write_text(details)
    review=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='GPU52E0_bounded_C16case_448of450_and_corrected_local_answers_passed_full_goal_incomplete',projection=proof,original=native,installed_MCP=mcp['status'],local_samples=samples,retained_failures=failures,model_idle=True,known_compute_jobs='terminal',native_new_response_verified=False,native_UI_observation='CUA getApp LMStudio timed out after120.6164seconds; lockstate unknown',new_training=False,system_prompt_changed=False,tool_routing_changed=True,default_promoted=False,published_components_unchanged=114,new_published_components=0,live_CPU_E19E_linked=False,full_viewport_proved=False,full_goal_status='active incomplete',next_work='Exercise projection first/last-vertex branches F03558/F03560; reconstruct fullCPU E19E and integrate coherent GPUcontext; reconstruct57A0/58A0/6380chain andCPU E202; then displaylist/overlay,remainingtasks,scenes,audio,boot,fullgame and native easy inference/ad evaluation.',snapshots=snapshots,readable_chat_transcript=str(audit/'readable-chat-transcript.txt'),exact_audit=str(audit/'prompts-and-responses.txt'))
    save(audit/'review.json',review);save(ROOT/'verification/projection-review.json',review)
    heading='GPU52E0 PROJECTION CHECKPOINT — '+review['recorded_at']+'\n\n'
    body='The next GPU projection/sort program now has fixed C matching 16 retained original-GPU observations from real live-scene E19E call boundaries. Registers, flags, accumulator, divider/matrix state, 4KB GPU RAM, 2MB main RAM, direct branch order and external bus shapes/stores match; 16 host guards pass. Coverage is 448/450 instructions. Two first/last-vertex branches remain unobserved; CPU E19E is not yet reconstructed or linked. This is pending work and adds zero to the published 114 selected components. Projection leaves drawing-list head0 or47 at10A684; return alone does not imply zero. The later57A0 routine loads resident58A0 and queues6380; that chain is extracted but unverified. Complete viewport, playable game, audio, boot and remaining tasks/scenes are unfinished. OriginalGPU context is preserved from geometry into these projection probes, but full C cross-kernel integration remains unproved.\n\nCodex authored and checked this code. Local27B answered two scope questions; Analyst/Reviewer are roles on one model. Initial role answer was rejected for wrong routing, unsupported claims and135words. Tool documentation/fallback evidence corrected; repeated identical prompts each return56correctwords with one rendering evidence lookup in about11.18/18.79SDKseconds. NativeChat UI timedout; API transcripts retained, no native conversation injection. No newtraining, preset/systemprompt/weight/default changes. All compute jobs terminal; goal active and incomplete.\n\nREADABLE PROMPTS / RESPONSES\n'+str(audit/'readable-chat-transcript.txt')+'\n\nFULL AUDIT / REJECTED ANSWER\n'+str(audit/'prompts-and-responses.txt')+'\n\n'
    for name in ['CURRENT DECOMPILATION.txt','POST REVIEW.txt']:
        p=ROOT/name;p.write_text(heading+body+p.read_text())
    p=ROOT/'START HERE.txt';p.write_text(heading+'The next GPU projection C passes a bounded16case comparison,448of450instructions; it is pending, unlinked and not another published live component. Full game remains incomplete. Two corrected local API replies are saved below; nativeChat UI still times out.\n\n'+str(audit/'readable-chat-transcript.txt')+'\n\n'+p.read_text())
    print(json.dumps(dict(review=str(ROOT/'verification/projection-review.json'),transcript=review['readable_chat_transcript'],status=review['status'],components=114)))
if __name__=='__main__':main()
