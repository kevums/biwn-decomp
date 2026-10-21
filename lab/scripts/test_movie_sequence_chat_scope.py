"""Natural questions on the everyday model after compact current-status routing.

No model swaps, preset edits, raw-output cleanup or native Chat claim. Exact
messages remain in the audit; separate roles use the same model weights.
"""
import fcntl
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RUNTIME=Path.home()/'.lmstudio/local-ai-lab'
sys.path.insert(0,str(RUNTIME))
import chat_tools
import lab
import lmstudio

save=lambda p,v:p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')


def preset(name):
    data=json.loads((ROOT/'presets'/f'{name}.preset.json').read_text())
    return next(f['value'] for f in data['operation']['fields'] if f['key']=='llm.prediction.systemPrompt')


def main():
    out=ROOT/'verification/easy-movie-sequence-scope'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    questions=[dict(role='game_assistant',system=preset('Game Assistant'),maxTokens=1024,
        user='Can I watch any reconstructed Black Ice White Noise videos now? What is verified, and is the game able to play these movies itself yet? Keep it under 150 words.')]
    tools=[chat_tools.verify_68000_fixture,chat_tools.render_inventory_preview,chat_tools.render_animation_preview,
        chat_tools.project_evidence,chat_tools.inspect_boot,chat_tools.search_references]
    record=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='running',model='advertising-scholar',
        interface='LM Studio SDK with installed tools, not native Chat',questions=questions,results=[],
        config=dict(temperature=0.2),budgets_from_configured_presets=True,max_prediction_rounds=2,max_parallel_tool_calls=1,
        tool_descriptions={t.__name__:t.__doc__ for t in tools},
        installed_tools_sha256=lab.sha(RUNTIME/'chat_tools.py'),new_training=False,model_defaults_changed=False,
        independent_model_verification=False)
    save(out/'protocol.json',record);print(out,flush=True)
    try:
        with (ROOT/'runs/.inference.lock').open('w') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],text=True))
            assert len(models)==1 and models[0]['identifier']=='advertising-scholar' and models[0]['contextLength']==32768
            assert models[0]['status']=='idle' and models[0]['parallel']==1 and models[0]['queued']==0
            record['initial_model_state']=models;save(out/'protocol.json',record)
            for question in questions:
                item=dict(role=question['role'],events=[],prediction_stats=[]);record['results'].append(item)
                def message(value):
                    item['events'].append(value.to_dict());save(out/'protocol.json',record)
                def prediction_completed(value):
                    item['prediction_stats'].append(dict(round_index=value.round_index,stats=value.stats.to_dict(),prediction_config=value.prediction_config.to_dict()))
                    save(out/'protocol.json',record)
                history=lmstudio.Chat(question['system']);history.add_user_message(question['user'])
                result=lmstudio.llm('advertising-scholar').act(history,tools,max_prediction_rounds=2,
                    max_parallel_tool_calls=1,config=lmstudio.LlmPredictionConfig.from_dict({**record['config'],'maxTokens':question['maxTokens']}),on_message=message,on_prediction_completed=prediction_completed)
                messages=[''.join(c.get('text','') for c in e['content'] if c['type']=='text')
                    for e in item['events'] if e['role']=='assistant' and not any(c['type']=='toolCallRequest' for c in e['content'])]
                answer='\n'.join(messages)
                item.update(answer=answer,words=len(answer.split()),rounds=result.rounds,
                    seconds=result.total_time_seconds,quality_flags=lab.response_quality_flags(answer),semantic_review='pending coordinator source review')
                if item['prediction_stats'][-1]['stats']['stopReason'] not in ['eosFound','stopStringFound']:
                    item['quality_flags'].append('incomplete_prediction_'+item['prediction_stats'][-1]['stats']['stopReason'])
                save(out/'protocol.json',record)
                print(json.dumps({k:item[k] for k in ['role','words','seconds','quality_flags']}),flush=True)
        record.update(status='completed_pending_coordinator_review',completed_at=datetime.now(timezone.utc).isoformat())
        save(out/'protocol.json',record)
        (out/'prompts-and-responses.txt').write_text('LOCAL PLAIN QUESTIONS — SDK, NOT NATIVE CHAT\n\n'+
            '\n\n'.join('ROLE: '+q['role']+'\nSYSTEM:\n'+q['system']+'\nUSER:\n'+q['user']+
                '\nEXACT MESSAGES:\n'+json.dumps(r['events'],indent=2,ensure_ascii=False)
                for q,r in zip(questions,record['results']))+'\n')
        save(ROOT/'verification/easy-movie-sequence-scope-pointer.json',dict(directory=str(out),status=record['status']))
    except Exception as error:
        record.update(status='terminal_failed',error=repr(error));save(out/'protocol.json',record);raise


if __name__=='__main__':main()
