"""Fresh installed advertising assistant lesson using preserved source evidence."""
import fcntl,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];RUNTIME=Path.home()/'.lmstudio/local-ai-lab';sys.path.insert(0,str(RUNTIME))
import chat_tools,lab,lmstudio
def save(p,value):p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def main():
    preset=ROOT/'presets/Advertising Assistant.preset.json';system=next(f['value']for f in json.loads(preset.read_text())['operation']['fields']if f['key']=='llm.prediction.systemPrompt')
    prompt='Using Lee & Koo (2016), prepare a short classroom example that distinguishes a measured variable from a manipulated variable. Include one learning objective, one student question, and one grading criterion. Cite the retrieved source excerpt and stay under100words.'
    repair='--repair-citation'in sys.argv
    suffix='advertising-measured-manipulated-lesson-citation-repair'if repair else'advertising-measured-manipulated-lesson'
    original_path=None
    if repair:
        original_path=Path(json.loads((ROOT/'verification/advertising-measured-manipulated-lesson-current.json').read_text())['directory'])/'protocol.json'
        previous=json.loads(original_path.read_text())
        answer='\n'.join(b['text']for e in previous['events']if e['role']=='assistant'for b in e['content']if b['type']=='text'and b['text'])
        prompt+=' Your earlier answer was: '+answer+' Check the cited source page numbers again and return the corrected lesson. Identify PDF pages explicitly, rather than ambiguous journal pagination.'
    out=ROOT/'verification'/suffix/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    record=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='running',interface='localhost SDK with installed advertising preset/tools, not nativeChat',model='advertising-scholar',system=system,user=prompt,preset_sha256=lab.sha(preset),installed_tool_source_sha256=lab.sha(RUNTIME/'chat_tools.py'),config={'temperature':0.2,'maxTokens':384},events=[],prior_protocol=str(original_path)if original_path else None)
    save(out/'protocol.json',record);print(out,flush=True)
    try:
        with(ROOT/'runs/.inference.lock').open('w')as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True));assert len(models)==1 and models[0]['identifier']=='advertising-scholar'and models[0]['status']=='idle'and models[0]['queued']==0 and models[0]['contextLength']==32768
            chat=lmstudio.Chat(system);chat.add_user_message(prompt)
            def message(value):record['events'].append(value.to_dict());save(out/'protocol.json',record)
            result=lmstudio.llm('advertising-scholar').act(chat,[chat_tools.search_references],max_prediction_rounds=2,max_parallel_tool_calls=1,config=lmstudio.LlmPredictionConfig.from_dict(record['config']),on_message=message)
            record.update(status='completed_pending_coordinator_review',rounds=result.rounds,SDK_reported_seconds=result.total_time_seconds);save(out/'protocol.json',record)
        (out/'prompts-and-responses.txt').write_text('ADVERTISING LESSON — LOCAL SDK, NOT NATIVECHAT\n\nSYSTEM:\n'+system+'\n\nUSER:\n'+prompt+'\n\nEXACTMESSAGES:\n'+json.dumps(record['events'],ensure_ascii=False,indent=2)+'\n')
        save(ROOT/'verification'/(suffix+'-current.json'),dict(directory=str(out),status=record['status']));print(record['SDK_reported_seconds'],flush=True)
    except Exception as error:record.update(status='terminal_failed',error=repr(error));save(out/'protocol.json',record);raise
if __name__=='__main__':main()
