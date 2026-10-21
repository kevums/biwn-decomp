"""Fresh installed real collision/movement/actor evidence, preserving separate startup/removal scope."""
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
   data={topic:unpack(await client.call_tool('project_evidence',{'topic':topic}))for topic in ['actor_collision','actor_movement','actor_task','actor_navigation','rng','status','render_startup']}
 assert len(names)==6
 for value in data.values():
  checks=value['isolated_cpu_and_portable_C_checks'];assert checks['portable_C_component_count']==103 and checks['processor_components']=={'CPU':101,'GPU':2}
 collision=data['actor_collision'];assert collision['CPU_actor_collision']['CPU_cases']==4096 and collision['CPU_actor_collision']['CPU_instruction_coverage']==[109,109]and collision['CPU_actor_collision']['nested_helper_scripts']==0
 assert collision['CPU_geometry_full_CPU']['CPU_cases']==1024 and collision['CPU_geometry_full_CPU']['CPU_instruction_coverage']==[170,170]
 assert collision['checked_partial_return_example']['full_D0']=='0xffff0000'and not collision['checked_partial_return_example']['low_word']
 assert not collision['actor_complete_movement_pipeline']['scripted_services']
 actor=collision['actor_full_movement_runtime'];assert actor['cases']==128 and actor['actor_iterations']==1024 and actor['task_handoffs']==3072 and actor['helper_return_CPU_comparisons_total']==2671
 assert not actor['scripted_helpers']and actor['position_change_cases_observed']==101 and not actor['removal_TRAP2_executed']and not actor['startup21context_fixture_linked']
 for value in [data['actor_task']['CPU_actor_task_scheduler_integration'],data['actor_navigation']['actor_navigation_scheduler_integration'],data['rng']['actor_rng_scheduler_integration'],data['status']['separate_actor_runtime']]:assert not value['scripted_helpers']
 assert data['actor_movement']['movement_GPU_pipeline']['scripted_services']==[]
 assert data['render_startup']['render_task_startup_progress']['actor_task_bodies_executed']==0
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'fresh_installed_real_collision_actor_evidence_passed','tools':names,'topics':data,'scope':'Fresh installed MCP, separate from native Chat.'}
 (ROOT/'verification/actor-collision-MCP-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'tools':6,'topics':7,'components':103,'actor_helper_scripts':0,'actor_handoffs':3072,'startup_actor_bodies':0,'removal_pending':True}))

if __name__=='__main__':asyncio.run(main())
