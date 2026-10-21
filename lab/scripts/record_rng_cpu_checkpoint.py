"""Record the full CPU RNG proof, single ordinary inference sample and remaining work."""
import hashlib,json,shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text())
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def main():
 now=datetime.now(timezone.utc).isoformat();unit=read(ROOT/'verification/biwn-rng-cpu-checks.json');linked=read(ROOT/'verification/biwn-actor-rng-runtime-checks.json')
 assert unit['CPU_cases']==6144 and unit['host_guards']==19 and unit['reachable_nonexception_instruction_coverage']==[120,120]
 assert linked['helper_return_CPU_comparisons_total']==2375 and linked['indexed_RNG_return_CPU_comparisons']==561 and linked['scripted_helpers']==['0x13c9a']
 for proof in [unit,linked]:
  folder=Path(proof['directory']);assert read(folder/'status.json')['status']=='terminal_pass'
  for name,digest in proof['source_sha256'].items():assert hashlib.sha256((ROOT/'projects/black-ice-white-noise/restoration'/name).read_bytes()).hexdigest()==digest
  for name,digest in read(folder/'harness-snapshot/manifest.json').items():assert hashlib.sha256((folder/'harness-snapshot'/name).read_bytes()).hexdigest()==digest
 mcp=read(ROOT/'verification/rng-cpu-MCP-check.json');assert mcp['status']=='fresh_installed_full_CPU_RNG_evidence_passed'
 question_dir=Path(read(ROOT/'verification/easy-rng-cpu-current.json')['directory']);protocol=read(question_dir/'protocol.json');assert protocol['status']=='completed_pending_coordinator_review'
 question=protocol['questions'][0];calls=[b['toolCallRequest']for e in question['events']for b in e['content']if b['type']=='toolCallRequest']
 answer='\n'.join(b['text'].strip()for e in question['events']if e['role']=='assistant'for b in e['content']if b['type']=='text'and b['text'].strip())
 assert len(calls)==1 and calls[0]['arguments']=={'topic':'rng'}
 for term in ['6,144','120','122','one','scripted','zero new components','100','did not finish']:assert term in answer
 assert len(answer.split())<=85
 models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],cwd=Path.home()/'.lmstudio',text=True));assert len(models)==1 and models[0]['identifier']=='advertising-scholar'and models[0]['status']=='idle'and models[0]['queued']==0
 audit=ROOT/'verification/rng-cpu-review'/Path(linked['directory']).name;audit.mkdir(parents=True)
 shutil.copy2(question_dir/'protocol.json',audit/'ordinary-question.json')
 who=('Codex authored the accepted full CPU RNG interface, original/C comparison and actor integration harness. The existing checked division and multiply algorithms are reused. '
      'Original M68000 execution decides C acceptance. No local-model code draft or independent agent vote was used this turn. '
      'The existing27Blocalbase answered one ordinary question using current evidence, via LM Studio localhost SDK. '
      'Native Chat was confirmed locked; latest preset/MCP adoption in that existing chat remains unverified. API logs are separate from native Chat history. '
      'No model training, weight changes or default promotion occurred.')
 review={'recorded_at':now,'directory':str(audit),'status':'ordinary_full_CPU_RNG_scope_answer_correct_one_call',
         'question':question['user'],'answer':answer,'tool_calls':calls,'SDK_reported_seconds':question['SDK_reported_seconds'],
         'who_did_what':who,'native_UI':'CUA confirmed locked this turn; no unlock requested.',
         'scope':'One correct evidence-grounded sample, not general unaided reasoning, accuracy, speed or native UI verification.'}
 save(audit/'review.json',review);save(ROOT/'verification/rng-cpu-review.json',review)
 transcript=('FULL CPU RNG CHECKPOINT\n\nWHO DID WHAT\n'+who+'\n\nSYSTEM\n'+protocol['system']+'\n\nUSER\n'+question['user']+
             '\n\nTOOLS\n'+json.dumps(calls,indent=2)+'\n\nANSWER\n'+answer+'\n\nCHECKS\n'
             '6144 original CPU cases;120/120 nonexception instructions outof122total;19host guards; fullCPU/SR/privateframes/RAM/accessorder andRTS. '
             'Zero-divisor original exception instructions E606/E608 are excluded; hostzeroerror preserves priorRAM effects andcallerCPU. '
             'Actor integration128cases,1024iterations,3072actualhandoffs,2375helperreturnCPUstates including561RNG returns. Onlymovement13C9Ais scripted.\n\n'
             'FAILURES AND CORRECTIONS\nThe first build failed -Werror for an unused static word helper. It was removed without behavior changes. '
             'The next64-case preflight passed, followed by6144cases. Four corrupt-return guards were then added and all6144cases/19guards rerun successfully. '
             'Previous local source-reading failures remain in the navigation audit; this successful retrieval does not erase or repair them.\n\n'
             'LIMITS\nMovement and geometry fields remain test inputs. Actors are still blocked in the21-context startup. Removal, loading task switches, completeAI/physics, '
             'remaining tasks/world/render/asset lifecycles/graphics/mainloop/scenes/audio/game/hardware are unfinished. Count100is unchanged because the RNG/math bodies were already counted.\n')
 (audit/'prompts-and-responses.txt').write_text(transcript)
 evidence=['verification/biwn-rng-cpu-checks.json','verification/biwn-actor-rng-runtime-checks.json','verification/rng-cpu-MCP-check.json','verification/rng-cpu-review.json',str((audit/'prompts-and-responses.txt').relative_to(ROOT))]
 checkpoint={'recorded_at':now,'published_components':100,'processor_components':{'CPU':98,'GPU':2},'new_components':0,
  'pending_actor_caller_components':1,'RNG_math_CPU_cases':6144,'CPU_instruction_coverage':[120,122],'nonexception_instruction_coverage':[120,120],
  'exception_only_instructions_excluded':['0xe606','0xe608'],'host_guards':19,'full_CPU_stack_banks_private_RAM_bus_and_RTS_match':True,
  'actor_integration_cases':128,'actor_iterations':1024,'scheduler_handoffs':3072,'helper_return_CPU_comparisons':2375,'indexed_RNG_return_CPU_comparisons':561,
  'scripted_actor_helpers':['0x13c9a'],'startup21_actor_bodies_executed':0,'removal_executed':False,'ordinary_question_correct':True,'ordinary_question_tools':1,
  'model_idle':True,'known_compute_jobs':'terminal','native_UI':'CUA confirmed locked this turn; no unlock requested. Existing native Chat adoption unverified.',
  'new_training':False,'model_defaults_unchanged':True,'full_goal_status':'active incomplete','evidence':evidence,
  'next_work':'Reconstruct movement13C9A and actor collision13B5A/13BB0, connect existing GPU4320 movement math, then integrate actual actors into startup/world/render and remaining game systems.'}
 save(ROOT/'verification/rng-cpu-checkpoint.json',checkpoint)
 for name in ['setup-status.json','current-runtime-state.json','everyday-inference.json','requirements-audit.json']:
  path=ROOT/'verification'/name;value=read(path);value.update(rng_full_CPU_checkpoint=checkpoint,rng_full_CPU_review=review)
  if name=='current-runtime-state.json':value.update(recorded_at=now,models=models,local_inference_jobs='Terminal. One ordinary full-CPU RNG scope question correct with one evidence call; model idle.',emulator_jobs='Terminal. RNG/math6144cases/120nonexceptioninstructions/19guards; actor128cases/3072handoffs/2375helperreturnCPUs match.',latest_API_ease_review=str(ROOT/'verification/rng-cpu-review.json'))
  if name=='requirements-audit.json':
   value.update(recorded_at_utc=now,previous_goal_turn_classification='Progress: four navigation bodies4096CPUcases; actual actor scheduler128cases/3072handoffs; two source responses rejected and one evidence answer correct.',this_goal_turn_classification='Progress: indexed RNG plus math gain fullCPU/privateframes/flags;6144cases/19guards andactor128cases/3072handoffs/2375helperreturnCPUs pass. One ordinary local answer correct withonecall. Count100unchanged; movementonlyremainingactorhelper script.',next_safe_work=checkpoint['next_work'])
   for item in value['requirements']:
    if 'decompilation test'in item['requirement']:item['evidence']=list(dict.fromkeys(item['evidence']+evidence))
  save(path,value)
 progress=read(ROOT/'config.json')['rng_full_CPU_progress']
 note='\nFULL CPU RNG CHECKPOINT — '+now+'\n\n'+progress+'\n\nWHO DID WHAT\n'+who+'\n\nORDINARY LOCAL INFERENCE\nOne current-evidence answer correct with one rng tool call in '+str(question['SDK_reported_seconds'])+' SDK seconds. Single sample; no benchmark claim.\n\nEXACT PROMPTS/RESPONSES/ERRORS\n'+str(audit/'prompts-and-responses.txt')+'\n\nNEXT\n'+checkpoint['next_work']+'\nFull goal active and incomplete.\n'
 for name in ['POST REVIEW.txt','projects/black-ice-white-noise/restoration/READ ME.txt']:
  with(ROOT/name).open('a')as handle:handle.write(note)
 path=ROOT/'CURRENT DECOMPILATION.txt';text=path.read_text();text+='\nLOCAL INFERENCE RESULT\nOne ordinary evidence-grounded RNG question answered correctly with one tool call. Exact prompts, response, test failures/corrections and responsibility: '+str(audit/'prompts-and-responses.txt')+'\n';path.write_text(text)
 path=ROOT/'START HERE.txt';text=path.read_text();start=text.index('LOCAL INFERENCE RESULT\n');end=text.index('TRY ADVERTISING ASSISTANT\n',start);path.write_text(text[:start]+'LOCAL INFERENCE RESULT\nThe current RNG scope question answered correctly with one evidence call in about18seconds. Two previous ungrounded source-reading replies remain rejected. Native Chat was locked; logs are separate and latest native preset/MCP adoption is unverified.\n\nTry: What did the full-CPU RNG upgrade verify, and is actor movement complete?\n\n'+text[end:])
 subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'scripts/install_chat_runtime.py')],check=True)
 print(json.dumps({'components':100,'CPU_cases':6144,'host_guards':19,'actor_scripts':1,'helper_return_CPUs':2375,'question_tools':1,'SDK_seconds':question['SDK_reported_seconds'],'audit':str(audit)}))

if __name__=='__main__':main()
