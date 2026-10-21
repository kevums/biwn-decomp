"""Two scoped local inference samples; installed tools, no native Chat claim."""
import fcntl,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];RUNTIME=Path.home()/'.lmstudio/local-ai-lab'
sys.path.insert(0,str(RUNTIME));import chat_tools,lab,lmstudio
def save(p,value):p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def main():
    preset=ROOT/'presets/Game Assistant.preset.json';system=next(f['value']for f in json.loads(preset.read_text())['operation']['fields']if f['key']=='llm.prediction.systemPrompt')
    prompts=['What changed with the next GPU projection program? Is it already part of the live renderer, and can we play the game? Keep the answer under70words.',
             'Use Analyst and Reviewer roles to assess the latest projection test. Does returning from52E0 mean10A684must be zero, and can we count it as another fully verified live component? Keep the combined answer under100words.']
    out=ROOT/'verification/easy-gpu-projection'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    tools=[chat_tools.verify_68000_fixture,chat_tools.render_inventory_preview,chat_tools.render_animation_preview,chat_tools.project_evidence,chat_tools.inspect_boot,chat_tools.search_references]
    record=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='running',interface='localhost SDK with installed runtime tools, not nativeChat',model='advertising-scholar',system=system,preset_sha256=lab.sha(preset),installed_tool_source_sha256=lab.sha(RUNTIME/'chat_tools.py'),max_prediction_rounds=2,max_parallel_tool_calls=1,config={'temperature':0.2,'maxTokens':384},questions=[])
    save(out/'protocol.json',record);print(out,flush=True)
    try:
        with(ROOT/'runs/.inference.lock').open('w')as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True))
            assert len(models)==1 and models[0]['identifier']=='advertising-scholar'and models[0]['status']=='idle'and models[0]['contextLength']==32768 and models[0]['queued']==0,models
            for prompt in prompts:
                question=dict(user=prompt,events=[]);record['questions'].append(question);chat=lmstudio.Chat(system);chat.add_user_message(prompt)
                def message(value):question['events'].append(value.to_dict());save(out/'protocol.json',record)
                result=lmstudio.llm('advertising-scholar').act(chat,tools,max_prediction_rounds=2,max_parallel_tool_calls=1,config=lmstudio.LlmPredictionConfig.from_dict(record['config']),on_message=message)
                question.update(rounds=result.rounds,SDK_reported_seconds=result.total_time_seconds);save(out/'protocol.json',record);print(result.rounds,result.total_time_seconds,flush=True)
        record.update(status='completed_pending_coordinator_review',completed_at=datetime.now(timezone.utc).isoformat());save(out/'protocol.json',record)
        (out/'prompts-and-responses.txt').write_text('LOCAL SDK CHAT; NOT NATIVE CHAT\nOne27Bmodel, sequential Analyst/Reviewer roles; no independent agent verification.\n\nSYSTEM:\n'+system+'\n\n'+'\n\n'.join('USER:\n'+q['user']+'\nMESSAGES:\n'+json.dumps(q['events'],ensure_ascii=False,indent=2)for q in record['questions'])+'\n')
        save(ROOT/'verification/easy-gpu-projection-current.json',dict(directory=str(out),status=record['status']))
    except Exception as error:record.update(status='terminal_failed',error=repr(error));save(out/'protocol.json',record);raise
if __name__=='__main__':main()
