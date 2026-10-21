"""Preserve full scope after actual dispatcher integration/native gameplay tests."""
import json,hashlib,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,s):Path(p).write_text(json.dumps(s,indent=2)+'\n')
def main():
 now=datetime.now(timezone.utc);out=V/'goal-continuation-handoffs'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);pointer=V/'goal-continuation-current.json';state=read(pointer);shutil.copy2(pointer,out/'previous-handoff.json')
 review=read(V/'native-actor-dispatch-reviewed-current.json');c=read(V/'interior-C-processors-reviewed-current.json');index=read(V/'current-model-work-index-v4-current.json')
 ui=dict(status='terminal_native_Chat_inspection_timed_out_without_verified_interaction',directory=str(out),tool='mcp__cua_repl.js',action="cua.getApp('LM Studio') after rewriteDocumentation",observed_error='Sky Computer Use request timed out',tool_elapsed_seconds=120.6121,screen_lock_state_verified=False,app_restart_performed=False,native_Chat_verified=False,model_predictions=0,SDK_working=True,user_unlock_requested=False)
 save(out/'native-Chat-attempt.json',ui);save(V/'native-Chat-timeout-retry-current.json',ui)
 checks=[]
 for label,pids in [('completed18888C',[35110,35120]),('completed19460native',[38876,38881])]:
  for pid in pids:
   p=subprocess.run(['ps','-p',str(pid),'-o','pid=,etime=,command='],capture_output=True,text=True);checks.append(dict(label=label,pid=pid,present_now=p.returncode==0,observed=p.stdout.strip()))
 # These are terminal proof conclusions, not absence-derived results.
 assert c['status']=='terminal_interior_C_processors_independently_reviewed_equal'
 assert review['status']=='terminal_native_actor_dispatch_component_and_two_routes_reviewed'
 notes=ROOT/'BIWN Latest Work.txt';shutil.copy2(notes,out/'previous-BIWN Latest Work.txt');text=notes.read_text();lines=text.splitlines();lines[1]=now.isoformat();text='\n'.join(lines)+'\n'
 start=text.index('C PROCESSORS:');end=text.index('\n\nENTRY POINTS:',start)
 text=text[:start]+('C PROCESSORS: all five named16872/17084/17812/18270/18888jobs are terminal/equal for their own identified modified discs. Exact18888job independently matches24996aligned unique consecutive frames in all8fields,79987200PCMbytes and full observerJSON. CPU/GPU/DSP/IRQownership/error gates pass under retained HLE/device/IRQline/ACK/vector/commit/prefetch/cost/blitter/OP services. This result does not apply to19460or resolve compiled-helper-vs-original-entry media differences. Report: '+c['report'])+text[end:]
 text=text.replace('I shows51saved prompt/transcript records','I shows52saved prompt/transcript records')
 extra=('\nEXPERIMENTAL BUILD —19460RESIDENT BYTES (published/default remain18888): original-ABI13AE0dispatcher572bytes; coordinator reference,856cases/all38sites at final163788,96startup; unchanged18888parent prefix/20480reserve/heap163DC0,1020free. Read-only oracle qualified856original+856compiled cases/two corruption controls. Actual candidate24983frames/control24996bothreturnoutdoors. Both dispatch13calls:12actor/1sprite,0exhaustedpools; full real child-entry/register/SR/stack/args and captured child-output/root-return contracts pass, no monitor/pending/task-stack errors. Candidate328private depth/454minimum task headroom, control194/606. Full-pool live path remains unexercised.\n\nMedia/state differ: fresh prefix24983has17515video differences and21146CPU,24972RAM,24518GPU,9112DSP,19197navigation,234locomotion,347button differences; PCMhash/length differ79945600vs79987200. New adapter256private-gap context ends200bytes belowrootSP, versus194maximum control descendant depth:6byte observed clearance estimate, not a general bound. Evaluate a larger gap and broader real helpers before default/published promotion. Whole3384byte source-owned actor-group component remains separate/uninserted.\n\nLOCAL DISPATCHER TRIAL:2actual local27Bpredictions, Author62.01s/Reviewer8.38s. Rawcompilefailsunusedvariable; deleting only that declaration for diagnosis still fails real-child SR4vs0. Other source findings includeXmask0200,wrongNZ2,full32D1comparison/high-wordloss. No localbodyadopted. One development SFTrepair example prepared;0optimizersteps/newweights. NativeChat inspection timedout120.61s with no verified interaction;SDKworks,lockstateunverified,no unlock request.\n\nDispatcher report: '+review['report']+'\n')
 text+=extra;notes.write_text(text);shutil.copy2(notes,out/'current-BIWN Latest Work.txt')
 old=read(V/'actor-source-group-integrity-current.json');hashes=dict(old['dependencies_sha256']);hashes.update(review['dependencies_sha256']);hashes.update(c['source_sha256'])
 extra_paths=[Path(__file__),out/'native-Chat-attempt.json',out/'current-BIWN Latest Work.txt',Path(review['directory'])/'protocol.json',Path(c['directory'])/'protocol.json',Path(index['directory'])/'manifest.json',Path(index['report']),Path(index['source_list_snapshot']),ROOT/'verification/actor-dispatch-terminal-MCP-check/response.json']
 for p in extra_paths:hashes[str(p)]=sha(p)
 def check(item):
  p,h=item
  try:return None if sha(p)==h else dict(path=p,error='hash changed')
  except OSError as error:return dict(path=p,error=str(error))
 with ThreadPoolExecutor(max_workers=4)as pool:issues=[x for x in pool.map(check,hashes.items())if x]
 integrity=dict(status='terminal_actor_dispatch_and_inherited_evidence_integrity_pass'if not issues else'terminal_integrity_failed',directory=str(out),unique_bound_files=len(hashes),issues=issues,dependencies_sha256=hashes,scope='File integrity only; preserve full-game, model,UI,migration limitations.')
 save(out/'integrity.json',integrity);save(V/'actor-dispatch-turn-integrity-current.json',integrity);assert not issues,issues
 state.update(status='active_19460_dispatcher_live_verified_gap_and_media_work_pending',recorded_at=now.isoformat(),prior_state_archive=str(out/'previous-handoff.json'),goal_complete=False,
  previous_turn_classification='Progress: reproducible3384byte coupled source group,2596cases/retained-native replays, one local repair study, unchanged raw failures and coordinator corrections;51saved records. Exact18888C route was confirmed live.',
  this_turn_classification='Progress: complete original-ABI13AE0C dispatcher and adapter;856cases/38sites, no-op and wrong-X rejection, final-address component and96startup gates. New19460disc plus8byte-entry-restored control each complete real merchant/media/outdoor route;13dispatches/12actor/1sprite all ABI/return/task-stack contracts pass. Candidate24983vscontrol24996; video/audio/state differences persist.256gap has only6byte observed clearance estimate against control descendant stack depth, so remain experimental. Exact18888C job now independently matches24996frames/all8fields/fullPCM/fullobserver with ownership/error checks. New local trial2predictions fails compile and diagnostic nativeSR; coordinator body used; one SFTexample prepared/no weights.52saved prompt records; native UIgetApp timedout120.61s/no newChat proof. Integrity verified.',
  latest_built_disc_resident_bytes=19460,latest_published_live_build_resident_bytes=18888,
  latest_actor_dispatch_build=str(V/'native-actor-dispatch-disc-build-current.json'),latest_actor_dispatch_review=str(V/'native-actor-dispatch-reviewed-current.json'),latest_actor_dispatch_training_example=str(V/'actor-dispatch-repair-example-current.json'),latest_interior_C_live_review=str(V/'interior-C-processors-reviewed-current.json'),latest_native_UI_attempt=str(out/'native-Chat-attempt.json'),latest_integrity=str(out/'integrity.json'),final_integrity_unique_files=len(hashes),finite_jobs=[],finite_jobs_pending=0,completed_process_observations=checks,completed_current_turn_sessions=[29102,32085,54492,25216,85329,86548,19237],
  local_model_work_this_continuation=dict(predictions=2,model='advertising-scholar27Bbase',roles=['Author','same-weight Reviewer'],raw_compile_pass=False,compile_only_diagnostic_semantic_pass=False,selected_body='Coordinatorreference',new_training=False,prepared_SFT_examples=1,optimizer_steps=0,current_native_Chat_verified=False),
  next_actions=[
   'Before promoting19460, measure/increase actor-dispatch private capture gap. Current256places contextSP-272..SP-200; control descendants reached194belowroot, only6estimatedclearance. Make new versioned shim/Makefile/header/checker inputs (preserve bound as-run files), consider320gap (+64private stack, expected392depth/390headroom), run appropriate component/final-address/startup and real-child monitor/gameplay checks. Do not assume broader helper depth bounded by13calls.',
   'Retain current candidate24983/control24996fresh-pair video/PCM/state/navigation differences and old scanner media discrepancies. Newdispatcher functional route/ABI pass is not cycle or media equivalence. Fullpool actual gameplay remains unexercised.19460is built/live but not current published/default18888.',
   'Continue full game source reconstruction: remaining134DC/137E0native interfaces/actualexternalhelpers or all callers need porting for the separate3384source-owned group. Do not substitute entire emulator reconstruction or ever-increasing instruction counts for readable game work.',
   'All five namedCjobs are now terminal/equal only on16872/17084/17812/18270/18888identified discs. Exact18888review independently checks alignedframes8fields/PCM/fullobserver/backendcounts; no19460strict-Cjob has been launched. CurrentMCPv7already reports all five terminal throughactualconfigured bridge, latestpublished18888applicabilitytrueonlyfor18888.',
   'Ishows52saved prompt records, not52newpredictions. NewlocalAuthor rawcompilefails; one-line compile-onlydiagnostic stillfailsSR4vs0, sourceD1/X/NZbugsretained. One repair trainingexample is development-exposed, not heldout or trained. Do not promote model for these failed trials.',
   'NativeChatgetApp timedout120.61seconds afterdocumentationrefresh; no restart or currentUIgenerationverified, no lockstateclaim or unlockrequest. Do not repeat identicaltimeoutactions. SDK/CLIworks; historicalnative roles remainseparate.',
   'Advertising optionalstep8loadable/noobservedtransfergain remains; game native-repair-v3completed64updates/step32selectedbutunpromoted source failures. Preserve fullgoal: easyfrontend/roles/domaintrainingquality,fullreadableoriginal-consolegame and complete migration/future256GBpreparation. Fullworkbenchrelocation/hardwarestillunverified.'
  ],no_completion_claim=True,handoff_script_sha256=sha(Path(__file__)))
 state['current_entrypoints']['prompts_I']='52saved prompt/transcript records; no nativeChatstream claim'
 state['full_goal_requirements'][1]['additional_original_ABI_evidence']=review['report']
 state['full_goal_requirements'][1]['remaining']='19460experimental original-ABI13AE0build/live contract passes13calls, but private-gap broader safety and timing/media differences remain; fullgroup3348/3384sourceCABI stillnotintegrated, remainingreadablegame/original-console reconstruction unfinished.18888strict-C comparison now complete; appliesonlyto18888.'
 # Correct numerical typo in the descriptive field immediately, without touching any bound receipt.
 state['full_goal_requirements'][1]['remaining']=state['full_goal_requirements'][1]['remaining'].replace('fullgroup3348/3384','fullgroup3384')
 save(out/'protocol.json',state);save(pointer,state)
 with(ROOT/'runs/agent-work-audit.jsonl').open('a')as stream:stream.write(json.dumps(dict(recorded_at=now.isoformat(),event='original_ABI_dispatcher_real_gameplay_and18888_C_completion',coordinator='Nativeinterface/body/fixtures/monitor/layout/build/review; no rawlocalacceptance',local_roles='Author and same-weightReviewer',actual_local_predictions=2,new_training=False,prepared_SFT_examples=1,source_report=review['report'],processor_report=c['report'],candidate_frames=24983,control_frames=24996,live_dispatcher_calls=13,default_promoted=False,published_resident18888=True,bound_files_verified=len(hashes),goal_complete=False))+'\n')
 print(json.dumps(dict(status=state['status'],bound_files=len(hashes),pending_jobs=0,published=18888,experimental_built=19460,goal_complete=False)))

if __name__=='__main__':main()
