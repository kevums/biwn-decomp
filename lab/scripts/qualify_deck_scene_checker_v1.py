"""Compiled wrong-stride, scan-bound, positive-test and angle-rounding controls."""
import json,subprocess,hashlib
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 component=json.loads((ROOT/'verification/Deck-scene-source-current.json').read_text());source=Path(component['source']);text=source.read_text()
 out=ROOT/'verification/deck-scene-checker-qualification'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 rows=[]
 for name,old,new in [('wrong_record_stride','deck_sx16(r[0])*46u','deck_sx16(r[0])*44u'),('skip_last_record','scene_alu16(s,r[2],15,1,1)','scene_alu16(s,r[2],14,1,1)'),('zero_treated_positive','if(!(s->cpu.sr&12u))','if(!(s->cpu.sr&8u))'),('wrong_orientation_rounding','r[1]=32;','r[1]=31;')]:
  assert old in text,name;folder=out/name;folder.mkdir();candidate=folder/'candidate.c';candidate.write_text(text.replace(old,new,1));command=[str(ROOT/'.venv/bin/python3.12'),str(ROOT/'scripts/check_deck_scene_source_v1.py'),'--source',str(candidate),'--output',str(folder/'checks'),'--limit','8']
  with(folder/'check.log').open('w')as log:p=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
  assert p.returncode!=0,name;counterexample=folder/'checks/counterexample.json';assert counterexample.exists(),(name,(folder/'check.log').read_text());proof=json.loads(counterexample.read_text());rows.append(dict(mutation=name,rejected=True,case=proof['case'],candidate_sha256=sha(candidate),counterexample=str(counterexample),counterexample_sha256=sha(counterexample)))
 report=dict(status='terminal_Deck_scene_four_source_defects_rejected',directory=str(out),source=str(source),source_sha256=sha(source),mutations=rows,checker_source_sha256={str(p):sha(p)for p in [Path(__file__),ROOT/'scripts/check_deck_scene_source_v1.py']},scope='Four deliberate compiled defects produce actual original/C CPU,RAM or helper-entry counterexamples. Finite component sensitivity,not exhaustive verification.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/Deck-scene-checker-qualification-current.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],flush=True)
if __name__=='__main__':main()
