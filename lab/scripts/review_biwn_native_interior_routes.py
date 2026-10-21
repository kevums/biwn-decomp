"""Review the two fresh exact-layout interior-selector gameplay routes."""
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT, sha, save


def read(p):return json.loads(Path(p).read_text())


def main():
    v=ROOT/'verification';cp=v/'native-interior-candidate-current.json';op=v/'native-interior-control-current.json'
    candidate,control=read(cp),read(op)
    for d in [candidate,control]:
        assert d['status']=='terminal_native_interior_route_pending_review' and d['exit_code']==0
        assert d['returned_outdoors'] and d['live_monitor_pass'] and d['interior_monitor_pass']
        assert d['door_monitor_pass'] and d['geometry_monitor_pass'] and d['select_monitor_pass'] and d['scan_monitor_pass']
        o=d['observations']
        assert o['interior_entries']==o['interior_returns']>0
        assert o['interior_errors']==o['interior_pending']==o['interior_stack_outside']==o['errors']==o['copy_errors']==0
        assert sum(o['interior_kind_entries'])==o['interior_entries']
    bp=v/'native-interior-select-disc-build-current.json';build=read(bp)
    dp=v/'native-interior-development-reviewed-current.json';dev=read(dp)
    mp=v/'native-interior-monitor-current.json';monitor=read(mp)
    assert build['linked_component_bytes']==dev['resident_bytes']==18888 and dev['component_bytes']==616
    assert monitor['original_cases']==monitor['compiled_cases']==1958 and len(monitor['negative_controls'])==2
    cf=Path(candidate['directory'])/'candidate';of=Path(control['directory'])/'candidate'
    a,b=read(cf/'report.json'),read(of/'report.json')
    assert a['disc_sha256']==build['derived_disc_sha256']==dev['derived_disc_sha256']
    assert sha(cf/'report.json')==candidate['report_sha256'] and sha(of/'report.json')==control['report_sha256']
    delta=control['control_delta'];assert delta['restored_entries']==['10520','105da'] and delta['declared_bytes']==16
    assert delta['source_sha256']==a['disc_sha256'] and delta['control_sha256']==b['disc_sha256']
    assert a['core_sha256']==b['core_sha256']
    fields=['CPU_full','full_RAM_sha256','full_GPU_state_sha256','full_DSP_state_sha256','video_sha256','navigation','locomotion_state','held_buttons']
    differences={key:0 for key in fields};first={}
    assert len(a['frames'])>24000 and len(b['frames'])>24000
    for left,right in zip(a['frames'],b['frames']):
        assert left['frame']==right['frame']
        for key in fields:
            if left[key]!=right[key]:differences[key]+=1;first.setdefault(key,left['frame'])
    pcm=sha(cf/'frontend-PCM.s16le')==sha(of/'frontend-PCM.s16le')
    obs,original=candidate['observations'],control['observations']
    assert obs['interior_entries']==obs['interior_native_entries'] and obs['interior_old_steps']==0
    assert original['interior_native_entries']==0 and original['interior_old_steps']>0
    for d in [obs,original]:assert d['door_native_entries']==d['door_entries'] and d['door_old_steps']==0
    now=datetime.now(timezone.utc);out=v/'native-interior-live-reviewed'/now.strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();deps={};aliases={}
    def bind(path,expected=None):
        p=Path(path).resolve();assert p.is_relative_to(ROOT);h=sha(p);assert expected is None or h==expected,str(p)
        target=p
        if p.name.endswith(('-current.json','-active.json')):
            target=snap/(hashlib.sha256(str(p).encode()).hexdigest()[:12]+'-'+p.name);shutil.copy2(p,target);aliases[str(p)]=str(target)
        deps[str(target)]=h
    for p in [cp,op,bp,dp,mp,Path(__file__)]:bind(p)
    for d in [candidate,control]:
        for p,h in d['source_sha256'].items():bind(p,h)
        folder=Path(d['directory']);bind(folder/'protocol.json')
        for name in ['report.json','gameplay-observation.json','frontend-PCM.s16le']:bind(folder/'candidate'/name)
    for d in [dev,monitor]:
        for p,h in d.get('dependencies_sha256',d.get('source_sha256',{})).items():bind(p,h)
    report=ROOT/'reports/native-interior-select-live.txt'
    report.write_text('BIWN — LOCAL INTERIOR SELECTOR GAMEPLAY\n'+now.isoformat()+'\n\n'
      f"The18888byte resident candidate completed {len(a['frames'])} fresh gameplay frames; its same-layout control completed {len(b['frames'])}. Both returned outdoors. The control restores only the two eight-byte10520/105DAentries; previous doorway/geometry routines remain compiled in both. Candidate/control call counts by actor and sprite: {obs['interior_kind_entries']}/{original['interior_kind_entries']}; successes {obs['interior_kind_successes']}/{original['interior_kind_successes']}; failures {obs['interior_kind_failures']}/{original['interior_kind_failures']}. Combined candidate skipped scans {obs['interior_skips']}, scan iterations {obs['interior_iterations']}. Unreached per-kind paths remain component coverage.\n\n"
      f"The candidate executed {obs['interior_entries']} compiled entries and {obs['interior_returns']} returns, with no original selector body steps. The control executed {original['interior_entries']} original entries/returns and no compiled selector entries. Both stable-entry oracles pass fullD/A/SR/USP/SSP, actor six fields/sprite selected field, argument/return bytes and observed task stacks, with zero reported interior errors/pending/outside. Candidate maximum private depth {obs['interior_max_depth']}bytes/minimum task headroom {obs['interior_min_headroom']}bytes; control {original['interior_max_depth']}/{original['interior_min_headroom']}.\n\n"
      'The read-only oracle was qualified on1958original+1958final-address compiled stable fixtures, including two corrupted-return negatives and entry/return RAM immutability guards. Its fixture-only task-ID adapter avoids altering dense table RAM; live task ID is read fromC0920. Predictions use stable entry RAM and ordered shadow writes for actor/record overlap. Changing/concurrent/device reads and arbitrary interleavings are not independently predicted live;768changing-read component cases remain separate.\n\n'
      'Aligned-prefix differences:\n'+json.dumps(differences,indent=2)+'\nFirst different frames:\n'+json.dumps(first,indent=2)+
      f"\nCompared prefix {min(len(a['frames']),len(b['frames']))}frames; equal frame counts: {len(a['frames'])==len(b['frames'])}; full captured PCM byte-equal: {pcm}.\n\n"
      'The accepted616byte native selector kernel is unchanged local27B output after one coordinator-guided repair, outer fence removed. The first draft failed compilation; the coordinator supplied additional source findings. Same-weight Reviewers missed those defects. Layout/ABI/contract/verifiers/integration are coordinator work, and the model used scalar volatile-width helpers instead of the requested struct fields. These supported development checks do not demonstrate training gain or independent review.\n\n'
      'Both routes use retained native emulator processors/platform services. New exact-disc C-provider comparison is separate. No whole-machine/cycle/physical-console or full-game rebuild proof; older compiled-scanner/original-scanner-entry timing/video/audio differences remain inherited limits. Default preview is unchanged.\n\n'
      'Exact model work: '+dev['transcript']+'\nComponent/build evidence: '+dev['report']+'\n')
    bind(report)
    result=dict(status='terminal_native_interior_two_live_routes_reviewed',recorded_at=now.isoformat(),directory=str(out),report=str(report),
                build=str(bp),build_sha256=sha(bp),candidate_frames=len(a['frames']),control_frames=len(b['frames']),
                compared_prefix_frames=min(len(a['frames']),len(b['frames'])),frame_counts_equal=len(a['frames'])==len(b['frames']),
                same_layout_differences=differences,first_differing_frames=first,PCM_equal=pcm,candidate_observations=obs,
                control_observations=original,live_monitor_pass=True,processors='Retained native emulator processors/platform services',
                derived_disc=build['derived_disc'],derived_disc_sha256=build['derived_disc_sha256'],resident_bytes=18888,native_bytes=616,
                stable_cases=1958,changing_cases=768,accepted_local_body_edited=False,dependencies_sha256=deps,pointer_snapshots=aliases,
                new_training=False,native_Chat_verified=False,default_promoted=False,whole_game_complete=False,physical_console_verified=False)
    save(out/'protocol.json',result);save(v/'native-interior-live-reviewed-current.json',result)
    print(json.dumps({k:result[k]for k in ['status','candidate_frames','control_frames','same_layout_differences','PCM_equal','report']}))


if __name__=='__main__':main()
