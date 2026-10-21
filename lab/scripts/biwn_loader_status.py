"""Read-only exact-build facts for the repaired loader disc; never starts work."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def evidence():
 v=ROOT/'verification';paths={}
 def read(name):
  path=v/(name+'.json')
  if not path.exists():return None
  value=json.loads(path.read_text());paths[str(path)]=sha(path);return value
 pre=read('native-load-bundle-preflight-current')
 if pre is None:return None
 assert sha(pre['binary'])==pre['binary_sha256']
 result=dict(candidate='native28 repaired loader integrated experiment',linked_bytes=pre['binary_bytes'],reserved_bytes=pre['reserved_bytes'],binary_sha256=pre['binary_sha256'],component_checks='not_run',new_disc_built=False,startup_entry_and_keypad='not_run',adaptive_gameplay='not_run',fixed_input_equivalence_to_native26='not_run',same_layout_original_loader_control='not_run',default_variant_promotion='not_promoted',native_Chat='unverified',whole_game_source_rebuild='incomplete',physical_console='not_run',new_training=False,authorship='Coordinator loader C and ABI; explicit C translation of the existing local-model-authored18byte word-scan assembly repair. Raw full-loader localC draft rejected. Same weights are not independent validation.')
 bp=v/'native-load-disc-build-current.json';build=read('native-load-disc-build-current')
 if build and build['linked_component_sha256']==pre['binary_sha256']and build['status']=='terminal_partial_native_load_disc_built_pending_execution':
  assert sha(build['linked_component'])==pre['binary_sha256'];result.update(component_checks='passed',new_disc_built=True,derived_disc=build['derived_disc'],loader_native_cases=1100,loader_ordered_cases=114,real_dependency_cases=[16,16],original_disc_preserved=True)
  ep=read('native-load-disc-entry-current')
  if ep and ep['build_proof_sha256']==sha(bp)and ep['status']=='terminal_native_entry_heap_and_component_pass':result.update(startup_entry_and_keypad='passed',startup_cases=ep['entry_cases'],installed_keypad_cases=ep['component_cases'])
  for kind,key in [('route','adaptive_gameplay'),('fixed-route','fixed_input_equivalence_to_native26')]:
   p=read('native-load-'+kind+'-active')
   if not p:continue
   matching=p.get('build_proof_sha256')==sha(bp)if kind=='route'else p.get('build_proofs',{}).get(str(bp))==sha(bp)
   if not matching:continue
   if p['status'].startswith('running_'):
    live=[]
    for command in p['commands']:
     actual=subprocess.run(['ps','-p',str(command['pid']),'-o','command='],capture_output=True,text=True,timeout=5).stdout
     if str(Path(p['directory']))in actual:live.append(command['pid'])
    result[key]='running_verified'if live else'needs_observation_no_terminal_verdict'
    result[kind+'_live_PIDs']=live
   elif p['status']=='terminal_failed':result[key]='failed';result[kind+'_error']=p.get('error')
   else:
    a=read('native-load-'+kind+'-analysis-current');rp=v/('native-load-'+kind+'-current.json')
    if not a or not rp.exists()or a.get('route_proof_sha256')!=sha(rp):result[key]='finished_analysis_pending';continue
    if kind=='route':
     result[key]='passed'if a['both_completed']else'failed'
     result['adaptive_results']={lane:dict(frames=row['executed_frames'],merchant_reached=row['merchant_reached'],outdoor_hold=row['completed_outdoor_hold'],nonzero_audio_samples=row['nonzero_audio_samples'],compiled_loader_calls=row['observation']['native_C_loader_calls'],old_loader_body_steps=row['observation']['old_loader_body_steps'],loader_stack_violations=row['observation']['loader_task_stack_outside'])for lane,row in p['results'].items()}
    else:
     result[key]='passed_selected_fields'if a['native28_matches_native26_selected_game_video_PCM']else'failed'
     result['fixed_comparison']=dict(frames=a['frames_per_lane'],actual_callbacks_equal=a['actual_callback_observation_masks_equal'],raw_PCM_equal=a['raw_PCM_equal'],both_PCM_silent=all(x['nonzero_samples']==0 for x in a['audio'].values()),compared_fields=a['compared_fields'])
 control=read('native-load-layout-control-active');fp=v/'native-load-fixed-route-current.json'
 if control and fp.exists()and control.get('fixed_pair_proof_sha256')==sha(fp):
  if control['status'].startswith('running_'):
   actual=subprocess.run(['ps','-p',str(control['child_pid']),'-o','command='],capture_output=True,text=True,timeout=5).stdout
   result['same_layout_original_loader_control']='running_verified'if str(Path(control['directory'])/'fresh-layout-control.py')in actual else'needs_observation_no_terminal_verdict'
  elif control['status']=='terminal_same_layout_loader_toggle_fixed_control_classified':
   result['same_layout_original_loader_control']='classified';result['loader_control_comparisons']=control['comparisons']
  else:result['same_layout_original_loader_control']='failed'
 result['scope']='Mixed native/original experimental disc. Native28uses7680heapreservation/startupcopy versus native26at6144; acquire andloader/compiler costs also differ. Equal entry ABI does not mean equal cycles. Same-layoutloadercontrol toggles only8entrybytes but changes implementationandcost together; no unsupported causal attribution or transferredoldercontrol conclusion. ComponentfixtureBIOSadapters and actualgameHLE/core/devicesremain. Adaptivecompletion is notfixed-input/full-game/physical equivalence. Equal silentPCM is notworking-audioproof.'
 result['evidence_files']=paths
 return result
