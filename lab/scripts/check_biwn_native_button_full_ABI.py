"""New native wrapper versus original full-register/condition-code ABI."""
from datetime import datetime,timezone
from pathlib import Path
import itertools,json,os,subprocess
from check_biwn_native_button_digit import ROOT,CODE,execute,sha,save,SP,STOP
import check_biwn_scheduler as scheduler

class NativeCPU:
 def __init__(self):self.native=scheduler.Native()
 def close(self):self.native.close()
 def execute(self,image,entry,limit,mask,incoming,sr):
  native=self.native;lib=native.lib;native.device.seed(image,0);lib.m68k_pulse_reset();lib.m68k_set_irq(0)
  lib.m68k_set_reg(17,0x2000);lib.m68k_set_reg(15,SP);lib.m68k_set_reg(17,sr);lib.m68k_set_reg(15,SP)
  registers=[0]*16;registers[0]=incoming;registers[1]=0x11223344;registers[8]=0x33445566;registers[9]=0x55667788;registers[15]=SP
  for i,reg in enumerate([2,3,4,5,6,7,10,11,12,13,14]):registers[reg]=(0x12345678+i*0x11111111)&0xffffffff
  for reg,value in enumerate(registers):lib.m68k_set_reg(reg,value)
  native.device.direct(SP,4,STOP);native.device.direct(SP+4,4,mask);expected_RAM=bytearray(image);expected_RAM[SP:SP+8]=STOP.to_bytes(4,'big')+mask.to_bytes(4,'big')
  lib.m68k_set_reg(16,entry);pcs=[]
  for _ in range(10000):
   pc=lib.m68k_get_reg(None,16)
   if pc==STOP:break
   assert entry<=pc<limit,('native code escaped',hex(pc));pcs.append(pc);lib.m68k_execute(1)
  else:raise AssertionError('Native component did not return')
  returned=native.device.ram();assert returned[:SP-0x1000]==expected_RAM[:SP-0x1000]and returned[SP:]==expected_RAM[SP:],'Nonprivate nativeRAM changed'
  result=dict(registers=[lib.m68k_get_reg(None,i)for i in range(16)],PC=lib.m68k_get_reg(None,16),SR=lib.m68k_get_reg(None,17))
  assert result['registers'][15]==SP+4
  return result,pcs

def main():
 out=ROOT/'verification/native-button-full-ABI'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 state=dict(status='prepared',pid=os.getpid(),directory=str(out),whole_game_complete=False,game_image_patched=False,source_accepted=False,new_training=False,native_Chat=False)
 def checkpoint():save(out/'protocol.json',state);save(ROOT/'verification/native-button-full-ABI-active.json',state)
 checkpoint();print(out,flush=True)
 try:
  native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
  author_path=ROOT/'verification/local-native-button-full-abi-current.json';author=json.loads(author_path.read_text());assert author['status']in ['terminal_assembled_pending_native_semantics','terminal_native_semantics_accepted']
  shim=native/'button-digit-full-ABI-shim.S';assert sha(shim)==author['candidate_sha256']==sha(author['candidate'])
  toolchain_path=ROOT/'verification/m68k-toolchain-current.json';tools=json.loads(toolchain_path.read_text());assert tools['status']=='terminal_toolchain_smoke_pass'
  command=['/usr/bin/make','-f','Makefile.full-abi','full-abi','BUILD='+str(out/'build')]
  result=subprocess.run(command,cwd=native,capture_output=True,text=True);(out/'make.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
  binary=out/'build/button-digit-full-ABI.bin';elf=out/'build/button-digit-full-ABI.elf';code=binary.read_bytes();assert 0<len(code)<0x10000
  original=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes();candidate=bytearray(original);candidate[CODE:CODE+len(code)]=code;candidate=bytes(candidate)
  prior_path=ROOT/'verification/native-button-digit-current.json';prior=json.loads(prior_path.read_text());old=bytearray(original);old_code=Path(prior['compiled_binary']).read_bytes();old[CODE:CODE+len(old_code)]=old_code
  cpu=NativeCPU()
  expected,_=cpu.execute(original,0x1b718,0x1b780,1<<19,0xdeadbeef,0x201f)
  old_actual,_=cpu.execute(bytes(old),CODE,CODE+len(old_code),1<<19,0xdeadbeef,0x201f)
  assert old_actual['registers'][0]==expected['registers'][0]and old_actual['registers'][1]!=expected['registers'][1]
  relevant=[19,18,17,7,6,5,4,3,2,1];incoming_values=[0,0x8000ffff,0xdeadbeef]
  base=[(sum(1<<bit for bit,enabled in zip(relevant,flags)if enabled),incoming,0x2000)
        for flags in itertools.product([0,1],repeat=10)for incoming in incoming_values]
  matrix=[(mask,incoming,mode|ccr)for mask in [0]+[1<<bit for bit in relevant]for incoming in incoming_values for mode in [0,0x2000]for ccr in range(32)]
  cases=list(dict.fromkeys(base+matrix));assert len(cases)==5151
  rows=[];reference_pcs=set();compiled_pcs=set();state.update(status='checking_full_register_ABI',compile_command=command);checkpoint()
  for ordinal,(mask,incoming,sr)in enumerate(cases):
   expected,pcs=cpu.execute(original,0x1b718,0x1b780,mask,incoming,sr)
   actual,new_pcs=cpu.execute(candidate,CODE,CODE+len(code),mask,incoming,sr)
   assert actual==expected,('full_ABI_mismatch',ordinal,hex(mask),hex(incoming),hex(sr),expected,actual)
   assert actual['registers'][1]==mask
   reference_pcs.update(pcs);compiled_pcs.update(new_pcs);rows.append(dict(mask=mask,incoming_D0=incoming,incoming_SR=sr,full_registers_PC_SR=actual,reference_steps=len(pcs),compiled_steps=len(new_pcs)))
   if ordinal%512==0:state['completed_cases']=ordinal;checkpoint();print('full ABI',ordinal,'/',len(cases),flush=True)
  save(out/'cases.json',rows)
  core=ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib';device=Path(cpu.native.device.lib._name)
  state['native_execution_dependencies_sha256']={str(path):sha(path)for path in [core,device]}
  unicorn_probe,_,_=execute(original,0x1b718,0x1b780,0,0,return_cpu=True)
  state['flag_oracle_note']='Full-register/SR gate uses the same pinned native M68000 core on both lanes. The earlier Unicorn original-case SR read differed; physical hardware remains untested.'
  state['original_SR_oracle_probe']=dict(pinned_native=rows[0]['full_registers_PC_SR']['SR'],Unicorn=unicorn_probe['SR'])
  cpu.close()
  paths=[native/name for name in ['Makefile','Makefile.full-abi','native.ld','button-digit-full-ABI-shim.S']]+[native.parent/name for name in ['biwn_inventory_select.c','biwn_inventory_select.h']]
  state.update(status='terminal_recovered_C_native_button_digit_full_register_ABI_matches',source_accepted=True,cases=len(rows),base_button_cases=len(base),CCR_mode_matrix_cases=len(matrix),unique_extra_CCR_mode_cases=len(rows)-len(base),all32CCR_inputs=True,user_and_supervisor_modes=True,all16registers_PC_and_SR_match=True,D1_original_mask_restored=True,prior_scalar_wrapper_D1_difference_detected=True,original_stack_argument_and_return_SP_preserved=True,nonprivate_final_RAM_unchanged=True,compiled_binary=str(binary),compiled_binary_sha256=sha(binary),compiled_ELF=str(elf),compiled_ELF_sha256=sha(elf),compiled_binary_bytes=len(code),source_sha256={str(path):sha(path)for path in paths},toolchain_proof=str(toolchain_path),toolchain_proof_sha256=sha(toolchain_path),author_proof=str(author_path),author_candidate_sha256=author['candidate_sha256'],guided_model_repair=True,coordinator_supplied_instruction_plan=True,coordinator_edited_model_source=False,raw_guided_model_source_accepted_unchanged=True,existing_recovered_C_source_reused=True,model_wrote_recovered_C_body_this_turn=False,original_BIWN_function_instructions_executed_on_candidate=0,reference_instruction_locations=len(reference_pcs),compiled_instruction_locations=len(compiled_pcs),execution='Pinned native M68000 core for reference and candidate; no physical console or game frames.',scope='5151unique native-original/compiled cases:3072all-relevant-button/inputD0 cases plus2079extraCCR/mode cases; the2112case matrix includes33overlaps. Full16registers, PC, SR, original argument/returnSP and nonprivate finalRAM match. New unchanged guided local shim fixes priorD1difference via flag-preserving load. Compiler emits realM68000code from existing recovered C; original function never executes on candidate. No native-game call-site/frame integration, safe code placement, cycle timing, disc image or physical console proof.')
  checkpoint();save(ROOT/'verification/native-button-full-ABI-current.json',state)
  author.update(status='terminal_native_semantics_accepted',source_accepted=True,native_semantics_proof=str(ROOT/'verification/native-button-full-ABI-current.json'),coordinator_edited_model_source=False);save(author_path,author);save(Path(author['directory'])/'protocol.json',author)
  print(json.dumps(dict(status=state['status'],directory=str(out),cases=len(rows),bytes=len(code),model_source_accepted_unchanged=True)),flush=True)
 except BaseException as error:state.update(status='terminal_failed',error=repr(error));checkpoint();raise

if __name__=='__main__':main()
