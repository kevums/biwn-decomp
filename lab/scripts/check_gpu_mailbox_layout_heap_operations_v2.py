"""Validate actual relocated resident heap/copy bytes at the raised boundary."""
import argparse,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
import check_biwn_native_load_scan_bundle_heap as e
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def read(p):return json.loads(Path(p).read_text())
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);args=ap.parse_args();bp=ROOT/'verification/native-gpu-mailbox-disc-build-current.json';build=read(bp);floor=build['heap_start'];payload=Path(build['component']).read_bytes();e.BASE=build['resident_address'];assert floor==0x166b40 and len(payload)==32128
 original=bytearray((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes())
 for a in [0x1521c,0x1526c]:assert original[a:a+4]==(0x15edc0).to_bytes(4,'big');original[a:a+4]=floor.to_bytes(4,'big')
 candidate=bytearray(original);candidate[e.BASE:e.BASE+len(payload)]=payload;stage=Path(build['derived_stage']).read_bytes()
 for entry in [0x15200,0x152a2,0xe3e0,0xe3ee]:
  jump=stage[entry-0x4000:entry-0x4000+6];assert jump[:2]==b'\x4e\xf9'and e.BASE<=int.from_bytes(jump[2:],'big')<e.BASE+len(payload);candidate[entry:entry+6]=jump
 cases=e.vectors(floor);cases=cases[:args.limit]if args.limit else cases;out=ROOT/'verification/gpu-mailbox-layout-heap-operations'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 state=dict(status='running_relocated_heap_operations',directory=str(out),planned=len(cases),completed=0,heap_floor=hex(floor),resident_reserve=len(payload))
 def mark():save(out/'protocol.json',state);save(ROOT/'verification/gpu-mailbox-layout-heap-operations-active.json',state)
 mark();(out/'fixtures.jsonl').write_text(''.join(json.dumps(c,separators=(',',':'))+'\n'for c in cases));rows=[];native=e.sched.Native();coverage=set()
 try:
  for i,case in enumerate(cases):
   left=e.old.Script(original,case);right=e.old.Script(candidate,case)
   ar,ac,pcs,cy,calls,hw,stats=e.native(native,bytes(left.memory),case,len(payload),True);br,bc,newpcs,ncy,newcalls,newhw,newstats=e.native(native,bytes(right.memory),case,len(payload),False)
   if ac!=bc or e.normalize(br,ar,len(payload))!=ar or calls!=newcalls or hw!=newhw:
    save(out/'native-mismatch.json',dict(index=i,case=case,original_CPU=ac,compiled_CPU=bc,original_calls=calls,compiled_calls=newcalls,RAM_differences=[hex(j)for j,(a,b)in enumerate(zip(ar,e.normalize(br,ar,len(payload))))if a!=b][:32]));raise AssertionError('Relocated native heap/copy mismatch')
   assert br[e.BASE:e.BASE+len(payload)]==payload
   at,atr,areg=e.trace(bytes(left.memory),case,len(payload),True);bt,btr,breg=e.trace(bytes(right.memory),case,len(payload),False)
   if at!=bt or e.normalize(btr,atr,len(payload))!=atr or areg!=breg:
    save(out/'ordered-mismatch.json',dict(index=i,case=case,original_trace=at,compiled_trace=bt,original_regs=areg,compiled_regs=breg));raise AssertionError('Relocated ordered heap/copy mismatch')
   assert btr[e.BASE:e.BASE+len(payload)]==payload;coverage.update(pcs);rows.append(dict(index=i,entry=hex(case['entry']),native_CPU=bc,ordered_events=len(at),ordered_trace_sha256=hashlib.sha256(json.dumps(at,separators=(',',':')).encode()).hexdigest(),copy_calls=newcalls,hardware=newhw,original_cycles=cy,native_cycles=ncy,original_device=stats,native_device=newstats))
   if i%128==0:state['completed']=len(rows);mark();print('Relocated heap',len(rows),'/',len(cases),flush=True)
  inputs=[Path(__file__),Path(e.__file__),ROOT/'scripts/check_biwn_memory.py',bp,Path(build['component']),Path(build['derived_stage']),ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'tools/libbiwn-movement-device.dylib',ROOT/'render-assets/biwn-inventory-baseline.bin']
  save(out/'results.json',rows);state.update(status='terminal_relocated_heap_operations_preflight_pass'if args.limit else'terminal_relocated_heap_native_blitter_and_ordered_pass',completed=len(rows),native_cases=len(rows),ordered_cases=len(rows),original_instruction_sites=len(coverage),source_sha256={str(p):sha(p)for p in inputs},scope=__doc__+' Native lanes execute actual copy and pinned emulated blitter; ordered trace lanes prescribe copy effects/returned caller registers/CCR. Original compactors are intentionally patched to the same declared new boundary. Private8KBstack/installedcode/entryJMPexclusions; no arbitraryfault/IRQ/concurrency/fullgame proof.',new_predictions=0)
  mark()
  if not args.limit:save(ROOT/'verification/gpu-mailbox-layout-heap-operations-current.json',state)
  print(json.dumps({k:state[k]for k in ['status','native_cases','ordered_cases','heap_floor']}))
 except BaseException as error:state.update(status='terminal_relocated_heap_operations_failed',error=repr(error),completed=len(rows));mark();raise
 finally:native.close()

if __name__=='__main__':main()
