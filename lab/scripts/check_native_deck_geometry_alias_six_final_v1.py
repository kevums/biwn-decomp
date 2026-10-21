"""Actual CPU coordinate-to-geometry and geometry-to-coordinate alias-busy fallback fixtures.

Injected helper JSRs are explicit component fixtures, not natural game calls.
The inner caller must execute its original body without changing the active
outer C frame/stack. CPU, non-arena RAM and helper entries match original.
"""
import argparse
from datetime import datetime,timezone
import json,os
from pathlib import Path
import check_native_deck_shared_v4 as m
ROOT=m.ROOT;save=m.save;sha=m.sha
def main():
 build=json.loads((ROOT/'verification/native-Deck-six-disc-build-v1-current.json').read_text());m.CODE=build['shared_Deck_code_address'];m.ARENA=build['deck_arena_address']
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,default=64);args=ap.parse_args();assert 1<=args.limit<=64
 out=ROOT/'verification/native-deck-geometry-alias-six-final-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);state=dict(status='preparing',pid=os.getpid(),directory=str(out),whole_game_complete=False,new_training=False)
 def mark():save(out/'protocol.json',state)
 mark()
 try:
  gate_path=ROOT/'verification/native-deck-shared-six-final-v1-current.json';gate=json.loads(gate_path.read_text());assert gate['completed']==5248
  for p,h in gate['source_sha256'].items():assert sha(Path(p).read_bytes())==h,p
  payload=Path(gate['payload']).read_bytes();assert sha(payload)==gate['payload_sha256'];syms=gate['symbols'];save(out/'component-gate.json',gate)
  coordinate_ram,coordinate_cpu,coordinate_case=m.coordinate.fixtures()[0]
  m.configure('geometry');_,geometry_cpu,geometry_case=m.fixtures('geometry')[0]
  geometry_ram=coordinate_ram;helpers=m.HELPERS['geometry']|{0xe26c};m.scene.HELPERS=helpers;engine=m.Engine('geometry');rows=[]
  def run(ram,initial,case,outer,native):
   inner='geometry'if outer=='coordinate'else'coordinate';injection=0xe26c if outer=='coordinate'else 0x10968;continuation=injection+6;memory=bytearray(ram)
   if native:
    for name in ['coordinate','geometry']:
     root=m.LAYOUT[name][0];memory[root:root+6]=b'\x4e\xf9'+syms['biwn_v4_'+name].to_bytes(4,'big')
   task=int.from_bytes(ram[0xc0920:0xc0924],'big');base=m.ARENA+task-m.POOL;engine.native.device.seed(bytes(memory),0);engine.set_cpu(initial,True)
   active={};entries=[];injected=0;protected=None;counts=dict(coordinate=0,geometry=0);fallbacks=dict(counts);returns=dict(counts)
   def normalize(raw,final=False):
    value=bytearray(raw);value[m.ARENA:m.ARENA+m.SLOTS*1024]=ram[m.ARENA:m.ARENA+m.SLOTS*1024]
    for name in ['coordinate','geometry']:
     root=m.LAYOUT[name][0];value[root:root+6]=ram[root:root+6]
    for sp,(physical,logical)in active.items():
     if int.from_bytes(value[sp:sp+4],'big')==physical:
      assert not final,'Compiler return remains in guest RAM';value[sp:sp+4]=logical.to_bytes(4,'big')
    return value
   def finish_helper(memory,cpu,target):
    if target==0xe26c:m.coordinate.Engine.gpu_fixture(engine,memory,cpu,case)
    else:m.scene.Engine.helper(engine,memory,cpu,target,case,len(entries)-1)
    cpu.pc=int.from_bytes(memory[cpu.registers[15]:cpu.registers[15]+4],'big');cpu.registers[15]+=4
    if cpu.sr&0x2000:cpu.ssp=cpu.registers[15]
    else:cpu.usp=cpu.registers[15]
    engine.native.device.seed(bytes(memory),0);engine.set_cpu(cpu)
   for step in range(200000):
    cpu=engine.cpu();pc=cpu.pc;sp=cpu.registers[15]
    if pc==m.STOP:break
    if native:
     for name in counts:
      if pc==syms['biwn_v4_'+name]:counts[name]+=1
      if pc==syms['biwn_v4_'+name+'_original_fallback']:fallbacks[name]+=1
      if pc==syms['biwn_v4_'+name+'_return']:returns[name]+=1
    if pc==continuation:
     memory=bytearray(engine.native.device.ram())
     if native:assert protected==[bytes(memory[base+16:base+134]),bytes(memory[base+832:base+1008])],'Alias callee changed suspended outer context/stack'
     finish_helper(memory,cpu,injection);continue
    if pc in helpers:
     memory=bytearray(engine.native.device.ram())
     if native:
      physical=int.from_bytes(memory[sp:sp+4],'big');ret=syms['biwn_v4_'+outer+'_helper_return']
      if physical==ret:
       frame=base+16;assert int.from_bytes(memory[frame+106:frame+110],'big')==sp;active[sp]=(ret,int.from_bytes(memory[frame+110:frame+114],'big'))
     entries.append(engine.entry(normalize(memory),cpu))
     if pc==injection and injected==0:
      injected+=1
      if native:protected=[bytes(memory[base+16:base+134]),bytes(memory[base+832:base+1008])]
     else:finish_helper(memory,cpu,pc);continue
    allowed=0x11ad4<=pc<0x11b4c or 0x11d1a<=pc<0x11e64 or 0xe540<=pc<0xe588 or pc==injection
    assert allowed or(native and m.CODE<=pc<m.CODE+len(payload)),hex(pc);engine.core.m68k_execute(1)
   else:raise AssertionError(('instruction bound',hex(pc)))
   raw=engine.native.device.ram();assert injected==1
   for slot in range(m.SLOTS):
    at=m.ARENA+slot*1024
    for lo,hi in m.FENCES:assert raw[at+lo:at+hi]==ram[at+lo:at+hi]
   if native:
    assert counts==dict(coordinate=1,geometry=1)and returns[outer]==1 and returns[inner]==0 and fallbacks[inner]==1 and fallbacks[outer]==0,(counts,returns,fallbacks)
    assert raw[base+130:base+134]==bytes(4)
    assert raw[m.ARENA:base]==ram[m.ARENA:base]and raw[base+1024:m.ARENA+m.SLOTS*1024]==ram[base+1024:m.ARENA+m.SLOTS*1024]
    allowed=set(range(16,134))|set(range(832,1008));assert all(i in allowed or raw[base+i]==ram[base+i]for i in range(1024))
   return bytes(normalize(raw,True)),engine.cpu(),entries,dict(instructions=step,native_entries=counts,native_returns=returns,fallback_entries=fallbacks,suspended_alias_frame_preserved=native)
  try:
   for outer in ['coordinate','geometry']:
    for i in range(args.limit):
     memory=bytearray(geometry_ram);memory[0x90000:0x90090]=memory[0x80000:0x80090];memory[m.CODE:m.CODE+len(payload)]=payload;memory[m.ARENA:m.ARENA+m.SLOTS*1024]=bytes([0xa5])*(m.SLOTS*1024)
     for slot in range(m.SLOTS):
      for _,offset,_,_ in m.LAYOUT.values():memory[m.ARENA+slot*1024+offset+114:m.ARENA+slot*1024+offset+118]=bytes(4)
     task=m.POOL+[0,1,6,100][i%4]*1024;sp=task+[0x3c0,0x3be,0x200][i%3];memory[sp-256:sp+32]=geometry_ram[m.SP-256:m.SP+32];memory[sp:sp+4]=m.STOP.to_bytes(4,'big');memory[0xc0920:0xc0924]=task.to_bytes(4,'big')
     initial=m.CPU.from_buffer_copy(bytes(coordinate_cpu if outer=='coordinate'else geometry_cpu));initial.pc=m.LAYOUT[outer][0];initial.sr=(0x2000 if i>=32 else 0)|(i%32);initial.registers[15]=sp;initial.usp=0x1d8000 if initial.sr&0x2000 else sp;initial.ssp=sp if initial.sr&0x2000 else 0x1ff000
     injection=0xe26c if outer=='coordinate'else 0x10968;inner='geometry'if outer=='coordinate'else'coordinate';memory[injection:injection+6]=b'\x4e\xb9'+m.LAYOUT[inner][0].to_bytes(4,'big');case={**coordinate_case,**geometry_case,'variant':i,'held':0,'pressed':0};ram=bytes(memory)
     expected,cpu,entries,_=run(ram,initial,case,outer,False);actual,got,observed,details=run(ram,initial,case,outer,True)
     if expected!=actual or m.cpu_dict(cpu)!=m.cpu_dict(got)or entries!=observed:
      save(out/'counterexample.json',dict(outer=outer,case=i,original_CPU=m.cpu_dict(cpu),native_CPU=m.cpu_dict(got),original_entries=entries,native_entries=observed,RAM_differences=[[hex(a),u,v]for a,(u,v)in enumerate(zip(expected,actual))if u!=v][:32]));raise AssertionError(out/'counterexample.json')
     rows.append(dict(outer=outer,case=i,mode=initial.sr&0x2000,flags=i%32,task=hex(task),full_CPU_nonarena_RAM_helper_entries_match=True,**details))
     if i%16==0:state.update(status='checking',completed=len(rows));mark();print(outer,i+1,flush=True)
  finally:engine.native.close()
  save(out/'cases.json',rows);paths=[ROOT/'verification/native-Deck-six-disc-build-v1-current.json',Path(__file__),gate_path,Path(m.__file__),Path(m.coordinate.__file__),Path(m.scene.__file__),Path(m.scene.__file__)]
  state.update(status='terminal_coordinate_geometry_cross_busy_fallback_match',completed=len(rows),source_sha256={str(p):sha(p.read_bytes())for p in paths},scope=__doc__+' 64eachdirection cover bothbanks/allCCR,4taskslots,3guestSPdepths. One injected JSR level, declared helper effects; no natural IRQ/reentry claim.');mark()
  if args.limit==64:save(ROOT/'verification/native-deck-geometry-alias-six-final-v1-current.json',state)
  print(state['status'],len(rows),flush=True)
 except BaseException as error:state.update(status='terminal_failed',error=repr(error));mark();raise
if __name__=='__main__':main()
