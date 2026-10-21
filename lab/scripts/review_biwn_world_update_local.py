"""Logged local Analyst/Reviewer contracts for the checked CPU update caller."""
import fcntl,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab

def main():
 report=json.loads((ROOT/'verification/biwn-world-update-checks.json').read_text());assert report['CPU_cases']==1024
 source=(ROOT/'projects/black-ice-white-noise/restoration/biwn_world_update.c').read_text()
 evidence={'portable_C':source,'original_CPU_comparison':report,'naming':'World/primary/view/axis names are analyst labels, not recovered original symbols.'}
 task='Return JSON only under120words: negative_tick_delta_after_clamp(integer; input signed-1), fraction_3fff_plus1_remainder(integer), fraction_3fff_plus1_carry(integer), collision_result2_advances_secondary_positions(boolean), collision_result0_restores_saved_primary_positions(boolean), GPU_movement_helper_reconstructed_by_this_test(boolean), full_game_rebuilt(boolean), key_limit(string). Read exact source and scoped originalCPU checks. Previous drafts are untrusted, same-model roles are correlated.'
 out=ROOT/'runs'/(lab.stamp()+'-game-world-update-review');out.mkdir();prior=[]
 (out/'protocol.json').write_text(json.dumps({'task':task,'evidence':evidence,'roles':['analyst','reviewer'],'same_weights_correlated':True,'native_chat_history':False},indent=2)+'\n')
 with (ROOT/'runs/.inference.lock').open('w')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  for role in ['analyst','reviewer']:
   response=lab.generate('advertising',lab.COMMON+'\nYour role: '+lab.ROLES['game'][role],json.dumps({'task':task,'evidence':evidence,'previous_drafts':prior}),512)
   (out/(role+'.json')).write_text(json.dumps(response,indent=2)+'\n')
   with (out/'prompts-and-responses.txt').open('a')as f:f.write(role.upper()+'\nREQUEST:\n'+json.dumps(response['request'],indent=2)+'\nRESPONSE:\n'+response['text']+'\n\n')
   prior.append({'role':role,'text':response['text'],'seconds':response['seconds']});print(role,response['seconds'],flush=True)
 result={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'completed_pending_coordinator_review','directory':str(out),'roles':prior}
 (out/'status.json').write_text(json.dumps(result,indent=2)+'\n');(ROOT/'verification/biwn-world-update-local-review.json').write_text(json.dumps(result,indent=2)+'\n');print(out,flush=True)
if __name__=='__main__':main()
