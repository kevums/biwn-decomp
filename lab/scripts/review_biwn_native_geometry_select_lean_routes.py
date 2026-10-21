"""Review fresh selector/native-control gameplay without assuming cycle equality."""
import hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
def read(p):return json.loads(Path(p).read_text())
def main():
    v=ROOT/'verification';cp=v/'native-geometry-select-lean-candidate-current.json';np=v/'native-geometry-select-lean-control-current.json';candidate,control=read(cp),read(np)
    for d in [candidate,control]:
        assert d['status']=='terminal_native_frame_acquire_route_pending_review' and d['exit_code']==0
        assert d['returned_outdoors'] and d['live_monitor_pass'] and d['select_monitor_pass']
        assert d['observations']['select_errors']==d['observations']['select_pending']==d['observations']['select_stack_outside']==0
    bpath=v/'native-geometry-select-lean-disc-build-current.json';build=read(bpath);componentp=v/'native-geometry-select-lean-reviewed-current.json';component=read(componentp)
    assert component['stable_cases']==1280 and component['changing_cases']==512 and component['native_bytes']==298
    cfolder=Path(candidate['directory'])/'candidate';nfolder=Path(control['directory'])/'candidate';a=read(cfolder/'report.json');b=read(nfolder/'report.json')
    assert a['disc_sha256']==build['derived_disc_sha256']==component['derived_disc_sha256']
    assert sha(cfolder/'report.json')==candidate['report_sha256'] and sha(nfolder/'report.json')==control['report_sha256']
    assert control['control_delta']['restored_entries']==['1039C'] and control['control_delta']['declared_bytes']==8
    fields=['CPU_full','full_RAM_sha256','full_GPU_state_sha256','full_DSP_state_sha256','video_sha256','navigation','locomotion_state','held_buttons']
    differences={k:0 for k in fields};CPUframes=[]
    for x,y in zip(a['frames'],b['frames']):
        assert x['frame']==y['frame']
        for k in fields:differences[k]+=x[k]!=y[k]
        if x['CPU_full']!=y['CPU_full']:CPUframes.append(dict(frame=x['frame'],candidate=x['CPU_full'],control=y['CPU_full']))
    PCM=sha(cfolder/'frontend-PCM.s16le')==sha(nfolder/'frontend-PCM.s16le')
    obs=candidate['observations'];original=control['observations']
    assert obs['select_entries']==obs['select_native_entries']==obs['select_returns'] and obs['select_entries']>0 and obs['select_old_steps']==0
    assert original['select_entries']==original['select_returns'] and original['select_native_entries']==0 and original['select_old_steps']>0
    now=datetime.now(timezone.utc);out=v/'native-geometry-select-lean-live-reviewed'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();deps={};aliases={}
    def bind(path,expected=None):
        path=Path(path).resolve();assert path.is_relative_to(ROOT);digest=sha(path);assert expected is None or expected==digest,str(path);target=path
        if path.name.endswith(('-current.json','-active.json')):
            target=snap/(hashlib.sha256(str(path).encode()).hexdigest()[:12]+'-'+path.name);shutil.copy2(path,target);aliases[str(path)]=str(target)
        deps[str(target)]=digest
    for p in [cp,np,bpath,componentp]:bind(p)
    for d in [candidate,control]:
        for p,h in d['source_sha256'].items():bind(p,h)
        folder=Path(d['directory']);bind(folder/'protocol.json')
        for name in ['report.json','gameplay-observation.json','frontend-PCM.s16le']:bind(folder/'candidate'/name)
    for p,h in component['dependencies_sha256'].items():bind(p,h)
    bind(Path(__file__))
    bind(ROOT/'reports/native-geometry-select-prediction-index.json')
    # This diagnostic records reported differences only; no per-address intermediate RAM claim.
    save(out/'CPU-different-frames.json',CPUframes);bind(out/'CPU-different-frames.json')
    report=ROOT/'reports/native-geometry-select-lean-live.txt'
    report.write_text('BIWN — NATIVE INDEXED SELECTOR GAMEPLAY COMPARISON\n'+now.isoformat()+'\n\n'
        f"The 17,382-byte native selector disc completed {len(a['frames']):,} frames; the same-layout control restoring only the eight-byte original1039Centry completed {len(b['frames']):,}. Both returned outdoors through the merchant/media route with live ABI/object-write/task-stack checks passing. The candidate executed the compiled selector {obs['select_native_entries']} times: {obs['select_successes']} success paths and {obs['select_failures']} failure paths. The control executed {original['select_entries']} original calls. Unreached return paths remain component-test coverage.\n\n"
        f"Candidate private selector depth was {obs['select_max_depth']} bytes; minimum observed headroom was {obs['select_min_headroom']} bytes. Reported selector/register/SR/bank/object-write errors, pending calls and stack-outside observations are zero. The live oracle samples entry RAM and assumes stability during each call; changing-read behavior was separately tested by component fixtures.\n\n"
        'Per-field differences over aligned recorded frames:\n'+json.dumps(differences,indent=2)+'\n'
        f"Full PCM streams equal: {PCM}. Frame-count equality: {len(a['frames'])==len(b['frames'])}. Per-frame differences are measured, not waived; no claim of whole-state or cycle equivalence is made. RAM observations are hashes, not classification of all changed addresses.\n\n"
        'The corrected observer applies the24bit guest bus mask before guarded RAM reads, retaining all full-register/pointer checks. Tagged-pointer component coverage passed1280stable+512changing cases on the selected298byte source/binary. The original failed monitor receipts remain rejected. Both gameplay runs retain emulator CPU/GPU/DSP/IRQ and platform services. C-processor results for preceding cache/boundary discs do not apply to this new selector disc. The accepted selector C, ABI, verification and integration are coordinator work after two rejected local Author drafts and unreliable same-weight reviews. No new weights, independent model review, whole-game source rebuild, physical-console readiness or default preview promotion is established.\n\n'
        'Exact local prompts/raw outputs:\n'+str(ROOT/'reports/native-geometry-select-prompts-and-responses.txt')+'\nComponent/final-address evidence:\n'+component['report']+'\n')
    bind(report)
    result=dict(status='terminal_native_geometry_select_two_live_routes_reviewed',recorded_at=now.isoformat(),directory=str(out),report=str(report),build=str(bpath),build_sha256=sha(bpath),candidate_frames=len(a['frames']),control_frames=len(b['frames']),compared_prefix_frames=min(len(a['frames']),len(b['frames'])),same_layout_differences=differences,PCM_equal=PCM,candidate_observations=obs,control_observations=original,live_monitor_pass=True,processors='Retained native emulator processors and platform services',derived_disc=build['derived_disc'],derived_disc_sha256=build['derived_disc_sha256'],dependencies_sha256=deps,pointer_snapshots=aliases,new_training=False,native_Chat_verified=False,default_promoted=False,whole_game_complete=False,physical_console_verified=False)
    save(out/'protocol.json',result);save(v/'native-geometry-select-lean-live-reviewed-current.json',result);print(json.dumps({k:result[k]for k in ['status','candidate_frames','control_frames','same_layout_differences','PCM_equal','report']}),flush=True)
if __name__=='__main__':main()
