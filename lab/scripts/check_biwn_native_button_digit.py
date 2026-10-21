"""Cross-compile recovered BIWN C and compare original native call ABI.

The candidate executes newly GCC-compiled M68000 code plus the proposed
local-model assembly shim. Original code executes only on the reference
lane. No game image/preview is patched. Caller-saved registers/CCR and real
game call-site assumptions are outside this first component's acceptance.
"""
import argparse,hashlib,itertools,json,os,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *

ROOT=Path(__file__).resolve().parents[1]
SP,STOP,CODE=0x180000,0x1f0000,0x10000
SAVED=[UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,UC_M68K_REG_A2,UC_M68K_REG_A3,UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6]
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def execute(image,entry,limit,input_value,incoming,return_cpu=False,sr=0x2000):
 cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_write(0,image)
 cpu.reg_write(UC_M68K_REG_SR,sr);cpu.reg_write(UC_M68K_REG_A7,SP);cpu.reg_write(UC_M68K_REG_D0,incoming)
 cpu.reg_write(UC_M68K_REG_D1,0x11223344);cpu.reg_write(UC_M68K_REG_A0,0x33445566);cpu.reg_write(UC_M68K_REG_A1,0x55667788)
 saved=[(0x12345678+i*0x11111111)&0xffffffff for i in range(len(SAVED))]
 for reg,value in zip(SAVED,saved):cpu.reg_write(reg,value)
 cpu.mem_write(SP,STOP.to_bytes(4,'big')+input_value.to_bytes(4,'big'))
 steps=[];writes=[]
 def code(engine,address,width,_):
  assert entry<=address<limit,('code outside component',hex(address));steps.append(address)
 def write(engine,access,address,width,value,_):
  assert SP-0x1000<=address and address+width<=SP,('unexpected nonprivate store',hex(address),width)
  writes.append([address,width,value])
 cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_WRITE,write)
 cpu.emu_start(entry,STOP,count=10000,timeout=500000)
 assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
 assert all(cpu.reg_read(reg)==value for reg,value in zip(SAVED,saved))
 assert bytes(cpu.mem_read(SP+4,4))==input_value.to_bytes(4,'big')
 if return_cpu:
  registers=[UC_M68K_REG_D0,UC_M68K_REG_D1,*SAVED[:6],UC_M68K_REG_A0,UC_M68K_REG_A1,*SAVED[6:],UC_M68K_REG_A7]
  return dict(registers=[cpu.reg_read(reg)for reg in registers],PC=cpu.reg_read(UC_M68K_REG_PC),SR=cpu.reg_read(UC_M68K_REG_SR)),steps,writes
 return cpu.reg_read(UC_M68K_REG_D0),steps,writes

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--wait-toolchain',action='store_true');args=parser.parse_args()
 out=ROOT/'verification/native-button-digit'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 state=dict(status='prepared',pid=os.getpid(),directory=str(out),native_Chat=False,new_training=False,source_accepted=False,whole_game_complete=False,game_image_patched=False)
 def checkpoint():save(out/'protocol.json',state);save(ROOT/'verification/native-button-digit-active.json',state)
 checkpoint();print(out,flush=True)
 try:
  started=time.monotonic();last_phase=None
  while not(ROOT/'verification/m68k-toolchain-current.json').exists():
   if not args.wait_toolchain:raise RuntimeError('Compiler smoke not yet passed; follow the existing build.')
   tool=json.loads((ROOT/'verification/m68k-toolchain-active.json').read_text())
   observed=subprocess.run(['ps','-p',str(tool['pid']),'-o','command='],capture_output=True,text=True).stdout
   if 'build_biwn_m68k_toolchain.py'not in observed:raise RuntimeError('Existing toolchain builder ended: '+tool['status'])
   if tool['status']!=last_phase:
    state.update(status='waiting_for_toolchain',builder_pid=tool['pid'],build_phase=tool['status']);checkpoint();print('verified live builder',tool['pid'],tool['status'],flush=True);last_phase=tool['status']
   if time.monotonic()-started>3600:raise TimeoutError('Stopped waiting after1hour; do not restart the compiler automatically.')
   time.sleep(2)
  tool=json.loads((ROOT/'verification/m68k-toolchain-current.json').read_text());assert tool['status']=='terminal_toolchain_smoke_pass'
  native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';author_path=ROOT/'verification/local-native-button-shim-current.json';author=json.loads(author_path.read_text())
  assert author['status']in ['terminal_assembled_pending_native_semantics','terminal_native_semantics_accepted']
  assert sha(native/'button-digit-shim.S')==author['candidate_sha256']==sha(author['candidate'])
  command=['/usr/bin/make','BUILD='+str(out/'build')];state.update(status='building_native_component',command=command);checkpoint()
  built=subprocess.run(command,cwd=native,capture_output=True,text=True);(out/'make.log').write_text(built.stdout+built.stderr);assert built.returncode==0,built.stderr
  binary=out/'build/button-digit.bin';code=binary.read_bytes();assert 0<len(code)<0x10000
  expected_source=ROOT/'verification/zero-warm-startup-instruction-atlas.bin';original=expected_source.read_bytes();assert len(original)==0x200000
  candidate=bytearray(original);candidate[CODE:CODE+len(code)]=code
  rows=[];reference_locations=set();candidate_locations=set();state['status']='checking_original_and_compiled_M68000';checkpoint()
  relevant=[19,18,17,7,6,5,4,3,2,1]
  cases=[(sum((1<<bit)for bit,enabled in zip(relevant,flags)if enabled),incoming)
         for flags in itertools.product([0,1],repeat=len(relevant))for incoming in [0,0x8000ffff,0xdeadbeef]]
  for ordinal,(mask,incoming)in enumerate(cases):
   expected,pcs,_=execute(original,0x1b718,0x1b780,mask,incoming)
   actual,compiled_pcs,_=execute(bytes(candidate),CODE,CODE+len(code),mask,incoming)
   assert actual==expected,('native D0 mismatch',ordinal,hex(mask),hex(incoming),hex(expected),hex(actual))
   reference_locations.update(pcs);candidate_locations.update(compiled_pcs);rows.append(dict(mask=mask,incoming_D0=incoming,full_D0=actual,original_steps=len(pcs),compiled_steps=len(compiled_pcs)))
   if ordinal%256==0:state['completed_cases']=ordinal;checkpoint();print('native cases',ordinal,'/',len(cases),flush=True)
  save(out/'cases.json',rows)
  source_paths=[native/'Makefile',native/'native.ld',native/'button-digit-shim.S',native.parent/'biwn_inventory_select.c',native.parent/'biwn_inventory_select.h']
  state.update(status='terminal_recovered_C_native_button_digit_matches',source_accepted=True,cases=len(rows),compiled_binary=str(binary),compiled_binary_sha256=sha(binary),compiled_ELF=str(out/'build/button-digit.elf'),source_sha256={str(p):sha(p)for p in source_paths},toolchain_proof=str(ROOT/'verification/m68k-toolchain-current.json'),toolchain_proof_sha256=sha(ROOT/'verification/m68k-toolchain-current.json'),author_proof=str(author_path),author_candidate_sha256=author['candidate_sha256'],raw_local_model_shim_accepted_unchanged=True,guided_model_repair=author['guided_repair'],initial_raw_model_attempt_accepted=False,coordinator_supplied_instruction_plan=author['coordinator_supplied_instruction_plan'],existing_recovered_C_source_reused=True,model_wrote_recovered_C_body_this_turn=False,coordinator_edited_model_source=False,original_reference_instruction_locations=len(reference_locations),compiled_instruction_locations=len(candidate_locations),original_BIWN_function_instructions_executed_on_candidate=0,full_D0_and_original_stack_argument_preserved=True,eleven_callee_saved_registers_preserved=True,no_nonprivate_writes=True,scope='3072original/compiledM68000cases cover all1024relevant-button combinations with3incomingD0words. Candidate is actual native GCC output from recovered C plus unchanged localRestorer ABI shim from a guided repair; the first raw draft was rejected and the coordinator supplied the instruction plan. Original reference code never runs on candidate. Caller-saved registers/CCR, live call-site assumptions, full game image, disc packaging and physical console are unverified. Linker address10000is an isolated test address, not a safe game patch location.')
  checkpoint();save(ROOT/'verification/native-button-digit-current.json',state)
  author.update(status='terminal_native_semantics_accepted',source_accepted=True,native_semantics_proof=str(ROOT/'verification/native-button-digit-current.json'),coordinator_edited_model_source=False)
  save(author_path,author);save(Path(author['directory'])/'protocol.json',author)
  print(json.dumps(dict(status=state['status'],directory=str(out),cases=len(rows),model_shim_accepted_unchanged=True)),flush=True)
 except BaseException as error:state.update(status='terminal_failed',error=repr(error));checkpoint();raise

if __name__=='__main__':main()
