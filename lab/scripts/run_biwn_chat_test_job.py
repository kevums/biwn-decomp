"""Detached worker for a fixed four-frame CPU/GPU comparison, with strict terminal state."""
import argparse,fcntl,json,os,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--job-folder',type=Path,required=True);args=ap.parse_args();folder=args.job_folder.resolve();state=json.loads((folder/'state.json').read_text());state.update(pid=os.getpid(),status='queued',started_unix=time.time());
    def save():
        temporary=folder/'state-next.json';temporary.write_text(json.dumps(state,indent=2)+'\n');temporary.replace(folder/'state.json')
    save()
    kind=state['kind'];assert kind in ['CPU','GPU','GPU_full','Dialogue','Music','Cold'] and state['direction']in ['none','U']and state['frames']==(600 if kind=='Cold'else 179 if kind=='Music'else 32 if kind=='Dialogue'else 4)
    with (ROOT/'runs/.frame-test.lock').open('a')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);state['status']='running';save()
        script='run_biwn_cold_start_test.py'if kind=='Cold'else'run_biwn_music_startup_test.py'if kind=='Music'else'run_biwn_dialogue_test.py'if kind=='Dialogue'else'run_biwn_frame_CPU_test.py'if kind=='CPU'else'run_biwn_GPU_frame_test.py'
        command=[sys.executable,str(ROOT/'scripts'/script)]
        if kind not in ['Dialogue','Music','Cold']:command+=['--frames','4']
        if kind in ['GPU','GPU_full']:command+=['--direction',state['direction'],'--material-bundles']
        if kind=='GPU_full':command+=['--control-bundles','--setup-bundles','--native-GPU-bridge','--GPU-frame-only','--native-CPU-bridge']
        state['command']=command;save()
        with (folder/'comparison.log').open('w')as log:p=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
        state.update(status='passed'if p.returncode==0 else'failed',exit_code=p.returncode,elapsed_seconds=time.time()-state['started_unix'],log=str(folder/'comparison.log'))
        if p.returncode==0:
            name='frame-CPU-owner-runtime-current.json'if kind=='CPU'else'setup-GPU-runtime-current.json'if kind=='GPU_full'else'material-GPU-runtime-current.json'
            proof_path=ROOT/'verification'/name
            report_lines=[line[8:]for line in (folder/'comparison.log').read_text().splitlines()if line.startswith('Report: ')]
            assert len(report_lines)==1;proof_path=Path(report_lines[0])
            proof=json.loads(proof_path.read_text());(folder/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');state['proof']=str(folder/'proof.json')
            if kind=='Music':
                assert proof['status']=='fresh_DSP_comparison_pass'and proof['frames']==179 and all(proof['checks'].values())
            if kind=='Cold':
                assert proof['status']=='CPU_GPU_DSP_frame_comparison_pass'and proof['frames']==600 and proof['original_warm_frames']==0 and proof['restored_original_checkpoint']is None and all(proof['checks'].values())
            state['checked_result']={key:proof[key]for key in ['status','direction','frames','CPU_owned_instructions','GPU_counts','frontend_nonzero_audio_samples','reconstructed_DSP_playback_verified','regular_GPU_owned_bundles','regular_GPU_original_bundles_remaining','all_regular_GPU_owned_in_test_window','GPU_instruction_states_recorded','native_elapsed_seconds','original_CPU_in_owned_window','all_audio_samples_silent','whole_game_complete']if key in proof}
            if kind=='CPU':state['checked_result']['runs']={key:{k:v[k]for k in ['frames','owned_CPU_instructions','original_CPU_instructions','all_audio_samples_silent']if k in v}for key,v in proof['runs'].items()}
            if kind=='Cold':
                state['checked_result'].update(owned_CPU_instructions=proof['owned_CPU_instructions'],DSP_counts=proof['DSP_counts'],original_warm_frames=0,no_saved_starting_state=True,PCM_byte_exact=proof['checks']['frontend-PCM.s16le'],remaining_providers=proof['remaining_providers'])
                if proof.get('source_IRQ_entry'):
                    state['checked_result']['source_IRQ_entry']=proof['source_IRQ_entry']
                    state['scope']='Fresh600frames with sourceCPU/GPU/DSP plus portableIRQentry. No warmup/checkpoint. IRQselection/ACK,hostcommit/prefetch/cyclecharge,HLE/devices remain; silentstartupPCM,notfullgame/nativeChat proof.'
            state['checked_result']['limits']=proof.get('limits',[])
            if proof.get('DSP_report'):
                state['checked_result']['DSP_core_counts']=proof['DSP_report']['core_counts']
                state['checked_result']['PCM_byte_exact']=proof['checks'].get('frontend_PCM_byte_exact',proof['checks'].get('frontend-PCM.s16le',False))
        save()
if __name__=='__main__':main()
