"""Actual game-call return ABI versus isolated original M68000 routines.
Records come from a separate read-only fresh-game capture. This gate proves
scalar arithmetic call semantics, not whole-game timing equivalence.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,os,subprocess,ctypes as c
import numpy as np
from check_biwn_native_button_digit import ROOT,sha,save
from check_biwn_scheduler import Native
CPU_DTYPE=np.dtype(dict(names=['registers','pc','usp','ssp','sr'],formats=[('<u4',(16,)),'<u4','<u4','<u4','<u2'],offsets=[0,64,68,72,76],itemsize=80))
PAIR_DTYPE=np.dtype(dict(names=['entry','numerator','denominator','start_frame','end_frame','depth','return_pc','before','after'],formats=['<u4']*7+[CPU_DTYPE,CPU_DTYPE],offsets=[0,4,8,12,16,20,24,28,108],itemsize=188))
ORACLE=r'''
#include <stdint.h>
#include <string.h>
struct cpu {uint32_t r[16],pc,usp,ssp;uint16_t sr;};
struct pair {uint32_t entry,numerator,denominator,start_frame,end_frame,depth,return_pc;struct cpu before,after;};
struct host {void(*reset)(void);void(*set_irq)(uint32_t);void(*set_reg)(int,uint32_t);uint32_t(*get_reg)(void*,int);int(*execute)(int);unsigned char*ram;uint32_t*prefix;};
struct result {uint32_t status,index,field,steps;uint64_t completed,original_instructions;struct cpu got,want;};
_Static_assert(sizeof(struct pair)==188,"record ABI");
static void put32(unsigned char*p,uint32_t a,uint32_t value){p[a]=(unsigned char)(value>>24);p[a+1]=(unsigned char)(value>>16);p[a+2]=(unsigned char)(value>>8);p[a+3]=(unsigned char)value;}
int original_replay(const struct host*h,const struct pair*records,uint32_t count,struct result*out){
 uint32_t i,j,pc,sp;const struct pair*p;struct cpu got;memset(out,0,sizeof(*out));
 for(i=0;i<count;i++){
  p=records+i;out->index=i;
  if(p->entry!=0xe540&&p->entry!=0xe588&&p->entry!=0xe60a){out->status=1;return 1;}
  if(p->entry!=0xe540&&!p->denominator){out->status=2;return 2;}
  sp=p->before.r[15];if(sp<256||sp>0x1ffff4||p->after.r[15]!=sp+4||p->after.pc!=p->return_pc){out->status=3;return 3;}
  h->reset();h->set_irq(0);
  h->set_reg(17,0x2000);h->set_reg(15,p->before.ssp);
  h->set_reg(17,0);h->set_reg(15,p->before.usp);
  h->set_reg(17,p->before.sr);
  for(j=0;j<16;j++)h->set_reg((int)j,p->before.r[j]);
  put32(h->ram,sp,p->return_pc);put32(h->ram,sp+4,p->numerator);put32(h->ram,sp+8,p->denominator);
  h->set_reg(16,p->entry);
  for(j=0;j<2048;j++){
   pc=h->get_reg(0,16);
   if(pc==p->return_pc&&h->get_reg(0,15)==sp+4)break;
   if(pc<0xe540||pc>=0xe61c){out->status=4;out->field=pc;return 4;}
   h->execute(1);out->original_instructions++;
  }
  out->steps=j;if(j==2048){out->status=5;return 5;}
  memset(&got,0,sizeof(got));for(j=0;j<16;j++)got.r[j]=h->get_reg(0,(int)j);
  got.pc=h->get_reg(0,16);got.sr=(uint16_t)h->get_reg(0,17);
  got.usp=got.sr&0x2000?h->prefix[16]:got.r[15];got.ssp=got.sr&0x2000?got.r[15]:h->prefix[17];
  out->got=got;out->want=p->after;
  for(j=0;j<16;j++)if(got.r[j]!=p->after.r[j]){out->status=6;out->field=j;return 6;}
  if(got.pc!=p->after.pc){out->status=6;out->field=16;return 6;}
  if(got.sr!=p->after.sr){out->status=6;out->field=17;return 6;}
  if(got.usp!=p->after.usp){out->status=6;out->field=18;return 6;}
  if(got.ssp!=p->after.ssp){out->status=6;out->field=19;return 6;}
  out->completed++;
 }
 return 0;
}
'''
class CPU(c.Structure):_fields_=[('registers',c.c_uint32*16),('pc',c.c_uint32),('usp',c.c_uint32),('ssp',c.c_uint32),('sr',c.c_uint16)]
class Host(c.Structure):_fields_=[(name,c.c_void_p)for name in ['reset','set_irq','set_reg','get_reg','execute','ram','prefix']]
class Result(c.Structure):_fields_=[('status',c.c_uint32),('index',c.c_uint32),('field',c.c_uint32),('steps',c.c_uint32),('completed',c.c_uint64),('original_instructions',c.c_uint64),('got',CPU),('want',CPU)]
def cpu_json(s):return dict(registers=list(s.registers),pc=s.pc,usp=s.usp,ssp=s.ssp,sr=s.sr)
def main():
 out=ROOT/'verification/native-math-live-replay'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 cap_path=ROOT/'verification/native-math-live-capture-current.json';cap=json.loads(cap_path.read_text());assert cap['status']=='terminal_actual_native_math_calls_captured_unchanged_game'
 for path,digest in cap['source_sha256'].items():assert sha(path)==digest
 assert sha(cap['records'])==cap['records_sha256'];reference_path=ROOT/'verification/native-math-reference-original-disc-current.json';reference=json.loads(reference_path.read_text());assert sha(reference['original_reference'])==reference['original_reference_sha256']
 records=np.memmap(cap['records'],mode='r',dtype=PAIR_DTYPE);assert len(records)==138014
 source=out/'original_replay.c';source.write_text(ORACLE);library=out/'liboriginal-replay.dylib';command=['clang','-dynamiclib','-std=c11','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(library)]
 built=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(built.stdout+built.stderr);assert built.returncode==0,built.stderr
 n=Native();n.device.seed(Path(reference['original_reference']).read_bytes(),0);n.device.lib.lab_device_observe(type(n.device.observer)())
 lib=n.lib;host=Host(*[c.cast(getattr(lib,name),c.c_void_p)for name in ['m68k_pulse_reset','m68k_set_irq','m68k_set_reg','m68k_get_reg','m68k_execute']],n.device.pointer,c.cast(n.prefix,c.c_void_p))
 bridge=c.CDLL(str(library));bridge.original_replay.argtypes=[c.POINTER(Host),c.c_void_p,c.c_uint32,c.POINTER(Result)];bridge.original_replay.restype=c.c_int
 state=dict(status='prepared',pid=os.getpid(),directory=str(out),capture_proof=str(cap_path),capture_proof_sha256=sha(cap_path),record_count=len(records),whole_game_complete=False,game_clock_replayed=False)
 def checkpoint():save(out/'protocol.json',state);save(ROOT/'verification/native-math-live-replay-active.json',state)
 checkpoint();print(out,flush=True)
 try:
  result=Result();state['status']='replaying_original_arithmetic';checkpoint();code=bridge.original_replay(c.byref(host),c.c_void_p(records.ctypes.data),len(records),c.byref(result))
  detail=dict(code=code,index=result.index,field=result.field,completed=result.completed,steps=result.steps,original_instructions=result.original_instructions,original_expected=cpu_json(result.got),live_native_return=cpu_json(result.want));save(out/'result.json',detail)
  assert code==0,detail
  byentry={hex(entry):int(np.count_nonzero(records['entry']==entry))for entry in [0xe540,0xe588,0xe60a]};frames=[int(records['start_frame'].min()),int(records['end_frame'].max())]
  deps={str(path):sha(path)for path in [source,library,Path(__file__),Path(reference['original_reference']),ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'tools/libbiwn-movement-device.dylib']};n.close()
  state.update(status='terminal_all_actual_native_arithmetic_returns_match_original_replay',completed_calls=result.completed,entry_counts=byentry,frame_span=frames,original_instructions=result.original_instructions,all_D_A_registers_PC_SR_USP_SSP_match=True,zero_denominators_observed=0,new_training=False,source_and_dependencies_sha256=deps,original_disc_reference_proof=str(reference_path),original_disc_reference_proof_sha256=sha(reference_path),scope='Every138014completed arithmetic call captured from the real fresh24000frame native run matches original M68000 function execution on its actual scalar args/full incoming CPU. AllD/A,PC,SR,USP/SSP match. Pure argument/private-stack routines are replayed in isolation with no IRQ/clock or game/device continuation; this proves return semantics, not whole-game scheduling/video equivalence. No zero divisor occurred;512earlierzero-exception cases remain separate.')
  checkpoint();save(ROOT/'verification/native-math-live-replay-current.json',state);print(json.dumps({k:state[k]for k in ['status','completed_calls','entry_counts','original_instructions']}),flush=True)
 except BaseException as error:state.update(status='terminal_failed',error=repr(error));checkpoint();raise
if __name__=='__main__':main()
