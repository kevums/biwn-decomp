"""Publish reviewed v16/v17 component results, preserving game/preview boundaries.
No inference, training, disc construction or native Chat verification occurs here.
"""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
PACKAGE=Path('/Users/kevin/Documents/Local AI Lab Restore Tests/20261020T194117.103058Z-biwn-current-moved')
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def atomic(p,x):
 p=Path(p);tmp=p.with_name(p.name+'.publishing');save(tmp,x);os.replace(tmp,p)
def main():
 names=['native-multiply-regions-v1','native-multiply-leaf-v1','native-multiply-leaf-guards-v1','native-multiply-leaf-cost-v1','native-deck-retained-leaf-multiply-v1','native-Deck-leaf-multiply-v1','native-multiply-scalar-leaf-v1','native-multiply-scalar-leaf-guards-v1','native-multiply-scalar-leaf-cost-v1','native-deck-retained-scalar-leaf-multiply-v1','native-Deck-scalar-leaf-multiply-v1']
 receipts={name:read(V/(name+'-current.json'))for name in names}
 for name,d in receipts.items():
  assert d['status'].startswith('terminal_') and 'failed'not in d['status'],(name,d['status'])
  for path,digest in d.get('source_sha256',{}).items():assert sha(path)==digest,(name,path)
 for variant in ['leaf','scalar-leaf']:
  d=receipts['native-multiply-'+variant+'-v1'];assert d['completed']==2192 and d['fallbacks']==320
  assert receipts['native-multiply-'+variant+'-guards-v1']['completed']==1280
  assert receipts['native-deck-retained-'+variant+'-multiply-v1']['completed']==4992
  assert receipts['native-deck-retained-'+variant+'-multiply-v1']['fallback_cases']==16
  assert receipts['native-Deck-'+variant+'-multiply-v1']['completed']==256
  hashes={receipts[key]['payload_sha256']for key in names if key.startswith(('native-multiply-'+variant+'-v1','native-multiply-'+variant+'-guards','native-deck-retained-'+variant+'-multiply','native-Deck-'+variant+'-multiply'))};assert len(hashes)==1
 out=V/'native-multiply-scalar-leaf-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 for name,d in receipts.items():
  target=out/name;subprocess.run(['/bin/cp','-cR',d['directory'],str(target)],check=True,capture_output=True);save(out/(name+'.json'),d)
 for profile in ['deck-shared-v16-leaf-multiply','deck-shared-v17-scalar-leaf-multiply']:
  source=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'/profile
  subprocess.run(['/bin/cp','-cR',str(source),str(out/profile)],check=True,capture_output=True)
 before=read(V/'native-multiply-public-cost-v1-current.json')['cases'];after=receipts['native-multiply-scalar-leaf-cost-v1']['cases'];assert [x['case']['variant']for x in before]==[x['case']['variant']for x in after]
 improvement=[1-b['costs']['native']['cycles']/a['costs']['native']['cycles']for a,b in zip(before,after)]
 g=receipts['native-multiply-scalar-leaf-v1'];retained=receipts['native-deck-retained-scalar-leaf-multiply-v1'];geometry=receipts['native-Deck-scalar-leaf-multiply-v1']
 copy_receipt=PACKAGE/'workbench/verification/native-multiply-scalar-leaf-v1'/Path(g['directory']).name/'copied-native-rebuild.json';copied=read(copy_receipt);assert copied['sha256']==g['payload_sha256'] and sha(copied['copied_payload'])==g['payload_sha256'];save(out/'copied-native-rebuild.json',copied)
 rows=read(Path(retained['directory'])/'cases.json');witnesses=sum(x.get('native_multiply_entries',0)for x in rows)
 facts=dict(status='terminal_scalar_leaf_E540_prototype_qualified_cost_still_unapproved',entry='0xe540',
  authorship='Coordinator-authored scalar/context and original-ABI optimizations; no model-authored source or prediction in this work',
  body_cases=2192,body_case_scope='Body exercised through 2192 public-entry cases, not a separate new standalone-context matrix',public_entry_cases=2192,public_guard_cases=1600,
  public_normal_private_C_stack_bytes=g['maximum_C_stack_bytes'],prototype_module_bytes=g['module_bytes'],retained_caller_cases=4992,retained_fallback_cases=retained['fallback_cases'],geometry_cases=256,geometry_C_stack_peak=geometry['maximum_C_stack_bytes'],internal_math_entry_witnesses=witnesses,
  extra_guest_stack_spills=0,guest_sign_scratch_bytes=2,declared_extra_runtime_reads='One task-pointer read at0xc0920 per publicentry',
  public_cost_ratio_range=[min(x['native_to_original_ratio']for x in after),max(x['native_to_original_ratio']for x in after)],public_cost_original_cycles=[x['costs']['original']['cycles']for x in after],public_cost_native_cycles=[x['costs']['native']['cycles']for x in after],
  cost_reduction_vs_v14_fraction_range=[min(improvement),max(improvement)],cost_approved=False,global_disc_redirect_installed=False,new_disc_built=False,fresh_gameplay_tested=False,physical_console_tested=False,
  copied_module_byte_identical=True,source_directory=str(ROOT/'projects/black-ice-white-noise/restoration/native-m68k/deck-shared-v17-scalar-leaf-multiply'),source_profile='v17-scalar-leaf',
  new_model_predictions=0,new_training=False,native_Chat_display_verified=False,latest_reader_retested_on_this_source=False,
  scope='Successful ordinary nonaliasing RAM at the tested prototype addresses. Full return CPU/public RAM/original two-byte sign scratch/ordered argument-word and scratch/RTS accesses compare with original68000; private arena alone normalized. C ABI preserves physical callee-saved registers; only defined scratch outputs are restored. v16 isolates bridge change;v17 also scalarizes the recovered body and uses supplied target flag primitives. No arbitrary IRQ, task/context alias, final-image nesting, global redirect, fresh gameplay or console proof. Cycle samples are pinned-emulator entry-to-return CPU costs, not physical speed or game fidelity.')
 report=ROOT/'reports/Native Multiply Scalar and ABI Optimization Review.txt';facts['report']=str(report)
 report.write_text('BIWN E540 — scalar and original-ABI prototype optimization\n\n'
 'Coordinator authored this work. No local prediction or training update completed in this turn. A separate local Author task was prepared but returned busy before sending any request.\n\n'
 'v16 removes the full virtual CPU register save/restore from the public entry and relies on the C callee-preservation convention. Original output A0/A1 come from preserved physical D2/D3. v17 additionally uses scalar word reads, removes unobservable intermediate software-register stores and uses target arithmetic flag primitives. The original public two-byte scratch and ordered word accesses remain checked.\n\n'
 'Each version passed 2192 public cases,1600 guarded fallback cases,4992 retained caller cases plus16 caller fallback cases,and256 geometry cases with real formatter/text dependencies. GPU service remains a declared fixture. Geometry stack peak is164/176bytes. v17 also rebuilds byte-identically using the moved copied runtime/toolchain.\n\n'
 'v14 original bridge total cycles: '+str([x['costs']['native']['cycles']for x in before])+'\n'
 'v16 smaller bridge total cycles: '+str([x['costs']['native']['cycles']for x in receipts['native-multiply-leaf-cost-v1']['cases']])+'\n'
 'v17 scalar plus smaller bridge total cycles: '+str(facts['public_cost_native_cycles'])+'\n'
 'Original routine cycles: '+str(facts['public_cost_original_cycles'])+'\n'
 f"v17 reduces sampled total cost by {100*min(improvement):.1f}–{100*max(improvement):.1f}%, but remains {facts['public_cost_ratio_range'][0]:.1f}–{facts['public_cost_ratio_range'][1]:.1f}times the original. Cost remains unapproved.\n\n"
 'No game image or Desktop preview changed. Whole-game source rebuilding remains incomplete. Reader32 predates this optimization; its exact older request/response remains preserved. One-click future Reader requests now receive the updated prototype evidence, but no new response is claimed.\n')
 save(out/'facts.json',facts);shutil.copy2(Path(__file__),out/'publisher-source.py')
 wrapper_path=V/'native-Deck-current-status-v1-current.json';wrapper=read(wrapper_path)
 for path,digest in wrapper['dependencies_sha256'].items():assert sha(path)==digest,path
 packet=read(wrapper['packet']);save(out/'before-current-status-packet.json',packet)
 packet['previous_native_multiply_progress']=packet['native_multiply_progress'];packet['native_multiply_progress']=facts;packet['latest_source_development']=facts
 packet['current_copied_Reader_progress']['latest_source_changed_since_last_prediction']=True;packet['current_copied_Reader_progress']['current_source_reply_verified']=False
 packet_path=out/'current-status-packet.json';save(packet_path,packet)
 deps={str(p):sha(p)for p in out.rglob('*')if p.is_file()};deps[str(report)]=sha(report)
 publication=dict(status=facts['status'],directory=str(out),facts=str(out/'facts.json'),report=str(report),dependencies_sha256=deps,new_predictions=0,new_training=False,disc_changed=False,whole_objective_complete=False)
 pub=V/'native-multiply-scalar-leaf-reviewed-v1-current.json';atomic(pub,publication)
 wrapper.update(packet=str(packet_path),dependencies_sha256={**wrapper['dependencies_sha256'],**deps,str(pub):sha(pub)})
 atomic(wrapper_path,wrapper)
 # Root-owned evidence is copied verbatim. Existing path adapter rebases it
 # in memory without rewriting the frozen receipts.
 for name,digest in wrapper['dependencies_sha256'].items():
  source=Path(name);assert source.is_relative_to(ROOT);dest=PACKAGE/'workbench'/source.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True)
  if not dest.is_file()or sha(dest)!=digest:subprocess.run(['/bin/cp','-c',str(source),str(dest)],check=True,capture_output=True)
 shutil.copy2(wrapper_path,PACKAGE/'workbench/verification'/wrapper_path.name)
 for rel in ['native_deck_source_context_v13.py','scripts/show_native_status_v2.py']:shutil.copy2(ROOT/rel,PACKAGE/'workbench'/rel)
 goal=read(V/'goal-continuation-current.json');save(out/'prior-goal.json',goal)
 goal.update(status='active_native_E540_scalar_ABI_optimized_full_game_and_model_quality_open',recorded_at=datetime.now(timezone.utc).isoformat(),previous_goal_turn_classification='Progress: prior substantive goal work completed copied two-update training capability and scoped local Reader checks. The intervening launcher answer verified existing controls only.',current_turn_classification='Progress: measured v14 cycle attribution, qualified v16 smaller C ABI entry and v17 scalar body, reduced sampled multiply cost34..40%,copied byte-identical40448byte rebuild,updated current/copy context and176record prompt export. Local Author attempt busy before request;zero model predictions/updates this turn.',new_training_this_turn=False,optimizer_updates_this_turn=0,completed_new_local_predictions_this_turn=0,new_coordinator_authored_routines_this_turn=0,new_target_implementation_optimizations_this_turn=2,latest_native_multiply_review=str(pub),latest_native_multiply_report=str(report),saved_prompt_or_transcript_records=176,current_status_reader_live_generation_verified=False,prior_Reader32_generation_verified=True,current_status_reader_scope='Generic Reader32 gets current facts;latest recorded response predates the new v17source and is not claimed verified for it.',full_objective_complete=False,blocked=False,ongoing_finite_workers=[])
 goal['remaining_requirements']['local_frontend']='Native Chat earlier three-role rendering verified with overlength failure. Copied base Reader inference works;Reader32 predates v17 multiply. Copied-weight native Chat/output quality and useful training acceptance remain unverified.'
 goal['remaining_requirements']['game']+=' v17scalar/publicABIprototype passes2192normal/1600guards/4992retained/256geometry,40448bytecopiedrebuild;samplecost34..40%lower thanv14butstill4.1..7.6timesoriginal,unapproved outsidegame.'
 goal['do_not_restart']+=['Completedv14multiply three-case cycle attribution','Completedv16andv17each2192public/1600guards/4992retained/16retainedfallback/256geometry/eightcostsamples','Completedv17copied40448byte exact rebuild','LocalAuthorv15busyattemptcompletedzeropredictions;onlyretryafteractualownerterminal orleaseavailable']
 atomic(V/'goal-continuation-current.json',goal)
 print(json.dumps(dict(status=publication['status'],report=str(report),cost_ratio=facts['public_cost_ratio_range'],cost_reduction_fraction=facts['cost_reduction_vs_v14_fraction_range'],full_goal_complete=False),indent=2))
if __name__=='__main__':main()
