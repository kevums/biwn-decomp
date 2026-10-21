"""Clarified frozen code tasks, same base/selected adapter; serialize after Advertising."""
import argparse,fcntl,gc,hashlib,json,os,re,shutil,subprocess,sys,time
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--after-advertising-pipeline',type=int,required=True);args=parser.parse_args()
    prepared=read(ROOT/'verification/native-build-contract-followup-current.json');directory=Path(prepared['directory']);frozen_path=directory/'frozen-protocol.json';assert sha(frozen_path)==prepared['protocol_sha256'];frozen=read(frozen_path)
    selected=Path(frozen['selected_adapter']);assert sha(selected/'adapters.safetensors')==frozen['selected_adapter_sha256']
    assert not (ROOT/'verification/native-build-contract-evaluation-current.json').exists(),'Inspect the prior evaluation before scheduling another'
    out=directory/'evaluation'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    scripts=[Path(__file__),ROOT/'scripts/check_native_curriculum_candidate.py',*[ROOT/'scripts'/('check_biwn_native_'+case['id']+'.py')for case in frozen['cases']]];snapshot=out/'orchestration-as-run';snapshot.mkdir()
    for p in scripts:shutil.copy2(p,snapshot/p.name)
    state=dict(status='waiting_for_advertising_pipeline',pid=os.getpid(),directory=str(out),frozen_protocol_sha256=sha(frozen_path),waiting_for_pid=args.after_advertising_pipeline,selected_step=frozen['selected_step'],selected_adapter_sha256=frozen['selected_adapter_sha256'],results=[],new_training=False,default_promoted=False,scope=frozen['scope'],execution_scripts_sha256={str(p):sha(p)for p in scripts})
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-build-contract-evaluation-current.json',state)
    mark()
    try:
        while True:
            observation=subprocess.run(['ps','-p',str(args.after_advertising_pipeline),'-o','pid=,command='],capture_output=True,text=True)
            if not observation.stdout.strip():break
            assert 'run_advertising_v10_training.py'in observation.stdout,'PID reused; inspect before model loading'
            state['last_live_advertising_observation']=dict(recorded_at=datetime.now(timezone.utc).isoformat(),process=observation.stdout.strip());mark();time.sleep(5)
        ad=read(ROOT/'verification/advertising-v10-training-current.json');assert ad['status'].startswith('terminal_')and ad.get('daily_model_restored'),'Advertising must finish and restore daily model first'
        assert all(sha(p)==state['execution_scripts_sha256'][str(p)]for p in scripts)
        with(ROOT/'runs/.inference.lock').open('a')as lock:
            fcntl.flock(lock,fcntl.LOCK_EX);lms=str(Path.home()/'.lmstudio/bin/lms')
            try:
                subprocess.run([lms,'unload','--all'],cwd=Path.home()/'.lmstudio',check=True,capture_output=True,text=True,timeout=120);os.environ['MLX_DISABLE_COMPILE']='1'
                import mlx.core as mx
                from mlx_lm import load,stream_generate
                from mlx_lm.sample_utils import make_sampler
                from mlx_lm.tuner.utils import load_adapters
                mx.set_cache_limit(512*1024**2);state['status']='loading_base_model';mark();model,tokenizer=load(str(Path.home()/'.lmstudio/models'/frozen['base_repo']))
                for phase in ['base','adapter']:
                    if phase=='adapter':
                        assert sha(selected/'adapters.safetensors')==frozen['selected_adapter_sha256'];load_adapters(model,str(selected));model.eval();mx.eval(model.parameters());mx.clear_cache()
                    for case in frozen['cases']:
                        folder=out/phase/case['id'];folder.mkdir(parents=True);save(folder/'prompt.json',case['messages']);prompt=tokenizer.apply_chat_template(case['messages'],tokenize=True,add_generation_prompt=True,enable_thinking=False);assert len(prompt)+5000+128<=32768
                        state.update(status='generating',current_phase=phase,current_function=case['id']);mark();response='';last=None;start=time.monotonic()
                        with(folder/'response.txt').open('w')as stream:
                            for token in stream_generate(model,tokenizer,prompt,max_tokens=5000,sampler=make_sampler(temp=0),prefill_step_size=256):response+=token.text;stream.write(token.text);stream.flush();last=token
                        assert last is not None
                        result=dict(phase=phase,function=case['id'],seconds=time.monotonic()-start,generation_tokens=last.generation_tokens,finish_reason=last.finish_reason,prompt_tokens=len(prompt),response_sha256=sha(folder/'response.txt'),verified=False)
                        source=response.strip();fence=re.fullmatch(r'```(?:c|c99)?\s*\n([\s\S]*?)\n```\s*',source)
                        if fence:source=fence.group(1)
                        result['format_normalization']='single outer c fence removed'if fence else'none'
                        candidate=folder/(case['id'].replace('_','-')+'-candidate.c');candidate.write_text(source+'\n');result['candidate_sha256']=sha(candidate)
                        command=[sys.executable,str(ROOT/'scripts/check_native_curriculum_candidate.py'),case['id'],str(candidate),str(folder/'receipts')];state['status']='checking_generated_code';mark()
                        try:
                            checked=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=240);(folder/'check.log').write_text(checked.stdout+checked.stderr);result.update(verified=checked.returncode==0,gate_exit_code=checked.returncode)
                        except subprocess.TimeoutExpired as error:(folder/'check.log').write_text(str(error));result['gate_timeout']=True
                        save(folder/'result.json',result);state['results'].append(result);mark();mx.clear_cache();print(phase,case['id'],result['verified'],round(result['seconds'],2),flush=True)
                state.update(status='terminal_clarified_code_outputs_pending_review',base_passed=sum(r['verified']for r in state['results']if r['phase']=='base'),adapter_passed=sum(r['verified']for r in state['results']if r['phase']=='adapter'),cases_per_model=3);mark()
            finally:
                if 'model'in locals():del model
                if 'mx'in locals():gc.collect();mx.clear_cache();mx.synchronize()
                restored=subprocess.run([lms,'load','local/advertising-qwen38','--identifier','advertising-scholar','--context-length','32768','--parallel','1','--ttl','3600','--yes'],cwd=Path.home()/'.lmstudio',capture_output=True,text=True,timeout=300);(out/'daily-model-restore.log').write_text(restored.stdout+restored.stderr);state['daily_model_restored']=restored.returncode==0;mark()
        print(state['status'],flush=True)
    except BaseException as error:state.update(status='terminal_clarified_code_trial_failed',error=repr(error));mark();raise
if __name__=='__main__':main()
