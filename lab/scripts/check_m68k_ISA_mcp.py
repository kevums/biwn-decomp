"""Fresh installed ISA schema/definition and native/C path scoping."""
import asyncio,json
from check_audio_native_mcp import ROOT,RUNTIME,unpack
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
async def main():
 p=StdioServerParameters(command=str(RUNTIME/'.venv/bin/python'),args=[str(RUNTIME/'chat_tools.py')],cwd=str(RUNTIME))
 async with stdio_client(p)as(r,w):
  async with ClientSession(r,w)as client:
   await client.initialize();tools=(await client.list_tools()).tools;isa=unpack(await client.call_tool('project_evidence',{'topic':'m68k_isa'}));boot=unpack(await client.call_tool('project_evidence',{'topic':'boot_loader'}));C=unpack(await client.call_tool('project_evidence',{'topic':'nextstage_entry'}))
 assert len(tools)==6 and isa['SR_CCR_masks']==dict(X=16,N=8,Z=4,V=2,C=1)
 assert isa['no_current_user_program_execution'] and 'not flags'in isa['public_fixture_tool_scope']
 assert boot['separate_firmware_boot_progress']['source_stage_loading']['all_payload_bytes_match']
 assert boot['separate_C_game_chain_test']['initial60000byte_stub_supplied'] and not boot['separate_C_game_chain_test']['source_loaded_native_state_linked_into_C_chain']
 assert 'current_checkpoint'in C and not boot['whole_game_complete'];assert (ROOT/'chat_tools.py').read_bytes()==(RUNTIME/'chat_tools.py').read_bytes()
 report=dict(status='fresh_installed_ISA_and_boot_scope_checked',tools=[t.name for t in tools],ISA=isa,boot=boot,broader_C_chain_details_topic_available=True,native_Chat_refresh_verified=False)
 (ROOT/'verification/m68k-ISA-MCP-check.json').write_text(json.dumps(report,indent=2)+'\n');print('6tools; ISA masks correct; native/C boot paths distinct')
if __name__=='__main__':asyncio.run(main())
