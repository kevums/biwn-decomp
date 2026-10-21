"""Exercise the moved package's actual launchers, preserving every request/result.
The LM Studio host service remains external; both clients/dependencies and model
weight files come from the moved package. Restore the ordinary daily model.
"""
import fcntl, hashlib, json, os, subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
V = ROOT / 'verification'
LMS = Path('/Users/kevin/.lmstudio/bin/lms')

def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')

def ps():
    return json.loads(subprocess.check_output([str(LMS), 'ps', '--json'], text=True))

def main():
    package = Path(json.loads((V / 'portable-sdk-workbench-current.json').read_text())['package'])
    out = V / 'portable-assistant-launchers' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    state = dict(status='prepared', pid=os.getpid(), directory=str(out), package=str(package), jobs=[], new_training=False, native_Chat_verified=False)
    def mark():
        save(out / 'protocol.json', state)
        save(V / 'portable-assistant-launchers-current.json', state)
    def run(command, name, timeout):
        save(out / (name + '-command.json'), command)
        with (out / (name + '.log')).open('w') as stream:
            child = subprocess.Popen(command, stdout=stream, stderr=subprocess.STDOUT, env={k:v for k,v in os.environ.items() if k not in ['PYTHONPATH','PYTHONHOME','VIRTUAL_ENV']})
            state.update(status='running_' + name, child_pid=child.pid)
            mark()
            code = child.wait(timeout=timeout)
        state['jobs'].append(dict(name=name, exit_code=code))
        mark()
        assert code == 0, str(out / (name + '.log'))
    mark()
    with (ROOT / 'runs/.inference.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        before = ps()
        save(out / 'before-models.json', before)
        assert len(before)==1 and before[0]['modelKey']=='local/advertising-qwen38' and before[0]['status']=='idle' and before[0].get('queued',0)==0
        try:
            run([str(package / 'Run Game Assistant.command'), 'In exactly two sentences and at most 90 words, explain what can currently be rebuilt for Black Ice White Noise and whether the evidence establishes a complete same-console game-source rebuild or physical-console readiness.'], 'game', 600)
            save(out / 'game-models.json', ps())
            save(out / 'game-result.json', json.loads((package / 'portable-game-latest.json').read_text()))
            run([str(package / 'Load Advertising Reviewer.command'), 'Review this draft about Schreiner2026 Study2A in exactly two sentences and at most 100 words: "AI aversion was randomly assigned before the ads, so the study proves aversion causes ad attitudes." Identify design and measurement-timing errors using the supplied source sections.'], 'advertising-reviewer', 600)
            save(out / 'reviewer-models.json', ps())
            save(out / 'advertising-result.json', json.loads((package / 'portable-advertising-latest.json').read_text()))
            state['both_actual_launcher_predictions_returned'] = True
        except BaseException as error:
            state.update(status='terminal_launcher_test_failed', error=repr(error))
            mark()
            raise
        finally:
            loaded = ps()
            save(out / 'before-restore-models.json', loaded)
            assert all(x['status']=='idle' and x.get('queued',0)==0 for x in loaded), 'Preserve any active prediction'
            bindings = json.loads((package / 'portable-model-bindings.json').read_text()) if (package / 'portable-model-bindings.json').exists() else {'models':{}}
            allowed = {'local/advertising-qwen38', *[x['model_key'] for x in bindings['models'].values()]}
            assert all(x['modelKey'] in allowed for x in loaded), 'Preserve unrelated model'
            if not (len(loaded)==1 and loaded[0]['modelKey']=='local/advertising-qwen38' and loaded[0]['identifier']=='advertising-scholar' and loaded[0]['contextLength']==32768):
                run([str(LMS),'unload','--all'], 'restore-unload', 120)
                run([str(LMS),'load','local/advertising-qwen38','--identifier','advertising-scholar','--context-length','32768','--parallel','1','--ttl','3600','--yes'], 'restore-load', 300)
            after = ps()
            save(out / 'after-models.json', after)
            assert len(after)==1 and after[0]['identifier']=='advertising-scholar' and after[0]['contextLength']==32768 and after[0]['parallel']==1
            state['daily_default_restored'] = True
            mark()
    state.update(status='terminal_two_moved_package_launcher_predictions_returned_pending_quality_review', new_predictions=2, host_LM_Studio_service_required=True)
    mark()
    print(json.dumps(state))

if __name__ == '__main__':
    main()
