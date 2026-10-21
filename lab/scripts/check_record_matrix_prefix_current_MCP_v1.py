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
 f=read(V/'record-strides-fresh-reviewed-v1-current.json');b=read(V/'native-record-strides-disc-build-v1-current.json');c=result['latest_native_candidate'];n=result['native_geometry_records_progress'];local=result['latest_source_development']
 assert local['profile']=='deck-shared-v35-local-record-prologue-v1' and local['artifact_type']=='mixed_source_component_prototype_not_disc_image'
 assert local['actual_predictions']==1 and local['seconds']==44.56 and local['model_block_statement_edits']==0
 assert local['host_cases']==local['native_body_cases']==512 and local['host_guards']==19 and local['prototype_scene_cases']==772
 assert local['module_bytes']==54446 and local['body_C_stack_bytes']==108 and local['copied_prototype_module_byte_identical']
 assert not local['new_disc_built']and not local['model_source_installed']and not local['new_training']
 assert c['candidate_frames']==f['candidate_frames'] and c['control_frames']==f['control_frames']
 assert c['native_scene_returns']==f['native_scene_returns'] and c['native_record_returns']==f['native_record_returns']
 assert c['native_record_copy_returns']==f['native_record_copy_returns'] and c['native_record_matrix_returns']==f['native_record_matrix_returns']
 assert c['differing_video_frames']==f['video_differences'] and c['minimum_sampled_heap_while_outer_active']==f['minimum_sampled_heap_while_outer_active']
 assert c['native_module_bytes']==54134 and c['native_code_bytes']==b['linked_component_bytes'] and c['candidate_initial_heap_bytes']==134080
 assert c['new_nesting_verified'] and c['new_fresh_gameplay_verified'] and not c['native_disc_fidelity_verified'] and not c['whole_game_complete']
 assert n['profile']=='deck-shared-v34-record-strides-v1' and n['artifact_type']=='built_experimental_disc_fresh_route_reviewed'
 assert n['new_disc_built'] and n['fresh_gameplay_verified'] and n['whole_scene_actual_inherited_provider_cases']==772
 assert n['actual_record_shared_observer_CPU_lanes']==768 and n['module_bytes']==54134 and n['CPU_cycles_saved_each_fixture']==8080
 assert n['native_record_matrix_fresh_path_verified'] and n['native_record_matrix_returns']==0
 m=n['record_matrix_fresh_coverage']
 assert m['native_record_matrix_returns']==190 and m['original_record_matrix_returns']==266
 assert m['candidate_frames']==22536 and m['control_frames']==22363 and m['static_angle']==0
 assert m['final_video_equal'] and m['final_player_XZ_scene_floor_heading_equal']
 assert m['video_differences']==21803 and not m['final_render_batch_region_equal']
 assert m['outer_active_heap_bytes']is None and not m['outer_active_heap_measured']
 assert result['native_scene_draw_progress']['record_matrix_fresh_coverage']==m
 assert n['current_fixed_input_comparison_verified'] and n['current_fixed_input_video_comparison']['count']==450
 assert n['current_fixed_input_video_comparison']['first_frame']==378
 assert result['native_scene_draw_progress']['record_strides_fixed_input_progress']['held_buttons_identical']
 assert result['native_geometry_record_stride_progress']['new_disc_built'] and result['native_geometry_record_stride_progress']['fresh_gameplay_verified']
 assert 'pending_native_candidate'not in result and not c['installed_preview_changed']
 assert result['current_copied_Reader_progress']['latest_source_changed_since_last_prediction']and not result['current_copied_Reader_progress']['current_source_reply_verified']
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
 save(V/'record-matrix-prefix-v34-delivered-copied-MCP-response.json',dict(status='terminal_actual_copied_MCP_v34_separate_standard_and_matrix_routes_unpromoted_local_v35_scope_verified',server=init.serverInfo.model_dump(mode='json'),tools=names,result=raw,new_predictions=0,new_training=False,native_Chat_verified=False))
 print('Copied MCP:',init.serverInfo.version,len(names),flush=True)

def main():
 load(ROOT)
 with ReferenceBridge()as bridge:result=bridge.call('project_evidence',{'topic':'status'});metadata=bridge.metadata
 validate(result,V/'native-Deck-current-status-v1-current.json');assert len(metadata['tools'])==19
 save(V/'record-matrix-prefix-v34-delivered-current-MCP-response.json',dict(status='terminal_actual_Root_MCP_v34_separate_standard_and_matrix_routes_unpromoted_local_v35_scope_verified',metadata=metadata,result=result,new_predictions=0,new_training=False))
 print('Root MCP:',metadata['server']['version'],len(metadata['tools']),flush=True);asyncio.run(copied())
if __name__=='__main__':main()
