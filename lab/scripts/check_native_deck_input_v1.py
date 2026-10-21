"""Real compiled68000 input caller versus original; helpers are fixtures.

Compare full CPU and nonarena RAM, helper-entry CPU/RAM, task-local stacks,
all slot fences, other slots and the coordinate frame/stack within this slot.
"""
import argparse
import ctypes as c
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import check_deck_input_source_v1 as original
from check_native_deck_coordinate_v1 import symbols

ROOT=original.ROOT; CPU=original.CPU; SP=original.SP; STOP=original.STOP
SRC=ROOT/'projects/black-ice-white-noise/restoration/native-m68k/deck-input-v1'
CODE=0x180000; ARENA=0x160000; POOL=0xc0928; SLOTS=101; STRIDE=1024
HELPERS={0xe4c0,0x10c6e,0x10e72,0x10cb6,0x1102a}
save=original.save; sha=original.sha; cpu_dict=original.cpu_dict

class Engine(original.Engine):
 def entry(self,memory,state):
  row=super().entry(memory,state)
  row['return_PC']=int.from_bytes(memory[state.registers[15]:state.registers[15]+4],'big')
  return row
 def compiled(self,ram,initial,case,syms,expected_entries,fallback=False):
  self.native.device.seed(ram,0);state=CPU.from_buffer_copy(bytes(initial));state.pc=syms['biwn_native_deck_input'];self.set_cpu(state,True)
  entries=[];trace=[];low=704;lookups=0;return_checks=0;original_steps=0
  task=int.from_bytes(ram[0xc0920:0xc0924],'big');slot=(task-POOL)//STRIDE if POOL<=task<POOL+SLOTS*STRIDE and not(task-POOL)%STRIDE else None
  base=ARENA+slot*STRIDE if slot is not None else None
  for _ in range(50000):
   state=self.cpu();pc=state.pc;sp=state.registers[15]
   if pc==STOP:break
   if base is not None and base<=sp<base+STRIDE:
    if pc==syms['biwn_native_input_helper_return']+12:
     lookups+=1;assert sp==base+144,(hex(pc),hex(sp))
    else:low=min(low,sp-base)
   if pc==syms['biwn_native_input_helper_return']:
    return_checks+=1;assert sp==last_helper_sp+4
   if pc in HELPERS:
    memory=bytearray(self.native.device.ram());normalized=bytearray(memory);normalized[ARENA:ARENA+SLOTS*STRIDE]=ram[ARENA:ARENA+SLOTS*STRIDE]
    wanted=expected_entries[len(entries)]['return_PC'];physical_ret=int.from_bytes(memory[sp:sp+4],'big')
    assert physical_ret==(wanted if fallback else syms['biwn_native_input_helper_return'])
    normalized[sp:sp+4]=wanted.to_bytes(4,'big');entries.append(self.entry(normalized,state))
    self.helper(memory,state,pc,case,len(entries)-1);self.native.device.seed(bytes(memory),0)
    last_helper_sp=sp;state.pc=physical_ret;state.registers[15]+=4
    if state.sr&0x2000:state.ssp=state.registers[15]
    else:state.usp=state.registers[15]
    self.set_cpu(state);continue
   if 0x11b4c<=pc<0x11d1a:
    assert fallback,hex(pc);original_steps+=1
   else:assert CODE<=pc<CODE+len(case['payload']),hex(pc)
   trace.append(pc);self.core.m68k_execute(1)
  else:raise AssertionError(('native input instruction bound',hex(pc)))
  assert len(entries)==len(expected_entries)
  assert fallback or lookups==return_checks==len(entries)
  memory=self.native.device.ram()
  for i in range(SLOTS):
   at=ARENA+i*STRIDE
   for lo,hi in [(0,16),(128,144),(256,272),(704,720),(1008,1024)]:
    assert memory[at+lo:at+hi]==ram[at+lo:at+hi],('fence',i,lo)
  if not fallback:
   assert low>272,('input C stack reaches frame fence',low)
   assert memory[ARENA:base]==ram[ARENA:base] and memory[base+STRIDE:ARENA+SLOTS*STRIDE]==ram[base+STRIDE:ARENA+SLOTS*STRIDE]
   assert memory[base:base+144]==ram[base:base+144] and memory[base+704:base+STRIDE]==ram[base+704:base+STRIDE], 'coordinate frame/stack touched'
   assert memory[base+244:base+248]==bytes(4),'active input flag not cleared'
   assert memory[task:task+38]==ram[task:task+38]
  normalized=bytearray(memory);normalized[ARENA:ARENA+SLOTS*STRIDE]=ram[ARENA:ARENA+SLOTS*STRIDE]
  return bytes(normalized),self.cpu(),entries,dict(instructions=len(trace),C_stack_low_offset=low,C_stack_bytes=704-low,SP_only_lookups=lookups,helper_return_checks=return_checks,original_input_steps=original_steps)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);args=ap.parse_args()
 out=ROOT/'verification/native-deck-input-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 state=dict(status='building',pid=os.getpid(),directory=str(out),whole_game_complete=False,native_disc_changed=False,new_training=False,authorship='Coordinator qualified input source and native ABI; no local model authorship claim.')
 def mark():save(out/'protocol.json',state)
 mark();build=out/'build'
 try:
  p=subprocess.run(['make','BUILD='+str(build),'ADDRESS='+hex(CODE),'ARENA_ADDRESS='+hex(ARENA)],cwd=SRC,capture_output=True,text=True);(out/'compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
  payload=(build/'native-input.bin').read_bytes();syms=symbols(build/'symbols.txt');engine=Engine();rows=[];coverage=set();fallbacks=[]
  def prepare(row,index,task=None,busy=False):
   ram,initial,case=row;memory=bytearray(ram);memory[CODE:CODE+len(payload)]=payload;memory[ARENA:ARENA+SLOTS*STRIDE]=bytes([0xa5])*(SLOTS*STRIDE)
   for i in range(SLOTS):memory[ARENA+i*STRIDE+244:ARENA+i*STRIDE+248]=bytes(4)
   valid_task=POOL+(index%SLOTS)*STRIDE;memory[0xc0920:0xc0924]=(valid_task if task is None else task).to_bytes(4,'big')
   guest_sp=valid_task+[0x3c0,0x3be,0x200][index%3];memory[guest_sp-256:guest_sp+32]=memory[SP-256:SP+32]
   initial=CPU.from_buffer_copy(bytes(initial));initial.registers[15]=guest_sp
   if initial.sr&0x2000:initial.ssp=guest_sp
   else:initial.usp=guest_sp
   if busy:memory[ARENA+(index%SLOTS)*STRIDE+244:ARENA+(index%SLOTS)*STRIDE+248]=(1).to_bytes(4,'big')
   return bytes(memory),initial,{**case,'payload':payload}
  try:
   selected=original.fixtures();selected=selected[:args.limit] if args.limit else selected
   for i,row in enumerate(selected):
    ram,initial,case=prepare(row,i);expected,cpu,entries,covered=engine.original(ram,initial,case);actual,got,observed,details=engine.compiled(ram,initial,case,syms,entries)
    if expected!=actual or cpu_dict(cpu)!=cpu_dict(got) or entries!=observed:
     save(out/'counterexample.json',dict(case=i,original_CPU=cpu_dict(cpu),native_CPU=cpu_dict(got),original_entries=entries,native_entries=observed,RAM_differences=[[hex(a),u,v]for a,(u,v)in enumerate(zip(expected,actual))if u!=v][:32],details=details));raise AssertionError(out/'counterexample.json')
    coverage|=covered;rows.append(dict(case=i,task=hex(POOL+(i%SLOTS)*STRIDE),full_CPU_nonarena_RAM_and_helper_entries_match=True,**details))
    if i%64==0:state.update(status='checking',completed=i+1,total=len(selected));mark();print(i+1,'/',len(selected),flush=True)
   if not args.limit:
    for task,busy in [(0,False),(POOL+1,False),(POOL+SLOTS*STRIDE,False),(POOL,True)]:
     ram,initial,case=prepare(selected[0],0,task,busy);expected,cpu,entries,_=engine.original(ram,initial,case);actual,got,observed,details=engine.compiled(ram,initial,case,syms,entries,True)
     assert expected==actual and cpu_dict(cpu)==cpu_dict(got) and entries==observed
     fallbacks.append(dict(task=hex(task),already_active=busy,**details))
  finally:engine.native.close()
  assert args.limit or len(coverage)==123
  save(out/'cases.json',rows);save(out/'fallbacks.json',fallbacks)
  paths=[Path(__file__),Path(original.__file__),SRC/'native-input.c',SRC/'native-input.S',SRC/'native-input.ld',SRC/'Makefile',original.SRC/'deck-input-source.c',original.SRC/'deck-input-source.h',original.SRC.parent/'deck-scene-source/deck-scene-contract.h',original.SRC.parent/'deck-coordinate-update-v2/deck-coordinate-contract.h']
  state.update(status='terminal_native_input_preflight_pass' if args.limit else 'terminal_native_input_original_CPU_and_helper_fixtures_match',completed=len(rows),fallback_cases=len(fallbacks),original_instruction_locations=len(coverage),task_slots=len({x['task']for x in rows}),code_bytes=len(payload),payload=str(build/'native-input.bin'),payload_sha256=sha(payload),symbols=syms,minimum_C_stack_offset=min(x['C_stack_low_offset']for x in rows),maximum_C_stack_bytes=max(x['C_stack_bytes']for x in rows),source_sha256={str(p):sha(p.read_bytes())for p in paths},scope=__doc__+' Finite helper fixtures, not real pad/GPU/scheduler/IRQ or native disc execution. Root-active fallback is original-code execution, separately counted.');mark()
  if not args.limit:save(ROOT/'verification/native-deck-input-v1-current.json',state)
  print(state['status'],len(rows),flush=True)
 except BaseException as error:state.update(status='terminal_failed',error=repr(error));mark();raise

if __name__=='__main__':main()
