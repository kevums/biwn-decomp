"""Local Coordinator asks fixed verified compiler tools; exact messages saved."""
import fcntl,json,os,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import assistant_chat,lab,lmstudio
from ccr_mcp_bridge import CCRBridge


def main():
    out=ROOT/'runs'/('verified-optimizer-'+lab.stamp());out.mkdir()
    preset=Path.home()/'.lmstudio/config-presets/BIWN Verified Optimizer.preset.json'
    system=next(f['value']for f in json.loads(preset.read_text())['operation']['fields']if f['key']=='llm.prediction.systemPrompt')
    user='Get the checked BIWN string-helper optimization and report its exact C path, test/cost scope and how it was generated.'
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),system=system,user=user,role='Coordinator',calls=[],messages=[],
               native_Chat_verified=False,new_training=False,local_model_authored_C=False)
    def save():
        (out/'protocol.json').write_text(json.dumps(state,indent=2)+'\n');(ROOT/'verification/native-ccr-agent-current.json').write_text(json.dumps(state,indent=2)+'\n')
    def message(value):state['messages'].append(value.to_dict());save()
    save();print('Exact prompts/responses: '+str(out)+'\nSYSTEM\n'+system+'\nUSER\n'+user,flush=True)
    try:
        with(ROOT/'runs/.inference.lock').open('a')as lock:
            try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:
                state.update(status='terminal_model_busy_no_duplicate_inference',model_inference_invoked=False);save();return 3
            identifier=assistant_chat.ensure_model('game');state['model_identifier']=identifier
            with CCRBridge()as bridge:
                state['MCP_connection']=bridge.metadata
                def get_biwn_string_optimization_status()->dict:
                    """Read current fixed string optimization and the exact checked CPU/cost scope."""
                    print('Coordinator → MCP: checked optimization status',flush=True);result=bridge.call('get_biwn_string_optimization_status');state['calls'].append(dict(name='get_biwn_string_optimization_status',result=result));save();return result
                def lower_checked_biwn_string_optimization()->dict:
                    """Re-lower the fixed string helper deterministically and reuse exact bound passing CPU receipts. No new build/test/training and no model-authored C."""
                    print('Compiler tool → MCP: exact C re-lowering and prior receipt reuse',flush=True);result=bridge.call('lower_checked_biwn_string_optimization');state['calls'].append(dict(name='lower_checked_biwn_string_optimization',result=result));save();return result
                state['status']='local_Coordinator_using_compiler_tools';save();start=time.monotonic()
                chat=lmstudio.Chat(system);chat.add_user_message(user)
                result=lmstudio.llm(identifier).act(chat,[get_biwn_string_optimization_status,lower_checked_biwn_string_optimization],
                    max_prediction_rounds=4,max_parallel_tool_calls=1,config={'temperature':0,'maxTokens':900,'contextOverflowPolicy':'stopAtLimit'},on_message=message)
                answer='\n'.join(''.join(p.get('text','')for p in m['content']if p['type']=='text')for m in state['messages']if m['role']=='assistant'and not any(p['type']=='toolCallRequest'for p in m['content']))
                lowered=next((c['result']for c in state['calls']if c['name']=='lower_checked_biwn_string_optimization'),{})
                flags=[]
                if lowered.get('status')!='relowered_exact_checked_CCR_string_source':flags.append('no_verified_compiler_result')
                if not lowered.get('source')or lowered['source']not in answer:flags.append('exact_source_path_missing')
                if len(answer.split())>=150:flags.append('word_limit_exceeded')
                if not answer.strip()or'<tool_call>'in answer:flags.append('missing_or_unexecuted_answer')
                state.update(status='terminal_verified_optimizer_output_pending_review',answer=answer,answer_review_flags=flags,
                    expected_tool_sequence=[c['name']for c in state['calls']]==['get_biwn_string_optimization_status','lower_checked_biwn_string_optimization'],
                    seconds=time.monotonic()-start,rounds=result.rounds,prior_CPU_receipts_reused=True);save();print(answer,flush=True);print('Seconds',state['seconds'],'calls',len(state['calls']),flags,flush=True)
    except BaseException as error:state.update(status='terminal_failed',error=repr(error));save();raise
    finally:
        (out/'prompts-and-responses.txt').write_text('LOCAL SDK COORDINATOR; NOT A NEW NATIVE CHAT\nSYSTEM\n'+system+'\nUSER\n'+user+
            '\nMESSAGES\n'+json.dumps(state['messages'],indent=2)+'\nACTUAL MCP RESULTS\n'+json.dumps(state['calls'],indent=2)+'\nFINAL\n'+state.get('answer',''))
    return 4 if state.get('answer_review_flags')else 0


if __name__=='__main__':sys.exit(main()or 0)
