"""Qualify the exact rendered read-only direction monitor on original/native CPU.
Only decoded observations are altered for controls; the guest CPU/RAM stay intact.
"""
import argparse,ctypes as c,json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
import native_actor_direction_engine_v1 as e
from actor_direction_observer_source import render,model_source
ROOT=e.ROOT;V=ROOT/'verification'
class CPU(c.Structure):_fields_=[('r',c.c_uint32*16),('pc',c.c_uint32),('usp',c.c_uint32),('ssp',c.c_uint32),('sr',c.c_uint16)]
def read(p):return json.loads(Path(p).read_text())
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);args=ap.parse_args();build=read(V/'native-actor-direction-disc-build-current.json');gate=read(V/'native-actor-direction-final-current.json');e.BASE=gate['code_address'];payload=Path(gate['binary']).read_bytes();symbols=gate['symbols'];snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();out=V/'actor-direction-live-observer'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source,include=render(build)
 header='''#include <stdint.h>
#include <string.h>
struct cpu{uint32_t r[16],pc,usp,ssp;uint16_t sr;};
static const unsigned char*ram;static unsigned errors;static void(*read_cpu)(struct cpu*);
#define BIWN_DIRECTION_TASK() (0x1ff000u-0x404u)
static uint32_t rd32(uint32_t a){if(a>0x1ffffcu){errors++;return 0;}return((uint32_t)ram[a]<<24)|((uint32_t)ram[a+1]<<16)|((uint32_t)ram[a+2]<<8)|ram[a+3];}
'''
 footer='''
void begin(const void*m,void*reader){ram=m;read_cpu=(void(*)(struct cpu*))reader;errors=0;memset(dir_calls,0,sizeof(dir_calls));dir_slots=dir_pending=0;dir_entries=dir_native=dir_returns=dir_old_steps=dir_source_steps=dir_errors=dir_context_errors=dir_stack_outside=dir_stack_observations=dir_context_entries=dir_context_returns=dir_max_depth=0;dir_min_headroom=0xffffffffu;}
void step(uint32_t pc){watch_direction(pc);}
void counts(uint64_t*out){uint64_t v[]={dir_entries,dir_native,dir_returns,dir_pending,dir_errors,dir_context_errors,dir_stack_outside,dir_context_entries,dir_context_returns,dir_old_steps,dir_source_steps,dir_max_depth,dir_min_headroom,errors};memcpy(out,v,sizeof(v));}
'''
 cpp=out/'monitor.c';cpp.write_text(header+source+footer);model=out/'direction-shadow-model.c';model.write_text(model_source());library=out/'monitor.dylib';run=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(cpp),str(model),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'build.log').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
 lib=c.CDLL(str(library));lib.begin.argtypes=[c.c_void_p,c.c_void_p];lib.step.argtypes=[c.c_uint32];lib.counts.argtypes=[c.POINTER(c.c_uint64)];native=e.Native();mirror=c.create_string_buffer(0x200000);negative=None;override=None;injected=False
 def reader(target):
  cpu=CPU();cpu.r[:]=[native.lib.m68k_get_reg(None,i)for i in range(16)];cpu.pc=native.lib.m68k_get_reg(None,16);cpu.sr=native.lib.m68k_get_reg(None,17);cpu.usp=native.prefix[16]if cpu.sr&0x2000 else cpu.r[15];cpu.ssp=cpu.r[15]if cpu.sr&0x2000 else native.prefix[17]
  if override=='task_SP':cpu.r[15]=e.SP-1000
  if override=='return_D0':cpu.r[0]^=1
  if override=='return_X':cpu.sr^=16
  c.memmove(target,c.byref(cpu),c.sizeof(cpu))
 callback=c.CFUNCTYPE(None,c.POINTER(CPU))(reader);real_execute=native.lib.m68k_execute;watched={0x13440,0x134da,symbols['biwn_native_actor_direction'],symbols['biwn_native_actor_direction_body'],symbols['biwn_native_actor_direction_return']}
 def execute(cycles):
  nonlocal override,injected
  pc=native.lib.m68k_get_reg(None,16)
  if pc in watched:c.memmove(mirror,native.device.pointer,0x200000)
  if negative and not injected:
   if negative=='task_SP'and pc==symbols['biwn_native_actor_direction']:override=negative;injected=True
   if negative in ['return_D0','return_X']and pc==symbols['biwn_native_actor_direction_return']:override=negative;injected=True
   if negative=='context_SR'and pc==symbols['biwn_native_actor_direction_body']:
    at=e.SP-124+66;c.memmove(c.addressof(mirror)+at,bytes([mirror.raw[at]^1]),1);injected=True
  before=mirror.raw if pc in watched else None;guest=native.device.ram()if pc in watched else None;lib.step(pc);override=None
  if pc in watched:assert mirror.raw==before and native.device.ram()==guest,'Observer changed RAM'
  return real_execute(cycles)
 native.lib.m68k_execute=execute
 def replay(case,compiled):
  expected=e.execute(snapshot,case,payload,symbols,compiled);c.memmove(mirror,snapshot,0x200000);lib.begin(mirror,c.cast(callback,c.c_void_p));actual=e.replay(native,snapshot,case,payload,symbols,compiled,expected);values=(c.c_uint64*14)();lib.counts(values);return list(values),actual
 allcases=e.vectors();indexes=sorted(set(list(range(64))+list(range(0,2048,79))+list(range(2048,2560,8))));groups=[allcases[i]for i in indexes];groups=groups[:args.limit]if args.limit else groups;rows=[];state=dict(status='qualifying_native_direction_observer',pid=os.getpid(),directory=str(out),planned=len(groups)*2,completed=0)
 def mark():e.g.save(out/'protocol.json',state);e.g.save(V/'actor-direction-live-observer-active.json',state)
 mark()
 try:
  for index,case in enumerate(groups):
   for compiled in [False,True]:
    values,_=replay(case,compiled);assert all(values[k]==0 for k in [3,4,5,6,13]),(index,compiled,values);assert values[0]==values[2]==1 and values[1]==int(compiled)and values[7]==values[8]==int(compiled)
    rows.append(dict(index=index,compiled=compiled,counts=values));state['completed']=len(rows)
   if index%32==0:mark();print('Direction observer',len(rows),'/',state['planned'],flush=True)
  controls=[];positive,baseline=replay(allcases[6],True)
  for defect in ['task_SP','return_D0','return_X','context_SR']:
   negative=defect;injected=False;values,actual=replay(allcases[6],True);assert injected and actual==baseline and any(values[k]for k in [4,5,6]),(defect,values);controls.append(dict(defect=defect,rejected=True,native_CPU_or_RAM_changed=False,counts=values))
  negative=None;e.g.save(out/'cases.json',rows);e.g.save(out/'controls.json',controls);inputs=[Path(__file__),Path(e.__file__),Path(e.g.__file__),ROOT/'scripts/actor_direction_observer_source.py',include,cpp,model,library,Path(gate['binary']),Path(gate['ELF']),ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib'];state.update(status='terminal_direction_observer_preflight_pass'if args.limit else'terminal_native_direction_live_observer_qualified',cases=len(groups),completed=len(rows),negative_controls=controls,source_sha256={str(p):e.g.sha(p)for p in inputs},scope=__doc__);mark()
  if not args.limit:e.g.save(V/'actor-direction-live-observer-current.json',state)
  print(json.dumps({k:state[k]for k in ['status','cases','completed']}))
 except BaseException as error:state.update(status='terminal_direction_observer_failed',error=repr(error));mark();raise
 finally:native.close()
if __name__=='__main__':main()
