"""Five in-place native callers (input/face and coordinate/geometry share guarded slots) versus original CPU, with declared helpers."""
import argparse
import ctypes as c
import struct
from collections import deque
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import subprocess
import check_deck_coordinate_source_v1 as coordinate
import check_deck_scene_source_v1 as scene
import check_deck_input_source_v1 as inputs
import check_deck_face_contact_v1 as faces
from check_native_deck_coordinate_v1 import symbols

ROOT=coordinate.ROOT;CPU=coordinate.CPU;SP=coordinate.SP;STOP=coordinate.STOP
SRC=ROOT/'projects/black-ice-white-noise/restoration/native-m68k/deck-shared-v33-geometry-records-v1'
CODE=0x180000;ARENA=0x1b0000;POOL=0xc0928;SLOTS=101;STRIDE=1024
LAYOUT={'coordinate':(0x11d1a,16,832,1008),'input':(0x11b4c,144,608,816),'face':(0x1186a,144,608,816),'scan':(0x11828,272,416,592),'geometry':(0x11ad4,16,832,1008)}
FENCES=[(0,16),(136,144),(264,272),(400,416),(592,608),(816,832),(1008,1024)]
HELPERS={'coordinate':{0xe26c,0xe540},'input':{0xe4c0,0x10c6e,0x10e72,0x10cb6,0x1102a},'scan':{0x11b4c,0x1186a,0x11d1a},'face':{0x10c6e,0x10cb6},'geometry':{0x10968,0x11384,0x10ba4,0x1142e,0x10734}}
save=coordinate.save;sha=coordinate.sha;cpu_dict=coordinate.cpu_dict

class Engine(coordinate.Engine):
 def __init__(self,kind):super().__init__();self.kind=kind
 def entry(self,memory,cpu):
  return dict(CPU=cpu_dict(cpu),RAM=sha(memory),arguments=bytes(memory[cpu.registers[15]+4:cpu.registers[15]+24]).hex(),return_PC=int.from_bytes(memory[cpu.registers[15]:cpu.registers[15]+4],'big'))
 def reset_body(self,memory,cpu):
  self.native.device.seed(bytes(memory),0);self.set_cpu(cpu,True)
  for step in range(64):
   pc=self.core.m68k_get_reg(None,16)
   if pc==0x110d2:break
   assert 0x1102a<=pc<0x110d4,hex(pc);self.core.m68k_execute(1)
  else:raise AssertionError('original reset bound')
  memory[:]=self.native.device.ram();c.memmove(c.byref(cpu),c.byref(self.cpu()),c.sizeof(CPU))
 def helper(self,memory,cpu,target,case,index):
  if self.kind=='input'and target==0x1102a:return self.reset_body(memory,cpu)
  if self.kind=='input':return inputs.Engine.helper(self,memory,cpu,target,case,index)
  if self.kind=='face':return faces.Engine.helper(self,memory,cpu,target,case,index)
  return scene.Engine.helper(self,memory,cpu,target,case,index)
 def reference(self,ram,initial,case):
  if self.kind=='coordinate':return coordinate.Engine.original(self,ram,initial,case)
  return scene.Engine.original(self,ram,initial,case)
 def compiled(self,ram,initial,case,syms,expected_entries,fallback=False):
  root,offset,lower,top=LAYOUT[self.kind];task=int.from_bytes(ram[0xc0920:0xc0924],'big');delta=task-POOL
  base=ARENA+delta if 0<=delta<SLOTS*STRIDE and delta%STRIDE==0 else None
  helper_return=syms['biwn_v4_'+self.kind+'_helper_return'];state=CPU.from_buffer_copy(bytes(initial));state.pc=syms['biwn_v4_'+self.kind]
  self.native.device.seed(ram,0);self.set_cpu(state,True);entries=[];low=top;lookups=0;original_steps=0;helper_returns=0;reset_entries=0;trace=deque(maxlen=24)
  for step in range(100000):
   state=self.cpu();pc=state.pc;sp=state.registers[15];trace.append([hex(pc),hex(sp)])
   if pc==STOP:break
   if base is not None and base<=sp<base+STRIDE:
    if helper_return+12<=pc<syms['biwn_v4_'+self.kind+'_capture_end']:
     displacement={12:0,16:0,20:64}.get(pc-helper_return,4)
     assert sp==base+offset+displacement,('direct capture SP',hex(pc),hex(sp))
     if pc==helper_return+12:lookups+=1
    else:low=min(low,sp-base)
   if pc==helper_return:helper_returns+=1;assert sp==last_helper_sp+4
   if pc==syms['biwn_v18_scene_reset_marker']:
    assert not fallback and self.kind=='input'
    memory=self.native.device.ram();at=int.from_bytes(memory[sp+4:sp+8],'big');assert at==base+offset
    values=struct.unpack('>19IH',memory[at+4:at+82]);virtual=CPU();virtual.registers[:]=values[:16];virtual.pc,virtual.usp,virtual.ssp,virtual.sr=values[16:]
    if virtual.sr&0x2000:virtual.usp=initial.usp
    else:virtual.ssp=initial.ssp
    assert virtual.pc==0x1102a
    normalized=bytearray(memory);normalized[ARENA:ARENA+SLOTS*STRIDE]=ram[ARENA:ARENA+SLOTS*STRIDE]
    entries.append(self.entry(normalized,virtual));reset_entries+=1
   if pc in HELPERS[self.kind]:
    memory=bytearray(self.native.device.ram());normalized=bytearray(memory);normalized[ARENA:ARENA+SLOTS*STRIDE]=ram[ARENA:ARENA+SLOTS*STRIDE]
    sp=state.registers[15];wanted=expected_entries[len(entries)]['return_PC'];physical=int.from_bytes(memory[sp:sp+4],'big')
    assert physical==(wanted if fallback else helper_return)
    normalized[sp:sp+4]=wanted.to_bytes(4,'big');entries.append(self.entry(normalized,state));last_helper_sp=sp
    if pc==0xe540:pass
    else:
     if pc==0xe26c:self.gpu_fixture(memory,state,case)
     else:self.helper(memory,state,pc,case,len(entries)-1)
     self.native.device.seed(bytes(memory),0);state.pc=physical;state.registers[15]+=4
     if state.sr&0x2000:state.ssp=state.registers[15]
     else:state.usp=state.registers[15]
     self.set_cpu(state);continue
   bounds={'coordinate':(0x11d1a,0x11e64),'input':(0x11b4c,0x11d1a),'face':(0x1186a,0x11ad4),'scan':(0x11828,0x1186a),'geometry':(0x11ad4,0x11b4c)}[self.kind]
   if bounds[0]<=pc<bounds[1]:assert fallback,hex(pc);original_steps+=1
   else:assert CODE<=pc<CODE+len(case['payload']) or 0xe540<=pc<0xe588,dict(pc=hex(pc),sp=hex(sp),low=low,trace=list(trace))
   self.core.m68k_execute(1)
  else:raise AssertionError(('instruction bound',self.kind,hex(pc)))
  assert len(entries)==len(expected_entries)
  assert fallback or lookups==helper_returns==len(entries)-reset_entries
  memory=self.native.device.ram()
  for slot in range(SLOTS):
   at=ARENA+slot*STRIDE
   for lo,hi in FENCES:assert memory[at+lo:at+hi]==ram[at+lo:at+hi],('fence',self.kind,slot,lo,low)
  if not fallback:
   assert low>=lower,(self.kind,'C stack exceeds partition',low,lower)
   assert memory[ARENA:base]==ram[ARENA:base]and memory[base+STRIDE:ARENA+SLOTS*STRIDE]==ram[base+STRIDE:ARENA+SLOTS*STRIDE]
   assert memory[base+offset+114:base+offset+118]==bytes(4)
   allowed=set(range(offset,offset+118))|set(range(lower,top))
   assert all(i in allowed or memory[base+i]==ram[base+i]for i in range(STRIDE)),(self.kind,'other caller context/stack touched')
   assert memory[task:task+38]==ram[task:task+38]
  normalized=bytearray(memory);normalized[ARENA:ARENA+SLOTS*STRIDE]=ram[ARENA:ARENA+SLOTS*STRIDE]
  return bytes(normalized),self.cpu(),entries,dict(instructions=step,C_stack_low=low,C_stack_bytes=top-low,SP_only_lookups=lookups,original_body_steps=original_steps,helper_returns=helper_returns,native_reset_entries=reset_entries)

def configure(kind):
 scene.HELPERS=HELPERS[kind]
 scene.ROOTS={LAYOUT[kind][0]:{'coordinate':0x11e64,'input':0x11d1a,'face':0x11ad4,'scan':0x1186a,'geometry':0x11b4c}[kind]}

def fixtures(kind):
 if kind=='coordinate':return coordinate.fixtures()
 if kind=='input':return inputs.fixtures()
 if kind=='face':return list(faces.fixtures())
 scene.ROOTS={0x11ad4:0x11b4c}if kind=='geometry'else{0x11828:0x1186a};return scene.fixtures()

def main():
 global SRC
 ap=argparse.ArgumentParser();ap.add_argument('--profile',choices=['deck-shared-v18-scene-reset','deck-shared-v33-geometry-records-v1'],default='deck-shared-v33-geometry-records-v1');ap.add_argument('--limit',type=int);ap.add_argument('--kind',choices=list(LAYOUT));args=ap.parse_args();SRC=SRC.parent/args.profile
 out=ROOT/'verification/native-deck-retained-geometry-records-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 state=dict(status='building',pid=os.getpid(),directory=str(out),native_disc_changed=False,whole_game_complete=False,new_training=False)
 def mark():save(out/'protocol.json',state)
 mark()
 try:
  build=out/'build';p=subprocess.run(['make','BUILD='+str(build),'ADDRESS='+hex(CODE),'ARENA_ADDRESS='+hex(ARENA)],cwd=SRC,capture_output=True,text=True);(out/'compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
  payload=(build/'native-shared.bin').read_bytes();syms=symbols(build/'symbols.txt');rows=[];coverage={};fallbacks=[]
  for kind in ([args.kind]if args.kind else [k for k in LAYOUT if k!='geometry']):
   configure(kind);selected=fixtures(kind);selected=selected[:args.limit]if args.limit else selected;engine=Engine(kind);covered=set()
   def prepare(row,index,task_override=None,busy=False):
    ram,initial,case=row;memory=bytearray(ram);memory[CODE:CODE+len(payload)]=payload;memory[ARENA:ARENA+SLOTS*STRIDE]=bytes([0xa5])*(SLOTS*STRIDE)
    for slot in range(SLOTS):
     for _,offset,_,_ in LAYOUT.values():memory[ARENA+slot*STRIDE+offset+114:ARENA+slot*STRIDE+offset+118]=bytes(4)
    task=POOL+(index%SLOTS)*STRIDE;memory[0xc0920:0xc0924]=(task if task_override is None else task_override).to_bytes(4,'big');sp=task+[0x3c0,0x3be,0x200][index%3];memory[sp-256:sp+32]=memory[SP-256:SP+32]
    initial=CPU.from_buffer_copy(bytes(initial));initial.registers[15]=sp
    if initial.sr&0x2000:initial.ssp=sp
    else:initial.usp=sp
    if busy:
     offset=LAYOUT[kind][1];memory[ARENA+(index%SLOTS)*STRIDE+offset+114:ARENA+(index%SLOTS)*STRIDE+offset+118]=(1).to_bytes(4,'big')
    return bytes(memory),initial,{**case,'payload':payload}
   try:
    for i,row in enumerate(selected):
     ram,initial,case=prepare(row,i);expected,cpu,entries,seen,*_=engine.reference(ram,initial,case);actual,got,observed,details=engine.compiled(ram,initial,case,syms,entries)
     if expected!=actual or cpu_dict(cpu)!=cpu_dict(got)or entries!=observed:
      save(out/'counterexample.json',dict(kind=kind,case=i,original_CPU=cpu_dict(cpu),native_CPU=cpu_dict(got),original_entries=entries,native_entries=observed,RAM_differences=[[hex(a),u,v]for a,(u,v)in enumerate(zip(expected,actual))if u!=v][:32],details=details));raise AssertionError(out/'counterexample.json')
     covered|=seen;rows.append(dict(kind=kind,case=i,task=hex(POOL+(i%SLOTS)*STRIDE),full_CPU_nonarena_RAM_and_helper_entries_match=True,**details))
     if i%64==0:state.update(status='checking',completed=len(rows),kind=kind,case=i+1);mark();print(kind,i+1,'/',len(selected),flush=True)
    if not args.limit:
     for task,busy in [(0,False),(POOL+1,False),(POOL+SLOTS*STRIDE,False),(POOL,True)]:
      ram,initial,case=prepare(selected[0],0,task,busy);expected,cpu,entries,_,*_=engine.reference(ram,initial,case);actual,got,observed,details=engine.compiled(ram,initial,case,syms,entries,True);assert expected==actual and cpu_dict(cpu)==cpu_dict(got)and entries==observed
      fallbacks.append(dict(kind=kind,task=hex(task),busy=busy,**details))
   finally:engine.native.close()
   coverage[kind]=len(covered)
  save(out/'cases.json',rows);save(out/'fallbacks.json',fallbacks)
  paths=[Path(__file__),SRC/'native-shared.c',SRC/'native-shared.S',SRC/'native-shared.ld',*list(SRC.glob('*.inc')),SRC/'Makefile',SRC/'native-alu.h',SRC.parent.parent/'experimental/deck-debug-overlay-v1/coordinator-reference.c',SRC.parent.parent/'experimental/deck-debug-overlay-v1/debug-contract.h',ROOT/'projects/black-ice-white-noise/restoration/experimental/deck-coordinate-local-v6-hybrid/deck-coordinate-hybrid.c',inputs.SRC/'deck-input-source.c',scene.SRC/'deck-scene-source.c',Path(coordinate.__file__),Path(inputs.__file__),Path(scene.__file__),Path(faces.__file__),faces.SRC/'deck-face-contact.c',faces.SRC/'deck-face-contact.h',faces.SRC.parent/'deck-scene-source/deck-scene-contract.h',faces.SRC.parent/'deck-coordinate-update-v2/deck-coordinate-contract.h']
  paths.append(ROOT/'projects/black-ice-white-noise/restoration/experimental/geometry-records-structured-v1/coordinator-reference.inc')
  state.update(status='terminal_shared_v4_preflight_pass'if args.limit else'terminal_shared_v4_original_CPU_helper_fixtures_match',completed=len(rows),counts={k:sum(x['kind']==k for x in rows)for k in LAYOUT},coverage=coverage,fallback_cases=len(fallbacks),code_bytes=len(payload),payload=str(build/'native-shared.bin'),payload_sha256=sha(payload),symbols=syms,layout=LAYOUT,fences=FENCES,maximum_C_stack_bytes={k:max((x['C_stack_bytes']for x in rows if x['kind']==k),default=0)for k in LAYOUT},minimum_C_stack_offset={k:min((x['C_stack_low']for x in rows if x['kind']==k),default=0)for k in LAYOUT},source_sha256={str(p):sha(p.read_bytes())for p in paths},scope=__doc__+' Individual callers; scan callees and input/face helpers except1102A are fixtures.1102A executes original CPU in the reference and compiled C at native marker entries;both complete input-caller results match. Input/face and coordinate/geometry alias active-guarded frames; this matrix does not itself establish actual alias nesting, coordinate GPU is a fixture and E540 executes. Actual nested callers, scheduler/IRQ and disc remain unverified.');mark()
  if not args.limit and not args.kind:save(ROOT/'verification/native-deck-retained-geometry-records-v1-current.json',state)
  print(state['status'],state['maximum_C_stack_bytes'],flush=True)
 except BaseException as error:state.update(status='terminal_failed',error=repr(error));mark();raise

if __name__=='__main__':main()
