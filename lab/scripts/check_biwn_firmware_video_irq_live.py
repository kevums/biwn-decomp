"""Independent live native/C video IRQ comparison; retain the next GPU stage."""
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    native=json.loads((ROOT/'verification/firmware-CPU-video-IRQ-native-discovery.json').read_text())
    translated=json.loads((ROOT/'verification/firmware-CPU-video-IRQ-C-linked.json').read_text())
    a=native['CPU_video_IRQ_observation'];b=translated['CPU_video_IRQ_observation'];left=Path(native['directory']);right=Path(translated['directory'])
    assert native['emulator_shutdown_completed']and translated['emulator_shutdown_completed']
    assert not a['source_C_verified']and b['source_C_verified']and b['original_CPU_handler_instructions_on_C_path']==0
    assert not b['initial_handler_boundary_hostloaded']and not b['host_mailbox_flag_write']and not b['CPU_reseeded']
    for key in ['CPU_before','CPU_after_exception_entry','CPU_after','instructions','PC_trace_sha256','mailbox_before','mailbox_after','source_mailbox_clear_reached','source_video_counter_before','source_video_counter_after','RAM_sha256','hardware']:
        assert a[key]==b[key],key
    visits={hex(row['address']):row['count']for row in a['visited_instructions']};assert visits==b['PC_visits'] and len(visits)==327
    assert b['stop_reason']=='source_handler_RTE_returned'and b['instructions']==660
    assert b['mailbox_before']=='0x1'and b['mailbox_after']=='0x0'and b['source_video_counter_after']==b['source_video_counter_before']+1
    assert a['CPU_before']==a['CPU_after']and b['CPU_before']==b['CPU_after']
    assert (left/'RAM-after-video-IRQ.bin').read_bytes()==(right/'RAM-after-video-IRQ.bin').read_bytes()
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'firmware-video-IRQ-generation.json').read_text())
    for name,digest in mapping['source_sha256'].items():assert sha(ROOT/'projects/black-ice-white-noise/restoration'/name)==digest
    next_GPU=translated.get('GPU_after_video_IRQ_observation')
    followup_native=None
    if next_GPU:
        assert next_GPU['stop_reason']=='source_GPU_GO_cleared'and next_GPU['final_control']&1==0 and not next_GPU['source_GPU_C_verified']
        assert not next_GPU['host_mailbox_flag_write']and not next_GPU['initial_GPU_boundary_hostloaded']
        followup_directory=ROOT/'verification/BIWN-relocated-firmware-observation/20261015T023545.991248Z'
        followup_native=json.loads((followup_directory/'report.json').read_text())
        assert followup_native['emulator_shutdown_completed'] and not followup_native['CPU_video_IRQ_observation']['source_C_verified']
        comparison=followup_native['GPU_after_video_IRQ_observation']
        for key in ['execution_blocks','executed_branch_delay_slots','instructions','PC_trace_sha256','instruction_byte_trace_sha256','final_PC','final_control','logical_GPU_sha256','RAM_sha256','hardware']:assert comparison[key]==next_GPU[key],key
        for name in ['GPU-after-video-IRQ-resume.bin','RAM-after-video-IRQ-GPU-resume.bin']:assert (followup_directory/name).read_bytes()==(right/name).read_bytes(),name
    report=dict(status='live_firmware_C_video_IRQ_frame_helpers_mailbox_RTE_native_C_match',recorded_at=datetime.now(timezone.utc).isoformat(),native_directory=str(left),C_directory=str(right),cases=1,independent_live_runs=2,source_instruction_coverage=[327,327],executed_CPU_handler_instructions=660,external_video_IRQ_events=1,source_handler='0x194c90',source_mailbox_clear_PC='0x194d18',mailbox='0xf03f4c',mailbox_before=1,mailbox_after=0,video_counter_before=0,video_counter_after=1,exception_frame_bytes=6,CPU_return_PC='0x50292',CPU_registers_flags_both_stack_banks_restored=True,full_CPU_private2MBRAM_GPU_DSP_TOM_JERRY_DAC_CDROM_state_PC_trace_counts_match=True,original_CPU_handler_instructions_on_C_path=0,initial_handler_boundary_hostloaded=False,host_mailbox_flag_write=False,CPU_reseeded=False,preceding_DSP_C=True,preceding_and_following_main_firmware_CPU_still_original=True,GPU_execution_still_original=True,physical_VBI_period_or_global_timing_verified=False,full_firmware_boot_verified=False,whole_game_complete=False,implementation_authorship='coordinator',local_model_authored_bodies_added=0,source_sha256=mapping['source_sha256'],generator_sha256=mapping['generator_sha256'],test_script_sha256=sha(Path(__file__)),compiler_log=str(right/'video-IRQ-compiler.txt'),emulator_shutdown_completed=True,next_original_GPU=({k:next_GPU[k]for k in ['stop_reason','execution_blocks','executed_branch_delay_slots','instructions','final_PC','final_control','logical_GPU_sha256','RAM_sha256','source_GPU_C_verified','CPU_state_unchanged']}if next_GPU else None),next_GPU_code_instruction_versions=len(next_GPU['visited_instructions'])if next_GPU else None,next_GPU_code_changes=len(next_GPU['observed_code_changes'])if next_GPU else None,limits=['One reached live firmware path:327selected handler/graphics helper instructions. Initial ROM/zeroRAM/device seed and explicitVBI event supplied; other queues/graphics/input/IRQ cases not proved.','Real source event frame, live state andRTE; no captured IRQ boundary, original handler execution on C path or host mailbox clear. MainfirmwareCPU andGPU still run original instructions around the C DSP/C videoIRQ components.','OriginalGPU resumes after C handler and stops through source drawing/code overlays:1317instruction versions/345observed mutations on this path. These GPU code variants remain unported; no physical/global schedule/disc-header loading/fullboot/playability proof.'])
    if followup_native:
        report.update(GPU_followup_after_original_and_C_IRQ_match=True,GPU_followup_native_directory=followup_native['directory'],GPU_followup_full4416_and2MBRAM_hardware_PC_and_byte_traces_match=True,GPU_code_change_observations=len(next_GPU['observed_code_changes']),GPU_distinct_changed_PC_addresses=len({event['PC']for event in next_GPU['observed_code_changes']}),GPU_change_count_units='Observations at re-visited executingPCs; not a count of every code write or unique locations.')
    save(ROOT/'verification/firmware-video-IRQ-live-checks.json',report)
    print(json.dumps({k:report[k]for k in ['status','source_instruction_coverage','executed_CPU_handler_instructions','mailbox_after','next_GPU_code_instruction_versions','whole_game_complete']}))

if __name__=='__main__':main()
