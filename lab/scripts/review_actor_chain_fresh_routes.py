"""Review the fresh shared C-chain route and same-layout original-root control.
Finite component proofs establish algorithm equivalence; the live observer checks
reached boundaries, body ownership and task/context integrity. Native emulated
processors and HLE remain. Adaptive inputs and timing/media differences limit the
comparison. Indoor collision remains component-only. No physical console claim.
"""
import json, hashlib, shutil, subprocess
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def main():
    out=V/'actor-chain-fresh-route-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();deps={}
    def bind(p,h=None):
        p=Path(p).resolve();actual=sha(p);assert h is None or h==actual,str(p)
        if p.name.endswith(('-current.json','-active.json')):
            dest=snap/(hashlib.sha256(str(p).encode()).hexdigest()[:12]+'-'+p.name);shutil.copy2(p,dest);p=dest
        assert str(p)not in deps or deps[str(p)]==actual,str(p);deps[str(p)]=actual
        return str(p)
    development=read(V/'actor-chain-development-reviewed-current.json');bind(V/'actor-chain-development-reviewed-current.json')
    for p,h in development['dependencies_sha256'].items():bind(p,h)
    build=read(V/'native-actor-chain-build-normalized-current.json');bind(V/'native-actor-chain-build-normalized-current.json')
    assert build['linked_component_bytes']==28448 and build['free_reserved_bytes']==96
    observer=read(V/'actor-chain-live-observer-current.json');bind(V/'actor-chain-live-observer-current.json')
    assert observer['completed']==550 and observer['cases']==275 and len(observer['negative_controls'])==5
    assert all(x['rejected']and not x['native_CPU_or_RAM_changed']for x in observer['negative_controls'])
    for p,h in observer['source_sha256'].items():bind(p,h)
    jobs={};reports={}
    for label in ['candidate','control']:
        pointer=V/('native-actor-chain-'+label+'-current.json');job=read(pointer);bind(pointer)
        assert job['status']=='terminal_native_actor_chain_route_pending_review'and job['exit_code']==0
        assert job['returned_outdoors']and job['live_monitor_pass']and job['actor_chain_monitor_pass']
        assert subprocess.run(['ps','-p',str(job['child_pid']),'-o','command='],capture_output=True).returncode!=0
        for p,h in job['source_sha256'].items():bind(p,h)
        folder=Path(job['directory'])/'candidate';report=read(folder/'report.json')
        for name in ['report.json','gameplay-observation.json','frontend-PCM.s16le','original-emulator-final-frame.png']:bind(folder/name)
        assert sha(folder/'report.json')==job['report_sha256']
        assert report['disc_sha256']==(build['derived_disc_sha256']if label=='candidate'else job['control_delta']['control_sha256'])
        assert not report['captured_state_input']and not report['host_CPU_or_GPU_register_seed']and report['C_CPU_backend']['mode']=='reference'
        assert job['checkpoint_restores']==0 and job['host_guest_RAM_writes']==0
        a=job['observations'];assert a['ach_entries']==a['ach_returns']and a['ach_virtual_entries']==a['ach_virtual_returns']
        assert all(a[k]==0 for k in ['ach_pending','ach_errors','ach_context_errors','ach_virtual_errors','ach_stack_outside'])
        if label=='candidate':
            assert a['ach_native']==a['ach_entries']and a['ach_old_steps']==[0,0,0]
            assert a['ach_entries']==[13806,0,0]and a['ach_virtual_entries']==[3883,0]
            assert a['ach_helper_counts'][:2]==[13806,13806]and sum(a['ach_helper_counts'])==a['ach_context_checks']==31495
            assert a['ach_max_depth'][0]==564 and a['ach_min_headroom'][0]==370 and a['ach_source_steps']>0
        else:
            assert a['ach_native']==[0,0,0]and a['ach_entries']==[16689,4750,0]and sum(a['ach_old_steps'])>0
            delta=job['control_delta'];assert delta['restored_entries']==['13c9a','13b5a','13bb0']and delta['declared_bytes']==delta['actual_changed_bytes']==22
        assert job['interior_kind_entries']==[14,1]and job['interior_kind_successes']==[14,0]and job['interior_kind_failures']==[0,1]
        jobs[label]=job;reports[label]=report
    keys=['CPU_full','full_RAM_sha256','full_GPU_state_sha256','full_DSP_state_sha256','video_sha256','navigation','locomotion_state','held_buttons']
    differences={k:sum(a[k]!=b[k]for a,b in zip(reports['candidate']['frames'],reports['control']['frames']))for k in keys}
    pcm={label:dict(bytes=(p:=Path(job['directory'])/'candidate/frontend-PCM.s16le').stat().st_size,sha256=sha(p))for label,job in jobs.items()}
    comparison=dict(candidate_frames=len(reports['candidate']['frames']),control_frames=len(reports['control']['frames']),aligned_frames=min(len(r['frames'])for r in reports.values()),differing_frames=differences,PCM=pcm,PCM_equal=pcm['candidate']==pcm['control'],adaptive_controller_paths_may_differ=True,whole_state_equivalent=False,timing_differences_unresolved=True)
    save(out/'comparison.json',comparison);bind(out/'comparison.json')
    image=Path(jobs['candidate']['directory'])/'candidate/original-emulator-final-frame.png'
    text='''BIWN SHARED C-CHAIN — REVIEWED FRESH GAMEPLAY

The 28,448-byte native C rebuild completed 29,808 frames and returned outdoors;
the fresh same-layout original-root control completed 29,804 and returned outdoors.
The candidate completed 13,806 movement calls and 3,883 internal outdoor collision
calls. Indoor collision reached zero times in both runs. The control completed
16,689 original movement and 4,750 original outdoor collision calls. Different
instruction cost, scheduling and adaptive inputs prevent a speedup/equality claim.

The candidate executes movement/collision via shared source-owned C ABI. Its
31,495 physical helper-context checks, 3,883 shadow-CPU virtual collision checks,
body ownership, public returns and task boundaries report no errors. Maximum
observed movement-chain private depth564, minimum live task headroom370; the
separate tighter fixture minimum is354. Virtual C entry checks are shadow CPU
comparisons, not equality with physical C-ABI registers. No universal interrupt,
concurrency, invalid-table-target or recursion bounds follow from these runs.

The exact new live observer passes550 original/C executions across275 stratified
cases and rejects5 decoded-observation corruptions. Algorithm evidence remains
separate:7,680 prototype+7,680 final cases/all301 sites,15,360 context executions,
96 full-payload startup cases. The live observer does not replace those proofs.

Control restores all3 original public roots13C9A/13B5A/13BB0 (22 bytes); prior
compiled functions, heap/reservation/staging and unused installed chain code
remain common. This control is not an unmodified-disc baseline. Retained native
emulator CPU/GPU/DSP/IRQ/platform and HLE execute both runs. Historical processor
replacement receipts do not apply to this new disc. No full readable game,
physical-console boot, complete media/timing equality or release readiness.

Selector outcomes:14 actor successes;1 skipped sprite failure. Dispatcher routes
12 actors/1 sprite are separate counts. Actual final image was visually inspected:
character stands outdoors with HUD/inventory visible. No UI keyboard test implied.

Fresh-pair comparison (not comparison to the historical external-DSP reference):
'''+json.dumps(comparison,indent=2)+'\n\nImage: '+str(image)+'\n'
    report=out/'review.txt';report.write_text(text);bind(report);bind(Path(__file__))
    result=dict(status='terminal_shared_C_chain_fresh_routes_reviewed',directory=str(out),report=str(report),resident_bytes=28448,candidate_frames=29808,control_frames=29804,movement_calls=[13806,16689],outdoor_calls=[3883,4750],indoor_calls=[0,0],physical_context_checks=31495,max_private_depth=564,minimum_live_headroom=370,minimum_fixture_headroom=354,live_monitor_pass=True,comparison=comparison,image=str(image),default_preview_promoted=False,whole_game_complete=False,physical_console_verified=False,new_training=False,new_local_code_adopted=False,dependencies_sha256=deps,scope=__doc__)
    save(out/'protocol.json',result);save(V/'actor-chain-integration-reviewed-current.json',result)
    print(json.dumps({k:result[k]for k in ['status','candidate_frames','control_frames','comparison']}))
if __name__=='__main__':main()
