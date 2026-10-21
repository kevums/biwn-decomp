"""Audit/publish the terminal24975frame initial-entry combined route; no game rerun."""
import copy,json,subprocess
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
def read(p):return json.loads(Path(p).read_text())

def main():
    route_path=ROOT/'verification/external-DSP-combined-route-current.json';route=read(route_path);assert route['status']=='terminal_initial_entry_external_DSP_combined_merchant_equal'
    directory=Path(route['directory']);reference=Path(route['reference']);assert route['exit_code']==0
    observation=subprocess.run(['ps','-p',str(route['pid'])+','+str(route['child_pid']),'-o','pid=,command='],capture_output=True,text=True);assert not observation.stdout.strip(),'Do not bind a still-running output directory'
    candidate=read(directory/'C/report.json');control=read(reference/'report.json');assert sha(directory/'C/report.json')==route['report_sha256']
    assert len(candidate['frames'])==len(control['frames'])==24975
    fields=['CPU_full','full_RAM_sha256','full_GPU_state_sha256','full_DSP_state_sha256','video_sha256','navigation','locomotion_state','held_buttons']
    comparisons={key:sum(a[key]!=b[key]for a,b in zip(candidate['frames'],control['frames']))for key in fields};assert not any(comparisons.values())and comparisons==route['comparisons']
    pcm=directory/'C/frontend-PCM.s16le';refpcm=reference/'frontend-PCM.s16le';assert sha(pcm)==sha(refpcm)and pcm.stat().st_size==refpcm.stat().st_size
    cpu=candidate['C_CPU_backend'];backends=candidate['C_processor_backends'];dsp=backends['DSP'];assert cpu['entry_gate']['original_before_owner_install']==0 and cpu['entry_gate']['source_from_initial_entry']
    assert cpu['counts']['Original']==cpu['counts']['Rejected']==cpu['stats']['errors']==0
    assert backends['GPU']['counts']['Original']==backends['GPU']['counts']['Rejected']==backends['GPU']['stats']['errors']==0
    assert dsp['errors']==dsp['uncovered']==dsp['core_counts']['Original']==dsp['core_counts']['Rejected']==0 and dsp['external_program']['owned']==460
    assert all(backends['IRQ'][group][key]==0 for group in ['core','selection']for key in ['Original','Rejected'])
    final=candidate['frames'][-1];assert final['player_mode_word']==1 and final['floor_word']==0 and final['navigation']['outdoor_hold']>=120
    assert candidate['audio']['nonzero_samples']==route['nonzero_audio_samples']==1609486
    pp=ROOT/'verification/source-CPU-entry-gameplay-publication-current.json';parent=read(pp);assert parent['current_status']['external_DSP_repair']['full_combined_route_verified']is False
    frozen=Path(parent['directory'])/'publication.json';assert sha(frozen)==sha(pp)
    deps=dict(parent['status_dependencies_sha256'])
    def add(p,expected=None):
        p=Path(p).resolve();assert p.is_relative_to(ROOT);digest=sha(p);assert expected is None or digest==expected,str(p);assert str(p)not in deps or deps[str(p)]==digest,str(p);deps[str(p)]=digest
    add(frozen)
    for p in directory.rglob('*'):
        if p.is_file():add(p)
    for path,digest in route['source_sha256'].items():add(path,digest)
    add(Path(__file__))
    for i,(path,digest)in enumerate(deps.items()):
        assert sha(path)==digest,path
        if i%1000==0:print('Bound evidence checked',i,'/',len(deps),flush=True)
    now=datetime.now(timezone.utc);out=ROOT/'verification/external-DSP-long-route-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    facts=dict(status='terminal_initial_entry_combined_merchant_outdoor_route_equal',frames=24975,all_eight_fields_equal=True,comparisons=route['comparisons'],complete_PCM_byte_equal=True,PCM_bytes=pcm.stat().st_size,PCM_sha256=sha(pcm),nonzero_audio_samples=1609486,
       ordinary_C_CPU_steps=cpu['stats']['steps'],retained_platform_HLE_adapters=cpu['stats']['HLE'],CPU_Original=0,CPU_Rejected=0,CPU_errors=0,original_CPU_before_owner_install=0,C_GPU_instructions=backends['GPU']['counts']['Owned'],C_DSP_instructions=dsp['core_counts']['Owned'],external_DSP_instructions=dsp['external_program']['owned'],source_IRQ_entries=backends['IRQ']['core']['Owned'],source_IRQ_selection_calls=backends['IRQ']['selection']['Owned'],all_processor_Original_fallback_and_rejection_zero=True,
       final_player_mode=final['player_mode_word'],final_floor=final['floor_word'],outdoor_hold_frames=final['navigation']['outdoor_hold'],division_provider_counts=route['division_provider_counts'],proof=str(directory/'protocol.json'),proof_sha256=sha(directory/'protocol.json'),native_reference_reused=True,reference=str(reference/'report.json'),reference_sha256=sha(reference/'report.json'),tested_disc=candidate['disc'],tested_disc_sha256=candidate['disc_sha256'],scope=route['scope'],physical_console_verified=False,whole_game_complete=False)
    summary=('The repaired disc completed a fresh 24,975-frame merchant/media/outdoor-return route with source C CPU execution from the HLE-prepared initial PC,source C GPU/DSP and source interrupt selection/entry together. Every frame matches the retained-native control in full CPU state,all 2 MB RAM,saved GPU/DSP state,video,navigation,locomotion and held controls. The complete '+str(pcm.stat().st_size)+'-byte PCM capture matches,including 1,609,486 nonzero samples;the final player is outdoors on floor zero after a 120-frame hold. '
      'There are zero original CPU instructions before owner installation and zero original processor fallback,rejections or provider errors during this finite route. The external DSP extension executes all 460 formerly uncovered instructions without fallback;the earlier frame-15,849 combined failure is resolved on this route. '
      'Counters include 435,201,975 ordinary source C CPU steps and 734,506 retained platform HLE adapter calls. These are execution counts,not recovered high-level function counts or a decompilation percentage. Platform firmware HLE,devices,IRQ lines/ACK/vector resolution,host state commit/prefetch/cost/clock and blitter/objectprocessor services remain. '
      'Local Code Author supplied the external ADDC body;its two MTOI drafts were rejected and Codex corrected MTOI. This execution result does not establish full readable game source,a standalone source-built Jaguar game,physical boot/audio,general speedup or learned-model quality. The separate new native frame-release port is not installed in this tested disc. The current preview is not restarted or promoted.')
    current=copy.deepcopy(parent['current_status']);current.update(recorded_at=now.isoformat(),checked_answer=summary,checked_current_summary=summary,current_verified_route_summary=summary,long_initial_entry_combined_route=facts,long_route_scope=facts['scope']+' Completed24975frames with all8per-frame fields andwholePCM equal;retained-native reference reused. Not the newer14972byte frame-release candidate.',native_Chat_verified=False,new_training=False,default_promoted=False,goal_complete=False)
    current['external_DSP_repair'].update(full_combined_route_verified=True,full_combined_route=facts)
    current['source_CPU_from_initial_entry']['long_combined_route']=facts
    current['unresolved_runtime_failure']=dict(status='prior_external_DSP_failure_resolved_on_this_finite_route',historical_failure=parent['current_status']['latest_combined_route_failure'],full_combined_route_retest_pending=False,resolution_proof=facts['proof'],other_unverified_paths_remain=True)
    report=ROOT/'reports/BIWN-combined-initial-entry-long-route.txt';current['report']=str(report)
    report.write_text('BIWN — VERIFIED COMBINED INITIAL-ENTRY ROUTE\n'+now.isoformat()+'\n\n'+summary+'\n\nTerminal execution proof: '+facts['proof']+'\nRetained-native reference: '+facts['reference']+'\nExact executed command,source/library/core hashes: '+str(directory/'protocol.json')+'\n\nNo model inference or training was invoked by this publication. No physical-console or whole-game completion claim.\n')
    add(report);save(out/'independent-terminal-audit.json',dict(comparisons=comparisons,complete_PCM_equal=True,PCM_bytes=pcm.stat().st_size,processes_terminal=True,terminal_process_observation=observation.stdout,facts=facts));add(out/'independent-terminal-audit.json')
    pub=dict(parent,directory=str(out),recorded_at=now.isoformat(),parent_publication=str(frozen),current_status=current,report=str(report),status_dependencies_sha256=deps,evidence_files_verified=len(deps),integrity_mismatches=[])
    save(out/'publication.json',pub);save(pp,pub);save(ROOT/'verification/external-DSP-long-route-publication-current.json',pub);save(ROOT/'verification/external-DSP-publication-current.json',pub)
    print(json.dumps(dict(status='terminal_initial_entry_combined_long_route_published',frames=24975,bound_files=len(deps),PCM_bytes=pcm.stat().st_size,report=str(report))),flush=True)
if __name__=='__main__':main()
