"""Logged sequential local roles for matrix semantics and linked CPU scope."""
import fcntl,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab

def main():
 report=json.loads((ROOT/'verification/biwn-movement-matrix-checks.json').read_text());pipeline=json.loads((ROOT/'verification/biwn-world-movement-pipeline-checks.json').read_text());assert report['GPU_cases']==1025 and pipeline['cases']==256
 evidence={'portable_C':(ROOT/'projects/black-ice-white-noise/restoration/biwn_movement_matrix.c').read_text(),'GPU_checks':report,'linked_CPU_checks':pipeline}
 task='Return JSON only under140words: rotation_order(list of angle1/angle2/angle3 names), speed_uses_signed_low16(boolean), rotation_rounding_bias(integer), translation_rounding_bias(integer), stored_fraction_bits(integer), identity_negative_unit_Z_fraction_word(integer; anglesall0, initialtranslation0, speedword0xffff), movement_linked_into_CPU_caller(boolean), physical_hardware_verified(boolean), whole_game_rebuilt(boolean), remaining_limit(string). Source and scoped execution checks are evidence; previous drafts untrusted and same-model roles correlated. Report actual raw16bitfraction store, not caller-masked14bits.'
 out=ROOT/'runs'/(lab.stamp()+'-game-movement-review');out.mkdir();prior=[]
 (out/'protocol.json').write_text(json.dumps({'task':task,'evidence':evidence,'roles':['analyst','reviewer'],'same_weights_correlated':True,'native_chat_history':False},indent=2)+'\n')
 with (ROOT/'runs/.inference.lock').open('w')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  for role in ['analyst','reviewer']:
   result=lab.generate('advertising',lab.COMMON+'\nYour role: '+lab.ROLES['game'][role],json.dumps({'task':task,'evidence':evidence,'previous_drafts':prior}),512)
   (out/(role+'.json')).write_text(json.dumps(result,indent=2)+'\n')
   with (out/'prompts-and-responses.txt').open('a')as f:f.write(role.upper()+'\nREQUEST:\n'+json.dumps(result['request'],indent=2)+'\nRESPONSE:\n'+result['text']+'\n\n')
   prior.append({'role':role,'text':result['text'],'seconds':result['seconds']});print(role,result['seconds'],flush=True)
 result={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'completed_pending_coordinator_review','directory':str(out),'roles':prior}
 (out/'status.json').write_text(json.dumps(result,indent=2)+'\n');(ROOT/'verification/biwn-movement-local-review.json').write_text(json.dumps(result,indent=2)+'\n');print(out,flush=True)
if __name__=='__main__':main()
