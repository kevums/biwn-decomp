"""Bounded reasoning-enabled comparison on the same full-function task."""
import fcntl
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import lab
from run_local_portal_author_test import ensure_game_model
def main():
    ensure_game_model()
    previous=json.loads((ROOT/'verification/local-scene-actor-author-current.json').read_text())
    evidence=json.loads((Path(previous['directory'])/'evidence.json').read_text())
    out=ROOT/'runs'/(lab.stamp()+'-reasoning-scene-actor-loader');out.mkdir();print(out,flush=True)
    (out/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    protocol=dict(status='running',directory=str(out),roles=['local Reasoning Author'],reasoning_requested='on',default_configuration_changed=False,new_training=False,native_Chat_verified=False)
    (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    with (ROOT/'runs/.inference.lock').open('w')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        lab.CONFIG['models']['game']['reasoning']='on'
        result=lab.generate('game','Recover the supplied complete 68000 routine in readable C99 using the exact host contract. Return JSON only with source and limitations. Work from the original assembly; preserve every memory operation and signed comparison.',json.dumps(evidence),6000)
    (out/'author.json').write_text(json.dumps(result,indent=2)+'\n')
    (out/'prompts-and-responses.txt').write_text('LOCAL REASONING AUTHOR\nREQUEST\n'+json.dumps(result['request'],indent=2)+'\nRESPONSE\n'+result['text']+'\n')
    try:proposed=lab.parse_object(result['text'])
    except (ValueError,KeyError)as error:
        protocol.update(status='terminal_failed_no_usable_source',error=repr(error),usage=result['usage'],seconds=result['seconds'],quality_flags=result['quality_flags'])
        (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
        raise
    (out/'biwn_local_scene_actor_loader.c').write_text(proposed['source']+'\n')
    protocol.update(status='proposed_reasoning_source_pending_checks',drafts=[dict(role='reasoning_author',text=result['text'],seconds=result['seconds'],quality_flags=result['quality_flags'])],usage=result['usage'])
    (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    (ROOT/'verification/local-scene-actor-author-current.json').write_text(json.dumps(protocol,indent=2)+'\n');print(protocol['status'],result['seconds'],result['usage'],flush=True)
if __name__=='__main__':main()
