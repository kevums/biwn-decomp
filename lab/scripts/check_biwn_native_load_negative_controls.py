"""Confirm loader execution gates reject distinct introduced semantic defects."""
from pathlib import Path
from datetime import datetime,timezone
import json,subprocess,hashlib,os
from check_biwn_native_button_digit import ROOT,save,sha

def main():
 source=ROOT/'projects/black-ice-white-noise/restoration/native-m68k/resource-load-reference.c';text=source.read_text();out=ROOT/'verification/native-load-negative-controls'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 changes=[('marker15','r[1]=15u;load_nz32(r,15u)','r[1]=14u;load_nz32(r,14u)','copy_ready'),('missing_completion','if(r[13]!=0u){LW16(r[13],1u);load_nz16(r,1u);}','if(r[13]!=0u){load_nz16(r,1u);}','copy_ready'),('null_unlock','r[0]=r[10];load_nz32(r,r[0]);return;','LW16(0x47b80u,0u);r[0]=r[10];load_nz32(r,r[0]);return;','null_handle')]
 jobs=[];state=dict(status='running',pid=os.getpid(),directory=str(out),original_source_sha256=sha(source),controls=[])
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-load-negative-controls-active.json',state)
 mark();print(out,flush=True)
 for label,old,new,kind in changes:
  assert text.count(old)==1;candidate=out/(label+'.c');candidate.write_text(text.replace(old,new));log=(out/(label+'.log')).open('w');command=[str(ROOT/'.venv/bin/python'),'-u',str(ROOT/'scripts/check_biwn_native_resource_load.py'),'--source',str(candidate),'--label','native-load-negative-'+label,'--kind',kind,'--limit','1'];child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);jobs.append((label,child,log,command,candidate))
 for label,child,log,command,candidate in jobs:
  code=child.wait();log.close();receipt=ROOT/'verification'/('native-load-negative-'+label+'-active.json');d=json.loads(receipt.read_text());assert code!=0 and d['status']=='terminal_failed',label
  mismatch=Path(d['directory'])/'mismatch.json'
  if not mismatch.exists():mismatch=Path(d['directory'])/'trace-mismatch.json'
  assert mismatch.exists(),(label,'Must fail actual execution comparison, not merely compilation/timeout')
  state['controls'].append(dict(label=label,exit_code=code,command=command,candidate=str(candidate),candidate_sha256=sha(candidate),receipt=str(receipt),receipt_sha256=sha(receipt),mismatch=str(mismatch),mismatch_sha256=sha(mismatch),actual_execution_mismatch_detected=True));mark();print(label,'rejected by native comparison',flush=True)
 assert sha(source)==state['original_source_sha256'];state.update(status='terminal_three_loader_semantic_negative_controls_detected',source_sha256={str(p):sha(p)for p in [Path(__file__),source,ROOT/'scripts/check_biwn_native_resource_load.py']});mark();save(ROOT/'verification/native-load-negative-controls-current.json',state)
if __name__=='__main__':main()
