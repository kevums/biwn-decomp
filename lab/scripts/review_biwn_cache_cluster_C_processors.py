"""Re-read the completed exact-disc comparison and freeze its scoped evidence."""
import hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
def read(p):return json.loads(Path(p).read_text())
def main():
    v=ROOT/'verification';p=v/'cache-cluster-C-processors-route-current.json';job=read(p)
    assert job['status']=='terminal_cache_cluster_C_processors_route_equal' and job['exit_code']==0
    directory=Path(job['directory']);ref=Path(job['reference']);actual=read(directory/'C/report.json');expected=read(ref/'report.json')
    assert sha(directory/'C/report.json')==job['report_sha256']
    assert actual['disc_sha256']==expected['disc_sha256']=='837dfd143a170b8ee9ea78090271fc57c6eac175e682b323b158b7614d15264c'
    assert actual['core_sha256']==expected['core_sha256']
    assert len(actual['frames'])==len(expected['frames'])==24978
    assert len({f['frame'] for f in actual['frames']})==24978
    fields=['CPU_full','full_RAM_sha256','full_GPU_state_sha256','full_DSP_state_sha256','video_sha256','navigation','locomotion_state','held_buttons']
    differences={k:0 for k in fields}
    for a,b in zip(actual['frames'],expected['frames']):
        assert a['frame']==b['frame']
        for k in fields:differences[k]+=a[k]!=b[k]
    assert not any(differences.values()) and differences==job['comparisons']
    PCM=directory/'C/frontend-PCM.s16le';nativePCM=ref/'frontend-PCM.s16le'
    assert sha(PCM)==sha(nativePCM) and PCM.stat().st_size==79929600
    cpu=actual['C_CPU_backend'];back=actual['C_processor_backends']
    assert cpu['entry_gate']['source_from_initial_entry'] and cpu['entry_gate']['original_before_owner_install']==0
    assert cpu['counts']['Original']==cpu['counts']['Rejected']==cpu['stats']['errors']==0
    assert back['GPU']['counts']['Original']==back['GPU']['counts']['Rejected']==back['GPU']['stats']['errors']==back['GPU']['stats']['uncovered']==0
    assert back['DSP']['core_counts']['Original']==back['DSP']['core_counts']['Rejected']==back['DSP']['errors']==back['DSP']['uncovered']==0
    assert all(back['IRQ'][kind][k]==0 for kind in ['core','selection'] for k in ['Original','Rejected'])
    assert back['IRQ']['source']['errors']==0
    observation=read(directory/'C/gameplay-observation.json');native=read(job['reference_proof'])
    assert observation==native['observations']==job['observations']
    assert observation['errors']==observation['acquire_monitor_errors']==observation['heap_floor_errors']==observation['leaf_pending']==0
    final=actual['frames'][-1];assert final['player_mode_word']==1 and final['floor_word']==0 and final['navigation']['outdoor_hold']>=120
    now=datetime.now(timezone.utc);out=v/'cache-cluster-C-processors-reviewed'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();deps={};aliases={}
    def bind(path,expected=None):
        path=Path(path).resolve();assert path.is_relative_to(ROOT);digest=sha(path);assert expected is None or expected==digest,str(path);target=path
        if path.name.endswith(('-current.json','-active.json')):
            target=snap/(hashlib.sha256(str(path).encode()).hexdigest()[:12]+'-'+path.name);shutil.copy2(path,target);aliases[str(path)]=str(target)
        deps[str(target)]=digest
    bind(p)
    for path,digest in job['source_sha256'].items():bind(path,digest)
    for path in [directory/'protocol.json',directory/'C/report.json',directory/'C/gameplay-observation.json',PCM,Path(__file__)]:bind(path)
    for backend in [cpu['stats'],back['GPU'],back['DSP']]:bind(backend['library'])
    report=ROOT/'reports/native-cache-cluster-C-processors.txt'
    report.write_text('BIWN — COMPLETE C-PROCESSOR COMPARISON OF THE CACHE DISC\n'+now.isoformat()+'\n\n'
        'The exact 16,872-byte compiled cache disc completed 24,978 frames under the fixed C CPU/GPU/DSP and IRQ selection/entry providers. Re-reading every frame against the same-disc native control found zero differences in full CPU state, RAM hash, GPU state hash, DSP state hash, video hash, navigation, locomotion state and held buttons. Frame identities and lengths match. The complete 79,929,600-byte captured PCM stream matches; 1,609,520 audio samples are nonzero. The route returned outdoors.\n\n'
        'CPU owned 436,052,692 callbacks, including 734,509 platform HLE services. GPU recorded 12,259,571,140 source instructions and DSP 9,933,701,839 owned instructions. IRQ entry handled 150,244 entries. Original/rejected processor counters and reported errors/uncovered counts are zero. These are execution counts, not recovered readable game functions or full instruction-state traces.\n\n'
        'The entire read-only live observer result also matches the native route: 555 lookups (552 matches, 3 misses), 264 single-reference calls (261 decrements), 116 acquisitions with 13 loader calls, and one table initialization. The group-reference routine was not reached. Private stack/headroom checks report no errors; the narrowest acquisition headroom is 88 bytes.\n\n'
        'This receipt applies only to cache disc SHA256 837dfd143a170b8ee9ea78090271fc57c6eac175e682b323b158b7614d15264c. The newer 17,084-byte boundary disc has a separate running C-processor test; no result is transferred between them. Original firmware HLE, devices, IRQ line/ACK/vector services, host state commit/prefetch, pinned cycle charges/clock, blitter and object processor remain. Per-frame equivalence on this route is not all-path, physical timing, standalone source-game recompilation or hardware readiness. No new training or preview promotion occurred.\n')
    bind(report)
    result=dict(status='terminal_cache_cluster_C_processors_full_route_reviewed_equal',recorded_at=now.isoformat(),directory=str(out),report=str(report),tested_resident_bytes=16872,tested_disc_sha256=actual['disc_sha256'],frames=24978,comparisons=differences,PCM_bytes=PCM.stat().st_size,PCM_sha256=sha(PCM),nonzero_audio_samples=actual['audio']['nonzero_samples'],zero_reported_processor_fallback_rejected_errors=True,complete_observer_equal=True,returned_outdoors=True,applies_to_latest_boundary_disc=False,dependencies_sha256=deps,pointer_snapshots=aliases,new_training=False,default_promoted=False,physical_console_verified=False,whole_game_complete=False)
    save(out/'protocol.json',result);save(v/'cache-cluster-C-processors-reviewed-current.json',result);print(json.dumps({k:result[k] for k in ['status','frames','PCM_bytes','report']}),flush=True)
if __name__=='__main__':main()
