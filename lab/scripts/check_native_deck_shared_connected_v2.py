"""Original scan/input/coordinate CPU versus their three compiled callers.

Input and coordinate execute as nested CPU calls from scan. Five input
dependencies, face and GPU are declared fixtures; math E540 executes.
No scheduler, interrupt, physical-console or whole-game equivalence claim.
"""
import argparse
from collections import deque
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import check_native_deck_shared_v2 as component

ROOT=component.ROOT; CPU=component.CPU
save=component.save; sha=component.sha; cpu_dict=component.cpu_dict
INPUT_HELPERS=component.HELPERS['input']
ROOTS={value[0]:name for name,value in component.LAYOUT.items()}
CALLEES={0x11b4c,0x11d1a,0x1186a,0xe26c,0xe540}|INPUT_HELPERS

class Engine(component.Engine):
 def __init__(self):super().__init__('scan')
 def run(self,ram,initial,case,syms,native,payload):
  memory=bytearray(ram)
  if native:
   for address,name in ROOTS.items():memory[address:address+6]=b'\x4e\xf9'+syms['biwn_v2_'+name].to_bytes(4,'big')
  self.native.device.seed(bytes(memory),0);self.set_cpu(initial,True)
  task=int.from_bytes(ram[0xc0920:0xc0924],'big');base=component.ARENA+task-component.POOL
  entries=[];counts={name:0 for name in component.LAYOUT};returns=dict(counts);low={name:value[3] for name,value in component.LAYOUT.items()}
  active=[];trace=deque(maxlen=20);suspended=[];protected_checks=0;coverage=set()
  def normalize(raw,final=False):
   result=bytearray(raw)
   if native:
    result[component.ARENA:component.ARENA+component.SLOTS*1024]=ram[component.ARENA:component.ARENA+component.SLOTS*1024]
    for address in ROOTS:result[address:address+6]=ram[address:address+6]
    for name in component.LAYOUT:
     at=base+component.LAYOUT[name][1]
     if int.from_bytes(raw[at+114:at+118],'big'):
      sp=int.from_bytes(raw[at+106:at+110],'big');physical=syms['biwn_v2_'+name+'_helper_return'];logical=int.from_bytes(raw[at+110:at+114],'big')
      if int.from_bytes(raw[sp:sp+4],'big')==physical:
       assert not final,'Unrestored compiler return in guest stack'
       result[sp:sp+4]=logical.to_bytes(4,'big')
   return result
  for step in range(250000):
   state=self.cpu();pc=state.pc;sp=state.registers[15];trace.append([hex(pc),hex(sp)])
   if pc==component.STOP:break
   if native:
    for name,(_,offset,lower,top)in component.LAYOUT.items():
     if pc==syms['biwn_v2_'+name]:
      counts[name]+=1
      if active:
       outer=active[-1];_,off,lo,hi=component.LAYOUT[outer]
       raw=self.native.device.ram();suspended.append((name,outer,bytes(raw[base+off:base+off+118]),bytes(raw[base+lo:base+hi])))
      active.append(name)
     if pc==syms['biwn_v2_'+name+'_return']:
      assert active.pop()==name;returns[name]+=1
      if suspended and suspended[-1][0]==name:
       _,outer,frame,stack=suspended.pop();_,off,lo,hi=component.LAYOUT[outer];raw=self.native.device.ram()
       assert raw[base+off:base+off+118]==frame and raw[base+lo:base+hi]==stack,'Nested caller changed suspended outer frame/stack'
       protected_checks+=1
    if component.ARENA<=sp<component.ARENA+component.SLOTS*1024:
     assert active
     name=active[-1];_,offset,lower,top=component.LAYOUT[name];ret=syms['biwn_v2_'+name+'_helper_return']
     if ret+12<=pc<syms['biwn_v2_'+name+'_capture_end']:
      displacement={12:0,16:0,20:64}.get(pc-ret,4);assert sp==base+offset+displacement
     else:low[name]=min(low[name],sp-base);assert base+lower<=sp<=base+top,(name,'C stack outside partition',hex(pc),hex(sp))
   if pc in CALLEES:
    raw=bytearray(self.native.device.ram());entries.append(self.entry(normalize(raw),state))
    if pc in INPUT_HELPERS or pc in [0x1186a,0xe26c]:
     if pc in INPUT_HELPERS:component.inputs.Engine.helper(self,raw,state,pc,case,len(entries)-1)
     elif pc==0x1186a:component.scene.Engine.helper(self,raw,state,pc,case,len(entries)-1)
     else:self.gpu_fixture(raw,state,case)
     self.native.device.seed(bytes(raw),0);state.pc=int.from_bytes(raw[sp:sp+4],'big');state.registers[15]+=4
     if state.sr&0x2000:state.ssp=state.registers[15]
     else:state.usp=state.registers[15]
     self.set_cpu(state);continue
   in_original=0x11828<=pc<0x1186a or 0x11b4c<=pc<0x11e64
   if native:
    assert pc in ROOTS or component.CODE<=pc<component.CODE+len(payload)or 0xe540<=pc<0xe588,dict(pc=hex(pc),trace=list(trace))
   else:assert in_original or 0xe540<=pc<0xe588,dict(pc=hex(pc),trace=list(trace))
   if in_original:coverage.add(pc)
   self.core.m68k_execute(1)
  else:raise AssertionError(('work bound',list(trace)))
  raw=self.native.device.ram()
  for slot in range(component.SLOTS):
   at=component.ARENA+slot*1024
   for lo,hi in component.FENCES:assert raw[at+lo:at+hi]==ram[at+lo:at+hi],('fence',slot,lo)
  if native:
   assert not active and not suspended
   assert counts==returns and counts['scan']==1 and counts['input']==counts['coordinate'],(counts,returns)
   assert raw[component.ARENA:base]==ram[component.ARENA:base]and raw[base+1024:component.ARENA+component.SLOTS*1024]==ram[base+1024:component.ARENA+component.SLOTS*1024]
   assert raw[task:task+38]==ram[task:task+38]
   for name,(_,offset,_,_)in component.LAYOUT.items():assert raw[base+offset+114:base+offset+118]==bytes(4)
   allowed=set()
   for _,offset,lower,top in component.LAYOUT.values():allowed.update(range(offset,offset+118));allowed.update(range(lower,top))
   assert all(i in allowed or raw[base+i]==ram[base+i]for i in range(1024))
  return bytes(normalize(raw,True)),self.cpu(),entries,dict(instructions=step,native_entries=counts,native_returns=returns,minimum_C_stack_offsets=low,suspended_frame_checks=protected_checks,original_instruction_locations=len(coverage))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,default=128);args=ap.parse_args();assert 1<=args.limit<=256
 out=ROOT/'verification/native-deck-shared-connected-v2'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 state=dict(status='preparing',pid=os.getpid(),directory=str(out),whole_game_complete=False,native_disc_changed=False,new_training=False)
 def mark():save(out/'protocol.json',state)
 mark()
 try:
  gate_path=ROOT/'verification/native-deck-shared-v2-current.json';gate=json.loads(gate_path.read_text());assert gate['completed']==2880
  for p,h in gate['source_sha256'].items():assert sha(Path(p).read_bytes())==h,p
  payload=Path(gate['payload']).read_bytes();assert sha(payload)==gate['payload_sha256'];syms=gate['symbols'];save(out/'component-gate.json',gate)
  component.configure('scan');scan_vectors=component.fixtures('scan');input_vectors=component.inputs.fixtures();coord_vectors=component.coordinate.fixtures()
  # The helper methods assert their explicit shared dependency set.
  component.scene.HELPERS=CALLEES
  engine=Engine();rows=[]
  try:
   for i in range(args.limit):
    scan_ram,initial,scan_case=scan_vectors[i];input_ram,_,input_case=input_vectors[(i*37)%len(input_vectors)];coord_ram,_,coord_case=coord_vectors[(i*19)%len(coord_vectors)]
    memory=bytearray(coord_ram)
    for lo,hi in [(0x80088,0x8008a),(0x90088,0x9008a),(0x49ba4,0x49bb0),(0x403cc,0x403ce),(0x403dc,0x4040e)]:memory[lo:hi]=input_ram[lo:hi]
    # Record poll can select the second descriptor on any case.
    memory[0x90000:0x90002]=coord_case['index'].__mod__(16).to_bytes(2,'big')
    for slot in range(16):
     a=0x400ea+46*slot;memory[a:a+2]=scan_ram[a:a+2]
    memory[component.CODE:component.CODE+len(payload)]=payload;memory[component.ARENA:component.ARENA+component.SLOTS*1024]=bytes([0xa5])*(component.SLOTS*1024)
    for slot in range(component.SLOTS):
     for _,offset,_,_ in component.LAYOUT.values():memory[component.ARENA+slot*1024+offset+114:component.ARENA+slot*1024+offset+118]=bytes(4)
    task=component.POOL+(i%component.SLOTS)*1024;sp=task+[0x3c0,0x3be,0x200][i%3];memory[sp-256:sp+32]=scan_ram[component.SP-256:component.SP+32];memory[sp:sp+4]=component.STOP.to_bytes(4,'big');memory[0xc0920:0xc0924]=task.to_bytes(4,'big')
    initial=CPU.from_buffer_copy(bytes(initial));initial.registers[15]=sp
    if initial.sr&0x2000:initial.ssp=sp
    else:initial.usp=sp
    case={**coord_case,**input_case,**scan_case};ram=bytes(memory)
    expected,cpu,entries,original=engine.run(ram,initial,case,syms,False,payload);actual,got,observed,details=engine.run(ram,initial,case,syms,True,payload)
    if expected!=actual or cpu_dict(cpu)!=cpu_dict(got)or entries!=observed:
     save(out/'counterexample.json',dict(case=i,original_CPU=cpu_dict(cpu),native_CPU=cpu_dict(got),original_entries=entries,native_entries=observed,RAM_differences=[[hex(a),u,v]for a,(u,v)in enumerate(zip(expected,actual))if u!=v][:32],details=details));raise AssertionError(out/'counterexample.json')
    rows.append(dict(case=i,task=hex(task),full_CPU_nonarena_RAM_helper_entries_and_suspended_frames_match=True,**details))
    if i%8==0:state.update(status='checking',completed=len(rows),total=args.limit);mark();print('case',i+1,'/',args.limit,flush=True)
  finally:engine.native.close()
  save(out/'cases.json',rows)
  paths=[Path(__file__),out/'component-gate.json',Path(component.__file__),Path(component.coordinate.__file__),Path(component.inputs.__file__),Path(component.scene.__file__)]
  state.update(status='terminal_three_compiled_callers_nested_CPU_match',completed=len(rows),task_slots=len({row['task']for row in rows}),native_entries={name:sum(row['native_entries'][name]for row in rows)for name in component.LAYOUT},suspended_frame_checks=sum(row['suspended_frame_checks']for row in rows),minimum_C_stack_offsets={name:min(row['minimum_C_stack_offsets'][name]for row in rows)for name in component.LAYOUT},source_sha256={str(p):sha(p.read_bytes())for p in paths},scope=__doc__);mark()
  if args.limit>=128:save(ROOT/'verification/native-deck-shared-connected-v2-current.json',state)
  print(state['status'],state['native_entries'],flush=True)
 except BaseException as error:state.update(status='terminal_failed',error=repr(error));mark();raise

if __name__=='__main__':main()
