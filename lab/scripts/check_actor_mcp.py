"""Fresh installed actor evidence, task provenance and direct/queue distinction."""
import asyncio,json
from datetime import datetime,timezone
from check_audio_native_mcp import ROOT,RUNTIME,unpack
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
async def main():
 params=StdioServerParameters(command=str(RUNTIME/'.venv/bin/python'),args=[str(RUNTIME/'chat_tools.py')],cwd=str(RUNTIME))
 async with stdio_client(params)as(reader,writer):
  async with ClientSession(reader,writer)as client:
   await client.initialize();names=[t.name for t in(await client.list_tools()).tools];data={topic:unpack(await client.call_tool('project_evidence',{'topic':topic}))for topic in ['status','actor_creation','render_startup','task_creation','texture_cache','scene_loading','rendering','memory','world_update']}
 assert len(names)==6
 for e in data.values():
  checks=e['isolated_cpu_and_portable_C_checks'];assert checks['portable_C_component_count']==96 and checks['processor_components']=={'CPU':94,'GPU':2}
  p=e['render_task_startup_progress'];assert p['cases']==144 and p['supplied_contexts']==2 and p['created_tasks_per_case']==19 and p['created_task_calls']==2736 and p['contexts_after_startup']==21
  assert p['real_actor_dispatch_calls']==432 and p['actor_records_created_per_case']==2 and p['actor_tasks_created_per_case']==2 and p['static_objects_created_per_case']==1
  assert p['real_allocations_total']==432 and p['real_static_sprite_allocations']==144 and p['scene_actor_creation_real']and p['real_player_outdoor_positioning']
  assert p['C_sprite_decodes']==144 and p['direct_static_factory_sprite_decodes']==144 and p['animation_queue_consumer_sprite_decodes']==0 and not p['actor_task_bodies_executed']
  assert len(p['startup_nested_scripted_targets'])==len(p['startup_nested_scripted_targets_reached'])==3 and p['task_handoffs']==432 and not p['complete_game_frames_executed']
  assert p['disc_read_requests']==1728 and p['resident_texture_payload_checks']==720
 a=data['actor_creation'];cpu=a['CPU_actor_creation'];assert cpu['CPU_cases']==2560 and cpu['CPU_instruction_coverage']==[469,469]and cpu['host_guards']==62 and cpu['helper_incoming_D0_compared']
 assert a['checked_full_entity_pool_example']['full_D0']=='0x1f62'and a['checked_full_entity_pool_example']['no_init_call']
 assert '2contexts'in data['render_startup']['checked_context_answer']and '19'in data['render_startup']['checked_context_answer']
 assert 'Queueconsumer decodes0'in data['render_startup']['checked_sprite_queue_answer']
 assert '0 top-level startup, 3 nested startup and 6 render services'in data['status']['checked_current_summary']
 assert data['world_update']['current_connected_pipeline']['other_task_bodies_unported']==18
 assert 'historical'in data['texture_cache']['texture_checkpoint_scope']
 report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'fresh_installed_actor_creation_evidence_passed','tools':names,'topics':data,'status_characters':len(json.dumps(data['status'])),'scope':'InstalledMCP, not nativeChatdisplay.'};(ROOT/'verification/actor-MCP-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'components':96,'tools':6,'topics':len(data),'status_characters':report['status_characters']}))
if __name__=='__main__':asyncio.run(main())
