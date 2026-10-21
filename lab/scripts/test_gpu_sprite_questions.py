"""Two ordinary local questions test new GPU sprite words and exact run ranges."""
from datetime import datetime,timezone
import fcntl,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import chat_tools,lab,lmstudio
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')

def main():
    preset=ROOT/'presets/Game Assistant.preset.json';system=next(f['value']for f in json.loads(preset.read_text())['operation']['fields']if f['key']=='llm.prediction.systemPrompt')
    prompts=['What has changed in the Black Ice White Noise sprite work? Can our rebuilt code produce any image data now, and is the whole inventory screen rebuilt? Keep it under80words.', 'Which three sprite run-length ranges did the checked Black Ice White Noise decoder establish? Is it already rebuilding the entire inventory image? Keep it under60words.']
    out=ROOT/'verification/easy-GPU-sprite'/lab.stamp();out.mkdir(parents=True);record={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'running','model':'advertising-scholar','system':system,'preset_sha256':lab.sha(preset),'tool_source_sha256':lab.sha(ROOT/'chat_tools.py'),'interface':'localhost SDK, not nativeChat','max_prediction_rounds':2,'max_parallel_tool_calls':1,'config':{'temperature':0.2,'maxTokens':384},'questions':[]};save(out/'protocol.json',record);print(out,flush=True)
    with (ROOT/'runs/.inference.lock').open('w')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True));assert len(models)==1 and models[0]['identifier']=='advertising-scholar'and models[0]['contextLength']==32768
        for prompt in prompts:
            question={'user':prompt,'events':[]};record['questions'].append(question);chat=lmstudio.Chat(system);chat.add_user_message(prompt)
            def message(value):question['events'].append(value.to_dict());save(out/'protocol.json',record)
            result=lmstudio.llm('advertising-scholar').act(chat,[chat_tools.verify_68000_fixture,chat_tools.project_evidence,chat_tools.inspect_boot,chat_tools.search_references],max_prediction_rounds=2,max_parallel_tool_calls=1,config=lmstudio.LlmPredictionConfig.from_dict(record['config']),on_message=message)
            question.update(rounds=result.rounds,SDK_reported_seconds=result.total_time_seconds);save(out/'protocol.json',record);print(result.rounds,result.total_time_seconds,flush=True)
    record.update(status='completed_pending_coordinator_review',completed_at=datetime.now(timezone.utc).isoformat());save(out/'protocol.json',record);save(out/'prompts-and-responses.txt',record);save(ROOT/'verification/easy-GPU-sprite-current.json',{'directory':str(out),'status':record['status']})

if __name__=='__main__':main()
