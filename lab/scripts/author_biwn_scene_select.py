"""Audited local roles for complete10A6A; API while locked,not native Chat history."""
import fcntl,json,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab
from run_local_portal_author_test import ensure_game_model
def main():
 ensure_game_model();prior=json.loads((ROOT/'verification/scene-selector-evidence-current.json').read_text());evidence=json.loads((Path(prior['directory'])/'evidence.json').read_text());out=ROOT/'runs'/(lab.stamp()+'-local-scene-select');out.mkdir();print(out,flush=True);(out/'biwn_scene_select.h').write_text(evidence['header']);(out/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n');drafts=[];protocol=dict(status='authoring',directory=str(out),new_training=False,native_Chat_verified=False,same_weights_correlated=True,coordinator_contribution='Original bytechecked listing,reviewed ABI/word/fullD0/data-order contract,header,prompts and original/native validators.')
 evidence['contract']+=' Return JSON only with source(string),limitations(string). Include exactly "biwn_scene_select.h". No directguestpointers,IO,allocation,assembly,librarycalls or extraexports. Use explicit signed16 conversion(v<32768?v:(int32_t)v-65536) and unsigned32 shifts to avoid signed-shift UB. Directbus failure returns2; bus->call failure MUSTreturn3. Zero arguments/callback pointers must be validated before access; output changes only on success. All addresses below are hex unless noteddecimal. Be precise about D0.low16 replacements,callbackfullD0,then EXT.L+shift3. Copy memory-move operations with temporary values so repeated reads remain repeated.'
 def save():(out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
 save()
 with(ROOT/'runs/.inference.lock').open('w')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  for role in ['author','reviewer']:
   system=lab.COMMON+'\n'+('Author the complete portable C routine from the supplied original instructions and exact contract.'if role=='author'else'Review every65originalinstructions against the draft,especially preserved highD0,signed/unsignedword comparisons,volatile rereads,repeatedtableloads and2versus3failurecodes. Return complete corrected source and limitations in JSON; do notclaim tests ran.')
   prompt=json.dumps(dict(evidence=evidence,prior=drafts));result=lab.generate('game',system,prompt,2600);(out/(role+'.json')).write_text(json.dumps(result,indent=2)+'\n')
   with(out/'prompts-and-responses.txt').open('a')as f:f.write(role.upper()+'\nREQUEST\n'+json.dumps(result['request'],indent=2)+'\nRESPONSE\n'+result['text']+'\n\n')
   drafts.append(dict(role=role,text=result['text'],seconds=result['seconds'],quality_flags=result['quality_flags']));protocol['drafts']=drafts;save();print(role,result['seconds'],result['quality_flags'],flush=True)
 parsed=lab.parse_object(drafts[-1]['text']);(out/'biwn_scene_select.c').write_text(parsed['source']+'\n');protocol.update(status='proposed_source_pending_original_checks',drafts=drafts);save();(ROOT/'verification/local-scene-select-author-current.json').write_text(json.dumps(protocol,indent=2)+'\n')
if __name__=='__main__':main()
