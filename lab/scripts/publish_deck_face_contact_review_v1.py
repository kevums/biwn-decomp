"""Freeze six-caller/positive-motion proof, raw V6 failures and qualified hybrid."""
import hashlib,json,shutil,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 pub=Path(read(V/'Deck-face-contact-and-local-v6-current.json')['directory']);sys.path.insert(0,str(ROOT))
 import deck_source_context_v4 as context
 facts=context.snapshot();assert facts['complete_hosted_callers_original_bytes']==1852
 candidate=read(V/'Deck-coordinate-source-candidate-current.json');local=read(V/'Deck-coordinate-local-v6-reviewed-current.json');reader=read(V/'Deck-status-live-v5-reviewed-current.json')
 initial_team=read(V/'native-six-Deck-team-reviewed-current.json');team=read(V/'native-six-Deck-team-role-contract-reviewed-current.json');routes=read(V/'Deck-face-context-current.json')
 assert local['actual_predictions']==2 and local['raw_source_accepted']is False and local['hybrid_positive_motion_pipeline_pass']
 assert reader['new_predictions']==1 and reader['source_checked']and reader['format_pass']
 assert initial_team['actual_predictions']==team['actual_predictions']==3 and not initial_team['role_specialization_pass']and team['role_specialization_pass']
 assert routes['actual_predictions']==0 and len(routes['routes'])==3
 ps=subprocess.run(['/Users/kevin/.lmstudio/bin/lms','ps','--json'],capture_output=True,text=True,check=True);models=json.loads(ps.stdout)
 assert len(models)==1 and models[0]['identifier']=='advertising-scholar'and models[0]['status']=='idle'and models[0]['queued']==0
 save(pub/'model-idle-final.json',models);save(pub/'current-six-caller-facts.json',facts)
 names=['Deck-face-contact-current.json','Deck-face-contact-checker-qualification-current.json','Deck-face-contact-pipeline-current.json','deck-face-contact-world-loop-v1-current.json','Deck-coordinate-source-candidate-current.json','Deck-coordinate-local-v6-current.json','Deck-coordinate-local-v6-reviewed-current.json','Deck-coordinate-boundaries-current.json','Deck-coordinate-v6-hybrid-qualification-current.json','Deck-status-live-v5-current.json','Deck-status-live-v5-reviewed-current.json','native-six-Deck-team-reviewed-current.json','native-six-Deck-team-role-contract-reviewed-current.json','Deck-face-context-current.json','current-model-work-index-v4-current.json']
 evidence=pub/'evidence';evidence.mkdir(exist_ok=True);sources=pub/'as-run-sources';sources.mkdir(exist_ok=True);bindings={};directories={}
 def bind(path,digest=None):
  p=Path(path);current=sha(p)
  if digest is not None:assert current==digest,str(p)
  key=str(p.resolve());target=sources/(hashlib.sha256(key.encode()).hexdigest()[:12]+'-'+p.name)
  if not target.exists():shutil.copy2(p,target)
  bindings[key]=dict(sha256=current,snapshot=str(target),snapshot_sha256=sha(target))
 for name in names:
  p=V/name;j=read(p);shutil.copy2(p,evidence/name)
  if j.get('directory'):directories.setdefault(str(Path(j['directory'])),name.removesuffix('-current.json'))
  for field in ['source_sha256','native_dependencies_sha256','checker_source_sha256','source_bindings']:
   values=j.get(field,{})
   if isinstance(values,dict):
    for path,digest in values.items():bind(path,digest)
   elif field=='source_sha256'and j.get('source'):bind(j['source'],values)
 for directory,label in directories.items():
  if Path(directory)!=pub:shutil.copytree(directory,evidence/label,dirs_exist_ok=True)
 for label,j in [('initial-native-backend-session',initial_team),('retested-native-backend-session',team)]:shutil.copytree(Path(j['session']),evidence/label,dirs_exist_ok=True)
 # Preserve earlier test diagnostics, including the invalid aliased-pointer
 # fixture and the first coordinator-only positive-motion integration.
 for group in ['deck-face-contact','deck-face-contact-pipeline','deck-face-contact-world-loop-v1']:
  shutil.copytree(V/group,evidence/('test-history-'+group),dirs_exist_ok=True)
 component_path=Path(candidate['receipt']);component=read(component_path)
 shutil.copytree(component_path.parent,evidence/'hybrid-component-and-normalization',dirs_exist_ok=True)
 shutil.copytree(Path(candidate['candidate']).parent,evidence/'hybrid-source-and-authorship',dirs_exist_ok=True)
 for path,digest in component['source_bindings'].items():bind(path,digest)
 for path in [Path(__file__),ROOT/'scripts/run_local_deck_coordinate_v6.py',ROOT/'deck_typed_evidence_v2.py',ROOT/'deck_typed_evidence_v3.py',ROOT/'scripts/run_deck_status_live_v5.py',ROOT/'scripts/check_deck_face_contact_pipeline_v1.py',ROOT/'scripts/check_deck_face_context_v1.py',ROOT/'scripts/native_chat_team_context.py',ROOT/'local_stream_inference_v1.py',ROOT/'deck_source_context_v1.py',ROOT/'deck_source_context_v2.py',ROOT/'deck_source_context_v3.py',ROOT/'deck_source_context_v4.py',ROOT/'config/current-model-work-sources.json',ROOT/'Live Local BIWN Briefing.command',ROOT/'Try Local Deck Coordinate.command',ROOT/'Open Local AI Lab v6.command']:bind(path)
 save(pub/'source-bindings.json',bindings)
 assert 'run_deck_status_live_v5.py'in(ROOT/'Live Local BIWN Briefing.command').read_text()
 assert 'run_local_deck_coordinate_v6.py'in(ROOT/'Try Local Deck Coordinate.command').read_text()
 assert (Path.home()/'Desktop/Local AI Lab Launcher.command').resolve()==ROOT/'Open Local AI Lab v6.command'
 assert (Path.home()/'Desktop/Live BIWN Briefing.command').resolve()==ROOT/'Live Local BIWN Briefing.command'
 index=read(V/'current-model-work-index-v4-current.json');assert index['saved_prompt_or_transcript_records']==101
 report=f'''DECK FACE CONTACT AND LOCAL HYBRID REVIEW

The six-face contact caller at 1186A..11AD4 is recovered as structured C. This adds 618 original bytes, including a pinned 12-byte jump table, and covers 175 original instruction locations. The source computes six face-bound arrangements, adds object translations, compares the player position against closed bounds, and invokes the selection/application helpers for the first match. It also preserves the original behavior for kinds above 5: existing bound registers are used rather than an invented skip. The coordinator authored this new caller, its tests and its integration.

All 2,112 original-CPU comparisons pass. They include counts 0..6 and FFFF with an early hit, six face kinds plus 6/FFFF, signed and overflow arithmetic, ASR sign behavior, exact axis boundaries, descriptor indices, all incoming CCR values, both stack banks, caller-saved clobbers, D2 mutation and descriptor changes at helper boundaries. Full CPU/SR/PC/USP/SSP, 2 MB RAM, private frames and helper-entry states match. Another 58 intentional error-handling checks pass. Four compiled defects in midpoint sign, closed-boundary selection, unknown-kind behavior and the helper return address are rejected. The two helper bodies remain declared fixtures in this component comparison; this is not timing, IRQ, physical-hardware or unrestricted-gameplay proof.

The initial extreme-data fixture exposed an alias in the test layout: descriptor index 1's box fields overlap the global descriptor-pointer bytes. Some random box values made that pointer odd and the original CPU correctly raised an address error. The fixture now restores its declared valid descriptor pointer after filling the box, preserving the resulting field aliases. The original CPU and the success comparison gates were unchanged. The failing oracle case and setup diagnostics are retained with the final proof.

The connected test now holds emulated Up through 16 Deck iterations, reaching the previously unexecuted contact helper 16 times against a six-kind game descriptor. Every contact entry/return CPU and RAM checkpoint matches. All six recovered callers execute together: 18 outer-task resumes, 17 input calls, 17 object scans, 16 geometry collections, 16 contact calls and 17 coordinate updates. All 31 native/C checkpoints match and 149 GPU commands execute. Constructor/disc suspension, completion and resume, viewer exit, cache restoration and two world updates remain in the test. There is no original CPU/GPU instruction execution on the C path, although other functions retain earlier generated C. This uses the selector/count13 patch, captured RAM, supplied world entry/two-context ring, resident GPU state and BIOS/disc providers. It does not establish natural unpatched gameplay, private GPU timing or physical-console behavior.

The local V6 coordinate trial added source-derived instruction sizes, exact JSR return PCs and explicit branch fallthrough/address-flag metadata. The original-byte metadata caught the old 11DFE/11E08 return-address guesses: the original returns are 11E00/11E0A. No coordinator target C was supplied. The actual daily 27B Author took 126.36 seconds and failed case 0 on final SR; final RAM matched. Its sole informed Repair took 151.10 seconds, passed case 0, and failed case 1 on three callee-entry SR values even though final CPU and RAM matched. Both raw model drafts remain rejected. Passing one initial case is not a component pass or a held-out result.

The coordinate implementation selected for this experimental pipeline is an explicit hybrid: the actual V6 Repair body plus ten coordinator-added MOVE.L stack flag updates and one temporary caching the existing GPU argument reads. These edits preserve X and set NZVC as the original data moves do. Original MOVEM saves remain flag-neutral. The exact edits and raw-source digest are in authorship.json. The hybrid passes the unchanged 576-case original-CPU/2 MB RAM/private-frame/helper-entry checker, all 87 intentional error-handling checks, another 128 exact boundary/wrap cases, four compiled defect controls and the six-caller positive-motion pipeline. The old coordinator implementation remains available. Raw local source was not silently promoted. No optimizer updates or new model weights were produced.

There are now six hosted readable callers spanning 1,852 original bytes. Five are coordinator-authored; the coordinate caller is the qualified local/coordinator hybrid. This subtotal includes the contact jump table and is not a whole-game completion percentage. The experimental native CDI is unchanged with 34,784 bytes of previously recompiled code. The new versions of these six callers have not replaced their original machine-code versions on that disc. The whole game cannot yet be rebuilt from recovered readable source.

The installed native-team backend ran three actual local roles on the current facts. The first Analyst/Restorer/Reviewer outputs were 58/59/55 words and factually consistent, but the Restorer repeated the Analyst instead of providing an engineering handoff. A Deck-specific Restorer contract now requires two JSON fields, next_source_step and reason, containing an unfinished implementation action rather than completed-work counts. On the same exposed question, the retest produced 59/35/58-word contributions: factual Analyst, valid distinct engineering handoff, and source-consistent Reviewer. This is a narrow repeat-case result; the role contract and authorship metadata were clarified, and it is not general quality or independent-verification evidence. Both runs retain exact formatted prompts and raw responses. The controller is a mock UI: current native LM Studio Chat model selection/rendering remains unverified. No native conversation file was injected, app restarted or unlock requested.

The separate live Reader produced a source-checked 61-word answer in 7.41 seconds, streamed in 116 message fragments with a 2.694-second first message. It distinguishes raw local failure from hybrid success and says the whole game is incomplete. It is one warm evidence-supplied inference, not a cold-start/general benchmark. Desktop menu option 11 and Live BIWN Briefing use it. Option 10 now runs the actually exercised V6 coding workflow; that two-role code trial took about 4.6 minutes of generation. Option 7 indexes 101 saved prompt/transcript records. There were nine actual predictions in this goal turn: two code drafts, three initial backend roles, three retest roles and one Reader. 101 is not a prediction count. Three final context routes (Deck, preview controls, copyediting) also pass with zero predictions.

Main menu v6, the installed plugin bundle and the v18 MCP tool set remain in place. The daily 27B model is idle and ready at the final check. Advertising's daily model and optional previously trained Reviewer are retained. The earlier Advertising entailment, follow-up chronology, length and repeated-Reviewer failures remain unresolved; there was no Advertising training or new quality claim here. The tested portable v17 snapshot is unchanged and does not contain this latest source, context, role-contract or shortcut work. Another-machine/future-hardware acceptance is pending.

The next substantial game step is to qualify the recovered Deck routines for the native-console build while resolving the remaining construction/slot/geometry dependencies and original asset schema. Broad gameplay, timing and physical-console verification are still required. Full restoration, easy native Chat, broader Advertising reliability and current-version migration remain active requirements.

Exact local code prompts, responses and counterexamples:
{Path(local['directory'])/'prompts-and-responses.txt'}

Exact final three-role prompts and responses:
{Path(team['directory'])/'prompts-and-responses.txt'}

Exact live Reader prompt and response:
{Path(reader['directory'])/'prompts-and-responses.txt'}

Source and evidence publication:
{pub}
'''
 friendly=ROOT/'reports/Deck Face Contact and Local Hybrid Review.txt';friendly.write_text(report);(pub/'report.txt').write_text(report)
 audit=dict(recorded_at=datetime.now(timezone.utc).isoformat(),full_objective_complete=False,requirements={
  'readable_BIWN_decompilation_and_same_console_rebuild':dict(status='incomplete',evidence='Sixhostedcallers1852originalbytes;newcontact2112comparisons andqualifiedlocalhybrid576+128cases;positive-motion31checkpointpipeline. NativeCDIunchanged34784,newcallersnotinstalled. Missingdependencies/asset/GPU/DSP/timing/hardwarework remain.'),
  'easy_local_inference_visible_multiagent_workflows_and_training':dict(status='partial',evidence='ActualV6Author/soleRepairrawrejected;qualifiedhybriduses10coordinatorflagupdates. Threeactualbackendroles neededspecificRestorercontract;retestpassesoneexposedcase. One-clickReader7.41s andsavedprompts101records. NativeChatUIunverified. Earliertrainedprofilesretained;nooptimizerupdatesthisturn.'),
  'Advertising_research_and_education_ready_model':dict(status='partial',evidence='Daily27BandoptionaltrainedReviewerretained. Priorsemantic/chronology/wordlimit/Reviewerduplication failuresremain. NonewAdvertisinginference/trainingorqualityclaimthisturn.'),
  'future_256GB_setup_and_portability':dict(status='partial',evidence='Earlierportablev17snapshotretained;currentv18andnewworkflow notmigrated. Actualothermachine/futurehardwareunverified.')})
 save(pub/'requirement-audit.json',audit)
 state=dict(status='terminal_Deck_face_contact_and_local_hybrid_reviewed',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(pub),new_face_extent_bytes=618,new_face_instruction_locations=175,face_component_cases=2112,face_error_checks_passed=58,face_defect_controls_rejected=4,total_six_hosted_caller_original_bytes=1852,coordinate_authorship='ActuallocalV6Repair+10coordinatorstackflagupdates/onecachedreadtemporary;rawCremainsrejected.',coordinate_hybrid_component_cases=576,coordinate_hybrid_error_checks_passed=87,coordinate_hybrid_boundary_cases=128,coordinate_hybrid_defect_controls_rejected=4,paired_checkpoints=31,contact_calls=16,GPU_commands=149,actual_predictions=9,new_training=False,raw_local_source_accepted=False,qualified_hybrid_selected=True,native_disc_changed=False,native_Chat_verified=False,whole_game_complete=False,review=str(friendly),review_sha256=sha(friendly),integrity=str(pub/'integrity.json'),ongoing_finite_workers=[])
 save(pub/'protocol.json',state);save(V/'Deck-face-contact-and-local-v6-current.json',state)
 goal_path=V/'goal-continuation-current.json';goal=read(goal_path)
 goal.update(status='active_Deck_face_contact_and_local_hybrid_reviewed',recorded_at=state['recorded_at'],directory=str(pub),previous_goal_turn_classification='progress:outertask recovered/qualified andV5/Readeractualinference reviewed',current_turn_classification='progress',full_objective_complete=False,blocked=False,ongoing_finite_workers=[],publication=str(V/'Deck-face-contact-and-local-v6-current.json'),review=str(friendly),integrity=str(pub/'integrity.json'),current_turn_predictions=9,new_training=False,saved_prompt_or_transcript_records=101,requirement_audit=str(pub/'requirement-audit.json'),Deck_face_contact_and_local_hybrid=state)
 goal['remaining_requirements']=dict(game='Fullreadablegame/sameconsolebuild incomplete. SixhostedDeckcallers1852originalbytes;face2112CPU/58errorchecks andqualifiedcoordinatehybrid576CPU/87error/128boundary pass. Positivemotion16contactcalls/31checkpoints/149GPU pass. NativeCDI34784unchanged;newsixcallersnotinstalled. Remainingconstruction/slot/geometry/assets/GPU/DSP/timing/hardware pending.',local_LM_frontend='OneclicksixcallerReader7.41sec116fragments. V6codeflow2rawcandidatesrejected;hybrid10coordinatorflagupdatesqualified. Actualbackend3rolesinitiallyrepeatedRestorer;twofieldhandoffretestpassesoneexposedcase. NativeChatUIunverified;finalcontext3routespass. Prompts101records.',Advertising=goal['remaining_requirements']['Advertising'],portable_future256GB='Retainedtestedportablev17/32980snapshot. Currentv18MCP/menuv6,new6Decksources/hybrid/contextv4/Restorercontract andnewliveReader/codeflow notmigrated. Actualfuturehardwareacceptance pending.')
 goal['next_actions']=['PrioritizequalifyingrecoveredDeckcallersfornativeconsolebuild withhonestregister/helper/stackABI gates;recoverremainingconstruction/slot/geometryandoriginalasset schemaasneeded. Do notsubstitutepatchedhostedproof forfullgame/hardware.', 'UseactualV6callee-entryflagfailures toguidefuturelocalworkflow/training. Rawcodefailed;hybridpassrequires10explicitcoordinatorfixes. Preserveexposed-case/noindependentgeneralizationboundary.', 'ImproveAdvertisingentailment/followupchronology/length andReviewerbehavior withoutweakeningexactsourcegates ortrainingonexcludedpaper.', 'VerifyactualnativeChatselection/display whenUIbridgeavailabilitychanges;continueheadlesswhilelocked withoutunlockrequests.', 'Packagecurrentv18plusnewsource/frontend/roleworkwithversionedacceptance;retainpassedv17 andtestactualfuturemachinebeforeclaimingmigration.']
 save(goal_path,goal);shutil.copy2(goal_path,pub/'goal-state-final.json')
 files=[]
 for p in sorted(pub.rglob('*')):
  if p.is_file()and p!=pub/'integrity.json':files.append(dict(path=str(p.relative_to(pub)),bytes=p.stat().st_size,sha256=sha(p)))
 save(pub/'integrity.json',dict(status='terminal_all_published_file_hashes_verified',files=len(files),entries=files))
 for row in files:
  p=pub/row['path'];assert p.stat().st_size==row['bytes']and sha(p)==row['sha256'],str(p)
 print(state['status']);print('Verified publication files:',len(files));print(friendly)
if __name__=='__main__':main()
