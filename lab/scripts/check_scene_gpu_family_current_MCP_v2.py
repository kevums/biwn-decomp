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
 c=result['latest_native_candidate'];gpu=result['native_scene_gpu_family_progress'];outer=result['native_outer_inplace_progress'];d=result['native_display_list_progress']
 assert c['native_module_bytes']==48738 and c['candidate_frames']==25001 and c['control_frames']==24969
 assert c['differing_video_frames']==8481 and c['final_video_equal']and not c['native_disc_fidelity_verified']
 assert c['minimum_sampled_heap_while_outer_active']==dict(candidate=560,control=560)
 assert c['total_internal_compiled_helpers']==16
 assert sha(c['native_module'])==sha(d['final_deployed_payload'])==d['module_sha256']==gpu['module_sha256']
 assert gpu['fresh_gameplay_verified']and gpu['all_monitors_clear_and_quiescent']and gpu['fresh_scene_native_returns']==6318
 assert gpu['fresh_scene_helper_returns']==5304 and gpu['native_display_returns']==5304
 assert gpu['connected_C_stack_bytes']==168 and gpu['minimum_sampled_heap_while_outer_active']==dict(candidate=560,control=560)
 assert gpu['inherited_global_GPU_redirects']and gpu['pending_acceptance_wait_bypassed_inside_scene']and not gpu['global_original_helper_entries_preserved']
 assert not gpu['current_fixed_input_v30_comparison_verified']and not gpu['installed_preview_changed']
 assert outer['C_stack_bytes']==164 and outer['previous_C_stack_bytes']==356 and outer['module_bytes']==6060
 assert outer['arena_bytes_reclaimed']==0 and not outer['disc_integrated']and not outer['fresh_gameplay_verified']
 assert result['latest_source_development']['profile']==outer['profile']
 assert 'pending_native_candidate'not in result
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
 save(V/'scene17-gpu-family-fresh-copied-MCP-response.json',dict(status='terminal_actual_copied_MCP_v30_fresh_and_outer_capacity_prototype_verified',server=init.serverInfo.model_dump(mode='json'),tools=names,result=raw,new_predictions=0,new_training=False,native_Chat_verified=False))
 print('Copied MCP:',init.serverInfo.version,len(names),flush=True)

def main():
 load(ROOT)
 with ReferenceBridge()as bridge:result=bridge.call('project_evidence',{'topic':'status'});metadata=bridge.metadata
 validate(result,V/'native-Deck-current-status-v1-current.json');assert len(metadata['tools'])==19
 save(V/'scene17-gpu-family-fresh-current-MCP-response.json',dict(status='terminal_actual_Root_MCP_v30_fresh_and_outer_capacity_prototype_verified',metadata=metadata,result=result,new_predictions=0,new_training=False))
 print('Root MCP:',metadata['server']['version'],len(metadata['tools']),flush=True);asyncio.run(copied())
if __name__=='__main__':main()
