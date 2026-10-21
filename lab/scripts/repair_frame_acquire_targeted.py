"""Audit exact local substitutions against compiler and original ABI feedback."""
import fcntl, hashlib, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import lab

p=ROOT/'verification/local-frame-resource-acquire-author-current.json'
d=json.loads(p.read_text());o=Path(d['directory']);source=o/'biwn_frame_resource_acquire.c'
before=source.read_text();(o/'pre-targeted-repair.c').write_text(before)
feedback='''Return JSON only with replacements array of {old,new}, reason. Each old must occur EXACTLY ONCE in source. Minimal literal substitutions, preserve all other bytes. Actual strict compiler still rejects four unused OUTER frame_offset/size declarations (two adjacent pairs); remove those pairs with distinct context so each old is unique. Keep the used declarations inside load_fill.
The prior repair also failed to implement these original ABI requirements: inside load_fill callback incoming D0 must be d0_shift (index<<3), not d0_idx (index<<2). Initialize d0_in=d0_shift. After callback last_d0_j must initialize to d0_in so negative count's skipped fill preserves loader-return high D0. Positive fill already updates last_d0_j correctly. Finally remove the extra remaining check/decrement immediately after count_sx==0 check in load_fill; budget is consumed once at each existing scan/fill loop, not again on entering helper. Keep all other budget checks. If d0_idx parameter becomes unused after repairs, remove it from helper signature and both call sites via exact substitutions (or explicitly consume it with (void)d0_idx; for minimal nonsemantic change). No test success claim.
SOURCE:\n'''
with (ROOT/'runs/.inference.lock').open('w') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX)
    result=lab.generate('game',lab.COMMON+'\nOutput exact small C patch JSON only.',feedback+before,2000)
(o/'targeted-repair.json').write_text(json.dumps(result,indent=2)+'\n')
patch=lab.parse_object(result['text']);after=before
for row in patch['replacements']:
    assert after.count(row['old'])==1,(row['old'],after.count(row['old']))
    after=after.replace(row['old'],row['new'],1)
source.write_text(after)
d.update(status='local_targeted_repair_pending_original_recheck',targeted_repair_seconds=result['seconds'],
         targeted_repair=patch,pre_targeted_sha256=hashlib.sha256(before.encode()).hexdigest(),
         repaired_sha256=hashlib.sha256(after.encode()).hexdigest(),coordinator_C_body_edits=False)
p.write_text(json.dumps(d,indent=2)+'\n');(o/'protocol.json').write_text(json.dumps(d,indent=2)+'\n')
with (o/'prompts-and-responses.txt').open('a') as f:
    f.write('TARGETED REPAIR\nREQUEST\n'+json.dumps(result['request'],indent=2)+'\nRESPONSE\n'+result['text']+'\n')
print('Local targeted patch saved',result['seconds'],len(patch['replacements']),flush=True)
