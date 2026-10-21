"""Read current v26 evidence through both actual configured MCP transports."""
import asyncio,json,os,sys
from pathlib import Path
from datetime import timedelta
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha
sys.path.insert(0,str(ROOT))
from reference_mcp_bridge import ReferenceBridge
from native_deck_status_evidence_v1 import load

def validate(result,expected,proof):
    scene=result['native_scene_draw_progress']
    assert scene['profile']=='deck-shared-v26-scene-clear' and scene['native_clear_integrated']
    for k in ['native_clear_returns','native_rotation_returns','fresh_scene_native_returns','fresh_differing_video_frames','fresh_scene_helper_returns']:
        assert scene[k]==expected[k],k
    assert result['proof_sha256']==sha(proof)
    assert '5,360' in result['checked_current_summary'] and '8,160' in result['checked_current_summary']
    assert scene['fixed_input_comparison']['clear']['video_sha256']['count']==279
    assert scene['fixed_input_control_layout_changes']['video_sha256']['count']==33
    assert not scene['new_disc_fidelity_verified']
    assert scene['final_scene_cases']==772
    assert 'structured native E03Aclear' in scene['scope']
    local=result['local_scene_clear_development_progress']
    assert local['target_native_cases']==772 and local['host_cases']==256
    assert local['accepted_complete_functions']==1 and not local['model_source_installed']

async def copied(expected):
    config=P/'lmstudio-home/mcp.json';entry=read(config)['mcpServers']['local-ai-lab']
    assert Path(entry['command']).is_relative_to(P) and Path(entry['args'][0]).is_relative_to(P)
    params=StdioServerParameters(command=entry['command'],args=entry['args'],env={**os.environ,**entry.get('env',{})},cwd=str(P/'runtime'))
    async with stdio_client(params) as(reader,writer):
        async with ClientSession(reader,writer,read_timeout_seconds=timedelta(seconds=60))as client:
            init=await client.initialize();names=[x.name for x in(await client.list_tools()).tools];result=await client.call_tool('project_evidence',{'topic':'status'})
    raw=result.model_dump(mode='json');decoded=json.loads(raw['content'][0]['text']);assert not result.isError and len(names)==18
    validate(decoded,expected,P/'workbench/verification/native-Deck-current-status-v1-current.json')
    save(V/'scene17-clear-copied-MCP-response.json',dict(status='terminal_copied_MCP_actual_status_returns_native_clear_facts',server=init.serverInfo.model_dump(mode='json'),tools=names,result=raw,new_predictions=0,new_training=False,native_Chat_verified=False,source_sha256={str(p):sha(p)for p in [Path(__file__),config,Path(entry['args'][0])]}))
    print('Copied MCP:',init.serverInfo.version,len(names),flush=True)

def main():
    expected=load(ROOT)['native_scene_draw_progress']
    with ReferenceBridge()as bridge:
        result=bridge.call('project_evidence',{'topic':'status'});metadata=bridge.metadata
    validate(result,expected,V/'native-Deck-current-status-v1-current.json');assert len(metadata['tools'])==19
    save(V/'scene17-clear-current-MCP-response.json',dict(metadata=metadata,result=result,new_predictions=0,new_training=False,native_Chat_verified=False))
    print('Root MCP:',metadata['server']['version'],len(metadata['tools']),flush=True)
    asyncio.run(copied(expected))
if __name__=='__main__':main()
