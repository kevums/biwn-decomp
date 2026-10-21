"""Qualify the exact read-only mailbox observer on real original/native CPU.
Scripted mailbox schedules, no GPU/frame execution. Four decoded-observation
defects affect only the observer's mirror/callback, never the guest CPU/RAM.
"""
import ctypes as c,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
import native_gpu_mailbox_engine_v2 as e
from gpu_mailbox_observer_source import render
V=e.ROOT/'verification'
class CPU(c.Structure):_fields_=[('r',c.c_uint32*16),('pc',c.c_uint32),('usp',c.c_uint32),('ssp',c.c_uint32),('sr',c.c_uint16)]
def main():
 build=e.read(V/'native-gpu-mailbox-disc-build-current.json');gate=e.read(V/'native-gpu-mailbox-final-current.json');e.BASE=gate['code_address'];e.PARENT_OVERRIDE=build;payload=Path(gate['binary']).read_bytes();symbols=gate['symbols'];snapshot=(e.ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();out=V/'gpu-mailbox-live-observer-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);source,include=render(build)
 header='''#include <stdint.h>
#include <string.h>
struct cpu{uint32_t r[16],pc,usp,ssp;uint16_t sr;};
static const unsigned char*ram;static unsigned errors;static void(*read_cpu)(struct cpu*);
#define BIWN_MAILBOX_TASK() (0x1ff000u-0x404u)
static uint32_t rd32(uint32_t a){if(a>0x1ffffcu){errors++;return 0;}return((uint32_t)ram[a]<<24)|((uint32_t)ram[a+1]<<16)|((uint32_t)ram[a+2]<<8)|ram[a+3];}
'''
 footer='''
void begin(const void*m,void*reader){ram=m;read_cpu=(void(*)(struct cpu*))reader;errors=0;memset(mb_calls,0,sizeof(mb_calls));memset(mb_entries,0,sizeof(mb_entries));memset(mb_native,0,sizeof(mb_native));memset(mb_returns,0,sizeof(mb_returns));mb_slots=mb_pending=0;mb_old_steps=mb_source_steps=mb_errors=mb_context_errors=mb_helpers=mb_context_entries=mb_context_returns=mb_stack_outside=mb_stack_observations=mb_max_depth=0;mb_min_headroom=0xffffffffu;}
void step(uint32_t pc){watch_mailbox(pc);}
void counts(uint64_t*out){uint64_t v[]={mb_entries[0],mb_entries[1],mb_native[0],mb_native[1],mb_returns[0],mb_returns[1],mb_pending,mb_errors,mb_context_errors,mb_helpers,mb_context_entries,mb_context_returns,mb_stack_outside,mb_stack_observations,mb_max_depth,mb_min_headroom,errors};memcpy(out,v,sizeof(v));}
'''
 cpp=out/'monitor.c';cpp.write_text(header+source+footer);library=out/'monitor.dylib';run=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(cpp),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'build.log').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
 lib=c.CDLL(str(library));lib.begin.argtypes=[c.c_void_p,c.c_void_p];lib.step.argtypes=[c.c_uint32];lib.counts.argtypes=[c.POINTER(c.c_uint64)];native=e.Native();mirror=c.create_string_buffer(0x200000);negative=None;override=None;injected=False
 def reader(target):
  cpu=CPU();cpu.r[:]=[native.lib.m68k_get_reg(None,i)for i in range(16)];cpu.pc=native.lib.m68k_get_reg(None,16);cpu.sr=native.lib.m68k_get_reg(None,17);cpu.usp=native.prefix[16]if cpu.sr&0x2000 else cpu.r[15];cpu.ssp=cpu.r[15]if cpu.sr&0x2000 else native.prefix[17]
  if override=='return_D0':cpu.r[0]^=1
  if override in ['return_X','helper_X']:cpu.sr^=16
  c.memmove(target,c.byref(cpu),c.sizeof(cpu))
 callback=c.CFUNCTYPE(None,c.POINTER(CPU))(reader);real_execute=native.lib.m68k_execute;watched={0xe220,0xe2b8,0xe26a,0xe2f2,0xe098,symbols['biwn_native_gpu_submit_4320'],symbols['biwn_native_gpu_submit_4b00'],symbols['biwn_native_gpu_mailbox_body'],symbols['biwn_native_gpu_submit_4320_return'],symbols['biwn_native_gpu_submit_4b00_return']};returns={symbols['biwn_native_gpu_submit_4320_return'],symbols['biwn_native_gpu_submit_4b00_return']}
 def execute(cycles):
  nonlocal override,injected
  pc=native.lib.m68k_get_reg(None,16)
  if pc in watched:c.memmove(mirror,native.device.pointer,0x200000)
  if negative and not injected:
   if negative in ['return_D0','return_X']and pc in returns:override=negative;injected=True
   if negative=='helper_X'and pc==0xe098:override=negative;injected=True
   if negative=='context_SR'and pc==symbols['biwn_native_gpu_mailbox_body']:
    at=e.SP-96+66;c.memmove(c.addressof(mirror)+at,bytes([mirror.raw[at]^1]),1);injected=True
  before=mirror.raw if pc in watched else None;guest=native.device.ram()if pc in watched else None;lib.step(pc);override=None
  if pc in watched:assert mirror.raw==before and native.device.ram()==guest,'Observer changed RAM'
  return real_execute(cycles)
 native.lib.m68k_execute=execute
 def replay(case,compiled):
  expected=e.execute(snapshot,case,payload,symbols,compiled);c.memmove(mirror,snapshot,0x200000);lib.begin(mirror,c.cast(callback,c.c_void_p));actual=e.replay(native,snapshot,case,payload,symbols,compiled,expected);values=(c.c_uint64*17)();lib.counts(values);return list(values),actual
 allcases=e.cases();indexes={g*623+i for g in range(4)for i in [0,1,2,3,4,5,26,53,80,107,108,109,110]};indexes|={(f%4)*623+111+8*f for f in range(64)};rows=[];state=dict(status='qualifying_gpu_mailbox_observer',pid=os.getpid(),directory=str(out),planned=2*len(indexes),completed=0)
 def mark():e.save(out/'protocol.json',state);e.save(V/'gpu-mailbox-live-observer-active.json',state)
 mark()
 try:
  for index,case_index in enumerate(sorted(indexes)):
   case=allcases[case_index];kind=int(case['entry']==0xe2b8)
   for compiled in [False,True]:
    values,_=replay(case,compiled);assert all(values[k]==0 for k in [6,7,8,12,16]),(case_index,compiled,values);assert values[kind]==values[4+kind]==1 and values[2+kind]==int(compiled)and values[9]==2 and values[10]==values[11]==int(compiled)
    rows.append(dict(case_index=case_index,compiled=compiled,counts=values));state['completed']=len(rows)
   if index%32==0:mark();print('Mailbox observer',len(rows),'/',state['planned'],flush=True)
  controls=[];positive,baseline=replay(allcases[0],True)
  for defect in ['return_D0','return_X','helper_X','context_SR']:
   negative=defect;injected=False;values,actual=replay(allcases[0],True);assert injected and actual==baseline and any(values[k]for k in [7,8]),(defect,values);controls.append(dict(defect=defect,rejected=True,native_CPU_or_RAM_changed=False,counts=values))
  negative=None;e.save(out/'cases.json',rows);e.save(out/'controls.json',controls);inputs=[Path(__file__),Path(e.__file__),e.ROOT/'scripts/gpu_mailbox_observer_source.py',include,cpp,library,Path(gate['binary']),Path(gate['ELF']),e.ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib'];state.update(status='terminal_native_gpu_mailbox_live_observer_qualified',cases=len(indexes),completed=len(rows),negative_controls=controls,source_sha256={str(p):e.sha(p)for p in inputs},scope=__doc__);mark();e.save(V/'gpu-mailbox-live-observer-current.json',state);print({k:state[k]for k in ['status','cases','completed']})
 except BaseException as error:state.update(status='terminal_gpu_mailbox_observer_failed',error=repr(error));mark();raise
 finally:native.close()
if __name__=='__main__':main()
