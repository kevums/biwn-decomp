"""Compare extracted, unedited pure C effect with the original source instructions."""
import ctypes as c,json,re,subprocess,os,hashlib
from pathlib import Path
import check_biwn_media_setup_cpu as media
ROOT=media.ROOT;save=media.save;sha=media.sha
p=json.loads((ROOT/'verification/actor14-local-voice-fragment-current.json').read_text());out=Path(p['directory']);protocol=json.loads((out/'protocol.json').read_text());raw=(out/'author.c').read_text();fences=re.findall(r'```c\s*\n(.*?)```',raw,re.S);assert len(fences)==1;source=fences[0];assert source.startswith('#include <stdint.h>')and not any(s in source for s in ['system(','fopen','malloc','asm','__attribute__']);candidate=out/'author-extracted.c';candidate.write_text(source);lib=out/'author-voice-flag.dylib';cmd=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(candidate),'-o',str(lib)];run=subprocess.run(cmd,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
fn=c.CDLL(str(lib)).biwn_actor14_voice_flag;fn.argtypes=[c.c_uint16,c.c_uint16];fn.restype=c.c_uint16
proof=json.loads((ROOT/'verification/entry-setup-helpers-checks.json').read_text());runtime=media.Runtime(Path(proof['directory'])/'libentry-helpers.dylib',[]);live=json.loads((ROOT/'verification/natural-actor14-task-current.json').read_text());ram=(Path(live['directory'])/'native-RAM.bin').read_bytes();runtime.reset(ram,0);runtime.core.m68k_set_irq(0);cpu=media.CPU();cpu.registers[15]=cpu.usp=0x1ff000;cpu.ssp=0x200000;cpu.pc=0x1a674;cpu.sr=0;runtime.seed_cpu(cpu);core=runtime.core;cases=0;errors=[];native_outcomes=set();native_instructions=0
try:
 vectors=[(voice,0x1234)for voice in range(65536)]+[(voice,previous)for voice in [0,1,2,3,4,5,0xffff]for previous in [0,1,0xffff]]
 for voice,previous in vectors:
  core.m68k_set_reg(0,0xdead0000|voice);core.m68k_set_reg(1,0xbeef0000);core.m68k_set_reg(15,0x1ff000);core.m68k_set_reg(17,0);core.m68k_set_reg(16,0x1a674);runtime.device.direct(0x462c2,2,previous)
  for steps in range(16):
   if core.m68k_get_reg(None,16)==0x1a690:break
   core.m68k_execute(1);native_instructions+=1
  else:raise AssertionError('Original branch bound')
  expected=runtime.device.read(0x462c2,2);actual=fn(voice,previous);native_outcomes.add((voice if expected!=previous else -1,expected))
  if expected!=actual:
   errors.append(dict(voice=voice,previous=previous,original=expected,C=actual))
   if len(errors)>10:break
  cases+=1
 report=dict(status='accepted_output_only_source_decision'if not errors else'rejected_output_mismatch',directory=str(out),model=protocol['model'],role='author',cases=cases,all_65536_voice_words_tested=cases>=65536,additional_prior_flag_cases=21,compiler=cmd,source_instruction_range=['0x1a674','0x1a690'],original_instructions_executed=native_instructions,source_RAM_sha256=sha(ram),raw_response_sha256=sha((out/'author.c').read_bytes()),candidate_sha256=sha(candidate.read_bytes()),format_contract_passed=False,coordinator_change='Only Markdown fence removal; C code unchanged. Raw response failed bare-source format.',coordinator_supplied=protocol['coordinator_supplied'],errors=errors,accepted=not errors,full_CPU_RAM_stack_flags_equivalence=False,source_output_only_flag_word=True,live_game_linked=False,new_training=False,legacy_instruction_case_body_count_changed=False,reviewer=dict(accepted=False,reason='No C output; truncated prose misreads BLS as testing unsigned subtraction result<=0, missing the borrow condition.',raw_response=str(out/'reviewer.json'),quality_flags=protocol['results'][1]['quality_flags'],independent_verification=False),whole_game_complete=False)
 save(out/'native-check.json',report);save(ROOT/'verification/actor14-local-voice-fragment-reviewed.json',report);protocol['status']=report['status'];protocol['native_check']=str(out/'native-check.json');save(out/'protocol.json',protocol);save(ROOT/'verification/actor14-local-voice-fragment-current.json',dict(directory=str(out),status=report['status']));print(report['status'],cases,flush=True)
finally:runtime.oracle.close()
