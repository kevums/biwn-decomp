"""Compare local follow-speed extraction with original source and real E588."""
import ctypes as c,json,re,subprocess,os,random
from pathlib import Path
import check_biwn_media_setup_cpu as media
ROOT=media.ROOT;save=media.save;sha=media.sha
out=Path(json.loads((ROOT/'verification/actor6-local-follow-fragment-current.json').read_text())['directory']);protocol=json.loads((out/'protocol.json').read_text())
proof=json.loads((ROOT/'verification/entry-setup-helpers-checks.json').read_text());runtime=media.Runtime(Path(proof['directory'])/'libentry-helpers.dylib',[]);live=json.loads((ROOT/'verification/natural-actor6-task-current.json').read_text());ram=(Path(live['directory'])/'native-RAM.bin').read_bytes();runtime.reset(ram,0);runtime.core.m68k_set_irq(0)
cpu=media.CPU();cpu.registers[11]=0x49d6c;cpu.registers[15]=cpu.usp=0x1ff000;cpu.ssp=0x200000;cpu.pc=0x1585c;cpu.sr=0;runtime.seed_cpu(cpu);core=runtime.core;expected=[];native_instructions=0
vectors=[(ticks,0xffff)for ticks in range(65536)]
vectors += [(ticks,fraction)for ticks in [0,1,75,300,0xffff,0x10000,0x1ffff,0x7fffffff,0x80000000,0xffffffff]for fraction in [0,1,0xffff,0x10000,0x7fffffff,0x80000000,0xffffffff]]
rng=random.Random(0x1585c);vectors += [(rng.getrandbits(32),rng.getrandbits(32))for _ in range(1024)]
try:
 for ticks,fraction in vectors:
  core.m68k_set_reg(15,0x1ff000);core.m68k_set_reg(17,0);core.m68k_set_reg(16,0x1585c);runtime.device.direct(0x4c24c,4,ticks);runtime.device.direct(0x49de8,4,fraction)
  for steps in range(256):
   if core.m68k_get_reg(None,16)==0x15896:break
   core.m68k_execute(1);native_instructions+=1
  else:raise AssertionError(('Original helper bound',hex(core.m68k_get_reg(None,16))))
  expected.append((runtime.device.read(0x49de8,4)<<32)|runtime.device.read(0x49de4,4))
 results=[]
 for role in ['author','reviewer']+(['guided-repair']if(out/'guided-repair.c').exists()else[])+(['saved-assistant']if(out/'saved-assistant.c').exists()else[]):
  raw=(out/(role+'.c')).read_text();fences=re.findall(r'```(?:c)?\s*\n(.*?)```',raw,re.S);source=fences[0]if len(fences)==1 else raw
  row=dict(role=role,raw_sha256=sha(raw.encode()),format_contract_passed=not fences and '#include <stdint.h>' in source,coordinator_change='Markdown fence removal only'if fences else'None',cases=len(vectors),accepted=False)
  if any(t in source for t in ['system(','fopen','malloc','asm','__attribute__','dlopen']):row.update(status='rejected_disallowed_source');results.append(row);continue
  candidate=out/(role+'-extracted.c');candidate.write_text(source);lib=out/(role+'-follow.dylib');cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(candidate),'-o',str(lib)];
  if '#include <stdint.h>' not in source:cmd[1:1]=['-include','stdint.h'];row['coordinator_change']='Required type header supplied at compilation only; raw C unchanged'
  run=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/(role+'-compiler.txt')).write_text(run.stdout+run.stderr)
  if run.returncode:row.update(status='rejected_compile',compiler=cmd);results.append(row);continue
  fn=c.CDLL(str(lib)).biwn_actor6_follow_step;fn.argtypes=[c.c_uint32,c.c_uint32];fn.restype=c.c_uint64;errors=[];failures=0
  for (ticks,fraction),original in zip(vectors,expected):
   actual=fn(ticks,fraction)
   if actual!=original:
    failures+=1
    if len(errors)<10:errors.append(dict(ticks=hex(ticks),fraction=hex(fraction),original=hex(original),C=hex(actual)))
  row.update(status='accepted_output_only_source_arithmetic'if not failures else'rejected_output_mismatch',accepted=not failures,failures=failures,errors=errors,candidate_sha256=sha(candidate.read_bytes()));results.append(row)
 report=dict(status='completed_output_only_native_checks',directory=str(out),results=results,cases=len(vectors),all_65536_low_tick_words_tested=True,random_32bit_pairs=1024,original_instructions_executed=native_instructions,source_instruction_range=['0x1585c','0x15896'],actual_E588_signed_division=True,source_RAM_sha256=sha(ram),full_CPU_RAM_stack_flags_equivalence=False,live_game_linked=False,new_training=False,legacy_instruction_case_body_count_changed=False,whole_game_complete=False)
 save(out/'native-check.json',report);save(ROOT/'verification/actor6-local-follow-fragment-reviewed.json',report);protocol.update(status=report['status'],native_check=str(out/'native-check.json'));save(out/'protocol.json',protocol);print([(r['role'],r['status'],r.get('failures'))for r in results],len(vectors),flush=True)
finally:runtime.oracle.close()
