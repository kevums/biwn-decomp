"""Installed initializer tool accepts exact checked source without promotion."""
import asyncio,json,hashlib
from datetime import datetime,timezone
from check_audio_native_mcp import ROOT,RUNTIME,unpack
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
async def main():
 accepted=ROOT/'verification/local-scene-initial-setup-release-checks-current.json';before=accepted.read_bytes();source=ROOT/'projects/black-ice-white-noise/restoration/biwn_scene_initial_setup.c';params=StdioServerParameters(command=str(RUNTIME/'.venv/bin/python'),args=[str(RUNTIME/'chat_tools.py')],cwd=str(RUNTIME))
 async with stdio_client(params)as(r,w):
  async with ClientSession(r,w)as client:
   await client.initialize();result=unpack(await client.call_tool('verify_scene_initial_candidate',dict(source=source.read_text())));evidence=unpack(await client.call_tool('project_evidence',dict(topic='scene_initial_setup')))
 assert result['verified']and result['cases']==284 and result['instruction_address_coverage']==[39,39]and result['native_CPU_cases']==27 and result['host_guards']==302
 assert accepted.read_bytes()==before and result['source_sha256']==hashlib.sha256(source.read_bytes()).hexdigest();assert evidence['linked_instruction_addresses']==198 and len(evidence['remaining_scripted_helpers'])==2 and not evidence['native_Chat_verified']and not evidence['coordinator_C_body_edits']
 report=dict(status='fresh_installed_initializer_candidate_and_evidence_pass',recorded_at=datetime.now(timezone.utc).isoformat(),result=result,evidence=evidence,accepted_component_pointer_unchanged=True,native_Chat_tool_adoption_verified=False,scope='Headless installed fixedfunctionMCP validator and evidence lookup. Local author/reviewer/repair used LMStudioAPIwhilelocked; no nativeChat authorship for10990,default promotion or new training.')
 (ROOT/'verification/scene-initial-candidate-tool-current.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],result['cases'],result['host_guards'])
if __name__=='__main__':asyncio.run(main())
