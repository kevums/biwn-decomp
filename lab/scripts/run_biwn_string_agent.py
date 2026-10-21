"""Local coordinator uses actual installed MCP to recover/check the supported string helper."""
import fcntl,json,os,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import assistant_chat,lab,lmstudio
from string_mcp_bridge import StringBridge

def main():
    folder=ROOT/'runs'/('string-agent-'+lab.stamp());folder.mkdir()
    preset=Path.home()/'.lmstudio/config-presets/BIWN String Worker.preset.json'
    system=next(f['value']for f in json.loads(preset.read_text())['operation']['fields']if f['key']=='llm.prediction.systemPrompt')
    user='Recover the supported BIWN string helper and give me the checked C source path and the actual verification scope.'
    state=dict(status='prepared',pid=os.getpid(),directory=str(folder),system=system,user=user,calls=[],messages=[],native_Chat_verified=False,new_training=False,local_model_authored_C=False)
    def save():
        (folder/'protocol.json').write_text(json.dumps(state,indent=2)+'\n');(ROOT/'verification/native-string-agent-current.json').write_text(json.dumps(state,indent=2)+'\n')
    def message(m):
        state['messages'].append(m.to_dict());save()
    save();print('Exact prompts/responses: '+str(folder)+'\nSYSTEM\n'+system+'\nUSER\n'+user,flush=True)
    try:
        with(ROOT/'runs/.inference.lock').open('a')as lock:
            try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:
                state['status']='model_busy_no_inference_started';save();print('Local model busy; no duplicate request started.',flush=True);return 3
            assistant_chat.ensure_model('game');model=lmstudio.llm(lab.CONFIG['models']['game']['identifier'])
            with StringBridge()as bridge:
                state['MCP_connection']=bridge.metadata
                def get_biwn_string_task()->dict:
                    """Fetch the supported complete BIWN string helper instruction facts and ABI before recovery."""
                    print('Analyst → MCP: instruction facts and ABI',flush=True);result=bridge.call('get_biwn_string_task');state['calls'].append(dict(name='get_biwn_string_task',result=result));save();return result
                def lift_biwn_string_task()->dict:
                    """Generate complete C deterministically from the facts and reuse an exact bound passing CPU receipt. No fresh CPU test; source is tool-generated, not LLM-authored."""
                    print('Recovery tool → MCP: re-lower and check exact certificate; prior CPU receipt reused',flush=True);result=bridge.call('lift_biwn_string_task');state['calls'].append(dict(name='lift_biwn_string_task',result=result));save();return result
                chat=lmstudio.Chat(system);chat.add_user_message(user);state['status']='local_coordinator_running';save();start=time.monotonic()
                result=model.act(chat,[get_biwn_string_task,lift_biwn_string_task],max_prediction_rounds=4,max_parallel_tool_calls=1,config={'temperature':0,'maxTokens':1000,'contextOverflowPolicy':'stopAtLimit'},on_message=message)
                answer='\n'.join(''.join(p.get('text','')for p in m['content']if p['type']=='text')for m in state['messages']if m['role']=='assistant'and not any(p['type']=='toolCallRequest'for p in m['content']))
                lifted=next((call['result']for call in state['calls']if call['name']=='lift_biwn_string_task'and call['result'].get('verified')),None)
                flags=[]
                if not lifted:flags.append('no_verified_tool_result')
                if lifted and lifted['source']not in answer:flags.append('exact_source_path_missing')
                if len(answer.split())>110:flags.append('requested_word_limit_exceeded')
                if not answer.strip()or'<tool_call>'in answer:flags.append('missing_or_unexecuted_final')
                state.update(status='terminal_string_agent_saved',seconds=time.monotonic()-start,rounds=result.rounds,answer=answer,answer_review_flags=flags,expected_tool_sequence=[x['name']for x in state['calls']]==['get_biwn_string_task','lift_biwn_string_task'],source_accepted=bool(lifted));save();print(answer,flush=True)
    except BaseException as error:
        state.update(status='terminal_failed',error=repr(error));save();raise
    finally:
        (folder/'prompts-and-responses.txt').write_text('SYSTEM\n'+system+'\nUSER\n'+user+'\nMESSAGES\n'+json.dumps(state['messages'],indent=2)+'\nTOOLS\n'+json.dumps(state['calls'],indent=2)+'\nRAW FINAL\n'+state.get('answer',''))
    return 4 if state['answer_review_flags']else 0

if __name__=='__main__':sys.exit(main()or 0)
