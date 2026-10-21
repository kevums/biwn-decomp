"""Matched local full-source inference; preserve raw outputs for source adjudication."""
import argparse,fcntl,gc,hashlib,json,os,re,shutil,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')

def structural_review(case,response,finish):
    """Mechanical evidence only; semantic pass remains unadjudicated."""
    checks=dict(complete_generation=finish!='length',semantic_review='pending_coordinator_source_review',overall_pass=None)
    if case['role']=='Educator':
        checks.update(words=len(response.split()),within_320_words=len(response.split())<=320,has_PDF_page_locator=bool(re.search(r'(?:PDF\s*)?pp?\.?\s*\d',response)))
    else:
        try:
            value=json.loads(response);assert isinstance(value,dict)and set(value)=={'issues'}and isinstance(value['issues'],list)
            draft=json.loads(case['messages'][-1]['content'])['draft']
            for issue in value['issues']:
                assert set(issue)=={'issue_type','draft_excerpt','problem','correction','source_pages'}
                assert all(isinstance(issue[k],str)for k in ['issue_type','draft_excerpt','problem','correction'])
                assert not issue['draft_excerpt']or issue['draft_excerpt']in draft
                assert isinstance(issue['source_pages'],list)and all(isinstance(p,int)and p>0 for p in issue['source_pages'])
            checks.update(valid_complete_schema=True,issue_count=len(value['issues']))
            if case['kind']=='reviewer_correct_draft_control':checks['zero_issues_on_clean_control']=not value['issues']
        except (ValueError,TypeError,AssertionError,KeyError)as error:checks.update(valid_complete_schema=False,schema_error=repr(error))
    return checks

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--job',type=Path);args=parser.parse_args()
    prepared=read(ROOT/'verification/advertising-v10-frozen-cases-current.json');directory=Path(prepared['directory']);data=Path(prepared['dataset'])
    assert sha(directory/'frozen-cases.json')==prepared['frozen_cases_sha256']
    frozen=read(directory/'frozen-cases.json');assert sha(directory/'frozen-protocol.json')==frozen['protocol_sha256']and sha(directory/'coordinator-rubrics-not-sent.json')==frozen['rubrics_sha256']
    assert sha(data/'train.jsonl')==frozen['train_sha256']and sha(data/'valid.jsonl')==frozen['validation_sha256']
    phase='adapter'if args.job else'base';out=directory/(phase+'-evaluation')/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    scripts=[Path(__file__),ROOT/'scripts/select_advertising_v10_checkpoint.py',ROOT/'scripts/target_chunk_loss.py']
    snapshot=out/'orchestration-as-run';snapshot.mkdir()
    for source in scripts:shutil.copy2(source,snapshot/source.name)
    state=dict(status='waiting_for_inference_lock',phase=phase,pid=os.getpid(),directory=str(out),frozen_cases_sha256=prepared['frozen_cases_sha256'],results=[],new_training=bool(args.job),default_promoted=False,
       backend='Offline local MLX; no LM Studio Chat visibility claim',sampling=dict(temperature=0,enable_thinking=False,prefill_step_size=256),source_review_required=True,whole_goal_complete=False,execution_scripts_sha256={str(p):sha(p)for p in scripts})
    def mark():save(out/'protocol.json',state);save(ROOT/'verification'/f'advertising-v10-{phase}-evaluation-current.json',state)
    mark();print(out,flush=True);lms=str(Path.home()/'.lmstudio/bin/lms')
    with(ROOT/'runs/.inference.lock').open('a')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        try:
            subprocess.run([lms,'unload','--all'],cwd=Path.home()/'.lmstudio',check=True,capture_output=True,text=True,timeout=120)
            os.environ['MLX_DISABLE_COMPILE']='1'
            import mlx.core as mx
            from mlx_lm import load,stream_generate
            from mlx_lm.sample_utils import make_sampler
            mx.set_cache_limit(512*1024**2);state['status']='loading_model';mark()
            model,tokenizer=load(str(Path.home()/'.lmstudio/models/lmstudio-community/Qwen3.8-27B-MLX-6bit'))
            if args.job:
                trained=read(args.job/'training-result.json');assert trained['status']=='pilot_adapter_created_unpromoted'and trained['data']==str(data)
                from select_advertising_v10_checkpoint import select_checkpoint
                state.update(status='rescoring_actual_saved_checkpoints',training_job=str(args.job));mark()
                selected=select_checkpoint(model,tokenizer,args.job,data);state['checkpoint_selection']=selected;mark()
            for case in frozen['cases']:
                folder=out/case['id'];folder.mkdir();save(folder/'prompt.json',case['messages'])
                if not case['context_supported']:
                    result=dict(id=case['id'],status='unsupported_context',overall_pass=False);save(folder/'result.json',result);state['results'].append(result);mark();continue
                prompt=tokenizer.apply_chat_template(case['messages'],tokenize=True,add_generation_prompt=True,enable_thinking=False)
                assert len(prompt)+case['max_output_tokens']+128<=32768
                state.update(status='generating',current_case=case['id']);mark();response='';last=None;start=time.monotonic()
                with(folder/'response.txt').open('w')as stream:
                    for token in stream_generate(model,tokenizer,prompt,max_tokens=case['max_output_tokens'],sampler=make_sampler(temp=0),prefill_step_size=256):
                        response+=token.text;stream.write(token.text);stream.flush();last=token
                assert last is not None
                result=dict(id=case['id'],role=case['role'],kind=case['kind'],status='raw_output_complete_pending_source_review',seconds=time.monotonic()-start,prompt_tokens=len(prompt),generation_tokens=last.generation_tokens,generation_tps=last.generation_tps,finish_reason=last.finish_reason,response_sha256=sha(folder/'response.txt'),raw_output_unchanged=True,structural=structural_review(case,response,last.finish_reason))
                save(folder/'result.json',result);state['results'].append(result);mark();mx.clear_cache();print(phase,case['id'],round(result['seconds'],2),result['finish_reason'],flush=True)
            state.update(status='terminal_raw_outputs_pending_source_review',semantic_score=None);mark()
        except BaseException as error:state.update(status='terminal_advertising_v10_evaluation_failed',error=repr(error));mark();raise
        finally:
            if 'model'in locals():del model
            if 'mx'in locals():gc.collect();mx.clear_cache();mx.synchronize()
            restored=subprocess.run([lms,'load','local/advertising-qwen38','--identifier','advertising-scholar','--context-length','32768','--parallel','1','--ttl','3600','--yes'],cwd=Path.home()/'.lmstudio',capture_output=True,text=True,timeout=300)
            (out/'daily-model-restore.log').write_text(restored.stdout+restored.stderr);state['daily_model_restored']=restored.returncode==0;mark()

if __name__=='__main__':main()
