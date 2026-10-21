"""Local single-replacement fix after an actual fullD0 mismatch."""
import fcntl,json,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab
p=ROOT/'verification/local-frame-reference-release-author-current.json';d=json.loads(p.read_text());o=Path(d['directory']);source=o/'biwn_frame_reference_release.c';before=source.read_text();(o/'pre-repair-biwn_frame_reference_release.c').write_text(before)
user='Actual originalcomparison failed case5: ID0,mode0,count1,noIDmatches. Every38read events matched, but originalfullD0=0x8c(lastindex35*4),CfullD0=0. The loop computes offset but never assigns d0. Return JSON only replacements array(old,new),reason. ExactlyONE unique replacement that assigns d0=offset immediately after the loopoffset computation,beforethetable read. Preserve everyotherbyte and allread/store/errorbehavior. No test-successclaim. SOURCE:\n'+before
with(ROOT/'runs/.inference.lock').open('w')as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);result=lab.generate('game',lab.COMMON+'\nProvide one exact C source replacement inJSON.',user,450)
(o/'repair.json').write_text(json.dumps(result,indent=2)+'\n');patch=lab.parse_object(result['text']);assert len(patch['replacements'])==1;row=patch['replacements'][0];assert before.count(row['old'])==1 and 'd0 = offset;'in row['new'];after=before.replace(row['old'],row['new'],1);source.write_text(after);d.update(status='local_fullD0_repair_pending_recheck',local_repair=patch,repair_seconds=result['seconds'],pre_repair_sha256=hashlib.sha256(before.encode()).hexdigest(),repaired_sha256=hashlib.sha256(after.encode()).hexdigest(),coordinator_C_body_edits=False);p.write_text(json.dumps(d,indent=2)+'\n');(o/'protocol.json').write_text(json.dumps(d,indent=2)+'\n')
with(o/'prompts-and-responses.txt').open('a')as f:f.write('REPAIR\nREQUEST\n'+json.dumps(result['request'],indent=2)+'\nRESPONSE\n'+result['text']+'\n')
print('LocalfullD0patch applied',result['seconds'],flush=True)
