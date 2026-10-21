"""Fresh installed MCP source startup scope, distinct from connected game."""
import asyncio,json,hashlib
from datetime import datetime,timezone
from check_audio_native_mcp import ROOT,RUNTIME,unpack
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
async def main():
    async with stdio_client(StdioServerParameters(command=str(RUNTIME/'.venv/bin/python'),args=[str(RUNTIME/'chat_tools.py')],cwd=str(RUNTIME)))as(r,w):
        async with ClientSession(r,w)as client:
            await client.initialize();tools=(await client.list_tools()).tools;assert len(tools)==6
            results={k:unpack(await client.call_tool('project_evidence',{'topic':k}))for k in ['render_startup','rng','status']}
    cp=json.loads((ROOT/'verification/source-startup-CPU-checkpoint.json').read_text())
    assert results['render_startup']['separate_standalone_startup_checkpoint']==results['rng']['separate_standalone_startup_checkpoint']==cp
    assert results['status']['separate_standalone_startup_progress']==cp
    assert cp['source_task_creations_per_case']==19 and cp['contexts_after_startup']==21 and cp['disc_requests_per_case']==12 and cp['disc_bytes_per_case']==758846 and not cp['remaining_game_helper_scripts']
    assert cp['earlier_startup_capture_still_supplied_to_connected_game']and not cp['actual_startup_scheduler_switching_verified']and not cp['inherited_GPU_DSP_state_compared']
    assert results['status']['current_checkpoint']['earlier_startup_capture_supplied']
    assert (ROOT/'chat_tools.py').read_bytes()==(RUNTIME/'chat_tools.py').read_bytes()
    report=dict(status='fresh_installed_MCP_source_startup_scope_match',recorded_at=datetime.now(timezone.utc).isoformat(),tools=[x.name for x in tools],evidence=results,installed_tools_sha256=hashlib.sha256((RUNTIME/'chat_tools.py').read_bytes()).hexdigest(),native_Chat_verified=False)
    (ROOT/'verification/source-startup-CPU-MCP-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],tools=len(tools))))
if __name__=='__main__':asyncio.run(main())
