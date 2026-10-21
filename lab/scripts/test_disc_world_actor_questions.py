"""Ordinary local world/actor timing and signed-clock role review, SDK fallback."""
from datetime import datetime,timezone
import argparse,fcntl,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import chat_tools,lab,lmstudio
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--question-limit',type=int);options=parser.parse_args()
    preset=ROOT/'presets/Game Assistant.preset.json';system=next(f['value']for f in json.loads(preset.read_text())['operation']['fields']if f['key']=='llm.prediction.systemPrompt')
    questions=["Does the world now supply the actors' movement time, or am I still feeding it directly? What is still mocked in that test? Use current evidence; under 100 words.",
               "Analyst: copy the checked clock-zero/previous-one timestep result and explain whether all time steps are clamped to 0..30. Reviewer: check that interpretation and state which inputs and world-helper limitations remain. These are roles using the same local model, not independent verification. Use current evidence; under 110 words total."]
    if options.question_limit:questions=questions[:options.question_limit]
    out=ROOT/'verification/easy-disc-world-actors'/lab.stamp();out.mkdir(parents=True)
    record={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'running','model':'advertising-scholar','system':system,'preset_sha256':lab.sha(preset),'tool_source_sha256':lab.sha(ROOT/'chat_tools.py'),
            'interface':'LM Studio localhost SDK fallback, not nativeChat; CUA inspection timed out twice','max_prediction_rounds':2,'max_parallel_tool_calls':1,'config':{'temperature':0.2,'maxTokens':384},'questions':[]}
    save(out/'protocol.json',record);print(out,flush=True)
    with(ROOT/'runs/.inference.lock').open('w')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True));assert len(models)==1 and models[0]['identifier']=='advertising-scholar'and models[0]['status']=='idle'and models[0]['contextLength']==32768
        for prompt in questions:
            question={'user':prompt,'events':[]};record['questions'].append(question);chat=lmstudio.Chat(system);chat.add_user_message(prompt)
            def message(value):question['events'].append(value.to_dict());save(out/'protocol.json',record)
            result=lmstudio.llm('advertising-scholar').act(chat,[chat_tools.verify_68000_fixture,chat_tools.render_inventory_preview,chat_tools.render_animation_preview,chat_tools.project_evidence,chat_tools.inspect_boot,chat_tools.search_references],max_prediction_rounds=2,max_parallel_tool_calls=1,config=lmstudio.LlmPredictionConfig.from_dict(record['config']),on_message=message)
            question.update(rounds=result.rounds,SDK_reported_seconds=result.total_time_seconds);save(out/'protocol.json',record);print(result.rounds,result.total_time_seconds,flush=True)
    record.update(status='completed_pending_coordinator_review',completed_at=datetime.now(timezone.utc).isoformat());save(out/'protocol.json',record)
    save(ROOT/'verification/easy-disc-world-actors-current.json',{'directory':str(out),'status':record['status']})
    (out/'prompts-and-responses.txt').write_text('SYSTEM\n'+system+'\n\n'+json.dumps(record['questions'],ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
