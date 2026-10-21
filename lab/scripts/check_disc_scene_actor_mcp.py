"""Verify installed scene-data bridge facts and limits across ordinary topics."""
import asyncio,json
from datetime import datetime,timezone
from check_audio_native_mcp import ROOT,RUNTIME,unpack
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    params=StdioServerParameters(command=str(RUNTIME/'.venv/bin/python'),args=[str(RUNTIME/'chat_tools.py')],cwd=str(RUNTIME))
    async with stdio_client(params)as(reader,writer):
        async with ClientSession(reader,writer)as client:
            await client.initialize();tools=(await client.list_tools()).tools
            results={topic:unpack(await client.call_tool('project_evidence',{'topic':topic}))for topic in ['actor_task','actor_collision','actor_movement','actor_navigation','status','render_startup']}
            focused=unpack(await client.call_tool('project_evidence',{'topic':'actor_scene'}))
    assert len(tools)==6
    for value in results.values():
        assert value['isolated_cpu_and_portable_C_checks']['portable_C_component_count']==106
        scene=value['current_disc_scene_actors']
        assert scene['cases']==16 and scene['actor_iterations']==1024 and scene['task_handoffs']==2064
        assert scene['full_helper_return_CPU_comparisons']==1108 and scene['cases_with_position_change']==12
        assert scene['created_contexts_preserved']==21 and scene['blocked_contexts']==17
        assert scene['shared_time_step_inputs']==[0,1,8,30] and scene['startup_C_scene_task_state_linked']
        assert not scene['uninterrupted_startup_actor_execution'] and not scene['geometry_replaced_by_synthetic_grid']
        assert not scene['actor_helper_scripts'] and scene['original_collision_entry_counts']=={'0x13b5a':40,'0x13bb0':0}
        assert value['current_actor_lifecycle']['removal_TRAP2_executed']
    for topic in ['status','render_startup']:
        assert results[topic]['render_task_startup_progress']['actor_task_bodies_executed']==0
    assert focused['checked_components']==106 and focused['current_disc_scene_actors']==results['actor_task']['current_disc_scene_actors']
    assert 'current_actor_lifecycle'not in focused
    old_size=len(json.dumps(results['actor_task']));focused_size=len(json.dumps(focused));assert focused_size<old_size
    report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'fresh_installed_disc_scene_actor_evidence_passed','tools':[t.name for t in tools],'topics':results,'focused_actor_scene':focused,'focused_payload_bytes':focused_size,'actor_task_payload_bytes':old_size,'scope':'Installed MCP only; native Chat checked separately.'}
    (ROOT/'verification/disc-scene-actor-MCP-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'tools':6,'topics':7,'components':106,'disc_scene_handoffs':2064,'timing_supplied':True,'whole_game':False,'focused_bytes':focused_size,'actor_task_bytes':old_size}))

if __name__=='__main__':asyncio.run(main())
