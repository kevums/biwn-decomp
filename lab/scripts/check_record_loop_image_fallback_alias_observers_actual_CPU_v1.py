"""Observe actual new-scene CPU lanes with exact shared and record witnesses.

Both functional lanes retain the whole-scene comparison's explicit device
fixtures. Observer snapshots copy guest RAM/CPU into host-owned memory only.
No observer writes guest memory,registers,task state or scheduling.
"""
import ctypes as c,importlib.util,sys
from pathlib import Path
from datetime import datetime,timezone
import geometry_records_scene_runtime_v1 as support
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha

def main():
 gp=V/'record-loop-image-commit-observer-qualified-v1-current.json';sp=V/'record-loop-image-shared-observer-qualified-v1-current.json';g=read(gp);s=read(sp)
 for gate in [g,s]:
  for p,h in gate['source_sha256'].items():assert sha(p)==h,p
 out=V/'record-loop-image-fallback-alias-observers-actual-CPU-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 record=c.CDLL(g['fixture_library']);shared=c.CDLL(s['fixture_library'])
 for f in [record,shared]:f.snapshot.argtypes=[c.c_void_p,c.c_void_p];f.pc.argtypes=[c.c_uint32]
 record.stat.argtypes=[c.c_uint];record.stat.restype=c.c_uint64;shared.stat.argtypes=[c.c_uint,c.c_uint];shared.stat.restype=c.c_uint64;rows=[];phase=''
 state=dict(status='checking',directory=str(out),pid=__import__('os').getpid(),CPU_lanes=0,new_predictions=0,new_training=False)
 def mark():save(out/'protocol.json',state)
 def finish():
  values=[dict(errors=shared.stat(0,k),outside=shared.stat(1,k),pending=shared.stat(2,k),entries=shared.stat(3,k),returns=shared.stat(4,k),fallbacks=shared.stat(5,k),attempts=shared.stat(6,k),C_observations=shared.stat(7,k))for k in range(6)]
  if not sum(x['attempts']for x in values):return
  assert all(x['errors']==x['outside']==x['pending']==0 and x['entries']==x['returns']and x['attempts']==x['entries']+x['fallbacks']for x in values),(phase,len(rows),values)
  accepted=sum(x['entries']for x in values);fallbacks=sum(x['fallbacks']for x in values)
  assert (accepted,fallbacks)==((0,1)if phase=='fallback'else(1,1)),(phase,values)
  r=[record.stat(n)for n in range(10)]
  assert r[0]==r[1]==r[9]==0 and r[2]==r[3]and r[5]==r[6]and r[7]==r[8]and r[4]==r[6]+r[8],(phase,len(rows),r)
  rows.append(dict(lane=len(rows),phase=phase,shared=values,records=dict(errors=r[0],pending=r[1],entries=r[2],returns=r[3],protected_provider_returns=r[4],copy_entries=r[5],copy_returns=r[6],matrix_entries=r[7],matrix_returns=r[8],original_body_steps_while_native=r[9])));state['CPU_lanes']=len(rows);save(out/'cases-progress.json',rows);mark();record.clear();shared.clear()
 original=support.Runtime;build=read(V/'native-record-loop-image-disc-build-v1-current.json');symbols=build['shared_Deck_symbols'];code=build['shared_Deck_code_address'];end=code+build['shared_Deck_code_bytes'];helper=symbols['biwn_v4_scene_helper_return'];roots=[0x11828,0x1186a,0x11ad4,0x11b4c,0x11d1a,0x17e0e]
 class Observed(original):
  def __init__(self,*args):
   self.lane_number=0;self.observed_lane=False;super().__init__(*args);self.execute_before_observation=self.core.m68k_execute
   def step(*args):
    if self.observed_lane:
     cpu=self.cpu();pc=cpu.pc
     if code<=pc<end or pc in [0xe3e0,0xe220]or any(a<=pc<a+1024 for a in roots):
      # Direct stable core RAM pointer avoids a Python copy; snapshots remain
      # owned by the host-only fixture and cannot repair the running core.
      for f in [shared,record]:f.snapshot(self.device.pointer,c.byref(cpu));f.pc(pc)
    return self.execute_before_observation(*args)
   self.core.m68k_execute=step
  def reset(self,*args):
   finish();record.clear();shared.clear();self.lane_number+=1;self.observed_lane=self.lane_number%2==0;return super().reset(*args)
  def close(self):
   finish();self.core.m68k_execute=self.execute_before_observation;return super().close()
 support.Runtime=Observed;record.clear();shared.clear();mark()
 scripts=[];sources=[]
 try:
  for phase,source_name,family in [('fallback','check_record_loop_image_final_fallback_v1.py','record-loop-image-final-fallback-v1'),('alias','check_record_loop_image_alias_reentry_v1.py','record-loop-image-alias-reentry-v1')]:
   support.Runtime=Observed;support.base.queue.SCRIPTS.clear();source=ROOT/'scripts'/source_name;text=source.read_text().replace(family,'record-loop-image-observed-'+phase+'-v1');script=out/(phase+'-harness.py');script.write_text(text);scripts.append(script);sources.append(source)
   spec=importlib.util.spec_from_file_location('observed_records_'+phase,script);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);sys.argv=[str(script)];module.main();finish();record.clear();shared.clear()
  assert len(rows)==704 and sum(x['phase']=='fallback'for x in rows)==384 and sum(x['phase']=='alias'for x in rows)==320
  save(out/'cases.json',rows);state.update(status='terminal_shared_and_record_observers_actual_fallback_and_alias_CPU_pass',CPU_lanes=704,fallback_CPU_lanes=384,alias_CPU_lanes=320,prior_body_CPU_lanes=64,total_reviewed_witness_CPU_lanes=768,record_calls=sum(x['records']['entries']for x in rows),copy_calls=sum(x['records']['copy_entries']for x in rows),matrix_calls=sum(x['records']['matrix_entries']for x in rows),observer_guest_RAM_writes=0,observer_CPU_writes=0,source_sha256={str(p):sha(p)for p in [Path(__file__),V/'record-loop-image-record-observer-actual-CPU-v1-current.json',gp,sp,Path(g['fixture_library']),Path(s['fixture_library']),*scripts,*sources,out/'cases.json']},scope=__doc__+'384actualinvalid/busyfallbacks and320actualinjectedscene-self/cross-rootJSRlanes. UnderlyingCPU/nonprivateRAM/helperrecordcomparisons also pass. E3E0 and input/face provider effects in nested fixtures are declared ABI adversaries;not GPUfidelity,natural nesting or arbitraryIRQ. Together with prior frozen64bodylanes,this qualifies768actualCPUlanes without replaying those64.');mark();save(V/'record-loop-image-fallback-alias-observers-actual-CPU-v1-current.json',state);print(state['status'],704,flush=True)
 except BaseException as error:state.update(status='terminal_failed',error=repr(error));mark();raise
 finally:support.Runtime=original
if __name__=='__main__':main()
