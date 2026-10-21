"""Read saved game-pilot progress and verify its exact worker processes."""
import argparse,json,re,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(Path(p).read_text())
def case_lines(e):
 return [f"  {x['function']}: {'accepted'if x['verified']else'rejected'}; {x['generation_tokens']:,} tokens in {x['seconds']:.1f}s"for x in e.get('results',[])]
def snapshot():
 s=read(ROOT/'verification/game-geometry-training-v4-current.json');data=Path(s['data']);jobs=sorted((data/'jobs').glob('*/training-result.json'));job=jobs[-1]if jobs else None;t=read(job)if job else {};pids={x for x in [s.get('pid'),s.get('child_pid'),t.get('pid')]if isinstance(x,int)}
 live=[]
 for pid in sorted(pids):
  p=subprocess.run(['ps','-p',str(pid),'-o','pid=,etime=,command='],capture_output=True,text=True)
  if p.returncode==0 and any(name in p.stdout for name in ['run_game_geometry_training_v4.py','train.py game','mlx_lora_reasoning_off.py','evaluate_game_geometry_curriculum_v4.py']):live.append(p.stdout.strip())
 log=(job.parent/'training.log').read_text()if job and(job.parent/'training.log').exists()else'';clean=re.sub(r'\x1b\[[0-9;]*m','',log);updates=[int(m[1])for m in re.finditer(r'^\s*(\d+)\s+(\d+\.\d+)\s+',clean,re.M)]
 lines=['GAME MODEL TRAINING — EXPERIMENTAL',f"Phase: {s['status']}",f'Completed optimizer reports: {max(updates,default=0)} / 64','Validation rows are not optimizer updates. Loss does not establish code quality.','Base control: 0/4 code tests passed. Selected adapter remains unpromoted.','',f'Job: {job.parent if job else "not created"}','Live training/evaluation workers:']+live
 if not live:lines+=['No matching live worker found; inspect the saved terminal result.']
 lines+=['','Recent trainer log:']+clean.splitlines()[-8:]
 evaluation=ROOT/'verification/game-geometry-v4-adapter-evaluation-current.json'
 if evaluation.exists():
  e=read(evaluation)
  if e.get('dataset')==str(data):lines+=['',f"Adapter evaluation: {e['status']}"]+case_lines(e)
 diagnostic=ROOT/'verification/game-header-diagnostic-v1-current.json';diagnostic_done=True
 if diagnostic.exists():
  d=read(diagnostic);diagnostic_live=[]
  for pid in sorted({d.get('pid'),d.get('child_pid')}-{None}):
   p=subprocess.run(['ps','-p',str(pid),'-o','pid=,etime=,command='],capture_output=True,text=True)
   if p.returncode==0 and any(name in p.stdout for name in ['run_game_header_diagnostic_v1.py','evaluate_game_header_diagnostic_v1.py']):diagnostic_live.append(p.stdout.strip())
  lines+=['','Separate filename-clarified diagnostic: '+d['status'],'Original four-test benchmark remains unchanged. No new training or checkpoint selection.','Live diagnostic workers:']+diagnostic_live
  if not diagnostic_live:lines+=['No matching live diagnostic worker found.']
  for phase in ['base','adapter']:
   path=ROOT/'verification'/f'game-header-diagnostic-v1-{phase}-evaluation-current.json'
   if path.exists():
    e=read(path);lines += [phase+': '+e['status']+'; '+str(e.get('current_function',''))]+case_lines(e)
  diagnostic_done=d['status'].startswith('terminal_')and not diagnostic_live
 repair=ROOT/'verification/game-compiler-feedback-v2-current.json';repair_done=True
 if not repair.exists():repair=ROOT/'verification/game-compiler-feedback-v1-current.json'
 if repair.exists():
  c=read(repair);p=subprocess.run(['ps','-p',str(c['pid']),'-o','pid=,etime=,command='],capture_output=True,text=True)
  repair_live=p.returncode==0 and any(name in p.stdout for name in ['run_game_compiler_feedback_v1.py','run_game_compiler_feedback_v2.py'])
  lines+=['','Separate local compiler-feedback workflow: '+c['status'],'Model: '+c['model_key'],f"One Author and at most {c['maximum_generations']-1} Repair generations; no automatic game-source adoption."]
  if repair_live:lines+=['Live worker: '+p.stdout.strip()]
  for row in c.get('rounds',[]):lines+=[f"  {row['role']} round {row['round']}: {'accepted by full gate'if row['verified']else'rejected'}"]
  lines+=['Exact prompts and partial responses: '+c['directory']]
  repair_done=c['status'].startswith('terminal_')and c.get('daily_model_restored',False)and not repair_live
 decomposed_paths=[ROOT/'verification'/n for n in ['game-decomposed-clear-v3-current.json','game-decomposed-clear-v2-current.json','game-decomposed-clear-v1-current.json']]
 decomposed=max((p for p in decomposed_paths if p.exists()),key=lambda p:p.stat().st_mtime_ns,default=decomposed_paths[0]);decomposed_done=True
 if decomposed.exists():
  d=read(decomposed);p=subprocess.run(['ps','-p',str(d['pid']),'-o','pid=,etime=,command='],capture_output=True,text=True)
  active=p.returncode==0 and any(name in p.stdout for name in ['run_game_decomposed_clear_v3.py','run_game_decomposed_clear_v1.py','run_game_decomposed_clear_v2.py'])
  lines+=['','Decomposed10968 local Author/Repair: '+d['status'],'Existing daily27Bweights reused;reasoning '+d.get('reasoning_configuration','off')+';no training or automatic source adoption.']
  if active:lines+=['Live worker: '+p.stdout.strip()]
  for row in d.get('rounds',[]):
   inference=Path(row['candidate']).parent/'inference.json';info=read(inference)if inference.exists()else{}
   outcome='full gate passed;unpromoted'if row['verified']else'no final C generated'if info and not info.get('text','').strip()else row.get('checker_status','rejected')
   lines+=[row['role']+': '+outcome]
  lines+=['Exact prompts and responses: '+d['directory']]
  decomposed_done=d['status'].startswith('terminal_')and not active
 lines+=['','Model jobs that change weights restore the daily model;the decomposed trial reuses it.','The BIWN game preview runs independently.']
 return '\n'.join(lines),s['status'].startswith('terminal_')and s.get('daily_model_restored',False)and diagnostic_done and repair_done and decomposed_done
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--watch',action='store_true');args=ap.parse_args()
 try:
  while True:
   text,done=snapshot()
   if args.watch:print('\033[2J\033[H',end='')
   print(text,flush=True)
   if not args.watch or done:break
   time.sleep(10)
 except KeyboardInterrupt:pass
if __name__=='__main__':main()
