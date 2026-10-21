"""Local model chooses a checked-frame tool; fresh installed MCP returns PNG."""
import asyncio,base64,fcntl,hashlib,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from typing import Literal
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import chat_tools,lab,lmstudio
RT=Path.home()/'.lmstudio/local-ai-lab'

def main():
    out=ROOT/'verification/easy-checked-actor-preview'/lab.stamp();out.mkdir(parents=True);print(out,flush=True)
    preset=lab.load_native_preset('game');system=next(f['value']for f in preset['operation']['fields']if f['key']=='llm.prediction.systemPrompt')
    prompt='Show checked actor B movement at source update 32.'
    data=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='running',model='advertising-scholar',system=system,user=prompt,events=[],MCP_calls=[],native_Chat_verified=False,new_training=False,interface='SDK model-selected tool; fresh installed stdio MCP returns original-matched PNG. Model receives metadata, not image pixels.')
    def save():
        (out/'protocol.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    async def invoke(frame,actor):
        params=StdioServerParameters(command=str(RT/'.venv/bin/python'),args=[str(RT/'chat_tools.py')],cwd=str(RT))
        async with stdio_client(params)as(reader,writer):
            async with ClientSession(reader,writer)as client:
                await client.initialize();result=await client.call_tool('show_checked_actor_motion',dict(frame=frame,actor=actor))
        assert not result.isError
        meta=result.structuredContent;images=[part for part in result.content if part.type=='image'];assert len(images)==1
        png=base64.b64decode(images[0].data);assert hashlib.sha256(png).hexdigest()==meta['png_sha256']
        (out/'installed-MCP-actor-frame.png').write_bytes(png)
        data['MCP_calls'].append(dict(arguments=dict(frame=frame,actor=actor),metadata=meta,PNG_received=True,SDK_model_received_pixels=False));save();return meta
    def show_checked_actor_motion(frame:int=1,actor:Literal['A','B']='A')->dict:
        """Show a saved original-matched moving-actor test image from Black Ice White Noise. Choose actor A or B and source update frame1..64. This is a recorded controlled C actor/render test with other tasks blocked and device/GPU resets, not live gameplay or a complete game. The installed MCP returns an image; copy its verified_caption exactly."""
        return asyncio.run(invoke(frame,actor))
    try:
        with(ROOT/'runs/.inference.lock').open('a')as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],text=True));assert len(models)==1 and models[0]['identifier']=='advertising-scholar'and models[0]['status']=='idle'
            chat=lmstudio.Chat(system);chat.add_user_message(prompt)
            def message(value):data['events'].append(value.to_dict());save()
            result=lmstudio.llm('advertising-scholar').act(chat,[show_checked_actor_motion,chat_tools.project_evidence,chat_tools.search_references],max_prediction_rounds=2,max_parallel_tool_calls=1,config={'temperature':0.1,'maxTokens':384},on_message=message)
            calls=[part['toolCallRequest']for e in data['events']if e['role']=='assistant'for part in e['content']if part['type']=='toolCallRequest']
            texts=[part['text'].strip()for e in data['events']if e['role']=='assistant'for part in e['content']if part['type']=='text'and part['text'].strip()]
            assert len(calls)==1 and calls[0]['name']=='show_checked_actor_motion'and calls[0]['arguments']==dict(frame=32,actor='B'),calls
            assert len(data['MCP_calls'])==1 and texts[-1]==data['MCP_calls'][0]['metadata']['verified_caption'],texts
            data.update(status='ordinary_actor_frame_request_tool_arguments_PNG_and_caption_pass',seconds=result.total_time_seconds,rounds=result.rounds,answer=texts[-1]);save()
    except Exception as error:data.update(status='terminal_failed',error=repr(error));save();raise
    finally:(out/'prompts-and-responses.txt').write_text('SYSTEM\n'+system+'\nUSER\n'+prompt+'\nMESSAGES\n'+json.dumps(data['events'],ensure_ascii=False,indent=2)+'\n')
    report={k:data[k]for k in ['status','recorded_at','seconds','rounds','answer','native_Chat_verified','new_training','interface']};report['directory']=str(out)
    (ROOT/'verification/easy-checked-actor-preview-current.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)

if __name__=='__main__':main()
