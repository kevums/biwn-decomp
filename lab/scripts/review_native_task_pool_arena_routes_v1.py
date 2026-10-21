"""Review the fresh composed initializer/GPU-arena candidate and same-layout control."""
import hashlib,json,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def prefix_sha(p,n):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  while n:
   block=f.read(min(n,1048576));assert block;h.update(block);n-=len(block)
 return h.hexdigest()
def main():
 out=V/'native-task-pool-arena-review-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();deps={}
 def bind(path,expected=None):
  path=Path(path).resolve();actual=sha(path)
  if expected is not None:assert actual==expected,(str(path),expected,actual)
  if path.name.endswith(('-current.json','-active.json'))or not path.is_relative_to(ROOT):
   target=snap/(hashlib.sha256(str(path).encode()).hexdigest()[:12]+'-'+path.name[-140:]);shutil.copy2(path,target);path=target
  assert str(path)not in deps or deps[str(path)]==actual;deps[str(path)]=actual
 records={}
 for name in ['task-pool-arena-final-current.json','native-task-pool-arena-disc-build-current.json','task-pool-arena-layout-startup-heap-initialize-current.json','task-pool-arena-layout-heap-operations-current.json','task-pool-arena-layout-capacity-witness-current.json','task-arena-mailbox-live-observer-current.json','task-pool-arena-observer-current.json','native-task-pool-current.json','native-task-pool-negatives-current.json','task-pool-create-composition-current.json','task-pool-Author-current.json','task-pool-Repair-current.json']:
  data=read(V/name);records[name]=data;bind(V/name)
  for p,h in data.get('source_sha256',{}).items():bind(p,h)
 b=records['native-task-pool-arena-disc-build-current.json'];g=records['task-pool-arena-final-current.json'];assert b['linked_component_bytes']==g['resident_code_bytes']==32980 and b['component_bytes']==g['reservation_bytes']==59200 and b['reserved_arena_bytes']==26112
 assert g['pool_cases']==512 and g['GPU_cases']==2512 and g['max_original_GPU_stack_bytes']==10 and g['max_GPU_arena_stack_bytes']==204
 assert records['task-pool-arena-layout-startup-heap-initialize-current.json']['startup_cases']==96 and records['task-pool-arena-layout-startup-heap-initialize-current.json']['heap_initialize_cases']==192
 assert records['task-pool-arena-layout-heap-operations-current.json']['native_cases']==3392 and records['task-pool-arena-layout-capacity-witness-current.json']['cases']==36 and records['task-pool-arena-layout-capacity-witness-current.json']['initial_capacity']==338688
 parent=read(b['parent_build']);prefix=bytearray(Path(parent['linked_component']).read_bytes());prefix.extend(bytes((-len(prefix))%4))
 for row in g['layout_relocations']:
  at=int(row['resident_address'],16)-b['resident_address'];old=bytes.fromhex(row['old']);assert prefix[at:at+len(old)]==old;prefix[at:at+len(old)]=bytes.fromhex(row['new'])
 prefix.extend(Path(g['pool_binary']).read_bytes());prefix.extend(bytes((-len(prefix))%4));prefix.extend(Path(g['GPU_binary']).read_bytes());assert bytes(prefix)==Path(b['linked_component']).read_bytes()
 full=Path(b['component']).read_bytes();assert full[:len(prefix)]==prefix
 for slot in range(102):
  at=b['arena_address']-b['resident_address']+slot*256;assert full[at:at+16]==full[at+240:at+256]==bytes([0xa5])*16 and not any(full[at+16:at+240])
 pending=['acquire_pending','table_pending','leaf_pending','geometry_pending','select_pending','scan_pending','door_pending','interior_pending','ad_pending','ai_pending','sc_pending','ach_pending','an_pending','dir_pending','mb_pending','pool_pending'];jobs={};reports={}
 for label in ['candidate','control']:
  p=V/('native-task-pool-arena-v1-quiescent-'+label+'-current.json');job=read(p);assert job['status']=='terminal_native_task_pool_arena_route_pending_review' and job['exit_code']==0 and job['returned_outdoors'] and job['live_monitor_pass'] and job['pool_monitor_pass'] and job['arena_monitor_pass'];bind(p)
  assert subprocess.run(['ps','-p',str(job['child_pid']),'-o','command='],capture_output=True).returncode!=0
  for p,h in job['source_sha256'].items():bind(p,h)
  folder=Path(job['directory'])/'candidate';report=read(folder/'report.json');assert sha(folder/'report.json')==job['report_sha256'];assert not report['captured_state_input'] and not report['host_CPU_or_GPU_register_seed'] and report['C_CPU_backend']['mode']=='reference' and job['checkpoint_restores']==job['host_guest_RAM_writes']==0
  o=job['observations'];assert all(o[k]==0 for k in pending) and o['mb_entries']==o['mb_returns'] and all(n>0 for n in o['mb_returns']);assert o['mb_helpers']==2*sum(o['mb_returns']) and all(o[k]==0 for k in ['mb_errors','mb_context_errors','mb_stack_outside','ad_context_collisions','sc_context_corruptions','pool_errors','arena_errors'])
  assert o['pool_entries']==o['pool_returns']==1
  if label=='candidate':assert o['mb_native']==o['mb_entries'] and o['mb_old_steps']==0 and o['mb_context_entries']==o['mb_context_returns']==sum(o['mb_entries']) and o['pool_native_entries']==1 and o['pool_old_steps']==0 and o['mb_max_depth']==10 and 0<o['arena_max_depth']<=224 and o['arena_used_slots'] and o['arena_unused_checks']==102-len(o['arena_used_slots']) and report['disc_sha256']==b['derived_disc_sha256']
  else:assert o['mb_native']==[0,0] and o['mb_source_steps']==0 and o['mb_old_steps']>0 and o['pool_native_entries']==0 and o['pool_source_steps']==0 and o['pool_old_steps']>0 and o['arena_used_slots']==[] and o['arena_unused_checks']==102 and job['control_delta']['restored_entries']==['dd40','e220','e2b8'] and job['control_delta']['declared_bytes']==20 and report['disc_sha256']==job['control_delta']['control_sha256']
  for name in ['report.json','gameplay-observation.json','frontend-PCM.s16le','original-emulator-final-frame.png','source-derived-current-room-exit-plan.json']:bind(folder/name)
  jobs[label]=job;reports[label]=report
 keys=['CPU_full','full_RAM_sha256','full_GPU_state_sha256','full_DSP_state_sha256','video_sha256','navigation','locomotion_state','held_buttons'];comparison=dict(candidate_frames=jobs['candidate']['frames'],control_frames=jobs['control']['frames'],aligned_frames=min(x['frames']for x in jobs.values()),differing_frames={k:sum(a[k]!=b[k]for a,b in zip(reports['candidate']['frames'],reports['control']['frames']))for k in keys},PCM={label:dict(bytes=(p:=Path(job['directory'])/'candidate/frontend-PCM.s16le').stat().st_size,sha256=sha(p))for label,job in jobs.items()},adaptive_controller_paths_may_differ=True,whole_state_equivalent=False,timing_differences_unresolved=True)
 common=min(x['bytes']for x in comparison['PCM'].values());comparison.update(PCM_equal=comparison['PCM']['candidate']==comparison['PCM']['control'],PCM_common_prefix_bytes=common,PCM_common_prefix_equal=len({prefix_sha(Path(job['directory'])/'candidate/frontend-PCM.s16le',common)for job in jobs.values()})==1);save(out/'fresh-pair-comparison.json',comparison);bind(out/'fresh-pair-comparison.json')
 o=jobs['candidate']['observations'];coverage=dict(pool_initializations=o['pool_returns'],candidate_GPU_returns=o['mb_returns'],control_original_GPU_returns=jobs['control']['observations']['mb_returns'],helper_entries=o['mb_helpers'],original_stack_bytes=o['mb_max_depth'],arena_max_stack_bytes=o['arena_max_depth'],arena_usable_bytes=224,arena_minimum_headroom=224-o['arena_max_depth'],arena_used_slots=o['arena_used_slots'],other_arenas_unchanged=o['arena_unused_checks'],guard_checks=o['arena_guard_checks'],dispatcher_context_minimum_clearance=o['ad_min_context_clearance'],direction_returns=o['dir_returns'],movement_returns=o['ach_returns'],navigation_returns=o['an_returns'],dispatcher_returns=o['ad_returns'],sprite_returns=o['sc_returns'],all_pending_zero=True,all_monitors_pass=True)
 report=out/'review.txt';report.write_text('BIWN TASK INITIALIZER AND PER-TASK GPU STACKS\n\nComplete DD40 initializer uses a local informed repair with one coordinator uint16_t wrap cast. Both unchanged local initializer proposals failed before correction. GPU C is the unchanged fresh one-clickv2 repair previously rejected under the old stack ABI. Supplied source-owned supervisor transition, flags, and per-task arena ABI are coordinator work. This proves a backend fix, not a model weight gain.\n\n32980 code bytes retain the prior prefix, including the now superseded GPU bridge, and append406initializer/812GPU bytes with alignment. Separately reserved26112arena-data bytes (102slots of256,16byte guards each end) are not code or decompiled bytes. Total59200reservation; heap16D500 leaves338688initial bytes. StagingEFA40..FE200; trailer unchanged; original CDI untouched. No default preview promotion.\n\nFinal512initializer and2512GPU CPU/SR/bank/RAM/ordered effects cases pass. Arena tests cover101source-proved task IDs and boot fallback; immediate and ancestor contexts retained. Live pool oracle qualified1024original/native replays and6decoded negatives; ownership1016boundary cases and3guard/unused/code negatives. GPU observer qualified458original/native replays and5controls. New96startup/192heapinitialize/3392heapoperations/36capacity checks pass.\n\n'+json.dumps(dict(coverage=coverage,comparison=comparison),indent=2)+'\n\nBoth fresh routes use ordinary inputs with retained emulator processors/platform/HLE, no state restore or guest RAM/register seed. Same-layout control restores20entry bytes across DD40/E220/E2B8. Fresh pair comparison above is authoritative; raw runner comparisons use an older reference. No whole-state/timing/hardware equivalence, complete-game source rebuild, overall audio equivalence or speedup claim. Native LM Studio Chat display, Advertising reliability and latest portable workflow verification remain unfinished.\n');bind(report);bind(Path(__file__))
 state=dict(status='terminal_native_task_pool_arena_fresh_routes_reviewed',directory=str(out),report=str(report),resident_code_bytes=32980,reservation_bytes=59200,reserved_arena_bytes=26112,initial_heap_bytes=338688,heap_start=b['heap_start'],staging_address=b['staging_address'],coverage=coverage,comparison=comparison,live_monitor_pass=True,new_local_GPU_C_body_adopted=True,initializer_hybrid_adopted=True,new_training=False,new_predictions=0,default_preview_promoted=False,whole_game_complete=False,physical_console_verified=False,dependencies_sha256=deps,scope=__doc__);save(out/'protocol.json',state);save(V/'native-task-pool-arena-integration-reviewed-current.json',state);print({k:state[k]for k in ['status','resident_code_bytes','coverage','comparison']})
if __name__=='__main__':main()
