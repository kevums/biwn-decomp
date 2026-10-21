"""Compare independently executed natural CPU + native/C firmware DSP paths."""
import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    left=ROOT/'verification/BIWN-relocated-firmware-observation/20261015T012902.854843Z'
    native=json.loads((left/'report.json').read_text())
    translated=json.loads((ROOT/'verification/relocated-firmware-DSP-C-linked.json').read_text());right=Path(translated['directory'])
    for record in [native,translated]:
        assert record['emulator_shutdown_completed'] and record['emulator_BIOS_boot_stub_injection_and_GPU_magic_stomp_disabled']
        assert record['initial_PC']=='0x802000' and record['initial_RAM'].startswith('zero-filled') and not record['disc_attached']
        assert record['first_DSP_observation']['stop_reason']=='source_DSP_GO_cleared'
        assert not record['CPU_continuation_after_first_DSP']['CPU_reseeded']
    assert not native['first_DSP_observation']['source_C_verified']
    assert translated['first_DSP_observation']['source_C_verified']
    assert translated['first_DSP_observation']['original_DSP_instructions_on_C_path']==0
    assert translated['first_DSP_observation']['live_CPU_loader_state_used'] and not translated['first_DSP_observation']['earlier_DSP_boundary_hostloaded']
    for key in ['source_BIOS_sha256','pinned_core_sha256','executed_steps','unique_visited_PCs','PC_trace_sha256','final_CPU','final_RAM_sha256','relocated_entry']:
        assert native[key]==translated[key],key
    for key in ['instructions','PC_trace_sha256','initial_logical_DSP_sha256','final_logical_DSP_sha256','main_RAM_sha256','header_word_F1B000','initial_DSP_PC','final_DSP_PC','final_control']:
        assert native['first_DSP_observation'][key]==translated['first_DSP_observation'][key],key
    assert (left/'DSP-after-first-program.bin').read_bytes()[:8496]==(right/'DSP-after-first-program.bin').read_bytes()[:8496]
    for filename in ['RAM-at-relocated-entry.bin','RAM-final.bin','RAM-after-first-DSP.bin','RAM-after-CPU-continuation.bin']:
        assert (left/filename).read_bytes()==(right/filename).read_bytes(),filename
    for key in ['steps','PC_trace_sha256','PC_visits','CPU','GPU_PC','GPU_GO','DSP_GO','RAM_sha256']:
        assert native['CPU_continuation_after_first_DSP'][key]==translated['CPU_continuation_after_first_DSP'][key],key
    for stage in ['final_hardware']:
        assert all(native[stage][key]==translated[stage][key] for key in native[stage]if key!='DSP')
    for key,value in native['CPU_continuation_after_first_DSP']['hardware'].items():
        if key!='DSP':assert translated['CPU_continuation_after_first_DSP']['hardware'][key]==value,key
    ending=translated['CPU_continuation_after_first_DSP'];assert ending['CPU']['pc']==0x50292 and ending['DSP_GO']&1==0 and ending['GPU_GO']&1==1
    standalone=json.loads((ROOT/'verification/firmware-DSP-auth-checks.json').read_text());assert standalone['source_instruction_coverage']==[462,462] and standalone['emulator_shutdown_completed']
    report=dict(status='natural_original_CPU_bootstrap_C_firmware_DSP_and_GPU_wait_match',recorded_at=datetime.now(timezone.utc).isoformat(),native_directory=str(left),C_directory=str(right),independent_live_runs=2,initial_CPU_PC='0x802000',initial_RAM='zero-filled2MB plus supplied retail userROM/CPU/device fixtures',CPU_steps_to_first_DSP_wait=native['executed_steps'],CPU_unique_PCs_to_first_DSP_wait=native['unique_visited_PCs'],relocated_entry_PC='0x500d6',CPU_first_DSP_wait_PC='0x5021c',firmware_DSP_instructions=standalone['instructions'],firmware_DSP_instruction_coverage=[462,462],firmware_DSP_checkpoints=standalone['checkpoints'],firmware_DSP_success_word='0x03d0dead',CPU_continuation_steps=ending['steps'],next_CPU_wait_PC='0x50292',next_GPU_PC=ending['GPU_PC'],next_GPU_control=ending['GPU_GO'],native_CPU_firmware_instructions_used=True,CPU_firmware_C_beyond_bootstrap_verified=False,firmware_DSP_C=True,original_DSP_instructions_on_C_path=0,initial_DSP_boundary_hostloaded=False,decrypted_code_host_copy=False,source_success_word_injected=False,emulator_BIOS_boot_stub_injection_disabled=True,emulator_GPU_auth_magic_stomp_disabled=True,CPU_reseeded_after_initial_ROM_entry=False,full_CPU_RAM_GPU_TOM_JERRY_DAC_CDROM_states_and_PC_traces_compared=True,DSP_equivalence_bytes=8496,DSP_pipeline_tail_excluded_bytes=233,C_DSP_pipeline_tail_provider='Initial tail retained when mirroring source-computed logical state to peripheral bus',complete_firmware_boot_verified=False,disc_attached=False,boot_stub_source_loaded=False,linked_into_full_C_game_startup=False,whole_game_complete=False,implementation_authorship='coordinator',local_model_authored_bodies_added=0,standalone_proof=standalone,observation_script_sha256=sha(ROOT/'scripts/observe_biwn_relocated_firmware.py'),comparison_script_sha256=sha(Path(__file__)),limits=['Natural live original CPU supplies the DSP program and data. C executes/decrypts/checks the ROM and stops itself; CPU continues without reseed. The preceding/following firmwareCPU still executes original instructions, GPU drawing does not run, and no disc is attached.', 'The check is for the pinned userROM path. DSP input clocks are explicitly delivered while CPU waits; this is not a verified physical/global schedule. DSP8496 logical bytes/bothbanks compare,233pipeline bytes are an explicit excluded provider.', 'Next: sourceGPU drawing/shutdown atCPU5028A..50292, then actual remaining firmwareCPU/DSP/controller/authenticated disc header/load/dispatch. Existing continuousgame180000->4000/startup/movie/world proof remains separate and still supplies the initial60000byte stub.'])
    save(ROOT/'verification/firmware-DSP-auth-live-checks.json',report)
    print(json.dumps({k:report[k]for k in ['status','firmware_DSP_instruction_coverage','firmware_DSP_instructions','CPU_continuation_steps','next_CPU_wait_PC','next_GPU_PC','whole_game_complete']}))

if __name__=='__main__':main()
