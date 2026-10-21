"""Review four native navigation roots, expanded layout, and rejected local proposals.
Actual full gameplay is a separate gate. Do not transfer older route proofs.
"""
import json,hashlib,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
import capstone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def main():
 out=V/'native-navigation-component-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();deps={}
 def bind(p,h=None):
  p=Path(p).resolve();actual=sha(p);assert h is None or actual==h,str(p)
  if p.name.endswith(('-current.json','-active.json')):
   dest=snap/(hashlib.sha256(str(p).encode()).hexdigest()[:12]+'-'+p.name);shutil.copy2(p,dest);p=dest
  assert str(p)not in deps or deps[str(p)]==actual,str(p);deps[str(p)]=actual
 names=['native-actor-navigation-current.json','native-actor-navigation-final-current.json','native-actor-navigation-build-normalized-current.json','actor-navigation-layout-startup-heap-initialize-current.json','actor-navigation-layout-heap-operations-current.json','actor-navigation-layout-capacity-witness-current.json','actor-navigation-live-observer-current.json','navigation-native-Author-current.json','navigation-native-Author-machine-reviewed-current.json','navigation-native-Author-repair-current.json','navigation-native-Author-repair-machine-reviewed-current.json']
 objects={}
 for name in names:
  obj=read(V/name);objects[name]=obj;bind(V/name)
  for p,h in obj.get('source_sha256',{}).items():bind(p,h)
 a,b,build,startup,heap,capacity,monitor,author,review,repair,repair_review=[objects[x]for x in names]
 assert a['cases']==b['cases']==6144 and a['per_root_cases']==b['per_root_cases']and a['binary_bytes']==b['binary_bytes']==1428
 data=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();decoder=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000)
 ranges=[(0xf368,0xf4d8),(0x13f12,0x13f3e),(0x13f48,0x13f7c),(0x13f7c,0x13fac),(0x13fb6,0x13fea),(0x13fea,0x1400e),(0x14018,0x1404c)];sites={i.address for lo,hi in ranges for i in decoder.disasm(data[lo:hi],lo)}
 assert len(sites)==209 and sites==set(a['original_sites'])==set(b['original_sites'])
 assert build['linked_component_bytes']==29876 and build['component_bytes']==30080 and build['free_reserved_bytes']==204 and build['heap_start']==0x166340 and build['staging_address']==0xf6c00 and build['staging_bytes_cleared']==0x7600
 assert startup['startup_cases']==96 and startup['heap_initialize_cases']==192 and startup['initial_heap_bytes']==367808
 assert heap['native_cases']==heap['ordered_cases']==3392 and capacity['cases']==36 and capacity['initial_capacity']==367808
 assert monitor['completed']==440 and monitor['cases']==220 and len(monitor['negative_controls'])==4 and all(x['rejected']and not x['native_CPU_or_RAM_changed']for x in monitor['negative_controls'])
 assert author['new_predictions']==repair['new_predictions']==1 and review['compiler_pass']and review['completed']==0 and not review['adopted']and not repair_review['compiler_pass']and not repair_review['adopted']
 for obj in [author,repair]:
  folder=Path(obj['directory'])
  for filename in ['request.json','response.json','response.txt','candidate.c','prompts-and-responses.txt']:bind(folder/filename)
 for obj in [a,b,monitor,author,repair]:
  if obj.get('pid'):
   result=subprocess.run(['ps','-p',str(obj['pid']),'-o','command='],capture_output=True,text=True)
   assert result.returncode!=0 or not any(x in result.stdout for x in ['check_native_actor_navigation','qualify_native_actor_navigation_observer','run_navigation_native_author']),obj['pid']
 text='''BIWN — FOUR NATIVE NAVIGATION ROOTS / LOCAL MODEL OUTPUT TEST

The existing portable C logic for F368 waypoint and13F12/13F7C/13FEA navigation
now has original-facing native68000 shims. Prototype and final-address matrices
pass6144cases each(1536/root),all209 original instruction sites. Complete returned
CPU/SR/banks,public2MBRAM and ordered public data access match original execution.
No prescribed helpers are needed. Private frames,installation bytes/return PCs
are excluded. Valid stored jump-table targets only; faults/alteredtargets/IRQ/
concurrency/timing are unproved. Max observed finite private depth180.

New development image:29876resident bytes/30080reserved/free204,heap166340,
initialcapacity367808. Heap boundary rises1536bytes; staging moves1024bytes earlier
toF6C00,clear30208endsFE200. The original staging window is zero; exact startup
96cases and192heapinitialize cases pass.3392 native-blitter plus3392 ordered
heap/copy cases and36 actual-constructor capacity requests pass at the declared
new floor. Atari trailer including94 nonzero bytes atFE520 is preserved. Parent
and original CDI hashes unchanged;28354changed CDI bytes all within declared
loader/staging/fourroot intervals. Runtime use and actual route remain separate.

The exact read-only navigation observer passes440original/native executions across
220stratified cases and rejects4 decodedCPU/mirror negatives without changing
native state. It checks entry/body ownership,callee/SP/args/return,72byte context
entry/return and task stack boundaries. Full algorithm equivalence is the separate
6144case matrix. No false claim of independent C-algorithm validation from matching
physical CPU to the same C context. Four new original-facing native roots,not four
newly discovered portable algorithms. Coordinator source; no local source adopted.

LOCAL OUTPUT TEST — TWO ACTUAL PREDICTIONS, NO NEW WEIGHTS
Daily advertising-scholar base weights through local LM Studio,reasoningoff,temp0.
Author775completion tokens/34.81seconds:complete13F12source compiled after only
removing Markdown fence,then failed first original-valid fixture. Original native
CPU replay returnsD0=1,D1=7,A0=120000 and4orderedpublicreads; candidate returnsD0=0,
wrongD1/A0,no publicreads. Incorrect incoming register arguments; no repair adopted.
One informed repair received the exact disassembly/header/counterexample,not goldC.
It returned148.34seconds and reached its3200token budget mid-function; strict
compiler rejects incomplete C. It also visibly defines wrong CCR masks. This is
retained evidence that local code generation remains unreliable,not a quality
improvement. No same-weight independent Reviewer claim. Native Chat display is
unverified; these are real local API generations with saved prompts/responses.

The latest reviewed gameplay publication remains28448bytes until the new expanded
image completes fresh route/control review. Full readable game/sameconsole release,
Advertising research/teaching reliability,nativeChat and complete future-machine
migration remain unfinished.
'''
 report=out/'review.txt';report.write_text(text);bind(report);bind(Path(__file__))
 result=dict(status='terminal_four_native_navigation_roots_and_layout_reviewed_gameplay_separate',directory=str(out),report=str(report),resident_bytes=29876,reserved_bytes=30080,prototype_cases=6144,final_cases=6144,original_instruction_sites=209,root_count=4,max_private_depth=180,startup_cases=96,heap_initialize_cases=192,heap_native_cases=3392,heap_ordered_cases=3392,capacity_cases=36,monitor_executions=440,monitor_cases=220,monitor_negative_controls=4,new_predictions=2,new_training=False,new_local_code_adopted=False,native_Chat_verified=False,gameplay_reviewed=False,default_promoted=False,whole_game_complete=False,dependencies_sha256=deps,scope=__doc__);save(out/'protocol.json',result);save(V/'native-navigation-component-reviewed-current.json',result);print(json.dumps(dict(status=result['status'],resident_bytes=29876,bound_files=len(deps))))
if __name__=='__main__':main()
