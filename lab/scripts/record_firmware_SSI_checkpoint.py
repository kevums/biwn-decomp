"""Publish declared receive-timing experiment and preserved baseline."""
import hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];INSTALLED=Path.home()/'.lmstudio/local-ai-lab'
save=lambda p,v:p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
sha=lambda b:hashlib.sha256(b).hexdigest()

def main():
    origin=ROOT/'verification/BIWN-relocated-firmware-observation/20261015T073630.362989Z'
    baseline=ROOT/'verification/BIWN-relocated-firmware-observation/20261015T073527.321710Z'
    old_baseline=ROOT/'verification/BIWN-relocated-firmware-observation/20261015T072026.200411Z'
    replay=ROOT/'verification/BIWN-relocated-firmware-observation/20261015T073511.798054Z'
    report=json.loads((origin/'report.json').read_text());base=json.loads((baseline/'report.json').read_text())
    assert report['emulator_shutdown_completed'] and base['emulator_shutdown_completed']
    assert report['SSI_previous_right_word_applications']==10073 and report['SSI_receive_word_swap_applications']==0
    assert report['SSI_stored_register_observations']==[dict(SMODE=20,SCLK=8,callbacks=10073)]
    baseline_files=['RAM-after-command-DSP.bin','DSP-after-command-program.bin','RAM-after-header-DSP.bin','DSP-after-header-program.bin','RAM-after-header-CPU.bin','DSP-after-header-CPU.bin']
    for name in baseline_files:assert (baseline/name).read_bytes()==(old_baseline/name).read_bytes(),name
    replay_files=['RAM-after-header-DSP.bin','DSP-after-header-program.bin','RAM-after-auth-DSP.bin','DSP-after-auth-program.bin','RAM-after-auth-CPU.bin','DSP-after-auth-CPU.bin']
    for name in replay_files:assert (origin/name).read_bytes()==(replay/name).read_bytes(),name
    ram=(origin/'RAM-after-header-DSP.bin').read_bytes();assert ram[0x4000:0x4020]==ram[0x51162:0x51182]
    cpu_header=report['CPU_continuation_after_CD_header'];rows={x['address']:x for x in cpu_header['visited_instructions']}
    assert rows[0x50a9e]['count']==rows[0x50aa4]['count']==32 and cpu_header['final_CPU']['pc']==0x50ab4
    auth=report['header_auth_DSP_observation'];assert auth['instructions']==340690 and auth['stop_reason']=='source_header_auth_command_acknowledged'
    result=report['auth_result_DSP_observation'];assert result['instructions']==119 and result['stop_reason'].endswith('after_IRQ_return')
    cpu=report['CPU_continuation_after_auth_result'];assert cpu['steps']==373 and cpu['final_CPU']['pc']==0x50be2 and not cpu['CPU_reseeded']
    final=(origin/'RAM-after-auth-result-CPU.bin').read_bytes();assert sha(final[0x180000:0x180000+60000])!='235b342638e4face19e82b68d1fdd6592e58dbf689792ee41d572db465cfc8a4'
    now=datetime.now(timezone.utc).isoformat();out=ROOT/'verification/firmware-SSI-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    summary=('A declared serial receive-timing provider keeps the current callback left word and previous callback right word. Under the existing diagnostic DSP ROM view5 and partial clocks, the original CPU now accepts all32 disc-header bytes, the original DSP completes header processing after340,690 instructions, and a119-instruction DSP result copy returns from its IRQ. The original CPU then executes373steps and reaches a further source303C CD challenge-read wait at50BE2. No header, result or game stub is copied into RAM by the host. The actual stored SMODE is20decimal/0x14 (MODE16), SCLK8;10,073 timing-provider applications and source bus-read assertions are recorded. Corrected untransformed baseline reproduces six prior RAM/DSP files exactly and still rejects the header. The two MODE32-gated swap experiments applied zero swaps; an unconditional swap left marker search pending at its budget. Header acceptance is diagnostic progress, not validated physical channel/strobe timing, game boot, or reconstructed C for these later CPU/DSP paths. Full decompilation and playability remain incomplete.')
    next_action='Execute and trace the next original DSP CD challenge at CPU50BE2, subsequent result copies and source checks; reach real boot-stub loading and natural game dispatch. Validate serial strobe timing and processor ROM mapping independently. Reconstruct second/third DSP and remaining firmware CPU as guarded C, then remove remaining full-game timing/input/task providers. Retest native Chat routing when accessible.'
    prior=json.loads((ROOT/'verification/firmware-CD-header-review.json').read_text())
    pointer=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])/'emulator-runtime/summary.json';compact=json.loads(pointer.read_text())['firmware_bootstrap_DSP_progress'];save(out/'previous-evidence.json',compact)
    diagnostic=compact['diagnostic_firmware_CD_progress'];diagnostic.update(status='diagnostic_timing_accepts_header_next_CD_challenge_pending',header_signature_accepted=True,header_comparison_bytes=32,header_rejection_PC=None,following_CPU_wait='0x50be2',following_original_CPU_steps=373,source_read_still_pending=True,source_read_ack_scope='First header search/read acknowledged; subsequent CD challenge read is pending. Game payload not loaded.',header_auth_DSP_original_instructions=340690,auth_result_DSP_original_instructions=119,header_auth_C_verified=False,SSI_previous_right_provider=dict(selected=True,applications=10073,current_left_previous_right=True,stored_SMODE_decimal=20,stored_SMODE_hex='0x14',MODE='MODE16',stored_SCLK=8,source_bus_reads_asserted=True,hardware_timing_verified=False),header_loaded_RAM_hex=ram[0x4000:0x4020].hex(),hardware_ROM_view_verified=False,physical_global_schedule_verified=False,known60000byte_game_stub_present=False,source_discovery_directory=str(origin))
    diagnostic['disc_header_evidence']['scope']='Historical unchanged input rejects ordering. Current timing input accepts32bytes. Neither is physical hardware verification.'
    compact.update(status=diagnostic['status'],recorded_at=now,audit=str(out),full_report=str(origin/'report.json'),plain_language_summary=summary,next_GPU_CPU_dependency=dict(status='Header accepted under declared receive timing; next CD challenge pending',next_action=next_action))
    compact['processor_responsibilities']['original_CD_followup']='Original CPU and second/third DSP perform TOC, seek, SSI search, header byte comparison, header processing and result copy under declared inputs. CPU now waits on a subsequent CD challenge. These later CPU/DSP paths are discovery, not reconstructed-C proof.'
    for base_dir in [ROOT,INSTALLED]:
        session=Path(json.loads((base_dir/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);p=session/'emulator-runtime/summary.json';data=json.loads(p.read_text());data['firmware_bootstrap_DSP_progress']=compact;save(p,data)
    role_dir=ROOT/'verification/firmware-SSI-local-roles/20261015T072931.384735Z';roles=json.loads((role_dir/'review.json').read_text());assert len(roles['rows'])==2
    roles['coordinator_review']=dict(status='bounded_algebra_and_scope_answers',Analyst='Half-word exchange algebra is correct; suggested header assertion is conditional and not an executed result.',Reviewer='Correctly distinguishes supplied diagnostic inputs from physical verification. Its phrase byte-swapping is imprecise: the experiment exchanges16bit words. Accepted header only proves this declared input follows the source acceptance path, not hardware-correct reconstruction.',independent_verification=False,new_training=False,accepted_code_bodies_added=0)
    save(role_dir/'coordinator-review.json',roles['coordinator_review'])
    files=[Path(__file__),ROOT/'scripts/observe_biwn_relocated_firmware.py',ROOT/'scripts/test_firmware_SSI_local_roles.py',ROOT/'chat_tools.py',role_dir/'review.json',role_dir/'prompts-and-responses.txt',role_dir/'coordinator-review.json']
    files.extend(origin/n for n in ['protocol.json','report.json','status.json','CPU-after-header-DSP.json','auth-DSP-observation.json','CPU-after-auth-DSP.json','auth-result-DSP-observation.json','CPU-after-auth-result-DSP.json'])
    files.extend(origin/n for n in replay_files);files.extend(baseline/n for n in ['protocol.json','report.json','status.json'])
    manifest=[]
    for i,p in enumerate(files):
        target=out/f'{i:02d}-{p.name}';shutil.copy2(p,target);manifest.append(dict(source=str(p),snapshot=str(target),sha256=sha(target.read_bytes())))
    review=dict(status='diagnostic_header_accepted_next_CD_challenge_pending_goal_incomplete',recorded_at=now,directory=str(out),evidence=compact,source_directory=str(origin),baseline_directory=str(baseline),baseline_replayed_files=6,diagnostic_replayed_files=6,manifest=manifest,previous_audit=prior['directory'],local_roles=roles,implementation_authorship='Coordinator instrumented source processors and diagnostic peripheral timing; Analyst/Reviewer ran sequentially on the same local27B model. No new local-model code body accepted.',new_weight_training=False,accepted_local_model_body_count=171,native_UI_verified=False,hardware_timing_verified=False,whole_goal_complete=False,scope_correction='Earlier audit manual-followup incorrectly described SMODE14decimal/MODE32. Recorded stored register value is20decimal/0x14,MODE16. Earlier MODE32-gated runs applied zero swaps; do not count them as channel-swap tests.')
    save(out/'review.json',review);save(ROOT/'verification/firmware-SSI-review.json',review)
    cmd=(ROOT/'runs/firmware-CD-auth-result.log').read_text()
    (out/'who-prompts-and-responses.txt').write_text(review['implementation_authorship']+'\n\nSOURCE INPUTS AND RESULT\n'+summary+'\n\nSOURCE COMMAND\n.venv/bin/python scripts/observe_biwn_relocated_firmware.py --DSP-boot-probe-C --DSP-ROM-view-mame-diagnostic --continue-CPU --attach-CDI --CPU-continuation-budget 2000000 --BUTCH-clock-from-CPU-cycles --run-second-DSP --continue-CPU-after-second-DSP --run-third-DSP --initialize-third-DSP-at-source-GO --continue-CPU-after-third-DSP --run-CD-read-command-DSP --third-DSP-budget 6000000 --continue-CPU-after-CD-read-command --run-CD-descriptor-DSP --continue-CPU-after-CD-descriptor --run-CD-header-DSP --continue-CPU-after-CD-header --SSI-previous-right-word-diagnostic --run-header-auth-DSP --continue-CPU-after-header-auth --run-auth-result-DSP --continue-CPU-after-auth-result\n\nSOURCE LOG\n'+cmd+'\n\nLOCAL ROLES EXACT PROMPTS AND RESPONSES\n'+(role_dir/'prompts-and-responses.txt').read_text()+'\n\nCOORDINATOR ROLE REVIEW\n'+json.dumps(roles['coordinator_review'],indent=2)+'\n')
    # Preserve readable current status and historical details in the audit.
    for name in ['START HERE.txt','CURRENT DECOMPILATION.txt','CURRENT LOCAL INFERENCE.txt']:shutil.copy2(ROOT/name,out/('prior-'+name))
    (ROOT/'CURRENT DECOMPILATION.txt').write_text('LATEST SOURCE BOOT CHECKPOINT\n'+now+'\n\n'+summary+'\n\nNEXT\n'+next_action+'\n\nAUDIT\n'+str(out)+'\n\nEarlier game/firmware proofs retain their original scopes. Local accepted code-body count171 is unchanged. No full-game completion percentage is implied.\n')
    p=ROOT/'verification/NEXT SOURCE AND INFERENCE WORK.json';data=json.loads(p.read_text());data.update(source_audit=str(out),local_audit=str(out),last_turn_classification='progress',new_training_this_turn=False,hardware_ROM_view_verified=False,native_firmware_routing_update_pending=True);data['next_source_work'][0]=next_action;save(p,data)
    print(out)

if __name__=='__main__':main()
