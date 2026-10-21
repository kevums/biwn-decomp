"""Publish actual local C authorship and finite fresh source-CPU integration."""
import json,re,subprocess
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
def read(path):return json.loads(Path(path).read_text())
def main():
 parentp=ROOT/'verification/native-formatter-GPU-wait-publication-current.json';parent=read(parentp)
 names=['GPU-wait-Code-Author','GPU-wait-Code-Author-revision','GPU-wait-local-C-check','native-formatter-C-bridge','native-formatter-C-new-forms','native-formatter-C-fresh-pair','native-formatter-C-merchant-pair']
 paths={name:ROOT/'verification'/(name+'-current.json')for name in names};proofs={k:read(p)for k,p in paths.items()}
 gate=proofs['GPU-wait-local-C-check'];small=proofs['native-formatter-C-fresh-pair'];long=proofs['native-formatter-C-merchant-pair'];forms=proofs['native-formatter-C-new-forms'];author=proofs['GPU-wait-Code-Author-revision'];bridge=proofs['native-formatter-C-bridge']
 assert gate['accepted']and gate['cases']==8192 and gate['failed_cases']==0 and forms['failures']==0 and forms['cases']==79488
 assert small['status']=='terminal_fresh_C_formatter_pair_equal'and long['status']=='terminal_fresh_C_merchant_pair_equal'
 assert all(not v['different_frames']for record in [small,long]for v in record['comparisons'].values())and long['audio_PCM_equal']and small['audio_PCM_equal']
 assert long['results']['C']['frames']==24975 and long['results']['C']['merchant_reached']and long['results']['C']['outdoor_hold']==120
 backend=long['C_backend'];assert backend['stats']['steps']==433073691 and backend['counts']['Original']==0 and backend['counts']['Rejected']==0 and backend['stats']['errors']==0
 assert backend['stats']['calls']==backend['stats']['steps']+backend['stats']['HLE']
 deps=dict(parent['status_dependencies_sha256']);deps[str(parentp)]=sha(parentp);input_aliases=[]
 def add(path,expected=None):
  p=Path(path).resolve();assert p.is_relative_to(ROOT),str(p)
  h=sha(p)
  if expected is not None and expected!=h:
   assert p==ROOT/'verification/GPU-wait-local-C-check-current.json',str(p)
   matches=[q for q in(ROOT/'verification/GPU-wait-local-C-check').glob('*/protocol.json')if sha(q)==expected]
   assert len(matches)==1,(str(p),expected)
   input_aliases.append(dict(as_run_path=str(p),as_run_sha256=expected,immutable_snapshot=str(matches[0])))
   p=matches[0];h=sha(p)
  assert expected is None or expected==h,str(p)
  if str(p)in deps:assert deps[str(p)]==h,str(p)
  deps[str(p)]=h
 for name,p in paths.items():
  d=proofs[name];add(p)
  for field in ['source_sha256','output_sha256']:
   table=d.get(field,{})
   if isinstance(table,dict):
    for key,h in table.items():add(key,h)
  directory=Path(d['directory'])
  for file in directory.iterdir():
   if file.is_file():add(file)
 for proof in [small,long]:
  for lane in ['reference','C']:
   d=Path(proof['directory'])/lane
   for name in ['report.json','RAM-final.bin','frontend-PCM.s16le','native-CPU-bridge-report.json']:add(d/name)
   r=read(d/'report.json');assert sha(d/'RAM-final.bin')==r['final_RAM_sha256']
 # Bind the dynamically linked local C provider graph, not just the newest
 # wrapper filename. System libraries remain host dependencies.
 queue=[Path(read(bridge['native_CPU_candidate'])['library']),Path(read(bridge['CPU_candidate'])['library'])];libraries=set()
 while queue:
  p=queue.pop().resolve()
  if p in libraries:continue
  libraries.add(p);add(p)
  text=subprocess.check_output(['otool','-L',str(p)],text=True)
  for line in text.splitlines()[1:]:
   path=line.strip().split(' (',1)[0]
   if path.startswith(str(ROOT))and Path(path).resolve()not in libraries:queue.append(Path(path))
 export=ROOT/'projects/black-ice-white-noise/restoration/experimental/native-formatter-runtime-C'
 for p in export.rglob('*'):
  if p.is_file():add(p)
 assert (export/'biwn_GPU_wait_repair.c').read_bytes()==Path(author['source']).read_bytes()
 add(Path(__file__))
 for p,h in deps.items():assert sha(p)==h,p
 now=datetime.now(timezone.utc);out=ROOT/'verification/native-formatter-C-runtime-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 initial=proofs['GPU-wait-Code-Author'];initial_gate=read(Path(initial['directory'])/'coordinator-review.json')if (Path(initial['directory'])/'coordinator-review.json').exists()else None
 local=dict(program='GPU completion wait; six fixed68000instruction entries',model_identifier=author['model_identifier'],source=str(export/'biwn_GPU_wait_repair.c'),source_sha256=sha(export/'biwn_GPU_wait_repair.c'),exact_prompt_response_directory=author['directory'],first_draft_failed_native_cases=[832,1024],guided_revision=True,coordinator_feedback='Explicit SRbitmasks,A7index and active/inactive stack-bank rules plus actual nativecounterexamples.',coordinator_edited_accepted_C=False,native_instruction_cases=8192,host_error_guards=7,same_weights_as_other_roles=True,independent_review=False,seconds_initial=initial['seconds'],seconds_revision=author['seconds'],original_game_function_recovery_claimed=False,new_training=False)
 summary=('The repaired14690byte BIWN image now also runs through a separate host C instruction provider. '
 'Across a fresh24975frame merchant/outdoor-return pair, every recorded fullCPU,2MBRAM,GPU/DSPstate, '
 'video and navigation result matches native68000execution on that same image; capturedPCM is byteidentical. '
 'After mainstage4000,the C lane executes433073691ordinary68000instruction steps inC plus25440HLE-return '
 'adapters,with0originalCPUopcodefallback/rejections. Pre-mainstage2837350callbacks andGPU,DSP,devices, '
 'IRQeventservices remain retainedemulator; this is not a standalone source-built console game. '
 'The local Code Author supplied an unedited guided six-entry wait C revision passing8192native cases '
 'and7hosterrorchecks; its firstdraft failed832of1024cases. Coordinator-added414instruction forms '
 'pass79488controllednative fixtures. The24962entry staticcatalogue includes4916native-image starts '
 'and doesnot measure recoveredoriginalgamefunctions. Prior 2600frame formatter-vs-original-helper '
 'Deck lanes still differ in positions/video; this new equal comparison is C-vs-native execution '
 'of the same repairedimage. No arbitraryfault/alias/IRQinterleaving,other-scene,whole-game,hardware '
 'or overall speedup proof. Originaldisc,defaultpreview andmodelweights are unpromoted; no newtraining.')
 status='terminal_native_formatter_C_runtime_and_local_authorship_published'
 current=dict(parent['current_status']);current.update(status=status,recorded_at=now.isoformat(),checked_answer=summary,checked_current_summary=summary,current_verified_route_summary=summary,local_C_authorship=local,C_runtime_comparison=dict(frames=24975,CPU_instruction_steps_in_C=backend['stats']['steps'],HLE_return_adapters=backend['stats']['HLE'],original_68000_opcode_fallback_after_mainstage_4000=0,pre_mainstage_native_callbacks=backend['entry_gate']['bootstrap_native_callbacks'],same_repaired_disc=True,all_recorded_frame_fields_equal=True,compared_fields=list(long['comparisons']),PCM_byte_identical=True,merchant_reached=True,outdoor_hold=120,retained_components=['pre-mainstage bootstrap','GPU','DSP','blitter/objectprocessor','firmwareHLE','device andIRQeventservices'],proof=str(paths['native-formatter-C-merchant-pair']),proof_sha256=sha(paths['native-formatter-C-merchant-pair']),scope='Finite frame-boundary/source-CPU comparison on the same repairedprogram,not completeplatformreplacement or physicalconsole.'),C_instruction_forms=dict(newly_supported_instruction_entries=414,native_cases=79488,zero_mismatches=True,scope=forms['scope']),static_C_instruction_catalogue=dict(entries=bridge['selected_static_cases'],native_image_starts_added=4916,original_game_function_or_unique_instruction_recovery_count=False),source_export=str(export),authorship_limits='Guided local source only for six-entry restoration wait. Other new native-imageC was coordinator-generated; existing original-game providers are inherited. No neworiginal-gamefunction total,independentreview or weighttraining.',whole_game_complete=False,physical_console_verified=False,standalone_runtime_verified=False,default_promoted=False,new_training=False,goal_complete=False)
 report=ROOT/'reports/native-formatter-C-runtime.txt';current['report']=str(report)
 text=f'''BIWN: FRESH C CPU INTEGRATION AND LOCAL CODE AUTHOR
{now.isoformat()}

The repaired 14,690-byte experimental disc now has a matching host C CPU provider. In a fresh 24,975-frame merchant and outdoor-return comparison, full CPU state, all 2 MB RAM, saved GPU/DSP state, video and navigation match at every recorded frame. Captured PCM is byte-identical. A separate fresh 1,600-frame pair also matches. Neither test restores a checkpoint or patches live guest RAM.

The long C run implements 433,073,691 ordinary 68000 instruction steps in C and 25,440 HLE return adapters after mainstage4000, with zero original 68000 opcode fallback or rejections. The 2,837,350 pre-mainstage bootstrap callbacks still use the native core. GPU, DSP, device, blitter/object-processor and IRQ event services remain retained emulator providers. Frame equality is scoped to these exact runs, not arbitrary internal instruction interleavings, other scenes, hardware or a standalone console source build.

LOCAL MODEL CONTRIBUTION
The local Code Author's first draft failed 832 of 1,024 native cases because of SR bits and stack handling. A guided revision, with explicit bitmasks and native counterexamples, passes 8,192 individual-instruction cases across all CCR values, both CPU modes and all interrupt masks, plus seven host-error checks. The accepted C text was not edited by the coordinator. This is six fixed entries implementing a coordinator-authored restoration repair; it is not a newly recovered original BIWN function, a held-out general code benchmark or new weight training.

The coordinator added the other missing instruction forms and runtime wiring. Their 414 newly supported instruction entries pass 79,488 native CPU fixtures with full CPU and 2 MB RAM comparisons. The 24,962-entry static catalogue and its 4,916 native-image starts are compile metadata, not original-game function coverage. Older failed preparation receipts remain unchanged; the later completed bridge and runtime proofs supersede them for this candidate.

The earlier native formatter-versus-original-helper Deck lanes retain their position/video differences. The new equal result compares C and native execution of the same repaired disc. It does not erase those earlier differences, prove an overall speedup or establish physical audio quality.

Exact model prompts and responses:
Initial: {initial['directory']}
Guided revision: {author['directory']}

Reusable C source and build instructions:
{export}

Proofs:
{chr(10).join(str(p)for p in paths.values())}

No existing preview or model weights were promoted. Advertising research and teaching entry points remain available; no advertising training or evaluation data changed in this work. Remaining work includes broader source/runtime integration, more scenes and exception/IRQ cases, native Chat usability, useful training gains, authenticated console boot, audio listening and future 256 GB hardware testing.
'''
 report.write_text(text);(out/'report.txt').write_text(text);add(report)
 publication=dict(status=status,recorded_at=now.isoformat(),directory=str(out),report=str(report),current_status=current,status_dependencies_sha256=deps,immutable_input_aliases=input_aliases,linked_local_libraries=len(libraries),integrity_mismatches=0,local_guided_C=local,original_disc_modified=False,new_training=False,default_promoted=False,goal_complete=False)
 save(out/'publication.json',publication);save(ROOT/'verification/native-formatter-C-runtime-publication-current.json',publication)
 ledgerp=ROOT/'verification/goal-continuation-current.json';ledger=read(ledgerp);ledger.update(status='active_fresh_C_formatter_CPU_runtime_and_guided_local_C_verified_goal_incomplete',recorded_at=now.isoformat(),previous_goal_turn_classification='progress: captured and repaired pendingGPUwait race; finite nativegameplay and localworkflow validated.',current_goal_turn_classification='progress',this_turn_classification='progress',current_goal_turn_progress='Guided localwaitC passes8192native cases after832/1024 initialfailures; coordinator414forms pass79488fixtures. Fresh C-vs-native1,600and24,975framepairs matchCPU/2MBRAM/GPU-DSP/video/PCM/navigation;433073691ordinaryCsteps+25440HLEreturns and0originalCPUopfallback after4000. Retainedbootstrap/GPU/DSP/devices andfullgoalunfinished.',current_goal_turn_evidence=str(ROOT/'verification/native-formatter-C-runtime-publication-current.json'),latest_C_formatter_runtime_publication=str(ROOT/'verification/native-formatter-C-runtime-publication-current.json'),latest_finite_jobs_running=False,goal_complete=False,new_training=False,next_actions=['Integrate/check sourceGPU/DSP and IRQproviders with the new fresh CCPU runtime.','Exercise additional scenes,exceptions and IRQinterleavings; preserve oldfailedartifacts.','Maintain source-separated advertisingtrainingdata and representative evaluation; do not promote regressedadapters.','Verify nativeChat,physicalconsole/audio andfuture256GBhardware whenavailable.']);save(ledgerp,ledger)
 with(ROOT/'runs/agent-work-audit.jsonl').open('a')as f:f.write(json.dumps(dict(recorded_at=now.isoformat(),coordinator='Native-imageC integration,414formemitter,79488oraclecases,freshpairs andpackaging',local_Code_Author='Initial53.01seconds failed832/1024; guided57.58second revision passed8192cases,rawCunchanged',same_model_weights=True,independent_review=False,compiler_and_emulator_are_tools=True,new_training=False,native_Chat_verified=False,publication=str(ROOT/'verification/native-formatter-C-runtime-publication-current.json')))+'\n')
 print(json.dumps(dict(status=status,evidence_files=len(deps),linked_local_libraries=len(libraries),integrity_mismatches=0,report=str(report))),flush=True)
if __name__=='__main__':main()
