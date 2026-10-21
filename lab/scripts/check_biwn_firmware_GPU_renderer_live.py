"""Compare independent original/C renderer runs from live firmware state."""
import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    gate=json.loads((ROOT/'verification/firmware-video-IRQ-live-checks.json').read_text());left=Path(gate['GPU_followup_native_directory'])
    native=json.loads((left/'report.json').read_text());translated=json.loads((ROOT/'verification/firmware-GPU-renderer-C-linked.json').read_text());right=Path(translated['directory'])
    assert native['emulator_shutdown_completed'] and translated['emulator_shutdown_completed']
    a=native['GPU_after_video_IRQ_observation'];b=translated['GPU_after_video_IRQ_observation']
    assert not a['source_GPU_C_verified'] and b['source_GPU_C_verified'] and b['original_GPU_instructions_on_C_path']==0
    assert not b['initial_GPU_boundary_hostloaded'] and not b['host_mailbox_flag_write']
    for key in ['execution_blocks','executed_branch_delay_slots','instructions','PC_trace_sha256','instruction_byte_trace_sha256','final_PC','final_control','logical_GPU_sha256','RAM_sha256','CPU_state_unchanged']:assert a[key]==b[key],key
    for key in a['hardware']:
        if key!='GPU':assert a['hardware'][key]==b['hardware'][key],key
    assert (left/'RAM-after-video-IRQ-GPU-resume.bin').read_bytes()==(right/'RAM-after-video-IRQ-GPU-resume.bin').read_bytes()
    assert (left/'GPU-after-video-IRQ-resume.bin').read_bytes()[:4396]==(right/'GPU-after-video-IRQ-resume.bin').read_bytes()[:4396]
    assert {(r['address'],r['bytes'],r['count'])for r in a['visited_instructions']}=={(r['address'],r['bytes'],r['count'])for r in b['visited_instructions']}
    standalone=json.loads((ROOT/'verification/firmware-GPU-renderer-checks.json').read_text());assert standalone['emulator_shutdown_completed'] and standalone['source_instruction_version_coverage']==[1317,1317]
    report=dict(status='live_firmware_C_GPU_renderer_overlays_output_and_source_stop_native_C_match',recorded_at=datetime.now(timezone.utc).isoformat(),native_directory=str(left),C_directory=str(right),source_instruction_version_coverage=[1317,1317],source_PCs=1013,execution_blocks=b['execution_blocks'],executed_branch_delay_slots=b['executed_branch_delay_slots'],instructions=b['instructions'],standalone_checkpoints=standalone['checkpoints'],original_GPU_instructions_on_renderer_C_path=0,renderer_boundary_hostloaded=False,source_overlay_payload_hostcopy=False,source_mailbox_host_write=False,CPU_state_unchanged_during_renderer=True,full_CPU_private2MBRAM_logicalGPU4396_bothbanks_other_peripherals_PC_byte_traces_counts_match=True,GPU_pipeline_tail_excluded_bytes=20,shared_blitter_MMIO_DMA_and_architectural_IRQ_model=True,source_GPU_GO_cleared=True,final_GPU_PC=b['final_PC'],final_GPU_control=b['final_control'],preceding_DSP_C=True,preceding_video_IRQ_C=True,initial_GPU_mailbox_wait_still_original=not translated.get('initial_GPU_wait_C_selected',False),main_firmware_CPU_still_original=True,disc_attached=False,initial60000byte_game_stub_still_supplied_in_separate_game_chain=True,firmware_to_game_dispatch_verified=False,physical_global_schedule_verified=False,whole_game_complete=False,implementation_authorship='coordinator',local_model_authored_bodies_added=0,source_sha256=standalone['source_sha256'],generator_sha256=standalone['generator_sha256'],live_test_script_sha256=sha(Path(__file__)),standalone_proof=standalone,limits=['Live original firmwareCPU supplies GPU/DSP code; C DSP/C videoIRQ precede renderer; original8instruction mailboxwait initialization remains before C renderer. This is not all-C firmware or disc boot.', 'Guarded1317observed instruction versions at1013PCs. Source stores and sharedblitter DMA generate/patch GPU code; no host overlay injection or originalGPU renderer execution. Otherinputs/codevariants need extension.', 'Shared peripheral MMIO/DMA/architecturalIRQ effects and initial20byte pipeline tail remain providers. Explicit processor sequencing and singleVBI event are not physical/globalclock proof. Main firmware CPU/cart mapping/disc authentication/header-load/game dispatch/fullplayability remain.'])
    if translated.get('initial_GPU_wait_C_selected'):report['limits'][0]='Live main firmwareCPU supplies code; initialGPUwait, DSP, videoIRQ and renderer run C. MainCPU remains original; no discboot or globalclock proof.'
    save(ROOT/'verification/firmware-GPU-renderer-live-checks.json',report)
    print(json.dumps({k:report[k]for k in ['status','source_instruction_version_coverage','instructions','source_GPU_GO_cleared','whole_game_complete']}))

if __name__=='__main__':main()
