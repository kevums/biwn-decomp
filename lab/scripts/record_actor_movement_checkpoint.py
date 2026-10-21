"""Freeze final wrap fixtures, partial movement/GPU linkage and ordinary inference audit."""
import hashlib,json,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def main():
 now=datetime.now(timezone.utc).isoformat();names=['biwn-actor-movement-boundary-checks.json','biwn-actor-direction-checks.json','biwn-actor-movement-direction-checks.json','biwn-movement-submit-cpu-checks.json','biwn-actor-movement-gpu-checks.json'];proofs={name:read(ROOT/'verification'/name)for name in names}
 caller,direction,connected,submit,gpu=proofs.values();assert caller['CPU_cases']==connected['CPU_cases']==2048 and caller['CPU_instruction_coverage']==connected['CPU_instruction_coverage']==[192,192]
 assert gpu['CPU_cases']==256 and gpu['CPU_instruction_coverage']==[192,192]and gpu['scripted_services']==['0x13b5a','0x13bb0']and not gpu['GPU_output_words_scripted']
 source=ROOT/'projects/black-ice-white-noise/restoration';scripts=['check_biwn_actor_movement.py','check_biwn_actor_direction.py','check_biwn_actor_movement_direction.py','check_biwn_movement_submit_cpu.py','check_biwn_actor_movement_gpu.py','check_biwn_rng_cpu.py','check_biwn_actor_navigation.py','check_biwn_actor_task.py','check_biwn_world_movement_pipeline.py','check_biwn_inventory_frame.py','check_unicorn_sr_observation.py']
 for proof in proofs.values():
  folder=Path(proof['directory']);assert read(folder/'status.json')['status']in['terminal_pass','terminal_pass_services_pending'];snapshot=folder/'harness-snapshot';snapshot.mkdir(exist_ok=True)
  for name,digest in proof['source_sha256'].items():assert hashlib.sha256((source/name).read_bytes()).hexdigest()==digest
  files=[ROOT/'scripts'/name for name in scripts]+[source/name for name in set(proof['source_sha256'])|{'biwn_scheduler.h','biwn_world_update.h','biwn_actor_task.h'}]
  for path in files:shutil.copy2(path,snapshot/path.name)
  manifest={path.name:hashlib.sha256(path.read_bytes()).hexdigest()for path in files};save(snapshot/'manifest.json',manifest)
  for name,digest in manifest.items():assert hashlib.sha256((snapshot/name).read_bytes()).hexdigest()==digest
 rows=read(Path(caller['directory'])/'fixtures.json');trace=rows[0]['trace'];obj=0x80000
 xwrites=[event[3]for event in trace if event[:3]==['write',obj+4,4]];zwrites=[event[3]for event in trace if event[:3]==['write',obj+10,4]]
 assert xwrites==[0x80000000,0x7fffffff]and zwrites==[0,0xffffffff]
 lowword=next(row for row in rows if any(e[0]=='call'and e[1]in[0x13b5a,0x13bb0]and row['parameters']['returns'][str(e[1])]==0x10000 for e in row['trace']))
 initial={a:(w,v)for a,w,v in lowword['parameters']['initial']};writes={e[1]:(e[2],e[3])for e in lowword['trace']if e[0]=='write'}
 for offset in [4,8,10,14,16,18]:assert writes[obj+offset]==initial[obj+offset]
 examples=read(ROOT/'verification/actor-movement-checked-examples.json');examples.update(explicit_32bit_wrap_example={'case':0,'scope':'Caller proof with explicit GPU integer fixture1, not a claim that the connected GPU produced this particular delta.','X_writes':[hex(x)for x in xwrites],'Z_writes':[hex(x)for x in zwrites],'original_CPU_C_bus_and_RAM_match':True},low_word_rollback_example={'case':lowword['case'],'full_collision_D0':'0x00010000','low_word':0,'all_six_position_fields_restored':True,'report':str(ROOT/'verification/biwn-actor-movement-boundary-checks.json')})
 examples['checked_rollback_answer']=examples['checked_rollback_answer'].replace('offsets4,8,10,14,16,18','decimal byte offsets 4, 8, 10, 14, 16, 18');save(ROOT/'verification/actor-movement-checked-examples.json',examples)
 session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);validation=read(session/'boot-slice-validation.json');assert validation['portable_C_component_count']==100
 validation.update(actor_movement_caller_reconstruction=caller,actor_direction_full_CPU=direction,actor_movement_direction_pipeline=connected,movement_submit_full_CPU=submit,actor_movement_GPU_pipeline=gpu,latest_aggregate_update=now);save(session/'boot-slice-validation.json',validation)
 shutil.copy2(Path(gpu['directory'])/'libactor-movement.dylib',ROOT/'tools/libbiwn-actor-movement-gpu.dylib')
 question_dir=Path(read(ROOT/'verification/easy-actor-movement-current.json')['directory']);protocol=read(question_dir/'protocol.json');assert protocol['status']=='completed_pending_coordinator_review';question=protocol['questions'][0]
 calls=[b['toolCallRequest']for e in question['events']for b in e['content']if b['type']=='toolCallRequest'];assert len(calls)==1 and calls[0]['arguments']=={'topic':'actor_movement'}
 answer='\n'.join(b['text'].strip()for e in question['events']if e['role']=='assistant'for b in e['content']if b['type']=='text'and b['text'].strip())
 for term in ['low 16 bits','restores X/Y/Z','retains','GPU matrix/fraction','still scripts','remain blocked']:assert term in answer
 assert len(answer.split())<=100
 models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True));assert len(models)==1 and models[0]['identifier']=='advertising-scholar'and models[0]['status']=='idle'and models[0]['queued']==0
 audit=ROOT/'verification/actor-movement-review'/Path(gpu['directory']).name;audit.mkdir(parents=True);shutil.copy2(question_dir/'protocol.json',audit/'ordinary-question.json')
 who=('Codex authored the movement caller, full CPU direction and GPU submission interfaces, and comparison harnesses. Original CPU/GPU execution decides acceptance. '
      'The existing reconstructed GPU4320 matrix algorithm is reused. No local-model code or independent agent votes were used this turn. '
      'The existing27Bbase answered one ordinary evidence question via LM Studio localhost SDK. Native Chat was confirmed locked; latest native adoption remains unverified. '
      'API logs are separate from native Chat. No new training or default-model promotion.')
 review={'recorded_at':now,'directory':str(audit),'status':'ordinary_movement_rollback_and_scope_answer_correct_one_call','question':question['user'],'answer':answer,'tool_calls':calls,'SDK_reported_seconds':question['SDK_reported_seconds'],'who_did_what':who,
         'scope':'One evidence-grounded sample, not general unaided accuracy/speed or native Chat verification. It used the preceding proof version; final explicit coordinate-wrap fixtures were added and rerun afterward with unchanged source/numeric scope.',
         'native_UI':'CUA confirmed locked this turn; no unlock requested.'}
 save(audit/'review.json',review);save(ROOT/'verification/actor-movement-review.json',review)
 transcript=('ACTOR MOVEMENT CHECKPOINT\n\nWHO DID WHAT\n'+who+'\n\nSYSTEM\n'+protocol['system']+'\n\nUSER\n'+question['user']+'\n\nTOOLS\n'+json.dumps(calls,indent=2)+'\n\nANSWER\n'+answer+
            '\n\nVERIFICATION\nMovement caller2048cases/all192instructions/17guards; direction2048cases/all61reachable of62instructions/13guards; movement+direction2048cases; GPU CPU submit128cases/all14instructions/14guards; computedGPU movement integration256cases/all192caller instructions. FullCPU/SR/privateRAM/RTS/bus compare.\n\n'
            'OBSERVATION ERROR AND CORRECTION\nFirst GPU-submit preflight matched allRAM/bus/CPUregisters butexpectedSR5 versusC4. Tiny reproduction showed directUnicornSRread commits staleC before laterMOVE.WSR,D7. Avoiding that earlyread givesSR4; GPU-submitCsource was unchanged. Corrected128case run passes. SourceinstructionE098isCMPI.L0,F03200, notTST; the earlier informal TST description was corrected by opcode inspection.\n\n'
            'FINAL FIXTURES\nExplicit32bit caller fixture updatesX7FFFFFFFto80000000 andZFFFFFFFFto0, then rolls them back. Unit/caller+direction/GPU-connected tests rerun after adding edge coordinates. No Csource behavior changed.\n\n'
            'LIMITS\nTwo collision helpers13B5A/13BB0 are scripts in this movement proof. Geometry and collision inputs are fixtures; synchronous GPU completion is a device model. The earlier actor/task-ring proof still scriptswhole13C9A. Actors remain blocked in21-contextstartup. Two caller components(actor/movement) remain pending; count100unchanged. Full goal active and incomplete.\n')
 (audit/'prompts-and-responses.txt').write_text(transcript);shutil.copy2(ROOT/'verification/unicorn-SR-read-side-effect.json',audit/'SR-observation-reproduction.json')
 evidence=['verification/'+name for name in names]+['verification/actor-movement-MCP-check.json','verification/actor-movement-review.json','verification/unicorn-SR-read-side-effect.json',str((audit/'prompts-and-responses.txt').relative_to(ROOT))]
 checkpoint={'recorded_at':now,'published_components':100,'processor_components':{'CPU':98,'GPU':2},'pending_actor_and_movement_caller_components':2,
  'movement_caller_CPU_cases':2048,'movement_caller_instruction_coverage':[192,192],'movement_caller_host_guards':17,'direction_CPU_cases':2048,'direction_reachable_instruction_coverage':[61,61],'direction_total_instructions':62,'direction_host_guards':13,
  'movement_with_direction_CPU_cases':2048,'GPU_submit_full_CPU_cases':128,'GPU_submit_instruction_coverage':[14,14],'GPU_submit_host_guards':14,'movement_with_GPU_cases':256,'movement_with_GPU_instruction_coverage':[192,192],
  'GPU_output_words_scripted':False,'movement_collision_scripts':['0x13b5a','0x13bb0'],'movement_linked_to_actor_task_test':False,'startup21_actor_bodies_executed':0,'removal_executed':False,
  'explicit_32bit_wrap_and_selective_rollback_checked':True,'SR_observation_error_reproduced_and_repaired':True,'ordinary_question_correct':True,'ordinary_question_tools':1,'model_idle':True,'known_compute_jobs':'terminal',
  'native_UI':'CUA confirmed locked this turn; no unlock requested. Existing native preset/MCP adoption unverified.','new_training':False,'model_defaults_unchanged':True,'full_goal_status':'active incomplete','evidence':evidence,
  'next_work':'Reconstruct13B5A/13BB0 actor collision helpers with full geometry effects; link movement into actor scheduling, then larger startup/world/render and remaining game systems.'}
 save(ROOT/'verification/actor-movement-checkpoint.json',checkpoint)
 for name in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']:
  path=ROOT/'verification'/name;value=read(path);value.update(actor_movement_checkpoint=checkpoint,actor_movement_review=review)
  if name=='current-runtime-state.json':value.update(recorded_at=now,models=models,local_inference_jobs='Terminal. One ordinary movement rollback/scope answer correct with one tool call; model idle.',emulator_jobs='Terminal. Movement2048caller anddirection2048cases; fullCPU GPUsubmit128cases; movement+realGPU256cases pass. Collision/task linkage unfinished.',latest_API_ease_review=str(ROOT/'verification/actor-movement-review.json'))
  if name=='requirements-audit.json':
   value.update(recorded_at_utc=now,previous_goal_turn_classification='Progress: fullCPU RNG6144cases andactor128cases/3072handoffs; movementonlyscriptedactorhelper.',this_goal_turn_classification='Progress: movementcaller2048cases/all192instructions, direction2048cases, GPUsubmit128cases and movement+GPU256cases match. Two collision scripts remain; task integration pending. One ordinary local answer correct withonecall. Count100unchanged.',next_safe_work=checkpoint['next_work'])
   for item in value['requirements']:
    if 'decompilation test'in item['requirement']:item['evidence']=list(dict.fromkeys(item['evidence']+evidence))
  save(path,value)
 progress=read(ROOT/'config.json')['actor_movement_progress'];note='\nACTOR MOVEMENT CHECKPOINT — '+now+'\n\n'+progress+'\n\nWHO DID WHAT\n'+who+'\n\nORDINARY LOCAL INFERENCE\nCorrect rollback/scope answer with one tool call in '+str(question['SDK_reported_seconds'])+' SDK seconds. Single sample, not a benchmark.\n\nEXACT PROMPTS/RESPONSES/ERROR CORRECTION\n'+str(audit/'prompts-and-responses.txt')+'\n\nNEXT\n'+checkpoint['next_work']+'\nFull goal active and incomplete.\n'
 for name in ['POST REVIEW.txt','projects/black-ice-white-noise/restoration/READ ME.txt']:
  with(ROOT/name).open('a')as handle:handle.write(note)
 path=ROOT/'CURRENT DECOMPILATION.txt';text=path.read_text();text+='\nLOCAL INFERENCE RESULT\nOne ordinary movement rollback/scope question answered correctly with one tool call in about20seconds. Exact prompts, response, test corrections and responsibilities: '+str(audit/'prompts-and-responses.txt')+'\n';path.write_text(text)
 path=ROOT/'START HERE.txt';text=path.read_text();start=text.index('LOCAL INFERENCE RESULT\n');end=text.index('TRY ADVERTISING ASSISTANT\n',start);path.write_text(text[:start]+'LOCAL INFERENCE RESULT\nThe current movement rollback/scope question answered correctly with one evidence call in about20seconds. Earlier source-reading failures remain rejected. Native Chat was locked; API/SDK logs are separate and native adoption remains unverified.\n\nTry: If collision returns0x00010000, what does movement roll back, and are actors running in startup?\n\n'+text[end:])
 for name in ['summarize_biwn_checks.py','install_chat_runtime.py','check_actor_movement_mcp.py']:subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts'/name)],check=True)
 print(json.dumps({'components':100,'movement_caller_cases':2048,'direction_cases':2048,'GPU_submit_cases':128,'movement_GPU_cases':256,'collision_scripts':2,'question_tools':1,'SDK_seconds':question['SDK_reported_seconds'],'audit':str(audit)}))

if __name__=='__main__':main()
