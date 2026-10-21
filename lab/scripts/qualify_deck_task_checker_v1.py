"""Require four distinct Deck outer task source defects to fail original CPU checks."""
import json,subprocess,hashlib
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 proof=json.loads((ROOT/'verification/Deck-task-source-current.json').read_text());source=Path(proof['source']);text=source.read_text()
 out=ROOT/'verification/deck-task-checker-qualification'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);rows=[]
 for name,old,new,last in [('wrong_local_initializer','deck_read(&s,0x11e68,4)','deck_read(&s,0x11e64,4)',False),('wrong_mail_argument_cleanup','deck_adjust(&s,28);','deck_adjust(&s,24);',False),('wrong_display_signed_test','if(!v||(v&0x80000000u))','if(!v)',False),('wrong_frame_restore','r[14]=deck_pop(&s);','(void)deck_pop(&s);',False)]:
  assert old in text;folder=out/name;folder.mkdir();candidate=folder/'candidate.c'
  if last:
   i=text.rfind(old);candidate.write_text(text[:i]+new+text[i+len(old):])
  else:candidate.write_text(text.replace(old,new,1))
  command=[str(ROOT/'.venv/bin/python3.12'),str(ROOT/'scripts/check_deck_task_source_v1.py'),'--source',str(candidate),'--output',str(folder/'checks'),'--limit','1280']
  with(folder/'check.log').open('w')as log:p=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
  assert p.returncode!=0,name;counter=folder/'checks/counterexample.json';assert counter.exists(),(name,(folder/'check.log').read_text());x=json.loads(counter.read_text());rows.append(dict(mutation=name,rejected=True,case=x['case'],source_sha256=sha(candidate),counterexample=str(counter),counterexample_sha256=sha(counter)))
 report=dict(status='terminal_Deck_task_four_source_mutations_rejected',directory=str(out),source=str(source),source_sha256=sha(source),mutations=rows,checker_source_sha256={str(p):sha(p)for p in[Path(__file__),ROOT/'scripts/check_deck_task_source_v1.py']},scope='Actual compiled initializer/mail-stack/signed-display/frame-restore controls rejected against nativeCPU/RAM/helperentry. Finite sensitivity,not exhaustive correctness.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/Deck-task-checker-qualification-current.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],flush=True)
if __name__=='__main__':main()
