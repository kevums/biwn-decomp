"""Resume only the unexecuted coder profile from the frozen paired comparison."""
from pathlib import Path
from datetime import datetime,timezone
import json,os,re,sys,fcntl,subprocess,hashlib,copy
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab,assistant_chat
LMS=Path.home()/'.lmstudio/bin/lms'
save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 prior_path=ROOT/'verification/native-author-model-comparison-current.json';prior=json.loads(prior_path.read_text());assert prior['status']=='terminal_comparison_failed'and prior['daily_restored']and len(prior['results'])==3 and all(x['profile']=='daily_base'for x in prior['results'])
 spec=Path(prior['precommitted_specification']);assert sha(spec)==prior['precommitted_sha256'];frozen=json.loads(spec.read_text());tasks=frozen['tasks'];expected=next(x for x in frozen['profiles']if x['name']=='coder_next')
 catalog=json.loads(subprocess.check_output([str(LMS),'ls','--json'],text=True));matches=[x for x in catalog if x['modelKey']=='qwen3-coder-next'and x['format']=='gguf'and x['path']==expected['key']];assert len(matches)==1 and matches[0]['sizeBytes']==36282685440
 profile={**expected,'key':matches[0]['modelKey']};tag=profile['name'];native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';out=ROOT/'runs'/('native-author-model-comparison-resume-'+lab.stamp());out.mkdir();print(out,flush=True)
 state=dict(status='prepared',pid=os.getpid(),directory=str(out),precommitted_specification=str(spec),precommitted_sha256=sha(spec),resumed_from=str(prior_path),resumed_from_sha256=sha(prior_path),prior_protocol=prior,results=copy.deepcopy(prior['results']),resolved_coder_metadata=matches[0],load_resolution='CLI accepts modelKey; full frozen target path is independently matched to that exact GGUF catalog entry. Prompts/budgets/target weights unchanged. Baseline not repeated.',new_training=False,default_model_changed=False,daily_restored=False)
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-author-model-comparison-active.json',state)
 def command(args,log):
  p=subprocess.run([str(LMS),*args],capture_output=True,text=True,timeout=300);(out/(log+'.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr;return p
 mark()
 with(ROOT/'runs/.inference.lock').open('a')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);before=json.loads(subprocess.check_output([str(LMS),'ps','--json'],text=True));assert len(before)==1 and before[0]['identifier']=='advertising-scholar'and before[0]['status']=='idle';state['daily_before']=before;mark()
  try:
   command(['unload','advertising-scholar'],'unload-daily');state['status']='loading_coder_next';mark();command(['load',profile['key'],'--identifier',profile['identifier'],'--context-length','16384','--parallel','1','--gpu','max','--ttl','3600','--yes'],'load-coder_next')
   loaded=json.loads(subprocess.check_output([str(LMS),'ps','--json'],text=True));assert len(loaded)==1 and loaded[0]['identifier']==profile['identifier']and loaded[0]['modelKey']=='qwen3-coder-next'and loaded[0]['format']=='gguf'and loaded[0]['sizeBytes']==36282685440;state['loaded_profiles']={**prior.get('loaded_profiles',{}),'coder_next':loaded};lab.CONFIG['models']['game']['reasoning']='off';mark()
   for task in tasks:
    assert sha(spec)==state['precommitted_sha256'];assert sha(native/task['header'])==task['header_sha256'];assert sha(ROOT/'scripts'/task['checker'])==task['checker_sha256']
    folder=out/(tag+'-'+task['name']);folder.mkdir();row=dict(profile=tag,model_key=profile['key'],task=task['name'],directory=str(folder),gate_passed=False,canonical_accepted=False);state['results'].append(row);state['status']='generating_'+tag+'_'+task['name'];mark();save(folder/'prepared-author.json',task)
    try:
     result=lab.generate('game',task['system'],task['user'],4500,model=profile['identifier']);save(folder/'response.json',result);(folder/'prompts-and-responses.txt').write_text('SYSTEM\n'+task['system']+'\nUSER\n'+task['user']+'\nRESPONSE\n'+result['text']);row.update(reported_seconds=result['seconds'],usage=result['usage'],quality_flags=result['quality_flags'])
     blocks=re.findall(r'```c\s*\n(.*?)```',result['text'],re.S|re.I)
     if len(blocks)!=1:row.update(status='rejected_code_fence_format');mark();continue
     code=blocks[0].strip()+'\n';source=folder/(task['name']+'-native.c');source.write_text(code);row.update(source=str(source),source_sha256=sha(source),raw_C_unchanged=True)
     includes=re.findall(r'^\s*#\s*include\s*[<"]([^>"]+)[>"]',code,re.M)
     if any(x not in [task['header'],'stdint.h']for x in includes)or re.search(r'\b(?:__asm__|__asm|asm|__builtin_)\b',code):row.update(status='rejected_header_or_asm_contract');mark();continue
     # Clone only artifact names/stem: candidate runs cannot replace canonical
     # current/active pointers. Build inputs, test vectors and assertions stay.
     gate_text=(ROOT/'scripts'/task['checker']).read_text();proof_name=task['prefix']+'-model-eval-'+tag
     if task['name']=='free':
      needle="name='native-free-bundle'if args.bundle else'native-free'";assert gate_text.count(needle)==1;gate_text=gate_text.replace(needle,"name='unused-eval-bundle'if args.bundle else'"+proof_name+"'").replace("build=out/'build';stem=name","build=out/'build';stem='native-free'")
     elif task['name']=='copy':
      needle="name='native-copy-bundle'if args.bundle else'native-copy';stem=name";assert gate_text.count(needle)==1;gate_text=gate_text.replace(needle,"name='unused-eval-bundle'if args.bundle else'"+proof_name+"';stem='native-copy'")
     else:
      needle="name='native-resource-release-bundle'if args.bundle else'native-resource-release'";assert gate_text.count(needle)==1;gate_text=gate_text.replace(needle,"name='unused-eval-bundle'if args.bundle else'"+proof_name+"'")
     gate=folder/'candidate-gate.py';gate.write_text(gate_text);compile(gate_text,str(gate),'exec');row['gate_script_sha256']=sha(gate);state['status']='checking_'+tag+'_'+task['name'];mark()
     with(folder/'gate.log').open('w')as log:p=subprocess.run([str(ROOT/'.venv/bin/python'),str(gate),'--source',str(source)],stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'PYTHONPATH':str(ROOT/'scripts')},timeout=300)
     row['gate_exit_code']=p.returncode;row['gate_active_proof']=str(ROOT/'verification'/(proof_name+'-active.json'))
     if p.returncode==0:
      current=ROOT/'verification'/(proof_name+'-current.json');g=json.loads(current.read_text());assert g['source_accepted']and g['native_cases']==g['trace_cases']==task['expected_full_native_cases'];row.update(status='strict_native_gate_pass_pending_manual_review',gate_passed=True,gate_proof=str(current),gate_proof_sha256=sha(current))
     else:row.update(status='rejected_native_or_compile_gate')
    except Exception as exc:row.update(status='task_failed',error=repr(exc))
    mark();print(tag,task['name'],row['status'],row.get('reported_seconds'),flush=True)
   state['status']='terminal_model_profile_comparison_complete'
  except BaseException as exc:state.update(status='terminal_comparison_failed',error=repr(exc));raise
  finally:
   loaded=json.loads(subprocess.check_output([str(LMS),'ps','--json'],text=True))
   if any(x['identifier']==profile['identifier']for x in loaded):command(['unload',profile['identifier']],'unload-coder_next')
   assistant_chat.ensure_model('advertising');after=json.loads(subprocess.check_output([str(LMS),'ps','--json'],text=True));assert len(after)==1 and after[0]['identifier']=='advertising-scholar';state.update(daily_after=after,daily_restored=True,finished_at=datetime.now(timezone.utc).isoformat());mark();save(ROOT/'verification/native-author-model-comparison-current.json',state)
 print(state['status'],'gate passes',sum(x['gate_passed']for x in state['results']),flush=True)
if __name__=='__main__':main()
