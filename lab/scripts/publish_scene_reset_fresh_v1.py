"""Review existing final-image/reset trials. Does not run a game or a model."""
import hashlib,json,os,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
P=Path('/Users/kevin/Documents/Local AI Lab Restore Tests/20261020T194117.103058Z-biwn-current-moved')
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def atomic(p,x):
 p=Path(p);q=p.with_name(p.name+'.publishing');save(q,x);os.replace(q,p)
def main():
 manifest=V/'native-Deck-current-status-v1-current.json';wrapper=read(manifest)
 for p,h in wrapper['dependencies_sha256'].items():assert sha(p)==h,p
 stems=['native-Deck-scene-reset-disc-build-v1','native-Deck-scene-reset-final-v1','native-Deck-scene-reset-final-geometry-v1','native-deck-retained-scene-reset-final-v1','shared-Deck-fallback-scene-reset-final-v1','native-Deck-scene-reset-startup-heap-v1','native-Deck-scene-reset-capacity-v1','native-Deck-outer-scene-reset-final-v1','native-Deck-outer-fallback-scene-reset-final-v1','native-Deck-outer-waits-scene-reset-final-v1','native-deck-alias-nesting-scene-reset-final-v1','native-scene-reset-geometry-alias-v1','native-Deck-outer-connected-scene-reset-v1','scene-reset-input-observer-qualified-v1','scene-reset-geometry-observer-qualified-v1','outer-scene-reset-geometry-observer-qualified-v1','scene-reset-observer-actual-CPU-v1','shared-Deck-region-check-scene-reset-v1']
 proofs={n:read(V/(n+'-current.json'))for n in stems}
 for n,g in proofs.items():
  assert g['status'].startswith('terminal_')and'failed'not in g['status'],n
  for p,h in g.get('source_sha256',{}).items():assert sha(p)==h,(n,p)
 b=proofs[stems[0]];assert sha(b['derived_disc'])==b['derived_disc_sha256']
 geo=proofs[stems[2]];ret=proofs[stems[3]]
 assert geo['completed']==256 and ret['completed']==4992 and ret['fallback_cases']==16
 assert geo['payload_sha256']==ret['payload_sha256']==sha(geo['payload'])
 assert geo['deployed_module_byte_identity']
 assert [proofs[n]['completed']for n in stems[10:13]]==[256,128,128]
 assert proofs[stems[13]]['actual_input_pairs']==64 and proofs[stems[16]]['CPU_lanes']==64
 out=V/'native-scene-reset-fresh-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 # Freeze receipts plus their small raw check outputs. Large existing disc and
 # live reports are guarded directly; they are not duplicated for this review.
 for n,g in proofs.items():
  save(out/(n+'.json'),g)
  if n!=stems[0]:subprocess.run(['/bin/cp','-cR',g['directory'],str(out/n)],check=True,capture_output=True)
 jobs={k:read(V/f'native-Deck-scene-reset-early-reset-v3-{k}-current.json')for k in ['candidate','control']}
 external={str(Path(b['derived_disc'])):b['derived_disc_sha256']}
 reports={}
 for lane,j in jobs.items():
  assert j['status']=='terminal_fresh_debug_geometry_route_pending_review'
  assert j['snapshot_restores']==j['host_guest_RAM_writes']==j['host_CPU_or_task_seeds']==0
  assert sha(j['report'])==j['report_sha256']
  for p,h in j['source_sha256'].items():assert sha(p)==h,p
  for kind in ['shared','face','geometry','outer','reset']:
   obs=j[kind+'_observation'];assert obs['errors']==obs['pending']==0,(lane,kind)
  assert j['retained_observation']['errors']==0
  save(out/(lane+'-job.json'),j);reports[lane]=read(j['report'])
  external[j['report']]=j['report_sha256'];external.update(j['source_sha256'])
  dest=out/lane;dest.mkdir()
  for p in Path(j['directory']).iterdir():
   if p.is_file()and p.suffix not in ['.cdi','.dylib']:shutil.copy2(p,dest/p.name)
  for p in (Path(j['directory'])/'candidate').glob('*observation.json'):shutil.copy2(p,dest/p.name)
 assert jobs['candidate']['reset_observation']['entries']==jobs['candidate']['reset_observation']['returns']==jobs['candidate']['reset_observation']['markers']==1
 assert jobs['control']['reset_observation']['entries']==0 and jobs['control']['reset_observation']['original_global_entries']==2
 a,c=[reports[k]['frames']for k in jobs]
 keys=['video_sha256','raw_player_X','raw_player_Z','scene_word','player_mode_word','tile_word','floor_word','locomotion_state','held_buttons']
 comparisons={key:dict(differing_frames=[x['frame']for x,y in zip(a,c)if x.get(key)!=y.get(key)],candidate_final=a[-1].get(key),control_final=c[-1].get(key))for key in keys}
 comparison=dict(candidate_frames=len(a),control_frames=len(c),paired_frames=min(len(a),len(c)),fields=comparisons,final_video_equal=a[-1]['video_sha256']==c[-1]['video_sha256'],audio={k:d['audio']for k,d in reports.items()},control_scope=jobs['candidate']['observer_geometry_completion_scope'],original_geometry_control=False,isolated_reset_timing_test=False)
 assert len(comparisons['video_sha256']['differing_frames'])==14 and comparison['final_video_equal']
 assert all(not comparisons[k]['differing_frames']for k in keys[1:-1])
 save(out/'fresh-comparison.json',comparison)
 trials=[]
 for version,prefix in [(1,'native-Deck-scene-reset-geometry-v1'),(2,'native-Deck-scene-reset-reset-v2')]:
  for lane in jobs:
   j=read(V/(prefix+'-'+lane+'-current.json'));assert j['status'].startswith('terminal_')
   save(out/f'coverage-trial-v{version}-{lane}.json',j)
   trials.append(dict(version=version,lane=lane,status=j['status'],reset=j.get('reset_observation'),scope='Candidate missed required reset coverage;all other observed guards clear. Preserved as unsuccessful coverage trial,not a passing reset test.'))
 save(out/'unsuccessful-coverage-trials.json',trials)
 packet=read(wrapper['packet']);save(out/'before-current-packet.json',packet)
 source=dict(packet['native_scene_reset_progress']);source.update(status='terminal_hybrid_reset_final_image_and_fresh_path_observed_fidelity_open',new_disc_built=True,experimental_disc_internal_reset_installed=True,global_disc_redirect_installed=False,fresh_gameplay_tested=True,required_reset_path_observed=True,fresh_native_reset_entries=1,fresh_native_reset_returns=1,final_address_gates_verified=True,nested_component_checks_verified=True,natural_IRQ_or_arbitrary_reentry_verified=False,cost_measured=False,cost_approved=False,scope='Hybrid corrected Repair in input dispatch of separate experimental disc;global1102A remains original. Final-address component,alias,connected and read-only observer tests pass. Fresh ordinary star input witnesses one native reset commit/return;control runs original input/reset. Not an isolated reset cost or original-geometry fidelity test. Raw later flag-helper Authors remain separate standalone proofs. Whole-game,arbitraryIRQ,physical console and broad fidelity unproven.')
 candidate=dict(packet['latest_native_candidate']);save(out/'previous-candidate.json',candidate)
 candidate.update(status='terminal_scene_reset_fresh_path_observed_fidelity_open',variant='six geometry helpers plus internal scene-reset experimental disc v1',directory=str(out),candidate_disc=b['derived_disc'],candidate_disc_sha256=b['derived_disc_sha256'],native_internal_helpers=['0x'+x for x in b['geometry_internal_helper_entries']],native_input_internal_helpers=['0x1102a'],total_internal_compiled_helpers=7,native_module=geo['payload'],native_module_sha256=geo['payload_sha256'],native_module_bytes=b['shared_Deck_code_bytes'],native_code_bytes=b['linked_component_bytes'],total_reservation_bytes=b['component_bytes'],candidate_initial_heap_bytes=b['initial_heap_bytes'],candidate_frames=len(a),control_frames=len(c),differing_video_frames=14,final_video_equal=comparison['final_video_equal'],control_scope=comparison['control_scope'],original_geometry_control=False,isolated_reset_timing_test=False,new_fresh_gameplay_verified=True,fresh_route_completed=True,final_address_gates_verified=True,new_nesting_verified=True,native_disc_qualified=False,native_disc_fidelity_verified=False,installed_preview_changed=False,whole_game_complete=False,fresh_native_reset_entries=1,fresh_native_reset_returns=1,fresh_reset_observer_errors=0,input_face_alias_cases=256,coordinate_geometry_alias_cases=128,connected_six_caller_cases=128,connected_task_slots=101,protected_component_parent_checks=proofs[stems[12]]['protected_suspended_frame_checks'],authorship=source['authorship'],scope=source['scope']+' Both lanes keep six compiled geometry helpers;only the original input entry is restored in control. Fourteen video differences in24967pairedframes and3held-button differences are unresolved;candidate/control recorded position and selected scene fields agree throughout. Audio output is silent in both lanes. Earlier58differences used a different original-geometry control,so this is not evidence that those were fixed.',next_action='Resolve input timing/video and silent-audio fidelity;continue remaining original CPU/GPU/DSP source recovery and same-console whole-game building. Preserve explicit reset authorship;qualify unedited flag-helper source before using it in an image. Native Chat with copied weights and useful trained-model quality remain unproven.')
 report=ROOT/'reports/Native Scene Reset Final Image and Fresh Route Review.txt';candidate['report']=source['report']=str(report)
 report.write_text('BIWN reset — final experimental image and fresh path\n\n'
  'The hybrid reset from the prior review is now installed inside input dispatch of a separate experimental CDI. It keeps one explicit coordinator SR-mask correction to the earlier local Repair;the global original1102Aentry remains unchanged. Later unedited local flag-helper outputs are separate standalone768case results and have not replaced this image body.\n\n'
  'Exact deployed40402byte shared module:geometry256,retained4992+16fallbacks,sharedfallback1280,startup6,heap192,capacity36,outer1280,outerfallback384,wait/resume192pairs pass. New alias256input/face+128coordinate/geometry and128connected cases cover101taskslots. These seeded matrices do not prove arbitraryIRQ/reentry. Reset observer:64actual original/native input pairs+16faultcontrols;geometry8legal/89fault,outer2legal/18fault,region88negative and64actual combinedCPUlanes pass.\n\n'
  'Fresh HLE CD boot:24967candidate/24968control frames. Candidate observes1native reset entry/marker/return with zero observer errors/pending;control has0native and2original global entries. Candidate has1original global entry elsewhere. Geometry stays compiled in both;control restores only10original input-entry bytes. This includes the whole input caller,not isolated reset timing. Fourteen paired video frames differ;finalvideo matches. Selected recorded player position/scene/mode/tile/floor/locomotion fields agree throughout;held buttons differ on3frames. Neither lane emits nonzero audio samples. No checkpoint restore or host guest-state seeds/writes.\n\n'
  'Earlier v1/v2candidate coverage attempts missed the reset path and remain unsuccessful. Offline sampled inputCPU timing showed the late star pulses missed input processing;v3moved ordinary star input tooffset55..82 and obtained coverage. The older58video differences used original geometry as control and are not demonstrated fixed by this changed comparison.\n\n'
  'Experimental only. Desktop checkpoint preview unchanged;whole-game rebuilding,physical console,fidelity and broad trained-model quality remain incomplete.\n\nDetailed comparison: '+str(out/'fresh-comparison.json')+'\n')
 packet['previous_native_candidate_before_scene_reset']=packet['latest_native_candidate'];packet['latest_native_candidate']=candidate;packet['latest_fresh_reviewed_candidate']=candidate;packet['native_scene_reset_progress']=source;packet['latest_source_development']=source
 packet['current_frame_difference_analysis']=dict(status='terminal_offline_reset_route_comparison',comparison=str(out/'fresh-comparison.json'),differing_video_frames=14,held_button_differing_frames=3,original_geometry_control=False,scope=comparison['control_scope'])
 packet['current_copied_Reader_progress'].update(latest_source_changed_since_last_prediction=True,current_source_reply_verified=False)
 save(out/'facts.json',dict(candidate=candidate,source=source,comparison=comparison));save(out/'current-status-packet.json',packet);shutil.copy2(__file__,out/'publisher-source.py')
 deps={str(p):sha(p)for p in out.rglob('*')if p.is_file()};deps.update(external);deps[str(report)]=sha(report)
 pub=V/'native-scene-reset-fresh-reviewed-v1-current.json';atomic(pub,dict(status=candidate['status'],directory=str(out),report=str(report),facts=str(out/'facts.json'),new_game_execution=False,new_predictions=0,new_training=False,whole_objective_complete=False,dependencies_sha256=deps))
 wrapper.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**wrapper['dependencies_sha256'],**deps,str(pub):sha(pub)});atomic(manifest,wrapper)
 index=ROOT/'config/current-model-work-sources.json';items=read(index);items=[x for x in items if x[0]!=pub.name];items.append([pub.name,'BIWN reset final experimental image and fresh required-path execution;fidelity open']);atomic(index,items)
 for p,h in wrapper['dependencies_sha256'].items():
  src=Path(p);assert src.is_relative_to(ROOT);dest=P/'workbench'/src.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True)
  if not dest.is_file()or sha(dest)!=h:subprocess.run(['/bin/cp','-c',str(src),str(dest)],check=True,capture_output=True)
 shutil.copy2(manifest,P/'workbench/verification'/manifest.name);shutil.copy2(index,P/'workbench/config'/index.name)
 print(json.dumps(dict(status=candidate['status'],report=str(report),video_differences=14,native_reset_returns=1),indent=2))
if __name__=='__main__':main()
