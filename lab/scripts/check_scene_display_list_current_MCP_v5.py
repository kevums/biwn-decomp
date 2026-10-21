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
 scene=result['native_scene_draw_progress'];display=result['native_display_list_progress'];candidate=result['latest_native_candidate']
 assert scene['profile']=='deck-shared-v27-scene-display-list-algorithm-v4'and scene['native_display_integrated']
 for k,v in dict(native_display_returns=5243,native_rotation_returns=5243,native_clear_returns=5243,fresh_scene_native_returns=6248,fresh_scene_helper_returns=26309,fresh_differing_video_frames=8375,held_input_differing_frames=457,candidate_frames=24990,control_frames=24963).items():assert scene[k]==v,(k,scene[k])
 assert scene['fixed_input_comparison']['display-list']['video_sha256']['count']==442
 assert scene['fixed_input_control_layout_changes']['video_sha256']['count']==72
 assert scene['minimum_sampled_heap_while_outer_active']==dict(candidate=816,control=816)
 assert scene['final_video_equal']and not scene['new_disc_fidelity_verified']and not scene['installed_preview_changed']
 assert display['disc_integrated']and display['fresh_gameplay_verified']and display['alias_nesting_verified']
 assert display['module_bytes']==48494 and display['connected_C_stack_bytes']==208 and display['connected_C_stack_margin']==0
 assert not display['game_fidelity_verified']and candidate['native_module_sha256']==display['module_sha256']
 assert result['proof_sha256']==sha(proof)
 reader=result['current_copied_Reader_progress'];assert reader['actual_predictions']==1 and reader['words']==156 and not reader['word_limit_pass']
 headroom=result['native_scene_dispatch_headroom_progress'];assert headroom['scene_C_stack_bytes']==168 and headroom['scene_C_stack_margin']==40 and headroom['module_bytes']==48410 and headroom['disc_integrated'] and headroom['new_disc_built'] and headroom['initial_heap_bytes']==120640 and not headroom['fresh_gameplay_verified']
 assert headroom['disc_integration_component_verification_complete']and headroom['final_existing_gates']==8 and headroom['exact_deployed_scene_cases']==772 and headroom['exact_deployed_body_cases']==1153 and not headroom['new_read_only_observers_qualified']

async def copied():
 config=P/'lmstudio-home/mcp.json';entry=read(config)['mcpServers']['local-ai-lab']
 assert Path(entry['command']).is_relative_to(P)and Path(entry['args'][0]).is_relative_to(P)
 params=StdioServerParameters(command=entry['command'],args=entry['args'],env={**os.environ,**entry.get('env',{})},cwd=str(P/'runtime'))
 async with stdio_client(params)as(reader,writer):
  async with ClientSession(reader,writer,read_timeout_seconds=timedelta(seconds=60))as client:
   init=await client.initialize();names=[x.name for x in(await client.list_tools()).tools];result=await client.call_tool('project_evidence',{'topic':'status'})
 raw=result.model_dump(mode='json');decoded=json.loads(raw['content'][0]['text']);assert not result.isError and len(names)==18
 validate(decoded,P/'workbench/verification/native-Deck-current-status-v1-current.json')
 save(V/'scene17-direct-dispatch-final-image-copied-MCP-response.json',dict(status='terminal_actual_copied_MCP_v27_tested_disc_v29_pending_image_and_Reader36_facts_verified',server=init.serverInfo.model_dump(mode='json'),tools=names,result=raw,new_predictions=0,new_training=False,native_Chat_verified=False))
 print('Copied MCP:',init.serverInfo.version,len(names),flush=True)

def main():
 load(ROOT)
 with ReferenceBridge()as bridge:result=bridge.call('project_evidence',{'topic':'status'});metadata=bridge.metadata
 validate(result,V/'native-Deck-current-status-v1-current.json');assert len(metadata['tools'])==19
 save(V/'scene17-direct-dispatch-final-image-current-MCP-response.json',dict(status='terminal_actual_Root_MCP_v27_tested_disc_v29_pending_image_and_Reader36_facts_verified',metadata=metadata,result=result,new_predictions=0,new_training=False))
 print('Root MCP:',metadata['server']['version'],len(metadata['tools']),flush=True);asyncio.run(copied())
if __name__=='__main__':main()
