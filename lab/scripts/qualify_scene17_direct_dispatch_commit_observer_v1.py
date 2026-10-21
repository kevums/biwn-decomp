"""Native rotation/display boundary witnesses from actual CPU steps and host-only corruption replays."""
import ctypes as c,importlib.util,sys,subprocess
from pathlib import Path
from datetime import datetime,timezone
import scene17_host_runtime_v1 as support
import shared_deck_scene17_direct_dispatch_full_observer_v1 as monitor
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha

def main():
 bp=V/'native-scene17-direct-dispatch-disc-build-v1-current.json';b=read(bp);out=V/'scene17-direct-dispatch-commit-observer-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 stub='''#include <stdint.h>\n#include <stdio.h>\n#include <string.h>\nstruct cpu{uint32_t r[16],pc,usp,ssp;uint16_t sr;};\nstatic struct cpu current;static uint8_t memory[0x200000],*ram=memory;\nstatic uint32_t rd32(uint32_t a){return ((uint32_t)ram[a]<<24)|((uint32_t)ram[a+1]<<16)|((uint32_t)ram[a+2]<<8)|ram[a+3];}\nstatic uint16_t rd16(uint32_t a){return ((uint16_t)ram[a]<<8)|ram[a+1];}\nstatic void read_cpu(struct cpu *s){*s=current;}\n'''
 extra='''\nvoid snapshot(const void *raw,const struct cpu *s){memcpy(memory,raw,sizeof(memory));current=*s;}\nvoid pc(uint32_t v){r25_watch(v);d27_watch(v);}\nvoid clear(void){memset(r25_slots,0,sizeof(r25_slots));memset(d27_slots,0,sizeof(d27_slots));r25_entries=r25_returns=r25_helpers=r25_helper_returns=r25_errors=d27_entries=d27_returns=d27_errors=d27_original_entries=d27_original_returns=0;}\nuint64_t stat(unsigned n){if(n==0)return r25_entries;if(n==1)return r25_returns;if(n==2)return r25_helpers;if(n==3)return r25_helper_returns;if(n==4)return r25_errors;if(n==5)return r25_pending_total();if(n==6)return d27_entries;if(n==7)return d27_returns;if(n==8)return d27_errors;if(n==9)return d27_pending_total();if(n==10)return d27_original_entries;return d27_original_returns;}\n'''
 source=out/'fixture.c';source.write_text(stub+monitor.prior.rotation_monitor(b)+monitor.display_monitor(b)+extra);lib=out/'fixture.dylib';q=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(lib)],capture_output=True,text=True);(out/'compiler.log').write_text(q.stdout+q.stderr);assert q.returncode==0,q.stderr
 f=c.CDLL(str(lib));f.snapshot.argtypes=[c.c_void_p,c.c_void_p];f.pc.argtypes=[c.c_uint32];f.stat.argtypes=[c.c_uint];f.stat.restype=c.c_uint64;f.rotation_dump.argtypes=[c.c_char_p];f.display_dump.argtypes=[c.c_char_p]
 syms=b['shared_Deck_symbols'];sites={syms[k]for k in ['biwn_v25_rotation_begin','biwn_v25_rotation_end','biwn_v27_display_begin','biwn_v27_display_end']};rows=[];checkpoints=[];selected=False;collect=False;original=support.Runtime
 def valid(v):return v[4]==v[5]==v[8]==v[9]==v[10]==v[11]==0 and all(v[i]==v[0]for i in [1,2,3,6,7])
 def finish():
  values=[f.stat(i)for i in range(12)]
  if not any(values):return
  assert valid(values),values;rows.append(dict(rotation_entries=values[0],display_entries=values[6],errors=values[4]+values[8],pending=values[5]+values[9]));f.clear()
 class Observed(original):
  in_reference=False
  def reset(self,*args):finish();f.clear();return super().reset(*args)
  def native(self,*args):
   self.in_reference=True
   try:return super().native(*args)
   finally:self.in_reference=False;f.clear()
  def __init__(self,*args):
   super().__init__(*args);self.old_execute=self.core.m68k_execute
   def step(*args):
    nonlocal collect,selected
    if not self.in_reference:
     state=super(Observed,self).cpu()
     if state.pc in sites:
      raw=self.device.ram()
      if state.pc==syms['biwn_v25_rotation_begin']and not selected:collect=True
      if collect:checkpoints.append((raw,support.base.CPU.from_buffer_copy(bytes(state))))
      f.snapshot(c.create_string_buffer(raw),c.byref(state));f.pc(state.pc)
      if state.pc==syms['biwn_v25_rotation_end']and collect:collect=False;selected=True
    return self.old_execute(*args)
   self.core.m68k_execute=step
  def close(self):finish();self.core.m68k_execute=self.old_execute;return super().close()
 support.Runtime=Observed;f.clear()
 try:
  text=(ROOT/'scripts/check_scene17_direct_dispatch_final_bridge_v1.py').read_text().replace("out=V/'scene17-direct-dispatch-final-bridge-v1'","out=V/'scene17-direct-dispatch-commit-observed-body-v1'")
  script=out/'actual-native-harness.py';script.write_text(text);spec=importlib.util.spec_from_file_location('display_monitor_actual',script);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);sys.argv=[str(script),'--limit','64'];m.main();finish()
 finally:support.Runtime=original
 assert sum(x['display_entries']for x in rows)>0
 assert [x.pc for _,x in checkpoints]==[syms[k]for k in ['biwn_v25_rotation_begin','biwn_v27_display_begin','biwn_v27_display_end','biwn_v25_rotation_end']]
 raw0,_=checkpoints[0];task=int.from_bytes(raw0[0xc0920:0xc0924],'big');frame=b['deck_arena_address']+task-0xc0928+144;raw2,_=checkpoints[2];guest_sp=int.from_bytes(checkpoints[1][0][frame+64:frame+68],'big');gframe=guest_sp-4;records=int.from_bytes(raw2[guest_sp+4:guest_sp+8],'big');field_end=int.from_bytes(raw2[gframe-16:gframe-12],'big');count=(field_end-records-18)//36;output_end=int.from_bytes(raw2[frame+36:frame+40],'big');faults=[]
 for i,(raw,state)in enumerate(checkpoints):(out/f'checkpoint-{i}-RAM.bin').write_bytes(raw);save(out/f'checkpoint-{i}-CPU.json',support.base.cd.scheduler.cpu_dict(state))
 def replay(name,mutate=None,skip=None):
  f.clear()
  for i,(raw,cpu)in enumerate(checkpoints):
   if i==skip:continue
   memory=bytearray(raw);state=support.base.CPU.from_buffer_copy(bytes(cpu))
   if mutate:mutate(i,memory,state)
   f.snapshot(c.create_string_buffer(bytes(memory)),c.byref(state));f.pc(state.pc)
  values=[f.stat(i)for i in range(12)];save(out/('control-'+name+'.json'),dict(values=values));return valid(values)and values[0]==1
 assert replay('legal')
 mutations=[('rotation_begin_PC',0,frame+68),('rotation_begin_bank',0,frame+72),('rotated_buffers',1,0xbd83c),('display_pointer',1,0x43daa),('display_entry_A0',1,frame+36),('display_entry_SP',1,frame+64),('display_entry_PC',1,frame+68),('guest_return',2,guest_sp),('guest_records_argument',2,guest_sp+4),('guest_output_argument',2,guest_sp+8),('saved_A6',2,gframe),('saved_D2',2,gframe-56),('saved_A2',2,gframe-32),('private_table_base',2,gframe-4),('private_table_cursor',2,gframe-12),('private_field_cursor',2,gframe-16),('stop_record',2,records+(count-1)*36),('output_last_word',2,output_end-4),('display_D0',2,frame+4),('display_D1',2,frame+8),('display_A0',2,frame+36),('display_A1',2,frame+40),('display_D2',2,frame+12),('display_A6',2,frame+60),('display_SP',2,frame+64),('display_PC',2,frame+68),('display_USP',2,frame+72),('display_SSP',2,frame+76),('display_SR',2,frame+81),('display_bus',2,frame),('display_csp_metadata',2,frame+98),('display_activeCPU_metadata',2,frame+102),('display_active',2,frame+117),('display_error',2,frame+97),('rotation_end_A2',3,frame+44),('rotation_end_SP',3,frame+64),('rotation_end_PC',3,frame+68),('rotation_end_SR',3,frame+81),('rotation_service',3,frame+82)]
 for name,index,address in mutations:
  def modify(i,memory,state,index=index,address=address):
   if i==index:memory[address]^=1
  assert not replay(name,modify),name;faults.append(dict(name=name,rejected=True))
 for index,name in enumerate(['missing_rotation_begin','missing_display_begin','missing_display_end','missing_rotation_end']):assert not replay(name,skip=index),name;faults.append(dict(name=name,rejected=True))
 def badstack(i,memory,state):
  if i==2:state.registers[15]=0
 assert not replay('physical_C_stack',badstack);faults.append(dict(name='physical_C_stack',rejected=True))
 save(out/'cases.json',rows);save(out/'faults.json',faults);proof=dict(status='terminal_native_display_rotation_actual_CPU_witnesses_and_faults_pass',directory=str(out),actual_native_scene_lanes=64,native_display_entries=sum(x['display_entries']for x in rows),native_rotation_entries=sum(x['rotation_entries']for x in rows),rejected_fault_controls=len(faults),host_guest_RAM_writes=0,new_predictions=0,new_training=False,source_sha256={str(p):sha(p)for p in [Path(__file__),Path(monitor.__file__),Path(monitor.prior.__file__),ROOT/'scripts/scene_rotation_display_observer_v2.inc.c',ROOT/'scripts/scene_display_observer_v1.inc.c',bp,source,lib,script,out/'cases.json',out/'faults.json',*out.glob('checkpoint-*')]},scope=__doc__+' Four actual native instruction boundaries:rotation begin/display begin/display end/rotation end. Guest frame/table shape, argument/save integrity, full callee saves/banks,finalflags/output commitment and stack/metadata are witnessed. Not a second full packing oracle. Host fault replays mutate copied snapshots only. Remaining services are component fixtures; no fresh-game/IRQ/console claim.');save(out/'review.json',proof);save(V/'scene17-direct-dispatch-commit-observer-v1-current.json',proof);print(proof['status'],proof['native_display_entries'],len(faults),flush=True)
if __name__=='__main__':main()
