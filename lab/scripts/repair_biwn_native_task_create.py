"""One targeted local repair after retained CPU rejected the raw Author C."""
from pathlib import Path
from datetime import datetime,timezone
import fcntl,json,re,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import lab,assistant_chat,binary_tools
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def main():
    prior=json.loads((ROOT/'verification/local-native-task-create-current.json').read_text());source=Path(prior['candidate']);assert binary_tools.sha(source)==prior['candidate_sha256']
    failure=ROOT/'verification/native-task-create/20261018T054454.773296Z/mismatch.json';assert failure.exists()
    out=ROOT/'runs'/('local-native-task-create-repair-'+lab.stamp());out.mkdir(parents=True);print(out,flush=True)
    system='You are local Repairer. Return the full corrected C file in exactly one c code fence; no explanation. Apply only the two coordinator-diagnosed changes. Do not claim tests.'
    user='''The retained native CPU rejected the Author candidate. Apply exactly these two edits:
1. CMPA.W #0,A1 compares the full 32-bit address register against sign-extended immediate zero. It does NOT truncate A1 to16bits. Replace if ((uint16_t)free == 0u) with if (free == 0u). Nonzero0x110000 must allocate, not raise ILLEGAL.
2. Move the one *current_out = current; assignment from the end to immediately after the current/free volatile reads, before the if. The wrapper needs the original current pointer also when free==0. This output is private stack, not a task/global memory write.
Keep every other declaration, target read/write and order unchanged. Return complete corrected file.\n'''+source.read_text()
    with(ROOT/'runs/.inference.lock').open('a')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);assistant_chat.ensure_model('game');a=lab.generate('game',system,user,1500)
    save(out/'response.json',a);blocks=re.findall(r'```c\s*\n(.*?)```',a['text'],re.S);assert len(blocks)==1
    candidate=out/'task-create-native.c';candidate.write_text(blocks[0].strip()+'\n')
    expected=source.read_text().replace('if ((uint16_t)free == 0u)', 'if (free == 0u)').replace('    *current_out = current;\n\n','')
    expected=expected.replace('    if (free == 0u)', '    *current_out = current;\n\n    if (free == 0u)')
    assert candidate.read_text()==expected,'Repair must match exactly the two supplied edits; preserve any other model edits for review.'
    (out/'prompts-and-responses.txt').write_text('REPAIR SYSTEM\n'+system+'\nREPAIR USER\n'+user+'\nREPAIR RESPONSE\n'+a['text']+'\n')
    d=dict(status='terminal_two_exact_model_edits_pending_native_gates',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),candidate=str(candidate),candidate_sha256=binary_tools.sha(candidate),raw_model_C_unchanged=True,coordinator_supplied_exact_edits=2,prior_author_proof=prior,raw_author_native_failure=str(failure),raw_reviewer_truncated_unusable=True,seconds=a['seconds'],native_Chat=False,new_training=False)
    save(out/'protocol.json',d);save(ROOT/'verification/local-native-task-create-repair-current.json',d);print(d['status'],a['seconds'],flush=True)
if __name__=='__main__':main()
