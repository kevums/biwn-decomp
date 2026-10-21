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
 c=result['latest_native_candidate'];new=result['latest_source_development'];scene=result['native_scene_draw_progress']
 assert c['candidate_frames']==25020 and c['control_frames']==24965 and c['native_scene_returns']==5668
 assert c['differing_video_frames']==8764 and c['native_record_returns']==4666 and c['native_record_copy_returns']==8381 and c['native_record_matrix_returns']==0
 assert c['native_scene_helper_returns']==8381 and 'E3E0'in c['native_scene_helper_returns_scope']
 assert c['minimum_sampled_heap_while_outer_active']==dict(candidate=14256,control=14256)
 assert c['native_module_bytes']==54214 and c['native_code_bytes']==95306 and c['total_reservation_bytes']==263872
 assert c['new_nesting_verified']and c['new_fresh_gameplay_verified']and c['all_runtime_error_pending_outside_counts_zero']
 assert not c['native_disc_fidelity_verified'] and not c['installed_preview_changed'] and not c['whole_game_complete']
 assert new['whole_scene_actual_inherited_provider_cases']==772 and new['actual_record_shared_observer_CPU_lanes']==768
 assert new['fresh_gameplay_verified'] and not new['native_record_matrix_fresh_path_verified'] and new['actual_local_predictions_v1_v2_total']==3
 assert new['current_fixed_input_video_comparison']['count']==448 and scene['current_fixed_input_video_comparison']['count']==448
 assert result['local_geometry_records_compact_progress']['truncation_correctly_classified'] and not result['local_geometry_records_compact_progress']['repair_run']
 assert 'pending_native_candidate'not in result
 assert result['current_copied_Reader_progress']['latest_source_changed_since_last_prediction']
 assert not result['current_copied_Reader_progress']['current_source_reply_verified']
 assert c['final_video_equal'] and result['proof_sha256']==sha(proof)

async def copied():
 config=P/'lmstudio-home/mcp.json';entry=read(config)['mcpServers']['local-ai-lab']
 assert Path(entry['command']).is_relative_to(P)and Path(entry['args'][0]).is_relative_to(P)
 params=StdioServerParameters(command=entry['command'],args=entry['args'],env={**os.environ,**entry.get('env',{})},cwd=str(P/'runtime'))
 async with stdio_client(params)as(reader,writer):
  async with ClientSession(reader,writer,read_timeout_seconds=timedelta(seconds=60))as client:
   init=await client.initialize();names=[x.name for x in(await client.list_tools()).tools];result=await client.call_tool('project_evidence',{'topic':'status'})
 raw=result.model_dump(mode='json');decoded=json.loads(raw['content'][0]['text']);assert not result.isError and len(names)==18
 validate(decoded,P/'workbench/verification/native-Deck-current-status-v1-current.json')
 save(V/'geometry-records-v33-delivered-copied-MCP-response.json',dict(status='terminal_actual_copied_MCP_v33_fresh_records_and_compact_Author_scope_verified',server=init.serverInfo.model_dump(mode='json'),tools=names,result=raw,new_predictions=0,new_training=False,native_Chat_verified=False))
 print('Copied MCP:',init.serverInfo.version,len(names),flush=True)

def main():
 load(ROOT)
 with ReferenceBridge()as bridge:result=bridge.call('project_evidence',{'topic':'status'});metadata=bridge.metadata
 validate(result,V/'native-Deck-current-status-v1-current.json');assert len(metadata['tools'])==19
 save(V/'geometry-records-v33-delivered-current-MCP-response.json',dict(status='terminal_actual_Root_MCP_v33_fresh_records_and_compact_Author_scope_verified',metadata=metadata,result=result,new_predictions=0,new_training=False))
 print('Root MCP:',metadata['server']['version'],len(metadata['tools']),flush=True);asyncio.run(copied())
if __name__=='__main__':main()
