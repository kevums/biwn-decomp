"""Review completed v29 component gates; keep v27 as the latest tested disc."""
import shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic

def clone(src,dest):
 dest.parent.mkdir(parents=True,exist_ok=True)
 subprocess.run(['/bin/cp','-c',str(src),str(dest)],check=True,capture_output=True)

def main():
 names={'scene-display-list-native-v6':1153,'scene17-display-list-bridge-v6':772,'native-deck-retained-scene17-direct-dispatch-v1':4992,'native-geometry-scene17-direct-dispatch-v1':256,'scene17-direct-dispatch-fallback-v1':384,'scene17-direct-dispatch-reentry-v1':64,'scene17-direct-dispatch-public-bus-v1':14,'scene17-direct-dispatch-input-face-alias-v1':256}
 gates={n:read(V/(n+'-current.json'))for n in names}
 for n,g in gates.items():
  assert g['status'].startswith('terminal_')and'failed'not in g['status']and g['completed']==names[n],(n,g['status'],g.get('completed'))
  for p,h in g['source_sha256'].items():assert sha(p)==h,(n,p)
 copied=read(V/'scene17-direct-dispatch-copied-rebuild-v1-current.json');assert copied['bytes']==48410 and not copied['final_disc_integrated']
 for key in ['source_sha256','copied_source_sha256']:
  for p,h in copied[key].items():assert sha(p)==h,p
 scene=gates['scene17-display-list-bridge-v6'];body=gates['scene-display-list-native-v6'];ret=gates['native-deck-retained-scene17-direct-dispatch-v1'];geometry=gates['native-geometry-scene17-direct-dispatch-v1']
 assert scene['payload_bytes']==body['payload_bytes']==48410 and scene['maximum_C_stack_bytes']==168
 assert scene['payload_sha256']==body['payload_sha256']==ret['payload_sha256']==geometry['payload_sha256']==copied['sha256']
 assert ret['fallback_cases']==16 and geometry['maximum_C_stack_bytes']==164
 assert scene['native_display_calls']==scene['native_clear_calls']==scene['native_rotation_calls']==680
 baseline=read(V/'scene17-display-list-bridge-v4-current.json');assert baseline['payload_bytes']==48494 and baseline['maximum_C_stack_bytes']==208
 rejected={n:read(V/(n+'-current.json'))for n in ['scene-display-list-algorithm-host-v3','scene-display-list-native-v5','scene17-display-list-bridge-v5']}
 assert rejected['scene-display-list-algorithm-host-v3']['completed']==1217 and rejected['scene-display-list-native-v5']['completed']==1153 and rejected['scene17-display-list-bridge-v5']['completed']==772
 assert rejected['scene17-display-list-bridge-v5']['maximum_C_stack_bytes']==208 and rejected['scene17-display-list-bridge-v5']['payload_bytes']==48514
 out=V/'scene-direct-dispatch-headroom-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 wp=V/'native-Deck-current-status-v1-current.json';w=read(wp)
 for p,h in w['dependencies_sha256'].items():assert sha(p)==h,p
 packet=read(w['packet']);save(out/'before-wrapper.json',w);save(out/'before-packet.json',packet)
 for n,g in {**gates,**rejected,'scene17-direct-dispatch-copied-rebuild-v1':copied}.items():save(out/(n+'.json'),g)
 report=ROOT/'reports/BIWN Native Scene Stack Headroom.txt'
 next_action='Integrate the exact48410byte direct-dispatch prototype into a separate image, qualify final addresses/resources/alias/observer boundaries, then run fresh candidate/control and fixed-input gameplay. Preserve v27 and the installed checkpoint preview. Continue heap/code-size work, remaining CPU/GPU/DSP/HLE source recovery, useful training and copied-weight Native Chat usability.'
 facts=dict(status='terminal_direct_scene_dispatch_component_headroom_verified_unpromoted',profile='deck-shared-v29-scene-direct-dispatch-v1',directory=str(out),report=str(report),authorship='Coordinator target-only service specialization;canonical scene/clear/rotation/display algorithms unchanged. No new model-authored code.',new_unique_original_functions=0,new_model_predictions=0,new_optimizer_updates=0,module_bytes=48410,previous_module_bytes=48494,module_bytes_saved=84,payload=scene['payload'],payload_sha256=scene['payload_sha256'],scene_cases=772,scene_helper_calls_each=680,native_display_body_cases=1153,retained_caller_cases=4992,retained_fallback_cases=16,geometry_cases=256,geometry_C_stack_bytes=164,scene_C_stack_bytes=168,scene_C_stack_reserved=208,scene_C_stack_margin=40,previous_scene_C_stack_bytes=208,forced_fallback_cases=384,nested_scene_cases=64,scene_public_bus_cases=14,input_face_alias_cases=256,copied_module_byte_identical=True,new_disc_built=False,disc_integrated=False,fresh_gameplay_verified=False,heap_headroom_improvement_measured=False,run_speed_measured=False,native_Chat_verified=False,new_training=False,installed_preview_changed=False,whole_game_complete=False,rejected_pointer_liveness_variant=dict(profile='deck-shared-v28-display-headroom-v1',host_cases=1217,host_guards=17,native_body_cases=1153,scene_cases=772,module_bytes=48514,scene_C_stack_bytes=208,reason='Semantically passing,20bytes larger and no stack saving;not selected.'),scope='Fixed internal scene provider dispatch specialized to direct C calls forE03A/17F14/185B2;logical JSR guest stack and final SP/return checks retained. Other services remain original captures. Component normal-call CPU/RAM/ordered-bus equivalence and explicit nesting fixtures are not arbitraryIRQ/console/timing proof. The live disc remains v27 with8375feedbackvideo differences,816sampledouter-activeheap and208/208scene stack.',next_action=next_action)
 save(out/'facts.json',facts)
 report.write_text('BIWN native scene — measured C-stack headroom\n\nThe separate v29prototype replaces redundant private service dispatch with direct calls to three already compiled internal helpers. Canonical readable scene,clear,rotation anddisplay algorithms are unchanged. Logical guest JSR/return and bank checks remain;other services stay captured. This is coordinator work,zero new recovered original functions and no model training.\n\nConnected772cases,680calls to each internal helper: maximum observed scene C stack falls208to168bytes,leaving40of208bytes. Shared module falls48494to48410bytes,84bytes smaller. Direct display1153,retained callers4992+16fallbacks,geometry256,forced fallback384,nested scene64,public bus14 andscene/input/face aliases256pass. Copied sources/SDK rebuild identical48410bytes. These finite tests do not establish arbitraryIRQ,physical console or game speed.\n\nThe earlier v28descriptor-pointer experiment passes host1217+17guards,native1153 andscene772but remains208stack and grows20bytes. It is retained as unsuccessful optimization evidence,not selected.\n\nNo v29disc orfresh game test yet. V27remains the latest experimental disc:24990/24963freshframes,5243native display/rotation/clearreturns,8375intermediate video differences,finalvideoagreement;sampledouter-activeheap816andscene stack208/208. Prototype savings do not prove new heap availability. The Desktop checkpoint preview is unchanged.\n\n'+next_action+'\n')
 packet['native_scene_dispatch_headroom_progress']=facts;packet['latest_source_development']=facts
 packet['native_scene_draw_progress']['headroom_prototype']=facts;packet['native_scene_draw_progress']['next_action']=next_action
 packet['native_display_list_progress']['next_action']=next_action
 packet['current_copied_Reader_progress'].update(latest_source_changed_since_last_prediction=True,latest_disc_reply_facts_reviewed=True,current_source_reply_verified=False)
 save(out/'current-status-packet.json',packet);shutil.copy2(__file__,out/'publisher-source.py')
 deps={str(p):sha(p)for p in out.rglob('*')if p.is_file()};deps[str(report)]=sha(report)
 for g in [*gates.values(),*rejected.values()]:deps.update(g['source_sha256'])
 # Copied-source paths are checked above, not put in the Root-only status wrapper.
 deps.update(copied['source_sha256'])
 pub=V/'scene-direct-dispatch-headroom-reviewed-v1-current.json';atomic(pub,dict(status=facts['status'],directory=str(out),facts=str(out/'facts.json'),report=str(report),new_predictions=0,new_training=False,dependencies_sha256=deps))
 w.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**w['dependencies_sha256'],**deps,str(pub):sha(pub)});atomic(wp,w)
 for p,h in w['dependencies_sha256'].items():
  src=Path(p);assert src.is_relative_to(ROOT),p;target=P/'workbench'/src.relative_to(ROOT)
  if not target.is_file()or sha(target)!=h:clone(src,target)
 clone(wp,P/'workbench/verification'/wp.name)
 print(facts['status'],str(report),flush=True)
if __name__=='__main__':main()
