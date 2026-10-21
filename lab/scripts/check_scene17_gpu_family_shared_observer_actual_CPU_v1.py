"""Exact new shared monitor over actual compiled scene/invalid/busy/reentry lanes.
Copies CPU/RAM into a host observer;never mutates guest state for observation.
Underlying harnesses retain declared helper/busy-read fixtures.
"""
import ctypes as c,importlib.util,sys
from pathlib import Path
from datetime import datetime,timezone
import scene_gpu_family_scene_runtime_v2 as support
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha

def main():
 gp=V/'scene17-gpu-family-shared-observer-qualified-v1-current.json';g=read(gp)
 for p,h in g['source_sha256'].items():assert sha(p)==h,p
 out=V/'scene17-gpu-family-shared-observer-actual-CPU-v2'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);f=c.CDLL(g['fixture_library']);f.snapshot.argtypes=[c.c_void_p,c.c_void_p];f.pc.argtypes=[c.c_uint32];f.stat.argtypes=[c.c_uint,c.c_uint];f.stat.restype=c.c_uint64;rows=[];phase=''
 def finish():
  attempts=f.stat(6,5)
  if not attempts:return
  values=dict(errors=f.stat(0,5),outside=f.stat(1,5),pending=f.stat(2,5),accepted=f.stat(3,5),returns=f.stat(4,5),fallbacks=f.stat(5,5),attempts=attempts,C_observations=f.stat(7,5))
  assert values['errors']==values['outside']==values['pending']==0,(phase,len(rows),values)
  assert values['accepted']==values['returns']and values['attempts']==values['accepted']+values['fallbacks']
  rows.append(dict(phase=phase,**values));save(out/'cases-progress.json',rows);f.clear()
 original=support.Runtime
 class Observed(original):
  in_reference=False
  def reset(self,*args):
   finish();f.clear();return super().reset(*args)
  def native(self,*args):
   self.in_reference=True
   try:return super().native(*args)
   finally:self.in_reference=False;f.clear()
  def __init__(self,*args):
   super().__init__(*args);self.execute_before_observation=self.core.m68k_execute
   def step(*args):
    if not self.in_reference:
     state=super(Observed,self).cpu();raw=self.device.ram();f.snapshot(c.create_string_buffer(raw),c.byref(state));f.pc(state.pc)
    return self.execute_before_observation(*args)
   self.core.m68k_execute=step
  def close(self):
   finish();self.core.m68k_execute=self.execute_before_observation;return super().close()
 support.Runtime=Observed;f.clear();scripts=[]
 try:
  for tag,source_name,limit in [('body','check_scene17_gpu_family_final_bridge_v1.py',64),('fallback','check_scene17_gpu_family_final_fallback_v1.py',None),('reentry','check_scene17_gpu_family_final_reentry_v1.py',None)]:
   phase=tag;source=ROOT/'scripts'/source_name;text=source.read_text();oldfamily={'body':'scene17-gpu-family-final-bridge-v1','fallback':'scene17-gpu-family-final-fallback-v1','reentry':'scene17-gpu-family-final-reentry-v1'}[tag];text=text.replace("out=V/'"+oldfamily+"'","out=V/'scene17-gpu-family-observed-"+tag+"-v1'")
   # Bridge uses the same family for both directory and optional current pointer.
   if tag=='body':text=text.replace("V/'scene17-gpu-family-final-bridge-v1-current.json',state","V/'scene17-gpu-family-observed-body-v1-current.json',state")
   else:text=text.replace("save(V/'"+oldfamily+"-current.json',state)","save(V/'scene17-gpu-family-observed-"+tag+"-v1-current.json',state)")
   path=out/(tag+'-harness.py');path.write_text(text);scripts+=[path];spec=importlib.util.spec_from_file_location('scene_observed_'+tag,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);sys.argv=[str(path)]+(['--limit',str(limit)]if limit else[]);m.main();finish();f.clear()
 finally:support.Runtime=original
 counts={tag:sum(x['phase']==tag for x in rows)for tag in ['body','fallback','reentry']};assert counts==dict(body=64,fallback=384,reentry=64),counts
 assert all(x['accepted']==1 and x['fallbacks']==0 and x['C_observations']>0 for x in rows if x['phase']=='body')
 assert all(x['accepted']==0 and x['fallbacks']==1 for x in rows if x['phase']=='fallback')
 assert all(x['accepted']==1 and x['fallbacks']==1 and x['attempts']==2 for x in rows if x['phase']=='reentry')
 save(out/'cases.json',rows);proof=dict(status='terminal_six_root_shared_monitor_actual_scene_fallback_reentry_lanes_pass',directory=str(out),CPU_lanes=len(rows),counts=counts,all_observer_error_pending_outside_zero=True,host_guest_RAM_writes=0,new_predictions=0,new_training=False,source_sha256={str(p):sha(p)for p in [Path(__file__),gp,Path(g['fixture_library']),*scripts,out/'cases.json']},scope=__doc__+'64nativebodycases,384actualinvalid/busyfallbacks,64actualinjectednestedJSRcases. FullunderlyingCPU/RAM/helperentrycomparisonsalsopass. Native-entryattemptsseparatefromacceptedbodyentries;no monitorstateRAM/CPUrepair. Notfreshgameplay/naturalIRQ.');save(out/'review.json',proof);save(V/'scene17-gpu-family-shared-observer-actual-CPU-v2-current.json',proof);print(proof['status'],counts,flush=True)
if __name__=='__main__':main()
