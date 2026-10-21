"""Fresh installed MCP projection routing, pending scope and unchanged counts."""
import asyncio,hashlib,json
from datetime import datetime,timezone
from check_audio_native_mcp import ROOT,RUNTIME,unpack
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
async def main():
    params=StdioServerParameters(command=str(RUNTIME/'.venv/bin/python'),args=[str(RUNTIME/'chat_tools.py')],cwd=str(RUNTIME))
    async with stdio_client(params)as(r,w):
        async with ClientSession(r,w)as client:
            await client.initialize();tools=(await client.list_tools()).tools
            topics={name:unpack(await client.call_tool('project_evidence',{'topic':name}))for name in ['rendering','status','camera','targeting','animation_images','movement_matrix','resources']}
    assert len(tools)==6
    description=next(t.description for t in tools if t.name=='project_evidence');assert 'GPU52E0 or10A684 questions belong to rendering'in description
    expected=topics['rendering']['pending_GPU52E0_projection']
    assert expected['GPU_cases']==16 and expected['source_instruction_coverage']==[448,450]and expected['host_guards']==16 and expected['projection_list_head_values']==[0,47]
    assert not expected['live_CPU_E19E_linked']and not expected['full_renderer_verified']and not expected['published_component_count_includes_GPU52E0']
    for name,value in topics.items():
        assert value['checked_components']==114 and value['processor_components']=={'CPU':111,'GPU':3}and not value['working_game_reconstruction']
        if name in ['rendering','status','camera','targeting']:assert value['pending_GPU52E0_projection']==expected
        else:assert 'pending_GPU52E0_projection'not in value
    local=ROOT/'chat_tools.py';installed=RUNTIME/'chat_tools.py';assert local.read_bytes()==installed.read_bytes()
    report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='fresh_installed_GPU52E0_pending_evidence_scope_and_projection_routing_passed',tools=[t.name for t in tools],topics=topics,checked_components_unchanged=114,tool_source_sha256=hashlib.sha256(local.read_bytes()).hexdigest(),installed_tool_sha256=hashlib.sha256(installed.read_bytes()).hexdigest(),native_cached_provider_adoption_verified=False)
    (ROOT/'verification/projection-MCP-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(tools=6,topics=7,pending_GPU52E0_instruction_coverage=[448,450],components=114)))
if __name__=='__main__':asyncio.run(main())
