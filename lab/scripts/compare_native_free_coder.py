"""One existing coder-model development task; restore daily model in finally."""
from pathlib import Path
from datetime import datetime,timezone
import fcntl,json,re,subprocess,sys,os,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import lab,assistant_chat
LMS=Path.home()/'.lmstudio/bin/lms';KEY='qwen3-coder-30b-a3b-instruct-mlx';ID='biwn-code-author-eval'
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def main():
    out=ROOT/'runs'/('native-free-coder-comparison-'+lab.stamp());out.mkdir();print(out,flush=True)
    prior=ROOT/'runs/local-native-free-20261018T074723.402359Z/prepared-author.json';prompt=json.loads(prior.read_text())
    state=dict(status='prepared',directory=str(out),pid=os.getpid(),model_key=KEY,identifier=ID,context_length=16384,workers=1,reasoning='off',new_training=False,native_UI=False,coordinator_supplied_full_algorithm=False,prior_prompt=str(prior),prior_prompt_sha256=hashlib.sha256(prior.read_bytes()).hexdigest(),comparison_scope='Same assembly/ABI/flag input as reasoning-medium failed attempt; different model and reasoning policy, development not controlled speed/generalization benchmark.',source_accepted=False)
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-free-coder-active.json',state)
    def command(args,name):
        p=subprocess.run([str(LMS),*args],capture_output=True,text=True,timeout=180);(out/(name+'.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr;return p
    mark()
    with(ROOT/'runs/.inference.lock').open('a')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        catalog=json.loads(subprocess.check_output([str(LMS),'ps','--json'],text=True));assert len(catalog)==1 and catalog[0]['identifier']=='advertising-scholar'and catalog[0]['status']=='idle',catalog
        state['daily_before']=catalog;mark()
        try:
            state['status']='unloading_daily_for_single_model_coder_check';mark();command(['unload','advertising-scholar'],'unload-daily')
            command(['load',KEY,'--identifier',ID,'--context-length','16384','--parallel','1','--ttl','3600','--yes'],'load-coder')
            state['coder_loaded']=json.loads(subprocess.check_output([str(LMS),'ps','--json'],text=True));assert len(state['coder_loaded'])==1 and state['coder_loaded'][0]['identifier']==ID
            state['status']='coder_author_running';mark();lab.CONFIG['models']['game']['reasoning']='off'
            result=lab.generate('game',prompt['system'],prompt['user'],4500,model=ID);save(out/'response.json',result)
            (out/'prompts-and-responses.txt').write_text('SYSTEM\n'+prompt['system']+'\nUSER\n'+prompt['user']+'\nRESPONSE\n'+result['text'])
            blocks=re.findall(r'```c\s*\n(.*?)```',result['text'],re.S);assert len(blocks)==1
            p=out/'free-native.c';p.write_text(blocks[0].strip()+'\n')
            state.update(status='terminal_coder_draft_pending_gates',source=str(p),source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),reported_seconds=result['seconds'],usage=result['usage'],quality_flags=result['quality_flags'],raw_model_C_unchanged=True)
        except BaseException as exc:state.update(status='terminal_coder_attempt_failed',error=repr(exc));raise
        finally:
            loaded=json.loads(subprocess.check_output([str(LMS),'ps','--json'],text=True))
            if any(x['identifier']==ID for x in loaded):command(['unload',ID],'unload-coder')
            assistant_chat.ensure_model('advertising')
            state['daily_after']=json.loads(subprocess.check_output([str(LMS),'ps','--json'],text=True));assert len(state['daily_after'])==1 and state['daily_after'][0]['identifier']=='advertising-scholar'
            state['daily_restored']=True;state['finished_at']=datetime.now(timezone.utc).isoformat();mark();save(ROOT/'verification/native-free-coder-current.json',state)
    print(state['status'],state.get('reported_seconds'),flush=True)
if __name__=='__main__':main()
