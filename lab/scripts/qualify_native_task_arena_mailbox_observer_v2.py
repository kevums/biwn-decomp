"""Qualify the exact read-only mailbox observer on real original/native CPU.
Scripted mailbox schedules, no GPU/frame execution. Four decoded-observation
defects affect only the observer's mirror/callback, never the guest CPU/RAM.
"""
import ctypes as c,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
import native_gpu_mailbox_arena_engine_v3 as e
from task_arena_observer_source_v1 import render_mailbox as render,render as render_arena
V=e.ROOT/'verification'
class CPU(c.Structure):_fields_=[('r',c.c_uint32*16),('pc',c.c_uint32),('usp',c.c_uint32),('ssp',c.c_uint32),('sr',c.c_uint16)]
def main():
 build=e.read(V/'native-task-pool-arena-disc-build-current.json');gate=e.read(V/'task-pool-arena-final-current.json');e.BASE=gate['GPU_address'];e.PARENT_OVERRIDE=build;payload=Path(gate['GPU_binary']).read_bytes();symbols=gate['GPU_symbols'];e.ARENA=build['arena_address'];snapshot=bytearray((e.ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes());resident=Path(build['component']).read_bytes();snapshot[build['resident_address']:build['resident_address']+len(resident)]=resident;snapshot=bytes(snapshot);
 original_seed=e.seed
 def seeded(*args):
  script=original_seed(*args);script.memory[e.ARENA:e.ARENA+102*256]=resident[e.ARENA-build['resident_address']:e.ARENA-build['resident_address']+102*256];return script
 e.seed=seeded;
 out=V/'task-arena-mailbox-live-observer-v2'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);source,include=render(build);arena_source,arena_include=render_arena(build)
 header='''#include <stdint.h>
#include <string.h>
#include <stdio.h>
struct cpu{uint32_t r[16],pc,usp,ssp;uint16_t sr;};
static const unsigned char*ram,*payload;static unsigned errors;static void(*read_cpu)(struct cpu*);

static uint32_t rd32(uint32_t a){if(a>0x1ffffcu){errors++;return 0;}return((uint32_t)ram[a]<<24)|((uint32_t)ram[a+1]<<16)|((uint32_t)ram[a+2]<<8)|ram[a+3];}
'''
 footer='''
void begin(const void*m,void*reader,const void*code){ram=m;payload=code;memset(arena_active,0,sizeof(arena_active));memset(arena_used,0,sizeof(arena_used));arena_errors=arena_guard_checks=arena_stack_observations=arena_unused_checks=arena_code_checks=arena_max_depth=0;arena_ready=1;read_cpu=(void(*)(struct cpu*))reader;errors=0;memset(mb_calls,0,sizeof(mb_calls));memset(mb_entries,0,sizeof(mb_entries));memset(mb_native,0,sizeof(mb_native));memset(mb_returns,0,sizeof(mb_returns));mb_slots=mb_pending=0;mb_old_steps=mb_source_steps=mb_errors=mb_context_errors=mb_helpers=mb_context_entries=mb_context_returns=mb_stack_outside=mb_stack_observations=mb_max_depth=0;mb_min_headroom=0xffffffffu;}
void step(uint32_t pc){watch_pool_arena(pc);watch_mailbox(pc);}
void counts(uint64_t*out){FILE*f=tmpfile();arena_dump(f);fclose(f);uint64_t v[]={mb_entries[0],mb_entries[1],mb_native[0],mb_native[1],mb_returns[0],mb_returns[1],mb_pending,mb_errors,mb_context_errors,mb_helpers,mb_context_entries,mb_context_returns,mb_stack_outside,mb_stack_observations,mb_max_depth,mb_min_headroom,errors,arena_errors};memcpy(out,v,sizeof(v));}
'''
 cpp=out/'monitor.c';cpp.write_text(header+arena_source+source+footer);library=out/'monitor.dylib';run=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(cpp),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'build.log').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
 lib=c.CDLL(str(library));lib.begin.argtypes=[c.c_void_p,c.c_void_p,c.c_void_p];resident_buffer=c.create_string_buffer(resident);lib.step.argtypes=[c.c_uint32];lib.counts.argtypes=[c.POINTER(c.c_uint64)];native=e.Native();mirror=c.create_string_buffer(0x200000);negative=None;override=None;injected=False
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
    at=e.ARENA+allcases[0]['slot']*256+240-124+66;c.memmove(c.addressof(mirror)+at,bytes([mirror.raw[at]^1]),1);injected=True
  before=mirror.raw if pc in watched else None;guest=native.device.ram()if pc in watched else None;lib.step(pc);override=None
  if pc in watched:assert mirror.raw==before and native.device.ram()==guest,'Observer changed RAM'
  return real_execute(cycles)
 native.lib.m68k_execute=execute
 def replay(case,compiled):
  expected=e.execute(snapshot,case,payload,symbols,compiled);c.memmove(mirror,snapshot,0x200000);lib.begin(mirror,c.cast(callback,c.c_void_p),resident_buffer);actual=e.replay(native,snapshot,case,payload,symbols,compiled,expected);values=(c.c_uint64*18)();lib.counts(values);return list(values),actual
 allcases=e.arena_cases();
 # No valid task means a privileged boot caller. A user caller outside the pool is a separate rejection.
 for case in allcases:
  if case['slot']==101:case['sr']|=0x2000
 indexes={g*623+i for g in range(4)for i in [0,1,2,3,4,5,26,53,80,107,108,109,110]};indexes|={(f%4)*623+111+8*f for f in range(64)};indexes|={next(i for i,c in enumerate(allcases)if c['slot']==owner)for owner in range(102)};indexes|=set(range(2492,len(allcases)));rows=[];state=dict(status='qualifying_gpu_mailbox_observer',pid=os.getpid(),directory=str(out),planned=2*len(indexes),completed=0)
 def mark():e.save(out/'protocol.json',state);e.save(V/'task-arena-mailbox-live-observer-active.json',state)
 mark()
 try:
  for index,case_index in enumerate(sorted(indexes)):
   case=allcases[case_index];kind=int(case['entry']==0xe2b8)
   for compiled in [False,True]:
    values,_=replay(case,compiled);assert all(values[k]==0 for k in [6,7,8,12,16,17]),(case_index,compiled,values);assert values[kind]==values[4+kind]==1 and values[2+kind]==int(compiled)and values[9]==2 and values[10]==values[11]==int(compiled)
    rows.append(dict(case_index=case_index,compiled=compiled,counts=values));state['completed']=len(rows)
   if index%32==0:mark();print('Mailbox observer',len(rows),'/',state['planned'],flush=True)
  controls=[];positive,baseline=replay(allcases[0],True)
  for defect in ['return_D0','return_X','helper_X','context_SR']:
   negative=defect;injected=False;values,actual=replay(allcases[0],True);assert injected and actual==baseline and any(values[k]for k in [7,8]),(defect,values);controls.append(dict(defect=defect,rejected=True,native_CPU_or_RAM_changed=False,counts=values))
  negative=None;
  import copy
  invalid=copy.deepcopy(allcases[0]);invalid.update(task=0,slot=101,sp=0x1ff000,sr=0)
  values,_=replay(invalid,True);assert values[12]>0
  controls.append(dict(defect='unowned_user_original_stack',rejected=True,counts=values))
  e.save(out/'cases.json',rows);e.save(out/'controls.json',controls);inputs=[Path(__file__),Path(e.__file__),e.ROOT/'scripts/task_arena_observer_source_v1.py',include,arena_include,cpp,library,Path(gate['GPU_binary']),Path(gate['GPU_ELF']),e.ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib'];state.update(status='terminal_native_task_arena_mailbox_observer_qualified',cases=len(indexes),completed=len(rows),negative_controls=controls,source_sha256={str(p):e.sha(p)for p in inputs},scope=__doc__);mark();e.save(V/'task-arena-mailbox-live-observer-current.json',state);print({k:state[k]for k in ['status','cases','completed']})
 except BaseException as error:state.update(status='terminal_gpu_mailbox_observer_failed',error=repr(error));mark();raise
 finally:native.close()
if __name__=='__main__':main()
