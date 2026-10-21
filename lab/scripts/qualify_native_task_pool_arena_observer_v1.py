"""Qualify read-only pool return and arena ownership/guard observer.
Original and compiled real M68000 replay; mirror/callback negatives never change guest state.
"""
import ctypes as c,json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
import native_task_pool_engine_v1 as e
from task_arena_observer_source_v1 import render
V=e.ROOT/'verification'
class CPU(c.Structure):_fields_=[('r',c.c_uint32*16),('pc',c.c_uint32),('usp',c.c_uint32),('ssp',c.c_uint32),('sr',c.c_uint16)]
def main():
 build=json.loads((V/'native-task-pool-arena-disc-build-current.json').read_text());gate=json.loads((V/'task-pool-arena-final-current.json').read_text());e.BASE=gate['pool_address'];payload=Path(gate['pool_binary']).read_bytes();symbols=gate['pool_symbols'];resident=Path(build['component']).read_bytes();snapshot=bytearray((e.ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes());snapshot[build['resident_address']:build['resident_address']+len(resident)]=resident;snapshot=bytes(snapshot)
 out=V/'task-pool-arena-observer-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);source,include=render(build)
 header='''#include <stdint.h>
#include <string.h>
#include <stdio.h>
struct cpu{uint32_t r[16],pc,usp,ssp;uint16_t sr;};
static const unsigned char *ram,*payload;static void(*read_cpu)(struct cpu*);
static uint32_t rd32(uint32_t a){return((uint32_t)ram[a]<<24)|((uint32_t)ram[a+1]<<16)|((uint32_t)ram[a+2]<<8)|ram[a+3];}
'''
 footer='''
void begin(const void*m,void*reader,const void*code){ram=m;read_cpu=(void(*)(struct cpu*))reader;payload=code;pool_pending=0;pool_entries=pool_returns=pool_errors=pool_native_entries=pool_old_steps=pool_source_steps=0;arena_errors=arena_guard_checks=arena_unused_checks=arena_code_checks=0;arena_ready=1;memset(arena_active,0,sizeof(arena_active));memset(arena_used,0,sizeof(arena_used));}
void step(uint32_t pc){watch_pool_arena(pc);}
void counts(uint64_t*out){uint64_t v[]={pool_entries,pool_native_entries,pool_returns,pool_errors,pool_old_steps,pool_source_steps,pool_pending};memcpy(out,v,sizeof(v));}
unsigned bound(uint32_t task,uint32_t sp,unsigned active){memset(arena_active,0,sizeof(arena_active));arena_active[task_arena_slot(task)]=active;return task_stack_valid(task,sp);}
uint64_t arena_result(void){FILE*f=tmpfile();arena_dump(f);fclose(f);return arena_errors;}
'''
 cpp=out/'monitor.c';cpp.write_text(header+source+footer);library=out/'monitor.dylib';run=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(cpp),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'build.log').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
 lib=c.CDLL(str(library));lib.begin.argtypes=[c.c_void_p,c.c_void_p,c.c_void_p];lib.step.argtypes=[c.c_uint32];lib.counts.argtypes=[c.POINTER(c.c_uint64)];lib.bound.argtypes=[c.c_uint32,c.c_uint32,c.c_uint];lib.bound.restype=c.c_uint;lib.arena_result.restype=c.c_uint64
 native=e.Native();mirror=c.create_string_buffer(0x200000);resident_buffer=c.create_string_buffer(resident);override=None;negative=None;injected=False
 def reader(target):
  cpu=CPU();cpu.r[:]=[native.lib.m68k_get_reg(None,i)for i in range(16)];cpu.pc=native.lib.m68k_get_reg(None,16);cpu.sr=native.lib.m68k_get_reg(None,17);cpu.usp=native.prefix[16]if cpu.sr&0x2000 else cpu.r[15];cpu.ssp=cpu.r[15]if cpu.sr&0x2000 else native.prefix[17]
  if override=='return_D0':cpu.r[0]^=0x10000
  if override=='return_SR':cpu.sr^=0x100
  if override=='return_SSP':cpu.ssp^=4
  c.memmove(target,c.byref(cpu),c.sizeof(cpu))
 callback=c.CFUNCTYPE(None,c.POINTER(CPU))(reader);real_execute=native.lib.m68k_execute
 def step(pc):
  nonlocal override,injected
  if pc in [e.ENTRY,e.END]:c.memmove(mirror,native.device.pointer,0x200000)
  if pc==e.END and negative:
   if negative.startswith('return_'):override=negative;injected=True
   else:
    at={'free_link':0xc0d28,'untouched_header':0xc0928+16,'trap_vector':0x80}[negative];c.memmove(c.addressof(mirror)+at,bytes([mirror.raw[at]^1]),1);injected=True
  guest=native.device.ram()if pc in[e.ENTRY,e.END]else None;before=mirror.raw if guest is not None else None;lib.step(pc);override=None
  if guest is not None:assert native.device.ram()==guest and mirror.raw==before,'Observer mutated RAM'
 def execute(cycles):step(native.lib.m68k_get_reg(None,16));return real_execute(cycles)
 native.lib.m68k_execute=execute
 def replay(case,compiled):
  expected=e.execute(snapshot,case,payload,symbols,compiled);c.memmove(mirror,snapshot,0x200000);lib.begin(mirror,c.cast(callback,c.c_void_p),resident_buffer);actual=e.replay(native,snapshot,case,payload,symbols,compiled,expected);step(e.END);values=(c.c_uint64*7)();lib.counts(values);return list(values),actual
 rows=[];bounds=[];controls=[];state=dict(status='qualifying_pool_and_arena_observer',pid=os.getpid(),directory=str(out),completed=0)
 def mark():e.save(out/'protocol.json',state);e.save(V/'task-pool-arena-observer-active.json',state)
 mark()
 try:
  for i,case in enumerate(e.cases()):
   for compiled in [False,True]:
    values,_=replay(case,compiled);assert values[0]==values[2]==1 and values[1]==int(compiled) and values[3]==values[6]==0,(i,compiled,values);assert (values[4]==0 and values[5]>0)if compiled else(values[4]>0 and values[5]==0);rows.append(dict(case_index=i,compiled=compiled,counts=values))
   state['completed']=len(rows)
   if i%64==0:mark();print('Pool observer',len(rows),'/1024',flush=True)
  _,baseline=replay(e.cases()[0],True)
  for defect in ['return_D0','return_SR','return_SSP','free_link','untouched_header','trap_vector']:
   negative=defect;injected=False;values,actual=replay(e.cases()[0],True);assert injected and actual==baseline and values[3]>0;controls.append(dict(defect=defect,rejected=True,counts=values,guest_changed=False))
  negative=None
  for owner in range(102):
   task=0xc0928+owner*1024 if owner<101 else 0;top=build['arena_address']+owner*256+240
   for sp,active,want in [(top-224,1,1),(top,1,1),(top-225,1,0),(top+1,1,0),(top,0,0),(build['arena_address']+((owner+1)%102)*256+128,1,0)]:assert lib.bound(task,sp,active)==want;bounds.append([owner,sp,active,want])
   if owner<101:
    for sp,want in [(task+37,0),(task+38,1),(task+0x400,1),(task+0x401,0)]:assert lib.bound(task,sp,0)==want;bounds.append([owner,sp,0,want])
  for defect,at in [('guard',build['arena_address']),('unused_other_slot',build['arena_address']+256+32),('resident_code',build['resident_address']+100)]:
   c.memmove(mirror,snapshot,0x200000);lib.begin(mirror,c.cast(callback,c.c_void_p),resident_buffer);assert lib.arena_result()==0;c.memmove(c.addressof(mirror)+at,bytes([mirror.raw[at]^1]),1);assert lib.arena_result()>0;controls.append(dict(defect=defect,rejected=True,guest_changed=False))
  e.save(out/'cases.json',rows);e.save(out/'bounds.json',bounds);e.save(out/'controls.json',controls);inputs=[Path(__file__),Path(e.__file__),e.ROOT/'scripts/task_arena_observer_source_v1.py',include,cpp,library,Path(gate['pool_binary']),Path(gate['pool_ELF']),Path(build['component']),e.ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib'];state.update(status='terminal_native_pool_and_arena_observer_qualified',completed=len(rows),ownership_boundary_cases=len(bounds),negative_controls=controls,source_sha256={str(p):e.sha(p)for p in inputs},scope=__doc__);mark();e.save(V/'task-pool-arena-observer-current.json',state);print({k:state[k]for k in['status','completed','ownership_boundary_cases']})
 except BaseException as error:state.update(status='terminal_pool_arena_observer_failed',error=repr(error));mark();raise
 finally:native.close()
if __name__=='__main__':main()
