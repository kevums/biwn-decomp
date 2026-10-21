"""One bounded local repair from concrete native failure; raw source stays auditable."""
from pathlib import Path
from datetime import datetime,timezone
import json,os,sys,re,fcntl,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import lab,assistant_chat
save=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
def main():
 pp=ROOT/'verification/local-native-resource-release-current.json';prior=json.loads(pp.read_text());pd=Path(prior['directory']);prepared=json.loads((pd/'prepared-author.json').read_text());mismatch=ROOT/'verification/native-resource-release/20261018T082353.069944Z/mismatch.json';m=json.loads(mismatch.read_text());out=ROOT/'runs'/('local-native-resource-release-repair-'+lab.stamp());out.mkdir();print(out,flush=True)
 system=prepared['system'].replace('local native C Author','local targeted Repair Author')
 user=prepared['user']+'\nPREVIOUS REJECTED C:\n'+Path(prior['source']).read_text()+'\nCoordinator defect review: r15 is the SP BEFORE the original12byte MOVEM, so the original post-MOVEM16(SP) is r15+4, not r15+16. The previous C never assigned semantic r0 or final low5CCR. Each original MULS writes full32bit D0 before comparison/free; a last-slot free may replace it through capture. Do not overwrite child r0/r1/r8/r9 with stale locals. The final D2 increment49→50 has X0; final CMP.W #49,50 has N/Z/V/C0. Preserve r16 upper bits while committing that original result. No new guard or full algorithm is supplied; infer the original scan from assembly.\nNative first failure (no matches):\n'+json.dumps({k:v for k,v in m.items()if k!='parameters'})+'\nReturn complete corrected C only.'
 state=dict(status='prepared',pid=os.getpid(),directory=str(out),previous=prior,reasoning='off',source_accepted=False,new_training=False,native_Chat=False,coordinator_supplied_complete_algorithm=False,coordinator_supplied_targeted_argument_D0_CCR_repairs=True,independent_model_validation=False)
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/local-native-resource-release-repair-active.json',state)
 mark();save(out/'prepared-author.json',dict(system=system,user=user,max_output_tokens=2400,reasoning='off'));(out/'prompts-and-responses.txt').write_text('SYSTEM\n'+system+'\nUSER\n'+user+'\n')
 try:
  with(ROOT/'runs/.inference.lock').open('a')as lock:
   fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);assistant_chat.ensure_model('game');lab.CONFIG['models']['game']['reasoning']='off';state['status']='repair_author_running';mark();a=lab.generate('game',system,user,2400)
  save(out/'response.json',a)
  with(out/'prompts-and-responses.txt').open('a')as f:f.write('RESPONSE\n'+a['text'])
  blocks=re.findall(r'```c\s*\n(.*?)```',a['text'],re.S);assert len(blocks)==1;p=out/'resource-release-native.c';p.write_text(blocks[0].strip()+'\n');state.update(status='terminal_targeted_release_repair_pending_native_gates',source=str(p),source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),raw_model_C_unchanged=True,reported_seconds=a['seconds'],usage=a['usage'],quality_flags=a['quality_flags'],recorded_at=datetime.now(timezone.utc).isoformat());mark();save(ROOT/'verification/local-native-resource-release-current.json',state);print(state['status'],a['seconds'],flush=True)
 except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
