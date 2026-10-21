"""Run independent native component checks in three separate processes."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess,time
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def main():
 prep_path=ROOT/'verification/native-acquire-gates-preparation-current.json';prep=json.loads(prep_path.read_text());out=ROOT/'verification/native-acquire-bundle-gates'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 rows=[]
 for row in prep['gates']:
  assert sha(row['adapted'])==row['adapted_sha256'];kind=row['kind'];old=json.loads((ROOT/'verification'/('native-resource-bundle-'+kind+'-current.json')).read_text());cmd=[str(ROOT/'.venv/bin/python'),'-u',row['adapted']]
  if kind=='rng':cmd+=['--source',str(ROOT/'projects/black-ice-white-noise/restoration/native-m68k/rng-native.c')]
  elif kind not in ['controller','initialize']:cmd+=['--bundle']
  expected={k:v for k,v in old.items()if k in ['native_cases','cpu_cases','trace_cases','raw_count_prefix_cases','changing_read_native_cases','empty_pool_exception_cases']};rows.append(dict(kind=kind,status='queued',command=cmd,expected_counts=expected,expected_status=old['status']))
 state=dict(status='running',pid=os.getpid(),directory=str(out),preparation=str(prep_path),preparation_sha256=sha(prep_path),target_binary_sha256=prep['target_binary_sha256'],workers=3,jobs=rows,whole_game_complete=False)
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-acquire-bundle-gates-active.json',state)
 mark();live={};failed=False
 while any(x['status']in ['queued','running']for x in rows):
  for row in rows:
   if row['status']=='queued'and len(live)<3:
    log=(out/(row['kind']+'.log')).open('w');p=subprocess.Popen(row['command'],stdout=log,stderr=subprocess.STDOUT);live[row['kind']]=(p,log);row.update(status='running',pid=p.pid,log=str(out/(row['kind']+'.log')));print('Started',row['kind'],p.pid,flush=True);mark()
  for kind,(p,log)in list(live.items()):
   code=p.poll()
   if code is None:continue
   log.close();del live[kind];row=next(x for x in rows if x['kind']==kind);row['exit_code']=code
   if code:
    row['status']='failed';failed=True;print('FAILED',kind,'exit',code,flush=True)
   else:
    receipt=ROOT/'verification'/('native-acquire-bundle-'+kind+'-current.json');proof=json.loads(receipt.read_text())
    assert proof['compiled_binary_sha256']==prep['target_binary_sha256']and proof['status']==row['expected_status'],kind
    assert all(proof.get(k)==v for k,v in row['expected_counts'].items()),kind
    row.update(status='passed',receipt=str(receipt),receipt_sha256=sha(receipt),directory=proof['directory']);print('Passed',kind,row['expected_counts'],flush=True)
   mark()
  if live:time.sleep(1)
 state['status']='terminal_one_or_more_acquire_bundle_component_gates_failed'if failed else'terminal_eight_acquire_bundle_component_gates_pass';mark();save(ROOT/'verification/native-acquire-bundle-gates-current.json',state);print(state['status'],flush=True)
 if failed:raise SystemExit(1)
if __name__=='__main__':main()
