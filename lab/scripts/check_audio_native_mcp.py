"""Fresh stdio smoke check for saved evidence; no model inference."""
import asyncio
from datetime import datetime, timezone
import json
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = Path.home()/'.lmstudio/local-ai-lab'


def unpack(result):
    assert not result.isError
    return json.loads(next(c.text for c in result.content if c.type == 'text'))


async def main():
    params = StdioServerParameters(command=str(RUNTIME/'.venv/bin/python'), args=[str(RUNTIME/'chat_tools.py')], cwd=str(RUNTIME))
    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as client:
            await client.initialize()
            names = [t.name for t in (await client.list_tools()).tools]
            status = unpack(await client.call_tool('project_evidence', {'topic':'status'}))
            components = status['isolated_cpu_and_portable_C_checks']['portable_C_component_count']
            audio = status['emulator_runtime']['audio_path_observations']
            commands = status['emulator_runtime']['audio_command_observations']
            correction = unpack(await client.call_tool('search_references', {'domain':'advertising', 'query':'1994 revised PII citation year 1984 correction Lee Koo'}))
            stats = unpack(await client.call_tool('search_references', {'domain':'advertising', 'query':'Gelman Stern significant nonsignificant difference uncertainty'}))
            assert components == 10
            assert 'zero' in json.dumps(audio).lower()
            assert commands['button_vs_baseline_difference_counts']['framebuffer_hash'] == 0
            assert any('source-correction-lee-koo.txt' in e['source'] for e in correction['evidence'])
            assert any('significance-comparisons.txt' in e['source'] for e in stats['evidence'])
    report = {'recorded_at':datetime.now(timezone.utc).isoformat(), 'status':'fresh_MCP_evidence_passed',
              'registered_tools':names, 'components':components, 'audio_path':audio, 'audio_commands':commands,
              'citation_correction_sources':[e['source'] for e in correction['evidence']],
              'statistical_reference_sources':[e['source'] for e in stats['evidence']],
              'scope':'Fresh stdio tool process; saved evidence and indexed-reference retrieval only. No model inference or native UI action.'}
    (ROOT/'verification/audio-native-MCP-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'tools':names,'components':components,'new_advertising_references_found':True}))


if __name__ == '__main__':
    asyncio.run(main())
