"""Review complete102C4 scanner gameplay against its original-entry control."""
import hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def read(p):return json.loads(Path(p).read_text())
def main():
    v=ROOT/'verification';cp=v/'native-geometry-scan-candidate-current.json';np=v/'native-geometry-scan-control-current.json';candidate,control=read(cp),read(np)
    for d in [candidate,control]:
        assert d['status']=='terminal_native_geometry_scan_route_pending_review' and d['exit_code']==0
        assert d['returned_outdoors'] and d['live_monitor_pass'] and d['scan_monitor_pass']
        obs=d['observations'];assert obs['scan_errors']==obs['scan_pending']==obs['scan_stack_outside']==obs['errors']==obs['copy_errors']==0
        assert d['geometry_monitor_pass'] and d['select_monitor_pass']
    bp=v/'native-geometry-scan-disc-build-current.json';build=read(bp);devp=v/'native-geometry-scan-development-reviewed-current.json';dev=read(devp);mp=v/'native-geometry-scan-monitor-current.json';monitor=read(mp)
    assert build['linked_component_bytes']==dev['resident_bytes']==17812 and dev['native_bytes']==428
    assert dev['stable_cases']==1377 and dev['changing_cases']==768 and monitor['original_cases']==monitor['compiled_cases']==1377
    cfolder=Path(candidate['directory'])/'candidate';nfolder=Path(control['directory'])/'candidate';a=read(cfolder/'report.json');b=read(nfolder/'report.json')
    assert a['disc_sha256']==build['derived_disc_sha256']==dev['derived_disc_sha256']
    assert sha(cfolder/'report.json')==candidate['report_sha256'] and sha(nfolder/'report.json')==control['report_sha256']
    assert control['control_delta']['restored_entries']==['102C4'] and control['control_delta']['declared_bytes']==8
    assert a['disc_sha256']==control['control_delta']['source_sha256'] and b['disc_sha256']==control['control_delta']['control_sha256']
    fields=['CPU_full','full_RAM_sha256','full_GPU_state_sha256','full_DSP_state_sha256','video_sha256','navigation','locomotion_state','held_buttons'];differences={k:0 for k in fields};first={}
    assert len(a['frames'])>24000 and len(b['frames'])>24000
    for x,y in zip(a['frames'],b['frames']):
        assert x['frame']==y['frame']
        for k in fields:
            if x[k]!=y[k]:differences[k]+=1;first.setdefault(k,x['frame'])
    pcm=sha(cfolder/'frontend-PCM.s16le')==sha(nfolder/'frontend-PCM.s16le');obs=candidate['observations'];original=control['observations']
    assert obs['scan_entries']==obs['scan_native_entries']==obs['scan_returns'] and obs['scan_entries']>0 and obs['scan_old_steps']==0
    assert original['scan_entries']==original['scan_returns'] and original['scan_native_entries']==0 and original['scan_old_steps']>0
    now=datetime.now(timezone.utc);out=v/'native-geometry-scan-live-reviewed'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();deps={};aliases={}
    def bind(path,expected=None):
        p=Path(path).resolve();assert p.is_relative_to(ROOT);h=sha(p);assert expected is None or h==expected,str(p);target=p
        if p.name.endswith(('-current.json','-active.json')):
            target=snap/(hashlib.sha256(str(p).encode()).hexdigest()[:12]+'-'+p.name);shutil.copy2(p,target);aliases[str(p)]=str(target)
        deps[str(target)]=h
    for p in [cp,np,bp,devp,mp]:bind(p)
    for d in [candidate,control]:
        for p,h in d['source_sha256'].items():bind(p,h)
        folder=Path(d['directory']);bind(folder/'protocol.json')
        for name in ['report.json','gameplay-observation.json','frontend-PCM.s16le']:bind(folder/'candidate'/name)
    for d in [dev,monitor]:
        for p,h in d.get('dependencies_sha256',d.get('source_sha256',{})).items():bind(p,h)
    bind(Path(__file__))
    report=ROOT/'reports/native-geometry-scan-live.txt';report.write_text('BIWN — COMPLETE102C4 SCANNER GAMEPLAY COMPARISON\n'+now.isoformat()+'\n\n'
      f"The17812byte resident disc and its same-layout original-scanner-entry control completed {len(a['frames'])} candidate and {len(b['frames'])} control frames and returned outdoors. Only the102C4eight-byte entry was restored in the control; preceding1028Eand1039Cnative routines remain compiled in both. The scanner candidate executed {obs['scan_entries']} compiled calls: {obs['scan_successes']} success returns, {obs['scan_failures']} failure returns, including {obs['scan_skips']} skips. It inspected {obs['scan_iterations']} records. The control executed {original['scan_entries']} original calls: {original['scan_successes']} successes and {original['scan_failures']} failures.\n\n"
      f"Both live scanner contracts passed full register/SR/USP/SSP outputs, six object fields, return/argument bytes and task-stack observations with zero reported errors/pending/outside. Candidate private depth {obs['scan_max_depth']}bytes, minimum observed task headroom {obs['scan_min_headroom']}bytes. The stable-entry oracle was first qualified against1377original and1377final-address compiled component cases. Live data stability is an assumption tested by return agreement; separately controlled changing-read fixtures cover768cases. Unreached live return paths remain component-only.\n\n"
      'Differences between aligned recorded frames:\n'+json.dumps(differences,indent=2)+'\nFirst differing frames:\n'+json.dumps(first,indent=2)+f'\nCompared aligned prefix: {min(len(a["frames"]),len(b["frames"]))}frames; frame counts equal: {len(a["frames"])==len(b["frames"])}. Full captured PCM streams equal: {pcm}.\n\n'
      'These differences are retained as limits; passing the function contract does not establish cycle or whole-machine equivalence. RAM hashes do not identify all changed addresses. Both runs retain emulator CPU/GPU/DSP/IRQ and platform services. Preceding-disc C-instruction-provider comparisons do not verify this new disc. This428byte scanner, ABI, layout/bounds helper, observer and integration are coordinator work after all three local candidates failed. Five actual local predictions and exact prompts/raw outputs are recorded separately. No weights changed; native Chat display, physical-console boot, complete source rebuild and default preview promotion are not established.\n\n'
      'Exact local model work:\n'+str(ROOT/'reports/native-geometry-scan-prompts-and-responses.txt')+'\nDevelopment/component evidence:\n'+dev['report']+'\n')
    bind(report)
    result=dict(status='terminal_native_geometry_scan_two_live_routes_reviewed',recorded_at=now.isoformat(),directory=str(out),report=str(report),build=str(bp),build_sha256=sha(bp),candidate_frames=len(a['frames']),control_frames=len(b['frames']),compared_prefix_frames=min(len(a['frames']),len(b['frames'])),frame_counts_equal=len(a['frames'])==len(b['frames']),same_layout_differences=differences,first_differing_frames=first,PCM_equal=pcm,candidate_observations=obs,control_observations=original,live_monitor_pass=True,processors='Retained native emulator processors/platform services',derived_disc=build['derived_disc'],derived_disc_sha256=build['derived_disc_sha256'],resident_bytes=17812,native_bytes=428,stable_cases=1377,changing_cases=768,dependencies_sha256=deps,pointer_snapshots=aliases,new_training=False,native_Chat_verified=False,default_promoted=False,whole_game_complete=False,physical_console_verified=False)
    save(out/'protocol.json',result);save(v/'native-geometry-scan-live-reviewed-current.json',result);print(json.dumps({k:result[k]for k in ['status','same_layout_differences','PCM_equal','report']}))
if __name__=='__main__':main()
