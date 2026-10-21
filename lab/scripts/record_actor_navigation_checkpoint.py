"""Refresh final RTS-inclusive proofs and retain both failed and successful inference."""
import collections,hashlib,json,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def main():
 now=datetime.now(timezone.utc).isoformat();unit=read(ROOT/'verification/biwn-actor-navigation-checks.json');linked=read(ROOT/'verification/biwn-actor-navigation-runtime-checks.json')
 assert unit['complete_function_RTS_executed']and unit['CPU_cases']==4096 and unit['CPU_instruction_coverage']==[209,209]and unit['host_guards']==15
 assert linked['cases']==128 and linked['task_handoffs']==3072 and linked['scripted_helpers']==['0x1a77c','0x13c9a']
 source=ROOT/'projects/black-ice-white-noise/restoration'
 names=['check_biwn_actor_navigation.py','check_biwn_actor_navigation_runtime.py','check_biwn_actor_task.py',
        'check_biwn_actor_task_runtime.py','check_biwn_render_display_runtime.py','check_biwn_actor_creation.py',
        'check_biwn_scene_loading.py','check_biwn_startup_services.py','check_biwn_boundary_handlers.py',
        'check_biwn_world_update.py','check_biwn_scheduler.py']
 for proof in [unit,linked]:
  out=Path(proof['directory']);assert read(out/'status.json')['status']=='terminal_pass'
  for name,digest in proof['source_sha256'].items():assert hashlib.sha256((source/name).read_bytes()).hexdigest()==digest
  snapshot=out/'harness-snapshot';snapshot.mkdir(exist_ok=True)
  files=[ROOT/'scripts'/n for n in names]+[source/n for n in set(proof['source_sha256'])|{'biwn_scheduler.h','biwn_world_update.h'}]+[ROOT/n for n in ['animation_renderer.py','inventory_renderer.py']]
  for path in files:shutil.copy2(path,snapshot/path.name)
  manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in files};save(snapshot/'manifest.json',manifest)
  for name,digest in manifest.items():assert hashlib.sha256((snapshot/name).read_bytes()).hexdigest()==digest
 rows=read(Path(linked['directory'])/'fixtures.json');linked['navigation_helper_return_comparisons']=dict(collections.Counter(hex(e['target'])for row in rows for e in row['rebuilt']['navigation_returns']))
 linked['navigation_helper_return_comparisons_total']=sum(linked['navigation_helper_return_comparisons'].values());assert linked['navigation_helper_return_comparisons_total']==1279
 linked['matched']=['Original CPU and translated C execute actor caller, four navigation helpers, two idle loops and real DF60/TRAP0/DE08/RTE. Complete CPU/SR/USP/SSP and all 2 MB RAM including private frames/public headers match without masks.',
                    '128 cases produce 1024 actor iterations and 3072 actual handoffs. All 1279 navigation return CPU states match: 708 waypoint, 307 left, 132 right and 132 forward.']
 linked['limits']=['Only RNG1A77C and movement13C9A remain scripted here. Movement field changes and geometry fixtures are external test inputs, not reconstructed physics or complete AI.',
                   'Separate from the 21-context startup, where actors remain blocked. Removal TRAP2, loading task switches, remaining callers, full world/render/lifecycles/scenes/audio/game/hardware remain unfinished. No original CPU/GPU/game frames execute on the C path.']
 save(ROOT/'verification/biwn-actor-navigation-runtime-checks.json',linked);save(Path(linked['directory'])/'report.json',linked)
 shutil.copy2(Path(unit['directory'])/'libactor-navigation.dylib',ROOT/'tools/libbiwn-actor-navigation.dylib')
 shutil.copy2(Path(linked['directory'])/'libactor-runtime.dylib',ROOT/'tools/libbiwn-actor-navigation-runtime.dylib')
 answers=read(ROOT/'verification/actor-navigation-checked-examples.json');unit_rows=read(Path(unit['directory'])/'fixtures.json');answers['checked_examples']=[unit_rows[4],unit_rows[8]]
 assert unit_rows[4]['CPU']['registers'][0]==0xaabb0001 and unit_rows[4]['CPU']['SR']==0x18
 assert unit_rows[8]['CPU']['registers'][0]==0xaabb0fe0
 save(ROOT/'verification/actor-navigation-checked-examples.json',answers)
 session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);validation=read(session/'boot-slice-validation.json');assert validation['portable_C_component_count']==100
 validation.update(actor_navigation_reconstruction=unit,actor_navigation_scheduler_integration=linked,latest_aggregate_update=now);save(session/'boot-slice-validation.json',validation)
 role_dir=Path(read(ROOT/'verification/actor-navigation-local-review-current.json')['directory']);roles=read(role_dir/'review.json')['rows']
 qdir=Path(read(ROOT/'verification/easy-actor-navigation-current.json')['directory']);protocol=read(qdir/'protocol.json');assert protocol['status']=='completed_pending_coordinator_review'
 question=protocol['questions'][0];calls=[b['toolCallRequest']for e in question['events']for b in e['content']if b['type']=='toolCallRequest']
 answer='\n'.join(b['text'].strip()for e in question['events']if e['role']=='assistant'for b in e['content']if b['type']=='text'and b['text'].strip())
 assert len(calls)==1 and calls[0]['arguments']=={'topic':'actor_navigation'}
 for text in ['0xAABB0001','0x0018','0xAABB0FE0','preserves','scripted']:assert text in answer
 assert len(answer.split())<=95
 audit=ROOT/'verification/actor-navigation-review'/Path(linked['directory']).name;audit.mkdir(parents=True)
 shutil.copy2(qdir/'protocol.json',audit/'ordinary-question.json');shutil.copy2(role_dir/'review.json',audit/'source-reading-roles.json')
 review={'recorded_at':now,'directory':str(audit),'source_reading_responses':[
  {'role':roles[0]['role'],'verdict':'rejected','reason':'D0, SR and final N/Z source are wrong. Only restored D2 is correct. The response claims no uncertainty despite errors.','response':roles[0]['text']},
  {'role':roles[1]['role'],'verdict':'rejected','reason':'ANDI.W preserves upper16bits. The answer wrongly says they clear, and omits LEA sign extension of the word index.','response':roles[1]['text']}],
  'ordinary_evidence_question':{'question':question['user'],'answer':answer,'verdict':'correct_bounded_sample','tool_calls':calls,'SDK_reported_seconds':question['SDK_reported_seconds']},
  'who_did_what':'Codex authored accepted C and comparison harnesses. Original CPU execution decides acceptance. Two sequential roles use the same local27Bbase; they are not independent verifiers. One fresh ordinary question used the installed evidence tool. No model weights were changed.',
  'scope':'Localhost API/SDK transcripts, separate from native Chat. Earlier source-reading mistakes are retained. Correct tool-grounded retrieval is not improved unaided reasoning, training, a general accuracy/speed benchmark or fullgame completion.',
  'ordinary_question_proof_version':'Question retrieved the preceding pre-RTS body proof. The final full-RTS proof was rerun afterward; checked numeric examples and helper/integration scope are unchanged.'}
 save(audit/'review.json',review);save(ROOT/'verification/actor-navigation-review.json',review)
 transcript='ACTOR NAVIGATION — EXACT PROMPTS AND RESPONSES\n\nWHO DID WHAT\n'+review['who_did_what']+'\n\n'
 for role in roles:transcript+='ROLE\n'+role['role']+'\nSYSTEM\n'+role['system']+'\nUSER\n'+role['prompt']+'\nRESPONSE (REJECTED)\n'+role['text']+'\n\n'
 transcript+='CPU-CHECKED CORRECTIONS\n'+answers['checked_waypoint_early_return']+'\n'+answers['checked_waypoint_word_arithmetic']+'\n\nORDINARY LOCAL QUESTION\nSYSTEM\n'+protocol['system']+'\nUSER\n'+question['user']+'\nTOOLS\n'+json.dumps(calls,indent=2)+'\nRESPONSE\n'+answer+'\n\nSCOPE\n'+review['scope']+'\n'+review['ordinary_question_proof_version']+'\n'
 (audit/'prompts-and-responses.txt').write_text(transcript);save(role_dir/'coordinator-review.json',review['source_reading_responses']);save(role_dir/'status.json',{'status':'terminal_rejected_source_responses','review':str(ROOT/'verification/actor-navigation-review.json')})
 models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True));assert len(models)==1 and models[0]['status']=='idle'and models[0]['queued']==0
 checkpoint={'recorded_at':now,'published_components':100,'processor_components':{'CPU':98,'GPU':2},'pending_actor_caller_components':1,
  'navigation_CPU_cases':4096,'navigation_instruction_coverage':[209,209],'navigation_host_guards':15,'standalone_RTS_executed':True,
  'integration_cases':128,'actor_iterations':1024,'scheduler_handoffs':3072,'navigation_return_CPU_comparisons':1279,
  'scripted_actor_helpers':2,'startup21_actor_bodies_executed':0,'removal_executed':False,'source_role_responses_rejected':2,
  'ordinary_question_correct':True,'ordinary_question_tools':1,'model_idle':True,'known_compute_jobs':'terminal',
  'native_UI':'Last CUA observation confirmed locked; no unlock requested. API/SDK separate from native Chat.',
  'new_training':False,'model_defaults_unchanged':True,'full_goal_status':'active incomplete',
  'next_work':'Replace RNG and movement service scripts, then integrate complete actor behavior with startup/world/render and implement remaining task/scene/graphics/audio work.'}
 save(ROOT/'verification/actor-navigation-checkpoint.json',checkpoint)
 for name in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']:
  path=ROOT/'verification'/name;value=read(path);value.update(actor_navigation_checkpoint=checkpoint,actor_navigation_review=review)
  if name=='current-runtime-state.json':value.update(recorded_at=now,models=models,local_inference_jobs='Terminal. Two source-reading replies rejected; one ordinary evidence question passed with one tool call.',emulator_jobs='Terminal. Navigation4096cases/209instructions/15guards and actor128cases/3072handoffs/1279helperreturnCPUs match.',latest_API_ease_review=str(ROOT/'verification/actor-navigation-review.json'))
  if name=='requirements-audit.json':value.update(recorded_at_utc=now,previous_goal_turn_classification='Progress: actor/two-idle real scheduler128cases and3072handoffs, fullCPU/RAM match.',this_goal_turn_classification='Progress: four real navigation helpers;4096CPUcases/all209instructions/15guards;1279helperreturnCPUs and3072handoffs match. Two local source answers rejected; one evidence-grounded ordinary answer correct.',next_safe_work=checkpoint['next_work'])
  save(path,value)
 note='\nACTOR NAVIGATION CHECKPOINT — '+now+'\n\n'+answers['checked_navigation_scope']+'\n\nFull standalone calls now execute RTS; all4096cases/all209instructions and15guards pass. Integration checks1279completehelperreturnCPUs,1024actoriterations and3072handoffs.\n\nLOCAL INFERENCE\nTwo ungrounded source responses were wrong and rejected. One ordinary evidence-grounded question returned all checked numeric results and the movement limitation correctly with one tool call in '+str(question['SDK_reported_seconds'])+' SDK seconds. This is one sample and no model training.\n\nEXACT PROMPTS/RESPONSES/WHO DID WHAT\n'+str(audit/'prompts-and-responses.txt')+'\n\nNEXT\n'+checkpoint['next_work']+'\nFull goal active and incomplete.\n'
 for name in ['POST REVIEW.txt','projects/black-ice-white-noise/restoration/READ ME.txt']:
  with(ROOT/name).open('a')as handle:handle.write(note)
 path=ROOT/'CURRENT DECOMPILATION.txt';text=path.read_text();text+='\nFINAL VERIFICATION\nStandalone calls include real original RTS and C return handling. The local evidence question returned correct values and movement limitations with one call. Exact rejected source answers and successful retrieval: '+str(audit/'prompts-and-responses.txt')+'\n';path.write_text(text)
 path=ROOT/'START HERE.txt';text=path.read_text();start=text.index('LOCAL INFERENCE RESULT\n');end=text.index('TRY ADVERTISING ASSISTANT\n',start);text=text[:start]+'LOCAL INFERENCE RESULT\nTwo local source-reading answers were wrong and rejected. One ordinary evidence-grounded waypoint question correctly returned the CPU-checked values with one tool call. Exact prompts and responses are in POST REVIEW.txt. Native Chat remains unverified while locked.\n\nTry: For the checked waypoint examples, what are the full D0/SR results, and is actor movement complete?\n\n'+text[end:];path.write_text(text)
 for name in ['summarize_biwn_checks.py','install_chat_runtime.py','check_actor_navigation_mcp.py']:subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts'/name)],check=True)
 print(json.dumps({'components':100,'CPU_cases':4096,'handoffs':3072,'return_CPU_comparisons':1279,'rejected_local_source_replies':2,'ordinary_evidence_question_correct':True,'SDK_seconds':question['SDK_reported_seconds'],'audit':str(audit)}))

if __name__=='__main__':main()
