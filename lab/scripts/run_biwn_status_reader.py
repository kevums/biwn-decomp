"""Local model reads current test handles through one read-only SDK tool."""
import fcntl
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
import lmstudio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import chat_tools
import lab
from refresh_biwn_operator_status import publish


def main():
    publish()
    out = ROOT/'runs/status-reader'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    system = lab.COMMON+'\nRead the tool evidence. Distinguish running tests from verified comparisons. Never claim that address reachability measures game completion. You explain results; the comparison runners perform validation.'
    user = 'Call read_current_biwn_tests. In under140words report the current tests and completed milestones. Say which verdicts are pending. Do not start or restart tests, give a completion percentage, or claim the full game is decompiled.'
    record = dict(status='running', interface='Local LM Studio Python SDK; not visible native Chat',
                  model=lab.CONFIG['models']['game']['identifier'], system=system, user=user,
                  events=[], tool_calls=[], native_Chat_verified=False, new_training=False)
    def save():
        (out/'protocol.json').write_text(json.dumps(record, indent=2)+'\n')
    def direct_status(status,reason,model_attempted=False):
        evidence=chat_tools.project_evidence('status')
        record.update(status=status,model_inference_invoked=None if model_attempted else False,model_inference_attempted=model_attempted,reason=reason,direct_evidence=evidence)
        save()
        (ROOT/'verification/status-reader-latest.json').write_text(json.dumps(dict(
            directory=str(out),status=status,model_inference_invoked=None if model_attempted else False,model_inference_attempted=model_attempted,
            native_Chat_verified=False),indent=2)+'\n')
        print(reason,flush=True)
        print(evidence['current_verified_route_summary'],flush=True)
        if evidence.get('job_status_scope'):print(evidence['job_status_scope'],flush=True)
        for row in evidence.get('current_running_tests',[]):
            progress=row.get('progress')or{}
            completed=progress.get('completed_frames',progress.get('latest',{}).get('frame'))
            print(row['label']+(': last recorded frame '+str(completed)if completed is not None else'')+'; verdict pending.',flush=True)
        print('Saved status: '+str(out/'protocol.json'),flush=True)
    def read_current_biwn_tests() -> dict:
        """Read live BIWN test handles and saved original/C comparisons; never runs a test."""
        result = chat_tools.current_route_evidence()
        record['tool_calls'].append(dict(tool='read_current_biwn_tests', result=result))
        save()
        return result
    def message(value):
        record['events'].append(value.to_dict())
        save()
    save()
    print('Read-only local status reader. Prompts/results: '+str(out), flush=True)
    # Status remains usable while the shared inference lock is held by
    # training. Do not wait for or attempt to load a competing model.
    training_path=ROOT/'verification/advertising-analysis-v6-running.json'
    if training_path.exists():
        training=json.loads(training_path.read_text())
        phase=training.get('status')
        command=training.get('phase_commands',{}).get(phase,[])
        pid=training.get('pid')
        if pid and len(command)>1:
            observed=subprocess.run(['ps','-p',str(pid),'-o','command='],capture_output=True,text=True,timeout=5).stdout
            if str(command[1]) in observed:
                snapshot=chat_tools.current_route_evidence()
                record.update(status='direct_status_during_active_training',model_inference_invoked=False,
                              training_phase=phase,training_pid=pid,training_handle_verified=True,
                              route_evidence=snapshot)
                save()
                (ROOT/'verification/status-reader-latest.json').write_text(json.dumps(dict(
                    directory=str(out), status=record['status'], model_inference_invoked=False,
                    training_phase=phase, training_handle_verified=True,
                    native_Chat_verified=False), indent=2)+'\n')
                print('Advertising pipeline phase: '+phase+'. Model inference is reserved for training/evaluation; this status comes directly from verified handles.',flush=True)
                for job in snapshot['jobs']:
                    print(job['test']+': '+job['status'],flush=True)
                print('Saved status: '+str(out/'protocol.json'),flush=True)
                return
    config = {'temperature':0.2, 'maxTokens':600}
    chat = lmstudio.Chat(system)
    chat.add_user_message(user)
    try:
        with (ROOT/'runs/.inference.lock').open('w') as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                snapshot=chat_tools.current_route_evidence()
                record.update(status='direct_status_during_busy_inference',model_inference_invoked=False,
                              reason='Another local workflow holds the inference lock.',route_evidence=snapshot)
                save()
                (ROOT/'verification/status-reader-latest.json').write_text(json.dumps(dict(
                    directory=str(out),status=record['status'],model_inference_invoked=False,
                    native_Chat_verified=False),indent=2)+'\n')
                print('Local model busy; current status comes directly from verified process handles.',flush=True)
                for job in snapshot['jobs']:
                    progress=job.get('progress',{})
                    frame=progress.get('completed_frames',progress.get('latest',{}).get('frame'))
                    print(job['test']+': '+job['status']+(('; last frame '+str(frame))if frame is not None else ''),flush=True)
                print('Saved status: '+str(out/'protocol.json'),flush=True)
                return
            catalog=subprocess.run([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],capture_output=True,text=True,timeout=30)
            models=json.loads(catalog.stdout)if catalog.returncode==0 else[]
            expected=lab.CONFIG['models']['game']
            if not any(row['identifier']==expected['identifier']and row['modelKey']==expected['model_key']for row in models):
                direct_status('direct_status_model_unloaded','The everyday model is unloaded; this status comes directly from verified reports and process handles.')
                return
            result = lmstudio.llm(record['model']).act(chat, [read_current_biwn_tests],
                max_prediction_rounds=2, max_parallel_tool_calls=1,
                config=lmstudio.LlmPredictionConfig.from_dict(config), on_message=message)
        finals = [''.join(part.get('text','') for part in event['content'] if part['type']=='text')
                  for event in record['events'] if event['role']=='assistant' and
                  not any(part['type']=='toolCallRequest' for part in event['content'])]
        answer = '\n'.join(finals)
        flags = lab.response_quality_flags(answer)
        if len(answer.split()) > 140: flags.append('word_limit_exceeded')
        if not record['tool_calls']: flags.append('required_status_tool_not_called')
        record.update(status='completed_pending_scope_review', answer=answer, quality_flags=flags,
                      rounds=result.rounds, seconds=result.total_time_seconds, config=config)
        save()
        (out/'prompts-and-responses.txt').write_text('LOCAL SDK STATUS READER; NOT NATIVE CHAT\nSYSTEM\n'+system+
            '\nUSER\n'+user+'\nMESSAGES\n'+json.dumps(record['events'], indent=2)+'\n')
        (ROOT/'verification/status-reader-latest.json').write_text(json.dumps(dict(directory=str(out),
            status=record['status'], seconds=record['seconds'], native_Chat_verified=False), indent=2)+'\n')
        print(answer, flush=True)
        print('Seconds:'+str(round(record['seconds'],2))+'; tool calls:'+str(len(record['tool_calls'])), flush=True)
    except Exception as error:
        record.update(status='model_explanation_failed', error=repr(error))
        save()
        direct_status('direct_status_after_model_error','Local explanation unavailable; verified status follows. The model error is retained in the saved protocol.',model_attempted=True)


if __name__ == '__main__':
    main()
