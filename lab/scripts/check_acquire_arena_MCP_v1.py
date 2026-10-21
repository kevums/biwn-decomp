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
    c=p['latest_native_candidate'];pending=p['pending_native_candidate'];image=p['unqualified_native_input_image']
    assert c['candidate_frames']==25012 and c['native_record_returns']==4777 and c['final_video_equal']
    assert pending['matrix_route']['final_differing_pixels']==22858 and not pending['default_promoted']
    assert image['profile']=='native-input-callsite-v38-experimental' and image['stack_failure_confirmed_two_CPUs'] and image['first_violating_stack_bytes']==958 and not image['default_promoted']
    a=p['current_acquire_arena_stack_progress'];component=p['current_native_input_prototype_progress']
    assert component==p['latest_source_development'] and component['profile']=='input-dispatch-native-v6-arena-admission'
    assert component['module_bytes']==10580 and component['resource_adapter_bytes']==676 and component['copied_SDK_byte_identical']
    assert component['same_v5_bytes_except_one_reserve_immediate'] and component['all_symbol_addresses_unchanged']
    assert not component['installed_in_experimental_image'] and not component['new_disc_built'] and not component['default_promoted']
    assert a['primary_paired_cases']==a['pinned_CPU_paired_cases']==27
    assert a['actual_loads_each']==a['actual_blitter_copies_each']==a['payload_checks_each']==a['controlled_loader_yields_each']==6
    assert a['parked_state_checks_each']==21 and a['native_routes_each']==a['supervisor_fallback_each']==a['valid_headroom_fallback_each']==9
    assert a['headroom_fixture_offset']==800 and a['old500fallback_not_qualified']
    assert a['native_guest_stack']==786 and a['fallback_guest_stack']==524
    assert a['private_scratch_used']==180 and a['private_scratch_usable']==224 and a['minimum_private_SP_offset']==60
    assert a['private_comparison_exclusion_bytes']==224 and a['private_raw_bus_differences']==746 and a['private_final_RAM_differing_cases']==2 and not a['runtime_RAM_normalized']
    assert a['primary_ordered_public_bus_and_all_parked_writes_checked'] and not a['pinned_ordered_CPU_bus_checked'] and a['all_final_contexts_match']
    assert a['input_bytes']==10580 and a['input_byte_changes']==1 and a['input_reserve']==768 and not a['input_reserve_global_bound_proven']
    assert a['entry_route_cases']==20188 and a['preflight_stack']==36
    assert a['adapter_only_identity_cases']==432 and a['identity_valid_slots']==101 and a['identity_invalid_ids']==7 and a['identity_C_body_RTS_provider']
    assert a['new_RAM_reserved']==0 and a['adapter_fixture_address']==0x1f0000 and a['adapter_stubs']==5
    assert a['rejected_gap']==448 and a['rejected_gap_completed_pairs']==6 and a['rejected_gap_parked_state_corruption']
    assert not a['scratch_lifetime_alias_qualified'] and not a['real_task_switch_qualified'] and not a['arbitrary_IRQ_qualified'] and not a['fresh_gameplay_verified']
    assert not a['new_disc_built'] and not a['installed_preview_changed'] and a['new_predictions']==a['optimizer_updates']==0
    assert p['current_status_frontend_progress']['portable_entry_version']==33 and p['current_status_frontend_progress']['default_brief_lines']==12
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
    save(V/'acquire-arena-delivered-copied-MCP-response.json',dict(status='terminal_actual_copied_MCP_preserves_source_repair_and_failed_v37_v38_images',server=init.serverInfo.model_dump(mode='json'),tools=names,result=raw,new_predictions=0,new_training=False));print('Copied MCP',len(names),'source repair and failed images preserved',flush=True)

def main():
    load(ROOT)
    with ReferenceBridge()as bridge:p=bridge.call('project_evidence',{'topic':'status'});meta=bridge.metadata
    validate(p,V/'native-Deck-current-status-v1-current.json');assert len(meta['tools'])==19
    save(V/'acquire-arena-delivered-current-MCP-response.json',dict(status='terminal_actual_Root_MCP_preserves_source_repair_and_failed_v37_v38_images',metadata=meta,result=p,new_predictions=0,new_training=False));print('Root MCP',len(meta['tools']),'source repair and failed images preserved',flush=True);asyncio.run(copied())

if __name__=='__main__':main()
