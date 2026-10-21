"""Review exact local-native10430 gameplay and its original-entry control."""
import hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def read(p):return json.loads(Path(p).read_text())
def main():
    v=ROOT/'verification';cp=v/'native-doorway-candidate-current.json';np=v/'native-doorway-control-current.json';candidate,control=read(cp),read(np)
    for d in [candidate,control]:
        assert d['status']=='terminal_native_doorway_route_pending_review' and d['exit_code']==0 and d['returned_outdoors'] and d['live_monitor_pass'] and d['door_monitor_pass']
        o=d['observations'];assert o['door_errors']==o['door_pending']==o['door_stack_outside']==o['errors']==o['copy_errors']==0
        assert d['geometry_monitor_pass'] and d['select_monitor_pass'] and d['scan_monitor_pass']
    bp=v/'native-doorway-disc-build-current.json';build=read(bp);dp=v/'native-doorway-development-reviewed-current.json';dev=read(dp);mp=v/'native-doorway-monitor-current.json';monitor=read(mp)
    assert build['linked_component_bytes']==dev['resident_bytes']==18270 and dev['native_bytes']==458 and dev['raw_candidates_passed']==1
    assert dev['stable_cases']==2025 and dev['changing_cases']==768 and monitor['original_cases']==monitor['compiled_cases']==2025
    cfolder=Path(candidate['directory'])/'candidate';nfolder=Path(control['directory'])/'candidate';a=read(cfolder/'report.json');b=read(nfolder/'report.json');assert a['disc_sha256']==build['derived_disc_sha256']==dev['derived_disc_sha256']
    assert sha(cfolder/'report.json')==candidate['report_sha256'] and sha(nfolder/'report.json')==control['report_sha256']
    assert control['control_delta']['restored_entries']==['10430'] and control['control_delta']['declared_bytes']==8
    assert a['disc_sha256']==control['control_delta']['source_sha256'] and b['disc_sha256']==control['control_delta']['control_sha256']
    fields=['CPU_full','full_RAM_sha256','full_GPU_state_sha256','full_DSP_state_sha256','video_sha256','navigation','locomotion_state','held_buttons'];differences={k:0 for k in fields};first={}
    assert len(a['frames'])>24000 and len(b['frames'])>24000
    for x,y in zip(a['frames'],b['frames']):
        assert x['frame']==y['frame']
        for k in fields:
            if x[k]!=y[k]:differences[k]+=1;first.setdefault(k,x['frame'])
    pcm=sha(cfolder/'frontend-PCM.s16le')==sha(nfolder/'frontend-PCM.s16le');obs=candidate['observations'];original=control['observations']
    assert obs['door_entries']==obs['door_native_entries']==obs['door_returns'] and obs['door_entries']>0 and obs['door_old_steps']==0
    assert original['door_entries']==original['door_returns'] and original['door_native_entries']==0 and original['door_old_steps']>0
    now=datetime.now(timezone.utc);out=v/'native-doorway-live-reviewed'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();deps={};aliases={}
    def bind(path,expected=None):
        p=Path(path).resolve();assert p.is_relative_to(ROOT);h=sha(p);assert expected is None or h==expected,str(p);target=p
        if p.name.endswith(('-current.json','-active.json')):
            target=snap/(hashlib.sha256(str(p).encode()).hexdigest()[:12]+'-'+p.name);shutil.copy2(p,target);aliases[str(p)]=str(target)
        deps[str(target)]=h
    for p in [cp,np,bp,dp,mp]:bind(p)
    for d in [candidate,control]:
        for p,h in d['source_sha256'].items():bind(p,h)
        folder=Path(d['directory']);bind(folder/'protocol.json')
        for name in ['report.json','gameplay-observation.json','frontend-PCM.s16le']:bind(folder/'candidate'/name)
    for d in [dev,monitor]:
        for p,h in d.get('dependencies_sha256',d.get('source_sha256',{})).items():bind(p,h)
    report=ROOT/'reports/native-doorway-live.txt';report.write_text('BIWN — LOCAL NATIVE DOORWAY10430 GAMEPLAY\n'+now.isoformat()+'\n\n'
      f"The18270byte resident disc completed {len(a['frames'])} native gameplay frames; its same-layout original-doorway-entry control completed {len(b['frames'])}. Both returned outdoors. Only the eight-byte10430entry is restored in the control; preceding geometry routines remain compiled in both. Candidate doorway calls: {obs['door_entries']}, including {obs['door_successes']} successes, {obs['door_count_rejects']} count rejections, {obs['door_sentinels']} sentinel rejections and {obs['door_key_mismatches']} key mismatches. Control: {original['door_entries']} calls, {original['door_successes']} successes, {original['door_count_rejects']} count rejections, {original['door_sentinels']} sentinel rejections and {original['door_key_mismatches']} key mismatches. Unreached paths remain component-only.\n\n"
      f"Both live contracts pass full registers/SR/USP/SSP, six object fields, return and argument bytes, ownership and task-stack observations, with zero reported errors/pending/outside. Candidate private depth {obs['door_max_depth']}bytes/minimum task headroom {obs['door_min_headroom']}bytes. The read-only oracle samples stable entry RAM, with source-ordered shadow writes for actor/record overlap; it was first qualified on2025original and2025final-linked compiled fixtures. Controlled changing reads separately cover768cases.\n\n"
      'Aligned prefix differences:\n'+json.dumps(differences,indent=2)+'\nFirst different frames:\n'+json.dumps(first,indent=2)+f"\nCompared prefix {min(len(a['frames']),len(b['frames']))}frames; frame counts equal: {len(a['frames'])==len(b['frames'])}; full captured PCM equal: {pcm}.\n\n"
      'The selected458byte C kernel is the local27B Author\'s repaired output, body unchanged after one guided repair; outer fence removed, redundant standard include retained. The first draft failed header-pointer indirection and its same-weight Reviewer missed the defect. The coordinator supplied contract/layout/fullABI/verifier/integration and a withheld reference; the earlier portable local body was supplied as data. Passing finite component/live contracts is not independent review or training gain. Both routes retain native emulator processors/platform services; exact-disc C-provider testing is separate. Differences are retained as limits, with no physical/cycle/whole-machine equivalence, complete source rebuild or default preview promotion.\n\nExact model work:\n'+dev['transcript']+'\nDevelopment/final-address evidence:\n'+dev['report']+'\n')
    bind(report);bind(Path(__file__))
    result=dict(status='terminal_native_doorway_two_live_routes_reviewed',recorded_at=now.isoformat(),directory=str(out),report=str(report),build=str(bp),build_sha256=sha(bp),candidate_frames=len(a['frames']),control_frames=len(b['frames']),compared_prefix_frames=min(len(a['frames']),len(b['frames'])),frame_counts_equal=len(a['frames'])==len(b['frames']),same_layout_differences=differences,first_differing_frames=first,PCM_equal=pcm,candidate_observations=obs,control_observations=original,live_monitor_pass=True,processors='Retained native emulator processors/platform services',derived_disc=build['derived_disc'],derived_disc_sha256=build['derived_disc_sha256'],resident_bytes=18270,native_bytes=458,stable_cases=2025,changing_cases=768,kernel_attribution=dev['kernel_attribution'],accepted_local_body_edited=False,dependencies_sha256=deps,pointer_snapshots=aliases,new_training=False,native_Chat_verified=False,default_promoted=False,whole_game_complete=False,physical_console_verified=False)
    save(out/'protocol.json',result);save(v/'native-doorway-live-reviewed-current.json',result);print(json.dumps({k:result[k]for k in ['status','candidate_frames','control_frames','same_layout_differences','PCM_equal','report']}))
if __name__=='__main__':main()
