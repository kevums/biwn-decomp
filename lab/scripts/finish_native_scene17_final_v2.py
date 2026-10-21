"""Continue remaining final-image gates after a generated startup-path error.
Completed geometry/retained matrices are validated and reused,never rerun.
The original v1driver remains failed. No game source/disc changes.
"""
import os,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha

def main():
 oldp=V/'native-Deck-scene17-final-v1-current.json';old=read(oldp);assert old['status']=='terminal_deeper_candidate_final_gate_failed'
 assert old['results']['geometry.py']['exit_code']==old['results']['retained.py']['exit_code']==0 and old['results']['startup.py']['exit_code']!=0
 bp=V/'native-scene17-disc-build-v1-current.json';b=read(bp);out=V/'native-scene17-final-v2'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);save(out/'failed-v1-driver.json',old)
 olddir=Path(old['directory']);state=dict(status='preparing',directory=str(out),pid=os.getpid(),results={},replayed_completed_matrices=False,whole_game_complete=False,new_training=False,fresh_gameplay_verified=False,new_outer_connected_matrix_verified=False,build=str(bp),build_sha256=sha(bp))
 def mark():save(out/'protocol.json',state);save(V/'native-scene17-final-v2-current.json',state)
 mark();proofs=[]
 for name,stem,count in [('geometry.py','native-Deck-scene17-final-geometry-v1',256),('retained.py','native-deck-retained-scene17-final-v1',4992)]:
  p=V/(stem+'-current.json');g=read(p);assert g['completed']==count and g['status'].startswith('terminal_')and'failed'not in g['status']
  for path,h in g['source_sha256'].items():assert sha(path)==h,path
  payload=Path(g['payload']).read_bytes();resident=Path(b['component']).read_bytes();off=b['shared_Deck_code_address']-b['resident_address'];assert payload==resident[off:off+len(payload)]
  state['results'][name]=dict(exit_code=0,reused_completed_matrix=True,proof=str(p),proof_sha256=sha(p));proofs.append(p)
 for name in ['startup.py','capacity.py','fallback.py','native_retained_final_checker.py','native_outer_final_checker.py','fallback-outer.py','waits-outer.py']:
  source=olddir/name;shutil.copy2(source,out/(name+'.v1-as-generated'))
  text=source.read_text().replace('native-Deck-scene17-disc-build-v1-current.json','native-scene17-disc-build-v1-current.json');(out/name).write_text(text)
 def launch(name):
  stream=(out/(name+'.log')).open('w');child=subprocess.Popen([str(ROOT/'.venv/bin/python3.12'),str(out/name)],stdout=stream,stderr=subprocess.STDOUT,cwd='/',env={**os.environ,'PYTHONPATH':str(out)+os.pathsep+str(ROOT/'scripts')});return child,stream
 def finish(name,pair):
  child,stream=pair;code=child.wait(timeout=900);stream.close();state['results'][name]=dict(exit_code=code,log=str(out/(name+'.log')));mark();assert code==0,(name,(out/(name+'.log')).read_text()[-4000:]);print(name,'passed',flush=True)
 try:
  group={name:launch(name)for name in ['startup.py','capacity.py','fallback.py']};state.update(status='checking',child_pids={k:p[0].pid for k,p in group.items()});mark()
  for name,pair in group.items():finish(name,pair)
  state['child_pids']={};mark()
  for name in ['native_outer_final_checker.py','fallback-outer.py','waits-outer.py']:
   pair=launch(name);state['child_pids']={name:pair[0].pid};mark();finish(name,pair);state['child_pids']={};mark()
  names=['native-Deck-scene17-final-geometry-v1','native-deck-retained-scene17-final-v1','shared-Deck-fallback-scene17-final-v1','native-Deck-scene17-startup-heap-v1','native-Deck-scene17-capacity-v1','native-Deck-outer-scene17-final-v1','native-Deck-outer-fallback-scene17-final-v1','native-Deck-outer-waits-scene17-final-v1'];proofs=[V/(n+'-current.json')for n in names]
  for p in proofs:
   g=read(p);assert g['status'].startswith('terminal_')and'failed'not in g['status'],(p,g['status'])
   for path,h in g.get('source_sha256',{}).items():assert sha(path)==h,path
  paths=[Path(__file__),oldp,bp,*proofs,*out.glob('*.py'),out/'failed-v1-driver.json'];state.update(status='terminal_scene17_existing_final_component_startup_heap_gates_pass',initial_driver_failed=True,initial_failure='Generated startup/capacity pointed to nonexistent native-Deck-scene17 build filename. New v2continuation corrects only that input path.',source_sha256={str(p):sha(p)for p in paths},scope=__doc__+' Exact deployedmodulegeometry256andretained4992reused. Remainingstartup6/heap192/capacity36/sharedfallback1280/outer1280/outerfallback384/wait192pairscompleted. No scene fresh/crossroot/observer/console proof.');mark();print(state['status'],flush=True)
 except BaseException as e:state.update(status='terminal_scene17_final_continuation_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
