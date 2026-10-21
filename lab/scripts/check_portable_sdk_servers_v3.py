"""Run copied MCP servers from the copied Python environment and save real replies."""
import asyncio,json,sys,os
from datetime import datetime,timezone,timedelta
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
PACKAGE=Path(__file__).resolve().parents[2]
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def unpack(result):
 assert not result.isError,str(result)
 texts=[x.text for x in result.content if x.type=='text']
 if result.structuredContent:return result.structuredContent
 if len(texts)==1:
  try:return json.loads(texts[0])
  except ValueError:return None
 return None
async def main():
 plan=json.loads((PACKAGE/'portable-server-test-plan.json').read_text());config=json.loads((PACKAGE/'lmstudio-home/mcp.json').read_text());out=PACKAGE/'test-results'/('servers-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir(parents=True);results=[];inventory={}
 for name,entry in config['mcpServers'].items():
  with(out/(name+'-stderr.log')).open('w')as errors:
   async with stdio_client(StdioServerParameters(command=entry['command'],args=entry['args'],env={**os.environ,**entry.get('env',{})},cwd=str(Path(entry['args'][0]).parent)),errlog=errors)as(r,w):
    async with ClientSession(r,w,read_timeout_seconds=timedelta(seconds=180))as client:
     await client.initialize();listed=await client.list_tools();inventory[name]=[x.model_dump(mode='json')for x in listed.tools];save(out/'inventory.json',inventory)
     if name=='local-ai-lab':
      assert len(listed.tools)==18
      for i,call in enumerate(plan['calls']):
       result=await client.call_tool(call['name'],call['arguments']);raw=result.model_dump(mode='json');save(out/(str(i)+'-'+call['name']+'.json'),raw);parsed=unpack(result)
       if call['name']=='search_references':
        assert all(Path(row['source']).is_relative_to(PACKAGE/'runtime/corpus')for row in parsed['evidence'])
        if call['arguments'].get('domain')=='advertising':assert {9,20}<={row['pdf_page']for row in parsed['source_section_evidence']}
       if call['name']=='project_evidence'and call['arguments'].get('topic')=='status':assert parsed['experimental_build']['resident_bytes']==30036
       results.append(dict(name=call['name'],isError=bool(result.isError),images=sum(block.type=='image'for block in result.content)));save(out/'calls.json',results);print(name,call['name'],'returned',flush=True)
     else:
      tool={'biwn-instruction-workbench':'get_biwn_instruction_task','biwn-string-workbench':'get_biwn_string_task','biwn-compiler-workbench':'get_biwn_string_optimization_status'}[name]
      result=await client.call_tool(tool,{});save(out/(name+'-'+tool+'.json'),result.model_dump(mode='json'));parsed=unpack(result);assert parsed is not None
      results.append(dict(server=name,name=tool,isError=bool(result.isError),images=0));save(out/'calls.json',results);print(name,tool,'returned',flush=True)
  print(name,len(inventory[name]),'tools initialized',flush=True)
 state=dict(status='terminal_moved_copied_python_four_MCP_servers_ten_tool_kinds_pass',directory=str(out),package=str(PACKAGE),python=sys.executable,registered_servers=list(inventory),main_tools=18,main_calls=8,total_calls=len(results),tested_tool_kinds=len({x['name']for x in results}),other_server_tool_calls_tested=True,new_predictions=0,new_training=False,scope=__doc__);save(out/'protocol.json',state);save(PACKAGE/'portable-server-test-current.json',state);print(json.dumps(state))
if __name__=='__main__':asyncio.run(main())
