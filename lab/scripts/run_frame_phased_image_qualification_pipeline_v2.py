"""Qualify the actual v39 image in dependency order; keep live handles on timeout."""
import concurrent.futures,os,subprocess,threading
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha

STAGES=[[
 ('check_frame_phased_image_disc_providers_v1.py','frame-phased-image-disc-providers-v1'),
 ('check_frame_phased_image_final_fallback_v1.py','frame-phased-image-final-fallback-v1'),
 ('check_frame_phased_image_alias_reentry_v1.py','frame-phased-image-alias-reentry-v1'),
 ('check_native_deck_alias_nesting_frame_phased_image_v1.py','native-deck-alias-nesting-frame-phased-image-final-v1'),
 ('check_native_frame_phased_image_geometry_alias_v1.py','native-frame-phased-image-geometry-alias-v1'),
 ('check_native_deck_outer_connected_frame_phased_image_v1.py','native-Deck-outer-connected-frame-phased-image-v1'),
 ('check_frame_phased_image_final_public_bus_v1.py','frame-phased-image-final-public-bus-v1'),
 ('check_frame_phased_image_final_display_v1.py','frame-phased-image-final-display-v1'),
 ('check_frame_phased_image_final_copied_rebuild_v1.py','frame-phased-image-final-copied-rebuild-v1'),
 ('check_frame_phased_image_whole_scene_disc_v3.py','frame-phased-image-whole-scene-disc-v3')],[
 ('qualify_frame_phased_image_geometry_observer_v2.py','frame-phased-image-geometry-observer-qualified-v1')],[
 ('qualify_frame_phased_image_outer_observer_v1.py','outer-frame-phased-image-geometry-observer-qualified-v1')],[
 ('check_shared_deck_observer_regions_frame_phased_image_v1.py','shared-Deck-region-check-frame-phased-image-v1'),
 ('qualify_frame_phased_image_shared_observer_v1.py','frame-phased-image-shared-observer-qualified-v1'),
 ('qualify_frame_phased_image_commit_observer_v1.py','frame-phased-image-commit-observer-qualified-v1'),
 ('qualify_frame_phased_image_reset_observer_v1.py','frame-phased-image-reset-observer-qualified-v1'),
 ('qualify_frame_phased_image_clear_commit_observer_v1.py','frame-phased-image-clear-commit-observer-v1'),
 ('qualify_frame_phased_image_rotation_commit_observer_v1.py','frame-phased-image-rotation-commit-observer-v1')],[
 ('check_frame_phased_image_observer_actual_CPU_v1.py','frame-phased-image-record-observer-actual-CPU-v1'),
 ('check_frame_phased_image_geometry_observer_actual_cpu_v1.py','frame-phased-image-geometry-observer-actual-CPU-v1'),
 ('check_frame_phased_image_outer_observer_actual_CPU_v2.py','frame-phased-image-outer-observer-actual-CPU-v2'),
 ('check_frame_phased_image_fallback_alias_observers_actual_CPU_v1.py','frame-phased-image-fallback-alias-observers-actual-CPU-v1')]]

def main():
    out=V/'frame-phased-image-qualification-pipeline-v2'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    state=dict(status='validating_existing_exact_gates',directory=str(out),pid=os.getpid(),children={},results={},new_predictions=0,new_training=False);mutex=threading.RLock()
    def mark():
        with mutex:save(out/'protocol.json',state);save(V/'frame-phased-image-qualification-pipeline-v2-current.json',state)
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
        verify(V/'native-Deck-frame-phased-image-final-v1-current.json');verify(V/'scene17-frame-phased-image-final-bridge-v1-current.json')
        for stage,items in enumerate(STAGES,1):
            state.update(status='qualifying_stage_'+str(stage));mark()
            with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:list(pool.map(run,items))
        # Additional resource/input monitor controls and actual-CPU proof are
        # required before a separate fresh preflight can be issued.
        state.update(status='terminal_v40_retained_image_gates_pass_resource_input_observer_extra_checks_pending');mark();print(state['status'],flush=True)
    except BaseException as error:
        state.update(status='observation_timeout_children_may_be_live'if isinstance(error,subprocess.TimeoutExpired)else'terminal_frame_phased_image_qualification_failed',error=repr(error));mark();raise

if __name__=='__main__':main()
