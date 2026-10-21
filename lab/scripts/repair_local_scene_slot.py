"""One bounded local repair for the observed D0 helper seed mismatch."""
import fcntl,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import lab
def main():
 pointer=ROOT/'verification/local-scene-slot-prepare-author-current.json';p=json.loads(pointer.read_text());out=Path(p['directory']);source=out/'biwn_scene_slot_prepare.c';old=source.read_text();(out/'before-D0-repair.c').write_text(old);(out/'mismatch-before-D0-repair.json').write_text((out/'mismatch.json').read_text());evidence=json.loads((out/'evidence.json').read_text())
 system=lab.COMMON+'\nReturn JSON only: replacements(array of objects old,new),limitations(string). Each old occurs exactly once. Propose only the smallest fix to this observed failing helper seed; retain every other byte.'
 prompt=json.dumps(dict(source=old,evidence=evidence,observed_failure='Original calls110D4 with full D0=64; C passes uninitialized ret_d0 (observed1). bus->call uses its final pointer as BOTH incoming and outgoing D0, as specified. Initialize the helper in/out value to current shifted-slot D0 before the call. Do not change validation or other code.'))
 (out/'D0-repair-prompt.json').write_text(json.dumps(dict(system=system,user=prompt),indent=2)+'\n')
 with(ROOT/'runs/.inference.lock').open('w')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);result=lab.generate('game',system,prompt,500)
 (out/'D0-repair.json').write_text(json.dumps(result,indent=2)+'\n');parsed=lab.parse_object(result['text']);new=old
 for patch in parsed['replacements']:
  assert new.count(patch['old'])==1;new=new.replace(patch['old'],patch['new'])
 source.write_text(new);p['drafts'].append(dict(role='D0_seed_repair',text=result['text'],seconds=result['seconds'],quality_flags=result['quality_flags']));p.update(local_repair=True,coordinator_C_body_edits=False,status='local_D0_repair_pending_original_checks');pointer.write_text(json.dumps(p,indent=2)+'\n');(out/'protocol.json').write_text(json.dumps(p,indent=2)+'\n')
 with(out/'prompts-and-responses.txt').open('a')as f:f.write('LOCAL D0 REPAIR\nREQUEST\n'+json.dumps(result['request'],indent=2)+'\nRESPONSE\n'+result['text']+'\n')
 print('Applied local D0 seed repair',result['seconds'],flush=True)
if __name__=='__main__':main()
