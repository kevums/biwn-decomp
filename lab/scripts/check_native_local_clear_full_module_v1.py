"""Exact shared-module local body across the full original helper matrix.
Execute unmodified linked bytes under the pinned68000and independentUnicorn;
compare raw-body CPU,publicRAM and ordered bus accesses with the raw local C.
Native directbus cannot report host callback failures. No disc/IRQ/fidelity claim.
"""
import ctypes as c,json,os,struct,subprocess
from pathlib import Path
from datetime import datetime,timezone
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_deck_geometry_helpers_v1 as h
ROOT=h.ROOT;V=ROOT/'verification';REGS=[UC_M68K_REG_D0,UC_M68K_REG_D1,UC_M68K_REG_D2,UC_M68K_REG_D3,UC_M68K_REG_D4,UC_M68K_REG_D5,UC_M68K_REG_D6,UC_M68K_REG_D7,UC_M68K_REG_A0,UC_M68K_REG_A1,UC_M68K_REG_A2,UC_M68K_REG_A3,UC_M68K_REG_A4,UC_M68K_REG_A5,UC_M68K_REG_A6,UC_M68K_REG_A7]
CODE=0x180000;ARENA=0x160000;SLOTS=101;STRIDE=1024
save=h.save
def read(p):return json.loads(Path(p).read_text())
def sha(p):return h.sha(Path(p).read_bytes())
def pack(s):return struct.pack('>19IH',*s.registers,s.pc,s.usp,s.ssp,s.sr)
def unpack(raw):
 v=struct.unpack('>19IH',raw);s=h.CPU();s.registers[:]=v[:16];s.pc,s.usp,s.ssp,s.sr=v[16:];return s

def main():
 gp=V/'native-Deck-local-clear-real-v1-current.json';gate=read(gp);assert gate['completed']==256
 for p,digest in gate['source_sha256'].items():assert sha(p)==digest,p
 out=V/'native-local-clear-full-module-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);state=dict(status='building_reference',pid=os.getpid(),directory=str(out),completed=0,new_predictions=0,new_training=False,native_disc_changed=False)
 def mark():save(out/'protocol.json',state);save(V/'native-local-clear-full-module-v1-current.json',state)
 mark();raw=ROOT/'projects/black-ice-white-noise/restoration/experimental/deck-clear-local-typed-v3/clear-records.c';typed=raw.parent.parent/'typed-deck-primitives-v1/typed-registers.h'
 source=out/'raw-body-reference.c';source.write_text('#include "'+str(typed)+'"\n#include "'+str(raw)+'"\n'+r'''
int apply(struct biwn_world_bus *bus,biwn_deck_write8 w8,struct biwn_task_cpu *cpu,
biwn_world_cpu_service service,void *opaque,uint32_t helper_budget,uint32_t byte_budget){
 struct biwn_deck_context s={bus,*cpu,service,opaque,helper_budget,0};
 clear_records(&s,w8,byte_budget);*cpu=s.cpu;return s.error;
}
''');lib=out/'reference.dylib';result=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(lib)],capture_output=True,text=True);(out/'compiler.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
 fn=c.CDLL(str(lib)).apply;fn.argtypes=[c.POINTER(h.Bus),h.W8,c.POINTER(h.CPU),h.SERVICE,c.c_void_p,c.c_uint32,c.c_uint32];fn.restype=c.c_int
 payload=Path(gate['payload']).read_bytes();entry=gate['symbols']['local_typed_clear_records'];engine=h.Engine();rows=[];budgets=[]
 def prepare(ram,initial,i,budget):
  memory=bytearray(ram);memory[CODE:CODE+len(payload)]=payload;memory[ARENA:ARENA+SLOTS*STRIDE]=bytes([0xa5])*(SLOTS*STRIDE);memory[h.STOP:h.STOP+2]=bytes.fromhex('60fe');base=ARENA+(i%SLOTS)*STRIDE;frame=base+16;csp=base+992
  memory[frame:frame+98]=struct.pack('>I',0)+pack(initial)+struct.pack('>4I',0x12345678,frame,7,0);memory[csp:csp+16]=struct.pack('>4I',h.STOP,frame,0,budget)
  physical=h.CPU();physical.registers[:]=[(0x1234567*(n+1))&0xffffffff for n in range(15)]+[csp];physical.pc=entry;physical.sr=initial.sr&0x2000;physical.usp=0x1d8000 if physical.sr else csp;physical.ssp=csp if physical.sr else 0x1ff000
  return bytes(memory),physical,base,frame,csp
 def normalize(raw,before):
  memory=bytearray(raw);memory[ARENA:ARENA+SLOTS*STRIDE]=before[ARENA:ARENA+SLOTS*STRIDE];return bytes(memory)
 def native(memory,physical,base,frame,csp):
  engine.native.device.seed(memory,0);engine.set_cpu(physical,True)
  for chunk in range(5000):
   engine.core.m68k_execute(10000)
   if engine.cpu().pc==h.STOP:break
  else:raise AssertionError('Native shared-body work limit')
  actual=engine.native.device.ram();done=engine.cpu();assert done.registers[15]==csp+4
  for index in [*range(2,8),*range(10,15)]:assert done.registers[index]==physical.registers[index],('C ABI preserved register',index)
  assert actual[CODE:CODE+len(payload)]==payload and actual[frame+82:frame+94]==memory[frame+82:frame+94]
  assert actual[ARENA:base]==memory[ARENA:base]and actual[base+STRIDE:ARENA+SLOTS*STRIDE]==memory[base+STRIDE:ARENA+SLOTS*STRIDE]
  assert actual[base:base+16]==memory[base:base+16]and actual[base+134:base+832]==memory[base+134:base+832]and actual[base+1008:base+1024]==memory[base+1008:base+1024]
  return int.from_bytes(actual[frame+94:frame+98],'big'),actual,unpack(actual[frame+4:frame+82]),chunk+1
 def ordered(memory,physical):
  u=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);u.ctl_set_cpu_model(UC_CPU_M68K_M68000);u.mem_map(0,0x200000);u.mem_write(0,memory);u.reg_write(UC_M68K_REG_SR,physical.sr)
  for reg,value in zip(REGS,physical.registers):u.reg_write(reg,value)
  events=[]
  def private(a,w):return ARENA<=a and a+w<=ARENA+SLOTS*STRIDE
  def rd(uc,access,a,w,value,data):
   if not private(a,w):events.append(['r',a,w,int.from_bytes(u.mem_read(a,w),'big')])
  def wr(uc,access,a,w,value,data):
   if not private(a,w):events.append(['w',a,w,value&((1<<(8*w))-1)])
  u.hook_add(UC_HOOK_MEM_READ,rd);u.hook_add(UC_HOOK_MEM_WRITE,wr);u.emu_start(entry,h.STOP,count=4000000,timeout=10000000);assert u.reg_read(UC_M68K_REG_PC)==h.STOP;return events
 try:
  for ram,initial,case in h.fixtures():
   if case['root']!=0x10968:continue
   i=case['variant']
   for budget in [65536]+([0,1,63,64,65,127]if i in [1,2,3,256,257,258,259]else[]):
    memory,physical,base,frame,csp=prepare(ram,initial,i,budget);reference=engine.translated(fn,memory,initial,case,byte_budget=budget);status,actual,got,chunks=native(memory,physical,base,frame,csp)
    assert not reference[-1]and status==reference[0]and normalize(actual,memory)==normalize(reference[1],memory)and h.cpu_dict(got)==h.cpu_dict(reference[2]),(i,budget,status,reference[0])
    events=ordered(memory,physical);assert events==reference[4],('ordered accesses',i,budget)
    if budget==65536:
     original,cpu,_,_,_=engine.original(memory,initial,case);assert normalize(original,memory)==normalize(actual,memory)
     expected=h.CPU.from_buffer_copy(bytes(cpu));expected.pc=0x1098e;expected.registers[15]=initial.registers[15]
     if expected.sr&0x2000:expected.ssp=initial.registers[15]
     else:expected.usp=initial.registers[15]
     assert h.cpu_dict(got)==h.cpu_dict(expected),('original fullCPU',i);rows.append(dict(case=i,public_events=len(events),full_CPU_public_RAM_order_C_ABI_and_fences_match=True,native_chunks=chunks))
    else:budgets.append(dict(case=i,budget=budget,status=status,public_events=len(events),partial_CPU_RAM_order_match=True))
   if len(rows)%16==0:state.update(status='checking',completed=len(rows));mark();print('completed',len(rows),flush=True)
 finally:engine.native.close()
 assert len(rows)==260 and len(budgets)==42;save(out/'cases.json',rows);save(out/'budgets.json',budgets);paths=[Path(__file__),gp,raw,typed,source,lib,Path(gate['payload']),out/'cases.json',out/'budgets.json'];state.update(status='terminal_exact_shared_local_body_260_original_and_42_budget_contracts_match',completed=len(rows),budget_cases=len(budgets),payload_sha256=gate['payload_sha256'],module_bytes=gate['code_bytes'],actual_instruction_work_bound=50000000,source_sha256={str(p):sha(p)for p in paths},scope=__doc__+' Contextservice/opaque/budget bytes andcallee-savedphysicalCregisters remainintact. Task-privatecontext/Cstack alone normalized. ActualmoduleCPUlogicalRTSstate comparesoriginalafter reversingonlyitsouterRTSpop. All32CCR/bothbanks andlarge/signedcountboundaries retained.42budgetcasescomparepartialprivateCPU/RAM/order withrawfunctionbody,includingzerobudget. Hostcallbackfailurebehavior remains theseparatelyqualifiedportablecontract.');mark();print(state['status'],flush=True)
if __name__=='__main__':main()
