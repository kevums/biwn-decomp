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
 c=result['latest_native_candidate'];outer=result['native_outer_compact_progress'];scene=result['native_scene_draw_progress'];display=result['native_display_list_progress']
 assert c['candidate_frames']==24985 and c['control_frames']==24969 and c['differing_video_frames']==7351
 assert c['native_scene_returns']==6299 and c['native_scene_helper_returns']==c['native_display_returns']==5297
 assert c['game_latched_button_RAM_differing_frames']==359 and c['frontend_button_schedule_differing_frames']==338
 assert c['minimum_sampled_heap_while_outer_active']==dict(candidate=19696,control=19696)
 assert c['native_outer_C_stack_bytes']==164 and c['native_outer_C_stack_reserved']==224 and c['native_outer_C_stack_margin']==60
 assert c['candidate_initial_heap_bytes']==139456 and c['total_reservation_bytes']==258432 and c['native_code_bytes']==89830
 assert sha(c['native_module'])==sha(display['final_deployed_payload'])==display['module_sha256']
 assert outer['outer_arena_bytes_reclaimed']==19392 and outer['initial_heap_increase_bytes']==outer['sampled_outer_active_heap_increase']==19136
 assert outer['fresh_gameplay_verified']and outer['live_heap_gain_measured']and not outer['global_heap_minimum_measured']
 assert outer['outer_C_stack_low_offsets']==dict(candidate=204,control=204)
 assert outer['actual_outer_boundary_observer_CPU_lanes']==128
 assert scene['current_fixed_input_video_comparison']['count']==437
 assert scene['fixed_input_control_layout_changes']['video_sha256']['count']==216
 new=result['latest_source_development'];assert new['profile']=='deck-shared-v33-geometry-records-v1'
 assert new['host_cases']==new['native_body_cases']==new['actual_disc_provider_cases']==512 and new['host_guards']==19
 assert new['prototype_scene_cases']==new['final_address_scene_cases']==772 and new['module_bytes']==54214
 assert new['new_unique_original_functions']==0 and new['connected_C_stack_bytes']==168 and new['C_stack_reserved']==208
 assert new['new_disc_built'] and not new['fresh_gameplay_verified'] and new['initial_heap_bytes']==134016
 assert new['actual_disc_provider_body_CPU_RAM_boundaries_match'] and not new['actual_disc_provider_bus_order_verified']
 assert c['final_video_equal']and not c['native_disc_fidelity_verified']and not c['installed_preview_changed']
 assert result['current_copied_Reader_progress']['words']==127 and result['current_copied_Reader_progress']['artifact_type_pass']
 assert result['current_copied_Reader_progress']['supplied_snapshot_factual_claims_approved']and not result['current_copied_Reader_progress']['complete_requested_briefing_approved']
 assert result['current_default_Reader_progress']['current_evidence_preflight_verified']and result['current_default_Reader_progress']['actual_prediction_verified']
 assert result['current_default_Reader_progress']['version']==38
 assert result['pending_native_candidate']['candidate_disc']==new['candidate_disc'] and not result['pending_native_candidate']['new_fresh_gameplay_verified']
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
 save(V/'geometry-records-delivered-copied-MCP-response.json',dict(status='terminal_actual_copied_MCP_readable_records_new_candidate_and_retained_v32_scope_verified',server=init.serverInfo.model_dump(mode='json'),tools=names,result=raw,new_predictions=0,new_training=False,native_Chat_verified=False))
 print('Copied MCP:',init.serverInfo.version,len(names),flush=True)

def main():
 load(ROOT)
 with ReferenceBridge()as bridge:result=bridge.call('project_evidence',{'topic':'status'});metadata=bridge.metadata
 validate(result,V/'native-Deck-current-status-v1-current.json');assert len(metadata['tools'])==19
 save(V/'geometry-records-delivered-current-MCP-response.json',dict(status='terminal_actual_Root_MCP_readable_records_new_candidate_and_retained_v32_scope_verified',metadata=metadata,result=result,new_predictions=0,new_training=False))
 print('Root MCP:',metadata['server']['version'],len(metadata['tools']),flush=True);asyncio.run(copied())
if __name__=='__main__':main()
