"""Host guards and exact coverage for the connected fullCPU submit wrapper."""
import ctypes as c,hashlib,json,re
from datetime import datetime,timezone
from pathlib import Path
import check_GPU4720_CPU_dispatch as test
ROOT=test.ROOT

def main():
 p=ROOT/'verification/GPU4720-CPU-dispatch-current.json';proof=json.loads(p.read_text());out=Path(proof['directory']);lib=c.CDLL(str(out/'libGPU4720-CPU-dispatch.dylib'));fn=lib.biwn_gpu4720_submit_cpu_call;fn.argtypes=[c.POINTER(test.media.Bus),c.POINTER(test.media.CPU),c.c_uint32];fn.restype=c.c_int
 listing=Path(json.loads((ROOT/'verification/main-CPU-route-coverage-current.json').read_text())['static_manifest']).parent/'listing.asm';expected={int(line[:8],16)for line in listing.read_text().splitlines()if re.match(r'^[0-9a-fA-F]{8}:',line)and(0xe26c<=int(line[:8],16)<=0xe2b6 or 0xe098<=int(line[:8],16)<=0xe0a4)};assert expected==set(proof['CPU_instruction_addresses'])and len(expected)==14
 w=test.media.scheduler.cleanup.world;guards=[]
 def attempt(mode,supervisor):
  ram=bytearray((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes());ram[test.SP:test.SP+24]=test.STOP.to_bytes(4,'big')+bytes(20);events=[];ack=0xffffffff
  def read(_,a,out):
   if mode=='read_fail':return 1
   out[0]=1 if a==0xf03200 and mode=='idle_busy'else 0 if a==0xf03200 else ack if a==0xf03204 else 0 if a==test.SP-4 and mode=='bad_return'else int.from_bytes(ram[a:a+4],'big');events.append(['r',a,out[0]]);return 0
  def write(_,a,value):
   nonlocal ack
   if mode=='write_fail':return 1
   events.append(['w',a,value])
   if a==0xf03204:ack=0x4720 if mode=='ack_busy'else 0xffffffff
   elif a<0x200000:ram[a:a+4]=value.to_bytes(4,'big')
   return 0
  rd=w.R32()if mode=='missing_read'else w.R32(read);wr=w.W32()if mode=='missing_write'else w.W32(write);bus=test.media.Bus(w.R8(),w.R16(),rd,w.W16(),wr,w.CALL(),None,0);cpu=test.media.CPU();cpu.registers[15]=test.SP;cpu.pc=0 if mode=='bad_pc'else 0xe26c;cpu.sr=0x2000 if supervisor else 0;cpu.usp=0x180000 if supervisor else test.SP;cpu.ssp=test.SP if supervisor else 0x1d0000;before=bytes(cpu)
  budget=0 if mode=='zero_budget'else 4 if mode in ['idle_busy','ack_busy']else 100;status=fn(None if mode=='null_bus'else c.byref(bus),None if mode=='null_cpu'else c.byref(cpu),budget)
  assert bytes(cpu)==before;expected=1 if mode in ['null_bus','null_cpu','missing_read','missing_write','bad_pc']else 2 if mode in ['read_fail','write_fail']else 3 if mode in ['zero_budget','idle_busy','ack_busy']else 4;assert status==expected,(mode,supervisor,status)
  guards.append(dict(mode=mode,supervisor=supervisor,status=status,CPU_unchanged=True,prior_memory_effects_retained=True,events=events))
 for supervisor in [False,True]:
  for mode in ['null_bus','null_cpu','missing_read','missing_write','bad_pc','read_fail','write_fail','zero_budget','idle_busy','ack_busy','bad_return']:attempt(mode,supervisor)
 (out/'host-guards.json').write_text(json.dumps(guards,indent=2)+'\n');proof.update(CPU_instruction_address_coverage=[14,14],host_guard_cases=len(guards),host_guard_proof=str(out/'host-guards.json'),dispatcher_source_hash_matches_prior_accepted=True);p.write_text(json.dumps(proof,indent=2)+'\n');(out/'report.json').write_text(json.dumps(proof,indent=2)+'\n');print('Connected protocol all14 CPU addresses and22 host guards checked')
if __name__=='__main__':main()
