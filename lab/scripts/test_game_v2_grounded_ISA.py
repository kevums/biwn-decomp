"""Freeze grounded repair context; compare same models, not a fresh holdout."""
import json,time,fcntl,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import chat_tools
from mlx_lora_reasoning_off import ReasoningOffTokenizer
j=json.loads((ROOT/'verification/game-source-v2-evaluation-current.json').read_text());out=Path(j['directory'])/'grounded-ISA';out.mkdir();training=json.loads((Path(j['job'])/'training-result.json').read_text());evidence=chat_tools.project_evidence('m68k_isa');system='You are the local Restorer role. You have no tools. Use supplied source definitions; return bare complete C source only, no fences or commentary. Do not claim execution.'
user='Write C99 including stdint.h. Export void biwn_moveq_effect(uint8_t immediate, uint32_t *d, uint16_t *sr). Pointers valid. Implement only MOVEQ effect; no RTS, allocation, I/O or other functions. Preserve all SR bits except N/Z/V/C; X must be preserved. Use the exact supplied masks.\nVERIFIED ISA DEFINITIONS\n'+json.dumps(evidence,indent=2)
protocol=dict(status='running',context_frozen_before_outputs=True,system=system,user=user,evidence=evidence,scope='Adaptive repair of observed bit-layout failures on same models/source; not independent validation or broad model promotion.',results=[]);(out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
with(ROOT/'runs/.inference.lock').open('a')as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);subprocess.run([str(Path.home()/'.lmstudio/bin/lms'),'unload','--all'],cwd=Path.home()/'.lmstudio',check=True,stdout=subprocess.DEVNULL)
 import mlx.core as mx
 from mlx_lm import load,stream_generate
 from mlx_lm.tuner.utils import load_adapters
 from mlx_lm.sample_utils import make_sampler
 model,t=load(str(Path.home()/'.lmstudio/models'/training['base']['repo']));tokenizer=ReasoningOffTokenizer(t)
 for phase in ['base','adapter']:
  if phase=='adapter':load_adapters(model,j['selection']['selected_adapter'])
  prompt=tokenizer.apply_chat_template([dict(role='system',content=system),dict(role='user',content=user)],tokenize=True,add_generation_prompt=True);text='';last=None;start=time.monotonic()
  for item in stream_generate(model,t,prompt,max_tokens=768,sampler=make_sampler(temp=0)):text+=item.text;last=item
  row=dict(phase=phase,system=system,prompt=user,response=text,seconds=time.monotonic()-start,finish_reason=last.finish_reason);protocol['results'].append(row);(out/(phase+'.c')).write_text(text);(out/(phase+'.json')).write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(dict(phase=phase,seconds=row['seconds'],finish=row['finish_reason'])),flush=True)
protocol['status']='terminal_generated_validation_pending';(out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');print(out,flush=True)
