"""Warm CLI launch timing,including setup/evidence; no native-UI click claim."""
import json,os,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha

def main():
    out=V/'copied-Reader41-ordinary-benchmark-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    entry=P/'workbench/portable_biwn_try_v21.py';assert sha(entry)==sha(ROOT/'scripts/portable_biwn_entry_v21.py')
    command=[str(P/'runtime/python/bin/python3.12'),str(entry),'reader'];pointer=P/'workbench/verification/Deck-status-live-v41-current.json'
    catalog=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd='/',text=True,timeout=30));save(out/'loaded-models-before-launch.json',catalog)
    state=dict(status='launching_ordinary_copied_Reader41',directory=str(out),pid=os.getpid(),child_pid=None,command=command,new_predictions=0,new_training=False,native_Chat_verified=False)
    def mark():save(out/'protocol.json',state);save(V/'copied-Reader41-ordinary-benchmark-v1-current.json',state)
    first=None;run=None;started=time.monotonic();mark()
    with(out/'console.log').open('w')as log:
        child=subprocess.Popen(command,cwd='/',env={k:v for k,v in os.environ.items()if k not in ['PYTHONPATH','PYTHONHOME','VIRTUAL_ENV']},stdout=log,stderr=subprocess.STDOUT);state['child_pid']=child.pid;mark()
        while child.poll()is None:
            if pointer.exists():
                try:g=read(pointer)
                except (ValueError,OSError):g=None
                if g and g.get('pid')==child.pid:
                    run=Path(g['directory']);partial=run/'response.partial.txt'
                    if first is None and partial.exists()and partial.stat().st_size:
                        first=time.monotonic()-started;state.update(CLI_start_to_first_text_seconds=round(first,3));mark();print('First local text after',round(first,3),'seconds including setup/evidence.',flush=True)
            if time.monotonic()-started>900:
                state.update(status='observation_timeout_ordinary_Reader_child_may_be_live',elapsed_seconds=round(time.monotonic()-started,3));mark();raise TimeoutError('Observe existing child;do not restart')
            time.sleep(.1)
        code=child.returncode
    elapsed=time.monotonic()-started;state.update(child_pid=None,exit_code=code,CLI_start_to_completion_seconds=round(elapsed,3),CLI_start_to_first_text_seconds=round(first,3)if first is not None else None)
    if run is None or code:
        state.update(status='terminal_ordinary_Reader_no_completed_prediction',error=(out/'console.log').read_text()[-2500:]);mark();print(state['status'],flush=True);return
    g=read(run/'protocol.json');assert g['status']=='terminal_streamed_current_Reader41_pending_source_review'and g['new_predictions']==1,g
    state.update(status='terminal_ordinary_copied_Reader41_prediction_and_warm_CLI_timing_pending_review',run_directory=str(run),new_predictions=1,generation_seconds=g['seconds'],words=g['words'],word_limit_pass=g['word_limit_pass'],source_sha256={str(p):sha(p)for p in [Path(__file__),ROOT/'scripts/run_deck_status_live_v41.py',ROOT/'scripts/portable_biwn_entry_v21.py',entry,out/'loaded-models-before-launch.json',out/'console.log',run/'protocol.json',run/'prompt.json',run/'response.json',run/'response.txt',run/'evidence.json',run/'full-MCP-evidence.json',run/'prompts-and-responses.txt']},scope='Actual copied package CLI entry;model was inspected beforelaunch and entry preserves unrelated/busymodels. Timer includes interpreter/model-setup/evidence/streaming/exit. Firsttext observed bypolling flushed response.partial.txt at100msresolution. Warm single-runmeasurement,not coldmodel load,physicalperformance,nativeChat display or literalGUIclicklatency.');mark()
    print('Ordinary copied Reader41:',g['words'],'words;generation',g['seconds'],'seconds;whole CLI',round(elapsed,3),'seconds.',flush=True)

if __name__=='__main__':main()
