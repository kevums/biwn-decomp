"""Actual compiled input/coordinate nesting via declared JSR helper fixtures.

Both lanes execute CPU instructions, including the injected helper JSR.
This is an explicit component witness, not a natural scheduler/IRQ claim.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import check_native_deck_input_v1 as inp
import check_deck_coordinate_source_v1 as coord

ROOT=inp.ROOT; save=inp.save; sha=inp.sha; CPU=inp.CPU
COORD_SRC=ROOT/'projects/black-ice-white-noise/restoration/native-m68k/deck-coordinate-v1'
COORD_CODE=0x188000

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,default=64);args=ap.parse_args();assert 1<=args.limit<=64
 out=ROOT/'verification/native-deck-input-nesting-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 state=dict(status='building',pid=os.getpid(),directory=str(out),new_training=False,whole_game_complete=False)
 def mark():save(out/'protocol.json',state)
 mark()
 try:
  builds={}
  for name,source,address,binary in [('input',inp.SRC,inp.CODE,'native-input.bin'),('coordinate',COORD_SRC,COORD_CODE,'native-deck.bin')]:
   dest=out/name;p=subprocess.run(['make','BUILD='+str(dest),'ADDRESS='+hex(address),'ARENA_ADDRESS='+hex(inp.ARENA)],cwd=source,capture_output=True,text=True);(out/(name+'-compiler.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
   builds[name]=(address,(dest/binary).read_bytes(),inp.symbols(dest/'symbols.txt'))
  engine=inp.Engine();rows=[];vectors=inp.original.fixtures();coords=coord.fixtures()
  def run(ram,initial,case,direction,native):
   memory=bytearray(ram)
   if native:
    for root,name in [(0x11b4c,'input'),(0x11d1a,'coordinate')]:memory[root:root+6]=b'\x4e\xf9'+builds[name][2]['biwn_native_deck_'+name].to_bytes(4,'big')
   engine.native.device.seed(bytes(memory),0);engine.set_cpu(initial,True)
   active={};entries=[];counts=dict(input=0,coordinate=0);lows=dict(input=704,coordinate=1008);injected=0;protected=None
   slot=(int.from_bytes(ram[0xc0920:0xc0924],'big')-inp.POOL)//1024;base=inp.ARENA+slot*1024
   injection=0xe4c0 if direction=='input_calls_coordinate' else 0xe26c
   continuation=injection+6
   protected_slices=[(144,704)] if direction=='input_calls_coordinate' else [(0,144),(704,1024)]
   def normalize(raw,returns=True):
    normalized=bytearray(raw);normalized[inp.ARENA:inp.ARENA+inp.SLOTS*1024]=ram[inp.ARENA:inp.ARENA+inp.SLOTS*1024]
    for root in [0x11b4c,0x11d1a]:normalized[root:root+6]=ram[root:root+6]
    for sp,(physical,logical) in active.items():
     if int.from_bytes(normalized[sp:sp+4],'big')==physical:
      assert returns,'Compiler return remains in final guest RAM'
      normalized[sp:sp+4]=logical.to_bytes(4,'big')
    return normalized
   for step in range(100000):
    cpu=engine.cpu();pc=cpu.pc;sp=cpu.registers[15]
    if pc==inp.STOP:break
    if native:
     for name,(_,_,syms) in builds.items():
      if pc==syms['biwn_native_deck_'+name]:counts[name]+=1
      # SP temporarily addresses frame metadata before restoring the C SP.
      if base<=sp<base+1024 and pc!=syms['biwn_native_'+('input' if name=='input' else 'deck')+'_helper_return']+12:
       if name=='input' and base+272<sp<base+704:lows[name]=min(lows[name],sp-base)
       if name=='coordinate' and base+720<sp<base+1008:lows[name]=min(lows[name],sp-base)
    if pc==continuation:
     current=engine.native.device.ram()
     if native:
      assert protected is not None
      assert [current[base+lo:base+hi]for lo,hi in protected_slices]==protected,'Nested callee changed suspended outer frame/stack'
     memory=bytearray(current)
     if injection==0xe4c0:engine.helper(memory,cpu,injection,case,0)
     else:engine.gpu_fixture(memory,cpu,case)
     engine.native.device.seed(bytes(memory),0);cpu.pc=int.from_bytes(memory[sp:sp+4],'big');cpu.registers[15]+=4
     if cpu.sr&0x2000:cpu.ssp=cpu.registers[15]
     else:cpu.usp=cpu.registers[15]
     engine.set_cpu(cpu);continue
    if pc in inp.HELPERS or pc in [0xe26c,0xe540]:
     memory=bytearray(engine.native.device.ram())
     if native:
      physical=int.from_bytes(memory[sp:sp+4],'big')
      for name,(_,_,syms) in builds.items():
       ret=syms['biwn_native_'+('input' if name=='input' else 'deck')+'_helper_return']
       if physical==ret:
        frame=base+(144 if name=='input' else 16);assert int.from_bytes(memory[frame+88:frame+92],'big')==sp
        active[sp]=(ret,int.from_bytes(memory[frame+92:frame+96],'big'))
     entries.append(engine.entry(normalize(memory),cpu))
     if pc==injection:
      injected+=1;assert injected==1
      if native:protected=[bytes(memory[base+lo:base+hi])for lo,hi in protected_slices]
      # Execute the declared actual JSR fixture, preserving its natural stack.
     elif pc in inp.HELPERS or pc==0xe26c:
      if pc==0xe26c:engine.gpu_fixture(memory,cpu,case)
      else:engine.helper(memory,cpu,pc,case,len(entries)-1)
      engine.native.device.seed(bytes(memory),0);cpu.pc=int.from_bytes(memory[sp:sp+4],'big');cpu.registers[15]+=4
      if cpu.sr&0x2000:cpu.ssp=cpu.registers[15]
      else:cpu.usp=cpu.registers[15]
      engine.set_cpu(cpu);continue
    if native:
     assert pc in [0x11b4c,0x11d1a,injection] or 0xe540<=pc<0xe588 or any(a<=pc<a+len(payload)for a,payload,_ in builds.values()),hex(pc)
    else:assert 0x11b4c<=pc<0x11e64 or 0xe540<=pc<0xe588 or pc==injection,hex(pc)
    engine.core.m68k_execute(1)
   else:raise AssertionError(('nested bound',hex(pc)))
   raw=engine.native.device.ram()
   for i in range(inp.SLOTS):
    at=inp.ARENA+i*1024
    for lo,hi in [(0,16),(128,144),(256,272),(704,720),(1008,1024)]:assert raw[at+lo:at+hi]==ram[at+lo:at+hi],('fence',i,lo)
   assert injected==1
   if native:assert counts==dict(input=1,coordinate=1),counts
   return bytes(normalize(raw,False)),engine.cpu(),entries,dict(native_entries=counts,C_stack_low_offsets=lows,instructions=step)
  try:
   for direction in ['input_calls_coordinate','coordinate_calls_input']:
    for i in range(args.limit):
     input_ram,input_cpu,input_case=vectors[(i*37)%2048];coord_ram,coord_cpu,coord_case=coords[i]
     memory=bytearray(coord_ram)
     for lo,hi in [(0x80088,0x8008a),(0x90088,0x9008a),(0x49ba4,0x49bb0),(0x403cc,0x403ce),(0x403dc,0x4040e)]:memory[lo:hi]=input_ram[lo:hi]
     for name,(address,payload,_) in builds.items():memory[address:address+len(payload)]=payload
     memory[inp.ARENA:inp.ARENA+inp.SLOTS*1024]=bytes([0xa5])*(inp.SLOTS*1024)
     for j in range(inp.SLOTS):memory[inp.ARENA+j*1024+244:inp.ARENA+j*1024+248]=bytes(4)
     task=inp.POOL+[0,1,6,100][i%4]*1024;sp=task+[0x3c0,0x3be,0x200][i%3]
     initial=CPU.from_buffer_copy(bytes(input_cpu if direction=='input_calls_coordinate' else coord_cpu));memory[sp-256:sp+32]=memory[inp.SP-256:inp.SP+32];memory[sp:sp+4]=inp.STOP.to_bytes(4,'big');initial.registers[15]=sp
     if initial.sr&0x2000:initial.ssp=sp
     else:initial.usp=sp
     memory[0xc0920:0xc0924]=task.to_bytes(4,'big')
     injection=0xe4c0 if direction=='input_calls_coordinate' else 0xe26c;target=0x11d1a if direction=='input_calls_coordinate' else 0x11b4c;memory[injection:injection+6]=b'\x4e\xb9'+target.to_bytes(4,'big')
     case={**input_case,**coord_case};ram=bytes(memory)
     expected,cpu,entries,_=run(ram,initial,case,direction,False);actual,got,observed,details=run(ram,initial,case,direction,True)
     if expected!=actual or inp.cpu_dict(cpu)!=inp.cpu_dict(got)or entries!=observed:
      save(out/'counterexample.json',dict(direction=direction,case=i,original_CPU=inp.cpu_dict(cpu),native_CPU=inp.cpu_dict(got),original_entries=entries,native_entries=observed,RAM_differences=[[hex(a),u,v]for a,(u,v)in enumerate(zip(expected,actual))if u!=v][:32]));raise AssertionError(out/'counterexample.json')
     rows.append(dict(direction=direction,case=i,task=hex(task),full_CPU_nonarena_RAM_helper_entries_and_suspended_frame_match=True,**details))
     if i%16==0:state.update(status='checking',completed=len(rows),total=2*args.limit);mark();print(direction,i+1,flush=True)
  finally:engine.native.close()
  paths=[Path(__file__),Path(inp.__file__),Path(inp.original.__file__),Path(coord.__file__),Path(inp.original.scene.__file__),ROOT/'render-assets/biwn-inventory-baseline.bin',ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'tools/libbiwn-movement-device.dylib']
  for source,stem in [(inp.SRC,'native-input'),(COORD_SRC,'native-deck')]:paths += [source/(stem+'.c'),source/(stem+'.S'),source/(stem+'.ld'),source/'Makefile']
  for _,(_,_,syms)in builds.items():assert syms
  save(out/'cases.json',rows);state.update(status='terminal_compiled_input_coordinate_declared_nested_helpers_match',completed=len(rows),source_sha256={str(p):sha(p.read_bytes())for p in paths},payloads={name:dict(address=a,bytes=len(payload),sha256=sha(payload),symbols=syms)for name,(a,payload,syms)in builds.items()},scope=__doc__,fixture='E4C0 JSRs coordinate or E26C JSRs input, then normal declared helper effects. Real CPU JSR/root/helper-return code; one nested level; no actual firmware-pad/GPU/IRQ timing claim.');mark();save(ROOT/'verification/native-deck-input-nesting-v1-current.json',state);print(state['status'],len(rows),flush=True)
 except BaseException as error:state.update(status='terminal_failed',error=repr(error));mark();raise

if __name__=='__main__':main()
