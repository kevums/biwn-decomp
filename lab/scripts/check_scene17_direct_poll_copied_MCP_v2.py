"""Exercise the moved package's actual read-only status tool, without inference."""
import asyncio, json, os
from datetime import timedelta
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from publish_scene_reset_fresh_v1 import ROOT, V, P, read, save, sha


async def main():
    config = P/'lmstudio-home/mcp.json'
    entry = read(config)['mcpServers']['local-ai-lab']
    assert Path(entry['command']).is_relative_to(P)
    assert Path(entry['args'][0]).is_relative_to(P)
    params = StdioServerParameters(command=entry['command'], args=entry['args'],
                                  env={**os.environ, **entry.get('env', {})}, cwd=str(P/'runtime'))
    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer, read_timeout_seconds=timedelta(seconds=60)) as client:
            init = await client.initialize()
            names = [x.name for x in (await client.list_tools()).tools]
            result = await client.call_tool('project_evidence', {'topic':'status'})
    raw = result.model_dump(mode='json')
    text = json.dumps(raw)
    output = V/'scene17-direct-poll-copied-MCP-response.json'
    decoded = json.loads(raw['content'][0]['text'])
    scene = decoded['native_scene_draw_progress']
    valid = (not result.isError and len(names) == 18
             and scene['status'] == 'terminal_scene17_direct_poll_fresh_pass_fidelity_open'
             and scene['fresh_scene_native_returns'] == 6473
             and scene['fresh_differing_video_frames'] == 7374
             and '7,374' in decoded['checked_current_summary']
             and '194' in decoded['checked_current_summary'])
    save(output, dict(status='terminal_copied_MCP_actual_status_returns_direct_poll_facts' if valid else 'terminal_copied_MCP_status_check_failed',
                      server=init.serverInfo.model_dump(mode='json'), tools=names, result=raw,
                      new_predictions=0, new_training=False, source_sha256={str(p):sha(p) for p in [Path(__file__), config, Path(entry['args'][0])]},
                      native_Chat_verified=False))
    assert valid, dict(tool_count=len(names), isError=result.isError, scene_status=scene.get('status'), summary=decoded.get('checked_current_summary'))
    print('Copied MCP', init.serverInfo.version, len(names), output, flush=True)


if __name__ == '__main__':
    asyncio.run(main())
