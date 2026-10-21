"""Require four distinct Deck input source defects to fail original CPU checks."""
import json,subprocess,hashlib
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 proof=json.loads((ROOT/'verification/Deck-input-source-current.json').read_text());source=Path(proof['source']);text=source.read_text()
 out=ROOT/'verification/deck-input-checker-qualification'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);rows=[]
 for name,old,new,last in [('wrong_direction_priority','if(bit(s,r[1],20))','if(bit(s,r[1],21))',False),('dirty_flag_wrong_button','if(bit(s,r[2],13))','if(bit(s,r[2],12))',False),('wrong_face_argument','scene_push_word(s,face);','scene_push_word(s,face+1);',False),('reset_leaves_rotation','deck_write(s,0x40402,4,0);deck_nz(s,0,32);','deck_write(s,0x40402,4,1);deck_nz(s,1,32);',True)]:
  assert old in text;folder=out/name;folder.mkdir();candidate=folder/'candidate.c'
  if last:
   i=text.rfind(old);candidate.write_text(text[:i]+new+text[i+len(old):])
  else:candidate.write_text(text.replace(old,new,1))
  command=[str(ROOT/'.venv/bin/python3.12'),str(ROOT/'scripts/check_deck_input_source_v1.py'),'--source',str(candidate),'--output',str(folder/'checks'),'--limit','2048']
  with(folder/'check.log').open('w')as log:p=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
  assert p.returncode!=0,name;counter=folder/'checks/counterexample.json';assert counter.exists(),(name,(folder/'check.log').read_text());x=json.loads(counter.read_text());rows.append(dict(mutation=name,rejected=True,case=x['case'],source_sha256=sha(candidate),counterexample=str(counter),counterexample_sha256=sha(counter)))
 report=dict(status='terminal_Deck_input_four_source_mutations_rejected',directory=str(out),source=str(source),source_sha256=sha(source),mutations=rows,checker_source_sha256={str(p):sha(p)for p in[Path(__file__),ROOT/'scripts/check_deck_input_source_v1.py']},scope='Actual compiled wrongdirection/dirtybutton/faceargument/reset controls rejected against nativeCPU/RAM/helperentry. Finite sensitivity,not exhaustive correctness.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/Deck-input-checker-qualification-current.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],flush=True)
if __name__=='__main__':main()
