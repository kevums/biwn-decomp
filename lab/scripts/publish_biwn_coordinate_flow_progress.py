"""Publish the checked continuation layer without claiming live scheduling."""
from datetime import datetime,timezone
import hashlib,json,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];RUNTIME=Path.home()/'.lmstudio/local-ai-lab'
def sha(path):
 with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(path,value):Path(path).write_text(json.dumps(value,indent=2)+'\n')
def main():
 now=datetime.now(timezone.utc).isoformat();out=ROOT/'verification/coordinate-flow-progress-evidence'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 names=['coordinate-flow-current.json','coordinate-task-controls-flow-current.json','coordinate-services-current.json',
        'coordinate-flow-installed-MCP-current.json','coordinate-flow-menu-current.json','local-coordinate-flow-review-current.json','game-preset-provider-scope-current.json']
 paths={name:ROOT/'verification'/name for name in names};proofs={name:json.loads(path.read_text())for name,path in paths.items()}
 flow=proofs[names[0]];linked=proofs[names[1]];service=proofs[names[2]];menu=proofs[names[4]];review=proofs[names[5]]
 for proof in [flow,linked]:
  for key in ['source','library']:assert sha(proof[key])==proof[key+'_sha256']
 assert sha(flow['header'])==flow['header_sha256']
 for path,digest in linked['sources_sha256'].items():assert sha(path)==digest,path
 assert flow['cases']==147 and linked['cases']==2086 and linked['native_cases']==18 and service['cases']==31
 assert linked['flow_driver_statistics']==dict(started=45,requests=5067,external_requests=34,completed=38)
 assert menu['exit_code']==0
 turn=menu['turn'];answer=turn['answer'];word_count=len(answer.split())
 accepted=not turn['quality_flags'] and word_count<120 and '0xdf60' in answer.lower() and '0x20f78' in answer.lower()
 # Final source review, separate from same-model mechanical revisions.
 menu.update(status='terminal_source_review_pass'if accepted else'terminal_output_quality_rejected',
  word_count=word_count,source_review_actor='Codex coordinator',source_review=dict(
   original_and_native_code_proof_separate_from_model_review=True,
   readable_flow_does_not_switch_Jaguar_tasks=True,source_fields_for_helpers_are_component_fixtures=True,
   final_answer_accepted=accepted,same_model_revision_not_independent=True,
   wording_clarification='One completion/request means an upper bound per advance: poll/terminal calls may accept or emit none, as the API header specifies.',
   source_scope='Engine/request semantics and authorship checked against current C/proofs. Full-controls test driver synchronous; actual scheduling/live CPU private ABI/time not verified.'))
 save(paths[names[4]],menu);save(Path(menu['directory'])/'source-review.json',menu['source_review'])
 review.update(status='terminal_advisory_review_qualified',coordinator_source_review=dict(
  overclaim_rejected_correctly=True,private_ABI_timing_and_sync_driver_limits_identified=True,
  literal_field_name_correction='linked_controls has actual_Jaguar_context_switch, not actual_Jaguar_task_context_switch; both relevant booleans are false.',
  raw_review_retained=True,code_acceptance_depended_on_execution_comparison=True))
 save(paths[names[5]],review)
 helper=subprocess.run([sys.executable,str(ROOT/'scripts/native_chat_team_context.py')],input=json.dumps(dict(domain='game',query=menu['question']))+'\n',capture_output=True,text=True)
 assert helper.returncode==0,helper.stderr
 ready=json.loads(helper.stdout);assert ready['status']=='ready'and len(ready['roles'])==3
 assert ready['evidence']['resumable_coordinate_flow']['actual_Jaguar_task_context_switch'] is False
 save(out/'native-helper-ready.json',ready)
 pins={}
 for name in ['interactive-preview-recipe.json','outdoor-restoration-preview-recipe.json']:
  recipe=json.loads((ROOT/'verification'/name).read_text())
  for path,digest in recipe['hashes'].items():assert sha(path)==digest,path
  pins[name]=dict(files=len(recipe['hashes']),all_hashes_match=True)
 models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],text=True))
 assert len(models)==1 and models[0]['status']=='idle'and models[0]['queued']==0
 section=f'''RESUMABLE COORDINATE CONTINUATION
The coordinator added a request/completion C engine for the complete logical18E92..190B8 coordinate routine. Each advance accepts at most one completion and emits at most one request; no bus callbacks, internal polling loop, recursion, allocation or hidden global state run inside the engine. The host may leave a request pending while other work proceeds. A unique context/sequence pair identifies each operation; repeated polls do not perform effects or advance state. The host must execute/cache each request once and acknowledge actual completion. Copied state retains the continuation.
All147original comparisons pass:77standalone and70real-digit-connected, with23selected native cases per lane and all166original caller locations represented. Trace/RAM/fullD0 and earlier fixture hashes match. There are123protocol/error guards and59,592completed repoll checks, not a current queue count. A frozen clock produced283clock-read requests over300finite host steps, then resumed when supplied time advanced. In two separate logical bus worlds, one context deferredDF60for50host quanta while the other finished. This is host round-robin proof, not Jaguar scheduling.
The readable service adapter links real panel/text, raw controller poll, digits, task pause/resume and room/texture/object/allocator cleanup. The linked path passes2,086original/C comparisons and18native CPU/blitter cases/2,147commands. Counters show45started flows,38completed and seven intentionally failed error cases, covering5,067requests and34external requests. That compatibility test driver deliberately services requests synchronously. Separate31service guards show EXTERNAL returns without executing a helper or changing output; callbacks forward their real context and failures retain the output contract. Helpers themselves are bounded synchronous C bodies.
DF60task switching and20F78scene setup/streaming remain external requests. Real scheduler/scene continuations, CPU private frame/other registers/CCR, cycle timing and live source-frame replacement are not verified. The live previews remain on their earlier instruction-compatible runtime. No new local-model source or weight training this turn; earlier guided task-gate C is reused.
Source: {flow['source']}
Protocol proof: {paths[names[0]]}
Linked proof: {paths[names[1]]}
\n'''
 path=ROOT/'CURRENT DECOMPILATION.txt';lines=path.read_text().splitlines();lines[1]='Updated '+now
 path.write_text('\n'.join(lines[:3])+'\n'+section+'\n'.join(lines[3:])+'\n');shutil.copy2(path,RUNTIME/path.name)
 inference=f'''LATEST CONTINUATION OUTPUT TEST
Actual installed menu1: {turn['seconds']}seconds, {turn['rounds']}generation(s), {word_count}words. Source-reviewed acceptance: {accepted}. This is a headless Terminal/SDK test, not native Chat rendering. Exact question: {menu['question']}
Final raw answer: {answer}
Earlier samples are preserved: overlong answers, native cases mislabeled as tasks, completed repoll counts called pending, and supplied component fixtures called emulator helpers. A saved Game Assistant prompt sentence overgeneralized provider provenance. It is corrected in the active saved preset and four exported copies, preserving old sessions/prompts. Native UI cache reload remains unverified. Brief continuation queries now receive a smaller typed evidence projection; word-limit review uses one fresh focused context on the same weights. No independent reviewer or new training is implied. If the final answer is rejected above, it must not be advertised as a passing easy-inference result.
Local Reviewer:14.51seconds, advisory conclusion correctly rejected real-Jaguar/live replacement without ABI/timing work. It misstated one literal key name in its citation; coordinator qualification is saved and raw text unchanged. Source acceptance comes from original/native comparisons, not this same-weight model review.
Proof: {paths[names[4]]}
Reviewer prompts/response: {Path(review['directory'])/'prompts-and-responses.txt'}
\n'''
 path=ROOT/'CURRENT LOCAL INFERENCE.txt';lines=path.read_text().splitlines();lines[1]='Updated '+now
 path.write_text('\n'.join(lines[:3])+'\n'+inference+'EARLIER VERIFIED WORKFLOW\n'+'\n'.join(lines[3:])+'\n');shutil.copy2(path,RUNTIME/path.name)
 for name,path in paths.items():shutil.copy2(path,out/name);shutil.copy2(path,RUNTIME/'verification'/name)
 for path in [ROOT/'chat_tools.py',ROOT/'assistant_chat.py',ROOT/'scripts/native_chat_team_context.py',ROOT/'scripts/check_biwn_coordinate_flow.py',ROOT/'scripts/check_biwn_coordinate_task_controls.py',ROOT/'scripts/check_biwn_coordinate_services.py']:
  shutil.copy2(path,out/path.name)
 ledger_path=ROOT/'verification/goal-continuation-current.json';ledger=json.loads(ledger_path.read_text());shutil.copy2(ledger_path,out/'previous-goal-continuation.json')
 ledger.update(status='concrete_progress_goal_incomplete',recorded_at=now,
  previous_turn_classification='progress: guided local task pause/resume accepted unchanged and three fixture services removed from readable controls,2086original/18native cases plus installed evidence/menu/source review published',
  this_turn_classification='progress: coordinator resumable coordinate engine and service adapter;147original/46native cases,123guards/59592repolls/state copies/frozen clock/interleaved isolated contexts; real readable services linked through2086controls/18native/2147blitter cases and31service guards. Fresh MCP/native-helper evidence; localReviewer advisory qualified; saved preset provider-provenance instruction repaired and brief evidence/fresh-context word-limit review added. Live game scheduling remains unverified.',
  latest_coordinate_flow=str(paths[names[0]]),latest_coordinate_flow_controls=str(paths[names[1]]),latest_coordinate_service_guards=str(paths[names[2]]),
  latest_coordinate_local_inference=str(paths[names[4]]),latest_coordinate_MCP=str(paths[names[3]]),latest_preset_scope_repair=str(paths[names[6]]),
  latest_evidence_snapshot=str(out),goal_complete=False,live_processes=[],preview_pin_checks=pins,
  live_process_observation=dict(observed_at=now,finite_compute_jobs_running=False,model=models),
  native_UI_observation='No new UI call; earlier CUA timeout leaves lock state unknown. New engine/services, Reviewer request and menu tests are headless. Existing genuine native game Chat remains separate.',
  next_actions=[
   'All engine/service/linkage/Reviewer/menu jobs are terminal and daily27Bmodel is idle. Do not poll/restart closed sessions67331/20685/46205/21102/90228/98075/17480/99130/61270. Failed first flow-linkage run was only a stats assertion that incorrectly expected deliberate callback-failure flows to complete; source comparisons had passed, no game source fix.',
   'Connect pendingDF60 to an actual scheduler continuation with task identity and caller frame preservation; resume the owning flow after other game work. Existing readable scheduler and task-loop APIs remain available but the new two-world test is not that integration.',
   'Connect the existing readable20F78scene-stream body and its CD/GPU/device completion dependencies to flow service requests; completion must mean finished work. Preserve source bus/frame behavior and existing P/O capability.',
   'Continue full game/branch coverage, maintainable engine reconstruction, runtime-provider removal, uninterrupted combined-profile route, performance and standalone build. New nonblocking API is one necessary layer, not goal completion or a decompilation percentage.',
   'Keep Advertising preferred base+retrieval; V6/V7quality-rejected. Broaden source-grounded research/teaching tasks and objective/data review before further training, rather than repeat unchanged smallSFT.',
   'When native UI becomes available, verify new preset adoption, Advertising rendering and pluginstats/title/cancel. Do not request unlock; new headless Reviewer/menu records are not fabricated native Chat.'
  ])
 save(ledger_path,ledger);shutil.copy2(ledger_path,RUNTIME/'verification'/ledger_path.name)
 audit=dict(recorded_at=now,actor='Codex coordinator',action='Implemented callback-free coordinate continuation and readable service adapter; original/native/protocol/service/linkage checks; repaired saved game-preset provider scope and focused word-limit review',
  local_roles=['Reviewer advisory'],new_local_model_source=False,new_training=False,original_and_native_flow_cases=[147,46],protocol_guards=123,completed_repoll_checks=59592,
  linked_controls_cases=2086,native_linkage_cases=18,service_guards=31,actual_Jaguar_task_context_switch=False,live_frame_runtime_changed=False,
  reviewer_seconds=14.51,reviewer_raw_retained=True,menu_final_accepted=accepted,menu_seconds=turn['seconds'],menu_generations=turn['rounds'],native_Chat_this_turn=False,
  proof=str(paths[names[0]]),prompts=str(Path(review['directory'])/'prompts-and-responses.txt'))
 with(ROOT/'runs/agent-work-audit.jsonl').open('a')as stream:stream.write(json.dumps(audit)+'\n')
 report=dict(status='coordinate_flow_progress_published',recorded_at=now,directory=str(out),menu_final_accepted=accepted,menu_words=word_count,
  menu_seconds=turn['seconds'],menu_generations=turn['rounds'],preview_pins=pins,whole_goal_complete=False,
  files_sha256={str(path):sha(path)for path in paths.values()})
 save(out/'report.json',report);save(ROOT/'verification/coordinate-flow-progress-publication-current.json',report)
 print(json.dumps(dict(status=report['status'],directory=str(out),menu_accepted=accepted,menu_words=word_count,menu_seconds=turn['seconds'])),flush=True)
if __name__=='__main__':main()
