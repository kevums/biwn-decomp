"""Four-lane old/new-core preview equivalence with isolated register GPU bridge."""
import hashlib,json,os,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    imported=json.loads((ROOT/'verification/GPU-register-checkpoint-current.json').read_text())
    assert imported['status']=='one_original_frame_cross_core_state_import_matches'
    core=json.loads((ROOT/'verification/GPU-register-state-experimental-candidate.json').read_text())
    gpu=json.loads((ROOT/'verification/GPU-register-bridge-experimental-candidate.json').read_text())
    assert gpu['required_core_sha256']==core['core_sha256']
    parent=Path(core['parent_source']);child=Path(core['source'])
    unchanged=['src/jerry/dsp.c','src/jerry/dsp.h','src/core/state.h','src/m68000/cpudefs.h','src/m68000/sysdeps.h']
    for name in unchanged:assert (parent/name).read_bytes()==(child/name).read_bytes()
    dsp_path=ROOT/'verification/GPU-register-DSP-router-experimental-candidate.json'
    dsp=json.loads((ROOT/'verification/fast-DSP-router-experimental-candidate.json').read_text())
    dsp.update(status='isolated_core_rebind_unverified',required_core_sha256=core['core_sha256'],
               previous_required_core_sha256=core['parent_core_sha256'],
               core_rebind_scope='Same DSP sources/headers/serialization and callback ABI, identical library; new core adds GPU serialization APIs only. DSP execution not established by inactive preview fixtures.')
    dsp_path.write_text(json.dumps(dsp,indent=2)+'\n')
    baseline=ROOT/'runs/world-controls-20261017T084146.540377Z';old=json.loads((baseline/'protocol.json').read_text())
    originals={row['phase']:row['command']for row in old['commands']}
    out=ROOT/'runs'/('GPU-register-preview-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir();print(out,flush=True)
    commands={}
    for phase in ['old_original','new_original','old_C','new_C']:
        mode='C'if phase.endswith('_C')else'reference';cmd=originals['C'if mode=='C'else'reference'][:]
        same_new=phase.startswith('new_');report=Path(imported['directory'])/('new_original'if same_new else'old_original')/'report.json'
        cmd[cmd.index('--restore-original-report')+1]=str(report);cmd[cmd.index('--output')+1]=str(out/phase)
        if same_new:
            cmd[cmd.index('--core')+1]=core['core_path'];cmd[cmd.index('--native-CPU-candidate')+1]=str(ROOT/'verification/GPU-register-native-CPU-experimental-candidate.json')
            if mode=='C':
                cmd[cmd.index('--native-GPU-candidate')+1]=str(ROOT/'verification/GPU-register-bridge-experimental-candidate.json')
                cmd[cmd.index('--DSP-router-candidate')+1]=str(dsp_path)
        commands[phase]=cmd
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),frames=200,commands=commands,
               old_core_sha256=core['parent_core_sha256'],new_core_sha256=core['core_sha256'],
               imported_checkpoint_proof=str(ROOT/'verification/GPU-register-checkpoint-current.json'),
               scope='Four200frame runs from byte-identical original checkpoint states, using old/new diagnostic cores and old/new source bridges. No guest instruction batching or timing changes. Trace-enabled functional comparisons; elapsed values observed under concurrent long startup workload, not native window or general performance acceptance.')
    def save():
        text=json.dumps(state,indent=2)+'\n';(out/'protocol.json').write_text(text);(ROOT/'verification/GPU-register-preview-active.json').write_text(text)
    save()
    try:
        for phase,command in commands.items():
            state['status']='running_'+phase
            with(out/(phase+'.log')).open('w')as log:
                process=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);state['child_pid']=process.pid;save();print(phase,'PID',process.pid,flush=True);code=process.wait()
            assert code==0,(phase,code,out/(phase+'.log'))
        reports={phase:json.loads((out/phase/'report.json').read_text())for phase in commands}
        before=reports['old_original'];checks={}
        files=['warm-RAM.bin','CPU-before-instructions.bin','retired-instruction-costs.bin','final-RAM.bin','final-video.bin','final-serialized-state.bin','frontend-PCM.s16le']
        for phase,report in reports.items():
            checks[phase+'_complete']=len(report['frames'])==200 and not report['errors']
            checks[phase+'_all_frames']=report['frames']==before['frames']
            checks[phase+'_CPU_count']=report['owned_CPU_instructions']+report['original_CPU_instructions']==before['original_CPU_instructions']
            for name in files:checks[phase+'_'+name]=(out/phase/name).read_bytes()==(out/'old_original'/name).read_bytes()
            if phase.endswith('_C'):
                checks[phase+'_no_CPU_fallback']=report['original_CPU_instructions']==report['rejected_CPU_instructions']==0
                for label,key,count_key in [('GPU','regular_GPU_report','counts'),('DSP','DSP_report','core_counts')]:
                    observed=json.loads(Path(report[key]).read_text());counts=observed[count_key]
                    checks[phase+'_'+label+'_no_fallback']=counts['Original']==counts['Rejected']==0
        state['checks']=checks;assert all(checks.values()),[key for key,value in checks.items()if not value]
        comparison=out/'new-comparison.json'
        command=[sys.executable,str(ROOT/'scripts/compare_biwn_frame_CPU_only.py'),'--C-run',str(out/'new_C'),'--reference',str(out/'new_original'),'--expected-frames','200','--original-checkpoint-report',imported['new_original_checkpoint'],'--output',str(comparison)]
        with(out/'comparison.log').open('w')as log:code=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT).returncode
        result=json.loads(comparison.read_text());failed=[key for key,value in result['checks'].items()if not value]
        assert code==1 and failed==['DSP_owned_positive']and result['DSP_counts']==dict(Owned=0,Original=0,Rejected=0),(code,failed)
        timings={phase:json.loads((out/phase/'native-CPU-bridge-report.json').read_text())['elapsed_seconds']for phase in ['old_C','new_C']}
        state.update(status='terminal_four_lane_CPU_GPU_frames_and_machine_match_DSP_inactive',
                     comparison=str(comparison),raw_combined_gate_passed=False,combined_failed_checks=failed,
                     CPU_instructions=result['owned_CPU_instructions'],GPU_counts=result['GPU_counts'],DSP_counts=result['DSP_counts'],
                     observed_frame_loop_seconds=timings,observed_time_reduction_percent=100*(1-timings['new_C']/timings['old_C']),
                     same_workload=True,DSP_execution_verified=False,full_GPU_hash_streams_verified=False,
                     native_window_verified=False,default_promoted=False,whole_game_complete=False)
        save();(ROOT/'verification/GPU-register-preview-current.json').write_text(json.dumps(state,indent=2)+'\n');print(json.dumps({key:state[key]for key in ['status','observed_frame_loop_seconds','observed_time_reduction_percent']}),flush=True)
    except BaseException as error:
        state.update(status='terminal_failed',error=repr(error));save();raise

if __name__=='__main__':main()
