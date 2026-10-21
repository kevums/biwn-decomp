"""Publish initial GPU comparison and bounded next CPU discovery."""
import hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
RUNTIME=Path.home()/'.lmstudio/local-ai-lab'
save=lambda p,v:p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')

def main():
    proof=json.loads((ROOT/'verification/firmware-initial-GPU-live-checks.json').read_text())
    report=json.loads((Path(proof['C_directory'])/'report.json').read_text())
    cpu=report['CPU_continuation_after_GPU']
    assert proof['initial_wait_source_instruction_coverage']==[8,8] and cpu['steps']==433
    assert cpu['final_CPU']['pc']==0x100c and not cpu['CPU_reseeded']
    out=ROOT/'verification/firmware-initial-GPU-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    prior=json.loads((ROOT/'verification/firmware-GPU-renderer-review.json').read_text())
    compact=dict(prior['evidence'])
    compact.update(status=proof['status'],recorded_at=proof['recorded_at'],audit=str(out),full_report=str(ROOT/'verification/firmware-initial-GPU-live-checks.json'),GPU_initial_mailbox_wait_still_original=False,GPU_initial_mailbox_wait_C_verified=True,GPU_initial_wait_source_instruction_coverage=[8,8],GPU_initial_wait_instructions=259413,GPU_initial_wait_execution_blocks=194561,GPU_firmware_C_verified=False,GPU_firmware_C_scope='Observed initial eight-instruction wait and resumed renderer are C; other firmware GPU paths remain unverified.',main_firmware_CPU_still_original=True)
    compact['processor_responsibilities'].pop('original_GPU_initial_wait',None)
    compact['processor_responsibilities']['C_GPU_initial_wait']='Eight reached instructions reconstructed and compared from live CPU-loaded state; 259,413 instructions including branch delays, no original GPU execution. 194,561 blocks is a matching observation quantum, not a physical duration.'
    compact['plain_language_summary']='The observed initial GPU wait now runs in C and matches the original GPU, alongside the already verified C DSP, video interrupt handler and resumed renderer. The original main CPU then naturally copies 228 bytes from RAM 0x502AA to 0x1000, jumps there and waits for five source video-counter increments. This next 433-step CPU trace is discovery only. Main CPU reconstruction, further video events/global timing, real disc header/loading and natural game dispatch remain unfinished. The separate game C test still supplies the initial 60,000-byte stub; the full rebuilt game cannot boot yet.'
    compact['next_CPU_after_GPU']=dict(status='native_discovery_only',steps=433,instruction_versions=15,final_PC='0x100c',source_copy_bytes=228,source_copy_from='0x502aa',source_copy_to='0x1000',CPU_reseeded=False,source_video_counter='0x1ae4d2',required_video_counter_delta=5,additional_host_video_events=0,source_C_verified=False)
    compact['next_GPU_CPU_dependency']=dict(status='Initial GPU wait and renderer C verified; next CPU video wait discovered',next_action='Reconstruct the 15 observed CPU instructions after GPU shutdown, deliver source video interrupts to advance the five-counter wait, then trace real disc header/load and dispatch. Derive actual global event timing and extend inputs/code variants.')
    save(out/'compact-evidence.json',compact)
    for base in [ROOT,RUNTIME]:
        folder=Path(json.loads((base/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
        path=folder/'emulator-runtime/summary.json';data=json.loads(path.read_text());data['firmware_bootstrap_DSP_progress']=compact;save(path,data)
    files=[ROOT/'verification/firmware-initial-GPU-live-checks.json',ROOT/'verification/firmware-GPU-renderer-live-checks.json',ROOT/'verification/firmware-GPU-renderer-checks.json',ROOT/'scripts/check_biwn_firmware_initial_GPU_live.py',ROOT/'scripts/observe_biwn_relocated_firmware.py',ROOT/'scripts/generate_biwn_firmware_GPU_renderer.py',ROOT/'scripts/record_firmware_initial_GPU_checkpoint.py',ROOT/'scripts/test_firmware_initial_GPU_chat_scope.py',ROOT/'projects/black-ice-white-noise/restoration/biwn_firmware_GPU_renderer.c',ROOT/'projects/black-ice-white-noise/restoration/biwn_firmware_GPU_renderer.h']
    files.extend(Path(proof['C_directory'])/name for name in ['protocol.json','report.json','status.json','GPU-shutdown-observation.json','CPU-after-GPU.json','CPU-after-GPU.txt','GPU-after-shutdown-probe.bin','GPU-after-video-IRQ-resume.bin','RAM-after-GPU-CPU.bin'])
    manifest=[]
    for i,p in enumerate(files):
        target=out/f'{i:02d}-{p.name}';shutil.copy2(p,target);manifest.append(dict(source=str(p),snapshot=str(target),sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
    review=dict(status='initial_GPU_C_verified_next_CPU_trace_discovered_goal_incomplete',directory=str(out),proof=proof,evidence=compact,manifest=manifest,implementation_authorship='Coordinator extended guarded GPU C with four initial-only variants, reused shared peripheral synchronization, compared independent native/C runs, and traced the next original CPU phase. No local model code body added.',local_model_accepted_body_counts_unchanged=True,new_weight_training=False,model_defaults_changed=False,native_UI_new_test_verified=False,whole_goal_complete=False)
    save(out/'review.json',review);save(ROOT/'verification/firmware-initial-GPU-review.json',review)
    (out/'who-prompts-and-responses.txt').write_text(review['implementation_authorship']+'\n\nSOURCE TEST COMMAND\n.venv/bin/python scripts/observe_biwn_relocated_firmware.py --DSP-C --continue-CPU --probe-GPU-shutdown --GPU-initial-wait-C --probe-CPU-video-IRQ --video-IRQ-C --resume-GPU-after-IRQ --GPU-renderer-C --continue-CPU-after-GPU\n\nOriginal CPU remains a discovery/reference provider. Local role prompt and exact tool messages will be appended after inference.\n')
    for name in ['START HERE.txt','CURRENT DECOMPILATION.txt','CURRENT LOCAL INFERENCE.txt']:shutil.copy2(ROOT/name,out/('prior-'+name))
    next_path=ROOT/'verification/NEXT SOURCE AND INFERENCE WORK.json';n=json.loads(next_path.read_text());n.update(source_audit=str(out),last_turn_classification='progress',firmware_initial_GPU_wait_C_verified=True,new_training_this_turn=False);n['next_source_work'][0]=compact['next_GPU_CPU_dependency']['next_action'];save(next_path,n)
    print(out)

if __name__=='__main__':main()
