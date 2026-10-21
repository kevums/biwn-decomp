"""Fresh installed geometry evidence, counts and current dependency scope."""
import asyncio,json
from datetime import datetime,timezone
from check_audio_native_mcp import ROOT,RUNTIME,unpack
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
async def main():
 params=StdioServerParameters(command=str(RUNTIME/'.venv/bin/python'),args=[str(RUNTIME/'chat_tools.py')],cwd=str(RUNTIME))
 async with stdio_client(params)as(reader,writer):
  async with ClientSession(reader,writer)as client:
   await client.initialize();names=[x.name for x in(await client.list_tools()).tools]
   data=unpack(await client.call_tool('project_evidence',{'topic':'geometry'}))
   others={topic:unpack(await client.call_tool('project_evidence',{'topic':topic}))for topic in ['world_update','boundary_handlers','movement_matrix']}
 assert len(names)==5 and data['isolated_cpu_and_portable_C_checks']['portable_C_component_count']==31
 assert data['isolated_cpu_and_portable_C_checks']['processor_components']=={'CPU':29,'GPU':2}
 geometry=data['CPU_geometry'];pipeline=data['current_connected_pipeline']
 assert geometry['CPU_cases']==1216 and geometry['CPU_instruction_coverage']==[245,245]and geometry['nested_helper_calls']==0 and geometry['full_D0_checked']
 assert pipeline['cases']==256 and all(x>0 for x in pipeline['geometry_function_calls'].values())and pipeline['redraw_cases']==166
 assert len(pipeline['remaining_top_level_scripted_helpers'])==5 and len(pipeline['remaining_nested_dependency_targets'])==5
 assert not pipeline['full_collision_geometry_reconstructed']and not pipeline['whole_game_rebuilt']and pipeline['complete_game_frames_executed']==0
 assert all(x['current_connected_pipeline']==pipeline for x in others.values())
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'fresh_installed_geometry_evidence_passed','tools':names,'geometry':data,'other_topics':others,'scope':'Fresh installed stdio evidence, not native Chat visual adoption or full game.'}
 (ROOT/'verification/geometry-MCP-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'components':31,'CPU_cases':1216,'linked_cases':256,'remaining_top_level':5,'nested_transition':5}))
if __name__=='__main__':asyncio.run(main())
