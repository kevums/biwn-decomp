"""Normal local request -> installed MCP -> native C panel -> model caption.

SDK adapter forwards structured metadata to the model. MCP PNG transport is
checked separately; this does not test model vision or native Chat display.
"""
import argparse,asyncio,base64,fcntl,hashlib,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import chat_tools,lab,lmstudio
RUNTIME=Path.home()/'.lmstudio/local-ai-lab'
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--starting-slot',type=int,default=1);parser.add_argument('--money',type=int,default=200);parser.add_argument('--cycle-count',type=int,default=0);parser.add_argument('--digit',type=int,choices=range(10));args=parser.parse_args()
    preset=ROOT/'presets/Game Assistant.preset.json';system=next(f['value']for f in json.loads(preset.read_text())['operation']['fields']if f['key']=='llm.prediction.systemPrompt')
    out=ROOT/'verification/easy-inventory-render'/lab.stamp();out.mkdir(parents=True)
    record={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'running','model':'advertising-scholar','system':system,
        'user':(f'Start the rebuilt Black Ice White Noise inventory at position {args.starting_slot} with ${args.money}, select digit {args.digit}, and show the resulting panel. Briefly explain what ran, under60words.' if args.digit is not None else f'Start the rebuilt Black Ice White Noise inventory at position {args.starting_slot} with ${args.money}, advance it {args.cycle_count} times, and show the resulting panel. Briefly explain what ran, under60words.' if args.cycle_count else f'Show the rebuilt Black Ice White Noise inventory panel starting at slot{args.starting_slot} with ${args.money}. Briefly explain what this output proves, under60words.'),
        'preset_sha256':lab.sha(preset),'interface':'localhostSDKtoolchoice/caption; freshinstalledMCPexecution. SDKadapterforwardsmetadataonly; modelvision/nativeChatdisplay not tested.',
        'config':{'temperature':0.2,'maxTokens':384},'max_prediction_rounds':2,'max_parallel_tool_calls':1,'events':[],'MCP_calls':[]}
    save(out/'protocol.json',record);print(out,flush=True)
    async def invoke(arguments):
        params=StdioServerParameters(command=str(RUNTIME/'.venv/bin/python'),args=[str(RUNTIME/'chat_tools.py')],cwd=str(RUNTIME))
        async with stdio_client(params)as(reader,writer):
            async with ClientSession(reader,writer)as client:
                await client.initialize();result=await client.call_tool('render_inventory_preview',arguments)
        if result.isError:raise RuntimeError(str(result.content))
        metadata=result.structuredContent;images=[block for block in result.content if block.type=='image'];assert metadata and len(images)==1
        png=base64.b64decode(images[0].data);assert hashlib.sha256(png).hexdigest()==metadata['png_sha256'];(out/'MCP-inventory-panel.png').write_bytes(png)
        record['MCP_calls'].append({'arguments':arguments,'metadata':metadata,'PNG_image_block_received':True,'SDK_model_received_image_pixels':False});save(out/'protocol.json',record)
        assert metadata['requested_starting_slot']==arguments.get('starting_slot',1)
        assert metadata['money']==arguments.get('money',200)
        return metadata
    def render_inventory_preview(startingSlot:int=1,selectedSlot:int|None=None,money:int=200,actions:list[str]|None=None)->dict:
        """Render the rebuilt inventory panel. Positions1..10 use screen digits1..9 then0. Starting position defaults1, selected defaults to it, money defaults200. Optional ordered actions (max20): cycle advances once with wrap, digit strings1..9 choose positions,0 chooses position10,none preserves state. Each call resets to startingSlot. Connected reconstructed C selection and drawing with emulated blitter; not physical polling/fullgame. Returns verified_caption and metadata; installed MCP also provides PNG."""
        arguments={'starting_slot':startingSlot,'money':money}
        if selectedSlot is not None:arguments['selected_slot']=selectedSlot
        if actions is not None:arguments['actions']=actions
        return asyncio.run(invoke(arguments))
    with (ROOT/'runs/.inference.lock').open('w')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True));assert len(models)==1 and models[0]['identifier']=='advertising-scholar'and models[0]['contextLength']==32768
        chat=lmstudio.Chat(system);chat.add_user_message(record['user'])
        def message(value):record['events'].append(value.to_dict());save(out/'protocol.json',record)
        result=lmstudio.llm('advertising-scholar').act(chat,[chat_tools.verify_68000_fixture,render_inventory_preview,chat_tools.project_evidence,chat_tools.inspect_boot,chat_tools.search_references],max_prediction_rounds=2,max_parallel_tool_calls=1,config=lmstudio.LlmPredictionConfig.from_dict(record['config']),on_message=message)
        assert len(record['MCP_calls'])==1
        actual=record['MCP_calls'][0]['metadata']
        assert actual['requested_starting_slot']==args.starting_slot and actual['money']==args.money,'Requested values were not delivered'
        assert actual['starting_slot']==((args.digit or 10)if args.digit is not None else (args.starting_slot-1+args.cycle_count)%10+1)
        if args.digit is not None:assert actual['actions']==[str(args.digit)]
        if args.cycle_count:assert actual['actions']==['cycle']*args.cycle_count
        record.update(status='completed_pending_coordinator_review',completed_at=datetime.now(timezone.utc).isoformat(),rounds=result.rounds,SDK_reported_seconds=result.total_time_seconds);save(out/'protocol.json',record)
    save(out/'prompts-and-responses.txt',record);save(ROOT/'verification/easy-inventory-render-current.json',{'directory':str(out),'status':record['status']});print(json.dumps({'rounds':result.rounds,'seconds':result.total_time_seconds}),flush=True)

if __name__=='__main__':main()
