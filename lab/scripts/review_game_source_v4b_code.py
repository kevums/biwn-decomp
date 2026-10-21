"""Check unchanged code outputs, with explicit scaffolding and separate pointers."""
import json,re,subprocess,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];save=lambda p,x:p.write_text(json.dumps(x,indent=2)+'\n')
e=Path(json.loads((ROOT/'verification/game-source-v4b-evaluation-current.json').read_text())['directory'])
scaffold=json.loads((ROOT/'verification/BIWN-tile-task-local-author/20261015T134353.173258Z/protocol.json').read_text());reviews=[]
for phase in ['base','adapter']:
 for case in ['tile-task-grounded-cases']:
  original=e/f'{phase}-{case}.json';row=json.loads(original.read_text());raw=row['response'];fences=re.findall(r'```(?:c|C|cpp)?\s*\n(.*?)```',raw,re.S);assert len(fences)==1
  model=fences[0];out=e/f'{phase}-{case}-native-check';out.mkdir(exist_ok=True)
  candidate=out/'candidate.c';fragment=case.endswith('cases');candidate.write_text(scaffold['coordinator_prefix']+model+scaffold['coordinator_suffix']if fragment else model)
  protocol=dict(directory=str(out),phase=phase,case=case,raw_response=str(original),raw_response_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),model_code_sha256=hashlib.sha256(model.encode()).hexdigest(),coordinator_prefix=scaffold['coordinator_prefix']if fragment else None,coordinator_suffix=scaffold['coordinator_suffix']if fragment else None,model_code_edited=False,new_training=phase=='adapter',model_edits=[])
  save(out/'protocol.json',protocol);pointer=out/'report-pointer.json'
  run=subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts/check_biwn_tile_task_candidate.py'),'--candidate',str(candidate),'--author',str(out/'protocol.json'),'--report-pointer',str(pointer)],cwd=ROOT,capture_output=True,text=True)
  (out/'check.log').write_text(run.stdout+run.stderr);report=json.loads(pointer.read_text())if pointer.exists()else {'status':'checker_failed','error':run.stderr}
  reviews.append(dict(phase=phase,case=case,exit_code=run.returncode,report=report))
  print(phase,case,report['status'],flush=True)
save(e/'tile-code-review.json',dict(results=reviews,raw_model_outputs_changed=False,legacy_accepted_fragment_unchanged=True))
save(ROOT/'verification/game-source-v4b-tile-code-review.json',dict(directory=str(e),results=reviews,default_promotion=False))
