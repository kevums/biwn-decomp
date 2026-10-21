"""Local API author/reviewer for the exact bytechecked1AE88 routine."""
import fcntl,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab
from run_local_portal_author_test import ensure_game_model
def main():
 ensure_game_model();prior=json.loads((ROOT/'verification/frame-reference-release-evidence-current.json').read_text());evidence=json.loads((Path(prior['directory'])/'evidence.json').read_text());out=ROOT/'runs'/(lab.stamp()+'-local-frame-reference-release');out.mkdir();print(out,flush=True);(out/'biwn_frame_reference_release.h').write_text(evidence['header']);(out/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n');drafts=[];receipt=dict(status='authoring',directory=str(out),new_training=False,native_Chat_verified=False,same_weights_correlated=True,coordinator_contribution='Bytechecked disassembly,reviewed ABI/register/data-order contract,header,prompts and original/native validators.')
 def save():(out/'protocol.json').write_text(json.dumps(receipt,indent=2)+'\n')
 save()
 with(ROOT/'runs/.inference.lock').open('w')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  for role in ['author','reviewer']:
   system=lab.COMMON+'\n'+('Author this complete portable C99 function,including exactly its provided header.'if role=='author'else'Audit all29originalinstructions against the draft. Preserve signed earlyreturn/count/ref tests,wantedwordwrap,fullD0 and SEPARATE TST/SUBQ memoryreads. Return corrected complete source inJSON; do notclaim tests ran.')
   prompt=json.dumps(dict(evidence=evidence,prior=drafts));result=lab.generate('game',system,prompt,1500);(out/(role+'.json')).write_text(json.dumps(result,indent=2)+'\n')
   with(out/'prompts-and-responses.txt').open('a')as f:f.write(role.upper()+'\nREQUEST\n'+json.dumps(result['request'],indent=2)+'\nRESPONSE\n'+result['text']+'\n\n')
   drafts.append(dict(role=role,text=result['text'],seconds=result['seconds'],quality_flags=result['quality_flags']));receipt['drafts']=drafts;save();print(role,result['seconds'],result['quality_flags'],flush=True)
 parsed=lab.parse_object(drafts[-1]['text']);(out/'biwn_frame_reference_release.c').write_text(parsed['source']+'\n');receipt.update(status='proposed_source_pending_original_checks',drafts=drafts);save();(ROOT/'verification/local-frame-reference-release-author-current.json').write_text(json.dumps(receipt,indent=2)+'\n')
if __name__=='__main__':main()
