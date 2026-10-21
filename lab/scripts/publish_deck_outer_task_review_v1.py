"""Freeze outer-task recovery, actual V5 predictions and current desktop delivery."""
import hashlib,json,os,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 pointer=V/'Deck-outer-task-and-local-v5-current.json';pub=Path(read(pointer)['directory']);assert pub.is_dir()
 import sys
 sys.path.insert(0,str(ROOT));import deck_source_context_v3 as context
 facts=context.snapshot();assert facts['whole_game_complete']is False
 local=read(V/'Deck-coordinate-local-v5-reviewed-current.json');reader=read(V/'Deck-status-live-v4-reviewed-current.json');routes=read(V/'Deck-outer-context-current.json')
 assert local['actual_predictions']==2 and local['source_accepted']is False and local['repair_executable_C_changed']
 assert all(not x['component_pass']and x['completed_comparisons']==0 for x in local['roles'])
 assert reader['source_checked']and reader['new_predictions']==1 and reader['format_pass']
 assert routes['actual_predictions']==0 and len(routes['routes'])==3
 ps=subprocess.run(['/Users/kevin/.lmstudio/bin/lms','ps','--json'],capture_output=True,text=True,check=True)
 models=json.loads(ps.stdout);assert len(models)==1 and models[0]['status']=='idle'and models[0]['queued']==0
 save(pub/'model-idle-final.json',models)
 goal_path=V/'goal-continuation-current.json';old_goal=read(goal_path);shutil.copy2(goal_path,pub/'before/goal-continuation-current.json')
 names=['Deck-task-source-current.json','Deck-task-pipeline-current.json','deck-task-readable-world-loop-v1-current.json','Deck-task-checker-qualification-current.json','Deck-task-volatile-waits-current.json','Deck-outer-context-current.json','Deck-coordinate-local-v5-current.json','Deck-coordinate-local-v5-reviewed-current.json','Deck-status-live-v4-current.json','Deck-status-live-v4-reviewed-current.json','current-model-work-index-v4-current.json']
 evidence=pub/'evidence';evidence.mkdir(exist_ok=True);sources=pub/'as-run-sources';sources.mkdir(exist_ok=True);bindings={}
 def bind(path,expected=None):
  p=Path(path);digest=sha(p)
  if expected is not None:assert digest==expected,str(p)
  key=str(p.resolve());dest=sources/(hashlib.sha256(key.encode()).hexdigest()[:12]+'-'+p.name)
  if not dest.exists():shutil.copy2(p,dest)
  bindings[key]=dict(sha256=digest,snapshot=str(dest),snapshot_sha256=sha(dest))
 directories={}
 for name in names:
  p=V/name;j=read(p);shutil.copy2(p,evidence/name)
  directory=Path(j['directory']);assert directory.is_dir()
  if directory!=pub:directories.setdefault(str(directory),name.removesuffix('-current.json'))
  for field in ['source_sha256','native_dependencies_sha256','checker_source_sha256']:
   values=j.get(field,{})
   if isinstance(values,dict):
    for p,digest in values.items():bind(p,digest)
   elif field=='source_sha256'and j.get('source'):bind(j['source'],values)
 for directory,label in directories.items():
  target=evidence/label
  shutil.copytree(directory,target,dirs_exist_ok=True)
 for p in [Path(__file__),ROOT/'scripts/run_local_deck_coordinate_v5.py',ROOT/'scripts/run_deck_status_live_v4.py',ROOT/'scripts/native_chat_team_context.py',ROOT/'deck_source_context_v1.py',ROOT/'deck_source_context_v2.py',ROOT/'deck_source_context_v3.py',ROOT/'deck_typed_evidence_v2.py',ROOT/'local_stream_inference_v1.py',ROOT/'config/current-model-work-sources.json',ROOT/'Live Local BIWN Briefing.command',ROOT/'Try Local Deck Coordinate.command',ROOT/'Open Local AI Lab v6.command']:bind(p)
 for p,digest in read(V/'deck-task-readable-world-loop-v1-current.json')['source_sha256'].items():bind(p,digest)
 save(pub/'source-bindings.json',bindings)
 live=ROOT/'Live Local BIWN Briefing.command';trial=ROOT/'Try Local Deck Coordinate.command'
 assert 'run_deck_status_live_v4.py'in live.read_text()and 'run_local_deck_coordinate_v5.py'in trial.read_text()
 for link,target in [(Path.home()/'Desktop/Local AI Lab Launcher.command',ROOT/'Open Local AI Lab v6.command'),(Path.home()/'Desktop/Live BIWN Briefing.command',live)]:assert link.resolve()==target,str(link)
 index=read(V/'current-model-work-index-v4-current.json');assert index['saved_prompt_or_transcript_records']==97
 roles=local['roles'];report=f'''DECK OUTER TASK RECOVERY AND LOCAL MODEL TRIAL

The outer Deck/C-Space task at 11E6C..11F6C is now recovered as structured C. This adds 256 original code bytes and 58 instruction locations. It preserves LINK/UNLK frames, signed mode dispatch, ordinary geometry and mail-view argument layouts, display submission, volatile waits, loop boundaries and dependency suspension/resumption. This source is coordinator-written. Dependencies remain explicit services; the complete game is not decompiled or rebuildable from recovered readable source.

All 1,280 original-CPU comparisons pass, including initialization, mode 0/1/2/3 and signed unknown modes, both stack banks, all incoming CCR values, every JSR-return continuation, helper clobbers and changed globals. CPU registers/SR/PC/USP/SSP, full 2 MB RAM, private frames and helper-entry states match. Another 41 intentional host-error checks and three continuation checks pass. These counts describe passed tests, not observed runtime errors. Four compiled defects in local initialization, mail-stack cleanup, signed display selection and frame restoration are rejected.

Twelve additional volatile-wait cases compare the original TST/BNE loop with the recovered source in both stack banks, using 0/1/3/8/63/65 declared nonzero flag reads before zero. The final CPU/RAM/helper entries and the flag-read count match. Two more compiled defects that skip waiting or omit the volatile read are rejected. The provider changes one explicit flag at read boundaries; this test does not simulate hardware time or interrupts. The recovered task can yield a committed continuation at 11F50 when a host polling quantum expires.

The connected experimental source test now runs all five recovered Deck callers: 18 outer-task resumes, 17 input calls, 17 active-object scans, 16 geometry collections and 17 coordinate updates. All 31 native/C checkpoints match, with 16 render iterations and 149 GPU commands. The sequence includes real source constructor/disc suspension, completion, resume, viewer exit, cache restoration and two world updates. There are no original CPU/GPU instructions on the C path. However, other bodies retain prior generated C; the selector/count13 patch, captured RAM, supplied world entry/two-context ring, BIOS/disc providers and resident GPU state remain experimental inputs. Natural unpatched gameplay, GPU private timing, physical hardware and unrestricted gameplay are not established.

These five hosted structured callers cover 1,234 original bytes. This is a subtotal for this Deck recovery, not all project code or a completion percentage. The native experimental CDI remains unchanged with 34,784 bytes of previously recompiled native code. The new C versions of these five callers have not replaced their original machine-code versions on that disc. Full same-console source rebuild remains unfinished.

Who did what: the coordinator recovered and integrated the outer-task C, supplied the explicit ABI and fixtures, wrote the comparisons and reviewed the results. The pinned original CPU, compiler, source pipeline and defect tests are tools. The local 27B base ran separate Author and Informed Repair contexts for the coordinate routine; these roles share weights and are not independent agents. The Author received original assembly/typed operands, exact physical register indices and glue semantics. The Repair received the same evidence, the prior draft and the actual concise counterexample. Neither received the coordinator's target C.

The actual Author took {roles[0]['seconds']} seconds and the sole Repair took {roles[1]['seconds']} seconds. Both compiled and both were rejected at the first original-CPU comparison. The Author now matches all 16 final registers but differs in SR and four RAM bytes. The Repair changes executable C and matches the complete final CPU state in that first case, but the same four memory differences remain, including private stack memory. This is not a component pass or a held-out/general quality gain. No raw local C was adopted, and no optimizer update or new model weights were produced.

The separate live status Reader answered in 6.30 seconds, with 88 visible message fragments and a 2.388-second first-message time. Its 44-word answer correctly scopes the five callers, outer/input counts, native-disc gap and incomplete whole-game rebuild. It is one warm evidence-supplied inference on the loaded daily 27B model, not a cold-start or general reliability benchmark. The final phrase 'Local candidates unverified' means unaccepted; the exact two V5 rejections are retained separately above.

Desktop Local AI Lab Launcher option 11 and Live BIWN Briefing now run that tested five-caller briefing. Option 10 runs the actually exercised V5 Author/verifier/Repair workflow. Option 7 includes the exact new transcripts and now indexes 97 saved prompt/transcript records; 97 is not a prediction count. There were three actual local predictions in this goal turn. Main menu v6, the v18 MCP tools and installed native-team plugin bundle are unchanged. The native team's source-context provider now receives the five-caller evidence. Direct context checks pass for Deck, preview controls and copyediting, with zero model predictions. Native Chat selection/rendering remains unverified; no UI retry, unlock request, app restart or hidden conversation injection occurred this turn.

Advertising's daily model and optional previously trained Reviewer remain available. Earlier source-entailment/follow-up/length failures and repeated Reviewer output remain unresolved. No Advertising training or new quality claim is made here. The retained portable v17 snapshot is unchanged and does not include these new source/menu/context changes; actual future-machine acceptance remains pending.

Next game work is the remaining Deck geometry, slot and construction dependencies and original asset schema, then qualified native-image integration and broader behavior/timing/hardware verification. Full-game restoration, easy native Chat, broader Advertising reliability and current-version migration remain active requirements.

Exact local code prompts, raw responses and verifier results:
{Path(local['directory'])/'prompts-and-responses.txt'}

Exact live Reader prompt and response:
{Path(reader['directory'])/'prompts-and-responses.txt'}

Source and evidence publication:
{pub}
'''
 friendly=ROOT/'reports/Deck Outer Task Recovery and Local Model Trial.txt';friendly.write_text(report);(pub/'report.txt').write_text(report)
 audit=dict(recorded_at=datetime.now(timezone.utc).isoformat(),full_objective_complete=False,requirements={
  'game_readable_decompilation_and_same_console_rebuild':dict(status='incomplete',evidence='Five hosted Deck callers/1234originalbytes;1280newoutercomparisons and31connectedcheckpoints. NativeCDIunchanged34784;newcallersnotinstalled. Othergame/geometry/asset/GPU/DSP/timing/hardware work pending.'),
  'easy_local_inference_and_visible_multiagent_frontend':dict(status='partial',evidence='Actual daily27B two-code-role benchmark rejectsboth;liveReader6.3seconds. One-click options updated. NativeChatUIunverified;contextproviderthree routesverified. Exactprompts/responses saved.'),
  'advertising_research_education_ready_model_and_training':dict(status='partial',evidence='Dailybase andoptionaltrainedReviewerretained. NoAdvertisingchanges/newtrainingthisturn. Priorsemantic/followup/wordlimit/Reviewerduplication failuresstillpending.'),
  'future_256GB_configuration_portability':dict(status='partial',evidence='Previously tested portablev17retained;currentv18andnewDeckworkflow notmigrated. Actualfuturehardwareunavailable/unverified.')} )
 save(pub/'requirement-audit.json',audit)
 state=dict(status='terminal_Deck_outer_task_and_local_v5_reviewed',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(pub),authorship='Coordinator recovered/integrated/testedouterC;actualdaily27BAuthor/soleRepairrejected;separatelocalReaderreviewed.',new_original_code_bytes=256,total_five_hosted_caller_original_bytes=1234,outer_CPU_comparisons=1280,host_error_checks_passed=41,continuation_checks_passed=3,volatile_wait_cases=12,compiled_defects_rejected=6,paired_checkpoints=31,outer_resumes=18,GPU_commands=149,actual_predictions=3,new_training=False,source_adopted_from_local_trial=False,native_disc_changed=False,whole_game_complete=False,native_Chat_verified=False,review=str(friendly),review_sha256=sha(friendly),integrity=str(pub/'integrity.json'),ongoing_finite_workers=[])
 save(pub/'protocol.json',state);save(pointer,state)
 old_goal.update(status='active_Deck_outer_task_and_local_v5_reviewed',recorded_at=state['recorded_at'],directory=str(pub),previous_observation_turn_classification='no_progress_read_only_user_status_answer;revalidatedcurrentstateandcompletednewsource/inferencework',current_turn_classification='progress',full_objective_complete=False,blocked=False,ongoing_finite_workers=[],publication=str(pointer),review=str(friendly),integrity=str(pub/'integrity.json'),current_turn_predictions=3,new_training=False,saved_prompt_or_transcript_records=97,requirement_audit=str(pub/'requirement-audit.json'),Deck_outer_task_and_local_v5=state)
 old_goal['remaining_requirements']=dict(game='Fullreadablegame/same-console sourcerebuild incomplete. FivehostedDeckcallers1234originalbytes nowstructuredC;outer1280CPU/41errorchecks/3continuations/12waitcases and31checkpointexperimentalpipeline pass. NativeCDI34784unchanged;fivecallersnotinstalled. Remaininggeometry/slot/construction/asset/GPU/DSP/timing/hardware pending.',local_LM_frontend='Fivecaller liveTerminalReader tested6.3sec/88fragments. Codeoption10V5actuallytested;Author/soleRepairbothfirstcaserejected. Exactprompts97savedrecords. Currentnativebackendfivecallercontextready,preview/copyeditroutespass;nativeChatUIstillunverified.',Advertising=old_goal['remaining_requirements']['Advertising'],portable_future256GB='Retainedportablev17/32980snapshot tested. Currentv18MCP/menuv6,newfiveDecksources/contextv3 andupdatedliveReader/codeflow notcopiedthere. Actualothermachine/future256GBacceptance pending.')
 old_goal['next_actions']=['RecoverremainingDeckgeometry/slot/constructiondependencies andoriginalasset schema;qualify readablecallers nativeimageintegration withoutclaimingunpatchedE26C/hardwarecoverage.', 'UseactualV5memory/privateframecounterexamples fornextlocalcodeimprovement;bothrawlocaldraftsstillfaildespiterepairfinalCPUmatch. Do nottrain/evalclaimgeneralizationonthisexposedroutine.', 'ImproveAdvertisingReviewersource-entailment/followupchronology/length;retainexactsourcegates andexcludedsourcetrainingboundary.', 'Verify nativeChat whenUIavailabilitychanges;continueheadlesswhilelocked withoutunlockrequests.', 'Packagecurrentv18andnewsource/frontendswithversionedacceptance;retainpassedv17snapshot anddeferactualfuturehardwareclaimuntiltested.']
 save(goal_path,old_goal);shutil.copy2(goal_path,pub/'goal-state-final.json')
 # Freeze current delivery and all evidence; the manifest excludes itself.
 files=[]
 for p in sorted(pub.rglob('*')):
  if p.is_file()and p!=pub/'integrity.json':files.append(dict(path=str(p.relative_to(pub)),bytes=p.stat().st_size,sha256=sha(p)))
 integrity=dict(status='terminal_all_published_file_hashes_verified',files=len(files),entries=files)
 save(pub/'integrity.json',integrity)
 for row in files:
  p=pub/row['path'];assert p.stat().st_size==row['bytes']and sha(p)==row['sha256'],str(p)
 print(state['status']);print('Verified publication files:',len(files));print(friendly)
if __name__=='__main__':main()
