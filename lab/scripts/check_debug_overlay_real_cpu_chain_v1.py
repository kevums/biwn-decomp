"""Structured10734 plus existing fullCPU formatter/text C and actual blitter.

No supplied helper results or pixel effects; original lane executes all bodies.
This is a finite host-C chain comparison, not native integration or gameplay.
"""
import argparse,ctypes as c,json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
import check_deck_debug_overlay_cpu_v1 as caller
ROOT=caller.ROOT;CPU=caller.CPU;Bus=caller.Bus;SERVICE=caller.SERVICE;save=caller.save;sha=caller.sha;cpu_dict=caller.cpu_dict
REST=ROOT/'projects/black-ice-white-noise/restoration'
FMT={0x1b160,0x1b1a8,0x1b212,0x1b29c,0x1b45a,0xe61c,0xe67c}
TEXT={0x181f8,0x14776,0x147a6,0x149ae,0xe540}
RANGES=[(0x10734,0x10968),(0x1b160,0x1b478),(0xe61c,0xe68c),(0x14776,0x14caa),(0xe540,0xe588)]
class Engine(caller.Engine):
 def original(self,ram,initial):
  device=self.native.device;device.seed(ram,0);self.set_cpu(initial,True);entries=[];coverage=set();calls={}
  for steps in range(1000000):
   s=self.cpu();pc=s.pc
   if pc==caller.STOP:break
   if pc in FMT|TEXT:calls[hex(pc)]=calls.get(hex(pc),0)+1
   if pc in caller.WIDTHS:entries.append(self.entry(device.ram(),s))
   assert any(a<=pc<b for a,b in RANGES),hex(pc);coverage.add(pc);self.core.m68k_execute(1)
  else:raise AssertionError('Real original chain work bound')
  return device.ram(),self.cpu(),entries,device.registers(),calls,coverage,steps
 def translated(self,lib,ram,initial):
  device=self.native.device;device.seed(ram,0);entries=[];errors=[];calls={}
  def reader(width):
   def cb(_,a,value):
    try:value[0]=device.read(a,width);return 0
    except BaseException as error:errors.append(repr(error));return 1
   return cb
  def writer(width):
   def cb(_,a,value):
    try:
     if width==1:
      assert a<0x200000,hex(a);device.direct(a,1,value)
     elif width==2:device.write16(a,value)
     else:device.write(a,value)
     return 0
    except BaseException as error:errors.append(repr(error));return 1
   return cb
  def service(_,bus,pointer,target):
   try:
    state=pointer.contents;assert target in FMT|TEXT,hex(target);calls[hex(target)]=calls.get(hex(target),0)+1
    if target in caller.WIDTHS:entries.append(self.entry(device.ram(),state))
    fn=lib.biwn_formatter_cpu_body if target in FMT else lib.biwn_overlay_text_cpu_body
    return fn(bus,pointer,callbacks[5],callbacks[6],None,1000000,0)
   except BaseException as error:errors.append(repr(error));return 1
  w=caller.h.base.scheduler.cleanup.world
  callbacks=[w.R8(reader(1)),w.R16(reader(2)),w.R32(reader(4)),w.W16(writer(2)),w.W32(writer(4)),caller.h.W8(writer(1)),SERVICE(service)]
  bus=Bus(*callbacks[:5],w.CALL(),None,0);state=CPU.from_buffer_copy(bytes(initial));status=lib.biwn_debug_overlay_cpu_call(c.byref(bus),c.byref(state),callbacks[6],None,16)
  return status,device.ram(),state,entries,device.registers(),calls,errors
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,default=8);args=ap.parse_args();assert 1<=args.limit<=256
 out=ROOT/'verification/debug-overlay-real-cpu-chain-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 state=dict(status='compiling',directory=str(out),pid=os.getpid(),new_training=False,native_disc_changed=False,helper_fixtures=False)
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/debug-overlay-real-cpu-chain-v1-current.json',state)
 mark()
 try:
  sources=[caller.SRC/'coordinator-reference.c',caller.SRC/'debug-adapter.c',REST/'biwn_formatter_cpu.c',REST/'biwn_overlay_text_cpu.c'];library=out/'chain.dylib'
  command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',*[str(p)for p in sources],'-o',str(library)];p=subprocess.run(command,capture_output=True,text=True);(out/'compiler.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
  lib=c.CDLL(str(library));lib.biwn_debug_overlay_cpu_call.argtypes=[c.POINTER(Bus),c.POINTER(CPU),SERVICE,c.c_void_p,c.c_uint32];lib.biwn_debug_overlay_cpu_call.restype=c.c_int
  for fn in [lib.biwn_formatter_cpu_body,lib.biwn_overlay_text_cpu_body]:fn.argtypes=[c.POINTER(Bus),c.POINTER(CPU),caller.h.W8,SERVICE,c.c_void_p,c.c_uint32,c.c_int];fn.restype=c.c_int
  vectors=list(caller.fixtures());order=[0,1,64,65,128,129,192,193]+[i for i in range(256)if i not in [0,1,64,65,128,129,192,193]];rows=[];coverage=set();e=Engine()
  try:
   for index in order[:args.limit]:
    ram,initial,case=vectors[index];memory=bytearray(ram);memory[0x403ca:0x403cc]=[0,1,2,31][len(rows)%4].to_bytes(2,'big');ram=bytes(memory)
    expected,cpu,entries,hardware,calls,seen,steps=e.original(ram,initial)
    status,actual,got,observed,registers,computed,errors=e.translated(lib,ram,initial)
    if status or errors or actual!=expected or cpu_dict(cpu)!=cpu_dict(got)or entries!=observed or hardware!=registers or calls!=computed:
     save(out/'counterexample.json',dict(case=case,status=status,errors=errors,original_CPU=cpu_dict(cpu),C_CPU=cpu_dict(got),original_calls=calls,C_calls=computed,original_entries=entries,C_entries=observed,original_hardware=hardware,C_hardware=registers,RAM_differences=[[hex(a),x,y]for a,(x,y)in enumerate(zip(expected,actual))if x!=y][:40]));raise AssertionError(out/'counterexample.json')
    coverage|=seen;rows.append(dict(case=index,flag=case['flag'],source_string_index=[0,1,2,31][(len(rows))%4],full_CPU_RAM_hardware_top_entries_and_callee_counts_match=True,original_instructions=steps,actual_source_provider_calls=computed));state.update(status='checking',completed=len(rows));mark();print('completed',len(rows),flush=True)
  finally:e.native.close()
  save(out/'cases.json',rows);save(out/'original-addresses.json',sorted(coverage));paths=[Path(__file__),Path(caller.__file__),*sources,caller.SRC/'debug-contract.h',REST/'biwn_formatter_cpu.h',REST/'biwn_overlay_text_cpu.h',library,out/'cases.json',out/'original-addresses.json']
  state.update(status='terminal_debug_real_formatter_text_CPU_and_blitter_chain_match',completed=len(rows),original_instruction_locations=len(coverage),source_sha256={str(p):sha(p.read_bytes())for p in paths},scope=__doc__+' Source string indices0,1,2,31 and captured font only. FullCPU/banks,whole2MBRAM including all private frames/global scratch,blitter registers,top-level helper entries and all provider call counts match. Existing formatter/text ports are static source instruction blocks. No changing reads,async IRQ,timing,native target compilation or natural gameplay claim.');mark();print(state['status'],len(rows),flush=True)
 except BaseException as error:state.update(status='terminal_debug_real_chain_failed',error=repr(error));mark();raise
if __name__=='__main__':main()
