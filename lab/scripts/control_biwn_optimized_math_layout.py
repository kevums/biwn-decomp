"""Hold startup instructions, copy length and heap layout fixed; change math.
This1500frame ablation is an unpromoted control, not a replacement preview.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,shutil,subprocess,os
from check_biwn_native_button_digit import ROOT,sha,save
from extract_biwn_stage import swap16

def main():
 out=ROOT/'verification/native-math-layout-control'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 oldp=ROOT/'verification/native-bundle-disc-cold-boot-current.json';old=json.loads(oldp.read_text());build=json.loads(Path(old['build_proof']).read_text());fastp=ROOT/'verification/native-optimized-math-current.json';fast=json.loads(fastp.read_text());payload=Path(fast['compiled_binary']).read_bytes();oldcode=Path(build['component']).read_bytes();assert len(payload)<len(oldcode)
 for name in ['biwn_native_button_digit','biwn_native_multiply','biwn_native_division','biwn_native_remainder','biwn_native_startup_finalize']:assert fast['symbols'][name]==build['symbols'][name]
 padded=payload+bytes(len(oldcode)-len(payload));(out/'padded-component.bin').write_bytes(padded)
 session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'nextstage-mapping.json').read_text());header_bytes=build['native_entry_bytes']-len(oldcode);offset=mapping['payload_raw_cdi_offset']+build['staging_address']-0x4000+header_bytes
 image=out/'optimized-math-fixed-layout-control.cdi';shutil.copyfile(build['derived_disc'],image)
 with image.open('r+b')as f:f.seek(offset);assert f.read(len(oldcode))==swap16(oldcode);f.seek(offset);f.write(swap16(padded))
 with Path(build['derived_disc']).open('rb')as a,image.open('rb')as b:
  position=0
  while True:
   left=a.read(1048576);right=b.read(1048576);assert len(left)==len(right)
   if not left:break
   for i,(x,y)in enumerate(zip(left,right)):
    if x!=y:assert offset<=position+i<offset+len(oldcode)
   position+=len(left)
 base=Path(old['directory']);text=(base/'native_observer.c').read_text();start=text.index('static const unsigned char payload[]={');end=text.index('};',start)+2;text=text[:start]+'static const unsigned char payload[]={'+','.join(str(x)for x in padded)+'};'+text[end:]
 source=out/'control_observer.c';source.write_text(text);lib=out/'libcontrol-observer.dylib';p=subprocess.run(['clang','-dynamiclib','-std=c11','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(lib)],capture_output=True,text=True);(out/'compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 text=(base/'fresh_native_disc_probe.py').read_text();assert text.count(str(base/'libnative-observer.dylib'))==1;text=text.replace(str(base/'libnative-observer.dylib'),str(lib));probe=out/'control_probe.py';probe.write_text(text)
 run=next(x['command'][:]for x in old['commands']if x['lane']=='candidate');run[1]=str(probe);run[run.index('--disc')+1]=str(image);run[run.index('--frames')+1]='1500';run[run.index('--output')+1]=str(out/'control');run[run.index('--frame-controller-script')+1]=str(out/'ordinary-input.json');save(out/'ordinary-input.json',dict(windows=[]))
 state=dict(status='prepared',pid=os.getpid(),directory=str(out),command=run,original_bundle_proof=str(oldp),original_bundle_proof_sha256=sha(oldp),optimized_component_proof=str(fastp),optimized_component_proof_sha256=sha(fastp),frames=1500,only_CDI_payload_window_changed=True,startup_copy_and_heap_layout_unchanged=True,source_raw_bytes=len(payload),padded_bytes=len(padded),whole_game_complete=False,preview_promoted=False)
 def checkpoint():save(out/'protocol.json',state);save(ROOT/'verification/native-math-layout-control-active.json',state)
 checkpoint();print(out,flush=True)
 try:
  with(out/'runtime.log').open('w')as log:
   child=subprocess.Popen(run,stdout=log,stderr=subprocess.STDOUT);state.update(status='running_control',child_pid=child.pid);checkpoint();rc=child.wait()
  assert rc==0,out/'runtime.log';report=json.loads((out/'control/report.json').read_text());obs=json.loads((out/'control/native-observation.json').read_text());assert not obs['errors']and not obs['copy_errors']and not obs['arithmetic_original_steps']
  fields=['raw_player_X','raw_player_Z','scene_word','player_mode_word','tile_word','equipped_word','movie_flag_words','movie_controller_state_word'];comparisons={}
  for lane in ['reference','candidate']:
   ref=json.loads((base/lane/'report.json').read_text())['frames'][:1500];different_video=[a['frame']for a,b in zip(report['frames'],ref)if a['video_sha256']!=b['video_sha256']];different_state=[a['frame']for a,b in zip(report['frames'],ref)if any(a[k]!=b[k]for k in fields)];comparisons[lane]=dict(video_different_frames=different_video,tracked_state_different_frames=different_state)
  state.update(status='terminal_fixed_layout_optimized_math_control_observed',comparisons=comparisons,observation=obs,source_sha256={str(p):sha(p)for p in [Path(__file__),source,lib,probe]},derived_disc_sha256=sha(image),scope='Same first native bundle startup instructions,copy byte count,heap boundary,keypad jumps and staging clear; only copied native code bytes/padding differ.1500fresh HLE frames. Optimized arithmetic changes instruction cost while preserving tested return semantics; physical timing/complete source game not proved.')
  checkpoint();save(ROOT/'verification/native-math-layout-control-current.json',state);print(json.dumps({lane:{key:len(value)for key,value in row.items()}for lane,row in comparisons.items()}),flush=True)
 except BaseException as error:state.update(status='terminal_failed',error=repr(error));checkpoint();raise
if __name__=='__main__':main()
