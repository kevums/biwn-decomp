"""Frozen filename-clarified diagnostic. Derived from v4; code gates unchanged.

Adaptive follow-up, not a replacement for the original benchmark.
"""
import argparse,fcntl,gc,hashlib,json,os,re,shutil,subprocess,sys,time
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path,required=True);p.add_argument('--adapter',action='store_true');args=p.parse_args()
 diagnostic=json.loads(args.manifest.read_text());data=Path(diagnostic['dataset']);manifest=diagnostic
 assert sha(diagnostic['cases'])==diagnostic['cases_sha256']
 assert all(sha(path)==digest for path,digest in diagnostic['source_sha256'].items())
 held=json.loads(Path(diagnostic['cases']).read_text());assert len(held)==4
 phase='adapter'if args.adapter else'base';suffix='-header-diagnostic-v1'
 out=Path(diagnostic['directory'])/(phase+'-evaluation')/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 state=dict(status='prepared',phase=phase,directory=str(out),dataset=str(data),pid=os.getpid(),results=[],default_promoted=False,raw_model_C_unchanged=True,sampling=dict(temperature=0,max_output_tokens=5000,enable_thinking=False),scope=manifest['scope'])
 scripts=[Path(__file__),ROOT/'scripts/select_game_geometry_checkpoint_v4.py',ROOT/'scripts/check_native_curriculum_candidate.py',*[ROOT/'scripts'/('check_biwn_native_'+row['function_id']+'.py')for row in held if row['function_id']!='plane_layout'],ROOT/'scripts/check_deck_plane_layout_v1.py']
 snapshot=out/'orchestration-as-run';snapshot.mkdir()
 for script in scripts:shutil.copy2(script,snapshot/script.name)
 state['execution_scripts_sha256']={str(script):sha(script)for script in scripts}
 state.update(diagnostic_manifest=str(args.manifest.resolve()),diagnostic_manifest_sha256=sha(args.manifest),training_job=diagnostic['training_job'],checkpoint_selection='frozen_prior_validation_selection_no_reselection')
 pointers=[ROOT/'verification'/n for n in ['native-resource-release-current.json','native-resource-acquire-controlled-current.json','native-resource-load-current.json','native-format-pad-current.json']]
 before={str(q):sha(q)for q in pointers if q.exists()}
 def save():
  for path in [out/'protocol.json',ROOT/'verification'/f'game{suffix}-{phase}-evaluation-current.json']:path.write_text(json.dumps(state,indent=2)+'\n')
 save();lms=str(Path.home()/'.lmstudio/bin/lms')
 with (ROOT/'runs/.inference.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  try:
   catalog=json.loads(subprocess.run([lms,'ps','--json'],cwd='/',capture_output=True,text=True,check=True).stdout);assert all(x.get('status')=='idle'and x.get('queued',0)==0 for x in catalog),'A live LM Studio request owns the model;do not interrupt'
   subprocess.run([lms,'unload','--all'],cwd=Path.home()/'.lmstudio',check=True,capture_output=True,text=True,timeout=120)
   os.environ['MLX_DISABLE_COMPILE']='1'
   import mlx.core as mx
   from mlx_lm import load,stream_generate
   from mlx_lm.sample_utils import make_sampler
   from mlx_lm.tuner.utils import load_adapters
   mx.set_cache_limit(512*1024**2)
   state['status']='loading_model';save()
   model,tokenizer=load(str(Path.home()/'.lmstudio/models/lmstudio-community/Qwen3.8-27B-MLX-6bit'))
   if args.adapter:
    selected=Path(diagnostic['selected_adapter']);assert sha(selected/'adapters.safetensors')==diagnostic['adapter_sha256']
    load_adapters(model,str(selected));model.eval();mx.eval(model.parameters());mx.clear_cache()
    state.update(selected_step=diagnostic['selected_step'],adapter_sha256=diagnostic['adapter_sha256']);save()
   for row in held:
    folder=out/row['function_id'];folder.mkdir();messages=row['messages']
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
    if row['function_id']=='plane_layout':
     checker=(ROOT/'scripts/check_deck_plane_layout_v1.py').read_text()
     # Preserve the complete positive/error matrix; reference-specific mutation
     # strings cannot be applied to arbitrary generated C. Baseline controls
     # already qualify that gate with four deliberate defects.
     begin=checker.index('    # Compile whole-function mutations');end=checker.index('  finally:e.native.close()',begin);checker=checker[:begin]+checker[end:]
     receipts=folder/'receipts';receipts.mkdir()
     checker=checker.replace("ROOT/'verification/deck-plane-layout-v1'","ROOT/'verification/deck-plane-layout-model-v4'").replace("ROOT/'verification/deck-plane-layout-v1-current.json'",'Path('+repr(str(receipts/'plane-layout-current.json'))+')')
     checker='"""Isolated generated-C plane scorer;full positive/error matrix."""\nimport sys\nsys.path.insert(0,'+repr(str(ROOT/'scripts'))+')\n'+checker
     program=folder/'plane-checker-as-run.py';program.write_text(checker)
     command=[sys.executable,str(program),'--source',str(candidate)]
    else:
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
