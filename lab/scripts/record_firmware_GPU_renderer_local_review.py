"""Retain exact local explanation, guarded-code gate and current source scope."""
import hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
save=lambda p,v:p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    review=json.loads((ROOT/'verification/firmware-GPU-renderer-review.json').read_text());out=Path(review['directory']);local=Path(json.loads((ROOT/'verification/easy-firmware-GPU-renderer-scope-pointer.json').read_text())['directory']);run=json.loads((local/'protocol.json').read_text());answer=run['results'][0]
    assert not answer['quality_flags']and answer['words']<=130
    assert 'resumed firmware GPU renderer is reconstructed C' in answer['answer'] and 'initial 8-instruction GPU mailbox wait' in answer['answer'] and 'main firmware CPU remain original' in answer['answer']
    assert 'full rebuilt game cannot boot yet' in answer['answer'] and 'supplied 60,000-byte stub' in answer['answer']
    local_review=dict(status='local_renderer_C_and_remaining_boot_scope_accepted',directory=str(local),words=answer['words'],seconds=answer['seconds'],semantic_note='Renderer has both standalone comparisons and a live firmware-prefix link. Model standaloneprefix wording means separatefrom existing connectedgame chain; it should not erase the provenlive link.',same_model_roles_not_independent=True,diagnostic_prompt_not_heldout_benchmark=True,new_weight_training=False,model_defaults_changed=False,native_UI_new_prompt_verified=False)
    run['results'][0]['semantic_review']=local_review['status'];save(local/'protocol.json',run);save(local/'coordinator-review.json',local_review);save(out/'local-review.json',local_review)
    guard=json.loads((ROOT/'verification/firmware-GPU-renderer-code-guard.json').read_text());assert guard['return_code']==7 and guard['input_state_unchanged']and not guard['silent_fallback']
    save(out/'code-guard-review.json',guard)
    files=[local/'protocol.json',local/'prompts-and-responses.txt',local/'coordinator-review.json',ROOT/'scripts/test_firmware_GPU_renderer_chat_scope.py',ROOT/'scripts/record_firmware_GPU_renderer_local_review.py',ROOT/'verification/firmware-GPU-renderer-code-guard.json',ROOT/'verification/game-firstboot-MCP-check.json']
    for i,source in enumerate(files):
        dest=out/f'local-{i:02d}-{source.name}';shutil.copy2(source,dest);review['manifest'].append(dict(source=str(source),snapshot=str(dest),sha256=sha(dest)))
    review.update(local_review=local_review,changed_instruction_guard=guard,new_weight_training=False,model_defaults_changed=False,whole_goal_complete=False)
    save(out/'review.json',review);save(ROOT/'verification/firmware-GPU-renderer-review.json',review)
    (out/'who-prompts-and-responses.txt').write_text('COORDINATOR\nGuardedC renderer generation, independentoriginal/C body comparisons and livefirmware link. No model-generated sourcebody added. Sharedblitter/MMIO/DMA andinitialGPUtail aredeclared providers. MainCPU/initialGPUwait/discboot/fullgoal remainincomplete.\n\nLOCAL ASSISTANT — SAME MODEL ROLES, SDK, NOT NATIVE CHAT\n'+(local/'prompts-and-responses.txt').read_text()+'\nCOORDINATOR SEMANTIC REVIEW:\n'+json.dumps(local_review,indent=2)+'\n\nSOURCE / BYTE-GUARD PROOF:\n'+str(out/'review.json')+'\n')
    feedback=ROOT/'training/feedback/firmware-GPU-renderer-20261015.jsonl';feedback.write_text(json.dumps(dict(directory=str(local),status=local_review['status'],used_in_weight_training=False,independent_heldout_eval=False))+'\n')
    now=datetime.now(timezone.utc).isoformat();ad=ROOT/'verification/advertising-analysis-v2-review/20261015T010126.787930Z';native=ROOT/'verification/firmware-relocation-review/20261015T011820.772829Z/native-chat-export.md'
    (ROOT/'START HERE.txt').write_text(f'''LOCAL AI — START HERE
Updated {now}

1. LM Studio Chat: “BIWN — Local Roles and Firmware Checkpoint” contains priorverified visibleprompts/responses.
2. Everyday model advertising-scholar; choose Game Assistant or Advertising Assistant and enable local-ai-lab.
3. Afterrestart, double-click Game Model.command or Advertising Model.command, then select theloadedmodel inChat.
Ask: Is the firmware GPU renderer now C, and can the fullgame boot yet?
Picture: Show the current interior drawing.

GAME PROGRESS
The resumedfirmware GPUrenderer nowruns asC:1,317instructionversions/104,628instructions/1,352standalone checkpoints matchoriginal; liveprefix output/state/traces matchtoo. C source recreatescodeoverlays/patches throughits ownstores/sharedblitter DMA, withnohost overlaycopy ororiginalGPUrenderer execution. C DSP/videoIRQ precede it. MainfirmwareCPU andinitial8instructionGPUwait remainoriginal; disc header/load/dispatch/globalclocks/fullboot unfinished. ExistinggameC test stillsupplies initial60000byte stub. Game notplayable yet.

LOCAL INFERENCE
SDK explanation84words/18.83seconds correctlysaid rendererC, originalinitialGPUwait/mainCPU, andincompletefullboot. One model playsroles; thisis adiagnostic,not broadreliability. NewnativeUI review/serverrefresh remainsunverified; backgroundSDK work followsuserpreference.
{out/'who-prompts-and-responses.txt'}

PRIOR NATIVE CHAT EXPORT
{native}

ADVERTISING
AnalysisPilotv2 trained/loadable butexperimental/unpromoted aftersemantic/rubric/toolformat failures. Everydaymodel unchanged. Correctedlesson:
{ad/'coordinator-corrected-lesson.txt'}

SOURCE AND LOCAL REVIEW
{out/'review.json'}
{out/'local-review.json'}
''')
    (ROOT/'CURRENT LOCAL INFERENCE.txt').write_text(f'''CURRENT LOCAL INFERENCE
Updated {now}

Everyday27B/6bit advertising-scholar,32,768context,oneworker,60minuteTTL. Dailyweights/presets unchanged. AdvertisingAnalysisPilotv2 trained/loadable/unpromoted.

NEW SOURCE RESULT
GuardedC firmwareGPUrenderer reproducescodeoverlays, drawingplane andsourceGO clear.1,317versions at1,013PCs,104,628instructions and1,352standalone checkpoints matchoriginal; liveprefix withC DSP/CvideoIRQ matchesCPU/privateRAM/logicalGPU/peripherals/PC/bytetraces/counts. Nocaptured rendererboundary/hostoverlaycopy/originalGPUrenderer instructions. Sharedblitter/MMIO/DMA/architecturalIRQ model andinitial20GPUtail bytes remainproviders. Changedinstructionbytes rejectwithstatus7,stateunchanged andnofallback.
MainfirmwareCPU andinitial8instructionGPUmailboxwait stilloriginal. Explicitsequencing/VBI/globalphysicalclocks, disc header/loading/naturalgamedispatch andfullplayability remainunverified. ExistinggameC chainstillprovides60000byteinitialstub.
{out/'review.json'}

LOCAL SDK OUTPUT TEST
84words/18.83seconds, oneevidence lookup,EOS. Core rendererC/initialGPUwait/mainCPU/fullboot/gamechain scopeaccepted. Minorwordingstandaloneprefix meansseparatefromgamechain; rendereralso hasverifiedlivefirmwareprefix link. Sameweights/diagnosticquestion,nobroadreliability/speedup/256GBbenchmark.
{out/'who-prompts-and-responses.txt'}
{out/'local-review.json'}

NATIVE CHAT
Earliervisible toolcall and84/88wordroleanswers remain in“BIWN — Local Roles and Firmware Checkpoint.” No newUIattemptafterAXtimeout. Newinstalled evidence/freshstdio/SDK verified; nativeMCPprocessrefresh pendingverification. Nativehistory neverinjected/edited:
{native}

ADVERTISING
V2 pilotpreviouslytrained36records(30/3/3),32steps/rank8/last2layers. Testloss1.82244->1.33735;packageloss1.33565. Load/textinferenceverified; semantic/grammar/rubric/toolformat errorspreventpromotion. Dailybase remainsactive.
{ad/'coordinator-corrected-lesson.txt'}
{ad/'review.json'}

NEXT
InitialGPUwait andremainingmainCPU firmware relocation/trampoline/video waits; realdisc header/authenticatedloading/naturalgame dispatch; expand otherGPU bytevariants/inputs andwholegame paths/globalclocks. Future256GBprofileunbenchmarked; wholegoalactive/incomplete.
''')
    for name in ['START HERE.txt','CURRENT LOCAL INFERENCE.txt']:
        dest=out/('current-'+name);shutil.copy2(ROOT/name,dest)
    path=ROOT/'verification/NEXT SOURCE AND INFERENCE WORK.json';n=json.loads(path.read_text());n.update(local_audit=str(out),last_turn_classification='progress',local_roles_this_turn=local_review,new_training_this_turn=False);save(path,n)
    assert all(sha(Path(x['snapshot']))==x['sha256']for x in review['manifest'])
    assert len((ROOT/'START HERE.txt').read_text().splitlines())<45
    print(json.dumps(dict(audit=str(out),local_words=answer['words'],local_seconds=answer['seconds'],whole_goal_complete=False)))

if __name__=='__main__':main()
