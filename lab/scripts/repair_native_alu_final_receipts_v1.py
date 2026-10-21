"""Reconcile misnamed terminal receipts,without reexecuting or altering machine checks."""
import json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 pointer=V/'native-Deck-alu-final-v1-current.json';state=read(pointer);out=Path(state['directory']);assert state['status']=='terminal_deeper_candidate_final_gate_failed'and len(state['results'])==8 and all(x['exit_code']==0 for x in state['results'].values())
 shutil.copy2(pointer,out/'controller-failed-as-run.json');controller=ROOT/'scripts/check_native_deck_alu_final_v1.py';shutil.copy2(controller,out/'controller-as-run.py');old=read(V/'native-Deck-faces-final-v1-current.json');restored=[]
 for kind in ['fallback','waits']:
  wrong=V/f'native-Deck-outer-{kind}-faces-final-v1-current.json';right=V/f'native-Deck-outer-{kind}-alu-final-v1-current.json';new=read(wrong)
  assert str(out)in next(iter(new['source_sha256']))
  for p,h in new['source_sha256'].items():assert sha(p)==h,p
  assert not right.exists();right.write_bytes(wrong.read_bytes());expected=old['source_sha256'][str(wrong)];matches=[p for p in (V/f'native-Deck-outer-{kind}-faces-final-v1').glob('*/protocol.json')if sha(p)==expected];assert len(matches)==1;wrong.write_bytes(matches[0].read_bytes());assert sha(wrong)==expected
  restored.append(dict(previous_pointer=str(wrong),restored_from=str(matches[0]),restored_sha256=expected,new_pointer=str(right),new_receipt_sha256=sha(right)))
 text=controller.read_text();assert "+'-faces-final-v1'"in text;controller.write_text(text.replace("+'-faces-final-v1'","+'-alu-final-v1'"))
 names=['native-Deck-alu-final-geometry-v1','native-deck-retained-alu-final-v1','shared-Deck-fallback-alu-final-v1','native-Deck-alu-startup-heap-v1','native-Deck-alu-capacity-v1','native-Deck-outer-alu-final-v1','native-Deck-outer-fallback-alu-final-v1','native-Deck-outer-waits-alu-final-v1'];proofs=[V/(n+'-current.json')for n in names]
 for p in proofs:
  proof=read(p)
  for path,h in proof['source_sha256'].items():assert sha(path)==h,path
 for path,h in old['source_sha256'].items():assert sha(path)==h,path
 state.pop('error');state.update(status='terminal_deeper_candidate_final_component_startup_heap_gates_pass',metadata_reconciliation=dict(script=str(Path(__file__)),restored_previous_receipts=restored,machine_gates_reexecuted=False,reason='Two terminal outer receipt names were generated with the previous candidate family;all eight gates exited zero. Failed controller and exact generated checks retained.'),source_sha256={str(p):sha(p)for p in [Path(__file__),out/'controller-as-run.py',out/'controller-failed-as-run.json',Path(state['build']),*proofs,*list(out.glob('*.py'))]},scope='Exact-image eight machine gates pass:256geometry,4992retained,1280fallback,6startup/192heap,36capacity,1280outer,384outerfallback,192waitpairs. Reporting names reconciled without reexecution;original previous-candidate receipts restored byte-for-byte. New nesting/connected/fresh gates remain separate. No preview promotion.')
 save(out/'receipt-reconciliation.json',dict(recorded_at=datetime.now(timezone.utc).isoformat(),restored=restored));save(out/'protocol.json',state);save(pointer,state);print(state['status'])
if __name__=='__main__':main()
