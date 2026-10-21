"""Finite v34 image qualification; reuse terminal gates and never restart live ones."""
import concurrent.futures,os,subprocess,threading,time
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,read,save

def main():
 out=V/'record-stride-image-qualification-pipeline-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 state=dict(status='waiting_existing_exact_gates',directory=str(out),pid=os.getpid(),children={},results={},new_predictions=0,new_training=False);mutex=threading.RLock()
 def mark():
  with mutex:save(out/'protocol.json',state);save(V/'record-stride-image-qualification-pipeline-v1-current.json',state)
 def existing(name,success):
  deadline=time.monotonic()+900;p=V/(name+'-current.json')
  while True:
   g=read(p)
   if g['status']==success:return
   if g['status'].startswith('terminal_'):raise RuntimeError((name,g['status'],g.get('error')))
   os.kill(g['pid'],0)
   if time.monotonic()>=deadline:raise TimeoutError('Observation timed out;inspect same live gate,do not restart:'+name)
   time.sleep(10)
 def run(name):
  log=out/(name+'.log');command=[str(ROOT/'.venv/bin/python3.12'),str(ROOT/'scripts'/name)]
  with log.open('w')as stream:
   child=subprocess.Popen(command,cwd=str(ROOT),stdout=stream,stderr=subprocess.STDOUT,env={**os.environ,'PYTHONPATH':str(ROOT/'scripts')})
   with mutex:state['children'][name]=child.pid;mark()
   code=child.wait(timeout=900)
  with mutex:state['children'].pop(name,None);state['results'][name]=dict(exit_code=code,log=str(log));mark()
  if code:raise RuntimeError(name+': '+log.read_text()[-3000:])
  print('Passed',name,flush=True)
 def batch(names):
  with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:
   results=list(pool.map(run,names))
 mark()
 try:
  existing('native-Deck-record-strides-final-v1','terminal_deeper_candidate_final_component_startup_heap_gates_pass')
  existing('scene17-record-strides-final-bridge-v1','terminal_scene17_shared_bridge_original_CPU_fixtures_match')
  state['status']='checking_functional_image_and_boundaries';mark()
  batch(['check_record_strides_disc_providers_v1.py','check_record_strides_final_fallback_v1.py','check_record_strides_alias_reentry_v1.py','check_native_deck_alias_nesting_record_strides_v1.py','check_native_record_strides_geometry_alias_v1.py','check_native_deck_outer_connected_record_strides_v1.py','check_record_strides_final_public_bus_v1.py','check_record_strides_final_display_v1.py','check_record_strides_final_copied_rebuild_v1.py'])
  state['status']='checking_actual_CPU_readonly_witnesses';mark()
  batch(['qualify_record_strides_reset_observer_v1.py','qualify_record_strides_clear_commit_observer_v1.py','qualify_record_strides_rotation_commit_observer_v1.py','check_record_strides_observer_actual_CPU_v1.py','check_record_strides_geometry_observer_actual_cpu_v1.py','check_record_strides_outer_observer_actual_CPU_v2.py','check_record_strides_fallback_alias_observers_actual_CPU_v1.py'])
  existing('record-strides-whole-scene-disc-v3','terminal_v30_vs_v33_whole_scene_actual_disc_providers_CPU_RAM_MMIO_pass')
  run('qualify_record_strides_fresh_preflight_v1.py')
  state['status']='terminal_record_stride_exact_image_and_readonly_observers_qualified';mark();print(state['status'],flush=True)
 except BaseException as error:
  state.update(status='terminal_record_stride_qualification_pipeline_failed',error=repr(error));mark();raise
if __name__=='__main__':main()
