"""Installed evidence distinguishes live geometry records from standalone GPU math."""
import asyncio,json
from datetime import datetime,timezone
from check_audio_native_mcp import ROOT,RUNTIME,unpack
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
async def main():
    params=StdioServerParameters(command=str(RUNTIME/'.venv/bin/python'),args=[str(RUNTIME/'chat_tools.py')],cwd=str(RUNTIME))
    async with stdio_client(params)as(r,w):
        async with ClientSession(r,w)as client:
            await client.initialize();names=[t.name for t in(await client.list_tools()).tools];topics={t:unpack(await client.call_tool('project_evidence',{'topic':t}))for t in ['rendering','animation_images','status','resources','movement_matrix']}
    for v in topics.values():
        assert v['checked_components']==113 and v['processor_components']=={'CPU':111,'GPU':2}and not v['working_game_reconstruction']
        g=v['live_geometry_records'];assert g['geometry_record_builder_fullCPU_real']and g['geometry_record_body_call_counts']=={'0x170a0':1008,'0xe3e0':3024,'0xe220':0}and g['geometry_record_count_values']==[4]and not g['geometry_nested_helper_scripts']
        scope=v['movement_matrix_scope'];assert scope['whole_scene_E220_submissions']==3488 and scope['world_recorded_E220_calls']==1440 and scope['actor_E220_calls_by_difference']==2048 and scope['geometry_record_builder_E220_calls']==0
        assert scope['geometry_record_builder_E220_provider_linked']and not scope['geometry_record_builder_E220_branch_executed']
        q=v['live_render_queue'];assert len(q['render_scene_overlay_script_targets'])==7 and sum(n>0 for n in q['render_scene_overlay_script_call_counts'].values())==5
        assert q['actual_C_sprite_decodes']==160 and not q['full_game_viewport_proved']and not q['full_scene_draw_executed']
    p=topics['rendering']['geometry_records_full_CPU'];assert p['CPU_cases']==512 and p['source_instruction_coverage']==[166,166]and p['actual_copy_calls']==5782 and p['actual_movement_matrix_submissions']==2569 and not p['scripted_helpers']
    p=topics['movement_matrix'];assert p['geometry_records_full_CPU']['actual_movement_matrix_submissions']==2569 and p['GPU_movement_matrix']['GPU_cases']==1025 and p['GPU_movement_matrix']['stored_raw_fraction_bits']==16
    sizes={k:len(json.dumps(v).encode())for k,v in topics.items()};assert len(names)==6 and max(sizes.values())<32000
    report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='fresh_installed_live_record_builder_standalone_matrix_and_script_scope_passed',tools=names,topics=topics,payload_bytes_by_topic=sizes,scope='Fresh installed process only; native latest provider/response not verified by this smoke.')
    (ROOT/'verification/geometry-records-MCP-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(tools=6,topics=5,live_matrix_submissions=0,standalone_matrix_submissions=2569,payload_bytes=sizes)))
if __name__=='__main__':asyncio.run(main())
