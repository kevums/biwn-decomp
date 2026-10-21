"""Compare the installed coder model on the same complete-function task."""
import fcntl
import json
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import lab
LMS=Path.home()/'.lmstudio/bin/lms'
def main():
    previous=json.loads((ROOT/'verification/local-scene-actor-author-current.json').read_text())
    evidence=json.loads((Path(previous['directory'])/'evidence.json').read_text())
    out=ROOT/'runs'/(lab.stamp()+'-coder-scene-actor-loader');out.mkdir();print(out,flush=True)
    protocol=dict(status='running',directory=str(out),model_key='qwen3-coder-30b-a3b-instruct-mlx',roles=['local Coder Author'],daily_default_changed=False,prior_failed_drafts=previous['directory'],new_training=False,native_Chat_verified=False)
    (out/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    actions=[]
    def cli(*args):
        run=subprocess.run([str(LMS),*args],capture_output=True,text=True,timeout=300)
        actions.append(dict(arguments=args,exit_code=run.returncode,stdout=run.stdout,stderr=run.stderr))
        assert run.returncode==0,run.stderr
    with (ROOT/'runs/.inference.lock').open('w')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        try:
            cli('unload','--all')
            cli('load',protocol['model_key'],'--identifier','game-coder-eval','--context-length','16384','--parallel','1','--ttl','3600','--yes')
            prompt=dict(evidence=evidence,additional_instructions='''Start from disassembly rather than an old draft.
MOVEM protects callee-saved regs, excluded from host ABI. First outer compare
reads count once; bottom compare rereads it, jumps20ABA directly if signed less.
D0 becomes signed-extended D5word shifted2; READ32 pointer from15ECE2+D0.
Each positive signed16 inner iteration reads mode1 and, if unequal, rereads
mode for mode2. MOVEA.W sign extends X/Z offsets. D0 lowword replaced by
extra field before helper; pass full currentD0 in callback output storage.
Do not ignore assembly lines or assume MOVE.W zeroes upper16. Return JSON
source and limitations only. Code must preserve all host ABI clauses.''')
            result=lab.generate('game','You are a C porting engineer. Recover the complete supplied function from original 68000 disassembly, using the exact host ABI. Return only JSON source and limitations.',json.dumps(prompt),2400,model='game-coder-eval')
            (out/'author.json').write_text(json.dumps(result,indent=2)+'\n')
            (out/'prompts-and-responses.txt').write_text('LOCAL CODER AUTHOR\nREQUEST\n'+json.dumps(result['request'],indent=2)+'\nRESPONSE\n'+result['text']+'\n')
            parsed=lab.parse_object(result['text']);(out/'biwn_local_scene_actor_loader.c').write_text(parsed['source']+'\n')
            protocol.update(status='proposed_coder_source_pending_checks',drafts=[dict(role='coder_author',text=result['text'],seconds=result['seconds'],quality_flags=result['quality_flags'])])
        finally:
            cli('unload','--all');lab.load('game','mac64-chat')
            protocol.update(model_actions=actions,daily_model_restored=True)
            (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    (ROOT/'verification/local-scene-actor-author-current.json').write_text(json.dumps(protocol,indent=2)+'\n')
    print(protocol['status'],result['seconds'],flush=True)
if __name__=='__main__':main()
