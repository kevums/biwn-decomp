"""Exact reset observer over64real original/native input lanes plus faults.
Host snapshots only; other input helpers are explicit fixtures. No game/IRQ claim.
"""
import ctypes as c,json,struct,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_native_deck_scene_reset_v1 as m
import shared_deck_record_loop_image_full_observer_v1 as monitor
ROOT=m.ROOT;V=ROOT/'verification';save=m.save
def read(p):return json.loads(Path(p).read_text())
def sha(p):return m.sha(Path(p).read_bytes())
def main():
 bp=V/'native-record-loop-image-disc-build-v1-current.json';b=read(bp);from record_loop_image_observer_build_v1 import with_aliases;b=with_aliases(b);gp=V/'native-deck-retained-record-loop-image-final-v1-current.json';g=read(gp);assert g['completed']==4992;payload=Path(g['payload']).read_bytes();assert m.sha(payload)==g['payload_sha256'];m.CODE=b['shared_Deck_code_address'];m.ARENA=b['deck_arena_address'];m.configure('input')
 out=V/'record-loop-image-reset-observer-qualified-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);source=out/'fixture.c'
 stub='''#include <stdint.h>\n#include <stdio.h>\n#include <string.h>\nstruct cpu{uint32_t r[16],pc,usp,ssp;uint16_t sr;};\nstatic struct cpu current;static uint8_t memory[0x200000],*ram=memory;\nstatic uint32_t rd32(uint32_t a){return ((uint32_t)ram[a]<<24)|((uint32_t)ram[a+1]<<16)|((uint32_t)ram[a+2]<<8)|ram[a+3];}\nstatic uint16_t rd16(uint32_t a){return ((uint16_t)ram[a]<<8)|ram[a+1];}\nstatic void read_cpu(struct cpu *o){*o=current;}\n'''
 extra='''\nvoid snapshot(const void *raw,const struct cpu *cpu){memcpy(memory,raw,sizeof(memory));current=*cpu;}\nvoid pc(uint32_t value){reset_watch(value);}\nvoid clear(void){memset(reset_slots,0,sizeof(reset_slots));reset_entries=reset_returns=reset_markers=reset_errors=reset_original_entries=reset_original_returns=0;}\nint wants(uint32_t pc){if(pc==0x1102au||pc==0x110d2u||pc=='''+str(b['shared_Deck_symbols']['dispatch'])+'u||pc=='+str(b['shared_Deck_symbols']['biwn_v18_scene_reset_marker'])+'''u)return 1;for(unsigned i=0;i<101;i++)if(reset_slots[i].active&&pc==reset_slots[i].ret)return 1;return 0;}\n'''
 source.write_text(stub+monitor.prior.prior.reset_monitor(b)+extra);lib=out/'fixture.dylib';a=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(lib)],capture_output=True,text=True);(out/'compiler.log').write_text(a.stdout+a.stderr);assert a.returncode==0,a.stderr
 bld_dispatch=b['shared_Deck_symbols']['dispatch'];f=c.CDLL(str(lib));f.snapshot.argtypes=[c.c_void_p,c.c_void_p];f.wants.argtypes=[c.c_uint32];f.wants.restype=c.c_int;f.pc.argtypes=[c.c_uint32];f.reset_dump.argtypes=[c.c_char_p];rows=[];checkpoints=[]
 def dump(name):
  path=out/name;assert f.reset_dump(str(path).encode())==0;return read(path)
 class Observed(m.Engine):
  observing=False;collect=False
  def cpu(self):
   state=super().cpu()
   if self.observing and f.wants(state.pc):
    raw=self.native.device.ram();f.snapshot(c.create_string_buffer(raw),c.byref(state));f.pc(state.pc)
    if self.collect and(state.pc!=bld_dispatch or int.from_bytes(raw[state.registers[15]+12:state.registers[15]+16],'big')==0x1102a):checkpoints.append((raw,m.CPU.from_buffer_copy(bytes(state))))
   return state
 e=Observed('input')
 try:
  for i,(ram,initial,case)in enumerate(m.inputs.fixtures()):
   if not 128<=i<192:continue
   memory=bytearray(ram);memory[m.CODE:m.CODE+len(payload)]=payload;memory[m.ARENA:m.ARENA+m.SLOTS*m.STRIDE]=bytes([0xa5])*(m.SLOTS*m.STRIDE)
   for slot in range(m.SLOTS):
    for _,offset,_,_ in m.LAYOUT.values():memory[m.ARENA+slot*m.STRIDE+offset+114:m.ARENA+slot*m.STRIDE+offset+118]=bytes(4)
   task=m.POOL+(i%m.SLOTS)*m.STRIDE;sp=task+[0x3c0,0x3be,0x200][i%3];memory[0xc0920:0xc0924]=task.to_bytes(4,'big');memory[sp-256:sp+32]=ram[m.SP-256:m.SP+32];initial=m.CPU.from_buffer_copy(bytes(initial));initial.registers[15]=sp
   if initial.sr&0x2000:initial.ssp=sp
   else:initial.usp=sp
   memory=bytes(memory);f.clear();e.observing=True
   try:expected,cpu,entries,*_=e.reference(memory,initial,case)
   finally:e.observing=False
   original=dump('original-'+str(i)+'.json');assert original['errors']==original['pending']==original['entries']==0 and original['original_global_entries']==original['original_global_returns']==1,original
   f.clear();e.observing=True;e.collect=i==144
   try:actual,got,observed,details=e.compiled(memory,initial,dict(case,payload=payload),g['symbols'],entries)
   finally:e.observing=e.collect=False
   native=dump('native-'+str(i)+'.json');assert native['errors']==native['pending']==0 and native['entries']==native['returns']==native['markers']==1,native
   assert expected==actual and m.cpu_dict(cpu)==m.cpu_dict(got)and entries==observed
   rows.append(dict(case=i,original=original,native=native,full_CPU_RAM_entries_match=True));
   if len(rows)%16==0:print('input lanes',len(rows),flush=True)
 finally:e.native.close()
 assert len(rows)==64;assert len(checkpoints)==3,[(hex(s.pc),hex(s.registers[15]))for _,s in checkpoints]
 raw0,s0=checkpoints[0];frame=int.from_bytes(raw0[s0.registers[15]+4:s0.registers[15]+8],'big');faults=[]
 def replay(name,mutate=None,skip=None):
  f.clear()
  for index,(raw,state)in enumerate(checkpoints):
   if index==skip:continue
   memory=bytearray(raw);cpu=m.CPU.from_buffer_copy(bytes(state))
   if mutate:mutate(index,memory,cpu)
   f.snapshot(c.create_string_buffer(bytes(memory)),c.byref(cpu));f.pc(cpu.pc)
  d=dump('fault-'+name+'.json');accepted=d['errors']==d['pending']==0 and d['entries']==d['returns']==1;return accepted,d
 assert replay('legal')[0]
 # Commit corruption cannot be accepted merely because control returned.
 for name,offset in [('D0',4),('A0',36),('SP',64),('PC',68),('USP',72),('SSP',76),('SR_X',81),('budget',93),('error',97),('active',117)]:
  def mutate(index,memory,cpu,offset=offset):
   if index==2:memory[frame+offset]^=16 if offset==81 else 1
  accepted,d=replay(name,mutate);assert not accepted,(name,d);faults.append(dict(name=name,rejected=True))
 for name,address in [('matrix',0x47b88),('copy_global',0x400ec),('clear_global',0x40402)]:
  def mutate(index,memory,cpu,address=address):
   if index==2:memory[address]^=1
  assert not replay(name,mutate)[0];faults.append(dict(name=name,rejected=True))
 for name,index in [('missing_marker',1),('missing_return',2)]:assert not replay(name,skip=index)[0];faults.append(dict(name=name,rejected=True))
 def badsp(index,memory,cpu):
  if index==2:cpu.registers[15]+=2
 assert not replay('physical_return_SP',badsp)[0];faults.append(dict(name='physical_return_SP',rejected=True))
 save(out/'cases.json',rows);save(out/'faults.json',faults);paths=[Path(__file__),Path(m.__file__),Path(monitor.__file__),Path(monitor.__file__).with_name('scene_reset_observer_v1.inc.c'),bp,gp,source,lib,out/'cases.json',out/'faults.json'];proof=dict(status='terminal_reset_observer_64_real_input_pairs_and_faults_pass',directory=str(out),actual_input_pairs=64,CPU_lanes=128,native_reset_entries=64,original_reset_entries=64,rejected_fault_controls=len(faults),host_guest_RAM_writes=0,new_predictions=0,new_training=False,source_sha256={str(x):sha(x)for x in paths},scope=__doc__+' AllCCR/bothbanks,actualfinalimagecode;observer checks logicalCPU,banks,PC/SR-X,originalreturnword,service/budget metadata,25publicwrites andCABIreturnSP. Otherinputhelpersarefixtures;checkpoints replayonlyinhostbuffers.');save(out/'review.json',proof);save(V/'record-loop-image-reset-observer-qualified-v1-current.json',proof);print(proof['status'])
if __name__=='__main__':main()
