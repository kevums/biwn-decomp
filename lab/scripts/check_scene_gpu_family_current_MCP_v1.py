"""Read the integrated v27 facts through both actual configured MCP transports."""
import asyncio,json,os,sys
from pathlib import Path
from datetime import timedelta
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha
sys.path.insert(0,str(ROOT))
from reference_mcp_bridge import ReferenceBridge
from native_deck_status_evidence_v1 import load

def validate(result,proof):
 candidate=result['latest_native_candidate'];gpu=result['native_scene_gpu_family_progress'];pending=result['pending_native_candidate'];local=result['local_scene_gpu_family_development_progress']
 assert candidate['native_module_bytes']==48410 and candidate['differing_video_frames']==8478 and candidate['final_video_equal']
 assert gpu['profile']=='deck-shared-v30-scene-gpu-commands-v1'and gpu['module_bytes']==48738 and gpu['initial_heap_bytes']==120320
 assert gpu['final_scene_cases']==772 and gpu['native_body_cases']==768 and gpu['actual_shared_monitor_CPU_lanes']==512
 assert gpu['new_internal_native_helper_integrations']==6 and gpu['new_unique_original_functions']==0
 assert gpu['global_original_helper_entries_preserved'] is False and gpu['inherited_global_GPU_redirects']
 assert gpu['pending_acceptance_wait_bypassed_inside_scene']
 assert gpu['connected_C_stack_bytes']==168 and gpu['C_stack_reserved']==208
 assert not gpu['fresh_gameplay_verified']and not gpu['installed_preview_changed']and not gpu['game_fidelity_verified']
 assert pending['profile']==gpu['profile']and not pending['new_fresh_gameplay_verified']
 assert local['actual_predictions']==2 and not local['model_source_installed']and not local['new_training']
 assert [x['accepted']for x in local['roles']]==[False,False]
 assert result['proof_sha256']==sha(proof)

async def copied():
 config=P/'lmstudio-home/mcp.json';entry=read(config)['mcpServers']['local-ai-lab']
 assert Path(entry['command']).is_relative_to(P)and Path(entry['args'][0]).is_relative_to(P)
 params=StdioServerParameters(command=entry['command'],args=entry['args'],env={**os.environ,**entry.get('env',{})},cwd=str(P/'runtime'))
 async with stdio_client(params)as(reader,writer):
  async with ClientSession(reader,writer,read_timeout_seconds=timedelta(seconds=60))as client:
   init=await client.initialize();names=[x.name for x in(await client.list_tools()).tools];result=await client.call_tool('project_evidence',{'topic':'status'})
 raw=result.model_dump(mode='json');decoded=json.loads(raw['content'][0]['text']);assert not result.isError and len(names)==18
 validate(decoded,P/'workbench/verification/native-Deck-current-status-v1-current.json')
 save(V/'scene17-gpu-family-component-copied-MCP-response.json',dict(status='terminal_actual_copied_MCP_v30_components_pending_game_review_and_local_rejections_verified',server=init.serverInfo.model_dump(mode='json'),tools=names,result=raw,new_predictions=0,new_training=False,native_Chat_verified=False))
 print('Copied MCP:',init.serverInfo.version,len(names),flush=True)

def main():
 load(ROOT)
 with ReferenceBridge()as bridge:result=bridge.call('project_evidence',{'topic':'status'});metadata=bridge.metadata
 validate(result,V/'native-Deck-current-status-v1-current.json');assert len(metadata['tools'])==19
 save(V/'scene17-gpu-family-component-current-MCP-response.json',dict(status='terminal_actual_Root_MCP_v30_components_pending_game_review_and_local_rejections_verified',metadata=metadata,result=result,new_predictions=0,new_training=False))
 print('Root MCP:',metadata['server']['version'],len(metadata['tools']),flush=True);asyncio.run(copied())
if __name__=='__main__':main()
