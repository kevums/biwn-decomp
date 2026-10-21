"""Actual pinned-CPU stack/CLR bus events versus unchanged portable C.
Four selected scene cases;recorder has no width field. Full expanded-Unicorn
width/order matrix is separate. This is not target C machine-code execution.
"""
import ctypes as c
from datetime import datetime,timezone
from pathlib import Path
import scene17_host_runtime_v1 as support
from check_native_scene_reset_core_bus_v1 import Event
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha
base=support.base
def main():
 prior=V/'scene17-structured-host-v1/20261020T230553.352177Z';guard=read(V/'scene17-structured-guards-v1-current.json');assert guard['completed_matrix_cases']==1024 and guard['guard_cases']==33
 for p,h in guard['source_sha256'].items():assert sha(p)==h,p
 session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);mapping=read(session/'scene-draw-fullCPU-generation.json');snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();runtime=support.Runtime(prior/'libscene-draw-cpu.dylib',mapping['instructions_decoded']);core=runtime.core
 core.vjtrace_ring_head.restype=c.c_uint64;core.vjtrace_ring_read.argtypes=[c.c_uint64,c.POINTER(Event)];core.vjtrace_ring_read.restype=c.c_int;core.vjtrace_watch_add.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32];core.vjtrace_watch_add.restype=c.c_int
 out=V/'scene17-actual-CLR-bus-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);rows=[];CLR_sites=set()
 def watched(a):return base.SP-128<=a<base.SP+4 or 0x49b88<=a<0x49b8c
 try:
  for i,case in enumerate(base.cases()):
   if i not in [257,258,259,267]:continue
   ram=base.fixture(snapshot,case);core.vjtrace_disarm();core.vjtrace_watch_clear()
   for low,high in [(base.SP-128,base.SP+3),(0x49b88,0x49b8b)]:assert core.vjtrace_watch_add(low,high,3)>=0
   begin=core.vjtrace_ring_head();core.vjtrace_arm();left,cpu,original=runtime.native(ram,case,set());core.vjtrace_disarm();end=core.vjtrace_ring_head();events=[]
   for n in range(begin,end):
    e=Event();assert core.vjtrace_ring_read(n,c.byref(e))
    if e.type in [11,12]and e.who==6 and watched(e.addr):
     events.append(dict(kind='r'if e.type==11 else'w',address=e.addr,value=e.value,PC=hex(e.pc)))
     if e.type==11 and e.pc in [0x17e1e,0x17e2c,0x17f02]:CLR_sites.add(e.pc)
   right,actual,rebuilt=runtime.translated(ram,case);assert rebuilt['status']==0 and not rebuilt['errors']and bytes(cpu)==bytes(actual)and left==right
   native=[(e['kind'],e['address'],e['value'])for e in events];portable=[(kind,address,value)for kind,address,width,value in rebuilt['trace']if watched(address)]
   save(out/f'case-{i}.json',dict(native=events,portable=portable))
   assert native==portable,(i,native,portable);rows.append(dict(case=i,watched_events=len(native),CPU_RAM_and_order_match=True))
 finally:core.vjtrace_disarm();runtime.close()
 assert len(rows)==4 and CLR_sites=={0x17e1e,0x17e2c,0x17f02},CLR_sites
 save(out/'cases.json',rows);paths=[Path(__file__),V/'scene17-structured-guards-v1-current.json',prior/'libscene-draw-cpu.dylib',*out.glob('case-*.json'),out/'cases.json'];d=dict(status='terminal_scene17_four_actual_CPU_stack_CLR_traces_match',directory=str(out),completed=4,original_CLR_sites=[hex(a)for a in sorted(CLR_sites)],target_C_machine_code_executed=False,new_predictions=0,new_training=False,scope=__doc__+' Watches gueststack128bytes plus49B88global;all3original memoryCLRsites witnessed. CPUtrace WHO6only;other MMIO/device effects excluded from this recorder comparison. No IRQ/physicalconsole proof.',source_sha256={str(p):sha(p)for p in paths});save(out/'review.json',d);save(V/'scene17-actual-CLR-bus-v1-current.json',d);print(d['status'])
if __name__=='__main__':main()
