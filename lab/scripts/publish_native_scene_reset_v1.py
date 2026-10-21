"""Publish complete reset recovery and actual rejected local generation evidence.
Component-only result;no disc/preview/weight promotion.
"""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification';P=Path('/Users/kevin/Documents/Local AI Lab Restore Tests/20261020T194117.103058Z-biwn-current-moved')
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def atomic(p,x):
 p=Path(p);q=p.with_name(p.name+'.publishing');save(q,x);os.replace(q,p)
def main():
 names=['native-scene-reset-context-v1','native-scene-reset-hybrid-v1','native-scene-reset-core-bus-v1','native-deck-retained-scene-reset-v1','native-geometry-scene-reset-v1'];proofs={n:read(V/(n+'-current.json'))for n in names}
 for n,g in proofs.items():
  assert g['status'].startswith('terminal_')and'failed'not in g['status'],n
  for path,digest in g.get('source_sha256',{}).items():assert sha(path)==digest,(n,path)
 assert proofs[names[0]]['completed']==proofs[names[1]]['completed']==768;assert proofs[names[2]]['completed']==4;ret=proofs[names[3]];geo=proofs[names[4]];assert ret['completed']==4992 and ret['fallback_cases']==16 and geo['completed']==256 and ret['payload_sha256']==geo['payload_sha256']
 local=read(V/'local-scene-reset-v1-current.json');assert local['status']=='terminal_local_reset_two_attempts_rejected'and local['new_predictions']==2 and not any(x['verified']for x in local['rounds'])
 out=V/'native-scene-reset-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 for n,g in proofs.items():subprocess.run(['/bin/cp','-cR',g['directory'],str(out/n)],check=True,capture_output=True);save(out/(n+'.json'),g)
 subprocess.run(['/bin/cp','-cR',local['directory'],str(out/'local-model')],check=True,capture_output=True);shutil.copy2(Path(local['directory'])/'prompts-and-responses.txt',out/'prompts-and-responses.txt')
 src=ROOT/'projects/black-ice-white-noise/restoration/native-m68k/deck-shared-v19-local-scene-reset';subprocess.run(['/bin/cp','-cR',str(src),str(out/src.name)],check=True,capture_output=True);change=read(src/'hybrid-source-changes.json');assert sha(change['raw_local_source'])==change['raw_sha256'] and sha(change['hybrid_source'])==change['hybrid_sha256']
 copy=read(Path(ret['directory'])/'copied-rebuild/receipt.json');assert copy['sha256']==geo['payload_sha256'] and sha(copy['payload'])==copy['sha256'];save(out/'copied-rebuild.json',copy)
 witnesses=sum(x['native_reset_entries']for x in read(Path(ret['directory'])/'cases.json'));assert witnesses>0
 facts=dict(status='terminal_hybrid_scene_reset_complete_component_recovery',entry='0x1102a',source_profile='v19-local-scene-reset',source_directory=str(src),authorship=change['authorship'],raw_Author_accepted=False,raw_Repair_accepted=False,unchanged_local_output_adopted=False,coordinator_semantic_corrections=1,
  body_cases=768,original_instruction_locations=27,all_original_instruction_locations_checked=True,ordered_bus_cases=768,actual_core_bus_cases=4,actual_core_bus_events_each=49,hardware_CLR_reads_each=19,
  public_entry_cases=0,public_guard_cases=0,new_public_entry=False,retained_caller_cases=4992,retained_fallback_cases=16,input_caller_cases=2048,native_reset_entry_witnesses=witnesses,geometry_regression_cases=256,
  module_bytes=geo['code_bytes'],input_C_stack_peak=ret['maximum_C_stack_bytes']['input'],geometry_C_stack_peak=geo['maximum_C_stack_bytes'],new_arena_bytes=0,original_stack_layout_changed=False,copied_module_byte_identical=True,
  cost_approved=False,cost_measured=False,component_internal_dispatch_integrated=True,global_disc_redirect_installed=False,new_disc_built=False,fresh_gameplay_tested=False,installed_preview_changed=False,native_Chat_display_verified=False,
  actual_new_model_predictions=2,new_training=False,trained_adapter_used=False,
  scope='Complete original1102A..110D2 body in C with supplied target CLR memory primitive. Coordinator body and corrected local Repair each pass768standalonecases;rawAuthorfailsSRvalue andrawRepairfailsXpreservation. Hybrid executes inside native input dispatch;real original reset executes in its reference. FullCPU/publicRAM/calleeentries and original stack compare;other poll/record/texture and GPU services remain declared fixtures in relevant matrices. No new public reset ABI,final-image alias/observer/IRQ/naturalgameplay/console proof. RawUnicorn traces and symmetrical hardwareCLR expansions checked separately;four actual pinnedCPUbus traces independently agree. This profile branches from the last clear-cast game source and does not include unapprovedE540multiplyprototype.',report=str(ROOT/'reports/Native Scene Reset and Local Author Review.txt'))
 save(out/'facts.json',facts)
 Path(facts['report']).write_text('BIWN scene reset1102A — complete body and native component recovery\n\n'
 'The raw local Author and its one feedback Repair were rejected. Author used SR0x4000 instead of Z4;Repair fixed Z but itsFF00mask erased X. One explicit coordinator expression correction changesFF00toFFF0. All other model C body statements are retained;the target CLR primitive,ABI,compiler and checker are supplied by the coordinator. No new training,base-weight change or nativeChat rendering is claimed.\n\n'
 'Both coordinator reference and hybrid pass768cases across all32CCR,both stack banks,ordinary/random descriptors and overlapping globals/guest-return/high-address aliases. All27original instruction locations are exercised. FullCPU/public2MBRAM/CABI and ordered widths compare. Unicorn omits physical68000CLRdummyreads;raw traces compare,andbothlanes are symmetrically expanded from decodedCLRinstructions. Four actual pinned68000bus traces independently match49kind/address/valueevents each,including19CLRreads. The first explicit-read-plus-store prototype and raw model failures are retained.\n'
 'Hardware reference: Motorola M68000PRM,section4-74,https://www.nxp.com/docs/en/reference-manual/M68000PRM.pdf . Pinned cpuemu.c CLR.W/L implementations also perform the operand read before the write.\n\n'
 f"Native component:{ret['completed']} retained caller cases plus16fallbacks and256geometrycases pass. Of these,2048exercise the complete input caller with real original reset on the reference side;{witnesses}native reset logical entries were witnessed. Input Cstack peak{facts['input_C_stack_peak']}bytes;geometry{facts['geometry_C_stack_peak']}/176bytes. The copied package rebuilds the same{copy['bytes']}byte module.\n\n"
 'This source is integrated only in the component input path. Global1102A and all game images/Desktop preview remain unchanged. Final addresses,nesting/observer/IRQ and fresh input-reset gameplay remain required before disc adoption. Whole-game source rebuilding and useful training quality remain unfinished.\n\n'
 'Actual local roles/prompts/responses: '+str(out/'prompts-and-responses.txt')+'\n')
 # Preserve a reviewed development example for a future broader curriculum.
 # It is train-only development data, never an untouched validation/test case.
 task=read(Path(local['directory'])/'frozen-task.json');target=Path(change['hybrid_source']).read_text().split('static void native_scene_reset_context',1)[1];target='static void native_scene_reset_context'+target
 record=dict(messages=[dict(role='system',content=task['system']),dict(role='user',content=task['user']),dict(role='assistant',content='```c\n'+target.strip()+'\n```')]);save(out/'reviewed-development-example.json',dict(record=record,split='train_development_only',family='scene_reset_1102A',semantic_validation=str(out/'facts.json'),not_training_ready_by_itself=True,actual_training_updates=0,holdout=False,authorship=change['authorship']))
 packet_manifest=V/'native-Deck-current-status-v1-current.json';wrapper=read(packet_manifest)
 for path,digest in wrapper['dependencies_sha256'].items():assert sha(path)==digest,path
 packet=read(wrapper['packet']);save(out/'before-current-packet.json',packet);packet['native_scene_reset_progress']=facts;packet['latest_source_development']=facts;packet['current_copied_Reader_progress'].update(latest_source_changed_since_last_prediction=True,current_source_reply_verified=False);newpacket=out/'current-status-packet.json';save(newpacket,packet);shutil.copy2(Path(__file__),out/'publisher-source.py')
 deps={str(x):sha(x)for x in out.rglob('*')if x.is_file()};deps[facts['report']]=sha(facts['report']);pub=V/'native-scene-reset-reviewed-v1-current.json';atomic(pub,dict(status=facts['status'],directory=str(out),facts=str(out/'facts.json'),report=facts['report'],transcript=str(out/'prompts-and-responses.txt'),new_predictions=2,new_training=False,dependencies_sha256=deps,whole_objective_complete=False))
 wrapper.update(packet=str(newpacket),dependencies_sha256={**wrapper['dependencies_sha256'],**deps,str(pub):sha(pub)});atomic(packet_manifest,wrapper)
 index=ROOT/'config/current-model-work-sources.json';items=read(index);row=[pub.name,'BIWN scene reset — actual Author/Repair rejected, one coordinator flag-mask correction qualified'];items=[x for x in items if x[0]!=row[0]];items.append(row);atomic(index,items)
 for path,digest in wrapper['dependencies_sha256'].items():
  source=Path(path);assert source.is_relative_to(ROOT);dest=P/'workbench'/source.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True)
  if not dest.is_file()or sha(dest)!=digest:subprocess.run(['/bin/cp','-c',str(source),str(dest)],check=True,capture_output=True)
 shutil.copy2(packet_manifest,P/'workbench/verification'/packet_manifest.name);shutil.copy2(index,P/'workbench/config'/index.name)
 for rel in ['native_deck_source_context_v13.py','scripts/show_native_status_v2.py']:shutil.copy2(ROOT/rel,P/'workbench'/rel)
 print(json.dumps(dict(status=facts['status'],report=facts['report'],native_reset_entries=witnesses,model_predictions=2,new_training=False,game_images_changed=False),indent=2))
if __name__=='__main__':main()
