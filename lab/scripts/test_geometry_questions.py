"""Ordinary local questions using the installed assistant's scoped evidence."""
from datetime import datetime,timezone
import fcntl,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import chat_tools,lab,lmstudio
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 retry='--retry-outside' in sys.argv
 preset=ROOT/'presets/Game Assistant.preset.json';system=next(f['value']for f in json.loads(preset.read_text())['operation']['fields']if f['key']=='llm.prediction.systemPrompt')
 prompts=['Are the five lower rectangle/tile/portal/region routines still scripted? What remains unfinished? Answer under65words.',
          'For geometry record word0x0400 shifted by6, do tile/region and portal code produce the same signed result? Answer under40words.',
          'In the outside-bounds predicate with incomingD0=0xabcd1234, what is fullD0 when inside, outside at the final Z-upper test, and outside at the first X-lower test? Answer under45words.']
 if retry:prompts=prompts[2:]
 out=ROOT/('verification/easy-geometry-retry' if retry else 'verification/easy-geometry')/lab.stamp();out.mkdir(parents=True)
 record={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'running','model':'advertising-scholar','system':system,'preset_sha256':lab.sha(preset),'tool_source_sha256':lab.sha(ROOT/'chat_tools.py'),'interface':'localhost SDK, not nativeChat','max_prediction_rounds':2,'max_parallel_tool_calls':1,'config':{'temperature':0.2,'maxTokens':384},'questions':[]};save(out/'protocol.json',record);print(out,flush=True)
 with(ROOT/'runs/.inference.lock').open('w')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True));assert len(models)==1 and models[0]['identifier']=='advertising-scholar'and models[0]['contextLength']==32768
  for prompt in prompts:
   question={'user':prompt,'events':[]};record['questions'].append(question);chat=lmstudio.Chat(system);chat.add_user_message(prompt)
   def message(value):question['events'].append(value.to_dict());save(out/'protocol.json',record)
   result=lmstudio.llm('advertising-scholar').act(chat,[chat_tools.verify_68000_fixture,chat_tools.render_inventory_preview,chat_tools.project_evidence,chat_tools.inspect_boot,chat_tools.search_references],max_prediction_rounds=2,max_parallel_tool_calls=1,config=lmstudio.LlmPredictionConfig.from_dict(record['config']),on_message=message)
   question.update(rounds=result.rounds,SDK_reported_seconds=result.total_time_seconds);save(out/'protocol.json',record);print(result.rounds,result.total_time_seconds,flush=True)
 record.update(status='completed_pending_coordinator_review',completed_at=datetime.now(timezone.utc).isoformat());save(out/'protocol.json',record)
 (out/'prompts-and-responses.txt').write_text('SYSTEM:\n'+system+'\n\n'+'\n\n'.join('USER:\n'+q['user']+'\nMESSAGES:\n'+json.dumps(q['events'],ensure_ascii=False,indent=2)for q in record['questions'])+'\n')
 save(ROOT/('verification/easy-geometry-retry-current.json' if retry else 'verification/easy-geometry-current.json'),{'directory':str(out),'status':record['status']})
if __name__=='__main__':main()
