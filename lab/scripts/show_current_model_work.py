"""Export exact saved evaluation messages and raw responses for easy inspection."""
import argparse, hashlib, json, subprocess
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]

def read(path):return json.loads(path.read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--no-open',action='store_true');args=parser.parse_args()
    lines=['LOCAL MODEL WORK — SAVED PROMPTS AND RAW RESPONSES',datetime.now(timezone.utc).isoformat(),'','This is a snapshot of saved files. Refresh by running Model Prompts and Responses.command again.','Offline evaluation roles run sequentially on the same local model. These are not agents streaming in LM Studio Chat.','Codex coordinates the experiment and source review; compiler/emulator gates are tools. Training loss is not an answer-quality score.','']
    manifest=[]
    for name,title in [('advertising-v10-base-evaluation-current.json','Advertising: base model'),('advertising-v10-adapter-evaluation-current.json','Advertising: original 64-update adapter trial'),('advertising-v10-resource-capped-adapter-evaluation-current.json','Advertising: separately frozen resource-capped adapter comparison'),('advertising-reviewer-v10cap-configured-native-current.json','Advertising: exported model tested through LM Studio'),('native-build-contract-evaluation-current.json','BIWN: clarified base/adapter code comparison'),('native-resource-feedback-team-current.json','BIWN: local Reviewer then Restorer feedback workflow'),('native-structured-resource-reviewer-current.json','BIWN: structured source-Reviewer probe through LM Studio')]:
        pointer=ROOT/'verification'/name
        if not pointer.exists():continue
        state=read(pointer);folder=Path(state['directory']);lines.extend(['='*72,title,'Phase: '+state['status'],'Saved run: '+str(folder),''])
        prompts=sorted(folder.rglob('prompt.json'))
        # Only model inputs from this run: exclude any archived implementation directories.
        prompts=[p for p in prompts if 'orchestration-as-run'not in p.parts]
        prompts += [p for p in folder.rglob('request.json') if not p.with_name('prompt.json').exists() and any(k in read(p) for k in ['system','system_prompt'])]
        if not prompts:lines.extend(['No model prompt/response files have been saved in this run yet.',''])
        for prompt in prompts:
            response=prompt.with_name('response.txt');messages=read(prompt)
            response_bytes=response.read_bytes()if response.exists()else None
            complete=prompt.with_name('result.json').exists()
            lines.extend(['-'*72,str(prompt.parent.relative_to(folder)),'Exact saved prompt: '+str(prompt),'Prompt SHA-256: '+sha(prompt),''])
            if isinstance(messages,list) and all(isinstance(m,dict)and'role'in m and'content'in m for m in messages):
                for m in messages:lines.extend(['['+m['role']+']',m['content']if isinstance(m['content'],str)else json.dumps(m['content'],ensure_ascii=False,indent=2),''])
            else:lines.extend([json.dumps(messages,ensure_ascii=False,indent=2),''])
            lines.extend(['[RAW MODEL RESPONSE — '+('generation result saved'if complete else'partial or awaiting generation result')+']',response_bytes.decode('utf-8')if response_bytes is not None else'No response has been saved yet.',''])
            manifest.append(dict(prompt=str(prompt),prompt_sha256=sha(prompt),response=str(response)if response_bytes is not None else None,response_sha256=hashlib.sha256(response_bytes).hexdigest()if response_bytes is not None else None,response_bytes=len(response_bytes)if response_bytes is not None else 0,generation_result_saved=complete))
    report=ROOT/'reports/current-model-prompts-and-responses.txt';report.write_text('\n'.join(lines)+'\n')
    metadata=dict(recorded_at=datetime.now(timezone.utc).isoformat(),report=str(report),report_sha256=sha(report),saved_prompts=len(manifest),files=manifest,new_inference=False,native_Chat=False)
    (ROOT/'reports/current-model-prompts-and-responses-manifest.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print('Saved prompts:',len(manifest));print('Open:',report)
    if not args.no_open:subprocess.run(['open','-a','TextEdit',str(report)],check=True)

if __name__=='__main__':main()
