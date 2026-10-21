"""Apply exact source replacements produced by the local model, retaining audit."""
import fcntl,json,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab
p=ROOT/'verification/local-scene-initial-setup-author-current.json';receipt=json.loads(p.read_text());out=Path(receipt['directory']);source=out/'biwn_scene_initial_setup.c';before=source.read_text();(out/'pre-repair-biwn_scene_initial_setup.c').write_text(before)
user='Original comparisons passed284ordinarycases, but the helper-failure guard failed. Interface: directbus read/write failure returns2; failure of bus->call returns3. Return JSON only with replacements array, each item old(string),new(string),plusreason. Provide exactly5 unique replacements changing ONLY the error return after each bus->call from2to3; retain every other byte. Source:\n'+before
with(ROOT/'runs/.inference.lock').open('w')as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);result=lab.generate('game',lab.COMMON+'\nReturn exact narrowly scoped C source replacements, no unrun test claim.',user,900)
(out/'repair.json').write_text(json.dumps(result,indent=2)+'\n');patch=lab.parse_object(result['text']);assert len(patch['replacements'])==5;after=before
for row in patch['replacements']:
 old,new=row['old'],row['new'];assert after.count(old)==1 and 'bus->call('in old and old.replace('return 2;','return 3;')==new,(old,new);after=after.replace(old,new,1)
source.write_text(after);receipt.update(status='local_error_mapping_repair_pending_recheck',local_repair=patch,repair_seconds=result['seconds'],pre_repair_sha256=hashlib.sha256(before.encode()).hexdigest(),repaired_sha256=hashlib.sha256(after.encode()).hexdigest(),coordinator_C_body_edits=False);p.write_text(json.dumps(receipt,indent=2)+'\n');(out/'protocol.json').write_text(json.dumps(receipt,indent=2)+'\n')
with(out/'prompts-and-responses.txt').open('a')as f:f.write('REPAIR\nREQUEST\n'+json.dumps(result['request'],indent=2)+'\nRESPONSE\n'+result['text']+'\n')
print('Local5call-errorpatch applied',result['seconds'],flush=True)
