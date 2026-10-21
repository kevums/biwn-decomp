"""Native LM Studio REST + registered local MCP, explicit reasoning off."""
import fcntl,json,subprocess,time,urllib.error,urllib.request
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
save=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
    out=ROOT/'verification/native-MCP-scene-question'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    preset=ROOT/'presets/Game Assistant.preset.json';system=next(f['value']for f in json.loads(preset.read_text())['operation']['fields']if f['key']=='llm.prediction.systemPrompt')
    request=dict(model='advertising-scholar',input='Can I play the rebuilt BIWN game now? What runs as C in the latest street test, and what still uses original code or remains untested? Keep it under110words.',system_prompt=system,integrations=[dict(type='plugin',id='mcp/local-ai-lab',allowed_tools=['project_evidence'])],reasoning='off',max_output_tokens=384,temperature=0.2,context_length=32768,store=False,stream=False)
    r=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='running',interface='Native REST with registered MCP; not visible native Chat',request=request,documentation=['https://lmstudio.ai/docs/developer/rest/chat','https://lmstudio.ai/docs/developer/core/mcp'])
    save(out/'protocol.json',r);print(out,flush=True)
    try:
        with(ROOT/'runs/.inference.lock').open('w')as lock:
            fcntl.flock(lock,fcntl.LOCK_EX);models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True));assert len(models)==1 and models[0]['identifier']=='advertising-scholar'and models[0]['contextLength']==32768 and models[0]['status']=='idle'and models[0]['queued']==0
            started=time.monotonic();http=urllib.request.Request('http://127.0.0.1:1234/api/v1/chat',data=json.dumps(request).encode(),headers={'Content-Type':'application/json'})
            with urllib.request.urlopen(http,timeout=180)as response:raw=json.load(response)
        r.update(status='completed_pending_review',seconds=time.monotonic()-started,raw_response=raw,answer='\n'.join(x['content']for x in raw['output']if x['type']=='message'),tool_calls=[x for x in raw['output']if x['type']=='tool_call'])
        save(out/'protocol.json',r);(out/'prompts-and-responses.txt').write_text('NATIVE LOCAL REST + REGISTERED READONLY MCP; NOT VISIBLE CHAT\nSYSTEM\n'+system+'\nUSER\n'+request['input']+'\nRAW RESPONSE\n'+json.dumps(raw,ensure_ascii=False,indent=2)+'\n')
        save(ROOT/'verification/native-MCP-scene-question-current.json',dict(directory=str(out),status=r['status']));print(json.dumps(dict(seconds=r['seconds'],words=len(r['answer'].split()),tool_calls=len(r['tool_calls']),stray_tag='</think>'in r['answer'],stats=raw['stats'])))
    except Exception as e:
        r.update(status='terminal_failed',error=repr(e))
        if isinstance(e,urllib.error.HTTPError):r['HTTP_error_body']=e.read().decode(errors='replace')
        save(out/'protocol.json',r);save(ROOT/'verification/native-MCP-scene-question-current.json',dict(directory=str(out),status=r['status']));raise
if __name__=='__main__':main()
