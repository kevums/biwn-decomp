"""Fresh installed fixed-function check; preserve accepted component metadata."""
import asyncio,json,hashlib
from datetime import datetime,timezone
from check_audio_native_mcp import ROOT,RUNTIME,unpack
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
async def main():
 source=ROOT/'projects/black-ice-white-noise/restoration/biwn_scene_record_insert.c';accepted=ROOT/'verification/local-scene-record-insert-checks-current.json';before=accepted.read_bytes();params=StdioServerParameters(command=str(RUNTIME/'.venv/bin/python'),args=[str(RUNTIME/'chat_tools.py')],cwd=str(RUNTIME))
 async with stdio_client(params)as(r,w):
  async with ClientSession(r,w)as client:
   await client.initialize();result=unpack(await client.call_tool('verify_scene_record_candidate',dict(source=source.read_text())));evidence=unpack(await client.call_tool('project_evidence',dict(topic='scene_record_insert')))
 assert result['verified']and result['cases']==284 and result['instruction_address_coverage']==[43,43]and result['native_CPU_cases']==27 and result['host_guards']==24
 assert accepted.read_bytes()==before and result['source_sha256']==hashlib.sha256(source.read_bytes()).hexdigest();assert evidence['native_Chat_authorship_verified']and not evidence['coordinator_C_body_edits']and not evidence['full_route_runtime_promoted']
 report=dict(status='fresh_installed_scene_candidate_success_and_evidence_pass',recorded_at=datetime.now(timezone.utc).isoformat(),result=result,evidence=evidence,accepted_component_pointer_unchanged=True,native_Chat_tool_adoption_verified=False,scope='Installed fixedfunctionMCP sink/checker accepts the exact earlier nativeChat-authored C. This MCP call itself is headless,not a new nativeChat execution; no source/runtime/weight promotion.')
 (ROOT/'verification/scene-candidate-tool-success-current.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],result['cases'],result['native_CPU_cases'],result['host_guards'])
if __name__=='__main__':asyncio.run(main())
