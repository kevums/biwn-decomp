"""Fresh installed focused authorship evidence and broader C scope."""
import asyncio,hashlib,json
from datetime import datetime,timezone
from check_audio_native_mcp import ROOT,RUNTIME,unpack
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
async def main():
    params=StdioServerParameters(command=str(RUNTIME/'.venv/bin/python'),args=[str(RUNTIME/'chat_tools.py')],cwd=str(RUNTIME))
    async with stdio_client(params)as(r,w):
        async with ClientSession(r,w)as client:
            await client.initialize();tools=(await client.list_tools()).tools;result=unpack(await client.call_tool('project_evidence',{'topic':'local_code_authorship'}))
    assert len(tools)==6 and 'local_code_authorship'in next(t.inputSchema for t in tools if t.name=='project_evidence')['properties']['topic']['enum']
    assert result['local_model_contribution']['accepted_case_bodies']==73 and not result['local_model_contribution']['coordinator_edited_case_bodies']
    assert [r['accepted']for r in result['local_model_contribution']['roles']]==[False,False,True]
    assert result['setup57_standalone_proof']['cases']==64 and result['setup57_hybrid_proof']['cases']==4 and result['setup57_hybrid_proof']['other_original_GPU_programs_executed']
    assert set(result['other_C_programs_already_verified_separately'])=={'GPU4D80_geometry','GPU52E0_projection','GPU4320_movement','GPU4B00_sprite_decode','CPU_E19E_projection_submission','CPU_E202_draw_submission'} and not result['whole_renderer_C']and not result['whole_game_complete']
    assert (ROOT/'chat_tools.py').read_bytes()==(RUNTIME/'chat_tools.py').read_bytes()
    report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='fresh_installed_focused_local_code_authorship_scope_passed',tools=[t.name for t in tools],result=result,payload_bytes=len(json.dumps(result).encode()),tool_sha256=hashlib.sha256((ROOT/'chat_tools.py').read_bytes()).hexdigest(),native_cached_provider_adoption_verified=False)
    (ROOT/'verification/code-authorship-MCP-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(tools=6,payload_bytes=report['payload_bytes'],case_bodies=73,standalone_cases=64,hybrid_cases=4)))
if __name__=='__main__':asyncio.run(main())
