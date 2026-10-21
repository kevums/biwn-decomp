"""Exercise the saved Game Assistant prompt with the actual read-only evidence tool."""
import fcntl
import json
import sys
from datetime import datetime,timezone
from pathlib import Path
import lmstudio
ROOT=Path(__file__).resolve().parents[1]
RUNTIME=Path.home()/'.lmstudio/local-ai-lab'
sys.path.insert(0,str(RUNTIME))
import chat_tools
import lab
def main():
    out=ROOT/'runs/six-function-readable-scene-answer'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    preset=lab.load_native_preset('game')
    system=next(x['value']for x in preset['operation']['fields']if x['key']=='llm.prediction.systemPrompt')
    user='What is the latest readable BIWN scene setup code we have actually checked? In under140words give the linked-function count, checks, remaining simulated helpers, and distinguish local-model work from coordinator corrections. Does this prove natural gameplay or newly trained weights?'
    record=dict(status='running',directory=str(out),interface='Local LM Studio SDK with saved Game Assistant prompt and installed evidence tool; not native Chat',system=system,user=user,events=[],new_training=False,native_Chat_verified=False)
    def save():(out/'protocol.json').write_text(json.dumps(record,indent=2)+'\n')
    def message(value):record['events'].append(value.to_dict());save()
    chat=lmstudio.Chat(system);chat.add_user_message(user);save()
    with (ROOT/'runs/.inference.lock').open('w')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        response=lmstudio.llm(lab.CONFIG['models']['game']['identifier']).act(chat,[chat_tools.project_evidence],max_prediction_rounds=3,max_parallel_tool_calls=1,config=lmstudio.LlmPredictionConfig.from_dict(dict(temperature=0,maxTokens=650)),on_message=message)
    texts=[''.join(c.get('text','')for c in event['content']if c['type']=='text')for event in record['events']if event['role']=='assistant'and not any(c['type']=='toolCallRequest'for c in event['content'])]
    answer='\n'.join(texts);record.update(status='completed_pending_semantic_review',answer=answer,quality_flags=lab.response_quality_flags(answer),seconds=response.total_time_seconds,rounds=response.rounds)
    save();(out/'prompts-and-responses.txt').write_text('SYSTEM\n'+system+'\nUSER\n'+user+'\nMESSAGES\n'+json.dumps(record['events'],indent=2)+'\n')
    (ROOT/'verification/local-six-function-scene-answer-current.json').write_text(json.dumps(dict(status=record['status'],directory=str(out),seconds=record['seconds'],native_Chat_verified=False),indent=2)+'\n');print(answer,flush=True);print('seconds',record['seconds'],'quality flags',record['quality_flags'],flush=True)
if __name__=='__main__':main()
