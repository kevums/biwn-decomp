"""Review final fresh routes; retain failed immediate-only bridge and its cause."""
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
   b=f.read(min(n,1048576));assert b;h.update(b);n-=len(b)
 return h.hexdigest()
def main():
 out=V/'native-gpu-mailbox-v3-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();deps={};old_snapshots={}
 for p in(V/'gpu-mailbox-bridge-v1-rejected').glob('*/snapshots.json'):
  for origin,item in read(p).items():old_snapshots[(origin,item['sha256'])]=item['snapshot']
 historical={}
 for pattern in ['builds/BIWN-native-gpu-mailbox*/20*/protocol.json','verification/gpu-mailbox-layout-*/*/protocol.json','verification/gpu-mailbox-live-observer-*/*/protocol.json']:
  for p in ROOT.glob(pattern):historical[sha(p)]=p
 def bind(p,h=None):
  p=Path(p).resolve();actual=sha(p)
  if h is not None and actual!=h:
   replacement=old_snapshots.get((str(p),h))or historical.get(h);assert replacement,('No as-run snapshot',str(p),h,actual);p=Path(replacement);actual=sha(p);assert actual==h
  if p.name.endswith(('-current.json','-active.json'))or not p.is_relative_to(ROOT):
   target=snap/(hashlib.sha256(str(p).encode()).hexdigest()[:12]+'-'+p.name[-140:]);shutil.copy2(p,target);p=target
  assert str(p)not in deps or deps[str(p)]==actual;deps[str(p)]=actual
 names=['native-gpu-mailbox-current.json','native-gpu-mailbox-contexts-negatives-current.json','native-gpu-mailbox-final-current.json','native-gpu-mailbox-disc-build-current.json','gpu-mailbox-layout-startup-heap-initialize-current.json','gpu-mailbox-layout-heap-operations-current.json','gpu-mailbox-layout-capacity-witness-current.json','gpu-mailbox-live-observer-current.json','gpu-mailbox-native-Author-current.json','gpu-mailbox-native-Repair-current.json','gpu-mailbox-frontend-v16-current.json']
 records={}
 for name in names:
  data=read(V/name);records[name]=data;bind(V/name)
  for p,h in data.get('source_sha256',{}).items():bind(p,h)
 build=records['native-gpu-mailbox-disc-build-current.json'];gate=records['native-gpu-mailbox-final-current.json'];assert build['linked_component_bytes']==31758 and gate['cases']==2492 and gate['dispatcher_ancestor_context_canaries']and gate['minimum_caller_context_clearance']==2
 parent=read(build['parent_build']);prefix=bytearray(Path(parent['linked_component']).read_bytes());prefix.extend(bytes((-len(prefix))%4))
 for row in gate['layout_relocations']:
  at=int(row['resident_address'],16)-build['resident_address'];old=bytes.fromhex(row['old']);assert prefix[at:at+len(old)]==old;prefix[at:at+len(old)]=bytes.fromhex(row['new'])
 assert Path(build['linked_component']).read_bytes()==bytes(prefix)+Path(gate['binary']).read_bytes();assert build['component_bytes']==32128 and build['free_reserved_bytes']==370
 keys=['CPU_full','full_RAM_sha256','full_GPU_state_sha256','full_DSP_state_sha256','video_sha256','navigation','locomotion_state','held_buttons'];pending=['acquire_pending','table_pending','leaf_pending','geometry_pending','select_pending','scan_pending','door_pending','interior_pending','ad_pending','ai_pending','sc_pending','ach_pending','an_pending','dir_pending','mb_pending'];jobs={};reports={}
 for label in ['candidate','control']:
  p=V/('native-gpu-mailbox-v3-quiescent-'+label+'-current.json');job=read(p);assert job['status']=='terminal_native_gpu_mailbox_route_pending_review'and job['exit_code']==0 and job['returned_outdoors']and job['live_monitor_pass']and job['mailbox_monitor_pass']
  assert subprocess.run(['ps','-p',str(job['child_pid']),'-o','command='],capture_output=True).returncode!=0;bind(p)
  for p,h in job['source_sha256'].items():bind(p,h)
  folder=Path(job['directory'])/'candidate';report=read(folder/'report.json');assert sha(folder/'report.json')==job['report_sha256'];assert not report['captured_state_input']and not report['host_CPU_or_GPU_register_seed']and report['C_CPU_backend']['mode']=='reference'and job['checkpoint_restores']==job['host_guest_RAM_writes']==0
  o=job['observations'];assert all(o[k]==0 for k in pending)and o['mb_entries']==o['mb_returns']and all(n>0 for n in o['mb_returns']);assert o['mb_helpers']==2*sum(o['mb_returns'])and all(o[k]==0 for k in ['mb_errors','mb_context_errors','mb_stack_outside','ad_context_collisions','sc_context_corruptions'])
  if label=='candidate':assert o['mb_native']==o['mb_entries']and o['mb_old_steps']==0 and o['mb_context_entries']==o['mb_context_returns']==sum(o['mb_entries'])and report['disc_sha256']==build['derived_disc_sha256']
  else:assert o['mb_native']==[0,0]and o['mb_source_steps']==0 and o['mb_old_steps']>0 and job['control_delta']['restored_entries']==['e220','e2b8']and job['control_delta']['declared_bytes']==12 and report['disc_sha256']==job['control_delta']['control_sha256']
  for name in ['report.json','gameplay-observation.json','frontend-PCM.s16le','original-emulator-final-frame.png','source-derived-current-room-exit-plan.json']:bind(folder/name)
  jobs[label]=job;reports[label]=report
 comparison=dict(candidate_frames=jobs['candidate']['frames'],control_frames=jobs['control']['frames'],aligned_frames=min(x['frames']for x in jobs.values()),differing_frames={k:sum(a[k]!=b[k]for a,b in zip(reports['candidate']['frames'],reports['control']['frames']))for k in keys},PCM={label:dict(bytes=(p:=Path(job['directory'])/'candidate/frontend-PCM.s16le').stat().st_size,sha256=sha(p))for label,job in jobs.items()},adaptive_controller_paths_may_differ=True,whole_state_equivalent=False,timing_differences_unresolved=True)
 common=min(x['bytes']for x in comparison['PCM'].values());comparison.update(PCM_equal=comparison['PCM']['candidate']==comparison['PCM']['control'],PCM_common_prefix_bytes=common,PCM_common_prefix_equal=len({prefix_sha(Path(job['directory'])/'candidate/frontend-PCM.s16le',common)for job in jobs.values()})==1);save(out/'fresh-pair-comparison.json',comparison);bind(out/'fresh-pair-comparison.json')
 correction=read(V/'gpu-mailbox-ancestor-correction-current.json');assert correction['actual_dispatcher_context_relative_to_GPU_entry']==[-230,-158]and [x['real_dispatcher_context_preserved']for x in correction['results']]==[False,False,False,True];bind(V/'gpu-mailbox-ancestor-correction-current.json')
 old_scope=dict(correction);old_scope['status']='three_failed_bridge_variants_retained_not_promoted';old_scope['fix']='124byte context stores44Ccallee-save bytes; actual fixed E098 preserves D/A and only SR is copied back. Generic flag helpers are forced inline to prevent deferred C call arguments from extending the frame. Selected local C body unchanged. Full2492prototype/finalcases preserve current320byte dispatcher and sprite contexts; maximum156bytes,2byte finite clearance.'
 for prefix in ['native-gpu-mailbox-quiescent-','native-gpu-mailbox-v2-quiescent-']:
  for label in ['candidate','control']:
   job=read(V/(prefix+label+'-current.json'));bind(Path(job['directory'])/'protocol.json')
   for p,h in job['source_sha256'].items():bind(p,h)
   for name in ['report.json','gameplay-observation.json','RAM-final.bin']:bind(Path(job['directory'])/'candidate'/name)
 save(out/'earlier-bridge-rejections.json',old_scope);bind(out/'earlier-bridge-rejections.json')
 o=jobs['candidate']['observations'];oc=jobs['control']['observations'];coverage=dict(candidate_mailbox_returns=o['mb_returns'],control_original_mailbox_returns=oc['mb_returns'],candidate_helper_entries=o['mb_helpers'],candidate_max_private_depth=o['mb_max_depth'],candidate_min_task_headroom=o['mb_min_headroom'],candidate_context_entries=o['mb_context_entries'],candidate_context_returns=o['mb_context_returns'],direction_returns=o['dir_returns'],movement_returns=o['ach_returns'],navigation_returns=o['an_returns'],dispatcher_returns=o['ad_returns'],sprite_returns=o['sc_returns'],all_pending_zero=True,all_monitors_pass=True)
 report=out/'review.txt';report.write_text('BIWN GPU COMMAND WRAPPERS — REVIEWED NATIVE EXPERIMENT\n\nTwo complete CPU command wrappers E220/E2B8 use the unchanged local informed repair. Only one outer Markdown fence was removed; supplied flags/ABI/assembly bridge are coordinator work. First Author output was incomplete and rejected. No optimizer update or broad quality gain is claimed.\n\nThe final native component is922bytes, appended with2alignment bytes to the prior30834bytes:31758resident/32128reserved/free370. Heap166B40,stagingF6400..FE200,trailer preserved. Seven heap and two staging operands relocate; prior algorithm bytes remain unchanged. Original CDI is untouched.\n\n2492prototype and2492final original/native CPU/SR/banks/publicRAM/ordered mailbox cases pass. Actual E098 runs in original and pending-repair variants. GPU replies are scripted in component tests. Known immediate and dispatcher-ancestor contexts are preserved; arbitrary interrupt/fault/concurrency/aliasing remains unproved. New96startup/192heapinitialize/3392native+orderedheap-copy/36capacity checks pass. Exact read-only live monitor is qualified232original/native executions and4decoded-observation negatives.\n\n'+json.dumps(dict(coverage=coverage,comparison=comparison,prior_bridge=old_scope),indent=2)+'\n\nBoth fresh routes use ordinary inputs with retained emulator CPU/GPU/DSP/IRQ/HLE, no RAM/register seed or state restore. Control restores only12declared entry bytes, same layout and other compiled code. Raw runner PCM/frame comparisons target an older historical reference; the fresh pair above is authoritative. No complete game/same-console source rebuild, hardware boot/timing, whole-game audio or speedup claim. LM Studio native Chat display remains unverified. Advertising reliability and portable/latest workflow work remain.\n');bind(report);bind(Path(__file__))
 state=dict(status='terminal_native_gpu_mailbox_v3_fresh_routes_reviewed',directory=str(out),report=str(report),resident_bytes=31758,reservation_bytes=32128,heap_start=build['heap_start'],staging_address=build['staging_address'],free_reserved_bytes=370,coverage=coverage,comparison=comparison,prior_bridge_rejection=old_scope,live_monitor_pass=True,image=str(Path(jobs['candidate']['directory'])/'candidate/original-emulator-final-frame.png'),new_local_C_body_adopted=True,new_training=False,default_preview_promoted=False,whole_game_complete=False,physical_console_verified=False,dependencies_sha256=deps,scope=__doc__);save(out/'protocol.json',state);save(V/'native-gpu-mailbox-v3-integration-reviewed-current.json',state);print({k:state[k]for k in ['status','resident_bytes','coverage','comparison']})
if __name__=='__main__':main()
