"""Fresh installed evidence tools distinguish current C loading from historical prefixes."""
import asyncio,hashlib,json
from datetime import datetime,timezone
from check_audio_native_mcp import ROOT,RUNTIME,unpack
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
async def main():
 params=StdioServerParameters(command=str(RUNTIME/'.venv/bin/python'),args=[str(RUNTIME/'chat_tools.py')],cwd=str(RUNTIME))
 async with stdio_client(params)as(r,w):
  async with ClientSession(r,w)as client:
   await client.initialize();tools=(await client.list_tools()).tools;assert len(tools)==6
   evidence={topic:unpack(await client.call_tool('project_evidence',{'topic':topic}))for topic in ['interior_rendering','C_draw_slice','local_code_authorship','scene_loading','status']}
 cp=evidence['interior_rendering']['current_checkpoint'];assert cp['published_components']==135 and cp['processor_components']=={'CPU':122,'GPU':13}and cp['cases']==24 and cp['C_loaded_pipeline']and cp['source_C_loader_verified']and not cp['original_loader_prefix_used_on_C_side']and not cp['loader_to_renderer_device_or_RAM_reset']
 assert cp['disc_transfers']==120 and cp['transferred_bytes']==8763648 and cp['loader_fullCPU_source_instruction_coverage']==[386,807]and cp['loader_host_guards']==21
 assert not cp['source_boundary_transition_cleanup_verified']and not cp['interior0_two_actor_records_verified']and not cp['actual_boundary_transition_or_scheduler_loading_yields']and not cp['full_game_complete']and not cp['playable']and not cp['native_Chat_verified']
 assert cp['resident_experimental']and cp['resident_standalone_instruction_coverage']==[1192,1275]and cp['geometry_reset_seed_RAM_fixture_retained']and not cp['global_GPU_context_proved']
 assert evidence['C_draw_slice']['current_interior_checkpoint']['C_loaded_pipeline']and evidence['C_draw_slice']['current_mode1_street_checkpoint']['render_cycles']==1008
 assert evidence['local_code_authorship']['total_local_model_case_bodies']==171 and evidence['local_code_authorship']['selected_components']==135
 assert evidence['scene_loading']['current_C_loaded_interior_pipeline']['C_loaded_pipeline']and evidence['status']['latest_interior_scene']['C_loaded_pipeline']
 assert (ROOT/'chat_tools.py').read_bytes()==(RUNTIME/'chat_tools.py').read_bytes()
 report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='fresh_installed_current_C_loaded_pipeline_scoped_evidence_passes',tools=[t.name for t in tools],results=evidence,installed_code_sha256=hashlib.sha256((RUNTIME/'chat_tools.py').read_bytes()).hexdigest(),native_cached_provider_adoption_verified=False,native_Chat_verified=False)
 (ROOT/'verification/C-loaded-interior-MCP-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(tools=6,components=135,C_loaded_pipeline_cases=24,loader_instruction_coverage=[386,807],original_loader_prefix=False,native_Chat_verified=False)))
if __name__=='__main__':asyncio.run(main())
