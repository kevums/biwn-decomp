"""Record observed firmware boundaries and original HLE game baseline."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INSTALLED=Path.home()/'.lmstudio/local-ai-lab'


def save(path, data):
    path.write_text(json.dumps(data, indent=2)+'\n')


def main():
    out=ROOT/'verification/auth-and-HLE-progress'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    (ROOT/'config').mkdir(exist_ok=True)
    manifest={}
    def read_run(log):
        path=ROOT/'runs'/log
        directory=Path(path.read_text().splitlines()[0])
        data=json.loads((directory/'report.json').read_text())
        status=json.loads((directory/'status.json').read_text())
        assert status['shutdown_completed'] and status['status']=='terminal_pass_probe_only'
        for p in [path,directory/'report.json',directory/'status.json',directory/'state-final.bin']:
            manifest[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
        return directory,data
    negative,neg=read_run('fresh-auth-hooks-off600-trace.log')
    negative_control,nc=read_run('fresh-auth-hooks-off600-control.log')
    assert neg['final_serialized_state_sha256']==nc['final_serialized_state_sha256']
    positive,pos=read_run('fresh-auth-all-off-source-conditions.log')
    positive_control,pc=read_run('fresh-auth-all-off90-control.log')
    assert pos['final_serialized_state_sha256']==pc['final_serialized_state_sha256']
    restart,res=read_run('fresh-auth-all-off-cause-trace.log')
    restart_control,rc=read_run('fresh-auth-all-off-return-control.log')
    assert res['final_serialized_state_sha256']==rc['final_serialized_state_sha256']
    first=next(z for z in neg['firmware_trace'] if z['PC']=='0x5e40')
    assert first['frame']==69 and first['GPU_local_auth_prefix'][:8]=='12345678'
    entry=next(z for z in pos['firmware_trace'] if z['PC']=='0x802000')
    assert entry['frame']==25 and entry['GPU_local_auth_prefix'][:8]=='03d0dead'
    DSP_check=next(z for z in pos['firmware_trace'] if z['PC']=='0x5022e')
    assert DSP_check['frame']==62 and DSP_check['CPU_registers'][1]==0x03d0dead
    assert DSP_check['DSP_local_auth_word']=='0x3d0dead'
    second=next(z for z in res['firmware_trace'] if z['PC']=='0x802000' and z['visit']==2)
    assert second['frame']==68 and second['previous_PC']=='0x10a8'
    firmware=dict(negative_trace=str(negative/'report.json'),positive_trace=str(positive/'report.json'),
        restart_trace=str(restart/'report.json'),
        trace_on_off_complete_serialized_state_equal=True,
        hooks_off_auth_byte_bypassed=dict(frame=69,CPU_check='0x5e40',expected='0x03d0dead',actual='0x12345678',failure_loop='0x50b6'),
        all_assists_off=dict(first_ROM_entry_frame=25,GPU_marker='0x03d0dead',relocated_entry_frame=32,
            relocated_entry='0x500d6',DSP_check_frame=62,DSP_marker='0x03d0dead',DSP_CPU_check='0x5022e',
            source_restart_frame=68,source_restart_predecessor='0x10a8',source_restart_target='0x802000'),
        scope='Native original processors under full-core frame scheduling; original retail BIOS authentication byte restored and BIOS strategy instruction assists disabled. Marker values and branches observed; not physical/authenticated disc boot or reconstructed C firmware proof.',
        next_action='Follow the source path into copied restart routine1000 and distinguish its header/firmware behavior from disc authentication. Prior hooks-only failure is not the same path as all-assists-off.')
    active,input_run=read_run('fresh-CD-hle-input.log')
    control,control_run=read_run('fresh-CD-hle-control.log')
    assert input_run['requested_options']['virtualjaguar_cd_boot_mode']=='hle'
    assert input_run['frames'][:299]==control_run['frames'][:299]
    assert input_run['frames'][-1]['raw_player_X']==control_run['frames'][-1]['raw_player_X']==9376
    assert input_run['frames'][-1]['raw_player_Z']==40090 and control_run['frames'][-1]['raw_player_Z']==40096
    assert input_run['pressed_input_samples']=={'4':60,'6':60}
    assert input_run['audio']['nonzero_samples']==control_run['audio']['nonzero_samples']==0
    assert input_run['stage_equal_to_extracted_reference_at_any_frame']
    native=dict(input_report=str(active/'report.json'),control_report=str(control/'report.json'),
        kind='Fresh original-emulator HLE boot and emulated controller test from preserved CDI',frames_each=600,
        captured_state_input=False,host_CPU_GPU_seed=False,first299_recorded_frame_rows_equal=True,
        input_plan='Up frames300-359, Left360-419, then release; actual libretro joypad callback, not game-memory writes.',
        final_X_each=9376,input_final_Z=40090,control_final_Z=40096,
        game_display_observed='Rendered street, character and HUD; raw XRGB screenshot visually checked.',
        all_audio_samples_zero=True,source_C_execution=False,unassisted_firmware_boot=False,
        physical_controller_test=False,whole_game_complete=False,
        scope='The original emulator executes game code. HLE supplies platform/CD BIOS services. This is an operational/reference baseline, not a finished reconstructed C game or proof of every game scene.')
    report=dict(status='firmware_auth_boundaries_and_fresh_HLE_game_input_verified',directory=str(out),
        firmware=firmware,native_HLE_game=native,new_training=False,new_local_model_C_authorship=False,
        whole_game_complete=False,next_action='Use fresh HLE boot as the practical reference/configuration baseline; connect reconstructed game entry/startup/tasks to this disc-derived boot path and continue missing game branches, audio and timing. Keep unassisted firmware reconstruction as a separate scope.')
    save(out/'report.json',report);save(ROOT/'verification/auth-and-HLE-current.json',report)
    for base in [ROOT,INSTALLED]:
        session=json.loads((base/'projects/black-ice-white-noise/analysis/current-session.json').read_text())
        path=Path(session['directory'])/'emulator-runtime/summary.json';data=json.loads(path.read_text())
        data['fresh_firmware_auth_trace']=firmware;data['native_HLE_game_test']=native;save(path,data)
    for name in ['probe_biwn_fresh_CD_boot.py','record_biwn_auth_and_HLE_progress.py']:
        p=ROOT/'scripts'/name;manifest[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
    save(out/'input-manifest.json',manifest)
    (out/'who-prompts-and-responses.txt').write_text('COORDINATOR\nTrace the first firmware authentication failure with an observational hook and full serialized-state controls. Follow the distinct all-assists-off path. Test HLE as a practical original-emulator baseline, actual controller callbacks and output. Do not call native HLE execution a C decompile, physical playability or authentic disc boot.\n\n'+json.dumps(report,indent=2)+'\n')
    save(ROOT/'config/biwn-native-reference.json',dict(core=input_run['core'],core_sha256=input_run['core_sha256'],
        disc=input_run['disc'],disc_sha256=input_run['disc_sha256'],libretro_options=input_run['requested_options'],
        scope=native['scope'],reference_report=str(out/'report.json'),audible_game_music_verified=False))
    print(out,flush=True)


if __name__=='__main__':main()
