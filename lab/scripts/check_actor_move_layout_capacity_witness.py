"""Fresh relocated heap init followed by boundary-size allocation requests."""
import json,random
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_native_load_scan_bundle_heap as e
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def read(p):return json.loads(Path(p).read_text())
def main():
 bp=ROOT/'verification/actor-move-layout-materialized-current.json';b=read(bp);baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();stage=Path(b['derived_stage']).read_bytes();payload=Path(b['component']).read_bytes();e.BASE=b['resident_address'];image=bytearray(baseline);image[0x4000:0x100000]=stage;image[e.BASE:e.BASE+len(payload)]=payload;image[e.SP:e.SP+4]=e.STOP.to_bytes(4,'big');n=e.sched.Native();rng=random.Random(0x165d4036);rows=[]
 try:
  n.device.seed(bytes(image),0);lib=n.lib;lib.m68k_pulse_reset();lib.m68k_set_irq(0);lib.m68k_set_reg(17,0x2000);lib.m68k_set_reg(15,e.SP);lib.m68k_set_reg(16,0x1557a)
  for _ in range(10000):
   pc=lib.m68k_get_reg(None,16)
   if pc==e.STOP:break
   assert pc==0x1557a or e.BASE<=pc<e.BASE+len(payload);lib.m68k_execute(1)
  else:raise AssertionError('Actual constructor did not return')
  fresh=bytearray(n.device.ram());capacity=0x1c0000-b['heap_start'];assert int.from_bytes(fresh[0x112d64:0x112d68],'big')==capacity==369344
  original=bytearray(fresh)
  for lo,hi in [(0x15200,0x1545c),(0xe3e0,0xe4aa)]:original[lo:hi]=baseline[lo:hi]
  for a in [0x1521c,0x1526c]:original[a:a+4]=b['heap_start'].to_bytes(4,'big')
  candidate=bytearray(original)
  for a in [0x15200,0x152a2,0xe3e0,0xe3ee]:candidate[a:a+6]=stage[a-0x4000:a-0x4000+6]
  requests=[0,1,1024,capacity-16,capacity-8,capacity-7,capacity-1,capacity,capacity+1]
  for requested in requests:
   for mode in [0,0x2000]:
    for flags in [0,31]:
     case=dict(entry=0x152a2,params=[requested],incoming=[rng.getrandbits(32)for _ in range(15)],sr=mode|flags,initial=[[e.SP,4,e.STOP],[e.SP+4,4,requested]],helper_D0=0,helper_registers=[0,0,0],helper_CCR=flags,default_helper_return=0,read_queues=[])
     a=e.old.Script(original,case);bscript=e.old.Script(candidate,case);left,lc,_,_,calls,hw,_=e.native(n,bytes(a.memory),case,len(payload),True);right,rc,_,_,ncalls,nhw,_=e.native(n,bytes(bscript.memory),case,len(payload),False)
     assert lc==rc and e.normalize(right,left,len(payload))==left and calls==ncalls and hw==nhw
     at,ar,areg=e.trace(bytes(a.memory),case,len(payload),True);bt,br,breg=e.trace(bytes(bscript.memory),case,len(payload),False);assert at==bt and e.normalize(br,ar,len(payload))==ar and areg==breg
     assert right[e.BASE:e.BASE+len(payload)]==payload;rows.append(dict(requested=requested,mode=mode,flags=flags,D0=rc['registers'][0],available_after=int.from_bytes(right[0x112d64:0x112d68],'big'),ordered_events=len(at)))
  out=ROOT/'verification/actor-move-layout-capacity-witness'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);save(out/'cases.json',rows);state=dict(status='terminal_actual_heap_initialize_then_capacity_requests_pass',directory=str(out),cases=len(rows),initial_capacity=capacity,requests=requests,source_sha256={str(p):sha(p)for p in [Path(__file__),Path(e.__file__),bp,Path(b['derived_stage']),Path(b['component']),ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'tools/libbiwn-movement-device.dylib']},scope=__doc__+' Each request starts from actual native-constructor RAM. Exact fullCPU/banks/publicRAM/nativecopy-blitter plus prescribed-copy ordered trace compare to original memory routines at same declared floor. Not arbitrary allocation sequence/resource or whole-game coverage.',new_predictions=0);save(out/'protocol.json',state);save(ROOT/'verification/actor-move-layout-capacity-witness-current.json',state);print(state['status'],len(rows))
 finally:n.close()

if __name__=='__main__':main()
