"""Compare diagnostic native/C DSP ROM-check failure and following CPU path."""
import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    left=ROOT/'verification/BIWN-relocated-firmware-observation/20261015T034733.947505Z'
    right=ROOT/'verification/BIWN-relocated-firmware-observation/20261015T034607.747838Z'
    a=json.loads((left/'report.json').read_text());b=json.loads((right/'report.json').read_text())
    assert a['emulator_shutdown_completed'] and b['emulator_shutdown_completed'] and a['disc_attached'] and b['disc_attached']
    x,y=a['first_DSP_observation'],b['first_DSP_observation'];assert not x['source_C_verified'] and y['original_DSP_instructions_on_C_path']==0
    for key in ['instructions','CPU_held_at','CPU_state_unchanged','initial_DSP_PC','final_DSP_PC','final_control','PC_trace_sha256','initial_logical_DSP_sha256','final_logical_DSP_sha256','main_RAM_sha256','header_word_F1B000']:assert x[key]==y[key],key
    assert x['header_word_F1B000']==0x12345678 and x['instructions']==10460873
    counts={hex(row['address']):row['count']for row in x['visited_instructions']};assert counts==y['observed_C_PC_counts'] and len(counts)==447 and '0xf1b560'in counts
    for phase in ['first_DSP_observation','CPU_continuation_after_first_DSP']:
        p,q=a[phase],b[phase]
        for key in p['hardware']:
            if key!='DSP':assert p['hardware'][key]==q['hardware'][key],(phase,key)
    p,q=a['CPU_continuation_after_first_DSP'],b['CPU_continuation_after_first_DSP']
    for key in ['steps','CPU','PC_trace_sha256','RAM_sha256','PC_visits']:assert p[key]==q[key],key
    for name,logical in [('DSP-at-CPU-wait.bin',8496),('DSP-after-first-program.bin',8496),('RAM-after-first-DSP.bin',None),('RAM-after-CPU-continuation.bin',None)]:assert (left/name).read_bytes()[:logical]==(right/name).read_bytes()[:logical],name
    for report in [a,b]:
        view=report['DSP_only_ROM_header_diagnostic'];assert view['temporary_DSP_view']==5 and view['original_CPU_view']==1 and view['restored_before_CPU_continuation'] and not view['hardware_behavior_verified'] and not view['source_magic_result_injection']
    report=dict(status='diagnostic_DSP_ROM_view_failure_branch_native_C_match',recorded_at=datetime.now(timezone.utc).isoformat(),native_directory=str(left),C_directory=str(right),observed_source_instruction_coverage=[447,447],compiled_instruction_count=463,executed_instructions=10460873,extra_source_failure_instruction='0xf1b560 MOVEI12345678,r4',source_result=hex(x['header_word_F1B000']),source_result_injected=False,original_DSP_instructions_on_C_path=0,source_decrypted_code_hostcopied=False,DSP_logical_state_bytes=8496,DSP_pipeline_tail_excluded_bytes=233,CPU_private2MBRAM_other_peripheral_PC_trace_counts_match=True,following_original_CPU_steps=300000,following_original_CPU_final_PC='0x50894',CPU_reseeded_after_ROM_view_restored=False,temporary_DSP_ROM_header_view=5,original_CPU_ROM_header_view=1,user_BIOS_file_sha256=sha(ROOT/'render-assets/jaguarcd_bios.bin'),hardware_ROM_view_verified=False,disc_attached=True,disc_header_or_game_stub_loaded=False,physical_global_schedule_verified=False,whole_game_complete=False,implementation_authorship='coordinator',local_model_authored_bodies_added=0,source_sha256={name:sha(ROOT/'projects/black-ice-white-noise/restoration'/name)for name in ['biwn_firmware_DSP_boot_probe.c','biwn_firmware_DSP_boot_probe.h']},test_sha256=sha(Path(__file__)),limits=['Native/C match under explicitly supplied DSP-only ROM data view5. This workaround is diagnostic and does not prove actual hardware ROM mapping or authentication.', 'The source computes failure12345678 itself; no result write or decrypted code injection. It routes CPU into the CD initialization branch. Body coverage447/463 compiled instructions on this input only.', 'Full DSP private pipeline tail233bytes excluded; CPU, private RAM, logical DSP and other available peripheral snapshots/traces/counts compared. No authentic full boot, timing, disc payload load or playable game claim.'])
    (ROOT/'verification/firmware-DSP-ROM-view-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k]for k in ['status','observed_source_instruction_coverage','executed_instructions','source_result','hardware_ROM_view_verified','whole_game_complete']}))

if __name__=='__main__':main()
