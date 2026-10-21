"""Fresh installed navigation facts and separation from full startup."""
import asyncio,json
from datetime import datetime,timezone
from check_audio_native_mcp import ROOT,RUNTIME,unpack
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
 parameters=StdioServerParameters(command=str(RUNTIME/'.venv/bin/python'),args=[str(RUNTIME/'chat_tools.py')],cwd=str(RUNTIME))
 async with stdio_client(parameters)as(reader,writer):
  async with ClientSession(reader,writer)as client:
   await client.initialize();names=[t.name for t in(await client.list_tools()).tools]
   evidence={topic:unpack(await client.call_tool('project_evidence',{'topic':topic}))for topic in ['actor_navigation','actor_task','status','render_startup']}
 assert len(names)==6
 for topic,value in evidence.items():
  checks=value['isolated_cpu_and_portable_C_checks'];assert checks['portable_C_component_count']==100 and checks['processor_components']=={'CPU':98,'GPU':2}
 nav=evidence['actor_navigation'];assert nav['CPU_actor_navigation']['CPU_cases']==4096 and nav['CPU_actor_navigation']['CPU_instruction_coverage']==[209,209]
 linked=nav['actor_navigation_scheduler_integration'];assert linked['navigation_helper_return_comparisons_total']==1279 and linked['task_handoffs']==3072
 assert linked['scripted_helpers']==['0x1a77c','0x13c9a']and not linked['startup21context_fixture_linked']and not linked['removal_TRAP2_executed']
 assert '0xAABB0001'in nav['checked_waypoint_early_return']and '0x0018'in nav['checked_waypoint_early_return']
 assert '0xAABB0FE0'in nav['checked_waypoint_word_arithmetic']
 assert evidence['actor_task']['CPU_actor_task_scheduler_integration']['navigation_helper_bodies_real']==4
 assert evidence['status']['separate_actor_navigation_runtime']['navigation_helper_bodies_real']==4
 assert not evidence['render_startup']['render_task_startup_progress']['actor_task_bodies_executed']
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'fresh_installed_navigation_evidence_passed','tools':names,'topics':evidence,'scope':'Installed MCP, not native Chat display.'}
 (ROOT/'verification/actor-navigation-MCP-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'components':100,'tools':6,'topics':4,'navigation_helpers_real':4,'actor_scripts':2}))

if __name__=='__main__':asyncio.run(main())
