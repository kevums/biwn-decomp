"""One local Author draft for the selected-actor/C-render integration API."""
import fcntl,json,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import lmstudio,sdk_thinking_override_probe
sdk_thinking_override_probe.install()
src=ROOT/'projects/black-ice-white-noise/restoration'
out=ROOT/'runs'/('local-actor-scene-tick-author-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir(parents=True);print(out,flush=True)
system='You are the local C integration Author. Use only the exact supplied APIs and algorithm. Do not invent game behavior, instructions, test results, or helper outcomes. Return one C code block and no prose.'
prompt='''Implement biwn_actor_scene_tick declared below. C99, -Wall -Wextra -Werror. Include biwn_actor_scene_tick.h. No other functions/APIs needed except a small task-check helper if useful.
Validation BEFORE any side effect: bus/cpu/write8/links/out_D0 nonnull; bus read8/read16/read32/write16/write32 allnonnull; capacity>0,budget>0,scratch>=256 and even; expected_task nonzero and even; cpu usermode (SR&0x2000 must be ZERO). Failure return BAD_ARGUMENT. Unsupported inputPC return OTHER_CONTINUATION with no effects; supported inputs DF60/F4D8/F56E/F70C only.
Algorithm, preserve exact phase ordering:
1 If inputPC=DF60, call biwn_actor_pipeline_step(bus,cpu,write8,budget,observer,opaque) ONCE. Nonzero ->COMPONENT_ERROR. Do not use a CPU copy: successful steps commit immediately.
2 Read32(bus->context,0xC0920,&current). Failure ->COMPONENT_ERROR. If current!=expected_task OR cpu.pc not F4D8/F56E/F70C return OTHER_CONTINUATION, retain earlier phase effects.
3 Call pipeline_step ONCE for actor body. Nonzero ->COMPONENT_ERROR. If cpu.pc==DF7A return EXIT_BOUNDARY (do not remove task or draw). If cpu.pc!=DF60 return OTHER_CONTINUATION.
4 Call pipeline_step ONCE for actual yield/resumption. Nonzero ->COMPONENT_ERROR. Read current task again, failure ->COMPONENT_ERROR. Require current==expected_task and cpu.pc==F70C, otherwise OTHER_CONTINUATION, do not render.
5 Call biwn_scene_render_pipeline(bus,write8,scratch,links,capacity,budget,incoming_D0,&local_result), not directly into out_D0. Nonzero ->RENDER_ERROR. On success assign*out_D0=local_result, return OK. No fabricated clock increments, task blocking, actor coordinates, camera, model/animation state, helper callbacks, RAM reads/writes beyond two current-task reads. Observer forwarded to all pipeline calls. All earlier effects retained on failure. There is no independent generated scheduler or CPU implementation here.
Exact headers:\n'''+''.join('\n'+(src/name).read_text()for name in ['biwn_actor_scene_tick.h','biwn_actor_pipeline.h','biwn_scene_render_pipeline.h','biwn_scheduler.h'])
record=dict(role='local Author',model='advertising-scholar',system=system,prompt=prompt,status='pending',new_training=False,scope='Coordinator supplies API and explicit phase algorithm; model writes facade only. Verification is separate.')
(out/'protocol.json').write_text(json.dumps(record,indent=2)+'\n');(out/'prompts-and-responses.txt').write_text('SYSTEM\n'+system+'\nUSER\n'+prompt+'\n')
with(ROOT/'runs/.inference.lock').open('w')as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],text=True));assert len(models)==1 and models[0]['identifier']=='advertising-scholar'and models[0]['status']=='idle'
 chat=lmstudio.Chat(system);chat.add_user_message(prompt);started=time.monotonic()
 response=lmstudio.llm('advertising-scholar').respond(chat,config={'temperature':0.1,'maxTokens':2600,'raw':{'fields':[{'key':'llm.prediction.reasoning.enableThinking','value':False},{'key':'ext.virtualModel.customField.enableThinking','value':False},{'key':'ext.virtualModel.customField.preserveThinking','value':False}]}})
 record['seconds']=time.monotonic()-started;raw=response.content
 (out/'raw-response.txt').write_text(raw)
 with(out/'prompts-and-responses.txt').open('a')as f:f.write('\nASSISTANT\n'+raw+'\n')
 assert raw.count('```')==2 and '```c'in raw
 code=raw.split('```c',1)[1].split('```',1)[0].strip()+'\n';(out/'candidate.c').write_text(code)
 record.update(status='draft_returned_unverified',directory=str(out),raw_response=raw)
 (out/'protocol.json').write_text(json.dumps(record,indent=2)+'\n');(ROOT/'verification/local-actor-scene-tick-workflow-current.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(dict(status=record['status'],seconds=record['seconds'])),flush=True)
