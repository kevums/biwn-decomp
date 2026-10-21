"""Baseline-verify a streaming observer, then try longer original-game inputs."""
import argparse
import csv
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import time
from observe_biwn_processor_state import ROOT,digest


def save(path,value):path.write_text(json.dumps(value,indent=2)+'\n')
def rows(path):
    with path.open() as stream:return list(csv.DictReader(stream))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--frames',type=int,default=9000);args=parser.parse_args()
    if args.frames<9000 or args.frames>18000:raise ValueError('Use9000..18000frames')
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    core=ROOT/'tools/virtualjaguar-runtime-source/virtualjaguar_libretro.dylib'
    image=ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi'
    bios=ROOT/'projects/black-ice-white-noise/reference-bios/jaguar-cd-user-provided.bin'
    binary=ROOT/'tools/biwn-audio-streaming-probe'
    original_observer=ROOT/'scripts/biwn_audio_command_probe.c'
    hashes={str(p):digest(p)for p in [core,image,bios,binary,original_observer]}
    assert hashes[str(core)]=='c2990c86f54473b55a68ee2493c50b6e584e4ac81a46bfb7e593611133e8e856'
    assert hashes[str(image)]=='0aaef12221309e3266861ebe5da0c14f419de49aac7eb727302e0f5983ec532f'
    out=session/'emulator-runtime'/('long-audio-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
    inputs=out/'inputs';inputs.mkdir(parents=True)
    (inputs/image.name).symlink_to(image);(inputs/'jaguarcd_bios.bin').symlink_to(bios)
    events=['690:up:1800','2490:left:360','2850:up:1800','4650:right:360','5010:up:1800','6810:down:600',
            '7500:a:30','7600:b:30','7700:c:30','7800:option:30','7900:pause:30','8000:pause:30',
            *[f'{8100+i*100}:{i}:30'for i in range(7)]]
    protocol={'scope':'Original preserved game in assisted-BIOS emulator, repeating one GPU bank0R31 assignment after437. New observer drains ring everyframe; no DSP/core changes.900frame preflight must exactly match previous baseline before two longer runs.',
              'frames':args.frames,'inputs':events,'wall_budget_seconds_per_run':180,'ring_capacity':4194304,
              'observer_source':str(ROOT/'scripts/biwn_audio_streaming_probe.c'),'observer_source_sha256':digest(ROOT/'scripts/biwn_audio_streaming_probe.c'),'input_hashes':hashes,
              'limits':['Chosen supplied buttons are not proof of game receipt, valid gameplay or sound triggering.','Latest1024DSP/CPU PCs are sampled, not a complete execution trace; postframe RAM can miss transient changes.',
                        'No hardware, rebuilt-game, listening-quality or no-assets conclusion. Core code unchanged; assisted boot remains an experiment.','Existing watch facility cannot observe DSP/GPU direct local-RAM self-writes.']}
    save(out/'protocol.json',protocol)
    prior=Path(json.loads((session/'emulator-runtime/audio-commands-current.json').read_text())['directory'])/'baseline'
    runs=[];frames={};commands={}
    for name,count,buttons in [('preflight900',900,[]),('long-baseline',args.frames,[]),('long-input',args.frames,events)]:
        directory=out/name;directory.mkdir()
        cmd=[str(binary),str(core),str(inputs/image.name),'--frames',str(count),'--bios','--system-dir',str(inputs),
             '--option','virtualjaguar_cd_boot_mode=bios','--option','virtualjaguar_usefastblitter=enabled','--option','virtualjaguar_crash_detect=enabled']
        for event in buttons:cmd+=['--press',event]
        env=os.environ.copy();env.update(BIWN_EXPERIMENT_GPU_STACK='F03FF0',VJ_EXPECT_BUILD='unknown',VJ_HARNESS_LOG_INFO='1',VJ_TRACE_RING='4194304')
        state={'name':name,'frames':count,'command':cmd,'status':'starting','events':buttons};save(directory/'status.json',state)
        started=time.monotonic()
        with (directory/'run.log').open('w') as log:
            process=subprocess.Popen(cmd,cwd=directory,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            state.update(status='running',pid=process.pid);save(directory/'status.json',state);print(name,process.pid,'running',flush=True)
            try:process.wait(timeout=180)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid,signal.SIGTERM)
                try:process.wait(timeout=5)
                except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
                state['wall_budget_expired']=True
        state.update(status='terminal',exit_code=process.returncode,seconds=round(time.monotonic()-started,3));save(directory/'status.json',state)
        if process.returncode:raise RuntimeError('Observer failed; preserve logs: '+str(directory))
        f=rows(directory/'audio-path-frames.csv');c=rows(directory/'audio-command-frames.csv');w=rows(directory/'audio-watch-events.csv')
        assert len(f)==len(c)==count
        assert (directory/'dsp-frames.bin').stat().st_size==count*8192
        end=re.search(r'AUDIO_STREAM frames=(\d+) ring=(\d+) unreadable=(\d+) watched=(\d+) initialization_count=(\d+) max_frame_events=(\d+) CPU_pcs=(\d+)',(directory/'run.log').read_text())
        assert end and int(end[1])==count and int(end[3])==0 and int(end[5])==1 and int(end[6])<4194304
        if name=='preflight900':
            assert f==rows(prior/'audio-path-frames.csv') and c==rows(prior/'audio-command-frames.csv')
            assert (directory/'dsp-frames.bin').read_bytes()==(prior/'dsp-frames.bin').read_bytes()
            assert w==rows(prior/'audio-watch-events.csv')
        elif name=='long-baseline':
            assert f[:900]==frames['preflight900'] and c[:900]==commands['preflight900']
        else:
            assert f[:689]==frames['long-baseline'][:689] and c[:689]==commands['long-baseline'][:689]
        changed=[int(row['frame'])for row in c[621:]if any(row[key]!=c[621][key]for key in row if key!='frame')]
        active_audio=[int(row['frame'])for row in f[621:]if int(row['i2s_nonzero_capture_count'])]
        post_audio_delta=int(f[-1]['audio_nonsilent_total'])-int(f[620]['audio_nonsilent_total'])
        state.update(directory=str(directory),ring_events=int(end[2]),ring_unreadable=0,watched_records=len(w),max_frame_events=int(end[6]),CPU_distinct_sampled_PCs=int(end[7]),
                     game_phase_watch_records=[e for e in w if int(e['frame'])>=622],command_state_changed_frames=changed,
                     post621_nonzero_capture_frames=active_audio,post621_nonsilent_audio_pairs_delta=post_audio_delta,
                     final_frame=f[-1],final_command_state=c[-1],
                     artifact_sha256={p.name:digest(p)for p in directory.iterdir()if p.is_file() and p.name!='status.json'})
        save(directory/'status.json',state);runs.append(state);frames[name]=f;commands[name]=c
        print(name,'terminal',state['seconds'],'sec;',len(changed),'command changes;',len(active_audio),'nonzero capture frames;',int(end[7]),'sampledCPU PCs',flush=True)
    diffs={key:[int(a['frame'])for a,b in zip(frames['long-baseline'],frames['long-input'])if a[key]!=b[key]]for key in ['cpu_pc','gpu_pc','dsp_pc','framebuffer_hash','audio_nonsilent_total']}
    command_diffs=[int(a['frame'])for a,b in zip(commands['long-baseline'],commands['long-input'])if a!=b]
    assert hashes=={str(p):digest(p)for p in [core,image,bios,binary,original_observer]}
    report={'recorded_at':datetime.now(timezone.utc).isoformat(),'directory':str(out),'status':'completed_pending_coordinator_review',
            'protocol':protocol,'runs':runs,'preflight900_exact_frame_command_DSP_watch_match':True,
            'long_baseline_first900_match':True,'pre_input_state_equal_through689':True,
            'input_vs_baseline_difference_frames':diffs,'input_vs_baseline_command_difference_frames':command_diffs,'inputs_core_original_observer_unchanged':True}
    save(out/'report.json',report);save(session/'emulator-runtime/long-audio-current.json',report)
    print(json.dumps({'directory':str(out),'difference_counts':{k:len(v)for k,v in diffs.items()},'command_difference_frames':len(command_diffs),'status':report['status']}),flush=True)


if __name__=='__main__':main()
