"""Installed current GPU4D80 evidence, count meanings and remaining renderer scripts."""
import asyncio,json
from datetime import datetime,timezone
from check_audio_native_mcp import ROOT,RUNTIME,unpack
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
async def main():
    params=StdioServerParameters(command=str(RUNTIME/'.venv/bin/python'),args=[str(RUNTIME/'chat_tools.py')],cwd=str(RUNTIME))
    async with stdio_client(params)as(r,w):
        async with ClientSession(r,w)as client:
            await client.initialize();names=[t.name for t in(await client.list_tools()).tools];topics={t:unpack(await client.call_tool('project_evidence',{'topic':t}))for t in ['rendering','animation_images','movement_matrix','status','resources']}
    for value in topics.values():
        assert value['checked_components']==114 and value['processor_components']=={'CPU':111,'GPU':3}and not value['working_game_reconstruction']
        g=value['live_GPU4D80_geometry'];assert g['GPU4D80_transform_C_real']and g['GPU4D80_transform_live_calls']==g['CPU_E0A6_live_calls']==1008 and g['CPU_E0A6_source_instruction_coverage']==[10,10]
        assert g['GPU_geometry_record_counts']==[0,55]and g['record_builder_added_record_counts']==[4]and g['geometry_record_count_values']==[4,59]
        assert g['CPU_bus_physical_address_mask']=='0x00ffffff'and g['C_CPU_bus_high_byte_aliases']==870 and not g['full_GPU_context_cross_kernel_proved']and not g['full_game_viewport_proved']
        scripts=value['live_render_queue'];assert len(scripts['render_scene_overlay_script_targets'])==6 and sum(n>0 for n in scripts['render_scene_overlay_script_call_counts'].values())==4
        movement=value['movement_matrix_scope'];assert movement['whole_scene_E220_submissions']==3488 and movement['geometry_record_builder_E220_calls']==0 and movement['geometry_record_builder_E220_provider_linked']
    p=topics['rendering']['GPU_geometry_program'];assert p['GPU_cases']==128 and p['source_instruction_coverage']==[434,434]and p['host_guards']==13 and p['initial_GPU_RAM_supplied']and not p['original_GPU_core_calls_on_C_side']
    sizes={k:len(json.dumps(v).encode())for k,v in topics.items()};assert len(names)==6 and max(sizes.values())<35000
    report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='fresh_installed_GPU4D80_scope_counters_and_lower_scripts_passed',tools=names,topics=topics,payload_bytes_by_topic=sizes,scope='Fresh installed process only; native Chat latest response/provider adoption separately checked.')
    (ROOT/'verification/GPU-geometry-MCP-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(tools=6,topics=5,GPU4D80_calls=1008,configured_render_scripts=6,reached_render_scripts=4,payload_bytes=sizes)))
if __name__=='__main__':asyncio.run(main())
