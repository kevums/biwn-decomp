"""Actual fresh local roles review three original CPU GPU-command routines."""
from pathlib import Path
import fcntl,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab,binary_tools
s=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);p=s/'nextstage-68000-candidate.bin';b=p.read_bytes();assert lab.sha(p)=='52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453'
ins,decoder=binary_tools.m68k_instructions(b[0xe098-0x4000:0xe148-0x4000],0xe098)
evidence={'candidate_sha256':lab.sha(p),'range':'[0xe098,0xe148)','bytes':176,'instructions':ins,'decoder':decoder,'function_entry_candidates':['0xe098','0xe0a6','0xe0f2'],'limits':'Static candidate instructions. No original names or proof of GPU operation/command meaning. Coordinator is separately preparing synthetic CPU/bus comparisons; no completed execution result supplied here.'}
task='In under200words, review the exact three routines and propose a portable callback-based read32/write32 translation contract. Preserve every read/write order, source-memory loads at49c18/49c1c, and exact command words4d80/6ae0. e098 waits forF03200==0; submit routines wait forF03204!=their command, then call e098 again. A nonzero unequal acknowledgement is allowed. Do not call the commands rendering/audio. A finite read budget/callback failure would be an added host guard, not an original timeout. Do not infer D0 return values or device completion from RTS. Explain what comparison against originalCPU on scripted bus replies can and cannot validate. Do not claim execution.'
out=ROOT/'runs'/f'{lab.stamp()}-game-gpu-command-review';out.mkdir();(out/'protocol.json').write_text(json.dumps({'task':task,'evidence':evidence,'model':lab.CONFIG['models']['advertising'],'roles':['analyst','restorer','reviewer'],'same_weights_correlated':True,'native_chat_history':False},indent=2)+'\n')
previous=[]
with (ROOT/'runs/.inference.lock').open('w') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 for role in ['analyst','restorer','reviewer']:
  x=lab.generate('advertising',lab.COMMON+'\nYour role: '+lab.ROLES['game'][role],json.dumps({'current_task':task,'source_evidence':evidence,'previous_drafts':previous},ensure_ascii=False),768);x['word_count']=len(x['text'].split());(out/(role+'.json')).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
  with (out/'prompts-and-responses.txt').open('a') as f:f.write(role.upper()+'\nREQUEST:\n'+json.dumps(x['request'],ensure_ascii=False,indent=2)+'\nRESPONSE:\n'+x['text']+'\n\n')
  previous.append({'role':role,'text':x['text']});print(role,x['seconds'],x['word_count'],flush=True)
status={'directory':str(out),'status':'completed_pending_coordinator_review','roles':previous};(out/'status.json').write_text(json.dumps(status,indent=2)+'\n');(ROOT/'verification/biwn-gpu-command-local-review.json').write_text(json.dumps(status,indent=2)+'\n');print(out,flush=True)
