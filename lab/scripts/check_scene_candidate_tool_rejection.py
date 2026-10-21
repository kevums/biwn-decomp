"""Fresh installed MCP rejects a malformed fixed-function candidate."""
import asyncio,json
from datetime import datetime,timezone
from check_audio_native_mcp import ROOT,RUNTIME,unpack
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
async def main():
 params=StdioServerParameters(command=str(RUNTIME/'.venv/bin/python'),args=[str(RUNTIME/'chat_tools.py')],cwd=str(RUNTIME))
 async with stdio_client(params)as(r,w):
  async with ClientSession(r,w)as client:
   await client.initialize();names={t.name for t in (await client.list_tools()).tools};assert 'verify_scene_record_candidate'in names
   result=unpack(await client.call_tool('verify_scene_record_candidate',dict(source='#include "biwn_scene_record_insert.h"\nint biwn_scene_record_insert( incomplete source\n')))
 assert result['status']=='candidate_rejected' and not result['verified']and not result['default_runtime_promoted']and not result['new_training']
 report=dict(status='fresh_installed_candidate_tool_rejection_pass',recorded_at=datetime.now(timezone.utc).isoformat(),result=result,native_Chat_tool_adoption_verified=False,scope='Malformed candidate rejected in fresh installed MCP; successful/nativeChat candidate checks remain separately required.')
 (ROOT/'verification/scene-candidate-tool-rejection-current.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
if __name__=='__main__':asyncio.run(main())
