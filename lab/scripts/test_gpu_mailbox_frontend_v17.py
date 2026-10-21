"""Actual MCP task/positive/negative/retained calls before live config update."""
import asyncio,hashlib,json,os,shutil
from pathlib import Path
from datetime import datetime,timezone,timedelta
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
ROOT=Path(__file__).resolve().parents[1];RT=Path('/Users/kevin/.lmstudio/local-ai-lab');V=ROOT/'verification'
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
async def main():
 out=V/'gpu-mailbox-frontend-v16'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 for name in ['gpu_mailbox_workbench_v4.py','chat_tools_current_v16.py']:
  target=RT/name
  if target.exists():assert sha(target)==sha(ROOT/name)
  else:shutil.copy2(ROOT/name,target)
 source=(ROOT/'projects/black-ice-white-noise/restoration/native-m68k/gpu-mailbox-local-repair-v1.c').read_text();negative=source.replace('sp + 4','sp + 8');assert source!=negative;calls=[]
 with(out/'server-stderr.log').open('w')as errors:
  async with stdio_client(StdioServerParameters(command=str(ROOT/'.venv/bin/python'),args=[str(RT/'chat_tools_current_v16.py')],cwd=str(RT)),errlog=errors)as(r,w):
   async with ClientSession(r,w,read_timeout_seconds=timedelta(seconds=240))as client:
    await client.initialize();listed=await client.list_tools();save(out/'inventory.json',[x.model_dump(mode='json')for x in listed.tools]);assert len(listed.tools)==18
    async def call(name,args,label):
     result=await client.call_tool(name,args);save(out/(label+'.json'),result.model_dump(mode='json'));assert not result.isError,str(result);value=result.structuredContent or json.loads(next(x.text for x in result.content if x.type=='text'));calls.append(dict(tool=name,label=label,isError=False));print(label,'returned',flush=True);return value
    task=await call('get_game_function_task',{'routine':'gpu_mailbox'},'gpu-task');assert not task['gold_C_supplied']and task['original_ABI_component_cases']==2492
    old=await call('get_game_function_task',{'routine':'actor_direction'},'retained-direction-task');assert old['routine']=='actor_direction'
    bad=await call('verify_game_function_candidate',{'routine':'gpu_mailbox','source':negative},'semantic-negative');assert not bad['verified']and bad['completed']==0 and bad['counterexample']
    good=await call('verify_game_function_candidate',{'routine':'gpu_mailbox','source':source},'local-repair-positive');assert good['verified']and good['completed']==2492 and not good['source_accepted']
 config_path=Path.home()/'.lmstudio/mcp.json';config=json.loads(config_path.read_text());assert config['mcpServers']['local-ai-lab']['args']==[str(RT/'chat_tools_current_v15.py')];shutil.copy2(config_path,out/'previous-mcp.json');config['mcpServers']['local-ai-lab']['args']=[str(RT/'chat_tools_current_v16.py')];save(config_path,config);save(out/'installed-mcp.json',config)
 state=dict(status='terminal_gpu_mailbox_task_and_verifier_staged_pass_v16_installed',pid=os.getpid(),directory=str(out),entrypoint=str(RT/'chat_tools_current_v16.py'),tool_count=18,calls=calls,local_repair_positive_cases=2492,semantic_negative_rejected=True,new_predictions=0,new_training=False,native_Chat_verified=False,configuration_backup=str(out/'previous-mcp.json'),source_sha256={str(p):sha(p)for p in [Path(__file__),RT/'gpu_mailbox_workbench_v4.py',RT/'chat_tools_current_v16.py',ROOT/'scripts/check_gpu_mailbox_workbench_candidate_v5.py',out/'previous-mcp.json',out/'installed-mcp.json']},scope=__doc__+' Positive source is unchanged local informed repair; supplied ABI/flag/assembly integration is coordinator work. Scripted bus, no actual GPU/frame/default promotion.');save(out/'protocol.json',state);save(V/'gpu-mailbox-frontend-v16-current.json',state);print(json.dumps(state))
if __name__=='__main__':asyncio.run(main())
