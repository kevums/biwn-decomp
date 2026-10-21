"""Read-only new call-site witness on original/native actual68000 scene lanes."""
import ctypes as c,importlib.util,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
import geometry_records_scene_runtime_v1 as support
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha

def main():
 gp=V/'record-loop-matrix-route-watch-qualified-v1-current.json';g=read(gp)
 for p,h in g['source_sha256'].items():assert sha(p)==h,p
 bp=V/'native-record-loop-image-disc-build-v1-current.json';b=read(bp);helper=b['shared_Deck_symbols']['biwn_v4_scene_helper_return']
 out=V/'record-loop-matrix-route-watch-actual-CPU-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 original_source=Path(g['directory'])/'fixture.c';source=out/'fixture.c';source.write_text(original_source.read_text()+'\nvoid snapshot(const void *raw,const struct cpu *cpu){memcpy(memory,raw,sizeof(memory));current=*cpu;}\n');lib=out/'fixture.dylib';q=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(lib)],capture_output=True,text=True);(out/'compiler.log').write_text(q.stdout+q.stderr);assert q.returncode==0,q.stderr
 f=c.CDLL(str(lib));f.snapshot.argtypes=[c.c_void_p,c.c_void_p];f.pc.argtypes=[c.c_uint32];f.stat.argtypes=[c.c_uint];f.stat.restype=c.c_uint64;rows=[];active=False
 def finish():
  nonlocal active
  if not active:return
  x=[f.stat(i)for i in range(7)];assert x[4]==x[5]==0,(len(rows),x)
  assert x[0]==x[2] and x[1]==x[3],x
  rows.append(dict(lane=len(rows),original_entries=x[0],native_entries=x[1],original_returns=x[2],native_returns=x[3],errors=x[4],pending=x[5],ignored_other_calls=x[6]));active=False
 original=support.Runtime
 class Observed(original):
  def __init__(self,*args):
   super().__init__(*args);execute=self.core.m68k_execute
   def step(*args):
    cpu=self.cpu()
    if cpu.pc in [0xe220,0x172c4,helper]:f.snapshot(c.create_string_buffer(self.device.ram()),c.byref(cpu));f.pc(cpu.pc)
    return execute(*args)
   self.core.m68k_execute=step
  def reset(self,*args):
   nonlocal active
   finish();f.clear();active=True;return super().reset(*args)
 support.Runtime=Observed
 path=ROOT/'scripts/check_record_loop_image_whole_scene_disc_v3.py';text=path.read_text().replace('record-loop-image-whole-scene-disc-v3','record-loop-matrix-watch-observed-scenes-v1');anchor='  rows=[];original_snapshot=bytes(snapshot);operand_cache={}';assert text.count(anchor)==1;text=text.replace(anchor,'  vectors=[vectors[i+32*(i%5)]for i in range(64)]\n'+anchor);script=out/'observed-scenes.py';script.write_text(text)
 try:
  spec=importlib.util.spec_from_file_location('matrix_route_observed_scenes',script);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);sys.argv=[str(script)];module.main();finish();assert len(rows)==128 and sum(x['original_entries']for x in rows)>0 and sum(x['native_entries']for x in rows)>0
  save(out/'cases.json',rows);proof=dict(status='terminal_original_native_record_matrix_callsite_actual_CPU_lanes_pass',directory=str(out),CPU_lanes=128,original_record_matrix_calls=sum(x['original_entries']for x in rows),native_record_matrix_calls=sum(x['native_entries']for x in rows),errors=0,pending=0,all32CCR_both_banks=True,observer_guest_RAM_writes=0,new_predictions=0,new_training=False,fresh_gameplay_verified=False,source_sha256={str(p):sha(p)for p in [Path(__file__),gp,bp,original_source,source,lib,path,script,out/'cases.json']},scope='Original170A0 and nativev37scene lanes use inherited native E220/E098providers and controlled/synchronous originalGPU4320fixtures. The new observer only snapshots guest state into hostmemory. Full paired functionalCPU/RAM/MMIOchecks also pass. This is not fresh/asynchronous/IRQ/console proof.');save(out/'review.json',proof);save(V/'record-loop-matrix-route-watch-actual-CPU-v1-current.json',proof);print(proof['status'],128,flush=True)
 finally:support.Runtime=original
if __name__=='__main__':main()
