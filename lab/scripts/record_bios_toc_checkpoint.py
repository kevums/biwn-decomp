"""Archive actual TOC linkage and exact local explanation, with bounded scope."""
import hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
save=lambda p,v:p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    cp=read(ROOT/'verification/startup-loading-movie-world-checkpoint.json');assert cp['actual_BIOS305A_TOC_CPU_linked']and not cp['synthetic_TOC_supplied']and not cp['initial_TOC_supplied']and not cp['source_boot_verified']
    assert cp['verified_profiles']==2 and cp['BIOS_TOC_proof']['source_instruction_coverage']==[174,184]and cp['source_BIOS_TOC_BUTCH_ticks']==157
    local=Path(read(ROOT/'verification/easy-bios-toc-scope-pointer.json')['directory']);a=read(local/'protocol.json');i=a['results'][0]
    assert a['status']=='completed_pending_coordinator_review'and not i['quality_flags']and i['words']<160 and all(s['stats']['stopReason']=='eosFound'for s in i['prediction_stats'])
    assert 'Startup no longer receives a synthetic TOC' in i['answer']and '174 of 184' in i['answer']and '157 ticks' in i['answer']
    now=datetime.now(timezone.utc);out=ROOT/'verification/bios-toc-local-review'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    paths=[Path(__file__),ROOT/'scripts/prepare_bios_toc_evidence.py',ROOT/'scripts/generate_biwn_bios_toc_cpu.py',ROOT/'scripts/check_biwn_bios_toc_cpu.py',ROOT/'scripts/biwn_bios_toc_runtime.py',ROOT/'scripts/check_biwn_bios_toc_music_cold_entry_scheduled_startup.py',ROOT/'scripts/check_bios_toc_mcp.py',ROOT/'scripts/test_bios_toc_scope.py',ROOT/'verification/startup-loading-movie-world-checkpoint.json',ROOT/'verification/bios-toc-CPU-checks.json',ROOT/'verification/bios-toc-MCP-check.json',ROOT/'verification/bios-TOC-synthetic-comparison.json',ROOT/'chat_tools.py',local/'protocol.json',local/'prompts-and-responses.txt']
    manifest=[]
    for n,p in enumerate(paths):
        target=out/f'{n:02d}-{p.name}';shutil.copy2(p,target);assert sha(p)==sha(target);manifest.append(dict(source=str(p),snapshot=str(target),sha256=sha(p)))
    reviews=['Correctly reports no supplied TOC, source305A buffer/reply/MSF/status behavior,174/184coverage,157pollticks,two connected profiles and incomplete boot/playability.','Uses internal boolean names and omits some supplied fixture details from its concise answer: hostloaded stage/firmware, CPU/device seed, controlled input/taskquiescence and file transport remain in authoritative evidence. Uncovered branches are a verification gap, not proof the current valid disc cannot boot.']
    report=dict(status='actual_BIOS305A_TOC_linkage_verified_local_core_scope_accepted',recorded_at=now.isoformat(),directory=str(out),source_audit=cp['audit'],model=a['model'],interface=a['interface'],words=i['words'],seconds=i['seconds'],semantic_review=reviews,native_Chat_verified=False,new_training=False,model_defaults_changed=False,whole_goal_complete=False,authorship=cp['implementation_authorship'],manifest=manifest)
    save(out/'review.json',report);save(ROOT/'verification/bios-toc-local-review.json',report)
    (out/'who-prompts-and-responses.txt').write_text('COORDINATOR\n'+cp['implementation_authorship']+'\nGenerated184fixedsource instructions, checked174in12standalone original/C runs, then replaced syntheticTOC in continuous source4000 startup/movie/world. Two profiles match complete state/RAM/traces/WAV bytes. TOC differs from host fixture in16bytes but allfive track-start MSFs agree. Ten unexercised branches remain unverified.\n\nLOCAL GAME ASSISTANT\n'+(local/'prompts-and-responses.txt').read_text()+'\n\nCOORDINATOR REVIEW\n'+'\n'.join(reviews)+'\n')
    p=ROOT/'verification/NEXT SOURCE AND INFERENCE WORK.json';n=read(p);n.update(source_audit=cp['audit'],local_audit=str(out),last_turn_classification='progress');n['next_source_work'][0]='Actual residentBIOS3000/3048/3006/305A linked from hostloadedROM. No syntheticTOC supplied;174of184TOC instructions checked on actualBIWN. Implement remaining CD transport/GPU CDISR, firmware relocation/stage-load/boot; replace source-poll controller ticks with verified global schedule. Otherdisc/error paths still need validation.';save(p,n)
    print(json.dumps(dict(status=report['status'],directory=str(out),words=i['words'],seconds=i['seconds'])))
if __name__=='__main__':main()
