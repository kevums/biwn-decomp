"""Require source-level defects to produce real original/C counterexamples."""
import hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 trial=json.loads((ROOT/'verification/Deck-coordinate-source-candidate-current.json').read_text());source=Path(trial['candidate']);text=source.read_text();assert sha(source)==trial['candidate_sha256']
 out=ROOT/'verification/deck-coordinate-checker-qualification'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 mutations=[('inverted_unsigned_bound','if(s->cpu.sr&1u)','if(!(s->cpu.sr&1u))'),('wrong_stack_reclamation','deck_adjust(s,8);','deck_adjust(s,4);'),('unsigned_word_offset','r[9]-=deck_sx16(deck_read(s,r[11]+14,2));','r[9]-=deck_read(s,r[11]+14,2);'),('wrong_angle_mask','r[1]=255;','r[1]=65535;')]
 rows=[]
 for name,old,new in mutations:
  assert old in text,name
  folder=out/name;folder.mkdir();candidate=folder/'candidate.c';candidate.write_text(text.replace(old,new,1))
  command=[str(ROOT/'.venv/bin/python3.12'),str(ROOT/'scripts/check_deck_coordinate_source_v2.py'),str(candidate),str(folder/'checks'),'--limit','16']
  with(folder/'check.log').open('w')as log:p=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
  proof=json.loads((folder/'checks/protocol.json').read_text());assert p.returncode==1 and proof['status']=='terminal_component_rejected'and proof['compiler_exit_code']==0,(name,proof)
  counterexample=Path(proof['counterexample']);assert counterexample.exists()
  rows.append(dict(mutation=name,rejected=True,completed_before_failure=proof['completed'],candidate_sha256=sha(candidate),counterexample=str(counterexample),counterexample_sha256=sha(counterexample)))
 report=dict(status='terminal_Deck_coordinate_source_mutations_rejected',directory=str(out),candidate=str(source),candidate_sha256=sha(source),mutations=rows,source_sha256={str(p):sha(p)for p in [Path(__file__),ROOT/'scripts/check_deck_coordinate_source_v1.py',ROOT/'scripts/check_deck_coordinate_source_v2.py']},scope='Four compiled source defects rejected by nativeCPU/RAM/helper-entry comparisons. Finite checker sensitivity evidence,not exhaustive correctness.')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/Deck-coordinate-checker-qualification-current.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],flush=True)
if __name__=='__main__':main()
