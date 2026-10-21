"""Reject four controlled defects using unchanged native clear acceptance assertions."""
import json,os,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def main():
 positive=read(V/'native-clear-contract-v1-current.json');assert positive['completed']==260 and positive['budget_cases']==35
 out=V/'native-clear-faults-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 original=ROOT/'projects/black-ice-white-noise/restoration/native-m68k/deck-shared-v9/native-clear-stages.inc';text=original.read_text();checker=(ROOT/'scripts/check_native_clear_contract_v1.py').read_text();rows=[]
 mutants=[('lost_high_word','r[1]&=0xffff0000u','r[1]=0',[0]),('lost_CLR_read','uint8_t old=*byte','uint8_t old=0',[1]),('wrong_X','(void)deck_alu(s,total,r[8],1,1);','(void)deck_alu(s,total,r[8],1,1);s->cpu.sr^=16u;',[1]),('signed_unsigned_compare','total>deck_sx16(counter)','(int32_t)total>(int32_t)deck_sx16(counter)',[256])]
 for name,old,new,selected in mutants:
  assert text.count(old)==1;folder=out/name;folder.mkdir();source=folder/'mutant.inc';source.write_text(text.replace(old,new));script=folder/'checker.py';changed=checker.replace("str(SRC/'native-clear-stages.inc')",repr(str(source)))
  changed=changed.replace("if case['root']!=0x10968:continue","if case['root']!=0x10968 or case['variant']not in "+repr(selected)+":continue")
  family='native-clear-fault-'+name+'-v1';changed=changed.replace('native-clear-contract-v1',family);script.write_text(changed)
  p=subprocess.run([sys.executable,str(script)],cwd='/',env={**os.environ,'PYTHONPATH':str(ROOT/'scripts')},capture_output=True,text=True,timeout=180);(folder/'check.log').write_text(p.stdout+p.stderr);result=read(V/(family+'-current.json'));assert p.returncode!=0 and result['status']=='terminal_native_clear_contract_failed',(name,p.returncode,result)
  gate=Path(result['directory']);counter=gate/('trace-mismatch.json'if name=='lost_CLR_read'else'counterexample.json');assert counter.exists(),name
  rows.append(dict(name=name,rejected=True,exit_code=p.returncode,mutant=str(source),checker=str(script),receipt=result,counterexample=str(counter)));print(name,'rejected',flush=True)
 save(out/'cases.json',rows)
 import hashlib
 paths=[Path(__file__),original,ROOT/'scripts/check_native_clear_contract_v1.py',out/'cases.json',*[Path(row['mutant'])for row in rows],*[Path(row['checker'])for row in rows]]
 state=dict(status='terminal_native_clear_four_deliberate_faults_rejected',directory=str(out),completed=len(rows),new_predictions=0,new_training=False,installed_preview_changed=False,source_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths},scope=__doc__);save(out/'review.json',state);save(V/'native-clear-faults-v1-current.json',state)
if __name__=='__main__':main()
