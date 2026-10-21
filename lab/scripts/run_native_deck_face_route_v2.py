"""Fresh three-caller candidate/control, original firmware helpers and CPU.
Read-only monitors; no checkpoint restore or host guest-state injection.
"""
import argparse
from datetime import datetime,timezone
import json,os,re,signal,subprocess
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
from extract_biwn_stage import swap16
import task_arena_observer_source_v2 as regions
import shared_deck_observer_v2 as retained_shared_observer
import shared_deck_face_observer_v1 as shared_observer
from shared_deck_face_observer_v1 import observer_source
V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--control',action='store_true');args=ap.parse_args()
 bp=V/'native-Deck-shared-disc-build-v2-current.json';build=read(bp);assert sha(build['derived_disc'])==build['derived_disc_sha256']
 startup=read(V/'native-Deck-shared-startup-heap-v2-current.json');assert startup['startup_cases']==6 and startup['heap_initialize_cases']==192
 capacity=read(V/'native-Deck-shared-capacity-v2-current.json');assert capacity['cases']==36
 final=read(V/'native-deck-shared-final-v2-current.json');nested=read(V/'native-deck-shared-connected-final-v2-current.json');assert final['completed']==2880 and final['deployed_module_byte_identity'] and nested['completed']>=128
 for proof in [startup,capacity,final,nested]:
  for p,h in proof['source_sha256'].items():assert sha(p)==h,p
 parent=read(V/'native-Deck-coordinate-disc-build-current.json');old_job=read(V/'native-Deck-asset-repair-gameplay-current.json')
 out=V/'native-Deck-face-route-v2'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')+('-control' if args.control else '-candidate'));out.mkdir(parents=True);print(out,flush=True)
 text,old_observer=observer_source(build,parent);cfile=out/'observer.c';cfile.write_text(text);library=out/'observer.dylib'
 direction_source=old_observer.with_name('direction-shadow-model.c');direction_model=out/'direction-shadow-model.c';direction_model.write_bytes(direction_source.read_bytes())
 result=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(cfile),str(direction_model),'-o',str(library)],capture_output=True,text=True);(out/'observer-compiler.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
 disc=Path(build['derived_disc'])
 if args.control:
  disc=out/'same-layout-original-scan.cdi';subprocess.run(['/bin/cp','-c',build['derived_disc'],str(disc)],check=True)
  session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);at=read(session/'nextstage-mapping.json')['payload_raw_cdi_offset']+0x11828-0x4000
  baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();before=Path(build['derived_stage']).read_bytes()[0x11828-0x4000:0x1182e-0x4000]
  with disc.open('r+b')as f:f.seek(at);assert f.read(6)==swap16(before);f.seek(at);f.write(swap16(baseline[0x11828:0x1182e]));f.flush();os.fsync(f.fileno())
  save(out/'control-delta.json',dict(address='0x11828',declared_bytes=6,before=before.hex(),after=baseline[0x11828:0x1182e].hex(),parent_sha256=sha(build['derived_disc']),control_sha256=sha(disc)))
 probe_source=Path(old_job['directory'])/'probe.py';probe_text=probe_source.read_text()
 probe_text,n=re.subn(r"(?m)^        observer=c.CDLL\('[^']+'\)",'        observer=c.CDLL('+repr(str(library))+')',probe_text);assert n==1
 probe_text,n=re.subn(r"observer_payload=c.create_string_buffer\(Path\('[^']+'\).read_bytes\(\)\)",'observer_payload=c.create_string_buffer(Path('+repr(build['component'])+').read_bytes())',probe_text);assert n==1
 anchor="        assert observer.finish_observe(str(out/'gameplay-observation.json').encode())==0";assert probe_text.count(anchor)==1
 probe_text=probe_text.replace(anchor,anchor+"\n        observer.shared_dump.argtypes=[c.c_char_p];observer.shared_dump.restype=c.c_int\n        assert observer.shared_dump(str(out/'shared-observation.json').encode())==0")
 old_stop="            if deck_trial_start is not None and current_frame-deck_trial_start>=400:break"
 new_stop="            if deck_trial_start is not None and current_frame-deck_trial_start>=400:\n                if observer.observer_quiescent():break\n                assert current_frame-deck_trial_start<912,'Watched calls did not quiesce within512release frames'"
 assert probe_text.count(old_stop)==1;probe_text=probe_text.replace(old_stop,new_stop)
 old_input="buttons=['1']if 1<=offset<9 else ['B','C']if 25<=offset<34 else ['0']if 225<=offset<234 else []"
 new_input="buttons=['1']if 1<=offset<9 else ['B','C']if 25<=offset<34 else ['U']if 50<=offset<130 else ['U','L']if 145<=offset<185 else ['0']if 225<=offset<234 else []"
 assert probe_text.count(old_input)==1;probe_text=probe_text.replace(old_input,new_input)
 probe_text=probe_text.replace("Ordinary keypad1,release,B+C,release,0,release after fresh outdoor route.","Ordinary keypad1,release,B+C,release,U,U+L,release,0,release after fresh outdoor route.")
 face_anchor="        assert observer.shared_dump(str(out/'shared-observation.json').encode())==0"
 assert probe_text.count(face_anchor)==1;probe_text=probe_text.replace(face_anchor,face_anchor+"\n        observer.face_dump.argtypes=[c.c_char_p];observer.face_dump.restype=c.c_int\n        assert observer.face_dump(str(out/'face-observation.json').encode())==0")
 probe=out/'probe.py';probe.write_text(probe_text);command=list(old_job['command']);command[2]=str(probe);command[command.index('--disc')+1]=str(disc);command[command.index('--output')+1]=str(out/'candidate')
 pointer=V/('native-Deck-face-v2-'+('control' if args.control else 'candidate')+'-current.json')
 state=dict(status='running_fresh_native_face_route',directory=str(out),pid=os.getpid(),command=command,control=args.control,build=str(bp),build_sha256=sha(bp),source_sha256={str(p):sha(p)for p in[Path(__file__),old_observer,cfile,library,probe_source,probe,direction_source,direction_model,Path(regions.__file__),Path(shared_observer.__file__),Path(retained_shared_observer.__file__)]},snapshot_restores=0,host_guest_RAM_writes=0,host_CPU_or_task_seeds=0,new_training=False,whole_game_complete=False)
 def mark():save(out/'protocol.json',state);save(pointer,state)
 mark();child=None
 try:
  with(out/'runtime.log').open('w')as log:
   child=subprocess.Popen(command,cwd='/',stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'PYTHONPATH':str(ROOT/'scripts')},start_new_session=True);state['child_pid']=child.pid;mark()
   try:code=child.wait(timeout=900)
   except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait();raise
  state['child_pid']=None;assert code==0,(out/'runtime.log').read_text()[-4000:]
  report=read(out/'candidate/report.json');observed=read(out/'candidate/gameplay-observation.json');inputs=read(out/'candidate/shared-observation.json')
  assert 400<=len(report['ordinary_Deck_input_trial']['inputs'])<=912
  retained_errors={k:v for k,v in observed.items()if isinstance(v,(int,float))and any(s in k for s in ['error','pending','outside','corruption','collision'])};assert retained_errors and not any(retained_errors.values()),retained_errors
  assert not any(inputs[k]for k in ['errors','pending','C_stack_outside'])
  assert inputs['native_entries']==inputs['native_returns'] and inputs['helper_entries']==inputs['helper_returns']
  if not args.control:assert all(n>0 for n in inputs['native_entries']) and inputs['original_body_steps']==inputs['fallback_entries']==[0,0,0]
  else:assert inputs['native_entries'][2]==0 and inputs['original_body_steps'][2]>0
  face=read(out/'candidate/face-observation.json');assert face['entries']==face['returns']==face['positive_speed_entries']>0 and face['errors']==face['pending']==0
  if not args.control:assert face['native_parent_returns']==face['suspended_native_parent_checks']==face['returns']
  else:assert face['original_parent_returns']==face['returns'] and face['native_parent_returns']==0
  state.update(status='terminal_fresh_face_route_pending_review',frames=len(report['frames']),shared_observation=inputs,face_observation=face,retained_observation=observed,report=str(out/'candidate/report.json'),report_sha256=sha(out/'candidate/report.json'));mark();print(state['status'],inputs,face,flush=True)
 except BaseException as error:state.update(status='terminal_failed',error=repr(error),child_pid=None if child is None or child.poll()is not None else child.pid);mark();raise

if __name__=='__main__':main()
