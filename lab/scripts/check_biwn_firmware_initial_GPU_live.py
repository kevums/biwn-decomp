"""Compare live initial C GPU wait and subsequent stages with a fixed native run."""
import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]

def main():
    left=ROOT/'verification/BIWN-relocated-firmware-observation/20261015T023545.991248Z'
    native=json.loads((left/'report.json').read_text())
    translated=json.loads((ROOT/'verification/firmware-GPU-renderer-C-linked.json').read_text())
    right=Path(translated['directory'])
    assert native['emulator_shutdown_completed'] and translated['emulator_shutdown_completed']
    assert translated['initial_GPU_wait_C_selected']
    a=native['GPU_shutdown_observation'];b=translated['GPU_shutdown_observation']
    assert not a['source_GPU_C_verified'] and b['source_GPU_C_verified']
    assert b['original_GPU_instructions_on_C_path']==0 and b['core_opcode_counter_delta']==0
    assert not b['initial_GPU_boundary_hostloaded']
    keys=['instructions','execution_blocks','executed_branch_delay_slots','CPU_held_at','CPU_state_unchanged','initial_GPU_PC','final_GPU_PC','initial_logical_GPU_sha256','final_logical_GPU_sha256','PC_trace_sha256','visited_instructions','final_control','RAM_sha256']
    for key in keys:assert a[key]==b[key],key
    assert b['instructions']==259413 and b['execution_blocks']==194561
    assert len(b['visited_instructions'])==8
    for key in a['hardware']:
        if key!='GPU':assert a['hardware'][key]==b['hardware'][key],key
    for name,logical in [('GPU-at-CPU-stop-wait.bin',4396),('GPU-after-shutdown-probe.bin',4396),('GPU-after-video-IRQ-resume.bin',4396),('RAM-after-GPU-shutdown-probe.bin',None),('RAM-after-video-IRQ.bin',None),('RAM-after-video-IRQ-GPU-resume.bin',None)]:
        assert (left/name).read_bytes()[:logical]==(right/name).read_bytes()[:logical],name
    for phase in ['CPU_video_IRQ_observation','GPU_after_video_IRQ_observation']:
        x,y=native[phase],translated[phase]
        for key in ['instructions','PC_trace_sha256','RAM_sha256']:
            assert x[key]==y[key],(phase,key)
        for key in (['CPU_before','CPU_after_exception_entry','CPU_after'] if phase=='CPU_video_IRQ_observation' else ['execution_blocks','executed_branch_delay_slots','instruction_byte_trace_sha256','final_PC','final_control','logical_GPU_sha256','CPU_state_unchanged','visited_instructions']):assert x[key]==y[key],(phase,key)
        for key in x['hardware']:
            if key not in ['GPU','DSP']:assert x['hardware'][key]==y['hardware'][key],(phase,key)
    report=dict(status='live_initial_GPU_wait_and_resumed_renderer_native_C_match',recorded_at=datetime.now(timezone.utc).isoformat(),native_directory=str(left),C_directory=str(right),initial_wait_source_instruction_coverage=[8,8],initial_wait_instructions=b['instructions'],initial_wait_execution_blocks=b['execution_blocks'],initial_wait_PC_trace_and_counts_match=True,whole_private2MBRAM_CPU_logicalGPU_other_peripheral_state_match=True,original_GPU_instructions_on_C_path=0,initial_GPU_boundary_hostloaded=False,source_mailbox_host_write=False,initial_wait_quantum_is_observation_boundary=True,GPU_pipeline_tail_excluded_bytes=20,shared_pinned_MMIO_blitter_DMA_architectural_IRQ_provider=True,compared_peripheral_fields=list(a['hardware']),live_blitter_private_state_compared=False,source_C_sha256=hashlib.sha256((ROOT/'projects/black-ice-white-noise/restoration/biwn_firmware_GPU_renderer.c').read_bytes()).hexdigest(),test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),preceding_DSP_C=True,video_IRQ_C=True,renderer_C=True,main_CPU_still_original=True,disc_attached=False,physical_global_schedule_verified=False,whole_game_complete=False,implementation_authorship='coordinator',local_model_authored_bodies_added=0,limits=['Live snapshots compare DSP/GPU/TOM/JERRY/DAC/CDROM/controller extension/TOM RAM/cart ROM; private Blitter state is separately checked in the standalone renderer proof, not this live comparison.', 'Eight reached initial wait instructions; 194561 outer blocks is the independent native observation quantum, not a physical wait duration.', 'Main firmware CPU remains original; one explicit video event and shared pinned peripherals remain providers. No disc header load or firmware-to-game dispatch proof.', '4396 logical GPU bytes compared; 20 initial pipeline bytes retained and excluded. Other inputs/code variants and global timing remain unverified.'])
    (ROOT/'verification/firmware-initial-GPU-live-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k]for k in ['status','initial_wait_source_instruction_coverage','initial_wait_instructions','whole_game_complete']}))

if __name__=='__main__':main()
