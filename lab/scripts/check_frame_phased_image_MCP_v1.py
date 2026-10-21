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
    assert p['latest_native_candidate']['candidate_frames']==25012 and p['latest_native_candidate']['native_record_returns']==4777
    assert p['pending_native_candidate']['matrix_route']['final_differing_pixels']==22858
    assert p['unqualified_native_input_image']['first_violating_stack_bytes']==958
    assert p['unqualified_resource_arena_image']['fresh_input_failure']['original_task_metadata_bytes_overwritten']==38
    f=p['current_frame_phased_image_progress'];assert f==p['unqualified_frame_phased_image']
    assert f['profile']=='native-frame-acquire-phased-v40-experimental'
    assert f['early_bytes']==1536 and f['tail_bytes']==240 and f['new_per_task_arena_bytes']==0
    assert f['resident_reservation']==275328 and f['copy_bytes']==133120 and f['initial_heap_bytes']==122560
    assert f['normal_component_cases']==631 and f['DIVS_RTE_cases']==192 and f['actual_image_task_provider_pairs']==634 and f['task_slots']==101
    assert f['static_leaf_C_phase_stack_bound']==184 and f['static_bound_excludes_helpers_and_IRQ'] and not f['all_global_stack_paths_proven']
    assert f['fresh_preflight_gate_files']==31 and f['Frame_observer_off_on_pairs']==24 and f['Frame_observer_calls']==834024
    assert f['copied_new_pieces']==5 and f['copied_new_piece_builds']==4 and f['unchanged_input_and_resource_copied_proofs_reused']
    assert f['candidate_frames']==34619 and f['control_frames']==25015
    assert f['candidate_Frame_calls']==f['candidate_Frame_returns']==75 and f['candidate_Frame_errors']==f['candidate_Frame_stack_outside']==0
    assert f['candidate_actor_dispatch_stack_outside']==f['candidate_actor_initialize_stack_outside']==630
    h=f['new_actor_init_failure'];assert h['frame']==8978 and h['private_gap']==448 and h['C_prologue_cumulative_metadata_bytes_clobbered']==26 and not h['fix_implemented']
    assert not f['default_promoted'] and not f['fresh_route_qualified'] and not f['installed_preview_changed'] and not f['whole_source_only_game_rebuild']
    assert f['new_predictions']==f['optimizer_updates']==0 and p['current_frame_phased_local_Reviewer_progress']['new_predictions']==0
    assert p['latest_source_development']==p['current_native_input_prototype_progress'] and p['latest_source_development']['profile']==f['profile']
    assert p['current_status_frontend_progress']['portable_entry_version']==36 and p['current_status_frontend_progress']['default_brief_lines']==12
    assert p['current_default_Reader_progress']['version']==43 and not p['current_copied_Reader_progress']['current_source_reply_verified']
    assert p['proof_sha256']==sha(proof) and not p['whole_game_complete']

async def copied():
    entry=read(P/'lmstudio-home/mcp.json')['mcpServers']['local-ai-lab'];assert Path(entry['command']).is_relative_to(P)and Path(entry['args'][0]).is_relative_to(P)
    params=StdioServerParameters(command=entry['command'],args=entry['args'],env={**os.environ,**entry.get('env',{})},cwd=str(P/'runtime'))
    async with stdio_client(params)as(reader,writer):
        async with ClientSession(reader,writer,read_timeout_seconds=timedelta(seconds=60))as client:
            init=await client.initialize();names=[x.name for x in(await client.list_tools()).tools];answer=await client.call_tool('project_evidence',{'topic':'status'})
    raw=answer.model_dump(mode='json');p=json.loads(raw['content'][0]['text']);assert not answer.isError and len(names)==18
    validate(p,P/'workbench/verification/native-Deck-current-status-v1-current.json')
    save(V/'frame-phased-image-delivered-copied-MCP-response.json',dict(status='terminal_actual_copied_MCP_preserves_frame_fix_actor_failure_and_baseline_failed_images',server=init.serverInfo.model_dump(mode='json'),tools=names,result=raw,new_predictions=0,new_training=False));print('Copied MCP',len(names),'v40 frame fix and actor failure preserved',flush=True)

def main():
    load(ROOT)
    with ReferenceBridge()as bridge:p=bridge.call('project_evidence',{'topic':'status'});meta=bridge.metadata
    validate(p,V/'native-Deck-current-status-v1-current.json');assert len(meta['tools'])==19
    save(V/'frame-phased-image-delivered-current-MCP-response.json',dict(status='terminal_actual_Root_MCP_preserves_frame_fix_actor_failure_and_baseline_failed_images',metadata=meta,result=p,new_predictions=0,new_training=False));print('Root MCP',len(meta['tools']),'v40 frame fix and actor failure preserved',flush=True);asyncio.run(copied())

if __name__=='__main__':main()
