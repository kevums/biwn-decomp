"""Keep daily Chat/team launchers on the tested base, with current BIWN evidence."""
import json,shutil
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];INSTALLED=Path.home()/'.lmstudio/local-ai-lab';out=ROOT/'config-backups'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')/'daily-team-consistency';out.mkdir(parents=True)
for base,label in [(ROOT,'root'),(INSTALLED,'installed')]:
 for name in ['config.json','lab.py']:
  shutil.copy2(base/name,out/f'{label}-{name}')
for name in ['Game Team.command','Advertising Team.command']:shutil.copy2(ROOT/name,out/name)
p=ROOT/'config.json';d=json.loads(p.read_text());old=d['models']['game'];new=dict(old);daily=d['models']['advertising'];
for k in ['repo','model_key','identifier','api','reasoning']:new[k]=daily[k]
new.pop('sampling',None);new.pop('sampling_source',None);new['status']='Daily game and advertising workflows share the tested 27B/6bit base. Experimental game v3 failed code gates and is unpromoted. Historical coding probes below refer to their explicitly named models, not this daily default.';d['models']['game']=new;p.write_text(json.dumps(d,indent=2)+'\n');shutil.copy2(p,INSTALLED/'config.json')
p=ROOT/'lab.py';s=p.read_text();needle='  evidence=tool_chunks+retrieve(domain,task,k=4 if binary_selection else None)';replacement=needle+'''
  if domain=='game':
   session_pointer=ROOT/'projects/black-ice-white-noise/analysis/current-session.json'
   if session_pointer.exists():
    session=Path(json.loads(session_pointer.read_text())['directory']);summary_path=session/'emulator-runtime/summary.json'
    if summary_path.exists():
     firmware=json.loads(summary_path.read_text()).get('firmware_bootstrap_DSP_progress',{})
     latest=firmware.get('plain_language_summary')
     if latest:evidence.insert(0,dict(source=str(summary_path),number=0,digest=sha(summary_path),body='CURRENT BIWN SAVED REPORT (specific to Black Ice White Noise; no test was run by this lookup): '+latest,priority='current_scoped_status'))
'''
assert needle in s;s=s.replace(needle,replacement);p.write_text(s);shutil.copy2(p,INSTALLED/'lab.py')
for name,domain in [('Game Team.command','game'),('Advertising Team.command','advertising')]:
 p=ROOT/name;s=p.read_text().replace(f'run {domain} "$LAB_TASK"',f'run {domain} "$LAB_TASK" --profile mac64-chat');p.write_text(s)
report=dict(status='daily_launchers_consistent_checks_pending',directory=str(out),previous_game_model=old['model_key'],daily_model=new['model_key'],identifier=new['identifier'],daily_context=32768,roles_sequential=True,weights_trained=False,experimental_adapter_promoted=False)
(ROOT/'verification/daily-team-consistency-current.json').write_text(json.dumps(report,indent=2)+'\n');print(out)
