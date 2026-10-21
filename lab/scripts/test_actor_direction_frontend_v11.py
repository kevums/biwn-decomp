"""Stage actual MCP task/verifier calls before updating the live entrypoint."""
import asyncio,hashlib,json,os,re,shutil
from pathlib import Path
from datetime import datetime,timezone,timedelta
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
ROOT=Path(__file__).resolve().parents[1];RT=Path('/Users/kevin/.lmstudio/local-ai-lab');V=ROOT/'verification'
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
async def main():
 out=V/'actor-direction-frontend-v11'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 for name in ['actor_direction_workbench.py','chat_tools_current_v11.py']:
  target=RT/name;assert not target.exists();shutil.copy2(ROOT/name,target)
 raw=(ROOT/'projects/black-ice-white-noise/restoration/native-m68k/actor-direction-reference-v2.c').read_text();source='\n'.join(x for x in raw.splitlines()if not x.startswith('#define'))
 for name,macro in [('R16','ADR16'),('R32','ADR32')]:source=re.sub(name+r'\(([^,]+),([^\)]+)\)',lambda m:'(('+m[2]+')='+macro+'('+m[1]+'))',source)
 source=re.sub(r'PUSH\(([^\)]+)\)',lambda m:'do{s.r[15]-=4;ADW32(s.r[15],'+m[1]+');}while(0)',source);(out/'coordinator-positive-expanded.c').write_text(source+'\n')
 rejected_state=json.loads((V/'actor-direction-local-proposal-reviewed-current.json').read_text());rejected=Path(rejected_state['candidate']).read_text()
 calls=[]
 with(out/'server-stderr.log').open('w')as errors:
  async with stdio_client(StdioServerParameters(command=str(ROOT/'.venv/bin/python'),args=[str(RT/'chat_tools_current_v11.py')],cwd=str(RT)),errlog=errors)as(r,w):
   async with ClientSession(r,w,read_timeout_seconds=timedelta(seconds=240))as client:
    await client.initialize();listed=await client.list_tools();save(out/'inventory.json',[x.model_dump(mode='json')for x in listed.tools]);assert len(listed.tools)==18
    async def call(name,args,label):
     result=await client.call_tool(name,args);save(out/(label+'.json'),result.model_dump(mode='json'));assert not result.isError,str(result);value=result.structuredContent or json.loads(next(x.text for x in result.content if x.type=='text'));calls.append(dict(tool=name,label=label,isError=False));print(label,'returned',flush=True);return value
    task=await call('get_game_function_task',{'routine':'actor_direction'},'direction-task');assert task['gold_C_supplied']is False and task['original_ABI_component_cases']==2560
    old=await call('get_game_function_task',{'routine':'frame_release'},'retained-frame-task');assert old
    bad=await call('verify_game_function_candidate',{'routine':'actor_direction','source':rejected},'actual-rejected-local-source');assert not bad['verified']and bad['completed']==0 and bad['counterexample']
    good=await call('verify_game_function_candidate',{'routine':'actor_direction','source':source},'coordinator-positive-component-check');assert good['verified']and good['completed']==2560 and not good['source_accepted']
 config_path=Path.home()/'.lmstudio/mcp.json';config=json.loads(config_path.read_text());assert config['mcpServers']['local-ai-lab']['args']==[str(RT/'chat_tools_current_v10.py')];shutil.copy2(config_path,out/'previous-mcp.json');config['mcpServers']['local-ai-lab']['args']=[str(RT/'chat_tools_current_v11.py')];save(config_path,config);save(out/'installed-mcp.json',config)
 state=dict(status='terminal_direction_task_and_bounded_verifier_staged_pass_frontend_installed',pid=os.getpid(),directory=str(out),entrypoint=str(RT/'chat_tools_current_v11.py'),tool_count=18,calls=calls,coordinator_positive_cases=2560,rejected_unchanged_local_candidate=True,new_predictions=0,new_training=False,native_Chat_verified=False,configuration_backup=str(out/'previous-mcp.json'),source_sha256={str(p):sha(p)for p in [Path(__file__),RT/'actor_direction_workbench.py',RT/'chat_tools_current_v11.py',ROOT/'scripts/check_actor_direction_workbench_candidate.py',out/'coordinator-positive-expanded.c',out/'previous-mcp.json',out/'installed-mcp.json']},scope=__doc__+' Positiveinputisexplicitcoordinatorreferencewithfourlocalmacrosmechanicallyexpanded,notmodelauthored. No automatic source/defaultpromotion.');save(out/'protocol.json',state);save(V/'actor-direction-frontend-v11-current.json',state);print(json.dumps(state))
if __name__=='__main__':asyncio.run(main())
