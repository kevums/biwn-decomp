"""Independently reread the completed18270byte scanner C/native comparison."""
import hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def read(p):return json.loads(Path(p).read_text())
def main():
    v=ROOT/'verification';jp=v/'doorway-C-processors-route-current.json';job=read(jp);assert job['status']=='terminal_doorway_C_processors_route_equal' and job['exit_code']==0
    folder=Path(job['directory']);ref=Path(job['reference']);a=read(folder/'C/report.json');b=read(ref/'report.json');assert sha(folder/'C/report.json')==job['report_sha256'];buildp=v/'native-doorway-disc-build-current.json';build=read(buildp);assert a['disc_sha256']==b['disc_sha256']==build['derived_disc_sha256']=='bcf1e502e7a759653105ddc5427093da2bc09a0d1c548b5d44ba7bd11a22e4eb';assert a['core_sha256']==b['core_sha256']
    assert len(a['frames'])==len(b['frames'])==24996 and len({x['frame']for x in a['frames']})==24996
    fields=['CPU_full','full_RAM_sha256','full_GPU_state_sha256','full_DSP_state_sha256','video_sha256','navigation','locomotion_state','held_buttons'];differences={k:0 for k in fields}
    for x,y in zip(a['frames'],b['frames']):
        assert x['frame']==y['frame']
        for k in fields:differences[k]+=x[k]!=y[k]
    assert not any(differences.values())and differences==job['comparisons'];pcm=folder/'C/frontend-PCM.s16le';npcm=ref/'frontend-PCM.s16le';assert sha(pcm)==sha(npcm) and pcm.stat().st_size==npcm.stat().st_size==79987200
    cpu=a['C_CPU_backend'];back=a['C_processor_backends'];assert cpu['entry_gate']['source_from_initial_entry']and cpu['entry_gate']['original_before_owner_install']==0;assert cpu['counts']['Original']==cpu['counts']['Rejected']==cpu['stats']['errors']==0
    assert back['GPU']['counts']['Original']==back['GPU']['counts']['Rejected']==back['GPU']['stats']['errors']==back['GPU']['stats']['uncovered']==0
    assert back['DSP']['core_counts']['Original']==back['DSP']['core_counts']['Rejected']==back['DSP']['errors']==back['DSP']['uncovered']==0
    assert all(back['IRQ'][kind][k]==0 for kind in ['core','selection']for k in ['Original','Rejected'])and back['IRQ']['source']['errors']==0
    observation=read(folder/'C/gameplay-observation.json');native=read(job['reference_proof']);assert observation==native['observations']==job['observations'];assert observation['errors']==observation['copy_errors']==observation['scan_errors']==observation['scan_pending']==observation['scan_stack_outside']==0
    assert observation['door_entries']==observation['door_native_entries']==observation['door_returns']==observation['door_successes']==1
    assert observation['door_old_steps']==observation['door_errors']==observation['door_pending']==observation['door_count_rejects']==observation['door_sentinels']==observation['door_key_mismatches']==observation['door_stack_outside']==0
    assert observation['door_max_depth']==80 and observation['door_min_headroom']==816
    assert observation['scan_entries']==observation['scan_native_entries']==observation['scan_returns']==4753 and observation['scan_successes']==11 and observation['scan_failures']==4742 and observation['scan_old_steps']==0
    final=a['frames'][-1];assert final['player_mode_word']==1 and final['floor_word']==0 and final['navigation']['outdoor_hold']>=120
    now=datetime.now(timezone.utc);out=v/'doorway-C-processors-reviewed'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();deps={};aliases={}
    def bind(path,expected=None):
        p=Path(path).resolve();assert p.is_relative_to(ROOT);h=sha(p);assert expected is None or h==expected,str(p);target=p
        if p.name.endswith(('-current.json','-active.json')):
            target=snap/(hashlib.sha256(str(p).encode()).hexdigest()[:12]+'-'+p.name);shutil.copy2(p,target);aliases[str(p)]=str(target)
        deps[str(target)]=h
    for p in [jp,buildp]:bind(p)
    for p,h in job['source_sha256'].items():bind(p,h)
    for p in [folder/'protocol.json',folder/'C/report.json',folder/'C/gameplay-observation.json',pcm,Path(__file__)]:bind(p)
    for backend in [cpu['stats'],back['GPU'],back['DSP']]:bind(backend['library'])
    report=ROOT/'reports/native-doorway-C-processors.txt';report.write_text('BIWN — COMPLETE18270BYTE DOORWAY DISC C-PROCESSOR COMPARISON\n'+now.isoformat()+'\n\n'
      'The exact18270byte resident doorway disc completed24996frames through the fixed C CPU/GPU/DSP and interrupt selection/entry providers. Every frame identity and all eight recorded fields match its same-disc retained-native control: fullCPU, RAMhash, GPUstatehash, DSPstatehash, videohash, navigation, locomotion and heldbuttons. The complete79987200byte captured stereo16bitPCM stream matches;1609436samples are nonzero. Both returned outdoors.\n\n'
      f"CPUowned {cpu['counts']['Owned']:,} callbacks, including {cpu['stats']['HLE']:,} retained platformHLE services. GPUsource instructions {back['GPU']['C_source_instructions']:,}; DSPowned instructions {back['DSP']['owned']:,}; sourceIRQentries {back['IRQ']['source']['owned']:,}. Reported Original/Rejected/errors/uncovered counts are zero under the separate recorded backend counters. These are execution counts, not recovered readable-function counts or a full all-instruction trace.\n\n"
      'The entire read-only observer result matches the native route, including1compiled doorway success return atframe8557, zero live failure returns,80byte private depth/minimum816byte headroom, and4753compiled scanner calls/11success/4742failure returns. There are no original doorway or scanner body steps and no reported monitor errors/pending/stack-outside. Doorway failure paths remain component-test coverage. SourceCPU begins at the HLE-prepared initial entry, with no original CPU opcodes before owner installation.\n\n'
      'This compares C versus native providers executing the SAME modified18270doorway disc. It does not resolve the separate compiled-scanner-versus-original-scanner-entry timing/video/audio differences, and it does not establish the newer18888interior-selector disc, whose gameplay is untested. PlatformHLE, device services, IRQline/ACK/vector selection plumbing, hostcommit/prefetch/cost/clock, blitter and objectprocessor services remain. No all-path, physical timing, standalone/full source rebuild, default preview promotion or new model training proof.\n')
    bind(report);result=dict(status='terminal_doorway_C_processors_full_route_reviewed_equal',recorded_at=now.isoformat(),directory=str(out),report=str(report),tested_resident_bytes=18270,tested_disc_sha256=a['disc_sha256'],frames=24996,comparisons=differences,PCM_bytes=pcm.stat().st_size,PCM_sha256=sha(pcm),nonzero_audio_samples=a['audio']['nonzero_samples'],zero_reported_processor_fallback_rejected_errors=True,complete_observer_equal=True,doorway_success_returns=1,doorway_failure_returns=0,returned_outdoors=True,applies_to_latest_interior_disc=False,dependencies_sha256=deps,pointer_snapshots=aliases,new_training=False,default_promoted=False,physical_console_verified=False,whole_game_complete=False)
    save(out/'protocol.json',result);save(v/'doorway-C-processors-reviewed-current.json',result);print(json.dumps({k:result[k]for k in ['status','frames','PCM_bytes','report']}))
if __name__=='__main__':main()
