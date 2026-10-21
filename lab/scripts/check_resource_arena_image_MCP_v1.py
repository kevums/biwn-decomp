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
    baseline=p['latest_native_candidate'];old37=p['pending_native_candidate'];old38=p['unqualified_native_input_image']
    assert baseline['candidate_frames']==25012 and baseline['native_record_returns']==4777 and baseline['final_video_equal']
    assert old37['matrix_route']['final_differing_pixels']==22858 and not old37['default_promoted']
    assert old38['first_violating_stack_bytes']==958 and old38['stack_failure_confirmed_two_CPUs'] and not old38['default_promoted']
    a=p['current_resource_arena_image_progress'];assert a==p['unqualified_resource_arena_image']
    component=p['current_native_input_prototype_progress'];assert component==p['latest_source_development']
    assert component['profile']=='input-v6-resource-arena-v39-partially-checked' and component['image_partial_qualification']==a
    assert component['installed_in_experimental_image'] and not component['installed_in_default_game'] and not component['default_promoted']
    assert a['profile']=='native-input-resource-arena-v39-experimental' and a['new_disc_built']
    assert a['input_bytes']==10580 and a['input_reserve']==768 and a['resource_adapter_bytes']==676 and a['resource_adapter_address']==0x17f078
    assert a['resident_reservation']==275072 and a['copy_bytes']==132864 and a['staging_clear_bytes']==132928 and a['staging_address']==0xddac0
    assert a['heap_start']==0x1a2040 and a['initial_heap_bytes']==122816 and a['new_private_arena_bytes']==0
    assert a['startup_cases_each_core']==6 and a['heap_initialize_cases']==192 and a['primary_caller_pairs']==a['pinned_caller_pairs']==27
    assert a['native_guest_stack']==786 and a['fallback_guest_stack']==524 and a['private_scratch_used']==180 and a['private_scratch_capacity']==224
    assert a['all_other_resident_code_and_arenas_immutable'] and a['caller_wait_transport_boundaries_still_controlled']
    assert a['primary_ordered_public_bus_checked'] and not a['pinned_ordered_CPU_bus_checked']
    assert a['current_private_comparison_exclusion']==224 and a['primary_private_bus_value_differences']==746 and a['private_final_RAM_differing_cases']==2
    assert a['real_wait_paired_cases']==32 and a['real_waits']==a['real_signals']==104 and a['real_switches']==208 and a['real_wait_GPU_submissions']==104
    assert a['parked_state_instruction_checks']==29160 and a['resource_task_guest_stack']==100 and a['resource_task_private_stack']==172
    assert a['other_task_guest_stack']==52 and a['other_task_private_stack']==156 and a['resource_task_supervisor_stack']==84
    assert a['real_wait_direct_resource_only'] and not a['real_wait_full_input_caller']
    assert a['selected_GPU_IRQ_paired_cases']==16 and len(a['selected_GPU_IRQ_phases'])==4 and a['selected_GPU_IRQ_returns_per_lane']==16
    assert a['IRQ_set_task_switches']==64 and a['IRQ_set_GPU_submissions']==32 and a['IRQ_all_interrupted_registers_banks_and102arena_slots_preserved'] and not a['IRQ_frame_fabricated']
    assert a['newly_copied_compiled_pieces']==4 and a['copied_new_pieces_identical'] and a['copied_prior_input_rebuild_reused'] and not a['full_source_only_copied_rebuild']
    for key in ['input_global_real_helper_IRQ_bound_proven','firmware_bit0_qualified','same_task_alias_reentry_qualified','arbitrary_IRQ_qualified','fresh_gameplay_verified','observer_qualified','all_final_address_gates_verified','default_promoted','installed_preview_changed','physical_console_verified']:
        assert not a[key],key
    assert a['game_frames']==a['new_predictions']==a['optimizer_updates']==0
    assert p['current_status_frontend_progress']['portable_entry_version']==34 and p['current_status_frontend_progress']['default_brief_lines']==12
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
    save(V/'resource-arena-image-delivered-copied-MCP-response.json',dict(status='terminal_actual_copied_MCP_preserves_partial_v39_and_baseline_failed_images',server=init.serverInfo.model_dump(mode='json'),tools=names,result=raw,new_predictions=0,new_training=False));print('Copied MCP',len(names),'partial v39 and failed images preserved',flush=True)

def main():
    load(ROOT)
    with ReferenceBridge()as bridge:p=bridge.call('project_evidence',{'topic':'status'});meta=bridge.metadata
    validate(p,V/'native-Deck-current-status-v1-current.json');assert len(meta['tools'])==19
    save(V/'resource-arena-image-delivered-current-MCP-response.json',dict(status='terminal_actual_Root_MCP_preserves_partial_v39_and_baseline_failed_images',metadata=meta,result=p,new_predictions=0,new_training=False));print('Root MCP',len(meta['tools']),'partial v39 and failed images preserved',flush=True);asyncio.run(copied())

if __name__=='__main__':main()
