"""Fresh installed task creation/startup evidence and legacy world separation."""
import asyncio,json
from datetime import datetime,timezone
from check_audio_native_mcp import ROOT,RUNTIME,unpack
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
async def main():
 params=StdioServerParameters(command=str(RUNTIME/'.venv/bin/python'),args=[str(RUNTIME/'chat_tools.py')],cwd=str(RUNTIME))
 async with stdio_client(params)as(reader,writer):
  async with ClientSession(reader,writer)as client:
   await client.initialize();names=[t.name for t in(await client.list_tools()).tools];data={topic:unpack(await client.call_tool('project_evidence',{'topic':topic}))for topic in ['status','task_creation','render_startup','rendering','world_update','display_list','rng']}
 assert len(names)==6
 for e in data.values():
  assert e['isolated_cpu_and_portable_C_checks']['portable_C_component_count']==77
  assert e['isolated_cpu_and_portable_C_checks']['processor_components']=={'CPU':75,'GPU':2}
  p=e['render_task_startup_progress'];assert p['cases']==144 and p['created_tasks_per_case']==17 and p['created_task_calls']==2448 and p['contexts_after_startup']==21
  assert p['startup_complete_caller']and not p['startup_services_fully_reconstructed']and p['render_task_caller_instruction_coverage']==[98,98]
  assert p['implemented_captured_task_callers_total']==4 and p['other_captured_task_callers_unported']==17
  assert p['blocked_contexts_after_startup']==18 and p['runnable_task_bodies_in_test']==3 and p['task_handoffs']==432
  assert p['public_context_header_bytes_compared']==38 and p['saved_context_CCR_bits_compared']and not p['complete_game_frames_executed']and not p['linked_to_existing_world_runtime']
 creation=data['task_creation']['CPU_task_creation'];assert creation['native_CPU_cases']==1028 and creation['successful_return_cases']==1024 and creation['native_ILLEGAL_cases']==4 and creation['CPU_instruction_coverage']==[25,25]and creation['host_guards']==9
 assert creation['checked_example']['D0']=='0x110000'and creation['checked_example']['A0']=='0x110400'
 startup=data['render_startup']['render_startup'];assert startup['host_guards']==12 and len(startup['startup_scripted_targets'])==0 and len(startup['render_scripted_targets'])==6
 assert data['world_update']['current_connected_pipeline']['other_task_bodies_unported']==18,'Historical world integration stays distinct from4unique callers across separate proofs'
 rng=data['rng']['CPU_rng'];assert rng['CPU_cases']==2194 and rng['CPU_instruction_coverage']==[187,187] and rng['host_guards']==42
 assert rng['examples'][0]['selector_writes']==['0xffff'] and rng['examples'][1]['selector_writes']==['0x0001','0xffff']
 assert data['status']['render_task_startup_progress']['RNG_fill_iterations']==36720
 assert '0 top-level startup, 7 nested startup and 6 render services' in data['status']['checked_current_summary']
 assert data['status']['render_task_startup_progress']['supplied_contexts']==4
 assert data['status']['render_task_startup_progress']['C_sprite_decodes']==0
 assert len(data['status']['render_task_startup_progress']['startup_nested_scripted_targets'])==7
 assert data['rendering']['scheduled_render_continuation_pipeline']['created_task_calls']==2448
 services=data['render_startup']['CPU_startup_services'];assert services['CPU_cases']==1152 and services['CPU_instruction_coverage']==[210,210] and services['host_guards']==43
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'fresh_installed_startup_services_evidence_passed','tools':names,'topics':data,'status_characters':len(json.dumps(data['status'])),'scope':'Installed MCP evidence, not native Chat display.'};(ROOT/'verification/services-MCP-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'components':77,'tools':6,'topics':len(data),'status_characters':report['status_characters']}))
if __name__=='__main__':asyncio.run(main())
