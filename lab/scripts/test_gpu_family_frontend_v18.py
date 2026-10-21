"""Stage real MCP schema/task/positive/negative calls; do not change the live configuration."""
import asyncio,hashlib,json,os,shutil
from pathlib import Path
from datetime import datetime,timezone,timedelta
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
ROOT=Path(__file__).resolve().parents[1];RT=Path.home()/'.lmstudio/local-ai-lab';V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
async def main():
 out=V/'gpu-family-frontend-v18'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);config=Path.home()/'.lmstudio/mcp.json';before=sha(config)
 for name in['gpu_command_family_workbench_v1.py','chat_tools_current_v18.py']:
  target=RT/name
  if target.exists():assert sha(target)==sha(ROOT/name)
  else:shutil.copy2(ROOT/name,target)
 source=(ROOT/'projects/black-ice-white-noise/restoration/native-m68k/gpu-family-hybrid-v1.c').read_text();negative=source.replace('r[0] = d0;','r[0] = d0 ^ 1u;');assert source!=negative;calls=[]
 with(out/'stderr.log').open('w')as errors:
  async with stdio_client(StdioServerParameters(command=str(ROOT/'.venv/bin/python3.12'),args=[str(RT/'chat_tools_current_v18.py')],cwd=str(RT)),errlog=errors)as(r,w):
   async with ClientSession(r,w,read_timeout_seconds=timedelta(seconds=240))as client:
    await client.initialize();listed=await client.list_tools();save(out/'inventory.json',[x.model_dump(mode='json')for x in listed.tools]);assert len(listed.tools)==18
    async def call(name,args,label):
     result=await client.call_tool(name,args);save(out/(label+'.json'),result.model_dump(mode='json'));assert not result.isError,str(result);value=result.structuredContent or json.loads(next(x.text for x in result.content if x.type=='text'));calls.append(dict(tool=name,label=label,isError=False));print(label,'returned',flush=True);return value
    task=await call('get_game_function_task',dict(routine='gpu_command_family'),'family-task');assert task['component_cases']==10048 and len(task['complete_original_entries'])==8 and not task['gold_C_supplied']
    for routine in['gpu_mailbox','actor_direction']:
     retained=await call('get_game_function_task',dict(routine=routine),'retained-'+routine);assert retained['routine']==routine
    good=await call('verify_game_function_candidate',dict(routine='gpu_command_family',source=source),'hybrid-positive');assert good['verified']and good['completed']==10048 and not good['source_accepted']
    bad=await call('verify_game_function_candidate',dict(routine='gpu_command_family',source=negative),'semantic-negative');assert not bad['verified']and bad['completed']==3738 and bad['counterexample']
 assert sha(config)==before
 state=dict(status='terminal_staged_v18_family_MCP_positive_negative_and_retained_tasks_pass',directory=str(out),entrypoint=str(RT/'chat_tools_current_v18.py'),main_tools=18,positive_component_cases=10048,semantic_negative_rejected_at_case=3738,live_configuration_changed=False,new_predictions=0,new_training=False,native_Chat_verified=False,calls=calls,source_sha256={str(p):sha(p)for p in[Path(__file__),ROOT/'gpu_command_family_workbench_v1.py',ROOT/'chat_tools_current_v18.py',RT/'gpu_command_family_workbench_v1.py',RT/'chat_tools_current_v18.py',out/'inventory.json',out/'hybrid-positive.json',out/'semantic-negative.json']});save(out/'protocol.json',state);save(V/'gpu-family-frontend-v18-current.json',state);print(json.dumps(state))
if __name__=='__main__':asyncio.run(main())
