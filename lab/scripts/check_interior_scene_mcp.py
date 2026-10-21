"""Fresh installed six-tool evidence schema/contents; no native Chat adoption claim."""
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
   result={topic:unpack(await client.call_tool('project_evidence',{'topic':topic}))for topic in ['interior_rendering','C_draw_slice','local_code_authorship','status']}
 cp=result['interior_rendering']['current_checkpoint'];assert cp['published_components']==135 and cp['processor_components']=={'CPU':122,'GPU':13}and cp['cases']==24 and cp['GPU_submissions']==123 and cp['cases_with_raster']==12 and cp['C_resident_blits']==3118
 assert cp['source_wrappers_reached']['0xe0f2']==24 and cp['source_wrappers_reached']['0xe148']==33 and not cp['source_C_loader_verified']and not cp['global_GPU_context_proved']and not cp['full_game_complete']and not cp['playable']and not cp['native_Chat_verified']
 assert cp['resident_experimental']and cp['resident_standalone_instruction_coverage']==[1192,1275]
 street=result['C_draw_slice']['current_mode1_street_checkpoint'];assert street['cases']==16 and street['render_cycles']==1008 and street['GPU_submissions']==3024
 auth=result['local_code_authorship'];assert auth['selected_components']==135 and auth['total_local_model_case_bodies']==171 and [p['accepted_case_bodies']for p in auth['local_model_contributions']]==[73,67,31]
 assert result['status']['checked_components']==135 and result['status']['latest_interior_scene']['cases']==24
 assert (ROOT/'chat_tools.py').read_bytes()==(RUNTIME/'chat_tools.py').read_bytes()
 report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='fresh_installed_interior_and_street_scoped_evidence_matches135selectedcomponents',tools=[t.name for t in tools],results=result,installed_code_sha256=hashlib.sha256((RUNTIME/'chat_tools.py').read_bytes()).hexdigest(),native_cached_provider_adoption_verified=False)
 (ROOT/'verification/interior-scene-MCP-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(tools=6,selected_components=135,CPU=122,GPU=13,interior_cases=24,street_cases=16,native_Chat_verified=False)))
if __name__=='__main__':asyncio.run(main())
