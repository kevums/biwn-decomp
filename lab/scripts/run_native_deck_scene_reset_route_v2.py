"""Fresh scene-reset candidate and same-layout original-input control. Geometry stays compiled in both lanes.
Read-only monitors; no checkpoint restore or host guest-state injection.
"""
import argparse
from datetime import datetime,timezone
import json,os,re,signal,subprocess
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
from extract_biwn_stage import swap16
import task_arena_observer_source_v2 as regions
import shared_deck_observer_v4 as retained_shared_observer
import shared_deck_scene_reset_observer_v1 as shared_observer
from shared_deck_scene_reset_observer_v1 import observer_source
V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--control',action='store_true');args=ap.parse_args()
 bp=V/'native-Deck-scene-reset-disc-build-v1-current.json';build=read(bp);assert sha(build['derived_disc'])==build['derived_disc_sha256']
 final=read(V/'native-Deck-scene-reset-final-v1-current.json');assert final['status']=='terminal_deeper_candidate_final_component_startup_heap_gates_pass' and final['build_sha256']==sha(bp)
 names=['outer-scene-reset-geometry-observer-qualified-v1-current.json','scene-reset-geometry-observer-qualified-v1-current.json','shared-Deck-region-check-scene-reset-v1-current.json','shared-Deck-fallback-scene-reset-final-v1-current.json','native-deck-alias-nesting-scene-reset-final-v1-current.json','native-scene-reset-geometry-alias-v1-current.json','native-Deck-outer-connected-scene-reset-v1-current.json','scene-reset-input-observer-qualified-v1-current.json']
 proofs=[final]+[read(V/name)for name in names]
 assert proofs[4]['completed']==1280 and proofs[5]['completed']==256 and all(x['completed']==128 for x in proofs[6:8]) and proofs[8]['actual_input_pairs']==64
 for proof in proofs:
  for p,h in proof['source_sha256'].items():assert sha(p)==h,p
 actual_monitor=read(V/'scene-reset-observer-actual-CPU-v1-current.json');assert actual_monitor['status']=='terminal_exact_debug_observer_actual_combined_CPU_contracts_match'and actual_monitor['CPU_lanes']==64
 for p,h in actual_monitor['source_sha256'].items():assert sha(p)==h,p
 preflight=read(V/'scene-reset-geometry-observer-qualified-v1-current.json')
 parent=read(V/'native-Deck-coordinate-disc-build-current.json');old_job=read(V/'native-Deck-asset-repair-gameplay-current.json')
 out=V/'native-Deck-scene-reset-reset-route-v2'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')+('-control' if args.control else '-candidate'));out.mkdir(parents=True);print(out,flush=True)
 text,old_observer=observer_source(build,parent);cfile=out/'observer.c';cfile.write_text(text);library=out/'observer.dylib';assert sha(cfile)==sha(preflight['observer']),'Live observer differs from qualified source'
 direction_source=old_observer.with_name('direction-shadow-model.c');direction_model=out/'direction-shadow-model.c';direction_model.write_bytes(direction_source.read_bytes())
 result=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(cfile),str(direction_model),'-o',str(library)],capture_output=True,text=True);(out/'observer-compiler.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
 disc=Path(build['derived_disc'])
 if args.control:
  disc=out/'same-layout-original-input.cdi';subprocess.run(['/bin/cp','-c',build['derived_disc'],str(disc)],check=True)
  session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);at=read(session/'nextstage-mapping.json')['payload_raw_cdi_offset']+0x11b4c-0x4000
  baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();before=Path(build['derived_stage']).read_bytes()[0x11b4c-0x4000:0x11b56-0x4000]
  with disc.open('r+b')as f:f.seek(at);assert f.read(10)==swap16(before);f.seek(at);f.write(swap16(baseline[0x11b4c:0x11b56]));f.flush();os.fsync(f.fileno())
  save(out/'control-delta.json',dict(address='0x11b4c',declared_bytes=10,before=before.hex(),after=baseline[0x11b4c:0x11b56].hex(),parent_sha256=sha(build['derived_disc']),control_sha256=sha(disc)))
 probe_source=Path(old_job['directory'])/'probe.py';probe_text=probe_source.read_text()
 probe_text=probe_text.replace('from biwn_controller import JOYPAD_BUTTONS','from biwn_controller import JOYPAD_BUTTONS, KEYBOARD_BUTTONS')
 probe_text=probe_text.replace('navigation_inputs = set()','navigation_inputs = set()\n    navigation_keyboard_inputs=set()')
 ka='        if pressed:\n            pressed_input_samples';assert probe_text.count(ka)==1
 probe_text=probe_text.replace(ka,'        if navigation_enabled and port==0 and device==3 and index==0:\n            pressed=button in navigation_keyboard_inputs\n'+ka)
 probe_text=probe_text.replace('navigation_inputs={button_ids[name]for name in buttons}','navigation_inputs={button_ids[name]for name in buttons if name in button_ids}\n                navigation_keyboard_inputs={KEYBOARD_BUTTONS[name]for name in buttons if name in KEYBOARD_BUTTONS}')
 probe_text,n=re.subn(r"(?m)^        observer=c.CDLL\('[^']+'\)",'        observer=c.CDLL('+repr(str(library))+')',probe_text);assert n==1
 probe_text,n=re.subn(r"observer_payload=c.create_string_buffer\(Path\('[^']+'\).read_bytes\(\)\)",'observer_payload=c.create_string_buffer(Path('+repr(build['component'])+').read_bytes())',probe_text);assert n==1
 anchor="        assert observer.finish_observe(str(out/'gameplay-observation.json').encode())==0";assert probe_text.count(anchor)==1
 probe_text=probe_text.replace(anchor,anchor+"\n        observer.shared_dump.argtypes=[c.c_char_p];observer.shared_dump.restype=c.c_int\n        assert observer.shared_dump(str(out/'shared-observation.json').encode())==0")
 old_stop="            if deck_trial_start is not None and current_frame-deck_trial_start>=400:break"
 new_stop="            if deck_trial_start is not None and current_frame-deck_trial_start>=800:\n                if observer.observer_quiescent():break\n                assert current_frame-deck_trial_start<1312,'Watched calls did not quiesce within512release frames'"
 assert probe_text.count(old_stop)==1;probe_text=probe_text.replace(old_stop,new_stop)
 old_input="buttons=['1']if 1<=offset<9 else ['B','C']if 25<=offset<34 else ['0']if 225<=offset<234 else []"
 new_input="buttons=['1']if 1<=offset<9 else ['B','C']if 25<=offset<34 else ['U']if 50<=offset<130 else ['U','L']if 145<=offset<185 else ['*']if 195<=offset<675 and (offset-195)%40<28 else ['0']if 725<=offset<734 else []"
 assert probe_text.count(old_input)==1;probe_text=probe_text.replace(old_input,new_input)
 probe_text=probe_text.replace("Ordinary keypad1,release,B+C,release,0,release after fresh outdoor route.","Ordinary keypad1,release,B+C,release,U,U+L,release,0,release after fresh outdoor route.")
 face_anchor="        assert observer.shared_dump(str(out/'shared-observation.json').encode())==0"
 assert probe_text.count(face_anchor)==1;probe_text=probe_text.replace(face_anchor,face_anchor+"\n        observer.face_dump.argtypes=[c.c_char_p];observer.face_dump.restype=c.c_int\n        assert observer.face_dump(str(out/'face-observation.json').encode())==0")
 geometry_anchor="        assert observer.face_dump(str(out/'face-observation.json').encode())==0"
 assert probe_text.count(geometry_anchor)==1
 probe_text=probe_text.replace(geometry_anchor,geometry_anchor+"\n        observer.geometry_dump.argtypes=[c.c_char_p];observer.geometry_dump.restype=c.c_int\n        assert observer.geometry_dump(str(out/'geometry-observation.json').encode())==0")
 outer_anchor="        assert observer.geometry_dump(str(out/'geometry-observation.json').encode())==0"
 assert probe_text.count(outer_anchor)==1
 probe_text=probe_text.replace(outer_anchor,outer_anchor+"\n        observer.outer_dump.argtypes=[c.c_char_p];observer.outer_dump.restype=c.c_int\n        assert observer.outer_dump(str(out/'outer-observation.json').encode())==0")
 # Preserve all new counter dumps even when a retained finish gate rejects.
 before="        assert observer.finish_observe(str(out/'gameplay-observation.json').encode())==0"
 assert probe_text.count(before)==1
 probe_text=probe_text.replace(before,"        retained_finish=observer.finish_observe(str(out/'gameplay-observation.json').encode())")
 after="        assert observer.outer_dump(str(out/'outer-observation.json').encode())==0"
 probe_text=probe_text.replace(after,after+"\n        assert retained_finish==0")
 reset_anchor="        assert observer.face_dump(str(out/'face-observation.json').encode())==0";assert probe_text.count(reset_anchor)==1
 probe_text=probe_text.replace(reset_anchor,reset_anchor+"\n        observer.reset_dump.argtypes=[c.c_char_p];observer.reset_dump.restype=c.c_int\n        assert observer.reset_dump(str(out/'reset-observation.json').encode())==0")
 probe=out/'probe.py';probe.write_text(probe_text);command=list(old_job['command']);command[2]=str(probe);command[command.index('--disc')+1]=str(disc);command[command.index('--output')+1]=str(out/'candidate')
 pointer=V/('native-Deck-scene-reset-reset-v2-'+('control' if args.control else 'candidate')+'-current.json')
 state=dict(status='running_fresh_native_outer_route',directory=str(out),pid=os.getpid(),command=command,control=args.control,build=str(bp),build_sha256=sha(bp),source_sha256={str(p):sha(p)for p in[Path(__file__),old_observer,cfile,library,probe_source,probe,direction_source,direction_model,Path(regions.__file__),Path(shared_observer.__file__),Path(retained_shared_observer.__file__),V/'scene-reset-observer-actual-CPU-v1-current.json']},component_gate_files=names,observer_geometry_completion_scope='Both lanes execute six compiled geometry helpers and the same native layout. Control restores only the original input entry. Candidate input dispatch adds the hybrid1102Areset. Ordinary frontend keyboard star pulse triggers reset;read-only observer checks native logicalCPU/memory/service commit. This comparison includes the whole original-versus-native input caller,not an isolated reset-only timing claim.',snapshot_restores=0,host_guest_RAM_writes=0,host_CPU_or_task_seeds=0,new_training=False,whole_game_complete=False)
 def mark():save(out/'protocol.json',state);save(pointer,state)
 mark();child=None
 try:
  with(out/'runtime.log').open('w')as log:
   child=subprocess.Popen(command,cwd='/',stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'PYTHONPATH':str(ROOT/'scripts')},start_new_session=True);state['child_pid']=child.pid;mark()
   try:code=child.wait(timeout=900)
   except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait();raise
  state['child_pid']=None;assert code==0,(out/'runtime.log').read_text()[-4000:]
  report=read(out/'candidate/report.json');observed=read(out/'candidate/gameplay-observation.json');inputs=read(out/'candidate/shared-observation.json')
  assert 800<=len(report['ordinary_Deck_input_trial']['inputs'])<=1312
  retained_errors={k:v for k,v in observed.items()if isinstance(v,(int,float))and any(s in k for s in ['error','pending','outside','corruption','collision'])};assert retained_errors and not any(retained_errors.values()),retained_errors
  assert not any(inputs[k]for k in ['errors','pending','C_stack_outside'])
  assert inputs['native_entries']==inputs['native_returns'] and inputs['helper_entries']==inputs['helper_returns']
  assert all(inputs['native_entries'][i]>0 and inputs['original_body_steps'][i]==0 for i in [0,2,3]) and inputs['fallback_entries']==[0]*5
  if args.control:assert inputs['native_entries'][1]==0 and inputs['original_body_steps'][1]>0
  else:assert inputs['native_entries'][1]>0 and inputs['original_body_steps'][1]==0
  face=read(out/'candidate/face-observation.json');assert face['entries']==face['returns']>0 and face['positive_speed_entries']>0 and face['errors']==face['pending']==0
  assert face['native_parent_returns']==face['suspended_native_parent_checks']==face['returns'] and face['original_parent_returns']==0
  geometry=read(out/'candidate/geometry-observation.json')
  assert geometry['entries']==geometry['returns']==geometry['matched_outer_parent_returns']>0 and geometry['errors']==geometry['pending']==0
  assert geometry['helper_entries']==geometry['helper_returns']==[geometry['entries']]*5
  assert geometry['original_body_steps']==0 and inputs['native_entries'][4]==geometry['entries']
  assert geometry['compiled_helper_services']==geometry['compiled_helper_markers']==[geometry['entries']]*5
  assert geometry['transform_entries']==geometry['transform_returns']==geometry['entries']
  assert geometry['original_transform_entries']==geometry['original_transform_returns']==geometry['original_transform_steps']==0
  assert geometry['original_faces_body_steps']==0 and geometry['native_GPU_entries']==geometry['native_GPU_returns']>0 and geometry['original_GPU_entries']==geometry['original_GPU_returns']==0
  want_debug=16*geometry['debug_active_entries'];assert geometry['debug_active_entries']+geometry['debug_inactive_entries']==geometry['entries']
  assert geometry['native_debug_dependency_entries']==geometry['native_debug_dependency_returns']==want_debug
  assert geometry['original_debug_dependency_entries']==geometry['original_debug_dependency_returns']==geometry['original_debug_body_steps']==0
  outer=read(out/'candidate/outer-observation.json')
  assert not any(outer[k]for k in ['errors','pending','helper_pending','C_stack_outside','fallbacks'])
  assert outer['helper_entries']==outer['helper_returns'] and all(outer['helper_entries'][k]>0 for k in [0,1,5,11,12])
  assert outer['public_entries']==outer['native_entries']==outer['native_returns']>0 and outer['original_returns']==outer['original_body_steps']==0
  assert outer['C_stack_observations']>0 and outer['C_stack_low_offset']>=144 and outer['protected_frame_checks']>0
  reset=read(out/'candidate/reset-observation.json');assert reset['errors']==reset['pending']==0 and reset['entries']==reset['returns']==reset['markers']
  assert reset['original_global_entries']==reset['original_global_returns']>0
  if args.control:assert reset['entries']==0
  else:assert reset['entries']>0
  state.update(reset_observation=reset)
  state.update(status='terminal_fresh_debug_geometry_route_pending_review',frames=len(report['frames']),shared_observation=inputs,face_observation=face,geometry_observation=geometry,outer_observation=outer,retained_observation=observed,report=str(out/'candidate/report.json'),report_sha256=sha(out/'candidate/report.json'));mark();print(state['status'],inputs,face,flush=True)
 except BaseException as error:state.update(status='terminal_failed',error=repr(error),child_pid=None if child is None or child.poll()is not None else child.pid);mark();raise

if __name__=='__main__':main()
