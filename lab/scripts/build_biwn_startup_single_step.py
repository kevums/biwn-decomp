"""Append bounded one-instruction exports; retain accepted original APIs."""
import re,json,hashlib,subprocess,os
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def main():
 prior=json.loads((ROOT/'verification/atomic-startup-all-candidate.json').read_text());accepted=json.loads((ROOT/'verification/startup-elapsed-clock-current.json').read_text());witness=Path(accepted['plans']['none']['runs']['native']);probe=json.loads((witness/'native-startup-instruction-probe.json').read_text());needed={int(p,16)for p in probe['PC_counts']};files=[Path(p)for p in prior['compiler']if p.endswith('.c')]
 out=ROOT/'verification/startup-single-step-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');src=out/'source';src.mkdir(parents=True)
 for p in Path(prior['directory']).joinpath('source').glob('*.h'):(src/p.name).write_bytes(p.read_bytes())
 selected={};cases={};priority=sorted(files,key=lambda p:(p.name not in ['biwn_startup_rng_math_cpu.c','biwn_scheduler.c','biwn_geometry_cpu.c','biwn_input_poll_cpu.c'],p.name))
 for p in priority:
  text=p.read_text()
  if 'struct dispatch {struct biwn_world_bus *bus;struct biwn_task_cpu cpu;' not in text:continue
  matches=list(re.finditer(r'^\s*case (0x[0-9a-f]+)u:',text,re.M))
  for index,m in enumerate(matches):
   pc=int(m[1],16)
   if pc not in needed or pc in selected:continue
   stop=matches[index+1].start()if index+1<len(matches)else text.index('default:',m.end())
   body=text[m.start():stop].rstrip()
   body=re.sub(r'CHECK\(invoke\(&s,[^;]+?\)\);','',body)
   body=body.replace('CHECK(s.service(s.context,s.bus,&s.cpu,v));','')
   if 's.service('in body and re.search(r'/\* jmp ',body):
    target=re.search(r's.cpu.pc=(0x[0-9a-f]+u);',body)[1]
    body=f'case {hex(pc)}u: /* original tail JMP, one boundary */\n biwn_instruction_observe(&s.cpu);s.cpu.pc={target};break;'
   assert 's.service('not in body,(p.name,hex(pc))
   assert 'invoke('not in body,(p.name,hex(pc))
   # Existing direct trap/yield cases commit CPU and return status6. This
   # remains a successful one-op boundary, not a host completion shortcut.
   selected[pc]=p.name;cases.setdefault(p.name,[]).append(body)
 missing=needed-set(selected);assert missing=={0x4088},list(map(hex,missing))
 names={p.name:'biwn_step_'+p.stem for p in files if p.name in cases}
 for p in files:
  text=p.read_text()
  if p.name in cases:
   text+='\n/* One source instruction only; calls retain their real frames. */\n'
   text+=f'int {names[p.name]}(struct biwn_world_bus *bus,struct biwn_task_cpu *state,biwn_input_write8 write8,biwn_world_cpu_service service,void *context){{\n'
   text+='struct dispatch s;uint32_t v=0,u=0,limit=0xffffffffu;int full_call=1,stop_on_yield=0,resume=0;\n(void)v;(void)u;(void)limit;(void)full_call;(void)stop_on_yield;(void)resume;\nif(!bus||!state||!write8||!service)return 1;\ns.bus=bus;s.cpu=*state;s.write8=write8;s.service=service;s.context=context;\nswitch(s.cpu.pc){\n'
   text+='\n'.join(cases[p.name])+'\n default:return 7;\n}\n*state=s.cpu;return 0;\n}\n'
  (src/p.name).write_text(text)
 dispatcher=src/'biwn_source_single_step.c';common='struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *'
 text='#include "biwn_input_dispatch_cpu.h"\n'+'\n'.join(f'extern int {n}({common});'for n in names.values())+'\nint biwn_source_CPU_step(struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,biwn_input_write8 w8,biwn_world_cpu_service service,void *context){if(!cpu)return 1;switch(cpu->pc){\n'
 for pc,name in sorted(selected.items()):text+=f'case {hex(pc)}u:return {names[name]}(bus,cpu,w8,service,context);\n'
 text+='default:return 7;}}\n';dispatcher.write_text(text)
 library=out/'libstartup-single-step.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(src),'-I',str(ROOT/'projects/black-ice-white-noise/restoration'),*[str(src/p.name)for p in files],str(dispatcher),'-o',str(library)]
 result=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
 report=dict(status='compiled_one_instruction_dispatcher_unverified',directory=str(out),library=str(library),compiler=command,instruction_cases=len(selected),selected_case_sources={hex(k):v for k,v in selected.items()},source_sha256={p.name:hashlib.sha256((src/p.name).read_bytes()).hexdigest()for p in files},coordinator_authored=True,new_training=False,new_unique_game_coverage=False,whole_game_complete=False,limits=['Only PCs reached by accepted bounded startup. Platform4088provider remains separate. Original exported helpers retained for loader/prefix/world.','No instruction timing adoption or new game path implied by compilation.'])
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/startup-single-step-candidate.json').write_text(json.dumps(report,indent=2)+'\n');print(out)
if __name__=='__main__':main()
