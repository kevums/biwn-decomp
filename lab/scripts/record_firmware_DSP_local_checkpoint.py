"""Retain local inference diagnostics and the next GPU/CPU mailbox evidence."""
import hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import binary_tools
save=lambda p,v:p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    review=json.loads((ROOT/'verification/firmware-DSP-progress-review.json').read_text());out=Path(review['directory'])
    first=Path(review['first_local_scope_diagnostic']);second=Path(json.loads((ROOT/'verification/easy-firmware-DSP-scope-pointer.json').read_text())['directory'])
    run=json.loads((second/'protocol.json').read_text());answer=run['results'][0]
    assert 'original CPU loads DSP code/data' in answer['answer'] and 'Reconstructed C DSP executes decryption/arithmetic' in answer['answer']
    assert 'not linked into the existing game test' in answer['answer'] and not answer['quality_flags'] and answer['words']<=130
    local_review=dict(status='local_replay_processor_attribution_and_incomplete_boot_scope_accepted',recorded_at=datetime.now(timezone.utc).isoformat(),first_run=str(first),first_run_status='CPU falsely attributed DSP decryption/check; rejected attribution',replay=str(second),replay_words=answer['words'],replay_seconds=answer['seconds'],semantic_notes=['CPU loads/starts/waits/reads success; reconstructedDSP performs decryption/arithmetic/ROM check and clearsGO.','516 checkpoints are standalone comparison checkpoints, not instructions. Live prefix and existing game chain remain separate.','Model uses independent to mean a separate game test; tests share code and pinned bus, so this is not independent hardware or model verification.'],same_prompt_reused=True,source_processor_note_added=True,warm_cache_or_context_effects_not_controlled=True,native_UI_new_prompt_sent=False,native_MCP_runtime_refresh_verified=False,model_weights_and_defaults_unchanged=True,used_for_weight_training=False,broad_reliability_verified=False)
    run['results'][0]['semantic_review']=local_review['status'];save(second/'protocol.json',run);save(second/'coordinator-review.json',local_review)
    save(out/'local-replay-review.json',local_review)
    current_GPU=json.loads((ROOT/'verification/firmware-GPU-shutdown-observation.json').read_text());GPU=current_GPU['GPU_shutdown_observation'];raw=Path(current_GPU['directory'])
    assert current_GPU['emulator_shutdown_completed'] and GPU['final_control']&1 and not GPU['source_GPU_C_verified']
    assert GPU['instructions']==GPU['execution_blocks']+GPU['executed_branch_delay_slots']
    assert any(row['address']==0xf03a8e for row in GPU['visited_instructions'])
    ram=(raw/'RAM-after-CPU-continuation.bin').read_bytes();gpu=(raw/'GPU-after-shutdown-probe.bin').read_bytes()
    assert int.from_bytes(ram[0x100:0x104],'big')==0x194c90
    assert int.from_bytes(gpu[0xf4c:0xf50],'big')==1 and int.from_bytes(gpu[0xf50:0xf54],'big')==1
    bios=(ROOT/'render-assets/jaguarcd_bios.bin').read_bytes();rows,decoder=binary_tools.m68k_instructions(bios[0x16eac:0x16f64],0x194c90)
    assert next(r for r in rows if r['address']==0x194d18)['assembly']=='clr.l $f03f4c.l'
    dependency=dict(status='GPU_mailbox_wait_observed_CPU_video_IRQ_clear_path_identified',source_BIOS_sha256=sha(ROOT/'render-assets/jaguarcd_bios.bin'),GPU_observation_directory=str(raw),GPU_current_PC=GPU['final_GPU_PC'],GPU_instructions=GPU['instructions'],GPU_execution_blocks=GPU['execution_blocks'],GPU_branch_delay_slots=GPU['executed_branch_delay_slots'],mailbox='0xf03f4c',mailbox_value=1,secondary_gate='0xf03f50',secondary_gate_value=1,CPU_current_PC='0x50292',CPU_vector_100='0x194c90',CPU_mailbox_clear_PC='0x194d18',CPU_mailbox_clear_instruction='clr.l $f03f4c.l',CPU_video_handler_rows=rows,decoder=decoder,CPU_video_handler_executed_in_this_probe=False,mailbox_host_poked=False,GPU_shutdown_C_verified=False,global_schedule_verified=False,next_action='Deliver an explicitly declared video IRQ and execute its actualCPU handler; observe mailbox acknowledgement and GPU progression without host flag writes. Then reconstruct/compare the reachedCPU/GPU blocks and global event schedule.')
    save(out/'GPU-mailbox-dependency.json',dependency);save(ROOT/'verification/firmware-GPU-mailbox-dependency.json',dependency)
    compact=json.loads((out/'compact-evidence.json').read_text());compact['next_GPU_CPU_dependency']={k:dependency[k]for k in ['status','GPU_current_PC','mailbox','mailbox_value','secondary_gate','secondary_gate_value','CPU_current_PC','CPU_vector_100','CPU_mailbox_clear_PC','CPU_mailbox_clear_instruction','CPU_video_handler_executed_in_this_probe','mailbox_host_poked','GPU_shutdown_C_verified','global_schedule_verified','next_action']};save(out/'compact-evidence.json',compact)
    for base in [ROOT,Path.home()/'.lmstudio/local-ai-lab']:
        folder=Path(json.loads((base/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);p=folder/'emulator-runtime/summary.json';data=json.loads(p.read_text());data['firmware_bootstrap_DSP_progress']=compact;save(p,data)
    feedback=ROOT/'training/feedback/firmware-DSP-20261015.jsonl'
    feedback.write_text('\n'.join(json.dumps(dict(directory=str(p),question='same130wordfirmwareDSPscopeprompt',status=kind,used_in_weight_training=False,independent_heldout_eval=False))for p,kind in [(first,'CPU_decryption_attribution_rejected'),(second,'processor_attribution_corrected_scope_accepted')])+'\n')
    files=[ROOT/'chat_tools.py',ROOT/'verification/firmware-DSP-MCP-check.json',ROOT/'verification/game-firstboot-MCP-check.json',ROOT/'verification/firmware-GPU-shutdown-observation.json',raw/'GPU-at-CPU-stop-wait.bin',raw/'GPU-after-shutdown-probe.bin',raw/'GPU-shutdown-observation.json',ROOT/'scripts/test_firmware_DSP_chat_scope.py',ROOT/'scripts/prepare_biwn_firmware_DSP_evidence.py',ROOT/'scripts/record_firmware_DSP_local_checkpoint.py',feedback]
    for p in [first,second]:files.extend([p/'protocol.json',p/'prompts-and-responses.txt',p/'coordinator-review.json'])
    for i,source in enumerate(files):
        target=out/f'local-{i:02d}-{source.name}';shutil.copy2(source,target);review['manifest'].append(dict(source=str(source),snapshot=str(target),sha256=sha(target)))
    review.update(local_replay=local_review,GPU_mailbox_dependency=str(out/'GPU-mailbox-dependency.json'),tool_status='New installed tool and freshstdio evidence smoke passed; nativeUI runtime refresh remains unverified after AX timeout',model_defaults_changed=False,new_weight_training=False,whole_goal_complete=False)
    save(out/'review.json',review);save(ROOT/'verification/firmware-DSP-progress-review.json',review)
    old=(out/'who-prompts-and-responses.txt').read_text()
    (out/'who-prompts-and-responses.txt').write_text(old+'\nLOCAL SDK ROLE DIAGNOSTIC — SAME MODEL\n\nFIRST EXACT SYSTEM/USER/TOOL/ANSWER:\n'+(first/'prompts-and-responses.txt').read_text()+'\nREPLAY AFTER EVIDENCE PROCESSOR NOTE:\n'+(second/'prompts-and-responses.txt').read_text()+'\nCOORDINATOR REVIEW:\n'+json.dumps(local_review,indent=2)+'\nGPU SOURCE DEPENDENCY:\n'+json.dumps({k:v for k,v in dependency.items()if k not in ['CPU_video_handler_rows','decoder']},indent=2)+'\n')
    now=datetime.now(timezone.utc).isoformat();ad=ROOT/'verification/advertising-analysis-v2-review/20261015T010126.787930Z';native=ROOT/'verification/firmware-relocation-review/20261015T011820.772829Z/native-chat-export.md'
    (ROOT/'START HERE.txt').write_text(f'''LOCAL AI — START HERE
Updated {now}

1. Open LM Studio Chat: “BIWN — Local Roles and Firmware Checkpoint” contains the last verified visible role prompts and responses.
2. Everyday model: advertising-scholar. Choose Game Assistant or Advertising Assistant; local-ai-lab supplies evidence and previews.
3. After a restart, double-click Game Model.command or Advertising Model.command, then select the loaded model in Chat.
Ask: What did we verify in the firmware DSP, and can the rebuilt game boot yet?
Picture: Show the current interior drawing.

GAME PROGRESS
A new462instruction firmwareDSP reconstruction completes its ROM check from live originalCPU-loaded state:10,460,888DSPinstructions and516standalone comparison checkpoints match. CPU continues to aGPU wait. No host-decrypted code or successmagic. FirmwareCPU remains original; GPU/video IRQ handshake, disc header/load and firmware-to-game dispatch remain unfinished. Existing game C test still supplies the initial60000byte stub. Full game is not playable.

LOCAL INFERENCE
SDK replay94words/14.32seconds correctly separates CPU loader and C DSP decryption/check. First83word answer misassigned decryption to CPU; both exact outputs retained. Same-model roles and repeated question are diagnostic, not broad reliability. NativeUI request timed out this step; installed new evidence is verified through freshstdio/SDK, native runtime refresh pending.
{out/'who-prompts-and-responses.txt'}

NATIVE CHAT EXPORT FROM PRIOR VERIFIED UI TEST
{native}

ADVERTISING
Analysis Pilot v2 is trained/loadable and experimental. Research/rubric/tool-call failures prevent promotion; daily model unchanged. Source-checked lesson:
{ad/'coordinator-corrected-lesson.txt'}

SOURCE AUDIT AND NEXT DEPENDENCY
{out/'review.json'}
{out/'GPU-mailbox-dependency.json'}
''')
    (ROOT/'CURRENT LOCAL INFERENCE.txt').write_text(f'''CURRENT LOCAL INFERENCE
Updated {now}

Everyday27B/6bit model advertising-scholar,32,768context,oneworker,60minuteTTL. Daily weights/presets unchanged. Advertising Analysis Pilot v2 remains trained/loadable/unpromoted.

NEW FIRMWARE WORK
Coordinator reconstructed462observedDSPinstructions with live byteguards and source-decrypted code.10,460,888instructions,516checkpoints,logicalDSP8496/bothbanks,CPU/privateRAM/peripherals/PCtrace/counts match. Live originalCPU prefix supplies DSPstate; C check completes; CPU resumes naturally. NooriginalDSPexec onCpath, nohostdecryptedcode/successword/CPUreseed.233DSPpipeline bytes remain an explicit initialtail provider. FirmwareCPU/GPU/disc loading/global clocks/fullboot are incomplete.
{out/'review.json'}

LOCAL SDK ROLE TEST
One evidence lookup: first83words/21.32seconds wrongly gave CPU decryption work. Added explicit processor responsibilities; same question replay94words/14.32seconds correctly gives CPU loader/wait and DSP decryption/ROMcheck. Core incompleteboot/separate-game-chain scope accepted. Warm-cache effects and repeated source/question prevent independent benchmark/generalization claims. One model plays all roles.
{out/'who-prompts-and-responses.txt'}
{out/'local-replay-review.json'}

NATIVE CHAT
Prior visible evidence call and84/88word role responses verified in “BIWN — Local Roles and Firmware Checkpoint.” New AX request timed out; no new UI prompt sent. New evidence/code installed and freshstdio/SDK verified; nativeMCPprocess refresh not yet verified. Native exported history was never injected or edited:
{native}

NEXT SOURCE DEPENDENCY
GPU pollsF03F4C=1 atF03A88. ActualCPUvideo handler194C90 contains gated clear at194D18; vector100points to194C90 andF03F50=1. No hostmailboxclear. Handler execution/CPU-GPU-eventlink and GPUshutdownC remain unverified.
{out/'GPU-mailbox-dependency.json'}

ADVERTISING
Previous v2 pilot trained36examples(30/3/3),rank8,last2layers,32steps; testloss1.82244->1.33735,packageloss1.33565. Load/textinference verified; semantic/grammar/rubric/tool-format failures prevent promotion. Dailybase remains active. Source-checked lesson/audit:
{ad/'coordinator-corrected-lesson.txt'}
{ad/'review.json'}
Future256GB profile remains unbenchmarked. Wholegoal incomplete.
''')
    for name in ['START HERE.txt','CURRENT LOCAL INFERENCE.txt']:
        target=out/('current-'+name);shutil.copy2(ROOT/name,target)
    npath=ROOT/'verification/NEXT SOURCE AND INFERENCE WORK.json';n=json.loads(npath.read_text());n.update(local_audit=str(out),last_turn_classification='progress',new_training_this_turn=False,next_GPU_CPU_mailbox_dependency=str(out/'GPU-mailbox-dependency.json'))
    n['next_source_work'][0]=dependency['next_action']+' Then finish firmware/disc header loading and natural game dispatch; the60000byte game stub is still supplied.';save(npath,n)
    assert all(sha(Path(item['snapshot']))==item['sha256']for item in review['manifest'])
    assert len((ROOT/'START HERE.txt').read_text().splitlines())<45
    print(json.dumps(dict(audit=str(out),local_replay_words=answer['words'],GPU_next_dependency=dependency['CPU_mailbox_clear_PC'],whole_goal_complete=False)))

if __name__=='__main__':main()
