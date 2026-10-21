"""Install the tested section-aware MCP entry, preserving all other configuration."""
import json,shutil,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from reference_mcp_bridge import ReferenceBridge
from run_biwn_native_fast_gameplay_route import sha,save

def main():
 v=ROOT/'verification';checked=json.loads((v/'reference-sections-MCP-v10-current.json').read_text());assert checked['status']=='terminal_reference_section_MCP_v10_pass'
 for p,h in checked['source_sha256'].items():assert sha(p)==h,p
 out=v/'reference-section-frontend-install'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);config=Path.home()/'.lmstudio/mcp.json';old=json.loads(config.read_text());shutil.copy2(config,out/'previous-mcp.json');new=json.loads(json.dumps(old));entry=new['mcpServers']['local-ai-lab'];runtime=Path(entry['args'][0]).parent;assert Path(entry['args'][0]).name=='chat_tools_current_v7.py';entry['args']=[str(runtime/'chat_tools_current_v10.py')];config.write_text(json.dumps(new,indent=2)+'\n')
 assert {k:x for k,x in old['mcpServers'].items()if k!='local-ai-lab'}=={k:x for k,x in new['mcpServers'].items()if k!='local-ai-lab'}
 try:
  with ReferenceBridge()as bridge:
   response=bridge.call('search_references',dict(domain='advertising',query='Schreiner2026 Study2A design procedure AI aversion measurement',max_chunks=4));connection=bridge.metadata
  assert {9,20}<={x['pdf_page']for x in response['source_section_evidence']}and len(connection['tools'])==18
 except BaseException:
  config.write_bytes((out/'previous-mcp.json').read_bytes());raise
 save(out/'installed-mcp.json',new);save(out/'actual-configured-response.json',response)
 state=dict(status='terminal_reference_section_frontend_installed_actual_MCP_verified',directory=str(out),entrypoint=str(runtime/'chat_tools_current_v10.py'),tool_count=18,connection=connection,native_Chat_display_verified=False,new_predictions=0,new_training=False,configuration_backup=str(out/'previous-mcp.json'),source_sha256={str(p):sha(p)for p in [Path(__file__),out/'installed-mcp.json',out/'actual-configured-response.json',runtime/'chat_tools_current_v10.py',runtime/'reference_sections_v2.py']},scope=__doc__);save(out/'protocol.json',state);save(v/'reference-section-frontend-installed-current.json',state);print(json.dumps(dict(status=state['status'],tool_count=18,source_pages=[x['pdf_page']for x in response['source_section_evidence']])))
if __name__=='__main__':main()
