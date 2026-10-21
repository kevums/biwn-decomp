"""Check installed inventory evidence after snapshot refresh; no inference."""
import asyncio, json
from datetime import datetime, timezone
from check_audio_native_mcp import ROOT, RUNTIME, unpack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    params=StdioServerParameters(command=str(RUNTIME/'.venv/bin/python'),args=[str(RUNTIME/'chat_tools.py')],cwd=str(RUNTIME))
    async with stdio_client(params) as (reader,writer):
        async with ClientSession(reader,writer) as client:
            await client.initialize()
            names=[t.name for t in (await client.list_tools()).tools]
            compact=unpack(await client.call_tool('project_evidence',{'topic':'inventory_drawing'}))
            status=unpack(await client.call_tool('project_evidence',{'topic':'status'}))
    panel=compact['inventory_panel']
    assert len(names)==5 and 'render_inventory_preview' in names
    assert compact['isolated_cpu_and_portable_C_checks']['portable_C_component_count']==22
    assert panel['complete_internal_inventory_panel_rendered'] and panel['GPU_sprite_decoder_linked']
    assert not panel['whole_game_rebuilt'] and not panel['complete_game_viewport_rendered']
    assert not panel['independent_blitter_reconstruction']
    assert panel['fast_cases']==300 and panel['accurate_cases']==30
    assert panel['selection_interaction']['steps']==600
    assert panel['selection_interaction']['redraw_steps']==520
    assert not panel['selection_interaction']['physical_controller_polled']
    assert status['emulator_runtime']['GPU_sprite_decoder_reconstruction']['linked_into_inventory_pipeline']
    report={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'fresh_installed_panel_evidence_passed',
            'tools':names,'inventory_evidence':compact,'scope':'Fresh stdio evidence only; native Chat visual adoption unverified while locked.'}
    (ROOT/'verification/inventory-frame-MCP-evidence-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'tools':len(names),'components':22,'panel_rendered':True,'whole_game_rebuilt':False}))

if __name__=='__main__': asyncio.run(main())
