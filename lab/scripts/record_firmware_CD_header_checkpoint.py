"""Publish observed disc header rejection without claiming a completed boot."""
import hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[1]
INSTALLED=Path.home()/'.lmstudio/local-ai-lab'
save=lambda p,v:p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
sha=lambda b:hashlib.sha256(b).hexdigest()

def main():
    origin=ROOT/'verification/BIWN-relocated-firmware-observation/20261015T072026.200411Z'
    prior_origin=ROOT/'verification/BIWN-relocated-firmware-observation/20261015T071734.038178Z'
    report=json.loads((origin/'report.json').read_text())
    assert report['emulator_shutdown_completed'] and report['disc_attached']
    assert json.loads((origin/'status.json').read_text())['status']=='terminal_observation_complete'
    command=report['CD_read_command_DSP_observation'];descriptor=report['CD_descriptor_DSP_observation'];header=report['CD_header_DSP_observation'];cpu=report['CPU_continuation_after_CD_header']
    assert command['stop_reason']=='source_CD_read_command_acknowledged' and command['instructions']==8119862
    assert descriptor['instructions']==71 and header['instructions']==227
    assert all(x['stop_reason'].endswith('after_IRQ_return') for x in [descriptor,header])
    assert cpu['steps']==264978 and cpu['final_CPU']['pc']==0x505fa and not cpu['CPU_reseeded']
    rows={r['address']:r for r in cpu['visited_instructions']}
    assert rows[0x50aa0]['assembly']=='bne.w $504ec'
    # Deterministic replay of all completed phases before the new CPU continuation.
    replay_files=['RAM-after-command-DSP.bin','DSP-after-command-program.bin','RAM-after-descriptor-DSP.bin','DSP-after-descriptor-program.bin','RAM-after-header-DSP.bin','DSP-after-header-program.bin']
    for name in replay_files:assert (origin/name).read_bytes()==(prior_origin/name).read_bytes(),name
    ram=(origin/'RAM-after-header-DSP.bin').read_bytes();actual=ram[0x4000:0x4088];expected=ram[0x51162:0x51182]
    assert expected.startswith(b'ATARI APPROVED DATA HEADER ATRI#')
    assert actual[0]!=expected[0]
    disc=ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi'
    with disc.open('rb')as f:f.seek(3244146);disc_header=f.read(160)
    decoded=b''.join(disc_header[i:i+2][::-1]for i in range(0,28,2))
    assert decoded==expected[:28]
    transformed=b''.join(disc_header[i:i+4][::-1]for i in range(2,30,4))
    assert transformed==actual[:28]
    # This identifies a real disc prefix and a transform, not the responsible hardware rule.
    now=datetime.now(timezone.utc).isoformat()
    out=ROOT/'verification/firmware-CD-header-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    old=json.loads((ROOT/'verification/firmware-CD-diagnostic-review.json').read_text())
    pointer=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])/'emulator-runtime/summary.json'
    compact=json.loads(pointer.read_text())['firmware_bootstrap_DSP_progress']
    save(out/'previous-evidence.json',compact)
    summary=('With the supplied DSP-only ROM header view5 and declared partial CD/SSI clocks, the original firmware third DSP acknowledges its CD command after 8,119,862 instructions. Original CPU then submits descriptor copies: 71 and 227 DSP instructions complete with interrupt returns. The copied header at4000 fails the source byte comparison at50AA0 and the CPU returns to a BIOS wait at505FA after264,978 further steps. Its first28 bytes match an explicitly reversed32-bit view starting two bytes into an actual CDI header; byte-pair decoding of the CDI contains the expected ATARI APPROVED DATA HEADER prefix. This identifies a disc/header ordering dependency, not its hardware-correct fix. No game boot stub is loaded or hostcopied. The separate C diagnostic proof remains447 reached instructions/10,460,873 executions/failure12345678; original ROM-view1 proof remains462/10,460,888/success03D0DEAD. Hardware ROM mapping, remaining C reconstruction, physical global timing and complete game boot remain unverified.')
    next_action='Resolve the source CD/SSI header ordering and offset against disc mastering and primary hardware documentation; test a declared diagnostic provider separately before adopting any hardware rule. Then reach real stub loading and natural game dispatch. Extend second/third DSP and remaining CPU C proofs and global timing. Retest native Chat routing when accessible.'
    d=compact['diagnostic_firmware_CD_progress']
    d.update(status='source_CD_command_acknowledged_header_rejected',source_read_still_pending=False,following_CPU_wait='0x505fa',following_original_CPU_steps=cpu['steps'],third_DSP_original_instructions=command['instructions'],third_DSP_command_acknowledged=True,third_DSP_SSI_callbacks=command['SSI_events'],descriptor_DSP_instructions=descriptor['instructions'],header_DSP_instructions=header['instructions'],descriptor_IRQ_returns_completed=True,header_signature_accepted=False,header_rejection_PC='0x50aa0',disc_header_evidence=dict(CDI_file_offset=3244146,matched_prefix_bytes=28,expected_prefix=expected[:28].decode(),observed_header_hex=actual[:32].hex(),expected_source_header_hex=expected.hex(),observed_transform='CDI bytes at offset+2, reverse bytes within each32bit group',CDI_expected_transform='swap bytes within each16bit word',hardware_rule_verified=False),known60000byte_game_stub_present=False,source_discovery_directory=str(origin),source_read_ack_scope='Command acknowledged; header rejected; game payload not loaded',physical_global_schedule_verified=False)
    compact.update(status='diagnostic_CD_header_rejected_ordering_unresolved',recorded_at=now,audit=str(out),full_report=str(origin/'report.json'),plain_language_summary=summary,next_GPU_CPU_dependency=dict(status='Real disc header prefix located; source rejects transferred ordering',next_action=next_action))
    compact['processor_responsibilities']['original_CD_followup']='Original CPU and second/third DSP perform TOC, seek, SSI header search and descriptor copies under partial declared clocks; source header comparison fails and CPU returns to BIOS wait. These later CPU/DSP paths are discovery, not verified reconstructed C.'
    for base in [ROOT,INSTALLED]:
        session=Path(json.loads((base/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);p=session/'emulator-runtime/summary.json';data=json.loads(p.read_text());data['firmware_bootstrap_DSP_progress']=compact;save(p,data)
    manifest=[]
    files=[Path(__file__),ROOT/'scripts/observe_biwn_relocated_firmware.py',ROOT/'chat_tools.py',ROOT/'scripts/check_game_firstboot_mcp.py']+[origin/n for n in ['protocol.json','report.json','status.json','CPU-after-header-DSP.json','command-DSP-observation.json','descriptor-DSP-observation.json','header-DSP-observation.json']]+[origin/n for n in replay_files]
    for i,p in enumerate(files):
        dest=out/f'{i:02d}-{p.name}';shutil.copy2(p,dest);manifest.append(dict(source=str(p),snapshot=str(dest),sha256=sha(dest.read_bytes())))
    review=dict(status='source_CD_header_rejection_observed_goal_incomplete',recorded_at=now,directory=str(out),evidence=compact,source_directory=str(origin),deterministic_prefix_replay_directory=str(prior_origin),replayed_binary_states=6,manifest=manifest,previous_audit=old['directory'],authorship='Coordinator instrumented original CPU/DSP phases and compared source bytes. Local LLM does not author new code bodies in this checkpoint.',new_weight_training=False,accepted_local_model_body_count=171,native_UI_verified=False,hardware_rule_verified=False,whole_goal_complete=False)
    save(out/'review.json',review);save(ROOT/'verification/firmware-CD-header-review.json',review)
    (out/'who-prompts-and-responses.txt').write_text('COORDINATOR WORK\n'+review['authorship']+'\n\nEXACT SOURCE COMMAND\n.venv/bin/python scripts/observe_biwn_relocated_firmware.py --DSP-boot-probe-C --DSP-ROM-view-mame-diagnostic --continue-CPU --attach-CDI --CPU-continuation-budget 2000000 --BUTCH-clock-from-CPU-cycles --run-second-DSP --continue-CPU-after-second-DSP --run-third-DSP --initialize-third-DSP-at-source-GO --continue-CPU-after-third-DSP --run-CD-read-command-DSP --third-DSP-budget 6000000 --continue-CPU-after-CD-read-command --run-CD-descriptor-DSP --continue-CPU-after-CD-descriptor --run-CD-header-DSP --continue-CPU-after-CD-header\n\nRESULT\n'+summary+'\n\nLOCAL MODEL\nNext: fresh SDK status question using installed evidence tools. Same weights for all roles; not independent verification. Native UI request timed out this turn; no successful native interaction claimed.\n')
    for name in ['START HERE.txt','CURRENT DECOMPILATION.txt','CURRENT LOCAL INFERENCE.txt']:
        p=ROOT/name;shutil.copy2(p,out/('prior-'+name));previous=p.read_text()
        p.write_text('LATEST CD HEADER CHECKPOINT\n'+now+'\n\n'+summary+'\n\nAUDIT\n'+str(out)+'\n\nNEXT\n'+next_action+'\n\nEARLIER NOTES (historical; current facts above supersede pending-read status)\n'+previous)
    p=ROOT/'verification/NEXT SOURCE AND INFERENCE WORK.json';n=json.loads(p.read_text());n.update(source_audit=str(out),last_turn_classification='progress',new_training_this_turn=False,whole_goal_complete=False);n['next_source_work'][0]=next_action;save(p,n)
    print(out)

if __name__=='__main__':main()
