"""Check masked answer-loss preservation when packaging the actual ad adapter."""
from datetime import datetime,timezone
from pathlib import Path
import fcntl,gc,hashlib,json,os,subprocess,sys,time,argparse
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from mlx_lora_reasoning_off import ReasoningOffTokenizer

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--package-report',type=Path,default=ROOT/'verification/advertising-analysis-v2-hybrid-package.json');parser.add_argument('--loss-report',type=Path,default=ROOT/'verification/advertising-analysis-v2-package-loss.json');parser.add_argument('--max-seq-length',type=int,default=512);args=parser.parse_args()
 pkg=json.loads(args.package_report.read_text());job=Path(pkg['selected_adapter']).parent;training=json.loads((job/'training-result.json').read_text());data=Path(training['data']);manifest=json.loads((data/'split-manifest.json').read_text())
 assert sha(data/'split-manifest.json')==training['dataset_manifest_sha256']
 for split,digest in manifest['split_sha256'].items():assert sha(data/(split+'.jsonl'))==digest
 assert sha(Path(pkg['selected_adapter'])/'adapters.safetensors')==pkg['adapter_sha256']
 out=job/'package-loss';out.mkdir(exist_ok=True)
 protocol={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'waiting_for_inference_lock','pid':os.getpid(),'job':str(job),'variants':['base','adapter','hybrid_package'],'test_source_groups':manifest['source_groups']['test'],'reasoning_off':True,'max_seq_length':args.max_seq_length,'batch_size':1,'aggregate_loss_tolerance':.01,'policy':'Set before package scoring; absolute aggregate masked-answer loss difference<=.01 versus selected adapter is a narrow packaging check, not proof of identical logits/text or semantic quality.','runs':[]}
 def record():save(out/'protocol.json',protocol)
 record();lms=str(Path.home()/'.lmstudio/bin/lms');cwd=Path.home()/'.lmstudio'
 with (ROOT/'runs/.inference.lock').open('w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  subprocess.run([lms,'unload','--all'],cwd=cwd,check=True,timeout=120,stdout=subprocess.DEVNULL)
  try:
   import mlx.core as mx
   from mlx_lm import load
   from mlx_lm.tuner.datasets import load_dataset,CacheDataset
   from mlx_lm.tuner.trainer import evaluate
   from types import SimpleNamespace
   base=Path.home()/'.lmstudio/models'/training['base']['repo']
   for phase in protocol['variants']:
    protocol.update(status='scoring',phase=phase);record();start=time.monotonic();mx.reset_peak_memory()
    path=Path(pkg['destination']) if phase=='hybrid_package' else base
    kwargs={'adapter_path':pkg['selected_adapter']} if phase=='adapter' else {}
    model,t=load(str(path),**kwargs);tokenizer=ReasoningOffTokenizer(t)
    _,_,test=load_dataset(SimpleNamespace(data=str(data),train=False,test=True,mask_prompt=True),tokenizer)
    processed=[test.process(test[i]) for i in range(len(test))];assert max(len(x[0]) for x in processed)<=args.max_seq_length
    per=[]
    for i in range(len(test)):
     from mlx_lm.tuner.datasets import ChatDataset
     single=ChatDataset([test[i]],tokenizer,mask_prompt=True)
     per.append(evaluate(model,CacheDataset(single),batch_size=1,num_batches=-1,max_seq_length=args.max_seq_length))
    aggregate=evaluate(model,CacheDataset(test),batch_size=1,num_batches=-1,max_seq_length=args.max_seq_length)
    row={'variant':phase,'aggregate_loss':aggregate,'per_example_loss':per,'sequence_lengths':[len(x[0]) for x in processed],'masked_prefix_lengths':[x[1] for x in processed],'seconds':round(time.monotonic()-start,3),'peak_metal_bytes':mx.get_peak_memory()};protocol['runs'].append(row);record();print(json.dumps(row),flush=True)
    del model,t,tokenizer,test,single,processed;gc.collect();mx.clear_cache()
   scores={x['variant']:x['aggregate_loss'] for x in protocol['runs']};delta=abs(scores['hybrid_package']-scores['adapter'])
   protocol.update(status='completed',scores=scores,package_minus_adapter_absolute_loss=delta,within_frozen_tolerance=delta<=protocol['aggregate_loss_tolerance'],scope='Three masked-answer examples from one held-out source group. Aggregate numerical preservation only; generated package outputs differ from direct adapter and retain documented semantic errors. Not default promotion.')
  except BaseException as e:
   protocol.update(status='failed_partial_results_preserved',error=repr(e));raise
  finally:
   record()
   with (out/'daily-model-restore.log').open('w') as f:subprocess.run([lms,'load','local/advertising-qwen38','--identifier','advertising-scholar','--context-length','32768','--parallel','1','--ttl','3600','--yes'],cwd=cwd,check=True,timeout=120,stdout=f,stderr=subprocess.STDOUT)
   protocol['daily_model_restored']=True;record()
 save(args.loss_report,protocol)
 print('Package comparison',protocol['within_frozen_tolerance'],flush=True)
if __name__=='__main__':main()
