"""Apply exact local-model cleanup edits; no coordinator C edits."""
from datetime import datetime,timezone
import fcntl,json,sys,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab,binary_tools,assistant_chat

def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def main():
    parent=json.loads((ROOT/'verification/local-native-controller-current.json').read_text());p=Path(parent['candidate']);out=ROOT/'runs'/('local-native-controller-cleanup-'+lab.stamp());out.mkdir(parents=True);print(out,flush=True)
    system='You are local Repairer. Return only JSON {"edits":[{"old":"exact literal text","new":"replacement"}]}. No markdown, no commentary, no test claims. Exact old strings must occur once.'
    user='The C draft fails -Wall -Wextra -Werror because static functions ror32 and rol32 are unused. Delete ONLY those two full function definitions; keep every other source byte unchanged. Duplicate mask expressions on nonvolatile local v have no extra observable access and need no change. Return exactly two deletion edits.\nSOURCE:\n'+p.read_text()
    state=dict(status='running',directory=str(out),recorded_at=datetime.now(timezone.utc).isoformat(),parent_source=str(p),parent_source_sha256=binary_tools.sha(p),system=system,user=user,native_Chat=False,new_training=False,coordinator_supplied_exact_repair_plan=True)
    save(out/'protocol.json',state)
    with (ROOT/'runs/.inference.lock').open('w')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);assistant_chat.ensure_model('game');response=lab.generate('game',system,user,450)
    save(out/'response.json',response);text=response['text'].strip();text=re.sub(r'^```(?:json)?\s*|\s*```$','',text);edits=json.loads(text)['edits'];assert len(edits)==2
    source=p.read_text()
    for edit in edits:
        assert edit['new']=='' and source.count(edit['old'])==1
        assert edit['old'].lstrip().startswith('static uint32_t ')
        assert edit['old'].count('{')==edit['old'].count('}')==1
        source=source.replace(edit['old'],edit['new'])
    candidate=out/'controller-native.c';candidate.write_text(source)
    (out/'prompts-and-responses.txt').write_text('SYSTEM\n'+system+'\nUSER\n'+user+'\nRESPONSE\n'+response['text']+'\n')
    state.update(status='terminal_model_literal_cleanup_pending_CPU_gates',candidate=str(candidate),candidate_sha256=binary_tools.sha(candidate),seconds=response['seconds'],edits=edits,coordinator_manually_edited_C=False,source_derivation='Local Author C plus two exact local Repairer deletion edits; host literal matcher applied them. Coordinator supplied algorithm, ABI and cleanup diagnosis.')
    save(out/'protocol.json',state);save(ROOT/'verification/local-native-controller-cleanup-current.json',state);print(state['status'],response['seconds'],flush=True)
if __name__=='__main__':main()
