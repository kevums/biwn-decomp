"""Check current installed lifecycle evidence and task-context counting scope."""
import asyncio, json
from datetime import datetime, timezone
from check_audio_native_mcp import ROOT, RUNTIME, unpack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    params = StdioServerParameters(command=str(RUNTIME / '.venv/bin/python'), args=[str(RUNTIME / 'chat_tools.py')], cwd=str(RUNTIME))
    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as client:
            await client.initialize()
            tools = (await client.list_tools()).tools
            tool = next(x for x in tools if x.name == 'project_evidence')
            assert 'task_removal' in tool.inputSchema['properties']['topic']['enum']
            topics = ['task_removal','actor_task','actor_collision','actor_movement','actor_navigation','rng','scheduler','status','render_startup']
            results = {topic: unpack(await client.call_tool('project_evidence', {'topic':topic})) for topic in topics}
    assert len(tools) == 6
    for topic, value in results.items():
        checks = value['isolated_cpu_and_portable_C_checks']
        assert checks['portable_C_component_count'] == 106 and checks['processor_components'] == {'CPU':104,'GPU':2}
        actor = value['current_actor_lifecycle']
        assert actor['cases'] == 256 and actor['task_handoffs'] == 3840 and actor['context_reuses'] == 256
        assert actor['removal_TRAP2_executed'] and not actor['scripted_actor_helpers'] and not actor['startup21context_fixture_linked']
        counts = value['task_entry_coverage']
        assert counts['implemented_distinct_entry_bodies'] == 5 and counts['contexts_with_implemented_entry'] == 6
        assert counts['captured_distinct_entries'] == 20 and counts['captured_contexts'] == 21
    for topic in ['task_removal','actor_task']:
        assert results[topic]['CPU_task_removal']['native_CPU_cases'] == 1024
        assert results[topic]['CPU_task_removal']['CPU_instruction_coverage'] == [29,29]
    for topic in ['status','render_startup']:
        startup = results[topic]['render_task_startup_progress']
        assert startup['actor_task_bodies_executed'] == 0 and startup['implemented_captured_task_callers_total'] == 6
        assert startup['other_captured_task_callers_unported'] == 15
    report = {'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'fresh_installed_lifecycle_evidence_passed',
              'tools':[t.name for t in tools], 'topics':results, 'scope':'Fresh installed MCP; native Chat separately verified.'}
    (ROOT / 'verification/actor-lifecycle-MCP-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'tools':6,'topics':len(results),'components':106,'lifecycle_handoffs':3840,'removal_executed':True,'startup_actor_bodies':0}))

if __name__ == '__main__':
    asyncio.run(main())
