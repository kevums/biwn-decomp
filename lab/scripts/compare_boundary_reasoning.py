"""Two fresh source-reading contracts, same loaded weights, off versus low."""
import argparse,fcntl,json,sys,urllib.request
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab

def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--retry-low',action='store_true');args=parser.parse_args();modes=['low'] if args.retry_low else ['off','low'];budget=4096 if args.retry_low else 1536
 with urllib.request.urlopen('http://127.0.0.1:1234/api/v1/models')as response:models=json.load(response)
 model=next(m for m in models['models']if m['key']=='local/advertising-qwen38');assert 'low'in model['capabilities']['reasoning']['allowed_options']
 source=ROOT/'projects/black-ice-white-noise/restoration';evidence={'portable_C':(source/'biwn_boundary_handlers.c').read_text(),'scope':'Nested helpers are scripted at their original call boundaries. Functions and fullD0 match1450originalCPUcases. Do not infer complete collision geometry/game.'}
 task='Return JSON only under130words, with keys unsupported_edge_D0_hex, neighbor_after_failed_check(integer), failed_check_D0_hex, matching_negative_flags_calls_target_helper(boolean), index_fffe_byte_offset(integer), cross64k_failed_or_zero_flags_D0_hex, full_geometry_reconstructed(boolean). Cases: (1) type1edge0x2345 and incomingD0=0xabcd1234; (2) type1edge0xffff, neighbor starts10, delta5, nested102c4 changes neighbor to100 then returns0x12340000; (3) type2record key matches and flags0x9000,target7; (4) type2indexword0xfffe; (5) type2first-record pointer0x9fffc, scan advances6to0xa0002, matches there with flags0. Do not treat lowword zero as full32bit zero. Previous cases are independent.'
 system=lab.COMMON+'\nUse the supplied C source to answer the exact typed contract. Analyst symbols, not original names. Return final JSON only.'
 out=ROOT/'verification'/('boundary-reasoning-retry' if args.retry_low else 'boundary-reasoning-comparison')/lab.stamp();out.mkdir(parents=True);save(out/'protocol.json',{'recorded_at':datetime.now(timezone.utc).isoformat(),'task':task,'evidence':evidence,'model_capabilities':model,'source_sha256':lab.sha(source/'biwn_boundary_handlers.c'),'reasoning_modes':modes,'same_weights_correlated':True,'fresh_contexts':True,'prior_drafts_shared':False,'max_output_tokens':budget,'native_Chat':False,'scope':'One response per mode; narrow probe, no training/default-preset change.'});print(out,flush=True)
 expected={'unsupported_edge_D0_hex':'0xabcd0000','neighbor_after_failed_check':95,'failed_check_D0_hex':'0x12340000','matching_negative_flags_calls_target_helper':True,'index_fffe_byte_offset':-12,'cross64k_failed_or_zero_flags_D0_hex':'0x90000','full_geometry_reconstructed':False};rows=[]
 with (ROOT/'runs/.inference.lock').open('w')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  for mode in modes:
   save(out/'status.json',{'status':'running','reasoning':mode});lab.CONFIG['models']['advertising']['reasoning']=mode
   result=lab.generate('advertising',system,json.dumps({'task':task,'evidence':evidence}),budget)
   save(out/(mode+'.json'),result)
   try:parsed=json.loads(result['text']);errors={key:{'expected':value,'received':parsed.get(key)}for key,value in expected.items()if parsed.get(key)!=value};parse_error=None
   except Exception as error:parsed=None;errors=None;parse_error=str(error)
   row={'reasoning':mode,'seconds':result['seconds'],'usage':result['usage'],'text':result['text'],'parsed':parsed,'contract_errors':errors,'parse_error':parse_error,'quality_flags':result['quality_flags'],'passed':errors=={}and parse_error is None};rows.append(row);save(out/'results.json',rows)
   with (out/'prompts-and-responses.txt').open('a')as f:f.write(mode.upper()+'\nREQUEST:\n'+json.dumps(result['request'],indent=2)+'\nFINAL RESPONSE:\n'+result['text']+'\n\n')
   print(mode,result['seconds'],'pass'if row['passed']else'fail',flush=True)
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'two_fresh_reasoning_modes_reviewed','directory':str(out),'results':rows,'expected_from_original_CPU_examples':expected,'scope':'One fresh response per mode, sameweights/prompt, no prior draft. Not independent verification or general ranking. No default or weight changes.'};save(out/'review.json',report);save(out/'status.json',{'status':'terminal','exit_code':0});save(ROOT/'verification'/('boundary-reasoning-retry-review.json' if args.retry_low else 'boundary-reasoning-comparison-review.json'),report);print(out,flush=True)
if __name__=='__main__':main()
