"""Verify fresh installed evidence distinguishes actor scheduling from full startup."""
import asyncio
import json
from datetime import datetime, timezone
from check_audio_native_mcp import ROOT, RUNTIME, unpack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    parameters = StdioServerParameters(command=str(RUNTIME / '.venv/bin/python'),
                                      args=[str(RUNTIME / 'chat_tools.py')], cwd=str(RUNTIME))
    async with stdio_client(parameters) as (reader, writer):
        async with ClientSession(reader, writer) as client:
            await client.initialize()
            names = [t.name for t in (await client.list_tools()).tools]
            evidence = unpack(await client.call_tool('project_evidence', {'topic': 'actor_task'}))
    assert len(names) == 6
    assert evidence['isolated_cpu_and_portable_C_checks']['portable_C_component_count'] == 96
    proof = evidence['CPU_actor_task_scheduler_integration']
    assert (proof['cases'], proof['actor_iterations'], proof['task_handoffs']) == (128, 1024, 3072)
    assert proof['scheduler_yields_real'] and not proof['startup21context_fixture_linked']
    assert len(proof['scripted_helpers']) == 6 and not proof['removal_TRAP2_executed']
    assert evidence['render_task_startup_progress']['actor_task_bodies_executed'] == 0
    assert 'six helpers remain scripted' in evidence['checked_actor_task_scope'].lower()
    report = {'recorded_at': datetime.now(timezone.utc).isoformat(),
              'status': 'fresh_installed_actor_task_scheduler_evidence_passed',
              'tools': names, 'topic': evidence, 'scope': 'Installed MCP, separate from native Chat.'}
    (ROOT / 'verification/actor-task-runtime-MCP-check.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'tools': len(names), 'cases': 128, 'handoffs': 3072, 'published_components': 96}))


if __name__ == '__main__':
    asyncio.run(main())
