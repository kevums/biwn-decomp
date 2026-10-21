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
    assert n==p['native_geometry_record_loop_progress']==p['native_scene_draw_progress']['pending_record_loop_candidate']
    component=p['current_native_input_prototype_progress'];assert p['latest_source_development']==component
    assert component['profile']=='native-191f4-input-dispatch-prototype-v1'and component['artifact_type']=='source_component_prototype'
    assert component['native_component_cases']==425 and component['captured_walking_cases']==194
    assert component['module_bytes']==10240 and component['C_stack_bytes']==276 and component['copied_SDK_byte_identical']
    assert not component['new_disc_built']and not component['caller_191F4_ABI_qualified']and not component['yielding_or_IRQ_qualified']
    r=p['local_record_loop_Repair_progress'];assert r['actual_Repair_predictions']==1 and r['seconds']==19.48 and not r['strict_compile_pass']and r['raw_candidate_byte_identical_to_failed_Author']
    reader=p['current_copied_Reader_progress'];assert reader['latest_source_changed_since_last_prediction']and not reader['current_source_reply_verified']
    assert reader['default_reader_version']==43 and reader['words']==99 and reader['seconds']==8.27
    assert reader['CLI_start_to_first_text_seconds']==18.94 and reader['CLI_start_to_completion_seconds']==25.18
    assert p['current_default_Reader_progress']['version']==43
    diagnosis=p['current_equal_state_diagnostic_progress']
    assert diagnosis['lanes']==12 and diagnosis['actual_recovered_C_integrator_transitions']==627
    assert diagnosis['unchanged_replicas_exact']and not diagnosis['fresh_matrix_gate_waived']
    assert diagnosis['motion_candidate_origin_nonzero_steps']==dict(native=22,original=23)
    timing=p['current_input_timing_progress'];assert timing['connected_original_dispatch_and_division_cases']==425 and timing['captured_walking_cases']==194
    assert timing['observer_preserves_all_prior_rows'] and not timing['fresh_matrix_gate_waived']
    lanes=timing['lane_summary'];assert [lanes['candidate'][k]['walking_clock_ticks']for k in ['native','original']]==[287,290]
    assert [lanes['candidate'][k]['movement_steps']for k in ['native','original']]==[22,23]
    assert [lanes['control'][k]['walking_clock_ticks']for k in ['native','original']]==[293,293]
    assert p['prepared_local_input_timing_analyst']['new_predictions']==0
    assert p['proof_sha256']==sha(proof)and not p['whole_game_complete']

async def copied():
    entry=read(P/'lmstudio-home/mcp.json')['mcpServers']['local-ai-lab'];assert Path(entry['command']).is_relative_to(P)and Path(entry['args'][0]).is_relative_to(P)
    params=StdioServerParameters(command=entry['command'],args=entry['args'],env={**os.environ,**entry.get('env',{})},cwd=str(P/'runtime'))
    async with stdio_client(params)as(reader,writer):
        async with ClientSession(reader,writer,read_timeout_seconds=timedelta(seconds=60))as client:
            init=await client.initialize();names=[x.name for x in(await client.list_tools()).tools];answer=await client.call_tool('project_evidence',{'topic':'status'})
    raw=answer.model_dump(mode='json');p=json.loads(raw['content'][0]['text']);assert not answer.isError and len(names)==18
    validate(p,P/'workbench/verification/native-Deck-current-status-v1-current.json')
    save(V/'native-input-component-delivered-copied-MCP-response.json',dict(status='terminal_actual_copied_MCP_preserves_baseline_and_failed_v37_gate',server=init.serverInfo.model_dump(mode='json'),tools=names,result=raw,new_predictions=0,new_training=False));print('Copied MCP',len(names),'pending failure preserved',flush=True)

def main():
    load(ROOT)
    with ReferenceBridge()as bridge:p=bridge.call('project_evidence',{'topic':'status'});meta=bridge.metadata
    validate(p,V/'native-Deck-current-status-v1-current.json');assert len(meta['tools'])==19
    save(V/'native-input-component-delivered-current-MCP-response.json',dict(status='terminal_actual_Root_MCP_preserves_baseline_and_failed_v37_gate',metadata=meta,result=p,new_predictions=0,new_training=False));print('Root MCP',len(meta['tools']),'pending failure preserved',flush=True);asyncio.run(copied())

if __name__=='__main__':main()
