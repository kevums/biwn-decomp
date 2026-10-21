"""Final-address dual-root ABI plus read-only parent/helper context canaries."""
import argparse,ctypes as c,json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
import actor_final_joint_environment as env
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
class CPU(c.Structure):_fields_=[('r',c.c_uint32*16),('pc',c.c_uint32),('usp',c.c_uint32),('ssp',c.c_uint32),('sr',c.c_uint16)]
def read(p):return json.loads(Path(p).read_text())
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);args=ap.parse_args();bp=ROOT/'verification/native-actor-initialize-disc-build-current.json';build=read(bp);snapshot,dispatch,init,symbols=env.prepare(build);j,ai=env.joint,env.initializer
 out=ROOT/'verification/actor-initialize-live-contexts'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 ad_path=ROOT/'scripts/native_actor_dispatch_canary_observer.inc.c';ai_path=ROOT/'scripts/native_actor_initialize_observer.inc.c';ad=ad_path.read_text();it=ai_path.read_text();ad_returns={}
 for name,target in [('actor',0x134dc),('sprite',0x137e0)]:
  pattern=b'\x4e\xb9'+target.to_bytes(4,'big');assert dispatch.count(pattern)==1;ad_returns[name]=build['actor_dispatch_start']+dispatch.index(pattern)+6
 maps=[(ad,{'__AD_ENTRY__':build['actor_dispatch_entry'],'__AD_START__':build['actor_dispatch_start'],'__AD_END__':build['actor_dispatch_end'],'__AD_RETURN__':build['actor_dispatch_return'],'__AD_ACTOR_CHILD_RETURN__':ad_returns['actor'],'__AD_SPRITE_CHILD_RETURN__':ad_returns['sprite']}),(it,{'__AI_ENTRY__':build['actor_initialize_entry'],'__AI_START__':build['actor_initialize_start'],'__AI_END__':build['actor_initialize_end'],'__AI_RETURN__':build['actor_initialize_return'],'__AI_OUTSIDE_CHILD_RETURN__':build['actor_initialize_helper_returns']['outside'],'__AI_INSIDE_CHILD_RETURN__':build['actor_initialize_helper_returns']['inside'],'__AI_TASK_CHILD_RETURN__':build['actor_initialize_helper_returns']['task']})];parts=[]
 for source,replacements in maps:
  for key,value in replacements.items():assert key in source;source=source.replace(key,str(value)+'u')
  parts.append(source)
 header='''#include <stdint.h>
#include <string.h>
struct cpu {uint32_t r[16],pc,usp,ssp;uint16_t sr;};
static const unsigned char *ram;static unsigned errors;static void(*read_cpu)(struct cpu*);
#define BIWN_ACTOR_DISPATCH_TASK() (0x1ff000u-0x404u)
#define BIWN_ACTOR_INITIALIZE_TASK() (0x1ff000u-0x404u)
static uint32_t rd16(uint32_t a){if(a>0x1ffffe){errors++;return 0;}return((uint32_t)ram[a]<<8)|ram[a+1];}
static uint32_t rd32(uint32_t a){if(a>0x1ffffc){errors++;return 0;}return(rd16(a)<<16)|rd16(a+2);}
static void emit(uint32_t pc){(void)pc;}
'''
 footer='''
void begin(const void*m,void*reader){ram=m;read_cpu=(void(*)(struct cpu*))reader;errors=0;
memset(ad_calls,0,sizeof(ad_calls));ad_slots=ad_pending=0;ad_entries=ad_native_entries=ad_returns=ad_old_steps=ad_native_steps=ad_errors=ad_child_entries=ad_child_returns=ad_actor=ad_sprite=ad_full=ad_stack_observations=ad_stack_outside=0;ad_max_depth=ad_max_child_depth=0;ad_min_context_clearance=ad_min_headroom=0xffffffffu;ad_context_collisions=ad_context_checks=ad_child_below_context=ad_context_SP_inside=0;
memset(ai_calls,0,sizeof(ai_calls));ai_slots=ai_pending=0;ai_entries=ai_native_entries=ai_returns=ai_old_steps=ai_native_steps=ai_errors=ai_helper_entries=ai_helper_returns=ai_context_checks=ai_context_corruptions=ai_stack_observations=ai_stack_outside=0;ai_max_depth=0;ai_min_headroom=0xffffffffu;}
void step(uint32_t pc){watch_actor_dispatch(pc);watch_actor_initialize(pc);}
unsigned check(unsigned ad_want,unsigned ai_want){return errors+(unsigned)(ad_errors+ad_context_collisions+ad_context_SP_inside+ad_stack_outside+ai_errors+ai_context_corruptions+ai_stack_outside)+ad_pending+ai_pending+(ad_entries!=ad_want)+(ad_returns!=ad_want)+(ai_entries!=ai_want)+(ai_returns!=ai_want);}
void counts(uint64_t *out){uint64_t a[]={ad_entries,ad_returns,ad_errors,ad_context_collisions,ad_context_SP_inside,ad_context_checks,ad_child_below_context,ai_entries,ai_returns,ai_errors,ai_context_checks,ai_context_corruptions,ai_helper_entries,ai_helper_returns,ad_max_depth,ai_max_depth};memcpy(out,a,sizeof(a));}
'''
 cpp=out/'monitor.c';cpp.write_text(header+'\n'.join(parts)+footer);library=out/'monitor.dylib';p=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(cpp),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'build.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 lib=c.CDLL(str(library));lib.begin.argtypes=[c.c_void_p,c.c_void_p];lib.step.argtypes=[c.c_uint32];lib.check.argtypes=[c.c_uint32,c.c_uint32];lib.check.restype=c.c_uint32;lib.counts.argtypes=[c.POINTER(c.c_uint64)]
 n=j.Native();mirror=c.create_string_buffer(0x200000);override=None;negative=None;injected=False
 def cpu_state():
  v=CPU();v.r[:]=[n.lib.m68k_get_reg(None,i)for i in range(16)];v.pc=n.lib.m68k_get_reg(None,16);v.sr=n.lib.m68k_get_reg(None,17);v.usp=n.prefix[16]if v.sr&0x2000 else v.r[15];v.ssp=v.r[15]if v.sr&0x2000 else n.prefix[17];return v
 def reader(target):
  v=override or cpu_state();c.memmove(target,c.byref(v),c.sizeof(v))
 callback=c.CFUNCTYPE(None,c.POINTER(CPU))(reader)
 watched={0x13ae0,0x134dc,0x137e0,0x102c4,0x10520,0xdf6c,0x13b3a,0x13b50,0x13b58,0x135f0,0x13602,0x137c6,0x137de,build['actor_dispatch_entry'],build['actor_dispatch_return'],build['actor_initialize_entry'],build['actor_initialize_return'],*ad_returns.values(),*build['actor_initialize_helper_returns'].values()}
 class Observer:
  def begin(self):
   c.memmove(mirror,n.device.pointer,0x200000);lib.begin(mirror,c.cast(callback,c.c_void_p))
  def step(self,pc):
   nonlocal override,injected
   if pc in watched:c.memmove(mirror,n.device.pointer,0x200000)
   if negative and not injected:
    if negative=='root_D0'and pc==build['actor_dispatch_return']:override=cpu_state();override.r[0]^=1;injected=True
    elif negative=='child_X'and pc==0x137e0:override=cpu_state();override.sr^=16;injected=True
    elif negative=='parent_context'and pc==ad_returns['sprite']:
     a=j.SP-336;c.memmove(c.addressof(mirror)+a,bytes([mirror.raw[a]^1]),1);injected=True
    elif negative=='initializer_context'and pc==build['actor_initialize_helper_returns']['outside']:
     a=ai.SP-480;c.memmove(c.addressof(mirror)+a,bytes([mirror.raw[a]^1]),1);injected=True
   before=mirror.raw[:0x200000]if pc in watched else None;native_before=n.device.ram()if pc in watched else None
   lib.step(pc);override=None
   if pc in watched:assert mirror.raw[:0x200000]==before and n.device.ram()==native_before,'Observer wrote fixture or native RAM'
 observer=Observer();rows=[];negatives=[];groups=[('dispatch',j,j.vectors(),dispatch),('initializer',ai,ai.vectors(),init)];totals=[0]*16
 if args.limit:groups=[(name,e,cases[:args.limit],code)for name,e,cases,code in groups]
 state=dict(status='qualifying_final_actor_context_canaries',directory=str(out),planned=sum(len(cases)*2 for _,_,cases,_ in groups),completed=0)
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/actor-initialize-live-contexts-active.json',state)
 mark()
 try:
  for name,e,cases,code in groups:
   for i,case in enumerate(cases):
    a=e.execute(snapshot,case,code,symbols,False);b=e.execute(snapshot,case,code,symbols,True);assert all(a[k]==b[k]for k in ['ram','registers','trace'])
    ad_want=int(case['entry']==0x13ae0);ai_want=sum(step['pc']==0x134dc for step in a['machine']);outputs=[]
    for compiled,expected in [(False,a),(True,b)]:
     output=env.native_replay(e,n,snapshot,case,code,symbols,compiled,expected,observer);error=lib.check(ad_want,ai_want);counts=(c.c_uint64*16)();lib.counts(counts)
     if error:save(out/'failure.json',dict(group=name,index=i,case=case,compiled=compiled,error=error,counts=list(counts)));raise AssertionError('Final context oracle mismatch')
     outputs.append(output);rows.append(dict(group=name,index=i,compiled=compiled,counts=list(counts),private_depth=expected['private_depth']));totals=[x+y for x,y in zip(totals,counts)]
    assert outputs[0]==outputs[1],'Full native CPU/SR/bank/helper entry mismatch'
    state['completed']=len(rows)
    if i%64==0:mark();print('Contexts',name,i+1,'/',len(cases),flush=True)
  for negative,name,e,case,code,wants in [('root_D0','dispatch',j,j.vectors()[0],dispatch,(1,0)),('child_X','dispatch',j,j.vectors()[0],dispatch,(1,0)),('parent_context','dispatch',j,j.vectors()[0],dispatch,(1,0)),('initializer_context','initializer',ai,ai.vectors()[0],init,(0,1))]:
   injected=False;expected=e.execute(snapshot,case,code,symbols,True);env.native_replay(e,n,snapshot,case,code,symbols,True,expected,observer);error=lib.check(*wants);counts=(c.c_uint64*16)();lib.counts(counts);assert injected and error>0,negative
   if negative=='parent_context':assert error==counts[3]==1
   if negative=='initializer_context':assert error==counts[11]==1
   negatives.append(dict(defect=negative,rejected=True,error=error,counts=list(counts),native_CPU_or_RAM_changed=False));negative=None
  paths=[Path(__file__),Path(env.__file__),Path(j.__file__),Path(ai.__file__),ad_path,ai_path,cpp,library,bp,Path(build['component_gate']),Path(build['component']),ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'tools/libbiwn-movement-device.dylib']
  save(out/'results.json',rows);state.update(status='terminal_actor_context_canaries_preflight_pass'if args.limit else'terminal_final_actor_joint_and_context_canaries_pass',completed=len(rows),dispatch_cases=len(groups[0][2]),initializer_cases=len(groups[1][2]),negative_controls=negatives,counter_totals=totals,AD_capture_returns=ad_returns,AI_capture_returns=build['actor_initialize_helper_returns'],source_sha256={str(p):sha(p)for p in paths},scope=__doc__+' Both rooted functions compared original-versus-C on common relocated parent helper code; four leaf services prescribed in fixtures. Instruction observation precedes service mutations. Monitor sees an exact fixture RAM mirror at watched boundaries; negatives alter only decoded CPU or mirror context bytes. Full original-root/helper ABI, publicRAM/ordered traces and nativeCPU checked; arbitrary concurrency/faults/live real helper behavior remain separate.',new_predictions=0)
  mark()
  if not args.limit:save(ROOT/'verification/actor-initialize-live-contexts-current.json',state)
  print(json.dumps({k:state[k]for k in ['status','dispatch_cases','initializer_cases']}))
 except BaseException as error:state.update(status='terminal_actor_context_canaries_failed',error=repr(error),completed=len(rows));mark();raise
 finally:n.close()

if __name__=='__main__':main()
