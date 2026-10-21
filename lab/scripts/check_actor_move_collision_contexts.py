"""Final13C9A read-only root/helper/context oracle and corruption qualification."""
import argparse,ctypes as c,json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
import actor_move_collision_final_environment as env
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
class CPU(c.Structure):_fields_=[('r',c.c_uint32*16),('pc',c.c_uint32),('usp',c.c_uint32),('ssp',c.c_uint32),('sr',c.c_uint16)]
def read(p):return json.loads(Path(p).read_text())
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);args=ap.parse_args();bp=ROOT/'verification/native-actor-move-disc-build-current.json';build=read(bp);snapshot,payload,symbols=env.prepare(build);e=env.engine;gate=read(build['component_gate']);assert payload==Path(gate['binary']).read_bytes()and sha(build['component'])==build['component_sha256']and sha(build['derived_stage'])==build['derived_stage_sha256']
 out=ROOT/'verification/actor-move-collision-contexts'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);sourcepath=ROOT/'scripts/native_actor_move_observer.inc.c';source=sourcepath.read_text();values={'__AM_ENTRY__':build['actor_move_entry'],'__AM_START__':build['actor_move_start'],'__AM_END__':build['actor_move_end'],'__AM_RETURN__':build['actor_move_return'],'__AM_DIRECTION_CHILD_RETURN__':build['actor_move_helper_returns']['direction'],'__AM_SUBMIT_CHILD_RETURN__':build['actor_move_helper_returns']['submit'],'__AM_OUTDOOR_CHILD_RETURN__':build['actor_move_helper_returns']['outdoor'],'__AM_INDOOR_CHILD_RETURN__':build['actor_move_helper_returns']['indoor']}
 for k,v in values.items():assert k in source;source=source.replace(k,str(v)+'u')
 header='''#include <stdint.h>
#include <string.h>
struct cpu{uint32_t r[16],pc,usp,ssp;uint16_t sr;};
static const unsigned char*ram;static unsigned errors;static void(*read_cpu)(struct cpu*);
#define BIWN_ACTOR_MOVE_TASK() (0x1ff000u-0x3bcu)
static uint32_t rd16(uint32_t a){if(a>0x1ffffe){errors++;return 0;}return((uint32_t)ram[a]<<8)|ram[a+1];}
static uint32_t rd32(uint32_t a){if(a>0x1ffffc){errors++;return 0;}return(rd16(a)<<16)|rd16(a+2);}
static void emit(uint32_t pc){(void)pc;}
'''
 footer='''
void begin(const void*m,void*reader){ram=m;read_cpu=(void(*)(struct cpu*))reader;errors=0;memset(am_calls,0,sizeof(am_calls));am_slots=am_pending=0;am_entries=am_native_entries=am_returns=am_old_steps=am_native_steps=am_errors=am_helper_entries=am_helper_returns=am_context_checks=am_context_corruptions=am_stack_observations=am_stack_outside=am_direction_calls=am_submit_calls=am_outdoor_calls=am_indoor_calls=0;am_max_depth=0;am_min_headroom=0xffffffffu;}
void step(uint32_t pc){watch_actor_move(pc);}
unsigned check(unsigned helpers){return errors+am_errors+am_context_corruptions+am_stack_outside+am_pending+(am_entries!=1)+(am_returns!=1)+(am_helper_entries!=helpers)+(am_helper_returns!=helpers);}
void counts(uint64_t*out){uint64_t a[]={am_entries,am_native_entries,am_returns,am_errors,am_context_checks,am_context_corruptions,am_helper_entries,am_helper_returns,am_stack_outside,am_pending,am_max_depth,am_min_headroom,am_direction_calls,am_submit_calls,am_outdoor_calls,am_indoor_calls};memcpy(out,a,sizeof(a));}
'''
 cpp=out/'monitor.c';cpp.write_text(header+source+footer);library=out/'monitor.dylib';p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(cpp),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'build.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 lib=c.CDLL(str(library));lib.begin.argtypes=[c.c_void_p,c.c_void_p];lib.step.argtypes=[c.c_uint32];lib.check.argtypes=[c.c_uint32];lib.check.restype=c.c_uint32;lib.counts.argtypes=[c.POINTER(c.c_uint64)];n=e.Native();mirror=c.create_string_buffer(0x200000);override=None;negative=None;injected=False
 def cpu_state():
  x=CPU();x.r[:]=[n.lib.m68k_get_reg(None,i)for i in range(16)];x.pc=n.lib.m68k_get_reg(None,16);x.sr=n.lib.m68k_get_reg(None,17);x.usp=n.prefix[16]if x.sr&0x2000 else x.r[15];x.ssp=x.r[15]if x.sr&0x2000 else n.prefix[17];return x
 def reader(target):
  x=override or cpu_state();c.memmove(target,c.byref(x),c.sizeof(x))
 callback=c.CFUNCTYPE(None,c.POINTER(CPU))(reader);watched={e.ENTRY,build['actor_move_entry'],build['actor_move_start'],build['actor_move_return'],0x13f10,0x13440,0xe220,0x13b5a,0x13bb0,0x13cce,0x13d7a,0x13e8a,0x13ee6,*build['actor_move_helper_returns'].values()}
 class Observer:
  def begin(self):c.memmove(mirror,n.device.pointer,0x200000);lib.begin(mirror,c.cast(callback,c.c_void_p))
  def step(self,pc):
   nonlocal override,injected
   if pc in watched:c.memmove(mirror,n.device.pointer,0x200000)
   if negative and not injected:
    if negative=='callee_D2'and pc==build['actor_move_return']:override=cpu_state();override.r[2]^=1;injected=True
    elif negative=='helper_X'and pc==0x13440:override=cpu_state();override.sr^=16;injected=True
    elif negative=='saved_context'and pc==build['actor_move_helper_returns']['direction']:
     a=e.SP-488;c.memmove(c.addressof(mirror)+a,bytes([mirror.raw[a]^1]),1);injected=True
    elif negative=='task_stack_boundary'and pc==build['actor_move_start']:override=cpu_state();override.r[15]=e.SP-0x3bc+36;injected=True
   before=mirror.raw[:0x200000]if pc in watched else None;actual=n.device.ram()if pc in watched else None;lib.step(pc);override=None
   if pc in watched:assert mirror.raw[:0x200000]==before and n.device.ram()==actual,'Read-only observer wrote RAM'
 observer=Observer();cases=e.vectors();cases=cases[:args.limit]if args.limit else cases;state=dict(status='qualifying_final_movement_context_oracle',directory=str(out),pid=os.getpid(),planned=2*len(cases),completed=0);rows=[];negatives=[]
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/actor-move-collision-contexts-active.json',state)
 mark()
 try:
  for i,case in enumerate(cases):
   a=e.execute(snapshot,case,payload,symbols,False);b=e.execute(snapshot,case,payload,symbols,True);assert all(a[k]==b[k]for k in ['ram','registers','trace']);helpers=sum(s['pc']in[0x13440,0xe220,0x13b5a,0x13bb0]for s in a['machine']);outputs=[]
   for compiled,expected in [(False,a),(True,b)]:
    result=env.native_replay(e,n,snapshot,case,payload,symbols,compiled,expected,observer);counts=(c.c_uint64*16)();lib.counts(counts);error=lib.check(helpers)
    if error:save(out/'failure.json',dict(index=i,case=case,compiled=compiled,errors=error,counts=list(counts)));raise AssertionError('Movement context oracle mismatch')
    outputs.append(result);rows.append(dict(index=i,compiled=compiled,counts=list(counts),private_depth=expected['private_depth']))
   assert outputs[0]==outputs[1];state['completed']=len(rows)
   if i%64==0:mark();print('Movement contexts',i+1,'/',len(cases),flush=True)
  for negative in ['callee_D2','helper_X','saved_context','task_stack_boundary']:
   injected=False;case=e.vectors()[0];expected=e.execute(snapshot,case,payload,symbols,True);helpers=sum(s['pc']in[0x13440,0xe220,0x13b5a,0x13bb0]for s in expected['machine']);env.native_replay(e,n,snapshot,case,payload,symbols,True,expected,observer);counts=(c.c_uint64*16)();lib.counts(counts);error=lib.check(helpers);assert injected and error>0
   if negative=='saved_context':assert error==counts[5]==1
   if negative=='task_stack_boundary':assert error==counts[8]==1
   negatives.append(dict(defect=negative,rejected=True,error=error,counts=list(counts),native_CPU_or_RAM_changed=False))
  negative=None;paths=[Path(__file__),Path(env.__file__),Path(e.__file__),Path(e.g.__file__),sourcepath,cpp,library,bp,Path(build['component_gate']),Path(build['component']),ROOT/'verification/native-actor-collision-final-current.json',Path(e.__file__),Path(e.g.__file__),ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'tools/libbiwn-movement-device.dylib'];save(out/'results.json',rows);state.update(status='terminal_movement_context_oracle_preflight_pass'if args.limit else'terminal_final_movement_context_oracle_pass',cases=len(cases),completed=len(rows),negative_controls=negatives,AM_capture_returns=build['actor_move_helper_returns'],max_private_depth=max(x['private_depth']for x in rows if x['compiled']),source_sha256={str(p):sha(p)for p in paths},scope=__doc__+' Original/C lanes execute actual direction, collision and geometry; only E220GPU effects prescribed. Root headroom918bytes matches worst observed live movement entry. Task header and128bytes below have byte canaries checked after each replay. FullnativeCPU/SR/banks/orderedpublicRAM/helperentry comparisons separate from read-only context checks. Monitor sees exactRAMmirror at watched boundaries before scripted effects. Negatives alter decodedCPU/mirror only; no nativeCPU/RAM changes. Arbitrary concurrency/faults/live real-helper behavior remain separate.',new_predictions=0);mark()
  if not args.limit:save(ROOT/'verification/actor-move-collision-contexts-current.json',state)
  print(json.dumps({k:state[k]for k in ['status','cases','completed','max_private_depth']}))
 except BaseException as error:state.update(status='terminal_movement_context_oracle_failed',error=repr(error));mark();raise
 finally:n.close()
if __name__=='__main__':main()
