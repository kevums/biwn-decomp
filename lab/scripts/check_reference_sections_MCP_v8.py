"""Exercise the new source-section retrieval with real stdio MCP, before installation."""
import asyncio,json,sys,os,shutil
from datetime import datetime,timezone,timedelta
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
from run_biwn_native_fast_gameplay_route import sha,save
RUNTIME=Path.home()/'.lmstudio/local-ai-lab'
def unpack(result):
 if result.isError:raise AssertionError(str(result))
 return json.loads(next(block.text for block in result.content if block.type=='text'))
async def main():
 out=ROOT/'verification/reference-sections-MCP-v8'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 for name in ['reference_sections_v1.py','chat_tools_current_v8.py']:
  target=RUNTIME/name
  if target.exists():assert target.read_bytes()==(ROOT/name).read_bytes(),'Preserve changed runtime source'
  else:shutil.copy2(ROOT/name,target)
 calls=[]
 with(out/'server-stderr.log').open('w')as errors:
  async with stdio_client(StdioServerParameters(command=str(RUNTIME/'.venv/bin/python'),args=[str(RUNTIME/'chat_tools_current_v8.py')],cwd=str(RUNTIME)),errlog=errors)as(r,w):
   async with ClientSession(r,w,read_timeout_seconds=timedelta(seconds=120))as client:
    await client.initialize();tools=await client.list_tools();names=[x.name for x in tools.tools];assert len(names)==18
    for query,expected in [('Schreiner2026 Study2A design procedure measured AI aversion',{9,20}),('Schreiner2026 design methods all studies AI aversion measures',{6,9,12,20}),('Schreiner2026 PDF pages 9 20',{9,20})]:
     result=unpack(await client.call_tool('search_references',dict(domain='advertising',query=query,max_chunks=4)));sections=result['source_section_evidence'];pages={x['pdf_page']for x in sections};assert expected<=pages,(query,pages)
     assert all(Path(x['source']).name=='Schreiner et al (2026).pdf'and x['sha256']=='7da27946e1061ed9ab195c9a14c0be28f648d2e719fafff7236dd48b93248f71'for x in sections)
     if 'Study2A'in query:assert 6 not in pages and 12 not in pages
     calls.append(dict(name='search_references',query=query,response=result))
    bad=await client.call_tool('search_references',dict(domain='advertising',query='Schreiner2026 PDF page 999',max_chunks=4));assert bad.isError;calls.append(dict(name='out_of_range_page_rejected',isError=True))
    status=unpack(await client.call_tool('project_evidence',dict(topic='status')));assert status['experimental_build']['resident_bytes']==29876 and not status['whole_game_complete'];calls.append(dict(name='project_evidence',response=status))
    game=unpack(await client.call_tool('search_references',dict(domain='game',query='Black Ice White Noise restoration',max_chunks=2)));assert game['evidence']and 'source_section_evidence'not in game;calls.append(dict(name='game_search_unchanged',response=game))
 save(out/'calls.json',calls);inputs=[Path(__file__),ROOT/'reference_sections_v1.py',ROOT/'chat_tools_current_v8.py',RUNTIME/'reference_sections_v1.py',RUNTIME/'chat_tools_current_v8.py',out/'calls.json']
 state=dict(status='terminal_reference_section_MCP_v8_pass',directory=str(out),tool_count=18,positive_reference_queries=3,out_of_range_rejected=True,current_game_status_unchanged=True,game_reference_search_unchanged=True,new_predictions=0,new_training=False,live_configuration_changed=False,source_sha256={str(p):sha(p)for p in inputs},scope=__doc__);save(out/'protocol.json',state);save(ROOT/'verification/reference-sections-MCP-v8-current.json',state);print(json.dumps({k:state[k]for k in ['status','tool_count','positive_reference_queries','out_of_range_rejected']}))
if __name__=='__main__':asyncio.run(main())
