"""Real compiled M68000 Deck hybrid versus original CPU; GPU fixture explicit.

Only the declared private C arena is excluded from final RAM comparison.
At helper entry the compiler return word is normalized to its source return
PC; all other guest RAM, registers, SR and arguments must match.
"""
import argparse,ctypes as c,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_deck_coordinate_source_v1 as original
ROOT=original.ROOT;CPU=original.CPU;SP=original.SP;STOP=original.STOP
SRC=ROOT/'projects/black-ice-white-noise/restoration/native-m68k/deck-coordinate-v1'
CODE=0x180000;ARENA=0x160000;SLOTS=101;STRIDE=1024;POOL=0xc0928
RETURNS=[0x11d82,0x11df6,0x11e00,0x11e0a]
sha=original.sha;save=original.save;cpu_dict=original.cpu_dict
def symbols(path):return {line.split()[2]:int(line.split()[0],16)for line in path.read_text().splitlines()if len(line.split())==3}
class Engine(original.Engine):
 def native_candidate(self,ram,initial,case,syms,fallback=False):
  self.native.device.seed(ram,0);state=CPU.from_buffer_copy(bytes(initial));state.pc=syms['biwn_native_deck_coordinate'];self.set_cpu(state,True)
  entries=[];trace=[];low=ARENA+SLOTS*STRIDE;original_steps=0;ret_checks=[]
  for step in range(30000):
   state=self.cpu();pc=state.pc
   if pc==STOP:break
   if ARENA<=state.registers[15]<ARENA+SLOTS*STRIDE:low=min(low,state.registers[15]%STRIDE)
   if pc==syms['biwn_native_deck_helper_return']:
    expected_sp=initial.registers[15]-44-20-(8 if len(entries)>1 else 0)
    assert state.registers[15]==expected_sp,(len(entries),hex(state.registers[15]),hex(expected_sp))
    ret_checks.append(dict(helper=len(entries),returned_SP=state.registers[15]))
   if pc in [0xe26c,0xe540]:
    memory=bytearray(self.native.device.ram());normalized=bytearray(memory);normalized[ARENA:ARENA+SLOTS*STRIDE]=ram[ARENA:ARENA+SLOTS*STRIDE]
    guest_sp=state.registers[15];physical_ret=int.from_bytes(memory[guest_sp:guest_sp+4],'big')
    assert physical_ret==(RETURNS[len(entries)]if fallback else syms['biwn_native_deck_helper_return'])
    normalized[guest_sp:guest_sp+4]=RETURNS[len(entries)].to_bytes(4,'big');entries.append(self.entry(normalized,state))
    if pc==0xe26c:
     self.gpu_fixture(memory,state,case);self.native.device.seed(bytes(memory),0)
     state.pc=int.from_bytes(memory[guest_sp:guest_sp+4],'big');state.registers[15]+=4
     if state.sr&0x2000:state.ssp=state.registers[15]
     else:state.usp=state.registers[15]
     self.set_cpu(state);continue
   if 0x11d1a<=pc<0x11e64:
    assert fallback,hex(pc);original_steps+=1
   else:assert CODE<=pc<CODE+len(case['payload'])or 0xe540<=pc<0xe588,hex(pc)
   trace.append(pc);self.core.m68k_execute(1)
  else:raise AssertionError(('native instruction bound',hex(pc)))
  assert len(entries)==4 and(fallback or len(ret_checks)==4)
  memory=self.native.device.ram()
  for slot in range(SLOTS):
   base=ARENA+slot*STRIDE
   assert memory[base:base+16]==ram[base:base+16]and memory[base+1008:base+1024]==ram[base+1008:base+1024],('guard',slot)
  if not fallback:
   task=int.from_bytes(ram[0xc0920:0xc0924],'big');slot=(task-POOL)//STRIDE;base=ARENA+slot*STRIDE
   assert memory[ARENA:base]==ram[ARENA:base]and memory[base+STRIDE:ARENA+SLOTS*STRIDE]==ram[base+STRIDE:ARENA+SLOTS*STRIDE]
   assert memory[task:task+38]==ram[task:task+38]
  normalized=bytearray(memory);normalized[ARENA:ARENA+SLOTS*STRIDE]=ram[ARENA:ARENA+SLOTS*STRIDE]
  return bytes(normalized),self.cpu(),entries,dict(instructions=len(trace),private_C_low_offset=low,original_coordinate_instructions=original_steps,helper_return_checks=ret_checks)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);args=ap.parse_args();out=ROOT/'verification/native-deck-coordinate-v2'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 state=dict(status='building',pid=os.getpid(),directory=str(out),whole_game_complete=False,native_disc_changed=False,new_training=False)
 def mark():save(out/'protocol.json',state)
 mark();build=out/'build';command=['make','BUILD='+str(build),'ADDRESS='+hex(CODE),'ARENA_ADDRESS='+hex(ARENA)]
 try:
  p=subprocess.run(command,cwd=SRC,capture_output=True,text=True);(out/'compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
  payload=(build/'native-deck.bin').read_bytes();syms=symbols(build/'symbols.txt');cases=original.fixtures();cases=cases[:args.limit]if args.limit else cases;engine=Engine();rows=[]
  try:
   for i,(ram,initial,case)in enumerate(cases):
    memory=bytearray(ram);memory[CODE:CODE+len(payload)]=payload;memory[ARENA:ARENA+SLOTS*STRIDE]=bytes([0xa5])*(SLOTS*STRIDE)
    task=POOL+(i%SLOTS)*STRIDE;memory[0xc0920:0xc0924]=task.to_bytes(4,'big');case={**case,'payload':payload}
    guest_sp=task+[0x3c0,0x3be,0x200][i%3]
    memory[guest_sp-256:guest_sp+32]=memory[SP-256:SP+32]
    initial=CPU.from_buffer_copy(bytes(initial));initial.registers[15]=guest_sp
    if initial.sr&0x2000:initial.ssp=guest_sp
    else:initial.usp=guest_sp
    expected,cpu,entries,_,_=engine.original(bytes(memory),initial,case)
    actual,got,observed,details=engine.native_candidate(bytes(memory),initial,case,syms)
    if expected!=actual or cpu_dict(cpu)!=cpu_dict(got)or entries!=observed:
     save(out/'counterexample.json',dict(case=i,original_CPU=cpu_dict(cpu),native_CPU=cpu_dict(got),original_entries=entries,native_entries=observed,RAM_differences=[[hex(a),u,w]for a,(u,w)in enumerate(zip(expected,actual))if u!=w][:32],details=details));raise AssertionError(out/'counterexample.json')
    rows.append(dict(case=i,task=hex(task),full_CPU_and_nonarena_RAM_match=True,helper_entry_normalized_match=True,**details))
    if i%32==0:state.update(status='checking',completed=i+1,total=len(cases));mark();print('case',i+1,'/',len(cases),flush=True)
   fallback_rows=[]
   if not args.limit:
    ram,initial,case=original.fixtures()[0];memory=bytearray(ram);memory[CODE:CODE+len(payload)]=payload;memory[ARENA:ARENA+SLOTS*STRIDE]=bytes([0xa5])*(SLOTS*STRIDE)
    for task in [0,POOL+1,POOL+SLOTS*STRIDE]:
     memory[0xc0920:0xc0924]=task.to_bytes(4,'big');case={**case,'payload':payload}
     expected,cpu,entries,_,_=engine.original(bytes(memory),initial,case);actual,got,observed,details=engine.native_candidate(bytes(memory),initial,case,syms,True)
     assert expected==actual and cpu_dict(cpu)==cpu_dict(got)and entries==observed
     fallback_rows.append(dict(task=hex(task),original_fallback=True,**details))
  finally:engine.native.close()
  save(out/'cases.json',rows);save(out/'fallbacks.json',fallback_rows)
  paths=[SRC/'native-deck.c',SRC/'native-deck.S',SRC/'native-deck.ld',SRC/'Makefile',Path(__file__),Path(original.__file__),ROOT/'projects/black-ice-white-noise/restoration/experimental/deck-coordinate-local-v6-hybrid/deck-coordinate-hybrid.c']
  state.update(status='terminal_native_coordinate_preflight_pass'if args.limit else'terminal_native_coordinate_hybrid_original_CPU_match',completed=len(rows),fallback_cases=len(fallback_rows),code_bytes=len(payload),arena_bytes=SLOTS*STRIDE,task_slots_covered=len({r['task']for r in rows}),minimum_private_C_stack_offset=min(r['private_C_low_offset']for r in rows),source_sha256={str(p):sha(p.read_bytes())for p in paths},payload=str(build/'native-deck.bin'),payload_sha256=sha(payload),symbols=syms,scope='Realcompiled68000execution versusoriginal11D1A. FinalD/A/SR/PC/USP/SSP andall2MBRAMexceptdeclared103424byteCarenamatch. Fourhelper-entryCPU/fullRAMsnapshotsmatchafterreplacingonlycompilerreturnwordwithoriginalreturnPCandnormalizingarena. E540realCPU,GPUresultfixture. All101arena guards andall101taskslotswithactualtask-localstacksat3depthscheckedin576cases. Invalididentityfallbackusesoriginalcode,separate. NoIRQ/timing/physicalconsole/disc/liveGPUclaim.');mark()
  if not args.limit:save(ROOT/'verification/native-deck-coordinate-v2-current.json',state)
  print(state['status'],len(rows),flush=True)
 except BaseException as e:state.update(status='terminal_failed',error=repr(e));mark();raise
if __name__=='__main__':main()
