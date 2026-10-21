"""Require four distinct Deck outer task source defects to fail original CPU checks."""
import json,subprocess,hashlib
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 proof=json.loads((ROOT/'verification/Deck-face-contact-current.json').read_text());source=Path(proof['source']);text=source.read_text()
 out=ROOT/'verification/deck-face-contact-checker-qualification'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);rows=[]
 for name,old,new,last in [('wrong_midpoint_sign','(value>>1)|(value&0x80000000u)','value>>1',False),('wrong_high_x_boundary','if(less(s))goto next;','if(less(s)||(s->cpu.sr&4u))goto next;',False),('skips_unknown_face_kinds','r[8]=deck_read(s,0x400e6,4);\n  r[1]=','if(kind>5)goto next;\n  r[8]=deck_read(s,0x400e6,4);\n  r[1]=',False),('wrong_face_selector_return','deck_call(s,0x10c6e,0x11a98)','deck_call(s,0x10c6e,0x11a96)',False)]:
  assert old in text;folder=out/name;folder.mkdir();candidate=folder/'candidate.c'
  if last:
   i=text.rfind(old);candidate.write_text(text[:i]+new+text[i+len(old):])
  else:candidate.write_text(text.replace(old,new,1))
  command=[str(ROOT/'.venv/bin/python3.12'),str(ROOT/'scripts/check_deck_face_contact_v1.py'),'--source',str(candidate),'--output',str(folder/'checks'),'--limit','2112']
  with(folder/'check.log').open('w')as log:p=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
  assert p.returncode!=0,name;counter=folder/'checks/counterexample.json';assert counter.exists(),(name,(folder/'check.log').read_text());x=json.loads(counter.read_text());rows.append(dict(mutation=name,rejected=True,case=x['case'],source_sha256=sha(candidate),counterexample=str(counter),counterexample_sha256=sha(counter)))
 report=dict(status='terminal_Deck_face_contact_four_source_mutations_rejected',directory=str(out),source=str(source),source_sha256=sha(source),mutations=rows,checker_source_sha256={str(p):sha(p)for p in[Path(__file__),ROOT/'scripts/check_deck_face_contact_v1.py']},scope='Actual compiled midpoint-sign/closed-boundary/unknown-kind/return-PC controls rejected against nativeCPU/RAM/helperentry. Finite sensitivity,not exhaustive correctness.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/Deck-face-contact-checker-qualification-current.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],flush=True)
if __name__=='__main__':main()
