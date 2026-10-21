"""Dedicated installed coder compatibility test using the fixed Chat task/check tools."""
import argparse,fcntl,json,os,re,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import lab,function_workbench


def inventory(lms):
    return json.loads(subprocess.check_output([lms,'ps','--json'],text=True,timeout=30))


def require_idle(rows):
    busy=[row['identifier']for row in rows if row.get('status')!='idle'or row.get('queued',0)]
    if busy:raise RuntimeError('Models busy or state unknown: '+', '.join(busy))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model-key',default='qwen3-coder-30b-a3b-instruct-mlx')
    parser.add_argument('--identifier',default='game-coder-benchmark')
    parser.add_argument('--context-length',type=int,default=16384)
    parser.add_argument('--max-tokens',type=int,default=6000)
    parser.add_argument('--receipt',default='coder-function-workflow-current.json')
    parser.add_argument('--repair-from',type=Path,help='One diagnostic-guided repair of drafts from a prior benchmark directory')
    args=parser.parse_args()
    assert 8192<=args.context_length<=32768 and 2048<=args.max_tokens<=12000
    assert re.fullmatch(r'[a-z0-9-]+\.json',args.receipt)
    if args.repair_from:assert args.repair_from.resolve().is_relative_to(ROOT/'runs')
    load_target=args.model_key
    daily_identifier=lab.CONFIG['models']['game']['identifier']
    assert args.identifier!=daily_identifier
    out=ROOT/'runs'/('coder-function-workflow-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir()
    pointer=ROOT/'verification'/args.receipt
    report=dict(status='loading',pid=os.getpid(),directory=str(out),
        model_key=args.model_key,model_identifier=args.identifier,context_length=args.context_length,results=[],
        default_promoted=False,new_training=False,native_Chat_verified=False,
        scope='Installed dedicated coder tested via LMStudio API with current task-fetch/rawC format and original/native gates. '
              'Prior27B benchmark used older contracts; this is a workflow compatibility test,not a controlled model ranking. '
              'No source promotion or whole-game claim.')
    if args.repair_from:
        report.update(repair_parent_run=str(args.repair_from.resolve()),mode='one_diagnostic_guided_repair_per_function',
                      coordinator_C_body_edits=False,reference_C_supplied=False)
    def save():
        (out/'protocol.json').write_text(json.dumps(report,indent=2)+'\n');pointer.write_text(json.dumps(report,indent=2)+'\n')
    save();print(out,flush=True);lms=str(Path.home()/'.lmstudio/bin/lms')
    daily=None;daily_unloaded=False;candidate_owned=False;load_attempted=False
    with (ROOT/'runs/.inference.lock').open('a')as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        try:
            lab.ensure_server()
            before=inventory(lms);require_idle(before);report['initial_inventory']=before;save()
            assert not any(row['identifier']==args.identifier for row in before),'Benchmark identifier in use'
            assert all(row['identifier']==daily_identifier for row in before),'Unrelated loaded models preserved'
            daily=next((row for row in before if row['identifier']==daily_identifier),None)
            if daily:
                assert not daily.get('engineConfigFileEnabled'),'Custom engine profile cannot be reproduced from inventory'
                require_idle(inventory(lms))
                subprocess.run([lms,'unload',daily_identifier],check=True,capture_output=True,text=True,timeout=120,stdin=subprocess.DEVNULL)
                daily_unloaded=True;report['daily_temporarily_unloaded']=True;save()
            estimate=subprocess.run([lms,'load',load_target,'--context-length',str(args.context_length),
                '--parallel','1','--estimate-only','--yes'],capture_output=True,text=True,timeout=120,stdin=subprocess.DEVNULL)
            estimate_text=estimate.stdout+estimate.stderr;(out/'estimate.log').write_text(estimate_text)
            if estimate.returncode or re.search(r'will fail|insufficient|out of memory|exceed.*guard',estimate_text,re.I):
                report['resource_guard_refused']=True
                raise RuntimeError('Ordinary memory estimate refused; no guarded load attempted')
            require_idle(inventory(lms))
            load_attempted=True;report['candidate_load_attempted']=True;save()
            loaded=subprocess.run([lms,'load',load_target,'--identifier',report['model_identifier'],
                '--context-length',str(args.context_length),'--parallel','1','--ttl','3600','--yes'],
                cwd=Path.home()/'.lmstudio',capture_output=True,text=True,timeout=300,stdin=subprocess.DEVNULL)
            (out/'load.log').write_text(loaded.stdout+loaded.stderr)
            candidate=next((row for row in inventory(lms)if row['identifier']==args.identifier),None)
            candidate_owned=candidate is not None
            assert loaded.returncode==0 and candidate,'Normal guarded load failed'
            assert candidate['modelKey']==args.model_key and candidate['contextLength']==args.context_length
            report['loaded_model']=candidate
            report['status']='generating';save()
            for routine in ['frame_release','scene_select','frame_acquire']:
                task=function_workbench.task(ROOT,routine)
                system=lab.COMMON+'\nAuthor the complete portable C99 function. Return compact raw C only,with minimal comments. Do not claim verification.'
                prompt='\n\n'.join(message['content']for message in task['messages'])
                if args.repair_from:
                    previous=json.loads((args.repair_from/(routine+'-inference.json')).read_text())
                    feedback=json.loads((args.repair_from/(routine+'-checks.json')).read_text())
                    log=Path(feedback['log']).read_text()if feedback.get('log')else feedback.get('diagnostic','')
                    details={key:feedback[key]for key in['status','exit_code','original_comparison_feedback']if key in feedback}
                    prompt+='\n\nYOUR PREVIOUS DRAFT\n'+previous['text']+'\n\nACTUAL VERIFIER DIAGNOSTICS\n'+json.dumps(details,indent=2)+'\n'+log[-8000:]
                    prompt+='\nReturn one complete corrected C file. Fix the observed compiler/original-code failure using the supplied assembly and ABI. No source solution is provided; do not claim a pass before verification.'
                (out/(routine+'-prompt.json')).write_text(json.dumps(dict(system=system,user=prompt),indent=2)+'\n')
                report['active_routine']=routine;save();print('Author:',routine,'— prompt saved',flush=True)
                result=lab.generate('game',system,prompt,args.max_tokens,model=report['model_identifier'])
                (out/(routine+'-inference.json')).write_text(json.dumps(result,indent=2)+'\n')
                with (out/'prompts-and-responses.txt').open('a')as f:
                    f.write(routine+'\nREQUEST\n'+json.dumps(result['request'],indent=2)+'\nRESPONSE\n'+result['text']+'\n')
                text=result['text'].strip();fence=re.fullmatch(r'```(?:c|c99|json)?\s*\n([\s\S]*?)\n```\s*',text)
                if fence:text=fence.group(1)
                try:structured=json.loads(text)
                except json.JSONDecodeError:structured=None
                if isinstance(structured,dict)and isinstance(structured.get('source'),str):text=structured['source']
                checked=function_workbench.verify(ROOT,routine,text)
                (out/(routine+'-checks.json')).write_text(json.dumps(checked,indent=2)+'\n')
                report['results'].append(dict(routine=routine,seconds=result['seconds'],
                    quality_flags=result['quality_flags'],verified=checked['verified'],check_status=checked['status'],
                    inference=str(out/(routine+'-inference.json')),proof=checked.get('proof_directory')))
                save();print(routine,'verified',checked['verified'],'seconds',result['seconds'],flush=True)
            report.update(status='terminal_workflow_benchmark',passes=sum(x['verified']for x in report['results']));save()
        except Exception as error:
            report.update(status='terminal_resource_guard_refused'if report.get('resource_guard_refused')else'terminal_failed',error=repr(error));save();raise
        finally:
            rows=inventory(lms)
            if any(row.get('status')!='idle'or row.get('queued',0)for row in rows):
                report['restoration_pending_busy_model']=True;save()
            else:
                owned=next((row for row in rows if row['identifier']==args.identifier and (candidate_owned or row['modelKey']==args.model_key)),None)
                if (candidate_owned or load_attempted)and owned:
                    subprocess.run([lms,'unload',args.identifier],capture_output=True,text=True,timeout=120,check=True)
                if daily_unloaded:
                    restored=subprocess.run([lms,'load',daily['modelKey'],'--identifier',daily_identifier,
                        '--context-length',str(daily['contextLength']),'--parallel',str(daily['parallel']),
                        '--ttl','3600','--yes'],capture_output=True,text=True,timeout=300,stdin=subprocess.DEVNULL)
                    report['daily_model_restored']=restored.returncode==0
                    (out/'daily-model-reload.log').write_text(restored.stdout+restored.stderr)
                save()
                if daily_unloaded and not report.get('daily_model_restored'):
                    report['status']='terminal_daily_restore_failed';save()
                    raise RuntimeError('Daily model restore failed; see reload log')


if __name__=='__main__':main()
