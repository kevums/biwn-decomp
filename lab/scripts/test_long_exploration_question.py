"""One ordinary progress question with saved preset and automatic local tools."""
from datetime import datetime,timezone
import fcntl
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import chat_tools,lab,lmstudio


def main():
    preset=json.loads((ROOT/'presets/Game Assistant.preset.json').read_text())
    system=next(f['value']for f in preset['operation']['fields']if f['key']=='llm.prediction.systemPrompt')
    prompt='What did the longer Black Ice White Noise test add, and did it produce game audio? In under90words, distinguish the approximate decompiler export from checked C components and a complete reconstructed game.'
    out=ROOT/'verification/easy-long-exploration'/lab.stamp();out.mkdir(parents=True)
    protocol={'recorded_at':datetime.now(timezone.utc).isoformat(),'status':'running','model':'advertising-scholar',
              'interface':'Local LM Studio SDK act API; not a native Chat message','system':system,'user':prompt,
              'preset_sha256':lab.sha(ROOT/'presets/Game Assistant.preset.json'),
              'config':{'temperature':0.2,'maxTokens':512},'max_prediction_rounds':2,'events':[]}
    def save():(out/'protocol.json').write_text(json.dumps(protocol,ensure_ascii=False,indent=2)+'\n')
    save();print(out,flush=True)
    with (ROOT/'runs/.inference.lock').open('w')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True))
        assert len(models)==1 and models[0]['identifier']=='advertising-scholar' and models[0]['contextLength']==32768
        chat=lmstudio.Chat(system);chat.add_user_message(prompt)
        def message(value):protocol['events'].append(value.to_dict());save()
        result=lmstudio.llm('advertising-scholar').act(chat,[chat_tools.project_evidence,chat_tools.inspect_boot,chat_tools.search_references,chat_tools.verify_68000_fixture],
                 max_prediction_rounds=2,max_parallel_tool_calls=1,config=lmstudio.LlmPredictionConfig.from_dict(protocol['config']),on_message=message)
        protocol.update(status='completed_pending_coordinator_review',completed_at=datetime.now(timezone.utc).isoformat(),rounds=result.rounds,seconds=result.total_time_seconds);save()
    (out/'prompts-and-responses.txt').write_text(json.dumps(protocol,ensure_ascii=False,indent=2)+'\n')
    (ROOT/'verification/easy-long-exploration-current.json').write_text(json.dumps({'directory':str(out),'status':protocol['status']},indent=2)+'\n')
    print(json.dumps({'rounds':result.rounds,'seconds':result.total_time_seconds,'status':protocol['status']}),flush=True)


if __name__=='__main__':main()
