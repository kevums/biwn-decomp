"""Resident-model analyst/reviewer on preserved GPU decoder source."""
from pathlib import Path
from datetime import datetime,timezone
import fcntl,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')

def main():
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);folder=session/'gpu-sprite-overlay'
    mapping=json.loads((folder/'mapping.json').read_text());decoded=json.loads((folder/'original-decode.json').read_text());report=json.loads((ROOT/'verification/biwn-sprite-decode-checks.json').read_text())
    evidence={'mapping':mapping,'code':[x for x in decoded['rows']if x['classification']=='decoded_instruction'],'verified_GPU_cases':report,'scope':'Separate originalGPUoverlay vsCdecoder. Read data inwatch isplaceholder, not measuredvalues. Not a gameframe or hardware proof.'}
    task=('Return JSON only under160words with zero_run_lengths:[min,max], repeat_run_lengths:[min,max], literal_run_lengths:[min,max], signed_origin_bits, literal_trailing_prefetch, output_word_bits, rebuilt_frame, unresolved. Read sourcecode and tabletargets. Note decoder immediates use hex: $18 means24, not18. Do not turn data-table bytes into executed instructions or invent a standardcompression name. Reviewer must check prior draft; add errors list. Same-model roles are correlated.')
    out=ROOT/'runs'/(lab.stamp()+'-game-gpu-sprite-review');out.mkdir();save(out/'protocol.json',{'task':task,'evidence':evidence,'roles':['analyst','reviewer'],'model':lab.CONFIG['models']['advertising'],'native_chat_history':False,'same_weights_correlated':True})
    prior=[]
    with (ROOT/'runs/.inference.lock').open('w')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        for role in ['analyst','reviewer']:
            result=lab.generate('advertising',lab.COMMON+'\nYour role: '+lab.ROLES['game'][role],json.dumps({'task':task,'evidence':evidence,'previous_draft':prior}),768);result['word_count']=len(result['text'].split());save(out/(role+'.json'),result)
            with (out/'prompts-and-responses.txt').open('a')as stream:stream.write(role.upper()+'\nREQUEST:\n'+json.dumps(result['request'],ensure_ascii=False,indent=2)+'\nRESPONSE:\n'+result['text']+'\n\n')
            prior.append({'role':role,'text':result['text'],'word_count':result['word_count']});print(role,result['seconds'],result['word_count'],flush=True)
    result={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'completed_pending_coordinator_review','directory':str(out),'roles':prior};save(out/'status.json',result);save(ROOT/'verification/biwn-gpu-sprite-local-review.json',result);print(out,flush=True)

if __name__=='__main__':main()
