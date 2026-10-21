"""Two logged local-model roles; coordinator checks the bounded contracts."""
import fcntl,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab

def main():
 report=json.loads((ROOT/'verification/biwn-inventory-interaction-checks.json').read_text());assert report['steps']==580
 source=(ROOT/'projects/black-ice-white-noise/restoration/biwn_inventory_select.c').read_text()
 evidence={'selection_source':source,'check_report':report,'verified_example':'Input bit9 cycles internal9 to0; if bit9 and digit1 bit19 are both set, cycle branch wins. Position10 is screen digit0. No relevant bits means no redraw.'}
 task='Return JSON only, under100words: cycle_9_result(integer), cycle_plus_digit1_from4_result(integer), no_relevant_bits_redraw(boolean), physical_controller_tested(boolean), full_game_rebuilt(boolean), limitation(string). Review source and scoped checks. Do not infer whole-game or independent hardware verification. Reviewer should independently re-evaluate each answer; previous draft is untrusted.'
 out=ROOT/'runs'/(lab.stamp()+'-game-inventory-interaction-review');out.mkdir();prior=[]
 (out/'protocol.json').write_text(json.dumps({'task':task,'evidence':evidence,'roles':['analyst','reviewer'],'same_weights_correlated':True,'native_chat_history':False},indent=2)+'\n')
 with (ROOT/'runs/.inference.lock').open('w')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  for role in ['analyst','reviewer']:
   result=lab.generate('advertising',lab.COMMON+'\nYour role: '+lab.ROLES['game'][role],json.dumps({'task':task,'evidence':evidence,'previous_drafts':prior}),384)
   (out/(role+'.json')).write_text(json.dumps(result,indent=2)+'\n')
   with (out/'prompts-and-responses.txt').open('a')as f:f.write(role.upper()+'\nREQUEST:\n'+json.dumps(result['request'],indent=2)+'\nRESPONSE:\n'+result['text']+'\n\n')
   prior.append({'role':role,'text':result['text'],'seconds':result['seconds']});print(role,result['seconds'],flush=True)
 result={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'completed_pending_coordinator_review','directory':str(out),'roles':prior}
 (out/'status.json').write_text(json.dumps(result,indent=2)+'\n');(ROOT/'verification/biwn-inventory-interaction-local-review.json').write_text(json.dumps(result,indent=2)+'\n')
 print(out,flush=True)
if __name__=='__main__':main()
