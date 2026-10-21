"""Fresh installed movement/GPU evidence with explicit pending collision/task scope."""
import asyncio,json
from datetime import datetime,timezone
from check_audio_native_mcp import ROOT,RUNTIME,unpack
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
 params=StdioServerParameters(command=str(RUNTIME/'.venv/bin/python'),args=[str(RUNTIME/'chat_tools.py')],cwd=str(RUNTIME))
 async with stdio_client(params)as(reader,writer):
  async with ClientSession(reader,writer)as client:
   await client.initialize();names=[tool.name for tool in(await client.list_tools()).tools]
   data={topic:unpack(await client.call_tool('project_evidence',{'topic':topic}))for topic in ['actor_movement','actor_task','status','render_startup']}
 assert len(names)==6
 for value in data.values():
  checks=value['isolated_cpu_and_portable_C_checks'];assert checks['portable_C_component_count']==100 and checks['processor_components']=={'CPU':98,'GPU':2}
 movement=data['actor_movement'];assert movement['CPU_movement_caller']['CPU_cases']==2048 and movement['CPU_movement_caller']['CPU_instruction_coverage']==[192,192]
 assert movement['CPU_direction']['reachable_instruction_coverage']==[61,61]and movement['CPU_direction']['host_guards']==13
 assert movement['CPU_GPU_submission']['cases']==128 and movement['CPU_GPU_submission']['host_guards']==14
 gpu=movement['movement_GPU_pipeline'];assert gpu['CPU_cases']==256 and gpu['CPU_instruction_coverage']==[192,192]and gpu['scripted_services']==['0x13b5a','0x13bb0']and not gpu['GPU_output_words_scripted']
 assert '0x00010000'in movement['checked_rollback_answer']and 'retains'in movement['checked_rollback_answer']
 assert data['actor_task']['CPU_actor_task_scheduler_integration']['scripted_helpers']==['0x13c9a']
 assert data['status']['separate_actor_movement_progress']['scripted_services']==['0x13b5a','0x13bb0']
 assert data['render_startup']['render_task_startup_progress']['actor_task_bodies_executed']==0
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'fresh_installed_actor_movement_evidence_passed','tools':names,'topics':data,'scope':'Fresh installed MCP, separate from native Chat.'}
 (ROOT/'verification/actor-movement-MCP-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'tools':6,'topics':4,'components':100,'movement_GPU_cases':256,'collision_scripts':2,'actor_task_linked':False}))

if __name__=='__main__':asyncio.run(main())
