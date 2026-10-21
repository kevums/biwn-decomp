"""Existing full format gates with bounded fast native dispatch and diagnostics.
Host code only dispatches the retained CPU; no host game/ISA effects supplied.
"""
import ctypes as c,inspect,json,subprocess,sys
from pathlib import Path
import check_biwn_native_format_pad as gate
ROOT=gate.ROOT
DRIVER=r'''
#include <stdint.h>
#include <string.h>
typedef int(*exec_fn)(int);typedef unsigned(*get_fn)(void*,int);
struct stats {uint32_t status,pc;uint64_t steps,cycles;uint8_t coverage[64];};
int run(exec_fn execute,get_fn get,uint32_t stop,uint32_t sp,uint32_t base,
 uint32_t end,uint32_t entry,uint32_t original,uint64_t limit,struct stats*out){
 memset(out,0,sizeof(*out));
 while(out->steps<limit){
  uint32_t pc=get(0,16);out->pc=pc;
  if(pc==stop&&get(0,15)==sp+4)return 0;
  if(original?!(pc>=entry&&pc<entry+64):!(pc==entry||(pc>=base&&pc<end))){out->status=1;return 1;}
  if(original)out->coverage[pc-entry]=1;
  int cycles=execute(1);if(cycles<=0){out->status=3;return 3;}
  out->steps++;out->cycles+=(unsigned)cycles;
 }out->status=2;return 2;
}
'''
class Stats(c.Structure):
 _fields_=[('status',c.c_uint32),('pc',c.c_uint32),('steps',c.c_uint64),('cycles',c.c_uint64),('coverage',c.c_uint8*64)]
def main():
 source=Path(sys.argv[1]).resolve();receipts=Path(sys.argv[2]).resolve();receipts.mkdir(parents=True,exist_ok=True)
 (receipts/'driver.c').write_text(DRIVER);r=subprocess.run(['clang','-std=c99','-O2','-dynamiclib',str(receipts/'driver.c'),'-o',str(receipts/'driver.dylib')],capture_output=True,text=True);(receipts/'driver-build.log').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr
 lib=c.CDLL(str(receipts/'driver.dylib'));lib.run.argtypes=[c.c_void_p,c.c_void_p,*([c.c_uint32]*6),c.c_uint64,c.POINTER(Stats)];lib.run.restype=c.c_int
 native_rows=[];original_results={};original_save=gate.save
 def isolated_save(path,value):
  path=Path(path)
  if path.parent==ROOT/'verification':path=receipts/path.name
  original_save(path,value)
 gate.save=isolated_save
 def fast_native(n,image,case,length,original):
  n.device.seed(gate.seed(image,case),0);l=n.lib;l.m68k_pulse_reset();l.m68k_set_irq(0);supervisor=bool(case['sr']&0x2000)
  l.m68k_set_reg(17,0x2000);l.m68k_set_reg(15,gate.SP if supervisor else 0x1ff000);l.m68k_set_reg(17,0);l.m68k_set_reg(15,0x1fe000 if supervisor else gate.SP);l.m68k_set_reg(17,case['sr'])
  for i,v in enumerate(case['incoming']+[gate.SP]):l.m68k_set_reg(i,v)
  l.m68k_set_reg(16,gate.ENTRY);stats=Stats();positive=case['left']if case['left']<32768 else 0;budget=min(50000000,50000+positive*1024)
  status=lib.run(c.cast(l.m68k_execute,c.c_void_p),c.cast(l.m68k_get_reg,c.c_void_p),gate.STOP,gate.SP,gate.BASE,gate.BASE+length,gate.ENTRY,int(original),budget,c.byref(stats))
  cpu=[l.m68k_get_reg(None,i)for i in range(18)];cpu.extend([n.prefix[16]if supervisor else cpu[15],cpu[15]if supervisor else n.prefix[17]]);ram=n.device.ram()
  key=json.dumps(case,sort_keys=True)
  native_rows.append(dict(original=original,steps=stats.steps,cycles=stats.cycles,budget=budget,status=status))
  if original:original_results[key]=cpu
  if status:
   frame=[int.from_bytes(ram[gate.SP-72+i*4:gate.SP-68+i*4],'big')for i in range(17)]
   original_save(receipts/'execution-diagnostic.json',dict(status=status,case=case,PC=hex(stats.pc),steps=stats.steps,budget=budget,current_internal_CPU=cpu,current_semantic_frame=frame,expected_return_CPU=original_results.get(key),scope='Observed state at stop/budget,not a returned CPU state. Expected values come from actual originalCPU,not C target.'))
   raise AssertionError('instruction_budget_exhausted'if status==2 else'native_code_boundary_or_execution_error')
  if not original:assert ram[gate.BASE:gate.BASE+length]==image[gate.BASE:gate.BASE+length]
  return ram,cpu,{gate.ENTRY+i for i,x in enumerate(stats.coverage)if x}
 gate.native=fast_native
 # Same ordered-access implementation; only explicit count/time budgets change.
 trace_source=inspect.getsource(gate.trace);assert trace_source.count('count=1000000')==1 and trace_source.count('timeout=10000000')==1
 trace_source=trace_source.replace('count=1000000','count=50000000').replace('timeout=10000000','timeout=30000000');(receipts/'ordered-trace-as-run.py').write_text(trace_source);namespace=dict(vars(gate));exec(compile(trace_source,'ordered-trace-as-run.py','exec'),namespace);gate.trace=namespace['trace']
 sys.argv=[gate.__file__,'--source',str(source)]
 try:gate.main()
 finally:
  original_save(receipts/'native-dispatch-results.json',native_rows);original_save(receipts/'backend.json',dict(host_game_effects=False,original_checker=str(Path(gate.__file__)),original_checker_sha256=gate.sha(Path(gate.__file__)),wrapper_sha256=gate.sha(Path(__file__)),native_budget='min(50000000,50000+1024*positive_signed16_remaining)',ordered_count_budget=50000000,ordered_timeout_microseconds=30000000))
if __name__=='__main__':main()
