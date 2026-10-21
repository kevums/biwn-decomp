"""Record pinned scan failure, separate seek experiment and TOC checksum rejection."""
import hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];INSTALLED=Path.home()/'.lmstudio/local-ai-lab'
save=lambda p,v:p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
sha=lambda b:hashlib.sha256(b).hexdigest()

def from_log(name):
    return next(Path(x)for x in (ROOT/'runs'/name).read_text().splitlines()if x.startswith('/')and '/BIWN-relocated-'in x)

def main():
    pinned=from_log('firmware-CD-pinned-full-challenges.log');origin=from_log('firmware-fourth-DSP-witnessed.log');off=from_log('firmware-CD-reseek-off-exported.log')
    stock=json.loads((pinned/'report.json').read_text());report=json.loads((origin/'report.json').read_text())
    assert stock['emulator_shutdown_completed'] and report['emulator_shutdown_completed']
    assert stock['execution_core_sha256']=='c2990c86f54473b55a68ee2493c50b6e584e4ac81a46bfb7e593611133e8e856'
    assert report['execution_core_sha256']=='e082a521cdbc8600e4e1c583802811e5e4fb0bd9ad1251affcd0c6214358495a'and report['force_repeated_seek_diagnostic']
    old=ROOT/'verification/BIWN-relocated-firmware-observation/20261015T074611.256801Z'
    replay=['RAM-after-first-DSP.bin','DSP-after-first-program.bin','RAM-after-header-DSP.bin','DSP-after-header-program.bin','RAM-after-auth-result-CPU.bin','DSP-after-auth-result-CPU.bin']
    for name in replay:assert (old/name).read_bytes()==(off/name).read_bytes()==(origin/name).read_bytes(),name
    scan=stock['CD_challenge_observation']['phases'][0]['DSP'];assert scan['marker_comparisons']==32768 and scan['marker_matches']==0 and scan['instructions']==26075387
    assert stock['CD_challenge_observation']['final_CPU']['pc']==0x505fa
    challenge=report['CD_challenge_observation'];first=challenge['phases'][0]['DSP'];assert first['marker_matches']==16 and first['marker_comparisons']==3527 and first['instructions']==10076298
    fourth=report['fourth_DSP_phases'];assert len(fourth['phases'])==2 and fourth['final_CPU']['pc']==0x505fa
    assert report['fourth_DSP_observation']['DSP']['instructions']==44
    assert fourth['phases'][0]['DSP']['instructions']==29259 and fourth['phases'][1]['DSP']['instructions']==43
    cpu=fourth['phases'][1]['CPU'];rows={x['address']:x for x in cpu['visited_instructions']};assert rows[0x50df4]['assembly']=='bne.w $504ec'
    folder=Path(fourth['phases'][1]['directory']);RAM=(folder/'RAM-after-DSP.bin').read_bytes();expected=RAM[0xfb004:0xfb014];actual=RAM[0xfb1b0:0xfb1c0]
    assert expected.hex()=='40ad9111f99460149c0cb36d7ef13724'and actual.hex()=='1f15655720541c9daf7557e7905ad21b'and actual!=expected
    probes=json.loads((ROOT/'verification/BIWN-TOC-checksum-inputs-current.json').read_text());assert len(probes['cases'])==7 and not any(x['matches_header']for x in probes['cases'])
    assert probes['cases'][0]['computed_checksum']==actual.hex()
    build=json.loads((ROOT/'verification/BIWN-reseek-diagnostic-build-current.json').read_text());tests=json.loads((Path(build['directory'])/'verified-tests.json').read_text());assert all(x['returncode']==0 for x in tests['tests'])
    now=datetime.now(timezone.utc).isoformat();out=ROOT/'verification/firmware-TOC-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    summary=('Under the earlier DSP-ROM-view5 and previous-right-word timing inputs, the pinned core completes a32,768-comparison marker scan with zero matches and returns to BIOS wait505FA. A separate diagnostic core forcing repeated seeks finds16marker words, advances through the challenge/result handoffs, stops the third DSP and initializes a fourth DSP at source GO before its command. Fourth initialization executes44instructions; its TOC command29259instructions and CPU-IRQ reply43instructions. The original CPU rejects the first returned checksum word at50DF4 and returns to505FA. Header-supplied expected checksum40ad9111f99460149c0cb36d7ef13724 differs from computed1f15655720541c9daf7557e7905ad21b. Seven captured-state TOC-input probes reproduce the baseline hash but no candidate matches. These are diagnostic/native discoveries, not reconstructed C for later processors, physical timing proof or full boot. No expected checksum, header or game stub is injected. The ordinary core/BIOS/CDI and local-model accepted-code count171 remain unchanged.')
    next_action='Trace the second DSP DSA/TOC acquisition and compare exact session, lead-out, pregap/index and duration semantics with the CDI descriptor and primary drive documentation. Derive the fourth DSP TOC checksum as checked C and test independently. Resolve the input mismatch without injecting the expected checksum; then reach real stub loading and game dispatch. Continue remaining game reconstruction, physical/global timing and native Chat usability.'
    previous=json.loads((ROOT/'verification/firmware-SSI-review.json').read_text())
    pointer=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])/'emulator-runtime/summary.json';compact=json.loads(pointer.read_text())['firmware_bootstrap_DSP_progress'];save(out/'previous-evidence.json',compact)
    experiments=dict(pinned=dict(core_sha256=stock['execution_core_sha256'],real_seek_count=1,marker_scan_instructions=26075387,marker_comparisons=32768,marker_matches=0,result='scan limit then BIOS rejection',final_CPU='0x505fa',directory=str(pinned)),repeat_seek_diagnostic=dict(core_sha256=report['execution_core_sha256'],repeated_seek_forced=True,real_seek_count=2,marker_scan_instructions=10076298,marker_comparisons=3527,marker_matches=16,challenge_phases=10,fourth_DSP_initialization_instructions=44,fourth_TOC_DSP_instructions=29259,fourth_reply_DSP_instructions=43,expected_header_checksum=expected.hex(),computed_TOC_checksum=actual.hex(),checksum_matches=False,rejection_PC='0x50df4',final_CPU='0x505fa',source_GO_initialization_order_checked=True,directory=str(origin)),captured_TOC_probes=dict(cases=7,matches=0,first_baseline_checksum_reproduced=True,captured_boundary_and_TOC_inputs=True,SSI_clocks_held=True,natural_boot=False,report=str(Path(probes['directory'])/'report.json')),source_C_verified_for_these_later_phases=False,hardware_ROM_view_verified=False,physical_global_timing_verified=False,known60000byte_game_stub_loaded=False,host_expected_result_or_payload_injected=False)
    compact.update(status='diagnostic_TOC_checksum_rejection_observed',recorded_at=now,plain_language_summary=summary,audit=str(out),full_report=str(origin/'report.json'),current_CD_authentication_experiments=experiments,next_GPU_CPU_dependency=dict(status='Fourth DSP TOC checksum mismatch is a concrete boot gate',next_action=next_action))
    diag=compact['diagnostic_firmware_CD_progress'];diag.update(status=compact['status'],following_CPU_wait='0x505fa',source_read_still_pending=False,source_read_ack_scope='Pinned scan fails; separate force-reseek input reaches TOC checksum rejection. No completed firmware/game boot.',fourth_TOC_checksum_expected=expected.hex(),fourth_TOC_checksum_computed=actual.hex(),fourth_TOC_checksum_matches=False,source_discovery_directory=str(origin),known60000byte_game_stub_present=False)
    compact['processor_responsibilities']['original_CD_followup']='Original second/third/fourth DSP and original main CPU discovery under declared ROM/SSI inputs and optional separately hashed repeat-seek core. Fourth TOC hash fails source CPU comparison. Later paths are not reconstructed-C or hardware proofs.'
    for base in [ROOT,INSTALLED]:
        session=Path(json.loads((base/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);p=session/'emulator-runtime/summary.json';d=json.loads(p.read_text());d['firmware_bootstrap_DSP_progress']=compact;save(p,d)
    advertising=json.loads((ROOT/'verification/advertising-sampling-reviewed.json').read_text())
    files=[Path(__file__),ROOT/'scripts/observe_biwn_relocated_firmware.py',ROOT/'scripts/observe_biwn_CD_challenge_phases.py',ROOT/'scripts/build_biwn_reseek_diagnostic_core.py',ROOT/'scripts/probe_biwn_TOC_checksum_inputs.py',ROOT/'lab.py',ROOT/'chat_tools.py',Path(probes['directory'])/'report.json',Path(build['directory'])/'build.json',Path(build['directory'])/'verified-tests.json',ROOT/'verification/advertising-sampling-reviewed.json']
    for folder_path in [origin,pinned]:files.extend(folder_path/n for n in ['protocol.json','report.json','status.json','challenge-phases.json'])
    files.extend(origin/n for n in ['fourth-DSP-command.json','fourth-phases.json']);files.extend(folder/n for n in ['DSP-report.json','CPU-report.json','RAM-after-DSP.bin','DSP-after.bin'])
    manifest=[]
    for i,p in enumerate(files):
        target=out/f'{i:02d}-{p.name}';shutil.copy2(p,target);manifest.append(dict(source=str(p),snapshot=str(target),sha256=sha(target.read_bytes())))
    review=dict(status='source_TOC_gate_found_advertising_workflow_repaired_goal_incomplete',recorded_at=now,directory=str(out),evidence=compact,experiments=experiments,diagnostic_build=build,diagnostic_tests=tests,advertising=advertising,manifest=manifest,previous_audit=previous['directory'],authorship='Coordinator instruments source execution, diagnostic drive switch, checksum input probes and REST capability/contract gates. Local Researcher/Educator/Reviewer use same weights within each model; base and trainedpilot are compared sequentially. No new local-model source body or weight training.',accepted_local_model_body_count=171,new_weight_training=False,temporary_model_switches=True,default_promotion=False,native_Chat_verified=False,whole_goal_complete=False)
    save(out/'review.json',review);save(ROOT/'verification/firmware-TOC-review.json',review)
    transcript=review['authorship']+'\n\nSOURCE SUMMARY\n'+summary+'\n\nEXACT SOURCE COMMANDS\n'
    for n in ['pinned-challenge-command.json','fourth-DSP-ordered-command.json','reseek-command-on.json']:transcript+=n+'\n'+(ROOT/'runs'/n).read_text()+'\n'
    transcript+='\nADVERTISING COORDINATOR REVIEW\n'+json.dumps(advertising,indent=2)+'\n'
    ad=Path(advertising['directory'])
    for p in sorted(ad.rglob('prompts-and-responses.txt')):transcript+='\nEXACT LOCAL REQUEST/RESPONSE FILE: '+str(p)+'\n'+p.read_text()+'\n'
    (out/'who-prompts-and-responses.txt').write_text(transcript)
    for name in ['START HERE.txt','CURRENT DECOMPILATION.txt','CURRENT LOCAL INFERENCE.txt']:shutil.copy2(ROOT/name,out/('prior-'+name))
    (ROOT/'CURRENT DECOMPILATION.txt').write_text('CURRENT SOURCE BOOT CHECKPOINT\n'+now+'\n\n'+summary+'\n\nNEXT\n'+next_action+'\n\nAUDIT\n'+str(out)+'\n')
    (ROOT/'START HERE.txt').write_text('LOCAL AI LAB — START HERE\n\nDouble-click Game Model.command or Advertising Model.command. In LM Studio Chat select Game Assistant or Advertising Assistant and enable local-ai-lab tools.\n\nDaily27B/6bit,32K context,one worker. Trained Analysis Pilot v2 remains loadable/experimental; base stays default.\n\nGAME QUESTION\nUse project_evidence with topic boot_loader. What is the latest BIWN boot gate?\n\nLATEST SOURCE\nFirmware diagnostics reach a fourth-DSP TOC checksum rejection. Full boot and full C game remain unfinished; normal core/disc untouched.\n\nADVERTISING\nREST roles explicitly have no tools; reasoning settings respect the loaded model capabilities. Reviewed132word base lesson passes this bounded task. Trainedpilot lesson needs one grading-wording correction; corrected copy is separately labelled. No new training or default promotion.\n\nTEACHING COPIES\n'+str(ad/'fresh-final-repairs/contract-repair-3/base-reviewed-lesson.txt')+'\n'+str(ad/'fresh-final-repairs/contract-repair-3/pilot-reviewed-teaching-copy.txt')+'\n\nWHO DID WHAT / EXACT PROMPTS AND RESPONSES\n'+str(out/'who-prompts-and-responses.txt')+'\n\nNative Chat current retest still pending; API/SDK output is not native Chat verification. Future256GB profile remains unbenchmarked.\n')
    p=ROOT/'verification/NEXT SOURCE AND INFERENCE WORK.json';d=json.loads(p.read_text());d.update(source_audit=str(out),local_audit=str(out),last_turn_classification='progress',new_training_this_turn=False,advertising_sampling_review=advertising,native_firmware_routing_update_pending=True);d['next_source_work'][0]=next_action;save(p,d)
    print(out)

if __name__=='__main__':main()
