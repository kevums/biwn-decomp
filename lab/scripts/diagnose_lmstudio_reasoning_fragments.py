"""Observe typed SDK fragments without hiding or rewriting any model output."""
import collections,fcntl,hashlib,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];RUNTIME=Path.home()/'.lmstudio/local-ai-lab';sys.path.insert(0,str(RUNTIME));import chat_tools,lab,lmstudio
save=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
    out=ROOT/'verification/reasoning-fragment-diagnostic'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    preset=ROOT/'presets/Game Assistant.preset.json';system=next(f['value']for f in json.loads(preset.read_text())['operation']['fields']if f['key']=='llm.prediction.systemPrompt')
    question='Can I play the rebuilt BIWN game now? What runs as C in the latest street test, and what still uses original code or remains untested? Keep it under110words.'
    tools=[chat_tools.verify_68000_fixture,chat_tools.render_inventory_preview,chat_tools.render_animation_preview,chat_tools.project_evidence,chat_tools.inspect_boot,chat_tools.search_references]
    r=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='running',interface='local SDK, not native Chat',model='advertising-scholar',system=system,user=question,config={'temperature':0.2,'maxTokens':384,'reasoningParsing':{'enabled':True,'startString':'<think>','endString':'</think>'}},messages=[],fragments=[])
    save(out/'protocol.json',r);print(out,flush=True)
    try:
        with(ROOT/'runs/.inference.lock').open('w')as lock:
            fcntl.flock(lock,fcntl.LOCK_EX);models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True));assert len(models)==1 and models[0]['status']=='idle'and models[0]['identifier']=='advertising-scholar'and models[0]['contextLength']==32768 and models[0]['queued']==0
            chat=lmstudio.Chat(system);chat.add_user_message(question)
            def message(v):r['messages'].append(v.to_dict());save(out/'protocol.json',r)
            def fragment(v,index):r['fragments'].append(dict(round=index,**v.to_dict()))
            result=lmstudio.llm('advertising-scholar').act(chat,tools,max_prediction_rounds=2,max_parallel_tool_calls=1,config=lmstudio.LlmPredictionConfig.from_dict(r['config']),on_message=message,on_prediction_fragment=fragment)
        types=collections.Counter((x['round'],x['reasoningType'])for x in r['fragments']);rounds=sorted({x['round']for x in r['fragments']})
        r.update(status='completed_pending_review',seconds=result.total_time_seconds,rounds=result.rounds,fragment_type_counts={str(k):v for k,v in types.items()},typed_visible_by_round={str(i):''.join(x['content']for x in r['fragments']if x['round']==i and x['reasoningType']=='none')for i in rounds},sdk_raw_text_by_message=[''.join(c.get('text','')for c in e['content']if c['type']=='text')for e in r['messages']if e['role']=='assistant'])
        save(out/'protocol.json',r);(out/'prompts-and-responses.txt').write_text('LOCAL SDK DIAGNOSTIC; NOT NATIVE CHAT\nSYSTEM\n'+system+'\nUSER\n'+question+'\nRAW MESSAGES\n'+json.dumps(r['messages'],ensure_ascii=False,indent=2)+'\nFRAGMENT TYPES\n'+json.dumps(r['fragment_type_counts'],indent=2)+'\nTYPED VISIBLE CONTENT (DERIVED FROM SERVER METADATA, RAW OUTPUT RETAINED)\n'+json.dumps(r['typed_visible_by_round'],ensure_ascii=False,indent=2)+'\n')
        save(ROOT/'verification/reasoning-fragment-diagnostic-current.json',dict(directory=str(out),status=r['status']));print(json.dumps(dict(seconds=r['seconds'],fragment_type_counts=r['fragment_type_counts'])))
    except Exception as e:r.update(status='terminal_failed',error=repr(e));save(out/'protocol.json',r);raise
if __name__=='__main__':main()
