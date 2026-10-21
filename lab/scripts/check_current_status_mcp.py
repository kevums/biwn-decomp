"""Check compact current status against the preserved original/C integration proof."""
import asyncio
import hashlib
import json
from datetime import datetime, timezone
from check_audio_native_mcp import ROOT, RUNTIME, unpack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    params=StdioServerParameters(command=str(RUNTIME/'.venv/bin/python'),args=[str(RUNTIME/'chat_tools.py')],cwd=str(RUNTIME))
    async with stdio_client(params) as (reader,writer):
        async with ClientSession(reader,writer) as client:
            await client.initialize()
            tool_list=(await client.list_tools()).tools
            assert len(tool_list)==6
            status=unpack(await client.call_tool('project_evidence',{'topic':'status'}))
            detail=unpack(await client.call_tool('project_evidence',{'topic':'world_input_rendering'}))
            legacy=unpack(await client.call_tool('project_evidence',{'topic':'npc_rendering'}))
    cp=status['current_checkpoint']
    assert cp==detail['current_checkpoint']
    original=json.loads((ROOT/'verification/biwn-scheduled-world-NPC-render-checks.json').read_text())
    for key in ['cases','world_updates','input_polls','NPC_iterations','GPU_submissions','C_sprite_decodes']:
        assert cp[key]==original[key]
    assert [cp[k] for k in ['cases','world_updates','input_polls','NPC_iterations','GPU_submissions','C_sprite_decodes']]==[4,28,28,20,112,24]
    assert status['checked_current_summary']==cp['checked_progress_answer']
    assert status['checked_playability_answer']==cp['checked_playability_answer']
    assert status['isolated_cpu_and_portable_C_checks']['portable_C_component_count']==135
    assert status['isolated_cpu_and_portable_C_checks']['processor_components']==dict(CPU=122,GPU=13)
    assert not status['working_game_reconstruction'] and not status['physical_hardware_validation'] and not status['native_Chat_verified']
    assert not cp['playable'] and not cp['composited_scanout_verified']
    assert legacy['current_checkpoint']['GPU_submissions']==96 and legacy['current_checkpoint']['C_sprite_decodes']==4
    size=len(json.dumps(status));assert size<12000
    assert (ROOT/'chat_tools.py').read_bytes()==(RUNTIME/'chat_tools.py').read_bytes()
    report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='fresh_installed_current_status_matches_original_C_proof',
        tool_names=[t.name for t in tool_list],current_status=status,current_status_serialized_characters=size,
        earlier_status_serialized_characters=131514,historical_NPC_renderer_scope_retained=True,
        installed_tool_source_sha256=hashlib.sha256((RUNTIME/'chat_tools.py').read_bytes()).hexdigest(),
        native_cached_provider_adoption_verified=False,native_Chat_verified=False)
    (ROOT/'verification/current-status-MCP-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],current_status_characters=size,tools=6,native_Chat_verified=False)))


if __name__=='__main__':asyncio.run(main())
