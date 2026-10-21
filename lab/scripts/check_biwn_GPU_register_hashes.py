"""Check GPU boundary hash streams, then untraced old/new preview equivalence."""
import hashlib,json,os,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    prior=json.loads((ROOT/'verification/GPU-register-preview-current.json').read_text())
    assert prior['status']=='terminal_four_lane_CPU_GPU_frames_and_machine_match_DSP_inactive'
    out=ROOT/'runs'/('GPU-register-hash-check-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir();print(out,flush=True)
    commands={}
    for phase in ['GPU_trace_reference','GPU_trace_C','old_untraced_C','new_untraced_C']:
        base='old_C'if phase=='old_untraced_C'else'new_C';cmd=prior['commands'][base][:]
        cmd[cmd.index('--output')+1]=str(out/phase)
        if phase.startswith('GPU_trace'):
            while '--capture-frame'in cmd:
                i=cmd.index('--capture-frame');del cmd[i:i+2]
            i=cmd.index('--frame-controller-script');del cmd[i:i+2]
            cmd[cmd.index('--frames')+1]='4';cmd.remove('--GPU-frame-only')
            if phase=='GPU_trace_reference':
                cmd[cmd.index('--mode')+1]='reference';cmd[cmd.index('--regular-GPU-mode')+1]='trace'
                for flag in ['--native-DSP-owner','--require-owned-DSP','--stop-on-GPU-original']:cmd.remove(flag)
                for flag in ['--DSP-owner-kind','--DSP-router-candidate']:
                    i=cmd.index(flag);del cmd[i:i+2]
        else:cmd+=['--no-instruction-trace']
        commands[phase]=cmd
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),commands=commands,
               scope='Four-frame GPU boundary before-state/PC hash streams plus complete CPU traces/frame/machine comparison. Then two200frame CPU-trace-off source runs from byte-identical old/new original states. Timings observed under concurrent long startup work; native interaction and general performance unverified.')
    def save():
        text=json.dumps(state,indent=2)+'\n';(out/'protocol.json').write_text(text);(ROOT/'verification/GPU-register-hash-check-active.json').write_text(text)
    save()
    try:
        for phase,cmd in commands.items():
            state['status']='running_'+phase
            with(out/(phase+'.log')).open('w')as log:
                child=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT);state['child_pid']=child.pid;save();print(phase,'PID',child.pid,flush=True);code=child.wait()
            assert code==0,(phase,code,out/(phase+'.log'))
        reports={phase:json.loads((out/phase/'report.json').read_text())for phase in commands};checks={};hashes={}
        before=reports['GPU_trace_reference'];after=reports['GPU_trace_C']
        checks['four_frame_records']=len(before['frames'])==len(after['frames'])==4 and before['frames']==after['frames']
        checks['four_frame_no_errors']=not before['errors']and not after['errors']
        for name in ['CPU-before-instructions.bin','retired-instruction-costs.bin','warm-RAM.bin','final-RAM.bin','final-video.bin','final-serialized-state.bin','frontend-PCM.s16le']:
            checks['four_frame_'+name]=(out/'GPU_trace_reference'/name).read_bytes()==(out/'GPU_trace_C'/name).read_bytes()
        for name in ['before-state-hashes.bin','PC-stream.bin']:
            left=out/'GPU_trace_reference/regular-GPU-bundles'/name;right=out/'GPU_trace_C/regular-GPU-bundles'/name
            assert left.stat().st_size>0;checks[name]=left.read_bytes()==right.read_bytes();hashes[name]=hashlib.sha256(right.read_bytes()).hexdigest()
        for phase,baseline in [('old_untraced_C','old_C'),('new_untraced_C','new_C')]:
            original_dir=Path(prior['directory'])/baseline;original=json.loads((original_dir/'report.json').read_text());observed=reports[phase]
            checks[phase+'_frames']=observed['frames']==original['frames'] and len(observed['frames'])==200 and not observed['errors']
            checks[phase+'_CPU_count']=observed['owned_CPU_instructions']==original['owned_CPU_instructions']
            checks[phase+'_no_CPU_fallback']=observed['original_CPU_instructions']==observed['rejected_CPU_instructions']==0
            checks[phase+'_no_disk_trace']=not(out/phase/'CPU-before-instructions.bin').exists()and not(out/phase/'retired-instruction-costs.bin').exists()
            for name in ['warm-RAM.bin','final-RAM.bin','final-video.bin','final-serialized-state.bin','frontend-PCM.s16le']:
                checks[phase+'_'+name]=(out/phase/name).read_bytes()==(original_dir/name).read_bytes()
            for label,key,count_key in [('GPU','regular_GPU_report','counts'),('DSP','DSP_report','core_counts')]:
                one=json.loads(Path(original[key]).read_text());two=json.loads(Path(observed[key]).read_text())
                checks[phase+'_'+label+'_counts']=one[count_key]==two[count_key]
                checks[phase+'_'+label+'_no_fallback']=two[count_key]['Original']==two[count_key]['Rejected']==0
        old_GPU=json.loads(Path(reports['old_untraced_C']['regular_GPU_report']).read_text())['counts'];new_GPU=json.loads(Path(reports['new_untraced_C']['regular_GPU_report']).read_text())['counts']
        checks['old_new_GPU_counts']=old_GPU==new_GPU
        trace_GPU=json.loads(Path(after['regular_GPU_report']).read_text())['counts'];checks['trace_GPU_source_owned']=trace_GPU['Owned']>0 and trace_GPU['Original']==trace_GPU['Rejected']==0
        state['checks']=checks;assert all(checks.values()),[key for key,value in checks.items()if not value]
        times={phase:json.loads((out/phase/'native-CPU-bridge-report.json').read_text())['elapsed_seconds']for phase in ['old_untraced_C','new_untraced_C']}
        state.update(status='terminal_GPU_boundary_hash_and_untraced_preview_match',GPU_boundary_hashes=hashes,
                     checked_GPU_boundaries=(out/'GPU_trace_C/regular-GPU-bundles/PC-stream.bin').stat().st_size//4,
                     traced_GPU_counts=trace_GPU,preview_GPU_counts=new_GPU,observed_frame_loop_seconds=times,
                     observed_time_reduction_percent=100*(1-times['new_untraced_C']/times['old_untraced_C']),
                     same_workload=True,frames=200,DSP_execution_verified=False,native_window_verified=False,default_promoted=False,
                     scope=state['scope']+' GPU hashes cover canonical4396byte before-state snapshots and callback PCs, including the shared4096byteRAM. Delayed pairs follow the existing bundle protocol; no separate internal-delay-slot post-state comparison. Inactive DSP/silent PCM do not establish audio/DSP coverage. New starts retain the documented exact cross-core checkpoint import.')
        save();(ROOT/'verification/GPU-register-hash-check-current.json').write_text(json.dumps(state,indent=2)+'\n');print(json.dumps({key:state[key]for key in ['status','checked_GPU_boundaries','observed_frame_loop_seconds','observed_time_reduction_percent']}),flush=True)
    except BaseException as error:
        state.update(status='terminal_failed',error=repr(error));save();raise

if __name__=='__main__':main()
