"""Qualify the exact live navigation C observer on original/native fixture runs.
Decoded observation negatives never alter actual guest CPU/RAM. Algorithm proof
remains6144 original-facing cases/all209sites; this is boundary instrumentation.
"""
import ctypes as c,json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
import native_actor_navigation_engine_v2 as e
from actor_navigation_observer_source import render
ROOT=e.ROOT;V=ROOT/'verification'
class CPU(c.Structure):_fields_=[('r',c.c_uint32*16),('pc',c.c_uint32),('usp',c.c_uint32),('ssp',c.c_uint32),('sr',c.c_uint16)]
def main():
 build=json.loads((V/'native-actor-navigation-disc-build-current.json').read_text());gate=json.loads((V/'native-actor-navigation-final-current.json').read_text());assert gate['cases']==6144;e.BASE=gate['code_address'];payload=Path(gate['binary']).read_bytes();symbols=gate['symbols'];snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
 out=V/'actor-navigation-live-observer'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);source,include=render(build)
 header='''#include <stdint.h>
#include <stdio.h>
#include <string.h>
struct cpu{uint32_t r[16],pc,usp,ssp;uint16_t sr;};
static const unsigned char*ram;static unsigned errors;static void(*read_cpu)(struct cpu*);
#define BIWN_NAVIGATION_TASK() (0x1ff000u-0x3bcu)
static uint32_t rd32(uint32_t a){if(a>0x1ffffcu){errors++;return 0;}return((uint32_t)ram[a]<<24)|((uint32_t)ram[a+1]<<16)|((uint32_t)ram[a+2]<<8)|ram[a+3];}
'''
 footer='''
static void array(FILE*f,const char*n,const uint64_t*v,unsigned count){fprintf(f,",\\"%s\\":[",n);for(unsigned i=0;i<count;i++)fprintf(f,"%s%llu",i?",":"",(unsigned long long)v[i]);fputc(']',f);}
void begin(const void*m,void*reader){ram=m;read_cpu=(void(*)(struct cpu*))reader;errors=0;memset(an_calls,0,sizeof(an_calls));an_slots=an_pending=0;memset(an_entries,0,sizeof(an_entries));memset(an_native,0,sizeof(an_native));memset(an_returns,0,sizeof(an_returns));memset(an_old_steps,0,sizeof(an_old_steps));memset(an_max_depth,0,sizeof(an_max_depth));for(unsigned i=0;i<4;i++)an_min_headroom[i]=0xffffffffu;an_errors=an_context_errors=an_context_entries=an_context_returns=an_stack_outside=an_stack_observations=an_source_steps=0;}
void step(uint32_t pc){watch_actor_navigation(pc);}
void counts(uint64_t*out){unsigned at=0;uint64_t scalars[]={an_pending,an_errors,an_context_errors,an_context_entries,an_context_returns,an_stack_outside,an_stack_observations,an_source_steps,errors};for(unsigned i=0;i<9;i++)out[at++]=scalars[i];const uint64_t*groups[]={an_entries,an_native,an_returns,an_old_steps,an_max_depth,an_min_headroom};for(unsigned g=0;g<6;g++)for(unsigned i=0;i<4;i++)out[at++]=groups[g][i];}
void dump(const char*path){FILE*f=fopen(path,"w");if(f){fputs("{\\"monitor\\":1",f);an_dump(f);fputs("}\\n",f);fclose(f);}}
'''
 cpp=out/'monitor.c';cpp.write_text(header+source+footer);library=out/'monitor.dylib';run=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(cpp),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'build.log').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
 lib=c.CDLL(str(library));lib.begin.argtypes=[c.c_void_p,c.c_void_p];lib.step.argtypes=[c.c_uint32];lib.counts.argtypes=[c.POINTER(c.c_uint64)]
 native=e.Native();mirror=c.create_string_buffer(0x200000);negative=None;override=None;injected=False;root=None
 def reader(target):
  cpu=CPU();cpu.r[:]=[native.lib.m68k_get_reg(None,i)for i in range(16)];cpu.pc=native.lib.m68k_get_reg(None,16);cpu.sr=native.lib.m68k_get_reg(None,17);cpu.usp=native.prefix[16]if cpu.sr&0x2000 else cpu.r[15];cpu.ssp=cpu.r[15]if cpu.sr&0x2000 else native.prefix[17]
  if override=='task_SP':cpu.r[15]=e.SP-920
  if override=='return_D2':cpu.r[2]^=1
  if override=='return_SR':cpu.sr^=16
  c.memmove(target,c.byref(cpu),c.sizeof(cpu))
 callback=c.CFUNCTYPE(None,c.POINTER(CPU))(reader);real_execute=native.lib.m68k_execute
 watched={0xf368,0x13f12,0x13f7c,0x13fea,0xf4d6,0x13f58,0x13f7a,0x13fc6,0x13fe8,0x14028,0x1404a,*build['navigation_entries'].values(),*build['navigation_returns'].values(),symbols['biwn_native_actor_navigation_body']}
 def execute(cycles):
  nonlocal override,injected
  pc=native.lib.m68k_get_reg(None,16)
  if pc in watched:c.memmove(mirror,native.device.pointer,0x200000)
  if negative and not injected:
   if negative=='task_SP'and pc==build['navigation_entries'][hex(root)]:override=negative;injected=True
   if negative in ['return_D2','return_SR']and pc==build['navigation_returns'][hex(root)]:override=negative;injected=True
   if negative=='context_metadata'and pc==symbols['biwn_native_actor_navigation_body']:
    at=e.SP-96-(8 if root==0xf368 else 0)+68;c.memmove(c.addressof(mirror)+at,bytes([mirror.raw[at]^1]),1);injected=True
  before=mirror.raw if pc in watched else None;guest=native.device.ram()if pc in watched else None
  lib.step(pc);override=None
  if pc in watched:assert mirror.raw==before and native.device.ram()==guest,'Observer changed RAM'
  return real_execute(cycles)
 native.lib.m68k_execute=execute
 def counts():
  values=(c.c_uint64*33)();lib.counts(values);return list(values)
 def replay(case,compiled):
  nonlocal root
  root=case['entry'];expected=e.execute(snapshot,case,payload,symbols,compiled);c.memmove(mirror,snapshot,0x200000);lib.begin(mirror,c.cast(callback,c.c_void_p));actual=e.replay(native,snapshot,case,payload,symbols,compiled,expected);return counts(),actual
 rows=[];groups=[];allcases=e.vectors()
 for entry in e.g.PATCH_WIDTHS:
  cases=[x for x in allcases if x['entry']==entry];groups.extend(cases[i]for i in sorted(set(list(range(8))+list(range(0,len(cases),32)))))
 state=dict(status='qualifying_navigation_live_observer',directory=str(out),pid=os.getpid(),planned=2*len(groups),completed=0)
 def mark():e.g.save(out/'protocol.json',state);e.g.save(V/'actor-navigation-live-observer-active.json',state)
 mark()
 try:
  for i,case in enumerate(groups):
   for compiled in [False,True]:
    values,_=replay(case,compiled)
    assert all(values[k]==0 for k in [0,1,2,5,8]),(i,compiled,values)
    assert sum(values[9:13])==sum(values[17:21])==1 and sum(values[13:17])==int(compiled)
    assert values[3]==values[4]==int(compiled)
    rows.append(dict(entry=case['entry'],compiled=compiled,counts=values));state['completed']=len(rows)
   if i%32==0:mark();print('Navigation observer',len(rows),'/',state['planned'],flush=True)
  controls=[];case=next(x for x in groups if x['entry']==0xf368)
  positive,baseline=replay(case,True)
  for defect in ['task_SP','return_D2','return_SR','context_metadata']:
   negative=defect;injected=False;values,actual=replay(case,True);assert injected and actual==baseline and any(values[k]for k in [1,2,5]),(defect,values)
   controls.append(dict(defect=defect,rejected=True,native_CPU_or_RAM_changed=False,counts=values))
  negative=None
  inputs=[Path(__file__),Path(e.__file__),Path(e.g.__file__),Path(e.g.navigation.__file__),include,ROOT/'scripts/actor_navigation_observer_source.py',cpp,library,Path(gate['binary']),Path(gate['ELF']),ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'render-assets/biwn-inventory-baseline.bin'];e.g.save(out/'cases.json',rows)
  state.update(status='terminal_navigation_live_observer_qualified',cases=len(groups),completed=len(rows),negative_controls=controls,source_sha256={str(p):e.g.sha(p)for p in inputs},scope=__doc__);mark();e.g.save(V/'actor-navigation-live-observer-current.json',state);print(json.dumps(dict(status=state['status'],cases=len(groups),executions=len(rows),negative_controls=len(controls))))
 except BaseException as error:state.update(status='terminal_navigation_live_observer_failed',error=repr(error));mark();raise
 finally:native.close()
if __name__=='__main__':main()
