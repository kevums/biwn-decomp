"""Actual Root/copied transports must retain v34 and expose v37's failed gate."""
import asyncio,json,os,sys
from pathlib import Path
from datetime import timedelta
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha
sys.path.insert(0,str(ROOT))
from reference_mcp_bridge import ReferenceBridge
from native_deck_status_evidence_v1 import load

def validate(p,proof):
    c=p['latest_native_candidate'];n=p['pending_native_candidate']
    assert c['candidate_frames']==25012 and c['control_frames']==24966 and c['native_record_returns']==4777 and c['differing_video_frames']==8717
    assert c['native_record_copy_returns']==8567 and c['native_record_matrix_returns']==0 and c['record_matrix_fresh_coverage']['native_record_matrix_returns']==190
    assert n['profile']=='deck-shared-v37-record-loop-advance-v2'and n['new_disc_built']and n['fresh_gameplay_tested']
    assert n['artifact_type']=='built_experimental_disc_tested_unpromoted_fidelity_gate_failed'
    assert n['standard_route']['candidate_frames']==25004 and n['standard_route']['control_frames']==24966
    assert n['standard_route']['native_record_returns']==4836 and n['standard_route']['native_record_copy_returns']==8663 and n['standard_route']['final_video_equal']
    m=n['matrix_route'];assert m['native_record_matrix_returns']==201 and m['original_record_matrix_returns']==266 and m['final_differing_pixels']==22858
    assert not m['baseline_final_video_gate_pass']and not m['final_video_equal']and not m['final_full_pose_equal']and m['final_integer_XZ_scene_floor_heading_equal']
    assert m['expanded_final_pose']['candidate']['camera_words'][-1]==1696 and m['expanded_final_pose']['control']['camera_words'][-1]==1697
    assert n['fixed_input_prefix']['count']==449 and p['native_scene_draw_progress']['current_fixed_input_video_comparison']['count']==450
    assert n['module_bytes']==54060 and n['native_code_bytes']==95152 and n['initial_heap_bytes']==134144 and n['qualification_gate_count']==23
    assert not n['fresh_gameplay_verified']and not n['default_promoted']and not n['final_matrix_video_comparison_pass']
    assert p['latest_source_development']==n==p['native_geometry_record_loop_progress']==p['native_scene_draw_progress']['pending_record_loop_candidate']
    r=p['local_record_loop_Repair_progress'];assert r['actual_Repair_predictions']==1 and r['seconds']==19.48 and not r['strict_compile_pass']and r['raw_candidate_byte_identical_to_failed_Author']
    assert p['current_copied_Reader_progress']['latest_source_changed_since_last_prediction']and not p['current_copied_Reader_progress']['current_source_reply_verified']
    assert p['proof_sha256']==sha(proof)and not p['whole_game_complete']

async def copied():
    entry=read(P/'lmstudio-home/mcp.json')['mcpServers']['local-ai-lab'];assert Path(entry['command']).is_relative_to(P)and Path(entry['args'][0]).is_relative_to(P)
    params=StdioServerParameters(command=entry['command'],args=entry['args'],env={**os.environ,**entry.get('env',{})},cwd=str(P/'runtime'))
    async with stdio_client(params)as(reader,writer):
        async with ClientSession(reader,writer,read_timeout_seconds=timedelta(seconds=60))as client:
            init=await client.initialize();names=[x.name for x in(await client.list_tools()).tools];answer=await client.call_tool('project_evidence',{'topic':'status'})
    raw=answer.model_dump(mode='json');p=json.loads(raw['content'][0]['text']);assert not answer.isError and len(names)==18
    validate(p,P/'workbench/verification/native-Deck-current-status-v1-current.json')
    save(V/'record-loop-pending-delivered-copied-MCP-response.json',dict(status='terminal_actual_copied_MCP_preserves_baseline_and_failed_v37_gate',server=init.serverInfo.model_dump(mode='json'),tools=names,result=raw,new_predictions=0,new_training=False));print('Copied MCP',len(names),'pending failure preserved',flush=True)

def main():
    load(ROOT)
    with ReferenceBridge()as bridge:p=bridge.call('project_evidence',{'topic':'status'});meta=bridge.metadata
    validate(p,V/'native-Deck-current-status-v1-current.json');assert len(meta['tools'])==19
    save(V/'record-loop-pending-delivered-current-MCP-response.json',dict(status='terminal_actual_Root_MCP_preserves_baseline_and_failed_v37_gate',metadata=meta,result=p,new_predictions=0,new_training=False));print('Root MCP',len(meta['tools']),'pending failure preserved',flush=True);asyncio.run(copied())

if __name__=='__main__':main()
