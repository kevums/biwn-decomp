"""Base or adapter code-only generation under identical resource-family prompts."""
import argparse,fcntl,gc,hashlib,json,os,re,shutil,subprocess,sys,time
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--job',type=Path);p.add_argument('--case-file',type=Path);args=p.parse_args()
 dataset=json.loads((ROOT/'verification/native-function-curriculum-current.json').read_text());data=Path(dataset['directory'])
 manifest=json.loads((data/'split-manifest.json').read_text());assert sha(data/'reviewed-source-examples.jsonl')==manifest['input_sha256']
 rows=[json.loads(x)for x in (data/'reviewed-source-examples.jsonl').read_text().splitlines()];held=[x for x in rows if x['split']=='test'];assert len(held)==3
 if args.case_file:
  held=[json.loads(args.case_file.read_text())];assert held[0]['source_id']not in manifest['source_groups']['train']+manifest['source_groups']['valid']
 phase='adapter'if args.job else'base'
 suffix='-fresh'if args.case_file else''
 out=data/(phase+suffix+'-evaluation')/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 state=dict(status='prepared',phase=phase,directory=str(out),dataset=str(data),pid=os.getpid(),results=[],default_promoted=False,raw_model_C_unchanged=True,sampling=dict(temperature=0,max_output_tokens=5000,enable_thinking=False),scope=manifest['scope'])
 scripts=[Path(__file__),ROOT/'scripts/check_native_curriculum_candidate.py',*[ROOT/'scripts'/('check_biwn_native_'+row['function_id']+'.py')for row in held]]
 snapshot=out/'orchestration-as-run';snapshot.mkdir()
 for script in scripts:shutil.copy2(script,snapshot/script.name)
 state['execution_scripts_sha256']={str(script):sha(script)for script in scripts}
 if args.case_file:state.update(case_file=str(args.case_file.resolve()),case_file_sha256=sha(args.case_file),scope='New formatting-helper prompt, outside this trial training/validation and original adaptive resource test. Coordinator reference/ABI and CPU gates were prepared before any local-model call. This is one fresh development case, not broad independent generalization.')
 if args.job:
  trained=json.loads((args.job/'training-result.json').read_text());assert trained['status']=='pilot_adapter_created_unpromoted'and trained['data']==str(data)
  state.update(training_job=str(args.job),adapter_sha256=sha(args.job/'adapters/adapters.safetensors'))
 pointers=[ROOT/'verification'/n for n in ['native-resource-release-current.json','native-resource-acquire-controlled-current.json','native-resource-load-current.json','native-format-pad-current.json']]
 before={str(q):sha(q)for q in pointers if q.exists()}
 def save():
  for path in [out/'protocol.json',ROOT/'verification'/f'native-function{suffix}-{phase}-evaluation-current.json']:path.write_text(json.dumps(state,indent=2)+'\n')
 save();lms=str(Path.home()/'.lmstudio/bin/lms')
 with (ROOT/'runs/.inference.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  try:
   subprocess.run([lms,'unload','--all'],cwd=Path.home()/'.lmstudio',check=True,capture_output=True,text=True,timeout=120)
   os.environ['MLX_DISABLE_COMPILE']='1'
   import mlx.core as mx
   from mlx_lm import load,stream_generate
   from mlx_lm.sample_utils import make_sampler
   from mlx_lm.tuner.utils import load_adapters
   mx.set_cache_limit(512*1024**2)
   state['status']='loading_model';save()
   model,tokenizer=load(str(Path.home()/'.lmstudio/models/lmstudio-community/Qwen3.8-27B-MLX-6bit'))
   if args.job:load_adapters(model,str(args.job/'adapters'));mx.eval(model.parameters())
   for row in held:
    folder=out/row['function_id'];folder.mkdir();messages=row['messages'][:-1]
    (folder/'prompt.json').write_text(json.dumps(messages,indent=2)+'\n')
    prompt=tokenizer.apply_chat_template(messages,tokenize=True,add_generation_prompt=True,enable_thinking=False)
    state.update(status='generating',current_function=row['function_id']);save();start=time.monotonic();response='';last=None
    for token in stream_generate(model,tokenizer,prompt,max_tokens=5000,sampler=make_sampler(temp=0)):
     response+=token.text;last=token
    result=dict(function=row['function_id'],seconds=time.monotonic()-start,response=response,prompt_tokens=len(prompt),generation_tokens=last.generation_tokens,generation_tps=last.generation_tps,finish_reason=last.finish_reason,verified=False)
    (folder/'inference.json').write_text(json.dumps(result,indent=2)+'\n');(folder/'response.txt').write_text(response)
    source=response.strip();fence=re.fullmatch(r'```(?:c|c99)?\s*\n([\s\S]*?)\n```\s*',source)
    if fence:source=fence.group(1)
    result['format_normalization']='single outer c fence removed'if fence else'none'
    candidate=folder/Path(row['source']).name;candidate.write_text(source+'\n');result['candidate_sha256']=sha(candidate)
    for header in Path(row['snapshots']).glob('*.h'):(folder/header.name).write_bytes(header.read_bytes())
    state['status']='checking_generated_code';save()
    command=[sys.executable,str(ROOT/'scripts/check_native_curriculum_candidate.py'),row['function_id'],str(candidate),str(folder/'receipts')]
    try:
     checked=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=240)
     result.update(verified=checked.returncode==0,exit_code=checked.returncode)
     (folder/'check.log').write_text(checked.stdout+checked.stderr)
     if checked.stdout.splitlines():result['gate_directory']=checked.stdout.splitlines()[0]
    except subprocess.TimeoutExpired as error:
     result.update(verified=False,gate_timeout=True);(folder/'check.log').write_text(str(error.stdout)+'\n'+str(error.stderr))
    (folder/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    state['results'].append({k:result[k]for k in ['function','seconds','generation_tokens','finish_reason','verified','candidate_sha256']});save()
    print(phase,row['function_id'],result['verified'],round(result['seconds'],2),flush=True);mx.clear_cache()
   assert all(sha(q)==h for q,h in before.items())
   state.update(status='terminal_code_evaluation',passed=sum(x['verified']for x in state['results']),total=len(held),accepted_pointers_unchanged=True);save()
  except BaseException as e:state.update(status='terminal_failed',error=repr(e));save();raise
  finally:
   if 'model'in locals():del model
   if 'mx'in locals():gc.collect();mx.clear_cache();mx.synchronize()
   restored=subprocess.run([lms,'load','local/advertising-qwen38','--identifier','advertising-scholar','--context-length','32768','--parallel','1','--ttl','3600','--yes'],cwd=Path.home()/'.lmstudio',capture_output=True,text=True,timeout=300)
   state['daily_model_restored']=restored.returncode==0;save();(out/'daily-model-reload.log').write_text(restored.stdout+restored.stderr)
if __name__=='__main__':main()
