"""Qualify the actual v37 image in dependency order; keep live handles on timeout."""
import concurrent.futures,os,subprocess,threading
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha

STAGES=[[
 ('check_record_loop_image_disc_providers_v1.py','record-loop-image-disc-providers-v1'),
 ('check_record_loop_image_final_fallback_v1.py','record-loop-image-final-fallback-v1'),
 ('check_record_loop_image_alias_reentry_v1.py','record-loop-image-alias-reentry-v1'),
 ('check_native_deck_alias_nesting_record_loop_image_v1.py','native-deck-alias-nesting-record-loop-image-final-v1'),
 ('check_native_record_loop_image_geometry_alias_v1.py','native-record-loop-image-geometry-alias-v1'),
 ('check_native_deck_outer_connected_record_loop_image_v1.py','native-Deck-outer-connected-record-loop-image-v1'),
 ('check_record_loop_image_final_public_bus_v1.py','record-loop-image-final-public-bus-v1'),
 ('check_record_loop_image_final_display_v1.py','record-loop-image-final-display-v1'),
 ('check_record_loop_image_final_copied_rebuild_v1.py','record-loop-image-final-copied-rebuild-v1'),
 ('check_record_loop_image_whole_scene_disc_v3.py','record-loop-image-whole-scene-disc-v3')],[
 ('qualify_record_loop_image_geometry_observer_v1.py','record-loop-image-geometry-observer-qualified-v1')],[
 ('qualify_record_loop_image_outer_observer_v1.py','outer-record-loop-image-geometry-observer-qualified-v1')],[
 ('check_shared_deck_observer_regions_record_loop_image_v1.py','shared-Deck-region-check-record-loop-image-v1'),
 ('qualify_record_loop_image_shared_observer_v1.py','record-loop-image-shared-observer-qualified-v1'),
 ('qualify_record_loop_image_commit_observer_v1.py','record-loop-image-commit-observer-qualified-v1'),
 ('qualify_record_loop_image_reset_observer_v1.py','record-loop-image-reset-observer-qualified-v1'),
 ('qualify_record_loop_image_clear_commit_observer_v1.py','record-loop-image-clear-commit-observer-v1'),
 ('qualify_record_loop_image_rotation_commit_observer_v1.py','record-loop-image-rotation-commit-observer-v1')],[
 ('check_record_loop_image_observer_actual_CPU_v1.py','record-loop-image-record-observer-actual-CPU-v1'),
 ('check_record_loop_image_geometry_observer_actual_cpu_v1.py','record-loop-image-geometry-observer-actual-CPU-v1'),
 ('check_record_loop_image_outer_observer_actual_CPU_v2.py','record-loop-image-outer-observer-actual-CPU-v2'),
 ('check_record_loop_image_fallback_alias_observers_actual_CPU_v1.py','record-loop-image-fallback-alias-observers-actual-CPU-v1')]]

def main():
    out=V/'record-loop-image-qualification-pipeline-v3'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    state=dict(status='validating_existing_exact_gates',directory=str(out),pid=os.getpid(),children={},results={},new_predictions=0,new_training=False);mutex=threading.RLock()
    def mark():
        with mutex:save(out/'protocol.json',state);save(V/'record-loop-image-qualification-pipeline-v3-current.json',state)
    def verify(pointer):
        proof=read(pointer);assert proof['status'].startswith('terminal_')and 'failed'not in proof['status'],(pointer,proof['status'])
        for path,h in proof.get('source_sha256',{}).items():assert sha(path)==h,path
        return proof
    def run(item):
        script,name=item;pointer=V/(name+'-current.json')
        if pointer.exists():
            g=read(pointer)
            if g['status'].startswith('terminal_')and'failed'not in g['status']:
                verify(pointer)
                with mutex:state['results'][script]=dict(reused_terminal=True,proof=str(pointer));mark()
                return
            if not g['status'].startswith('terminal_')and g.get('pid'):
                try:os.kill(g['pid'],0)
                except ProcessLookupError:pass
                else:raise RuntimeError('Existing live gate;observe its handle instead of restarting:'+str(pointer))
        log=out/(script+'.log')
        with log.open('w')as stream:
            child=subprocess.Popen([str(ROOT/'.venv/bin/python3.12'),str(ROOT/'scripts'/script)],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,env={**os.environ,'PYTHONPATH':str(ROOT/'scripts')})
            with mutex:state['children'][script]=child.pid;mark()
            try:code=child.wait(timeout=900)
            except subprocess.TimeoutExpired:
                with mutex:state.update(status='observation_timeout_children_may_be_live');mark()
                raise
        with mutex:state['children'].pop(script,None);state['results'][script]=dict(exit_code=code,log=str(log));mark()
        assert code==0,(script,log.read_text()[-4500:]);verify(pointer);print('Passed',script,flush=True)
    mark()
    try:
        verify(V/'native-Deck-record-loop-image-final-v1-current.json');verify(V/'scene17-record-loop-image-final-bridge-v1-current.json')
        for stage,items in enumerate(STAGES,1):
            state.update(status='qualifying_stage_'+str(stage));mark()
            with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:list(pool.map(run,items))
        run(('qualify_record_loop_image_fresh_preflight_v1.py','record-loop-image-fresh-preflight-v1'))
        state.update(status='terminal_v37_exact_image_providers_aliases_and_readonly_observers_qualified');mark();print(state['status'],flush=True)
    except BaseException as error:
        state.update(status='observation_timeout_children_may_be_live'if isinstance(error,subprocess.TimeoutExpired)else'terminal_record_loop_image_qualification_failed',error=repr(error));mark();raise

if __name__=='__main__':main()
