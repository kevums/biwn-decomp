"""One explicit temporary GPU-register intervention versus untouched baseline."""
import csv
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import signal
import subprocess
import time
from observe_biwn_processor_state import digest,ROOT

def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    binary=ROOT/'tools/biwn-gpu-stack-experiment';core=ROOT/'tools/virtualjaguar-runtime-source/virtualjaguar_libretro.dylib'
    image=ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi';bios=ROOT/'projects/black-ice-white-noise/reference-bios/jaguar-cd-user-provided.bin'
    hashes={str(p):digest(p) for p in (binary,core,image,bios)}
    assert hashes[str(image)]=='0aaef12221309e3266861ebe5da0c14f419de49aac7eb727302e0f5983ec532f'
    out=session/'emulator-runtime'/('gpu-stack-test-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
    inputs=out/'inputs';inputs.mkdir(parents=True);(inputs/image.name).symlink_to(image);(inputs/'jaguarcd_bios.bin').symlink_to(bios)
    protocol={'hypothesis':'BIOS-installed GPU handler depends on a valid bank0r31 stack before the game starts.',
              'intervention':'Initialize bank0r31 toF03FF0 once afterframe437, before438. No other guest-state writes by the harness.',
              'comparison':'Untouched baseline, same observer/options900frames; full CPU/GPU/DSPPC and framebuffer hash streams retained.',
              'limits':'Experimental proposed GPU-RAM stack location, not documented original stack. Assisted BIOS mode. Sensitivity test only, not hardware fix or reconstructed-game validation.',
              'framebuffer_hash_collection_enabled':True,'source':str(ROOT/'scripts/biwn_gpu_stack_experiment.c')}
    (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    runs=[];all_frames={}
    for name,setting in [('baseline',None),('initialized','F03FF0'),('initialized-input','F03FF0')]:
        cwd=out/name;cwd.mkdir()
        command=[str(binary),str(core),str(inputs/image.name),'--frames','900','--bios','--system-dir',str(inputs),
                 '--option','virtualjaguar_cd_boot_mode=bios','--option','virtualjaguar_usefastblitter=enabled',
                 '--option','virtualjaguar_crash_detect=enabled']
        events=['690:up:90','810:left:45'] if name=='initialized-input' else []
        for event in events:command+=['--press',event]
        env=os.environ.copy();env.update(VJ_EXPECT_BUILD='unknown',VJ_HARNESS_LOG_INFO='1');env.pop('BIWN_EXPERIMENT_GPU_STACK',None)
        if setting:env['BIWN_EXPERIMENT_GPU_STACK']=setting
        status={'command':command,'name':name,'setting':setting,'input_events':events,'status':'running','wall_budget_seconds':90}
        (cwd/'status.json').write_text(json.dumps(status,indent=2)+'\n')
        start=time.monotonic()
        with (cwd/'run.log').open('w') as log:
            process=subprocess.Popen(command,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            print(name,process.pid,flush=True)
            try:process.wait(timeout=90)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid,signal.SIGTERM)
                try:process.wait(timeout=5)
                except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
                status['wall_budget_expired']=True
        status.update(exit_code=process.returncode,status='terminal',seconds=round(time.monotonic()-start,3))
        (cwd/'status.json').write_text(json.dumps(status,indent=2)+'\n')
        if process.returncode:raise RuntimeError('GPU stack experiment failed: '+str(cwd))
        with (cwd/'processor-state.csv').open() as f:frames=list(csv.DictReader(f))
        assert len(frames)==900;all_frames[name]=frames
        status.update(final_frame=frames[-1],boot_wait_samples=sum(int(f['cpu_pc'],16) in (0x180178,0x18017e,0x180182) for f in frames),
                      low_running_GPU_samples=sum(int(f['gpu_pc'],16)<0x4000 and int(f['gpu_control'],16)&1!=0 for f in frames),
                      artifact_sha256={p.name:digest(p) for p in cwd.iterdir() if p.is_file() and p.name!='status.json'})
        assert (cwd/'guest-state-change.txt').exists()==bool(setting)
        (cwd/'status.json').write_text(json.dumps(status,indent=2)+'\n');runs.append(status)
        print(name,'terminal',status['seconds'],'seconds',flush=True)
    with (session/'emulator-runtime/pc-observer-20261012T221455.207800Z/bios/frame_pcs.csv').open() as f:prior=list(csv.DictReader(f))
    assert len(prior)==900
    prior_mismatches=[int(a['frame']) for a,b in zip(all_frames['baseline'],prior) if any(a[k]!=b[k] for k in ('frame','cpu_pc','gpu_pc','dsp_pc'))]
    differences={k:[int(a['frame']) for a,b in zip(all_frames['baseline'],all_frames['initialized']) if a[k]!=b[k]] for k in ('cpu_pc','gpu_pc','dsp_pc','framebuffer_hash','audio_nonsilent_total')}
    assert all(all_frames['baseline'][i]==all_frames['initialized'][i] for i in range(437))
    assert all(all_frames['initialized'][i]==all_frames['initialized-input'][i] for i in range(689))
    input_differences={k:[int(a['frame']) for a,b in zip(all_frames['initialized'],all_frames['initialized-input']) if a[k]!=b[k]] for k in ('cpu_pc','gpu_pc','dsp_pc','framebuffer_hash')}
    assert hashes=={str(p):digest(p) for p in (binary,core,image,bios)}
    report={'recorded_at':datetime.now(timezone.utc).isoformat(),'directory':str(out),'status':'controlled_experiment_completed_requires_review',
            'protocol':protocol,'runs':runs,'baseline_prior_PC_mismatch_frames':prior_mismatches,'all_pre_intervention_observations_equal':True,
            'difference_frames':differences,'originals_core_and_probe_unchanged':hashes,
            'input_comparison':{'pre_input_observations_equal_through_frame':689,'difference_frames':input_differences},
            'source_sha256':digest(ROOT/'scripts/biwn_gpu_stack_experiment.c')}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    (session/'emulator-runtime/gpu-stack-test-current.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'directory':str(out),'baseline_prior_PC_mismatches':len(prior_mismatches),'difference_counts':{k:len(v) for k,v in differences.items()},'final_frames':[r['final_frame'] for r in runs]},indent=2),flush=True)

if __name__=='__main__':main()
