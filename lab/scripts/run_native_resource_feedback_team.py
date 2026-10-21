"""One local Reviewer/Restorer correction round on each failed adaptive resource task."""
import argparse, fcntl, gc, hashlib, json, os, re, shutil, subprocess, sys, time
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(Path(p).read_text())
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--protocol',type=Path,required=True);args=parser.parse_args();frozen=read(args.protocol)
    assert frozen['status']=='frozen_before_feedback_model_outputs'
    out=Path(frozen['directory']);state=dict(status='waiting_for_Advertising_resource_capped_evaluation',pid=os.getpid(),directory=str(out),protocol=str(args.protocol),results=[],new_training=False,default_promoted=False,native_Chat=False)
    pointer=ROOT/'verification/native-resource-feedback-team-current.json'
    def mark():save(out/'run.json',state);save(pointer,state)
    def inputs():
        for path,digest in frozen['input_sha256'].items():assert sha(path)==digest,path
    mark();print(out,flush=True);inputs()
    while True:
        p=subprocess.run(['ps','-p',str(frozen['after_Advertising_pid']),'-o','command='],capture_output=True,text=True)
        if not p.stdout.strip():break
        assert 'evaluate_advertising_v10_resource_capped.py'in p.stdout,'PID reused; inspect before dispatch'
        time.sleep(5)
    previous=read(ROOT/'verification/advertising-v10-resource-capped-adapter-evaluation-current.json');assert previous['status'].startswith('terminal_')and previous.get('daily_model_restored')
    inputs();lms=str(Path.home()/'.lmstudio/bin/lms')
    with(ROOT/'runs/.inference.lock').open('a')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        try:
            subprocess.run([lms,'unload','--all'],cwd=Path.home()/'.lmstudio',capture_output=True,text=True,timeout=120,check=True);os.environ['MLX_DISABLE_COMPILE']='1'
            import mlx.core as mx
            from mlx_lm import load, stream_generate
            from mlx_lm.sample_utils import make_sampler
            from mlx_lm.tuner.utils import load_adapters
            mx.set_cache_limit(512*1024**2);state['status']='loading_base_model';mark();model,tokenizer=load(str(Path.home()/'.lmstudio/models'/frozen['base_repo']))
            def generate(folder,role,messages,budget):
                folder.mkdir(parents=True);save(folder/'prompt.json',messages);prompt=tokenizer.apply_chat_template(messages,tokenize=True,add_generation_prompt=True,enable_thinking=False);assert len(prompt)+budget+128<=32768
                state.update(status='generating',current_role=role,current_task=str(folder.relative_to(out)));mark();last=None;response='';start=time.monotonic()
                with(folder/'response.txt').open('w')as stream:
                    for token in stream_generate(model,tokenizer,prompt,max_tokens=budget,sampler=make_sampler(temp=0),prefill_step_size=256):stream.write(token.text);stream.flush();response+=token.text;last=token
                assert last is not None
                receipt=dict(role=role,seconds=time.monotonic()-start,prompt_tokens=len(prompt),generation_tokens=last.generation_tokens,finish_reason=last.finish_reason,response_sha256=sha(folder/'response.txt'));save(folder/'result.json',receipt);mx.clear_cache();return response,receipt
            for phase in ['base','adapter']:
                if phase=='adapter':
                    selected=Path(frozen['selected_adapter']);assert sha(selected/'adapters.safetensors')==frozen['selected_adapter_sha256'];load_adapters(model,str(selected));model.eval();mx.eval(model.parameters());mx.clear_cache()
                for case in frozen['cases']:
                    task=out/phase/case['id'];payload=dict(original_task_messages=case['original_messages'],generated_source=case['initial_source'][phase],verifier_feedback=case['feedback'][phase])
                    messages=[dict(role='system',content=frozen['reviewer_system']),dict(role='user',content=json.dumps(payload,ensure_ascii=False))]
                    review,review_receipt=generate(task/'reviewer','Reviewer',messages,frozen['reviewer_max_tokens'])
                    messages=case['original_messages']+[dict(role='assistant',content='```c\n'+case['initial_source'][phase]+'\n```'),dict(role='user',content=frozen['restorer_instruction']+'\n\nVerifier feedback:\n'+json.dumps(case['feedback'][phase],ensure_ascii=False)+'\n\nLocal Reviewer notes (unverified suggestions):\n'+review)]
                    response,receipt=generate(task/'restorer','Restorer',messages,frozen['restorer_max_tokens']);source=response.strip();fence=re.fullmatch(r'```(?:c|c99)?\s*\n([\s\S]*?)\n```\s*',source)
                    if fence:source=fence.group(1)
                    candidate=task/(case['id'].replace('_','-')+'-candidate.c');candidate.write_text(source+'\n');state.update(status='checking_generated_C',current_task=str(task.relative_to(out)));mark()
                    command=[sys.executable,str(ROOT/'scripts/check_native_curriculum_candidate.py'),case['id'],str(candidate),str(task/'receipts')]
                    result=dict(phase=phase,function=case['id'],Reviewer=review_receipt,Restorer=receipt,verified=False,candidate_sha256=sha(candidate),format_normalization='single outer C fence removed'if fence else'none')
                    try:
                        check=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=240);(task/'check.log').write_text(check.stdout+check.stderr);result.update(verified=check.returncode==0,gate_exit_code=check.returncode)
                    except subprocess.TimeoutExpired as error:(task/'check.log').write_text(str(error));result['gate_timeout']=True
                    save(task/'result.json',result);state['results'].append(result);mark();print(phase,case['id'],result['verified'],flush=True)
            state.update(status='terminal_resource_feedback_team_outputs_pending_review',base_passed=sum(x['verified']for x in state['results']if x['phase']=='base'),adapter_passed=sum(x['verified']for x in state['results']if x['phase']=='adapter'));mark()
        except BaseException as error:state.update(status='terminal_resource_feedback_team_failed',error=repr(error));mark();raise
        finally:
            if 'model'in locals():del model
            if 'mx'in locals():gc.collect();mx.clear_cache();mx.synchronize()
            restored=subprocess.run([lms,'load','local/advertising-qwen38','--identifier','advertising-scholar','--context-length','32768','--parallel','1','--ttl','3600','--yes'],cwd=Path.home()/'.lmstudio',capture_output=True,text=True,timeout=300);(out/'daily-model-restore.log').write_text(restored.stdout+restored.stderr);state['daily_model_restored']=restored.returncode==0;mark()

if __name__=='__main__':main()
