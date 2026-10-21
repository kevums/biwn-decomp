"""Real MCP stdio handshake/task and positive/negative source checks."""
import asyncio,json,sys
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
ROOT=Path(__file__).resolve().parents[1]
def unpack(result):
 return result.structuredContent or json.loads(next(c.text for c in result.content if c.type=='text'))
async def main():
 async with stdio_client(StdioServerParameters(command=str(ROOT/'.venv/bin/python'),args=[str(ROOT/'scripts/native_fact_chat_tools.py')],cwd=str(ROOT)))as(reader,writer):
  async with ClientSession(reader,writer)as client:
   await client.initialize();names=[t.name for t in(await client.list_tools()).tools];assert set(names)=={'get_biwn_instruction_task','verify_biwn_instruction_candidate','lift_biwn_instruction_task'}
   task=await client.call_tool('get_biwn_instruction_task',{});assert not task.isError;body=unpack(task);assert body['gold_C_supplied']==False and body['routine']=='format_pad'
   source=(ROOT/'projects/black-ice-white-noise/restoration/native-m68k/format-pad-reference.c').read_text();good=await client.call_tool('verify_biwn_instruction_candidate',dict(source=source));assert not good.isError;accepted=unpack(good);assert accepted['verified']and accepted['native_cases']==1668 and accepted['trace_cases']==1684
   bad=await client.call_tool('verify_biwn_instruction_candidate',dict(source='#include "/etc/passwd"\nvoid biwn_native_format_pad_body(uint32_t*r){}'));assert bad.isError
   lifted=await client.call_tool('lift_biwn_instruction_task',{});assert not lifted.isError;recovered=unpack(lifted);assert recovered['verified']and recovered['local_model_authored_C']==False
   report=dict(status='MCP_fact_task_native_positive_lifter_and_header_rejection_pass',tools=names,task_packet_sha256=body['packet_sha256'],positive=accepted,lifted=recovered,unsafe_include_rejected=True,native_Chat_verified=False,scope='ActualstdioMCP initialize/list/gettask/verify/lift calls. Coordinator positive C and deterministic lifter test plumbing/recovery,not local-model-authored C or native LM Studio Chat execution.')
   (ROOT/'verification/fact-chat-MCP-current.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],tools=names,native_cases=accepted['native_cases'],trace_cases=accepted['trace_cases'])),flush=True)
if __name__=='__main__':asyncio.run(main())
