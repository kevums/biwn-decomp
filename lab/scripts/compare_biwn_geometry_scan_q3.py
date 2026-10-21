"""One fresh installed-coder output on the original frozen scan task, no repair."""
import fcntl,json,os,re,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import lab
from benchmark_coder_function_workflow import inventory,require_idle
def read(p):return json.loads(Path(p).read_text())
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
    prior=read(ROOT/'verification/local-native-geometry-scan-author-current.json');request=read(Path(prior['directory'])/'frozen-request.json')
    for p,h in request['source_sha256'].items():assert lab.sha(Path(p))==h
    out=ROOT/'runs'/('local-native-geometry-scan-q3-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir(parents=True);print(out,flush=True)
    key='qwen3-coder-next';identifier='game-scan-q3-comparison';lms=str(Path.home()/'.lmstudio/bin/lms');daily=None;unloaded=False;attempted=False
    state=dict(status='waiting_for_inference_lock',pid=os.getpid(),directory=str(out),model_key=key,identifier=identifier,context_length=32768,parallel=1,new_training=False,default_promoted=False,native_Chat_verified=False,resource_guard_bypassed=False,scope='One fresh different-model response to the original exact system/user/2200token task, without repair feedback or coordinator search source. Typed header/bounds helper/ABI are coordinator-provided. Different architecture/quantization; one development task is not a model ranking or training-gain comparison.')
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/local-native-geometry-scan-q3-current.json',state)
    save(out/'frozen-request.json',dict(system=request['system'],user=request['user'],max_output_tokens=2200,temperature=0,model_key=key,identifier=identifier,source_request=str(Path(prior['directory'])/'frozen-request.json'),source_request_sha256=lab.sha(Path(prior['directory'])/'frozen-request.json'),source_sha256={str(p):lab.sha(p)for p in [Path(__file__),ROOT/'scripts/check_biwn_native_geometry_scan.py']},no_repair_feedback=True))
    transcript=out/'prompts-and-responses.txt';transcript.write_text('FRESH CODER AUTHOR COMPARISON\nSYSTEM:\n'+request['system']+'\nUSER:\n'+request['user']+'\nRESPONSE: awaiting generation\n');(out/'runner-as-run.py').write_bytes(Path(__file__).read_bytes());mark()
    with(ROOT/'runs/.inference.lock').open('a')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        try:
            before=inventory(lms);require_idle(before);state['initial_inventory']=before
            daily_id=lab.CONFIG['models']['game']['identifier'];assert all(row['identifier']==daily_id for row in before),'Unrelated models preserved'
            daily=next((row for row in before if row['identifier']==daily_id),None)
            if daily:
                assert not daily.get('engineConfigFileEnabled');subprocess.run([lms,'unload',daily_id],check=True,capture_output=True,text=True,timeout=120,stdin=subprocess.DEVNULL);unloaded=True;state['daily_temporarily_unloaded']=True
            state['status']='estimating_normal_guarded_coder_load';mark()
            estimate=subprocess.run([lms,'load',key,'--context-length','32768','--parallel','1','--estimate-only','--yes'],capture_output=True,text=True,timeout=120,stdin=subprocess.DEVNULL);message=estimate.stdout+estimate.stderr;(out/'estimate.log').write_text(message)
            assert estimate.returncode==0 and not re.search(r'will fail|insufficient|out of memory|exceed.*guard',message,re.I),'Normal resource estimate refused; no bypass'
            attempted=True;state['status']='loading_coder_normal_guard';mark();print('CODER LOAD: installed GGUF Q3,32K,one worker, normal guard',flush=True)
            load=subprocess.run([lms,'load',key,'--identifier',identifier,'--context-length','32768','--parallel','1','--ttl','3600','--yes'],capture_output=True,text=True,timeout=300,stdin=subprocess.DEVNULL);(out/'load.log').write_text(load.stdout+load.stderr)
            actual=next((row for row in inventory(lms)if row['identifier']==identifier),None)
            assert load.returncode==0 and actual and actual['modelKey']==key and actual['format']=='gguf' and actual['contextLength']==32768 and actual['parallel']==1
            state.update(status='generating_fresh_coder_kernel',loaded_model=actual);mark();print('AUTHOR: fresh coder response, original exact task, no failed drafts or feedback',flush=True)
            cfg=lab.CONFIG['models']['game'];cfg['reasoning']='off';cfg['sampling']={**cfg.get('sampling',{}),'temperature':0}
            a=lab.generate('game',request['system'],request['user'],2200,model=identifier);save(out/'author.json',a);(out/'response.txt').write_text(a['text']);text=a['text'].strip();m=re.fullmatch(r'```(?:c|c99)?\s*\n([\s\S]*?)\n```\s*',text)
            if m:text=m.group(1)
            source=out/'geometry-scan-candidate.c';source.write_text(text+'\n');state.update(status='checking_fresh_coder_kernel',candidate=str(source),candidate_sha256=lab.sha(source),author_seconds=a['seconds'],format_normalization='single outer fence removed'if m else'none');mark();transcript.write_text('FRESH CODER AUTHOR COMPARISON\nSYSTEM:\n'+request['system']+'\nUSER:\n'+request['user']+'\nRESPONSE:\n'+a['text']+'\n')
            with(out/'gate.log').open('w')as log:gate=subprocess.run([sys.executable,str(ROOT/'scripts/check_biwn_native_geometry_scan.py'),'--source',str(source),'--no-publish'],stdout=log,stderr=subprocess.STDOUT,timeout=480)
            proof=read(ROOT/'verification/native-geometry-scan-active.json');assert proof['source']==str(source)
            state.update(status='terminal_fresh_coder_geometry_scan_pending_coordinator_review',gate_exit_code=gate.returncode,raw_kernel_gate_pass=gate.returncode==0,gate_status=proof['status'],gate_proof=str(Path(proof['directory'])/'protocol.json'),native_cases=proof.get('native_cases',0),changing_cases=proof.get('changing_coordinate_cases',0));mark();print(state['status'],state['raw_kernel_gate_pass'],flush=True)
        except BaseException as e:state.update(status='terminal_fresh_coder_scan_failed',error=repr(e));mark();raise
        finally:
            rows=inventory(lms)
            if any(row.get('status')!='idle'or row.get('queued',0)for row in rows):state['daily_restoration_pending_busy_model']=True;mark()
            else:
                owned=next((row for row in rows if row['identifier']==identifier and row['modelKey']==key),None)
                if attempted and owned:subprocess.run([lms,'unload',identifier],check=True,capture_output=True,text=True,timeout=120,stdin=subprocess.DEVNULL)
                if unloaded:
                    restore=subprocess.run([lms,'load',daily['modelKey'],'--identifier',daily['identifier'],'--context-length',str(daily['contextLength']),'--parallel',str(daily['parallel']),'--ttl','3600','--yes'],capture_output=True,text=True,timeout=300,stdin=subprocess.DEVNULL);(out/'daily-restore.log').write_text(restore.stdout+restore.stderr);state['daily_model_restored']=restore.returncode==0;assert state['daily_model_restored'],'Daily restore failed'
                mark()
if __name__=='__main__':main()
