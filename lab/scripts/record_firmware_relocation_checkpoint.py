"""Publish bounded relocation proof and local review without boot overclaims."""
import hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[1]
save=lambda p,v:p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    report=json.loads((ROOT/'verification/firmware-relocation-CPU-checks.json').read_text())
    assert report['emulator_shutdown_completed'] and report['source_instruction_coverage']==[49,49]
    assert report['initial_RAM_domain']=='zero-filled main RAM'
    local=Path(json.loads((ROOT/'verification/firmware-relocation-local-review-pointer.json').read_text())['directory'])
    original=json.loads((local/'protocol.json').read_text())
    review=dict(status='coordinator_rejected_both_local_source_drafts',same_weights_not_independent=True,issues=['Both drafts falsely identify4E75 as NOP; it is RTS.','Both misidentify802082 as the table-resource loop; it copies the main code to50000. The table-resource loop is8020A0.','Both omit the fourth principal50000 code copy and treat a teardown failure as invalidating observed matched state.'],used_for_weight_training=False)
    save(local/'coordinator-review.json',review)
    out=ROOT/'verification/firmware-relocation-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    files=[ROOT/'verification/firmware-relocation-CPU-checks.json',Path(report['directory'])/'cases.json',Path(report['directory'])/'protocol.json',Path(report['directory'])/'status.json',local/'protocol.json',local/'who-prompts-and-responses.txt',local/'coordinator-review.json',ROOT/'scripts/generate_biwn_firmware_relocation_cpu.py',ROOT/'scripts/check_biwn_firmware_relocation_cpu.py',ROOT/'scripts/review_biwn_firmware_relocation_local.py',ROOT/'projects/black-ice-white-noise/restoration/biwn_firmware_relocation_cpu.c',ROOT/'projects/black-ice-white-noise/restoration/biwn_firmware_relocation_cpu.h']
    manifest=[]
    for i,source in enumerate(files):
        snapshot=out/f'{i:02d}-{source.name}';shutil.copy2(source,snapshot)
        manifest.append(dict(source=str(source),snapshot=str(snapshot),sha256=sha(snapshot)))
    corrected='The ROM bootstrap now has a separately checked C reconstruction: 12 fresh original/C cases cover all49 selected instructions, with full CPU, both stack banks, privateRAM and hardware matching, and clean process shutdown. It copies display data to192000, mainBIOS to80000, resident routines to3000, and relocated main code to50000. Real BSR/RTS802070 copies four table-selected resources atFB2F8 with8byte alignment. It preserves the old196446 word atFB07C, replaces it with4E75 (RTS), and naturally jumps to500D6. InitialROM/CPU/zeroRAM/device fixtures are supplied. The step remains standalone: authentication, DSP header/load, firmware-to-game dispatch/globaltiming and fullplayability are unverified.\n'
    (out/'coordinator-corrected-source-summary.txt').write_text(corrected)
    failures=[dict(directory=str(ROOT/'verification/BIWN-firmware-relocation-CPU'/name),observed_exit_code=134,status='comparisons_matched_shutdown_failed_not_clean_pass')for name in ['20261015T010740.586154Z','20261015T011327.513620Z']]
    summary=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='standalone_firmware_relocation_verified_full_boot_incomplete',directory=str(out),report=report,local_source_review=review,failed_fixture_runs=failures,shutdown_cause='unresolved; repeated-byte RAM failed, zero-filled RAM exits cleanly; temporary safe reset vector experiment did not resolve it and was removed',implementation_authorship='coordinator',local_model_authored_bodies_added=0,new_weight_training=False,whole_game_complete=False,linked_into_continuous_startup=False,manifest=manifest,next_work=['Execute/reconstruct relocated main500D6 and its dependencies, including displayBIOS/GPU/DSP and authenticated header/loading.','Replace supplied60000byte stub and hostfirmwareTOC API prelude with natural firmware-to-game continuation.','Continue localChat usability tests; same-weight roles require independent byte/state checks.'])
    save(out/'review.json',summary);save(ROOT/'verification/firmware-relocation-review.json',summary)
    (out/'who-prompts-and-responses.txt').write_text((local/'who-prompts-and-responses.txt').read_text()+'\nCOORDINATOR REVIEW:\n'+json.dumps(review,indent=2)+'\n\nCOORDINATOR CORRECTED SUMMARY:\n'+corrected)
    current=ROOT/'CURRENT DECOMPILATION.txt';shutil.copy2(current,out/'prior-CURRENT DECOMPILATION.txt')
    current.write_text('STANDALONE ROM BOOTSTRAP RELOCATION — GAME BOOT STILL INCOMPLETE\n'+summary['recorded_at']+'\n\n'+corrected+'\nAUDIT\n'+str(out)+'\n\nEARLIER CONNECTED CHECKPOINT (unchanged)\n'+current.read_text())
    next_path=ROOT/'verification/NEXT SOURCE AND INFERENCE WORK.json';n=json.loads(next_path.read_text())
    n.update(standalone_firmware_relocation_audit=str(out),last_turn_classification='progress',last_turn_authorship='Coordinator fixed source bootstrap relocation49instructions; local analyst/reviewer drafts rejected; nativeChat observation recorded separately.',new_training_this_source_step=False)
    n['next_source_work'][0]='The standalone ROM802000 bootstrap now naturally reaches relocated RAM500D6 with12 clean original/C zeroRAM fixtures/all49instructions. Implement following500D6 firmware dependencies, authenticatedDSP header/load and natural firmware-to-game dispatch to replace supplied60000byte initialstub/hostAPI prelude. Connected stage4000/startup/movie/world proof remains unchanged.'
    save(next_path,n)
    assert all(sha(Path(x['snapshot']))==x['sha256']for x in manifest)
    print(out)

if __name__=='__main__':main()
