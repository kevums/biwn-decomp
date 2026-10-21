"""Publish new input disc component qualification;fresh play still pending."""
import shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
def main():
 manifest=V/'native-Deck-current-status-v1-current.json';w=read(manifest)
 for p,h in w['dependencies_sha256'].items():assert sha(p)==h,p
 names=['native-Deck-input-clr-disc-build-v1','native-Deck-input-clr-final-v1','native-Deck-input-clr-final-geometry-v1','native-deck-retained-input-clr-final-v1','shared-Deck-fallback-input-clr-final-v1','native-Deck-input-clr-startup-heap-v1','native-Deck-input-clr-capacity-v1','native-Deck-outer-input-clr-final-v1','native-Deck-outer-fallback-input-clr-final-v1','native-Deck-outer-waits-input-clr-final-v1','native-deck-alias-nesting-input-clr-final-v1','native-input-clr-geometry-alias-v1','native-Deck-outer-connected-input-clr-v1','input-clr-final-public-bus-v1','input-clr-final-copied-rebuild-v1']
 proofs={n:read(V/(n+'-current.json'))for n in names}
 for n,g in proofs.items():
  assert g['status'].startswith('terminal_')and'failed'not in g['status'],n
  for p,h in g.get('source_sha256',{}).items():assert sha(p)==h,(n,p)
 b=proofs[names[0]];ret=proofs[names[3]];geo=proofs[names[2]];bus=proofs[names[13]];copy=proofs[names[14]]
 assert sha(b['derived_disc'])==b['derived_disc_sha256'];assert ret['completed']==4992 and ret['fallback_cases']==16 and geo['completed']==256 and bus['completed']==13
 assert ret['payload_sha256']==geo['payload_sha256']==bus['payload_sha256']==copy['sha256']
 assert [proofs[n]['completed']for n in names[10:13]]==[256,128,128]
 out=V/'native-input-clr-final-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 for n,g in proofs.items():
  save(out/(n+'.json'),g)
  if n!=names[0]:subprocess.run(['/bin/cp','-cR',g['directory'],str(out/n)],check=True,capture_output=True)
 facts=dict(status='terminal_input_CLR_new_disc_final_alias_connected_bus_pass_fresh_pending',directory=str(out),candidate_disc=b['derived_disc'],candidate_disc_sha256=b['derived_disc_sha256'],new_disc_built=True,previous_reviewed_disc_unchanged=True,final_address_gates_verified=True,final_input_public_bus_cases=13,input_face_alias_cases=256,coordinate_geometry_alias_cases=128,connected_cases=128,connected_task_slots=101,connected_native_returns=proofs[names[12]]['native_returns'],protected_parent_checks=proofs[names[12]]['protected_suspended_frame_checks'],module_bytes=ret['code_bytes'],module_sha256=ret['payload_sha256'],copied_final_module_rebuild_verified=True,initial_heap_bytes=b['initial_heap_bytes'],total_reservation_bytes=b['component_bytes'],final_layout_C_stack_bytes=ret['maximum_C_stack_bytes'],geometry_C_stack_bytes=164,installed_preview_changed=False,fresh_gameplay_tested=False,live_observers_requalified=False,natural_IRQ_or_arbitrary_reentry_verified=False,native_disc_fidelity_verified=False,whole_game_complete=False,new_training=False,new_model_predictions=0,scope='New separate experimental image with native input primitives/7explicitCLRsites. Exact deployed code/startup/heap/outer,384injectedalias and128connected fixtures pass;13actual public bus traces pass. Copied final module identical at0x16dc00/arena0x178b00. These component proofs do not establish fresh gameplay,live observer contracts,arbitraryIRQ,original GPU/DSP/physical/audio fidelity or whole-game rebuilding.')
 report=ROOT/'reports/Native Input CLR Final Image Review.txt';facts['report']=str(report);save(out/'facts.json',facts)
 report.write_text('BIWN input CLR — new experimental image component qualification\n\n'
  'A separate new CDI now contains the corrected input implementation. Exact38594byte shared module at16DC00,Deckarena178B00. Initial heap130496bytes;total resident reservation267392bytes. The previous reviewed v19disc and Desktop preview are unchanged.\n\n'
  'All8final gates pass:geometry256,retained4992+16fallback,sharedfallback1280,startup6,heap192,capacity36,outer1280,outerfallback384,outerwait/resume192pairs. Alias input/face256andcoordinate/geometry128pass. Combined outer/all5inner caller128cases span101taskslots. These use seeded states and explicitly declared remaining services,not natural IRQ/reentry. Geometry regression executes real original formatter/text and blitter as specified by its separate gate.\n\n'
  'Thirteen actual watched public-bus traces now match original event order at final addresses. This does not erase the preserved v19case0failure;it qualifies the new code. Recorder has no width field,and guest/private stacks are outside watched public ranges. CPU/nonarenaRAM/helper-entry and stack gates remain separate. Copied package rebuilds identical final module.\n\n'
  'Fresh ordinary reset/input gameplay and live geometry/reset/outer observer requalification remain pending. No whole-game,physical-console,arbitraryIRQ,audio,fidelity or trained-quality approval. Earlier8prototype cost samples27..34percent lower apply to the prototype measurement;no new fresh-game timing claim.\n\n'+b['derived_disc']+'\n')
 packet=read(w['packet']);save(out/'before-packet.json',packet);packet['native_input_disc_progress']=facts;s=dict(packet['native_input_optimization_progress']);s.update(new_disc_built=True,installed_in_new_unqualified_experimental_disc=True,new_experimental_disc=b['derived_disc'],new_experimental_disc_sha256=b['derived_disc_sha256'],final_address_gates_verified=True,final_input_public_bus_cases=13,copied_final_module_rebuild_verified=True,final_module_sha256=ret['payload_sha256'],fresh_gameplay_tested=False,live_observers_requalified=False,previous_reviewed_experimental_disc_unchanged=True,prototype_only=False,experimental_only=True)
 s['scope']+=' A separate new disc now passes final-address/alias/connected/bus gates;fresh/live-observer qualification remains pending. Previous reviewed candidate unchanged.'
 s['next_action']='Requalify live reset/geometry/outer observer contracts for final input-CLR image,then run fresh ordinary candidate/original-input control including required reset coverage. Preserve older baseline bus failure and changed-control caveats. Continue full-game source recovery and quality-focused local-model work.'
 packet['native_input_optimization_progress']=packet['latest_source_development']=s;packet['current_copied_Reader_progress']['latest_source_changed_since_last_prediction']=True;save(out/'current-status-packet.json',packet);shutil.copy2(__file__,out/'publisher-source.py')
 deps={str(p):sha(p)for p in out.rglob('*')if p.is_file()};deps[str(report)]=sha(report);deps[b['derived_disc']]=b['derived_disc_sha256'];pub=V/'native-input-clr-final-reviewed-v1-current.json';atomic(pub,dict(status=facts['status'],directory=str(out),facts=str(out/'facts.json'),report=str(report),new_predictions=0,new_training=False,whole_objective_complete=False,dependencies_sha256=deps))
 w.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**w['dependencies_sha256'],**deps,str(pub):sha(pub)});atomic(manifest,w)
 index=ROOT/'config/current-model-work-sources.json';items=read(index);items=[x for x in items if x[0]!=pub.name];items.append([pub.name,'BIWN corrected input new disc final-address/alias/connected/bus gates;fresh pending']);atomic(index,items)
 for p,h in w['dependencies_sha256'].items():
  source=Path(p);assert source.is_relative_to(ROOT);dest=P/'workbench'/source.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True)
  if not dest.is_file()or sha(dest)!=h:subprocess.run(['/bin/cp','-c',str(source),str(dest)],check=True,capture_output=True)
 shutil.copy2(manifest,P/'workbench/verification'/manifest.name);shutil.copy2(index,P/'workbench/config'/index.name);print(facts['status'],flush=True)
if __name__=='__main__':main()
