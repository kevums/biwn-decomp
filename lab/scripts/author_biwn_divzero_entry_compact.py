"""Bounded correction of the failed metadata-heavy local author request."""
import fcntl,json,os,sys,time
from datetime import datetime,timezone
from pathlib import Path
from pydantic import BaseModel,ConfigDict
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import assistant_chat,lmstudio
from run_biwn_native_fast_gameplay_route import sha,save
from author_biwn_divzero_entry import SYSTEM
class CodeOnly(BaseModel):
    model_config=ConfigDict(extra='forbid')
    source:str

def main():
    priorp=ROOT/'verification/divzero-Code-Author-current.json';prior=json.loads(priorp.read_text());request=Path(prior['directory'])/'request.json';old=json.loads(request.read_text());data=json.loads(old['user'])
    user=json.dumps(dict(task=data['task'],feedback='The previous reply copied the task into assumptions and exhausted the output limit before valid code. Return ONLY the source field. No assumptions field, task restatement, long comments or tests. About35lines is sufficient.',types='struct biwn_task_cpu { uint32_t registers[16], pc, usp, ssp; uint16_t sr; }; bus fields read32(context,address,uint32_t*), write16(context,address,uint16_t), write32(context,address,uint32_t) return0success; context is void*. Include biwn_scheduler.h for these exact definitions.'))
    out=ROOT/'runs'/('divzero-Code-Author-compact-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir(parents=True)
    (out/'runner-as-run.py').write_bytes(Path(__file__).read_bytes());save(out/'request.json',dict(system=SYSTEM,user=user,tools=[]))
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),role='Code Author compact revision',same_weights_as_other_roles=True,independent_review=False,native_Chat_verified=False,new_training=False,
        prior_rejected_protocol=str(Path(prior['directory'])/'protocol.json'),source_sha256={str(p):sha(p)for p in [out/'runner-as-run.py',out/'request.json',priorp,request]})
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/divzero-Code-Author-compact-current.json',state)
    mark();print(out,flush=True)
    try:
        with (ROOT/'runs/.inference.lock').open('a')as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);identifier=assistant_chat.ensure_model('game');model=lmstudio.llm(identifier)
            chat=lmstudio.Chat(SYSTEM);chat.add_user_message(user);tokens=model.count_tokens(model.apply_prompt_template(chat));assert tokens+1800+128<=model.get_context_length()
            state.update(status='local_compact_divzero_Code_Author_generating',model_identifier=identifier,input_tokens=tokens);mark();start=time.monotonic()
            result=model.respond(chat,response_format=CodeOnly,config={'temperature':0,'maxTokens':1800,'contextOverflowPolicy':'stopAtLimit'});seconds=time.monotonic()-start
        save(out/'response.json',dict(text=result.content,seconds=seconds,stats=result.stats.to_dict()));parsed=CodeOnly.model_validate_json(result.content)
        source=out/'biwn_divzero_entry.c';source.write_text(parsed.source)
        state.update(status='terminal_compact_divzero_C_pending_review',source=str(source),source_text_sha256=sha(source),seconds=seconds,compiled=False,accepted=False);mark();print(parsed.source,flush=True)
    except BaseException as error:state.update(status='terminal_compact_divzero_author_failed',error=repr(error));mark();raise
    finally:(out/'prompts-and-responses.txt').write_text('LOCAL SDK CODE AUTHOR; COMPACT REPAIR\nSYSTEM\n'+SYSTEM+'\nUSER\n'+user+'\nSOURCE\n'+(Path(state['source']).read_text()if state.get('source')else''))

if __name__=='__main__':main()
