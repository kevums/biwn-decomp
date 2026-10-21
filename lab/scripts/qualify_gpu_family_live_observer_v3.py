"""Qualify exact eight-root read-only CPU/context/acknowledgement oracle on real CPU replays."""
import ctypes as c,json,os,re,subprocess,copy
from pathlib import Path
from datetime import datetime,timezone
import native_gpu_family_arena_engine_v1 as e
from task_arena_observer_source_v1 import render as render_arena
from gpu_family_observer_source_v2 import render
V=e.ROOT/'verification'
class CPU(c.Structure):_fields_=[('r',c.c_uint32*16),('pc',c.c_uint32),('usp',c.c_uint32),('ssp',c.c_uint32),('sr',c.c_uint16)]
def main():
 build=e.read(V/'native-gpu-command-family-disc-build-current.json');gate=e.read(V/'gpu-family-arena-final-current.json');e.BASE=gate['GPU_address'];e.PARENT_OVERRIDE=build;e.ARENA=build['arena_address'];payload=Path(gate['GPU_binary']).read_bytes();symbols=gate['GPU_symbols'];resident=Path(build['component']).read_bytes();snapshot=bytearray((e.ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes());snapshot[build['resident_address']:build['resident_address']+len(resident)]=resident;snapshot=bytes(snapshot)
 original_seed=e.seed
 def seeded(*args):
  script=original_seed(*args);start=e.ARENA-build['resident_address'];script.memory[e.ARENA:e.ARENA+102*256]=resident[start:start+102*256];return script
 e.seed=seeded
 out=V/'GPU-family-live-observer-v3'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);source,include=render(build);arena_source,arena_include=render_arena(build)
 header='''#include <stdint.h>
#include <string.h>
#include <stdio.h>
struct cpu{uint32_t r[16],pc,usp,ssp;uint16_t sr;};
static const unsigned char*ram,*payload;static unsigned errors;static void(*read_cpu)(struct cpu*);
static uint32_t rd32(uint32_t a){if(a>0x1ffffcu){errors++;return 0;}return((uint32_t)ram[a]<<24)|((uint32_t)ram[a+1]<<16)|((uint32_t)ram[a+2]<<8)|ram[a+3];}
'''
 footer='''
void begin(const void*m,void*reader,const void*code){ram=m;payload=code;memset(arena_active,0,sizeof(arena_active));memset(arena_used,0,sizeof(arena_used));arena_errors=arena_guard_checks=arena_stack_observations=arena_unused_checks=arena_code_checks=arena_max_depth=0;arena_ready=1;read_cpu=(void(*)(struct cpu*))reader;errors=0;memset(mb_calls,0,sizeof(mb_calls));memset(mb_entries,0,sizeof(mb_entries));memset(mb_native,0,sizeof(mb_native));memset(mb_returns,0,sizeof(mb_returns));mb_slots=mb_pending=0;mb_old_steps=mb_source_steps=mb_errors=mb_context_errors=mb_helpers=mb_context_entries=mb_context_returns=mb_stack_outside=mb_stack_observations=mb_max_depth=mb_ack_checks=mb_stale_previews=0;mb_min_headroom=0xffffffffu;}
void step(uint32_t pc){watch_pool_arena(pc);watch_mailbox(pc);}
void counts(uint64_t*out){FILE*f=tmpfile();mb_dump(f);arena_dump(f);fclose(f);for(unsigned i=0;i<8;i++){out[i]=mb_entries[i];out[8+i]=mb_native[i];out[16+i]=mb_returns[i];}uint64_t v[]={mb_pending,mb_errors,mb_context_errors,mb_helpers,mb_context_entries,mb_context_returns,mb_stack_outside,mb_stack_observations,mb_max_depth,mb_min_headroom,errors,arena_errors,mb_ack_checks};memcpy(out+24,v,sizeof(v));}
'''
 cpp=out/'monitor.c';cpp.write_text(header+arena_source+source+footer);library=out/'monitor.dylib';run=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(cpp),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'build.log').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
 lib=c.CDLL(str(library));lib.begin.argtypes=[c.c_void_p,c.c_void_p,c.c_void_p];lib.step.argtypes=[c.c_uint32];lib.mb_retired.argtypes=[c.c_uint32,c.c_int32];lib.counts.argtypes=[c.POINTER(c.c_uint64)];lib.mb_set_gpu_reader.argtypes=[c.c_void_p];resident_buffer=c.create_string_buffer(resident);native=e.Native();mirror=c.create_string_buffer(0x200000);negative=None;override=None;injected=False;current_case=None
 def reader(target):
  cpu=CPU();cpu.r[:]=[native.lib.m68k_get_reg(None,i)for i in range(16)];cpu.pc=native.lib.m68k_get_reg(None,16);cpu.sr=native.lib.m68k_get_reg(None,17);cpu.usp=native.prefix[16]if cpu.sr&0x2000 else cpu.r[15];cpu.ssp=cpu.r[15]if cpu.sr&0x2000 else native.prefix[17]
  if override=='return_D0':cpu.r[0]^=1
  if override in ['return_X','helper_X']:cpu.sr^=16
  if override=='ack_register':cpu.r[8]=current_case['command']
  c.memmove(target,c.byref(cpu),c.sizeof(cpu))
 callback=c.CFUNCTYPE(None,c.POINTER(CPU))(reader)
 def gpu_reader(address,who):
  nonlocal injected
  value=native.lib.GPUReadLong(address,who)
  if negative=='ack_value':injected=True;return current_case['command']
  return value
 gpu_callback=c.CFUNCTYPE(c.c_uint32,c.c_uint32,c.c_uint32)(gpu_reader);lib.mb_set_gpu_reader(c.cast(gpu_callback,c.c_void_p));real_execute=native.lib.m68k_execute
 poll_text=re.search(r'mb_poll\[16\]=\{([^}]+)\}',source)[1];polls={int(v.strip().removesuffix('u'),16)for v in poll_text.split(',')}
 entries=set(e.ROOTS);original_returns={v[0]-2 for v in e.ROOTS.values()};native_returns={symbols[v[3]+'_return']for v in e.ROOTS.values()};watched=entries|original_returns|native_returns|{symbols[v[3]]for v in e.ROOTS.values()}|{0xe098,symbols['biwn_native_gpu_mailbox_body']}|polls
 def execute(cycles):
  nonlocal override,injected
  pc=native.lib.m68k_get_reg(None,16)
  if pc in watched:c.memmove(mirror,native.device.pointer,0x200000)
  if negative and not injected:
   if negative in ['return_D0','return_X']and pc in native_returns:override=negative;injected=True
   if negative=='helper_X'and pc==0xe098:override=negative;injected=True
   if negative=='context_SR'and pc==symbols['biwn_native_gpu_mailbox_body']:
    at=e.ARENA+current_case['slot']*256+240-124+66;c.memmove(c.addressof(mirror)+at,bytes([mirror.raw[at]^1]),1);injected=True
  before=mirror.raw if pc in watched else None;guest=native.device.ram()if pc in watched else None;lib.step(pc);override=None
  if pc in watched:assert mirror.raw==before and native.device.ram()==guest,'Read-only observer changed RAM'
  used=real_execute(cycles)
  if negative=='ack_value'and pc in polls and pc>=e.BASE:override='ack_register';injected=True
  lib.mb_retired(pc,used);override=None
  return used
 native.lib.m68k_execute=execute
 def replay(case,compiled):
  nonlocal current_case
  current_case=case;expected=e.execute(snapshot,case,payload,symbols,compiled);c.memmove(mirror,snapshot,0x200000);lib.begin(mirror,c.cast(callback,c.c_void_p),resident_buffer);actual=e.replay(native,snapshot,case,payload,symbols,compiled,expected);c.memmove(mirror,native.device.pointer,0x200000)
  if negative in ['arena_guard','unused_slot','resident_code']:
   at={'arena_guard':e.ARENA,'unused_slot':e.ARENA+101*256+80,'resident_code':build['resident_address']+32}[negative];c.memmove(c.addressof(mirror)+at,bytes([mirror.raw[at]^1]),1)
  before=mirror.raw;values=(c.c_uint64*37)();lib.counts(values);assert before==mirror.raw,'Dump modified observer mirror';return list(values),actual
 allcases=e.arena_cases()
 # Existing ownership contract:invalid identities use the privileged boot fallback.
 # User-mode invalid identities are explicit negative controls,not positive tasks.
 for case in allcases:
  if case['slot']==101:case['sr']|=0x2000
 indexes={g*623+i for g in range(16)for i in[0,1,2,3,4,5,26,53,80,107,108,109,110]}
 for group in range(16):
  flags=range(64)if group in[6,7,8,9]else[0,1,4,8,16,31,32,48,63]
  indexes|={group*623+111+8*f for f in flags}
 indexes|={next(i for i,x in enumerate(allcases)if x['slot']==owner)for owner in range(102)};indexes|=set(range(9968,len(allcases)));rows=[]
 state=dict(status='qualifying_eight_GPU_live_observer',pid=os.getpid(),directory=str(out),planned=2*len(indexes),completed=0,new_predictions=0,new_training=False)
 def mark():e.save(out/'protocol.json',state);e.save(V/'GPU-family-live-observer-active.json',state)
 mark()
 try:
  for j,index in enumerate(sorted(indexes)):
   case=allcases[index];kind=list(e.ROOTS).index(case['entry'])
   for compiled in[False,True]:
    values,_=replay(case,compiled);assert all(values[k]==0 for k in[24,25,26,30,34,35]),(index,compiled,values);assert values[kind]==values[16+kind]==1 and values[8+kind]==int(compiled)and values[27]==(1 if kind==4 else 2)and values[28]==values[29]==int(compiled)and values[36]>0
    rows.append(dict(case_index=index,compiled=compiled,counts=values));state['completed']=len(rows)
   if j%64==0:mark();print('Eight-root observer',len(rows),'/',state['planned'],flush=True)
  controls=[]
  for entry in e.ROOTS:
   selected=next(x for x in allcases if x['entry']==entry and x['slot']==0 and x['helper']=='original');negative=None;positive,baseline=replay(selected,True)
   for defect in['return_D0','return_X','helper_X','context_SR','ack_value']:
    negative=defect;injected=False;values,actual=replay(selected,True);assert injected and actual==baseline and any(values[k]for k in[25,26]),(hex(entry),defect,values);controls.append(dict(entry=hex(entry),defect=defect,rejected=True,native_CPU_or_RAM_changed=False,counts=values))
  selected=allcases[0];negative=None;_,baseline=replay(selected,True)
  for defect in['arena_guard','unused_slot','resident_code']:
   negative=defect;values,actual=replay(selected,True);assert actual==baseline and values[35]>0;controls.append(dict(defect=defect,rejected=True,native_CPU_or_RAM_changed=False,counts=values))
  for entry in e.ROOTS:
   invalid=copy.deepcopy(next(x for x in allcases if x['entry']==entry));invalid.update(task=0,slot=101,sp=0x1ff000,sr=0);negative=None;_,baseline=replay(invalid,False);values,actual=replay(invalid,True);assert values[30]>0 and actual==baseline;controls.append(dict(entry=hex(entry),defect='invalid_user_task_identity',rejected=True,native_CPU_or_RAM_changed=False,counts=values))
  negative=None;e.save(out/'cases.json',rows);e.save(out/'controls.json',controls);inputs=[Path(__file__),Path(e.__file__),e.ROOT/'scripts/gpu_family_observer_source_v2.py',include,arena_include,cpp,library,Path(gate['GPU_binary']),Path(gate['GPU_ELF']),Path(build['component']),e.ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib'];state.update(status='terminal_eight_GPU_roots_readonly_observer_qualified',cases=len(indexes),completed=len(rows),negative_controls=controls,source_sha256={str(p):e.sha(p)for p in inputs},scope=__doc__+' Full returnCPU/SR/banks/argument/context checks;retired actual operand capture and independent CMP flags;all102owners;43decoded mirror/callback-only defects plus8invalid-user-task negatives. Pre-read race and V1 fixture failure preserved;retirement sampling keeps predicates unchanged;positive boot-fallback cases are supervisor mode. Scripted replies,no frames/hardware/arbitraryIRQproof.');mark();e.save(V/'GPU-family-live-observer-current.json',state);print({k:state[k]for k in['status','cases','completed']})
 except BaseException as error:state.update(status='terminal_eight_GPU_observer_failed',error=repr(error));mark();raise
 finally:native.close()
if __name__=='__main__':main()
