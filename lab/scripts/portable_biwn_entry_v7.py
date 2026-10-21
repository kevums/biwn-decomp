"""Moved game-workbench entry;use copied evidence,SDK and package-owned weights."""
import argparse,fcntl,json,os,runpy,subprocess,sys
from pathlib import Path
PACKAGE=Path(__file__).resolve().parent.parent

def main():
 ap=argparse.ArgumentParser();ap.add_argument('action',choices=['status','reader','coder','coder-live','training-progress','prompts','preview','check-preview','register-model']);args=ap.parse_args()
 # Acquire the existing same-host machine lock before installing origin guards.
 # The sole allowed origin operation here is coordinating that lock descriptor.
 lock=None
 if args.action in ['reader','coder','register-model']:
  origin=json.loads((PACKAGE/'origin.json').read_text());candidate=Path(origin['original_workbench'])/'runs/.inference.lock';coordination=candidate if candidate.is_file()else PACKAGE/'.machine-inference.lock';lock=coordination.open('a')
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:
   print('Another local model job is active. Saved status and the playable preview remain available.');return
  model_setup=PACKAGE/'workbench/portable_models_game.py';command=[str(PACKAGE/'runtime/python/bin/python3.12'),str(model_setup)]
  if args.action!='register-model':command+=['--load','daily_base']
  subprocess.run(command,check=True,cwd='/',env={k:v for k,v in os.environ.items()if k not in ['PYTHONPATH','PYTHONHOME','VIRTUAL_ENV']})
  if args.action=='register-model':return
 # The menu deliberately uses the relocatable base interpreter. Explicitly
 # expose its copied SDK before any inference imports, as native Chat does.
 sys.path.insert(0,str(PACKAGE/'runtime/.venv/lib/python3.12/site-packages'))
 sys.path.insert(0,str(PACKAGE/'runtime'))
 import portable_runtime_paths_v8 as adapter
 adapter.install();sys.path.insert(0,str(PACKAGE/'workbench'))
 if args.action in ['reader','coder']:
  import assistant_chat
  models=json.loads((PACKAGE/'portable-model-bindings.json').read_text())['models'];selected=models['daily_base']
  for domain in ['game','advertising']:assistant_chat.lab.CONFIG['models'][domain].update(model_key=selected['model_key'],identifier=selected['identifier'])
 scripts=PACKAGE/'workbench/scripts'
 if args.action in ['preview','check-preview']:
  preview=PACKAGE/'runtime/native-preview-v4/scripts';sys.path.insert(0,str(preview));script=preview/'run_biwn_native_keyboard_v4.py';sys.argv=[str(script),'--check-only'if args.action=='check-preview'else'--play-audio']
 else:
  name,extra={'status':('show_native_status_v2.py',['--brief']),'reader':('run_deck_status_live_v35.py',['--default']),'coder':('run_local_scene_reset_flags_v3.py',[]),'coder-live':('show_scene_reset_coder_v1.py',[]),'training-progress':('show_game_geometry_progress_v4.py',[]),'prompts':('show_current_model_work_v4.py',['--no-open'])}[args.action];script=scripts/name;sys.argv=[str(script),*extra]
 runpy.run_path(str(script),run_name='__main__')
if __name__=='__main__':main()
