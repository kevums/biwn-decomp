"""Confirm installed reference lookup supplies unchanged original method pages."""
import asyncio,json,hashlib
from datetime import datetime,timezone
from pathlib import Path
from pypdf import PdfReader
from check_audio_native_mcp import ROOT,RUNTIME,unpack
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
async def main():
    results=[]
    async with stdio_client(StdioServerParameters(command=str(RUNTIME/'.venv/bin/python'),args=[str(RUNTIME/'chat_tools.py')],cwd=str(RUNTIME)))as(r,w):
        async with ClientSession(r,w)as client:
            await client.initialize()
            for query in ['Lee Koo measured product involvement experiment','Olsen household survey measured involvement']:
                results.append(unpack(await client.call_tool('search_references',{'domain':'advertising','query':query})))
    observed=set()
    for result in results:
        for item in result['source_method_evidence']:
            source=Path(item['source']);original=ROOT/'corpus/advertising/papers'/source.name
            assert hashlib.sha256(source.read_bytes()).hexdigest()==hashlib.sha256(original.read_bytes()).hexdigest()==item['sha256']
            page=PdfReader(original).pages[item['pdf_page']-1].extract_text()
            assert item['excerpt'] in page and len(item['excerpt'])>500
            observed.add((source.name,item['pdf_page']))
    assert {('Lee & Koo (2016).pdf',6),('Lee & Koo (2016).pdf',7),('Lee & Koo (2016).pdf',8),('Lee & Koo (2016).pdf',9),('Olsen (2001).pdf',4)}<=observed
    lee=[e for r in results for e in r['source_method_evidence']if Path(e['source']).name=='Lee & Koo (2016).pdf']
    assert any('variable measuring congruence was computed' in e['excerpt'] for e in lee if e['pdf_page']==7)
    assert any('endorser credibility' in e['excerpt']for e in lee if e['pdf_page']==8)
    assert any('Congruence × Involvement' in e['excerpt']for e in lee if e['pdf_page']==9)
    report=dict(status='fresh_MCP_pinned_method_pages_match_original_PDFs',recorded_at=datetime.now(timezone.utc).isoformat(),method_pages=sorted(observed),tool_evidence=results,native_Chat_verified=False,new_training=False,model_defaults_changed=False)
    (ROOT/'verification/reference-methods-MCP-check.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n');print(json.dumps(dict(status=report['status'],method_pages=report['method_pages'])))
if __name__=='__main__':asyncio.run(main())
