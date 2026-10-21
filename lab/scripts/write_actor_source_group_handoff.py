"""Preserve full goal and publish the new source component with actual job state."""
import json,shutil,hashlib,subprocess
from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def main():
 now=datetime.now(timezone.utc);out=V/'goal-continuation-handoffs'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 pointer=V/'goal-continuation-current.json';state=read(pointer);shutil.copy2(pointer,out/'previous-handoff.json')
 review=read(V/'actor-source-group-reviewed-current.json');pub=read(V/'actor-group-source-publication-current.json');job=read(V/'interior-C-processors-route-active.json');progress=read(Path(job['directory'])/'C/status.json');viewer=read(V/'current-model-work-index-v4-current.json');checks=[]
 for key,expected in [('pid','run_biwn_interior_C_processors_route.py'),('child_pid',str(Path(job['directory'])/'probe.py'))]:
  proc=subprocess.run(['ps','-p',str(job[key]),'-o','pid=,etime=,%cpu=,command='],capture_output=True,text=True);checks.append(dict(pid=job[key],kind=key,live_now=proc.returncode==0 and expected in proc.stdout,observed_command=proc.stdout.strip()))
 notes=ROOT/'BIWN Latest Work.txt';shutil.copy2(notes,out/notes.name);text=notes.read_text();text=text.replace('2026-10-19T07:27:17.119353+00:00',now.isoformat()).replace('last recorded frame 4321','last recorded frame '+str(progress['latest']['frame'])).replace('I shows48saved prompt/transcript records (not48new predictions).','I shows'+str(viewer['saved_prompt_or_transcript_records'])+'saved prompt/transcript records (not that many new predictions).')
 start=text.index('NEXT SOURCE GROUP:');end=text.index('\n\nLive report:',start)
 text=text[:start]+('NEXT SOURCE GROUP: all five actor/sprite source bodies now compile together with internal calls closed. Coordinator-corrected source component3384bytes/max248private stack, all2596coupled cases/469original sites pass and all2596retained-native-CPU replays pass; five source-API error propagation cases pass. The generic native bridge was4596bytes/512stack. Four external helpers remain prescribed. A clean canonical Makefile rebuild matches the tested binary SHA. No new logical function recovery is counted.\n\nLOCAL MODEL STUDY: five actual predictions in this actor study: Author/Reviewer, one repair/Reviewer, then exact-first-difference diagnostic Reviewer. Raw first draft failed66getter compile errors; raw repair compiled but failed its first runtime case with an incorrect decoder destination argument. Same-weight Reviewer missed it; exact trace feedback later elicited duplicate partial diagnoses. The published derivative includes coordinator fixes for three exhausted-pool loops, decoder argument storage/indexing and eight status-propagation sites. Raw local outputs were not accepted. No training/new weights/native Chat verification.\n\nNOT DISC-INTEGRATED: current source-owned C ABI does not reproduce original volatile-register/SR ABI or real external helpers.3384bytes exceeds1592free; measured4032additional staging bytes are only a layout option, not adopted. Need adapters/all callers, layout, real helper stack depth, heap/resource/task/startup/live validation. Full readable game/original-console reconstruction, broader paths, timing/media limits, Advertising reliability and complete migration remain unfinished.\n\nSource group report: '+review['report'])+text[end:];notes.write_text(text)
 # Previous manifests bind immutable snapshots, including previous notes/config.
 old=read(V/'interior-live-turn-integrity-current.json');hashes=dict(old['dependencies_sha256']);hashes.update(review['source_sha256'])
 extra=[Path(__file__),notes,V/'actor-source-group-reviewed-current.json',V/'actor-group-source-publication-current.json',V/'current-model-work-index-v4-current.json',Path(viewer['directory'])/'manifest.json',Path(viewer['report']),Path(viewer['source_list_snapshot'])]
 for p in extra:
  if p in [notes]:
   target=out/('current-'+p.name);shutil.copy2(p,target);hashes[str(target)]=sha(target)
  else:hashes[str(p)]=sha(p)
 def check(item):
  p,h=item
  try:return None if sha(p)==h else dict(path=p,error='hash changed')
  except OSError as e:return dict(path=p,error=str(e))
 with ThreadPoolExecutor(max_workers=4)as pool:issues=[x for x in pool.map(check,hashes.items())if x]
 integrity=dict(status='terminal_actor_group_and_inherited_bound_files_verified'if not issues else'terminal_actor_group_integrity_failed',directory=str(out),unique_bound_files=len(hashes),issues=issues,dependencies_sha256=hashes,scope='Checks retained405file proof plus source-group/publication/transcripts/current-note snapshot. This is file integrity, not full-game completion.')
 save(out/'integrity.json',integrity);save(V/'actor-source-group-integrity-current.json',integrity);assert not issues,issues
 state.update(status='active_actor_source_group_reproducible_original_ABI_and_full_game_pending',recorded_at=now.isoformat(),prior_state_archive=str(out/'previous-handoff.json'),goal_complete=False,
  previous_turn_classification='Progress: source-owned coupled reference linked/checked, first local Author/Reviewer completed and one repair started. Current continuation revalidated live repair and exact-disc route handles before taking the next source action.',
  this_turn_classification='Progress: raw repair compile passed but first execution case failed; retained that failure. Coordinator derivative fixes pool exhaustion, decoder argument storage/index and status propagation.2596coupled cases/469sites plus2596retained-native CPU replays pass at3384bytes/248private stack; five source API errors pass. Canonical source and clean exact-binary rebuild published. One diagnostic local Reviewer prediction received actual first trace difference; same-weight output is duplicated/partially inaccurate. Actor study total5predictions, no raw acceptance/training/nativeChat/disc replacement. Prompt viewer51saved records; inherited/new proof file integrity checked. Exact18888C route remains live.',
  latest_actor_source_group=str(V/'actor-source-group-reviewed-current.json'),latest_actor_source_publication=str(V/'actor-group-source-publication-current.json'),latest_integrity=str(out/'integrity.json'),final_integrity_unique_files=len(hashes),
  finite_jobs=[dict(status=job['status'],exec_session=19237,terminal=job['status'].startswith('terminal_'),tested_resident_bytes=18888,protocol=str(Path(job['directory'])/'protocol.json'),reference=job['reference'],actual_process_checks=checks,last_recorded_frame=progress['latest']['frame'])],finite_jobs_pending=int(any(c['live_now']for c in checks)),
  completed_current_turn_sessions=[93845,32535,72414,41640,66696,46860],
  local_model_work_this_continuation=dict(actor_study_total_predictions=5,original_Author_Reviewer=2,one_repair_Author_Reviewer=2,diagnostic_Reviewer=1,local_model='advertising-scholar27Bbase',sequential_same_weight_roles=True,independent_review=False,raw_model_accepted=False,coordinator_corrected=True,new_training=False,current_native_Chat_verified=False),
  next_actions=[
   'Continue actual game source reconstruction: adapt the five-member source group to original calling interfaces or port all callers. Inspect original finalD1/A0/A1/SR and external helper clobber/stack behavior, using existing factory CPU source only as data/reference. Do not substitute another entire emulator-reconstruction task for game decompilation.',
   'Resolve memory layout deliberately: current18888payload has1592spare, group3384before original-ABI adapters. Prior staging measurements allow a potential4032increase, but no layout change is adopted. Validate heap/loader dependencies and real task stack plus heap/resource/task/startup/gameplay if changed.',
   'Poll exact18888C route session19237/actual35110and35120; do not restart for observation timeout. When terminal independently compare full aligned frame IDs/all8fields/PCM/backend counters/observer equality and use distinct native-interior-C-processors report path.',
   'Broaden actor failure and sprite success/non-skipped live paths. Current published18888native route covers14actor successes and1sprite skipped failure; current video/state/navigation and older scanner media differences persist.',
   'Raw local whole-group trials failed; coordinator derivative passes. Future Reviewer requests should include compact exact first trace difference rather than generic failure log. Do not treat same-weight text review as proof. I has51saved records, not51new predictions.',
   'Current native Chat is unverified after stale controls; historical native3roles exist. Do not ask another unlock/repeat identical UI actions. SDK/CLI inference remains working. Advertising optional step8ready/no observed transfer gain and39file model inventory remain; broader reliability/full-workbench relocation/future hardware still unverified.'
  ],no_completion_claim=True,handoff_script_sha256=sha(Path(__file__)))
 state['current_entrypoints']['prompts_I']=str(viewer['saved_prompt_or_transcript_records'])+'saved prompt/transcript records; not a new-prediction count'
 state['full_goal_requirements'][1]['additional_source_component_evidence']=review['report']
 state['full_goal_requirements'][1]['remaining']='Full readable game/same-console rebuild remains unfinished. New five-member source component is target-built/reproducible but lacks original-facing ABI/layout/real-helper integration. Published18888live build and exact-disc C route are distinct; broader paths/current/inherited media/state differences remain.'
 save(out/'protocol.json',state);save(pointer,state)
 with(ROOT/'runs/agent-work-audit.jsonl').open('a')as f:f.write(json.dumps(dict(recorded_at=now.isoformat(),event='actor_source_group_native_component_and_local_model_study',coordinator_role='C API/fixtures/native replay/explicit derivative fixes/reproducible build/publication',local_roles='Sequential27BAuthor/Reviewer; one repair; feedback-fed diagnosticReviewer',actor_study_total_predictions=5,new_training=False,raw_model_accepted=False,disc_integrated=False,report=review['report'],source=pub['source'],bound_files_verified=len(hashes),goal_complete=False,live_route=state['finite_jobs'][0]))+'\n')
 print(json.dumps(dict(status=state['status'],verified_files=len(hashes),frame=progress['latest']['frame'],processes=[(c['pid'],c['live_now'])for c in checks],goal_complete=False)))

if __name__=='__main__':main()
