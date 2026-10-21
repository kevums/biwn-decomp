"""Publish completed exact-image gates; fresh v29 gameplay remains untested."""
import shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic

def main():
 driver=read(V/'native-Deck-scene17-direct-dispatch-final-v1-current.json');assert driver['status']=='terminal_deeper_candidate_final_component_startup_heap_gates_pass'
 assert len(driver['results'])==8 and all(x['exit_code']==0 for x in driver['results'].values())
 names=['scene17-direct-dispatch-final-bridge-v1','scene-direct-dispatch-final-native-v1','scene17-direct-dispatch-final-fallback-v1','scene17-direct-dispatch-final-reentry-v1','scene17-direct-dispatch-final-public-bus-v1','scene17-direct-dispatch-final-input-face-alias-v1']
 gates={n:read(V/(n+'-current.json'))for n in names}
 assert [g['completed']for g in gates.values()]==[772,1153,384,64,14,256]
 for g in [driver,*gates.values()]:
  assert g['status'].startswith('terminal_')and'failed'not in g['status']
  for p,h in g['source_sha256'].items():assert sha(p)==h,p
 scene,body=[gates[n]for n in names[:2]];assert scene['maximum_C_stack_bytes']==168 and scene['deployed_module_byte_identity']and body['deployed_module_byte_identity']and body['payload_sha256']==scene['payload_sha256']
 b=read(V/'native-scene17-direct-dispatch-disc-build-v1-current.json');assert b['shared_Deck_code_bytes']==48410 and sha(b['derived_disc'])==b['derived_disc_sha256']
 wp=V/'native-Deck-current-status-v1-current.json';w=read(wp)
 for p,h in w['dependencies_sha256'].items():assert sha(p)==h,p
 out=V/'direct-dispatch-final-image-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 packet=read(w['packet']);save(out/'before-wrapper.json',w);save(out/'before-packet.json',packet);save(out/'final-driver.json',driver)
 for n,g in gates.items():save(out/(n+'.json'),g)
 report=ROOT/'reports/BIWN Direct Dispatch Final Image Review.txt'
 next_action='Complete v29 final coordinate/geometry aliases and outer connected/suspension checks, qualify read-only scene/display/shared observers, then run fresh candidate/control and fixed-input gameplay. V27 remains the latest gameplay-tested disc. Continue resource/timing work, remaining original CPU/GPU/DSP/HLE source recovery, useful held-out training evaluation and copied-weight Native Chat usability.'
 head=dict(packet['native_scene_dispatch_headroom_progress']);head.update(status='terminal_direct_scene_dispatch_final_component_gates_pass_fresh_pending',disc_integration_component_verification_complete=True,exact_deployed_scene_cases=772,exact_deployed_body_cases=1153,exact_deployed_module_sha256=scene['payload_sha256'],final_deployed_module=scene['payload'],final_scene_fallback_cases=384,final_scene_nesting_cases=64,final_scene_public_bus_cases=14,final_scene_input_face_alias_cases=256,final_existing_gates=8,final_gates={n:dict(status=g['status'],completed=g.get('completed'),pointer=str(V/(n+'-current.json')))for n,g in {'native-Deck-scene17-direct-dispatch-final-v1':driver,**gates}.items()},fresh_gameplay_verified=False,live_game_heap_savings_verified=False,final_cross_root_alias_and_outer_connected_verified=False,new_read_only_observers_qualified=False,delivery_report=str(report),next_action=next_action)
 packet['native_scene_dispatch_headroom_progress']=packet['latest_source_development']=head;packet['native_scene_draw_progress']['headroom_prototype']=head;packet['native_scene_draw_progress']['next_action']=packet['native_display_list_progress']['next_action']=next_action
 packet['pending_native_candidate'].update(final_gates=head['final_gates'],final_existing_component_gates_pass=True,exact_deployed_scene_cases=772,exact_deployed_body_cases=1153,exact_deployed_module_sha256=scene['payload_sha256'],scene_C_stack_bytes=168,scene_C_stack_margin=40,report=str(report),next_action=next_action)
 report.write_text('BIWN v29 — exact experimental image gates complete\n\nThe separate direct-dispatch CDI passes all8relocated component/startup/heap gates:geometry256,retained4992,fallback1280,startup6/heap192,capacity36,outer1280,fallback384andwait192pairs. The deployed48410byte module is checked against the exact resident bytes. Its actual68000scene772anddisplay1153cases pass CPU/RAM and scoped bus/commit checks;scene stack168/208leaves40bytes. Final-scene fallback384,nesting64,publicbus14andscene/input/face aliases256pass. These are deterministic component fixtures,not fresh gameplay or arbitraryIRQproof.\n\nLinked native code89240bytes,totalreservation277248,bootcopy115648,initialheap120640. Compared withv27,the sharedmodule is84bytes smaller andinitialheap64bytes larger. No v29liveheap sample or speed measurement yet. Global original helpers/remainingrendering,GPU/DSP/HLE/device dependencies remain.\n\nV27remains the latest gameplay-tested image:24990/24963freshframes,5243native display/rotation/clearreturns,8375intermediatevideo differences,finalvideoagreement;sampledouter-activeheap816andscene stack208/208. The installed checkpoint preview is unchanged.\n\nNo additional model inference ortraining during these final gates. Earlier queuedReader36completed11.58seconds;156wordsfailed150requested,withscopedv27factsreviewed andpriorfailedqualitypilotomitted. Exactprompts/rawresponsesremainavailable. Copied-weightNativeChatandusefultrainingqualityremainunverified.\n\n'+next_action+'\n\nDisc: '+b['derived_disc']+'\n')
 save(out/'facts.json',head);save(out/'current-status-packet.json',packet);shutil.copy2(__file__,out/'publisher-source.py');shutil.copy2(report,out/report.name)
 deps={str(p):sha(p)for p in out.rglob('*')if p.is_file()};deps[str(report)]=sha(report)
 for g in [driver,*gates.values()]:deps.update(g['source_sha256'])
 pub=V/'direct-dispatch-final-image-reviewed-v1-current.json';atomic(pub,dict(status=head['status'],directory=str(out),facts=str(out/'facts.json'),report=str(report),new_predictions=0,new_training=False,dependencies_sha256=deps))
 w.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**w['dependencies_sha256'],**deps,str(pub):sha(pub)});atomic(wp,w)
 goalp=V/'goal-continuation-current.json';goal=read(goalp);save(out/'goal-before-final-reconciliation.json',goal)
 # This diagnostic goal snapshot is intentionally outside the status proof: it
 # can advance while the immutable exact-image evidence remains unchanged.
 goal.update(recorded_at=datetime.now(timezone.utc).isoformat(),status='active_v29_final_component_gates_pass_fresh_pending',ongoing_finite_workers=[],candidate_final_gate_pointer=str(V/'native-Deck-scene17-direct-dispatch-final-v1-current.json'),candidate_scene_final_gate_pointer=str(V/'scene17-direct-dispatch-final-bridge-v1-current.json'),candidate_new_nesting_verified=False,final_scene_alias_nesting_verified=True,final_cross_root_alias_and_outer_connected_verified=False,latest_component_source_review=str(pub),latest_source_recovery_review=str(pub),latest_source_recovery_report=str(report),latest_delivery_review=str(pub),new_internal_native_helper_integrations_this_turn=0,new_disc_internal_native_helper_integrations_this_turn=0,new_shared_native_component_helper_integrations_this_turn=0,new_hybrid_complete_functions_this_turn=0,new_model_source_scope='One previously queued copied Reader prediction recovered/reviewed;no new coding predictions,model-authored game code oroptimizerupdates. Target-only directdispatch is coordinator-authored.',latest_frame_difference_analysis=str(V/'scene17-display-list-fixed-prefix-review-v1-current.json'),next_game_source_target=next_action,source_recovery_review=str(pub),full_objective_complete=False,blocked=False)
 goal['next_actions'][0]=next_action;atomic(goalp,goal)
 for p,h in w['dependencies_sha256'].items():
  src=Path(p);assert src.is_relative_to(ROOT);target=P/'workbench'/src.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True)
  if not target.is_file()or sha(target)!=h:subprocess.run(['/bin/cp','-c',str(src),str(target)],check=True,capture_output=True)
 shutil.copy2(wp,P/'workbench/verification'/wp.name);shutil.copy2(goalp,P/'workbench/verification'/goalp.name)
 for root in [ROOT,P/'workbench']:
  (root/'CURRENT DECOMPILATION.txt').write_text('CURRENT — v29 exact-image component gates pass; fresh gameplay pending\n\n'+report.read_text()+'\nEarlier integration/Reader review: '+str(ROOT/'reports/BIWN Display List Integration Progress.txt')+'\n')
  notes=root/'WATCH LOCAL AGENTS.txt';text=notes.read_text();notes.write_text('LATEST: v29exact-image component gates now pass. Final cross-root/outer/observer qualification andfreshgameplay remainpending. Zero new modelgenerations ortraining for these gates.\nReport: '+str(report)+'\n\n'+text)
 print(head['status'],report,flush=True)
if __name__=='__main__':main()
