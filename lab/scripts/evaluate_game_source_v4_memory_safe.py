"""Exact checkpoint validation first; then adaptive code/scope output gates."""
import json,hashlib,shutil,fcntl,subprocess,time,sys
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1];save=lambda p,x:p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();data=Path(json.loads((ROOT/'verification/game-source-v4b-dataset.json').read_text())['directory']);job=sorted((data/'jobs').glob('*'))[-1];training=json.loads((job/'training-result.json').read_text());assert training['status']=='pilot_adapter_created_unpromoted'
for name,h in training['adapter_files'].items():assert sha(job/name)==h
out=job/'source-evaluation';out.mkdir(exist_ok=True);cases=[]
for i,row in enumerate(json.loads(x)for x in(data/'test.jsonl').read_text().splitlines()):cases.append(dict(id=f'heldout-project-{i+1}',messages=row['messages'][:-1],max_tokens=512,scope='Prior inspected project holdout; not untouched generalization.'))
def add(name,user,tokens=512):cases.append(dict(id=name,messages=[dict(role='system',content='Use supplied source evidence. Do not claim execution or physical hardware validation. Return the requested format.'),dict(role='user',content=user)],max_tokens=tokens,scope='Adaptive known task family; training-related diagnostic, not independent generalization.'))
v3=Path(json.loads((ROOT/'verification/game-source-v3-evaluation-current.json').read_text())['directory']);old=json.loads((v3/'frozen-cases.json').read_text());old_by={x['id']:x for x in old}
for name in ['m68k-negative','m68k-C-effect','source-injection','tile-task-grounded-cases']:cases.append(old_by[name])
voice=json.loads((ROOT/'verification/actor14-local-voice-fragment-reviewed.json').read_text());add('voice-flag-C',json.loads((Path(voice['directory'])/'protocol.json').read_text())['task'],768)
add('BLS-borrow','M68000 source SUBQ.W#1,D0 then CMP.W#1,D0 then BLS: initial low D0voice1 gives decrementedD0=0, CMP wrappedresultFFFF with C1/Z0; voice2 givesD0=1,C0/Z1. Explain whether each branch is taken and why wrapped-result unsigned<=0 is the wrong test. Under90words.',384)
add('current-source-scope','Saved proof: separate frame152snapshot-derived C task sequence7721originalCPUsteps to173B0/C3928; six new coordinator task modules, remaining tasks incomplete. OneexternalIRQ2, synchronousGPU, video/DSPheld. Centry/resource/movie-world chain is separate. Actualdistance/facing/direction/math helper test388user-modefixtures; otherhelpers areABI substitutes. A local output-only voiceflag function matches65557original-outputfixtures afterfenceremoval, fullCPU/stack/flags notproved andnotlive-linked. Is fullCboot/playability or generalmodelreliability proved? Explainunder110words.',512)
add('authorship-units','Evidence: legacy171model instruction case bodies and139game components; separate output-only semantic checksum andvoiceflagfunctions; six experimental coordinator task modules. Do two semantic functions mean173instructionbodies and141components? Explain under70words without mixing these units.',320)
save(out/'frozen-cases.json',cases);protocol=dict(status='running',directory=str(out),job=str(job),cases_sha256=sha(out/'frozen-cases.json'),results=[],validation_selection=[],selection_policy='Evaluate the exact saved checkpoint on validation; lowest measured loss, earliest exact tie. Training logs validate before the named update, so do not pair their printed loss with the after-update file.',new_default_promotion=False,temperature=0,enable_thinking=False);save(out/'protocol.json',protocol);print(out,flush=True)
with(ROOT/'runs/.inference.lock').open('a')as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);lms=str(Path.home()/'.lmstudio/bin/lms');subprocess.run([lms,'unload','--all'],cwd=Path.home()/'.lmstudio',check=True,stdout=subprocess.DEVNULL)
 import mlx.core as mx
 from mlx_lm import load,stream_generate
 from mlx_lm.sample_utils import make_sampler
 from mlx_lm.tuner.datasets import load_dataset,CacheDataset
 from mlx_lm.tuner.trainer import evaluate
 from mlx_lm.tuner.utils import load_adapters
 from mlx_lora_reasoning_off import ReasoningOffTokenizer
 mx.set_cache_limit(2*1024**3);model,base_tokenizer=load(str(Path.home()/'.lmstudio/models'/training['base']['repo']));tokenizer=ReasoningOffTokenizer(base_tokenizer);_,valid,test=load_dataset(SimpleNamespace(data=str(data),train=False,test=True,mask_prompt=True),tokenizer);valid=CacheDataset(valid);test=CacheDataset(test)
 for phase in ['base','adapter']:
  if phase=='adapter':
   checkpoints=sorted((job/'adapters').glob('[0-9]*_adapters.safetensors'));assert len(checkpoints)==8
   selected=job/'selection-work';selected.mkdir(exist_ok=True);shutil.copy2(job/'adapters/adapter_config.json',selected/'adapter_config.json')
   for index,checkpoint in enumerate(checkpoints):
    step=int(checkpoint.name.split('_')[0])
    if index==0:shutil.copy2(checkpoint,selected/'adapters.safetensors');load_adapters(model,str(selected))
    else:model.load_weights(list(mx.load(str(checkpoint)).items()),strict=False)
    mx.eval(model.parameters());value=evaluate(model,valid,batch_size=1,num_batches=-1,max_seq_length=1024);row=dict(step=step,validation_loss=value,checkpoint=str(checkpoint),sha256=sha(checkpoint));protocol['validation_selection'].append(row);save(out/'protocol.json',protocol);mx.clear_cache();print(json.dumps(dict(checkpoint=step,validation_loss=value)),flush=True)
   best=min(protocol['validation_selection'],key=lambda x:(x['validation_loss'],x['step']));selected=job/'selected-adapter';selected.mkdir(exist_ok=True);shutil.copy2(best['checkpoint'],selected/'adapters.safetensors');shutil.copy2(job/'adapters/adapter_config.json',selected/'adapter_config.json');model.load_weights(list(mx.load(str(selected/'adapters.safetensors')).items()),strict=False);mx.eval(model.parameters());protocol['selection']={**best,'selected_adapter':str(selected)};save(job/'checkpoint-selection.json',protocol['selection']);save(out/'protocol.json',protocol)
  mx.reset_peak_memory();value=evaluate(model,test,batch_size=1,num_batches=-1,max_seq_length=1024);summary=dict(phase=phase,test_loss=value,cases=[],peak_memory_bytes=mx.get_peak_memory());protocol['results'].append(summary);save(out/'protocol.json',protocol)
  for case in cases:
   prompt=tokenizer.apply_chat_template(case['messages'],tokenize=True,add_generation_prompt=True);text='';last=None;start=time.monotonic()
   for item in stream_generate(model,base_tokenizer,prompt,max_tokens=case['max_tokens'],sampler=make_sampler(temp=0)):text+=item.text;last=item
   row=dict(phase=phase,case=case['id'],messages=case['messages'],response=text,seconds=time.monotonic()-start,finish_reason=last.finish_reason,generation_tokens=last.generation_tokens,generation_tps=last.generation_tps,peak_memory_gb=last.peak_memory,scope=case['scope'],semantic_review='pending');save(out/(phase+'-'+case['id']+'.json'),row);summary['cases'].append(case['id']);save(out/'protocol.json',protocol);print(json.dumps(dict(phase=phase,case=case['id'],seconds=round(row['seconds'],2),finish=row['finish_reason'])),flush=True);mx.clear_cache()
 protocol['status']='terminal_outputs_generated_semantic_review_pending';save(out/'protocol.json',protocol);save(ROOT/'verification/game-source-v4b-evaluation-current.json',protocol)
 (out/'prompts-and-responses.txt').write_text('\n\n'.join('FILE '+p.name+'\n'+p.read_text()for p in sorted(out.glob('base-*.json'))+sorted(out.glob('adapter-*.json'))))
print('Evaluation outputs generated; wrapper restores daily model',flush=True)
