"""Ordinary local actor scheduling scope question."""
from datetime import datetime,timezone
import fcntl,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import chat_tools,lab,lmstudio
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 preset=ROOT/'presets/Game Assistant.preset.json';system=next(f['value']for f in json.loads(preset.read_text())['operation']['fields']if f['key']=='llm.prediction.systemPrompt')
 prompts=['If a collision helper returns 0x00010000, what does the movement caller roll back and what does it retain? Are the collision helpers implemented, and does the new movement test run actors in the 21-context startup? Use current evidence; under 100 words.']
 out=ROOT/'verification/easy-actor-movement'/lab.stamp();out.mkdir(parents=True)
 record={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'running','model':'advertising-scholar','system':system,'preset_sha256':lab.sha(preset),'tool_source_sha256':lab.sha(ROOT/'chat_tools.py'),'interface':'localhost SDK, not nativeChat','max_prediction_rounds':2,'max_parallel_tool_calls':1,'config':{'temperature':0.2,'maxTokens':384},'questions':[]};save(out/'protocol.json',record);print(out,flush=True)
 with(ROOT/'runs/.inference.lock').open('w')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True));assert len(models)==1 and models[0]['identifier']=='advertising-scholar'and models[0]['contextLength']==32768
  for prompt in prompts:
   question={'user':prompt,'events':[]};record['questions'].append(question);chat=lmstudio.Chat(system);chat.add_user_message(prompt)
   def message(value):question['events'].append(value.to_dict());save(out/'protocol.json',record)
   result=lmstudio.llm('advertising-scholar').act(chat,[chat_tools.verify_68000_fixture,chat_tools.render_inventory_preview,chat_tools.render_animation_preview,chat_tools.project_evidence,chat_tools.inspect_boot,chat_tools.search_references],max_prediction_rounds=2,max_parallel_tool_calls=1,config=lmstudio.LlmPredictionConfig.from_dict(record['config']),on_message=message)
   question.update(rounds=result.rounds,SDK_reported_seconds=result.total_time_seconds);save(out/'protocol.json',record);print(result.rounds,result.total_time_seconds,flush=True)
 record.update(status='completed_pending_coordinator_review',completed_at=datetime.now(timezone.utc).isoformat());save(out/'protocol.json',record)
 (out/'prompts-and-responses.txt').write_text('SYSTEM:\n'+system+'\n\n'+'\n\n'.join('USER:\n'+q['user']+'\nMESSAGES:\n'+json.dumps(q['events'],ensure_ascii=False,indent=2)for q in record['questions'])+'\n');save(ROOT/'verification/easy-actor-movement-current.json',{'directory':str(out),'status':record['status']})
if __name__=='__main__':main()
