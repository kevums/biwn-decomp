"""Check unedited local model output decisions against original CPU execution."""
import ctypes as c,json,re,subprocess,os
from pathlib import Path
import check_biwn_media_setup_cpu as media
ROOT=media.ROOT;save=media.save;sha=media.sha
pointer=json.loads((ROOT/'verification/actor7-local-distance-fragment-current.json').read_text());out=Path(pointer['directory']);protocol=json.loads((out/'protocol.json').read_text())
proof=json.loads((ROOT/'verification/entry-setup-helpers-checks.json').read_text());runtime=media.Runtime(Path(proof['directory'])/'libentry-helpers.dylib',[])
live=json.loads((ROOT/'verification/natural-actor8-task-current.json').read_text());ram=(Path(live['directory'])/'native-RAM.bin').read_bytes();runtime.reset(ram,0);runtime.core.m68k_set_irq(0)
cpu=media.CPU();cpu.registers[10]=0x49d6c;cpu.registers[15]=cpu.usp=0x1ff000;cpu.ssp=0x200000;cpu.pc=0x14d7c;cpu.sr=0;runtime.seed_cpu(cpu);core=runtime.core
vectors=[(mode,0)for mode in range(65536)]
vectors += [(mode,distance)for mode in [0,1,2,3,0x7fff,0x8000,0xffff]for distance in [-2147483648,-1,0,254,255,256,4095,4096,4097,2147483647]]
expected=[];native_instructions=0
try:
 for previous,distance in vectors:
  core.m68k_set_reg(0,distance&0xffffffff);core.m68k_set_reg(15,0x1ff000);core.m68k_set_reg(17,0);core.m68k_set_reg(16,0x14d7c);runtime.device.direct(0x49dd8,2,previous);message=0xffff
  for steps in range(32):
   pc=core.m68k_get_reg(None,16)
   if pc==0x14dba:break
   if pc==0x207cc:
    message=runtime.device.read(core.m68k_get_reg(None,15)+4,2)
    old=runtime.device.read(pc,2);runtime.device.direct(pc,2,0x4e75);core.m68k_execute(1);runtime.device.direct(pc,2,old)
   else:core.m68k_execute(1)
   native_instructions+=1
  else:raise AssertionError('Original branch bound')
  expected.append((message<<16)|runtime.device.read(0x49dd8,2))
 results=[]
 for role in ['author','reviewer']+(['format-repair']if(out/'format-repair.c').exists()else[]):
  raw=(out/(role+'.c')).read_text();fences=re.findall(r'```(?:c)?\s*\n(.*?)```',raw,re.S);source=fences[0]if len(fences)==1 else raw
  row=dict(role=role,raw_sha256=sha(raw.encode()),format_contract_passed=not fences,coordinator_change='Markdown fence removal only'if fences else'None',cases=len(vectors),accepted=False)
  if any(token in source for token in ['system(','fopen','malloc','asm','__attribute__','#include <unistd','dlopen']):
   row.update(status='rejected_disallowed_source');results.append(row);continue
  candidate=out/(role+'-extracted.c');candidate.write_text(source);lib=out/(role+'-decision.dylib');cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(candidate),'-o',str(lib)];run=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/(role+'-compiler.txt')).write_text(run.stdout+run.stderr)
  if run.returncode:row.update(status='rejected_compile',compiler=cmd);results.append(row);continue
  fn=c.CDLL(str(lib)).biwn_actor7_distance_decision;fn.argtypes=[c.c_uint16,c.c_int32];fn.restype=c.c_uint32;errors=[];failures=0
  for (previous,distance),original in zip(vectors,expected):
   actual=fn(previous,distance)
   if actual!=original:
    failures+=1
    if len(errors)<10:errors.append(dict(previous=previous,distance=distance,original=hex(original),C=hex(actual)))
  row.update(status='accepted_output_only_source_decision'if not failures else'rejected_output_mismatch',accepted=not failures,failures=failures,errors=errors,candidate_sha256=sha(candidate.read_bytes()));results.append(row)
 report=dict(status='completed_output_only_native_checks',directory=str(out),results=results,cases=len(vectors),all_65536_state_words_at_distance_zero=True,signed_distance_boundaries=True,original_instructions_executed=native_instructions,source_instruction_range=['0x14d7c','0x14dba'],source_RAM_sha256=sha(ram),helper_207CC='ABI return adapter, message argument observed; no actual audio/dialogue helper behavior',full_CPU_RAM_stack_flags_equivalence=False,live_game_linked=False,new_training=False,legacy_instruction_case_body_count_changed=False,whole_game_complete=False)
 save(out/'native-check.json',report);save(ROOT/'verification/actor7-local-distance-fragment-reviewed.json',report);protocol.update(status=report['status'],native_check=str(out/'native-check.json'));save(out/'protocol.json',protocol);print([(r['role'],r['status'],r.get('failures'))for r in results],len(vectors),flush=True)
finally:runtime.oracle.close()
