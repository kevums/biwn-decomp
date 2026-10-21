"""Ordinary local question checks current drawing progress and graphics limits."""
from datetime import datetime,timezone
import fcntl,json
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import chat_tools,lab,lmstudio


def main():
    preset=ROOT/'presets/Game Assistant.preset.json';doc=json.loads(preset.read_text());system=next(f['value']for f in doc['operation']['fields']if f['key']=='llm.prediction.systemPrompt')
    prompt='How far have we got with Black Ice White Noise inventory drawing? Is the rebuilt graphics working yet? Keep it under80words.'
    out=ROOT/'verification/easy-inventory-drawing'/lab.stamp();out.mkdir(parents=True)
    record={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'running','model':'advertising-scholar','system':system,'user':prompt,
            'config':{'temperature':0.2,'maxTokens':384},'max_prediction_rounds':2,'events':[],
            'interface':'LM Studio localhost SDK; not native Chat messages','preset_sha256':lab.sha(preset),'binary_tools_sha256':lab.sha(ROOT/'binary_tools.py')}
    def save():(out/'protocol.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    save();print(out,flush=True)
    with (ROOT/'runs/.inference.lock').open('w')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True));assert len(models)==1 and models[0]['identifier']=='advertising-scholar'and models[0]['contextLength']==32768
        chat=lmstudio.Chat(system);chat.add_user_message(prompt)
        def message(value):record['events'].append(value.to_dict());save()
        result=lmstudio.llm('advertising-scholar').act(chat,[chat_tools.verify_68000_fixture,chat_tools.project_evidence,chat_tools.inspect_boot,chat_tools.search_references],
                  max_prediction_rounds=2,max_parallel_tool_calls=1,config=lmstudio.LlmPredictionConfig.from_dict(record['config']),on_message=message)
        record.update(status='completed_pending_coordinator_review',completed_at=datetime.now(timezone.utc).isoformat(),rounds=result.rounds,SDK_reported_seconds=result.total_time_seconds);save()
    (out/'prompts-and-responses.txt').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    (ROOT/'verification/easy-inventory-drawing-current.json').write_text(json.dumps({'directory':str(out),'status':record['status']},indent=2)+'\n');print(json.dumps({'rounds':result.rounds,'seconds':result.total_time_seconds}),flush=True)


if __name__=='__main__':main()
