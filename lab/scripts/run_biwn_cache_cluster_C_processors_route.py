"""Exact cache disc: strict C processors versus its fresh native route.

Reuses the declared retained-native reference; never patches RAM or restores
a checkpoint. Source instruction execution remains distinct from recovered
readable game algorithms and from a standalone physical-console rebuild.
"""
import json, os, subprocess
from pathlib import Path
from datetime import datetime, timezone
from run_biwn_native_fast_gameplay_route import ROOT, sha, save


def read(p):
    return json.loads(Path(p).read_text())


def main():
    rp = ROOT/'verification/native-cache-cluster-route-current.json'
    native = read(rp)
    assert native['status']=='terminal_native_frame_acquire_route_pending_review'
    assert native['returned_outdoors'] and native['live_monitor_pass']
    buildp = ROOT/'verification/cache-cluster-C-runtime-build-current.json'
    build = read(buildp)
    assert build['status']=='terminal_cache_cluster_C_compiled_pending_checks'
    gatep = ROOT/'verification/cache-cluster-CPU-semantics-current.json'
    gate = read(gatep)
    assert gate['status']=='terminal_cache_cluster_CPU_semantics_native_and_cost_pass'
    cp = Path(build['CPU_candidate'])
    assert gate['CPU_candidate']==str(cp)
    for path,digest in gate['source_sha256'].items():
        assert sha(path)==digest,path
    nativep = Path(build['directory'])/'native-CPU-candidate.json'
    native_cpu = read(nativep)
    template = Path(native['directory'])/'probe.py'
    assert sha(template)==native['source_sha256'][str(template)]
    old_observer = Path(native['directory'])/'frame-acquire-observer.c'
    assert sha(old_observer)==native['source_sha256'][str(old_observer)]
    reference = Path(native['directory'])/'candidate'
    control = read(reference/'report.json')
    assert sha(reference/'report.json')==native['report_sha256']
    out = ROOT/'verification/cache-cluster-C-processors-route'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    (out/'runner-as-run.py').write_bytes(Path(__file__).read_bytes())
    print(out,flush=True)
    text = old_observer.read_text()
    marker='if(result)errors++;return result;'
    assert text.count(marker)==1
    text=text.replace(marker,'if(result<0)errors++;return result;')
    observer=out/'cache-observer.c'
    observer.write_text(text)
    library=out/'libcache-observer.dylib'
    compiled=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(observer),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'})
    (out/'observer-build.log').write_text(compiled.stdout+compiled.stderr)
    assert compiled.returncode==0,compiled.stderr
    text=template.read_text()
    oldp=read(ROOT/'verification/bootstrap-CPU-build-current.json')['native_CPU_candidate']
    assert text.count(repr(oldp))==1
    text=text.replace(repr(oldp),repr(str(nativep)))
    old_library=str(Path(native['directory'])/'libframe-acquire-observer.dylib')
    assert text.count(repr(old_library))==1
    text=text.replace(repr(old_library),repr(str(library)))
    marker="        assert args.CPU_mode=='reference'"
    assert text.count(marker)==1
    text=text.replace(marker,"        assert args.CPU_mode=='C'")
    marker='core.BIWNSetCPUExecOwner(watch_owner,0)'
    assert text.count(marker)==1
    text=text.replace(marker,'core.BIWNSetCPUExecOwner(watch_owner,1)')
    lines=[line for line in text.splitlines() if "report['C_CPU_backend']['scope']=" in line]
    assert len(lines)==1
    text=text.replace(lines[0],"        report['C_CPU_backend']['scope']='Strict source C CPU from HLE-prepared initialPC,source GPU/DSP/IRQ selection andentry. Exact cacheclusterdisc;read-only ABI/cache observer chains C owner. PlatformHLE/devices/IRQlines+ACK/vector/hostcommit/prefetch/cost/clock/blitter/OP retained. New compiled game C is executed as68000instructions bythe fixed C provider,not replaced with host high-level calls.'")
    probe=out/'probe.py'
    compile(text,str(probe),'exec')
    probe.write_text(text)
    command=list(native['command'])
    command[2]=str(probe)
    command[command.index('--CPU-mode')+1]='C'
    command[command.index('--output')+1]=str(out/'C')
    assert sha(Path(command[command.index('--disc')+1]))==control['disc_sha256']
    assert sha(Path(command[command.index('--core')+1]))==control['core_sha256']==native_cpu['required_core_sha256']
    paths=[out/'runner-as-run.py',rp,buildp,gatep,cp,Path(read(cp)['library']),nativep,Path(native_cpu['library']),
           template,old_observer,observer,library,probe,reference/'report.json',reference/'frontend-PCM.s16le']
    state=dict(status='running_fresh_cache_cluster_strict_C_processors_route',pid=os.getpid(),directory=str(out),
               command=command,reference=str(reference),reference_reused=True,reference_proof=str(rp),
               reference_proof_sha256=sha(rp),CPU_candidate=str(cp),native_CPU_candidate=str(nativep),
               source_sha256={str(p):sha(p) for p in paths},new_training=False,default_promoted=False,
               whole_game_complete=False,checkpoint_restores=0,host_guest_RAM_writes=0,
               scope='Exact new cacheclusterdisc versus its fresh retained-native route. Strict C CPU from HLEpreparedentry plus C GPU/DSP/IRQ selection/entry. Original platformHLE/device/IRQlines+ACK/vector/hostcommit/prefetch/cost/clock/blitter/OP retained. Staticinstruction translation isnotnew readable game-function recovery orstandalone hardwareproof. No nativeChat orweighttraining claim.')
    def mark():
        save(out/'protocol.json',state)
        save(ROOT/'verification/cache-cluster-C-processors-route-active.json',state)
    mark()
    try:
        with (out/'C.log').open('w') as log:
            child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
            state['child_pid']=child.pid;mark();code=child.wait()
        state['exit_code']=code
        if code:
            state.update(status='terminal_cache_cluster_C_processors_rejected',child_status=read(out/'C/status.json') if (out/'C/status.json').exists() else None)
            mark();save(ROOT/'verification/cache-cluster-C-processors-route-current.json',state)
            print(state['status'],flush=True)
            return
        report=read(out/'C/report.json')
        fields=['CPU_full','full_RAM_sha256','full_GPU_state_sha256','full_DSP_state_sha256','video_sha256','navigation','locomotion_state','held_buttons']
        differences={key:sum(a[key]!=b[key] for a,b in zip(report['frames'],control['frames'])) for key in fields}
        CPU=report['C_CPU_backend'];backends=report['C_processor_backends'];DSP=backends['DSP']
        assert CPU['entry_gate']['original_before_owner_install']==0
        assert CPU['counts']['Original']==CPU['counts']['Rejected']==CPU['stats']['errors']==0
        assert backends['GPU']['counts']['Original']==backends['GPU']['counts']['Rejected']==backends['GPU']['stats']['errors']==0
        assert DSP['errors']==DSP['uncovered']==DSP['core_counts']['Original']==DSP['core_counts']['Rejected']==0
        assert all(backends['IRQ'][kind][key]==0 for kind in ['core','selection'] for key in ['Original','Rejected'])
        PCM_equal=sha(out/'C/frontend-PCM.s16le')==sha(reference/'frontend-PCM.s16le')
        observations=read(out/'C/gameplay-observation.json')
        assert observations==native['observations'],'Observer counters differ despite identical instruction execution'
        final=report['frames'][-1]
        returned=final['player_mode_word']==1 and final['floor_word']==0 and final['navigation']['outdoor_hold']>=120
        equal=len(report['frames'])==len(control['frames']) and not any(differences.values()) and PCM_equal and returned
        state.update(status='terminal_cache_cluster_C_processors_route_equal' if equal else 'terminal_cache_cluster_C_processors_route_diverged',
                     frames=len(report['frames']),reference_frames=len(control['frames']),comparisons=differences,PCM_equal=PCM_equal,
                     returned_outdoors=returned,nonzero_audio_samples=report['audio']['nonzero_samples'],C_CPU_backend=CPU,
                     C_processor_backends=backends,observations=observations,report_sha256=sha(out/'C/report.json'))
        mark();save(ROOT/'verification/cache-cluster-C-processors-route-current.json',state)
        print(json.dumps({key:state[key] for key in ['status','frames','comparisons','PCM_equal','returned_outdoors']}),flush=True)
    except BaseException as error:
        state.update(status='terminal_cache_cluster_C_processors_driver_failed',error=repr(error));mark();raise


if __name__=='__main__':
    main()
