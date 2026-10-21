"""Read-only view of exact local Author/Repair prompts and streamed responses."""
import argparse,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--watch',action='store_true');args=ap.parse_args()
    seen=set();offsets={};last=None
    print('BIWN LOCAL CODER — SAVED LIVE STREAM\nAuthor and Repair use the same installed local weights. The compiler and original CPU check the result.\nThis viewer starts no inference and does not create LM Studio Chat tabs.\n',flush=True)
    try:
        while True:
            available=[ROOT/'verification'/name for name in ['game-decomposed-clear-v3-current.json','game-decomposed-clear-v2-current.json','game-decomposed-clear-v1-current.json','game-compiler-feedback-v2-current.json','game-compiler-feedback-v1-current.json']]
            available=[p for p in available if p.exists()]
            if not available:print('No coder run has been started.');return
            pointer=max(available,key=lambda p:p.stat().st_mtime_ns)
            state=json.loads(pointer.read_text());folder=Path(state['directory'])
            if last!=state['status']:
                print('\nWorkflow: '+state['status']+' | '+state.get('model_key',state.get('model','local model')),flush=True);last=state['status']
            for prompt in sorted(folder.glob('*/prompt.json')):
                if prompt not in seen:
                    seen.add(prompt);print('\n'+str(prompt.parent.name)+' — EXACT PROMPT',flush=True)
                    for message in json.loads(prompt.read_text()):print('['+message['role']+']\n'+message['content']+'\n',flush=True)
                    print('RAW LOCAL RESPONSE — LIVE',flush=True)
                response=prompt.with_name('response.partial.txt')
                if response.exists():
                    text=response.read_text();at=offsets.get(response,0)
                    if len(text)>at:print(text[at:],end='',flush=True);offsets[response]=len(text)
            done=state['status'].startswith('terminal_')and (state.get('daily_model_restored',False)or pointer.name.startswith('game-decomposed-clear-v'))
            if not args.watch or done:
                print('\n\nSaved run: '+str(folder),flush=True)
                for row in state.get('rounds',[]):
                    inference=Path(row['candidate']).parent/'inference.json';info=json.loads(inference.read_text())if inference.exists()else{}
                    outcome='full gate passed;unpromoted'if row['verified']else'no final C generated'if info and not info.get('text','').strip()else row.get('checker_status','rejected')
                    print(row['role']+': '+outcome,flush=True)
                    if info:
                        usage=info.get('usage',{});print('  Output tokens: '+str(usage.get('completion_tokens'))+'; reasoning tokens: '+str(usage.get('completion_tokens_details',{}).get('reasoning_tokens'))+'; seconds: '+str(info.get('seconds')),flush=True)
                return
            time.sleep(1)
    except KeyboardInterrupt:pass
if __name__=='__main__':main()
