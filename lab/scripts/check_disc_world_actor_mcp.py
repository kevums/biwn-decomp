"""Verify actual world-generated actor timing and remaining script scope in installed MCP."""
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
            results={topic:unpack(await client.call_tool('project_evidence',{'topic':topic}))for topic in ['actor_scene','actor_task','world_update','input_poll','status']}
    assert len(tools)==6
    for topic,value in results.items():
        checks=value.get('isolated_cpu_and_portable_C_checks',{})
        assert value.get('checked_components',checks.get('portable_C_component_count'))==106
        proof=value['current_world_actors'];assert proof['cases']==16 and proof['task_handoffs']==2576 and proof['world_updates']==512
        assert proof['world_caller_generates_actor_timestep']and not proof['shared_timestep_directly_scripted']and not proof['actor_helper_scripts']
        assert len(proof['configured_world_helper_scripts'])==7 and sum(v>0 for v in proof['reached_world_helper_script_counts'].values())==4
        assert proof['blocked_contexts']==16
        assert value['checked_signed_clock_example']['timestep_writes']==['0xffffffff']and value['checked_signed_clock_example']['negative_is_not_lower_clamped']
        assert value['checked_upper_clock_example']['timestep_writes']==['0x7fffffff','0x0000001e']
    for topic in ['world_update','input_poll']:
        assert results[topic]['world_full_CPU_reconstruction']['CPU_cases']==1035
        assert results[topic]['world_real_input_full_CPU']['CPU_instruction_coverage']==[313,313]
    size=len(json.dumps(results['actor_scene']));assert size<7000
    report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'fresh_installed_world_actor_timing_evidence_passed','tools':[t.name for t in tools],'topics':results,'focused_payload_bytes':size,'scope':'Installed MCP only; native Chat separately checked.'}
    (ROOT/'verification/disc-world-actor-MCP-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'tools':6,'topics':5,'components':106,'handoffs':2576,'world_generates_timestep':True,'configured_world_scripts':7,'reached_world_scripts':4,'focused_bytes':size}))
if __name__=='__main__':asyncio.run(main())
