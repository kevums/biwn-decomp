"""Package-local model registration/loading using copied Python dependencies and CLI.
This installer intentionally registers package-owned model links in the host LM
Studio installation. Inference runs separately in the guarded copied venv.
"""
import argparse,hashlib,json,os,sys,time,uuid,subprocess
from pathlib import Path
PACKAGE=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(PACKAGE/'runtime/.venv/lib/python3.12/site-packages'))
import yaml
LMS=PACKAGE/'lmstudio-home/bin/lms'
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def command(*args):return subprocess.check_output([str(LMS),*args],text=True,timeout=60)
def register():
 idfile=PACKAGE/'portable-package-id.json'
 if not idfile.exists():save(idfile,dict(id=uuid.uuid4().hex[:12]))
 identity=read(idfile)['id'];inventory=read(PACKAGE/'model-resource-inventory.json');host=Path.home()/'.lmstudio';bindings={};writes=[]
 previous=read(PACKAGE/'model-registration-receipt.json')if(PACKAGE/'model-registration-receipt.json').exists()else{}
 for label,definition_name in [('daily_base','advertising-qwen38'),('trained_reviewer_step8','advertising-reviewer-experimental')]:
  row=next(x for x in inventory if x['model']==label and Path(x['target_home_relative']).name=='config.json');relative=Path(row['target_home_relative']);weights=(PACKAGE/'lmstudio-home'/Path(*relative.parts[1:])).parent;assert weights.is_dir()
  suffix='daily'if label=='daily_base'else'reviewer';alias='portable-ailab-'+identity+'-'+suffix;link=host/'models/local'/alias;link.parent.mkdir(parents=True,exist_ok=True)
  if link.exists()or link.is_symlink():
   assert link.is_symlink(),'Preserve unrelated model directory'
   if link.resolve()!=weights.resolve():
    prior=next(x for x in previous.get('resources',[])if x['label']==label);assert str(link.readlink())==prior['copied_weights'],'Preserve unrelated model link';link.unlink();link.symlink_to(weights,target_is_directory=True);writes.append(str(link))
  else:link.symlink_to(weights,target_is_directory=True);writes.append(str(link))
  assert link.resolve()==weights.resolve()
  for attempt in range(5):
   catalog=json.loads(command('ls','--json'));matches=[x for x in catalog if x.get('path')=='local/'+alias]
   if matches:break
   time.sleep(0.5)
  assert len(matches)==1,'LM Studio has not discovered copied model link'
  raw=matches[0];name=alias+'-configured';directory=host/'hub/models/local'/name
  if directory.exists():assert read(directory/'provenance.json')['portable_package_id']==identity,'Preserve unrelated definition'
  directory.mkdir(parents=True,exist_ok=True);config=yaml.safe_load((PACKAGE/'lmstudio-home/hub/models/local'/definition_name/'model.yaml').read_text());config['model']='local/'+name;config['base']=[dict(key=raw['indexedModelIdentifier'],sources=[])]
  (directory/'model.yaml').write_text(yaml.safe_dump(config,sort_keys=False));save(directory/'manifest.json',dict(type='model',owner='local',name=name,dependencies=[dict(type='model',purpose='baseModel',modelKeys=[raw['indexedModelIdentifier']],sources=[])],revision=1));save(directory/'provenance.json',dict(portable_package_id=identity,copied_weights=str(weights),copied_definition=str(PACKAGE/'lmstudio-home/hub/models/local'/definition_name),package_root=str(PACKAGE)))
  for attempt in range(5):
   matches=[x for x in json.loads(command('ls','--json'))if x['modelKey']=='local/'+name]
   if matches:break
   time.sleep(0.5)
  assert len(matches)==1
  identifier='portable-ailab-'+identity+'-'+suffix;bindings[label]=dict(model_key=matches[0]['modelKey'],identifier=identifier,relative_weights=str(weights.relative_to(PACKAGE)))
  writes.extend(str(directory/x)for x in ['model.yaml','manifest.json','provenance.json'])
  bindings[label]['raw_resource_key']=raw['modelKey']
 resources=[dict(label=label,**info,copied_weights=str(PACKAGE/info['relative_weights']))for label,info in bindings.items()];save(PACKAGE/'portable-model-bindings.json',dict(portable_package_id=identity,models=bindings));save(PACKAGE/'model-registration-receipt.json',dict(status='copied_models_registered',package_root=str(PACKAGE),portable_package_id=identity,resources=resources,host_model_links_written=True,host_writes=writes,source_workbench_read=False,live_default_model_changed=False));return bindings

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--load',choices=['daily_base','trained_reviewer_step8']);ap.add_argument('--context',type=int,default=32768);args=ap.parse_args();models=register()
 if args.load:
  loaded=json.loads(command('ps','--json'));assert all(x['status']=='idle'and x.get('queued',0)==0 for x in loaded),'An existing prediction is active; preserve it'
  selected=models[args.load];allowed={'local/advertising-qwen38','local/advertising-reviewer-experimental',*[x['model_key']for x in models.values()]};assert all(x['modelKey']in allowed for x in loaded),'An unrelated model is loaded; preserve it'
  if not(len(loaded)==1 and loaded[0]['modelKey']==selected['model_key']and loaded[0]['identifier']==selected['identifier']and loaded[0]['contextLength']==args.context):
   subprocess.run([str(LMS),'unload','--all'],check=True,capture_output=True,text=True,timeout=120);run=subprocess.run([str(LMS),'load',selected['model_key'],'--identifier',selected['identifier'],'--context-length',str(args.context),'--parallel','1','--ttl','3600','--yes'],capture_output=True,text=True,timeout=300);(PACKAGE/'last-model-load.log').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
  loaded=json.loads(command('ps','--json'));assert len(loaded)==1 and loaded[0]['identifier']==selected['identifier'];save(PACKAGE/'last-loaded-model.json',loaded)
 print(json.dumps(dict(status='portable_models_ready',models=models,loaded=args.load,context=args.context)))
if __name__=='__main__':main()
