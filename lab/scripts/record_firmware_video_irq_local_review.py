"""Finalize source comparison, exact local responses, and current daily pages."""
import hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];RUNTIME=Path.home()/'.lmstudio/local-ai-lab'
save=lambda p,v:p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    review=json.loads((ROOT/'verification/firmware-video-IRQ-review.json').read_text());out=Path(review['directory']);proof=json.loads((ROOT/'verification/firmware-video-IRQ-live-checks.json').read_text())
    first=Path(review['first_local_scope_diagnostic']);second=Path(json.loads((ROOT/'verification/easy-firmware-video-IRQ-scope-pointer.json').read_text())['directory']);run=json.loads((second/'protocol.json').read_text());answer=run['results'][0]
    assert answer['words']<=130 and not answer['quality_flags']
    assert 'The C CPU video-IRQ handler acknowledges' in answer['answer'] and 'renderer is not reconstructed in C' in answer['answer']
    assert '345 code locations' not in answer['answer'] and 'remains unported to C' in answer['answer']
    local=dict(status='local_replay_handler_GPU_and_fullboot_scope_accepted',first_run=str(first),replay=str(second),first_words=91,first_seconds=18.42600949999178,replay_words=answer['words'],replay_seconds=answer['seconds'],first_issue='345byte-changeobservations incorrectly described as345code locations; actual239distinct PCs',source_note_added='Explicit observation/uniquePC/instruction-version units',same_prompt_reused=True,same_model_roles_not_independent=True,broad_reliability_or_speedup_verified=False,model_weights_and_defaults_unchanged=True,new_weight_training=False,native_UI_new_review_verified=False,semantic_note='Only CPU-side IRQ/mailbox path is C refers to the handler/renderer stages in this question. The preceding DSP is also C; mainfirmwareCPU/GPU remain original.')
    run['results'][0]['semantic_review']=local['status'];save(second/'protocol.json',run);save(second/'coordinator-review.json',local);save(out/'local-replay-review.json',local)
    raw=Path(proof['C_directory']);native_followup=Path(proof['GPU_followup_native_directory'])
    assert proof['GPU_followup_after_original_and_C_IRQ_match']and proof['GPU_distinct_changed_PC_addresses']==239
    save(out/'proof-before-followup.json',review['proof']);review['proof']=proof;review['local_replay']=local
    files=[ROOT/'verification/firmware-video-IRQ-live-checks.json',ROOT/'scripts/check_biwn_firmware_video_irq_live.py',ROOT/'scripts/observe_biwn_relocated_firmware.py',ROOT/'scripts/test_firmware_video_irq_chat_scope.py',ROOT/'scripts/record_firmware_video_irq_local_review.py',ROOT/'verification/game-firstboot-MCP-check.json']
    for folder in [raw,native_followup]:files.extend(folder/name for name in ['protocol.json','report.json','status.json','CPU-video-IRQ-observation.json','GPU-after-video-IRQ-resume.json','GPU-after-video-IRQ-resume.bin','RAM-after-video-IRQ.bin','RAM-after-video-IRQ-GPU-resume.bin'])
    for folder in [first,second]:files.extend(folder/name for name in ['protocol.json','prompts-and-responses.txt','coordinator-review.json'])
    for i,source in enumerate(files):
        dest=out/f'final-{i:02d}-{source.name}';shutil.copy2(source,dest);review['manifest'].append(dict(source=str(source),snapshot=str(dest),sha256=sha(dest)))
    compact=json.loads((out/'compact-evidence.json').read_text());compact.update(GPU_followup_after_original_and_C_IRQ_match=True,GPU_followup_full4416_RAM_peripherals_PC_byte_trace_match=True,GPU_code_change_count_units={'observations':345,'distinct_executed_PC_addresses':239,'instruction_versions':1317,'meaning':'Re-visiting an executedPC found changed instruction bytes; not every code store and not345 unique locations.'})
    review['evidence']=compact;save(out/'compact-evidence.json',compact)
    for base in [ROOT,RUNTIME]:
        folder=Path(json.loads((base/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);path=folder/'emulator-runtime/summary.json';data=json.loads(path.read_text());data['firmware_bootstrap_DSP_progress']=compact;save(path,data)
    review.update(status='C_videoIRQ_and_originalGPU_followup_verified_local_scope_replay_pass_fullgoal_incomplete',classification='progress',new_weight_training=False,model_defaults_changed=False,whole_goal_complete=False)
    save(out/'review.json',review);save(ROOT/'verification/firmware-video-IRQ-review.json',review)
    (out/'who-prompts-and-responses.txt').write_text('COORDINATOR\nTranslated327CPUvideoIRQ/helper instructions and realexceptionentry; no new model-generated source body. Original/C live comparison and originalGPUfollowup match. MainCPU/GPU stilloriginal; fullgoalunfinished.\n\nLOCAL ROLES — SAME MODEL, SDK, NOT NATIVE CHAT\nFIRST EXACT SYSTEM/USER/TOOLS/RESPONSE:\n'+(first/'prompts-and-responses.txt').read_text()+'\nREPLAY AFTER SOURCE COUNT-UNIT NOTE:\n'+(second/'prompts-and-responses.txt').read_text()+'\nCOORDINATOR REVIEW:\n'+json.dumps(local,indent=2)+'\n\nFULL SOURCE PROOF:\n'+str(out/'review.json')+'\n')
    feedback=ROOT/'training/feedback/firmware-video-IRQ-20261015.jsonl';feedback.write_text('\n'.join(json.dumps(dict(directory=str(path),status=state,used_in_weight_training=False,independent_heldout_eval=False))for path,state in [(first,'code_change_unit_correction_required'),(second,'scope_replay_accepted')])+'\n')
    now=datetime.now(timezone.utc).isoformat();ad=ROOT/'verification/advertising-analysis-v2-review/20261015T010126.787930Z';native=ROOT/'verification/firmware-relocation-review/20261015T011820.772829Z/native-chat-export.md'
    (ROOT/'START HERE.txt').write_text(f'''LOCAL AI — START HERE
Updated {now}

1. Open LM Studio Chat: “BIWN — Local Roles and Firmware Checkpoint” contains the prior verified visible prompts/responses.
2. Everyday model advertising-scholar; choose Game Assistant or Advertising Assistant and enable local-ai-lab.
3. After restart, double-click Game Model.command or Advertising Model.command, then select the loaded model in Chat.
Ask: What acknowledges the firmware GPU mailbox, and is its renderer reconstructed yet?
Picture: Show the current interior drawing.

GAME PROGRESS
C DSP462instructions and C videoIRQ327instructions are checked and linked to live firmware state. One videoIRQ executes660source steps,acknowledges GPU mailbox and restoresCPU. OriginalGPU then stops; its output/state match after either original orC IRQ. GPUrenderer remains original with1,317observed instructionversions,345byte-changeobservations at239distinctPCs. MainfirmwareCPU/disc header-load/globalclocks/fullboot remain unfinished. Existing gameC test stillsupplies its initial60000byte stub. Game notplayable yet.

LOCAL INFERENCE
SDK replay81words/13.70seconds correctly distinguishes C CPU IRQ from originalGPU and nofullboot. First91word draft misstated code-change units; exactoutputs and correctionretained. Same-modelroles/reusedquestion/warmcache are diagnostic,notbroadreliability orspeedup. NativeUI/newserverrefresh remains unverified after priorAXtimeout; backgroundSDK tests proceed per userpreference.
{out/'who-prompts-and-responses.txt'}

PRIOR NATIVE CHAT EXPORT
{native}

ADVERTISING
Analysis Pilot v2 is trained/loadable,experimental andunpromoted aftersemantic/rubric/tool-format failures; everydaymodel unchanged. Corrected lesson:
{ad/'coordinator-corrected-lesson.txt'}

SOURCE / INFERENCE AUDIT
{out/'review.json'}
{out/'local-replay-review.json'}
''')
    (ROOT/'CURRENT LOCAL INFERENCE.txt').write_text(f'''CURRENT LOCAL INFERENCE
Updated {now}

Everyday27B/6bit advertising-scholar,32,768context,oneworker,60minuteTTL. Dailyweights/presets unchanged. AdvertisingAnalysisPilotv2 remains trained/loadable/unpromoted.

SOURCE PROGRESS
C firmwareDSP462instructions checksROM fromliveCPU-loaded state. New C videoIRQ327instructions/660steps, real6byteframe, sourceF03F4Cack/counterincrement/RTE restoration matchindependentoriginalrun. Nohostmailboxclear, capturedIRQboundary, CPUreseed ororiginalhandlerinstructions onCpath. MainfirmwareCPU andGPU remainoriginalaround thosecomponents.
OriginalGPU aftereither original/C IRQ matchesfull4416GPU/private2MBRAM/peripherals/PC andbyte traces; sourceGO clears after104,628instructions. Drawingplane100000 changes4976bytes; physicalscanout unverified.1,317observed instructionversions and345byte-changeobservations at239distinctPCs identifyunportedself-modifyingrenderer. ExistinggameC startup/movie/world chainstill supplies initial60000byte stub. No fullboot/playability/globaltiming proof.
{out/'review.json'}

LOCAL SDK ROLE TEST
One evidence lookup. First91words/18.43seconds correctlydescribed CPU/GPU/fullboot scopebut incorrectlycalled345observations345locations. Explicitunits added; samequestionreplay81words/13.70seconds keptcore distinction andavoidedincorrectunit. Sameweights/reusedsource/warmcache; nobroadreliability/causalspeedup claims. No new weighttraining.
{out/'who-prompts-and-responses.txt'}
{out/'local-replay-review.json'}

NATIVE CHAT
Prior observedtool call and84/88word roleanswers remainvisible in“BIWN — Local Roles and Firmware Checkpoint.” No new UIattemptafterAXtimeout. Newinstalled evidence isverified throughfreshstdio/SDK; nativeMCPrefresh pendingverification. Nativehistory neverinjected/edited:
{native}

ADVERTISING
V2 pilotpreviouslytrained36examples(30/3/3),32steps/rank8/last2layers. Testloss1.82244->1.33735;packageloss1.33565. Load/textinferenceverified; semantic/grammar/rubric/toolformat failurespreventpromotion. Sourcecheckedlesson/audit:
{ad/'coordinator-corrected-lesson.txt'}
{ad/'review.json'}

NEXT
Reconstruct/compare GPU bytecodevariants with codeoverlay andimmediatepatch provenance, then remainingfirmwareCPU/disc loading/naturalgame dispatch/globalclocks/othergamepaths. Future256GBprofileunbenchmarked; wholegoalactive/incomplete.
''')
    for name in ['START HERE.txt','CURRENT LOCAL INFERENCE.txt']:
        dest=out/('current-'+name);shutil.copy2(ROOT/name,dest)
    npath=ROOT/'verification/NEXT SOURCE AND INFERENCE WORK.json';n=json.loads(npath.read_text());n.update(local_audit=str(out),last_turn_classification='progress',local_roles_this_turn=local,new_training_this_turn=False,GPU_followup_after_original_and_C_IRQ_match=True);save(npath,n)
    assert all(sha(Path(x['snapshot']))==x['sha256']for x in review['manifest'])
    assert len((ROOT/'START HERE.txt').read_text().splitlines())<45
    print(json.dumps(dict(audit=str(out),local_words=answer['words'],seconds=answer['seconds'],whole_goal_complete=False)))

if __name__=='__main__':main()
