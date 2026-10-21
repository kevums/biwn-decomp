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
    c=p['latest_native_candidate'];pending=p['pending_native_candidate']
    assert c['candidate_frames']==25012 and c['control_frames']==24966 and c['native_record_returns']==4777
    assert c['final_video_equal'] and c['record_matrix_fresh_coverage']['native_record_matrix_returns']==190
    assert pending['profile']=='deck-shared-v37-record-loop-advance-v2' and pending['matrix_route']['final_differing_pixels']==22858
    assert not pending['default_promoted'] and not pending['fresh_gameplay_verified']
    component=p['current_native_input_prototype_progress'];assert component==p['latest_source_development']
    assert component['profile']=='input-dispatch-native-v5-rebased' and component['module_bytes']==10580
    assert component['runtime_source_statements_changed']==0 and component['checked_relocation_records']==48 and component['changed_bytes']==144
    assert not component['component_prefix_byte_identical'] and not component['prior_prefix_byte_identical']
    assert component['copied_SDK_byte_identical'] and component['installed_in_experimental_image']
    assert not component['installed_in_default_game'] and not component['private_task_stack_admission_qualified']
    s=p['current_input_stream_rebase_progress']
    assert s['primary_paired_cases']==s['second_CPU_paired_cases']==27
    assert s['actual_loader_calls_each']==s['payload_checks_each']==6 and s['native_stack']==458 and s['fallback_stack']==196
    assert s['primary_ordered_bus_checked'] and not s['second_CPU_ordered_bus_checked']
    assert not s['full_real_helper_bound_proven'] and s['scripted_transport_wait_signal_yield_boundary_remain']
    b=p['unqualified_native_input_image'];assert component['experimental_image']==b
    assert b['profile']=='native-input-callsite-v38-experimental' and b['new_disc_built']
    assert b['resident_bytes']==274368 and b['copy_bytes']==132160 and b['staging_clear_bytes']==132224 and b['initial_heap_bytes']==123520
    assert b['native_startup_cases']==b['Unicorn_startup_cases']==6 and b['heap_initialize_cases']==192
    assert b['completed_image_provider_pairs']==0 and b['first_violating_stack_bytes']==958 and b['available_bytes_in_failing_fixture']==956
    assert b['protected_task_bytes_changed']==[62,63] and b['first_violation_PC']==0x1603fe and b['first_violation_SP']==0xc0966
    assert b['stack_failure_confirmed_two_CPUs'] and not b['full_path_stack_maximum_known']
    assert b['admission_reserve']==512 and not b['admission_reserve_sufficient']
    assert not b['default_promoted'] and not b['fresh_gameplay_verified'] and not b['installed_preview_changed']
    assert b['game_frames']==0 and not b['physical_console_verified'] and not b['arbitrary_IRQ_qualified']
    r=p['prepared_structured_stream_Reader'];assert r['new_predictions']==0 and not r['actual_schema_generation_support_tested'] and not r['default_promoted']
    assert p['current_default_Reader_progress']['version']==43 and not p['current_copied_Reader_progress']['current_source_reply_verified']
    f=p['current_status_frontend_progress'];assert f['portable_entry_version']==32 and f['default_brief_lines']==12
    assert p['proof_sha256']==sha(proof) and not p['whole_game_complete']

async def copied():
    entry=read(P/'lmstudio-home/mcp.json')['mcpServers']['local-ai-lab'];assert Path(entry['command']).is_relative_to(P)and Path(entry['args'][0]).is_relative_to(P)
    params=StdioServerParameters(command=entry['command'],args=entry['args'],env={**os.environ,**entry.get('env',{})},cwd=str(P/'runtime'))
    async with stdio_client(params)as(reader,writer):
        async with ClientSession(reader,writer,read_timeout_seconds=timedelta(seconds=60))as client:
            init=await client.initialize();names=[x.name for x in(await client.list_tools()).tools];answer=await client.call_tool('project_evidence',{'topic':'status'})
    raw=answer.model_dump(mode='json');p=json.loads(raw['content'][0]['text']);assert not answer.isError and len(names)==18
    validate(p,P/'workbench/verification/native-Deck-current-status-v1-current.json')
    save(V/'input-image-stack-delivered-copied-MCP-response.json',dict(status='terminal_actual_copied_MCP_preserves_baseline_and_failed_v37_v38_gates',server=init.serverInfo.model_dump(mode='json'),tools=names,result=raw,new_predictions=0,new_training=False));print('Copied MCP',len(names),'image stack failure preserved',flush=True)

def main():
    load(ROOT)
    with ReferenceBridge()as bridge:p=bridge.call('project_evidence',{'topic':'status'});meta=bridge.metadata
    validate(p,V/'native-Deck-current-status-v1-current.json');assert len(meta['tools'])==19
    save(V/'input-image-stack-delivered-current-MCP-response.json',dict(status='terminal_actual_Root_MCP_preserves_baseline_and_failed_v37_v38_gates',metadata=meta,result=p,new_predictions=0,new_training=False));print('Root MCP',len(meta['tools']),'image stack failure preserved',flush=True);asyncio.run(copied())

if __name__=='__main__':main()
