"""Review completed fresh direction/control routes and preserve exact limits."""
import hashlib,json,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def prefix_sha(path,length):
 h=hashlib.sha256()
 with Path(path).open('rb')as stream:
  while length:
   data=stream.read(min(length,1048576));assert data;h.update(data);length-=len(data)
 return h.hexdigest()
def main():
 out=V/'native-direction-integration-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();deps={}
 def bind(p,h=None):
  p=Path(p).resolve();actual=sha(p);assert h is None or actual==h,str(p)
  if p.name.endswith(('-current.json','-active.json')):
   target=snap/(hashlib.sha256(str(p).encode()).hexdigest()[:12]+'-'+p.name);shutil.copy2(p,target);p=target
  assert str(p)not in deps or deps[str(p)]==actual,str(p);deps[str(p)]=actual
 records={}
 for name in ['native-actor-direction-current.json','native-actor-direction-final-current.json','native-actor-direction-contexts-current.json','native-actor-direction-negatives-current.json','native-actor-direction-disc-build-current.json','actor-direction-layout-startup-heap-initialize-current.json','actor-direction-layout-heap-operations-current.json','actor-direction-layout-capacity-witness-current.json','actor-direction-live-observer-current.json','actor-direction-native-Author-current.json','actor-direction-native-Repair-current.json','actor-direction-local-proposal-reviewed-current.json','actor-direction-local-repair-reviewed-current.json','direction-route-pointer-repair-current.json','actor-direction-frontend-v11-current.json','configured-actor-direction-frontend-current.json','native-direction-development-SFT-current.json']:
  data=read(V/name);records[name]=data;bind(V/name)
  for p,h in data.get('source_sha256',{}).items():bind(p,h)
 build=records['native-actor-direction-disc-build-current.json'];gate=records['native-actor-direction-final-current.json'];assert build['linked_component_bytes']==30834 and gate['cases']==2560 and gate['minimum_caller_context_clearance']==8
 old=Path(read(build['parent_build'])['linked_component']).read_bytes();prefix=bytearray(old)
 for row in gate['layout_relocations']:
  at=int(row['resident_address'],16)-build['resident_address'];before=bytes.fromhex(row['old']);assert prefix[at:at+len(before)]==before;prefix[at:at+len(before)]=bytes.fromhex(row['new'])
 assert Path(build['linked_component']).read_bytes()==bytes(prefix)+Path(gate['binary']).read_bytes()
 keys=['CPU_full','full_RAM_sha256','full_GPU_state_sha256','full_DSP_state_sha256','video_sha256','navigation','locomotion_state','held_buttons'];jobs={};reports={};prior_cutoffs={}
 pending_keys=['acquire_pending','table_pending','leaf_pending','geometry_pending','select_pending','scan_pending','door_pending','interior_pending','ad_pending','ai_pending','sc_pending','ach_pending','an_pending','dir_pending']
 for label in ['candidate','control']:
  p=V/('native-actor-direction-quiescent-'+label+'-current.json');job=read(p);assert job['status']=='terminal_native_actor_direction_route_pending_review'and job['exit_code']==0 and job['returned_outdoors']and job['live_monitor_pass']and job['direction_monitor_pass']
  assert subprocess.run(['ps','-p',str(job['child_pid']),'-o','command='],capture_output=True).returncode!=0;bind(p)
  for name,h in job['source_sha256'].items():bind(name,h)
  folder=Path(job['directory'])/'candidate';report=read(folder/'report.json');assert sha(folder/'report.json')==job['report_sha256']
  assert not report['captured_state_input']and not report['host_CPU_or_GPU_register_seed']and report['C_CPU_backend']['mode']=='reference'and job['checkpoint_restores']==job['host_guest_RAM_writes']==0
  o=job['observations'];assert all(o[k]==0 for k in pending_keys)
  assert o['dir_entries']==o['dir_returns']>0 and o['dir_errors']==o['dir_context_errors']==o['dir_stack_outside']==0
  assert o['ach_entries']==o['ach_returns']and o['ach_context_errors']==o['ach_errors']==0 and o['an_entries']==o['an_returns']
  if label=='candidate':assert o['dir_native']==o['dir_entries']and o['dir_old_steps']==0 and o['dir_context_entries']==o['dir_context_returns']==o['dir_entries']and report['disc_sha256']==build['derived_disc_sha256']
  else:assert o['dir_native']==o['dir_source_steps']==0 and o['dir_old_steps']>0 and job['control_delta']['restored_entries']==['13440']and job['control_delta']['declared_bytes']==8 and report['disc_sha256']==job['control_delta']['control_sha256']
  for name in ['report.json','gameplay-observation.json','frontend-PCM.s16le','original-emulator-final-frame.png','source-derived-current-room-exit-plan.json']:bind(folder/name)
  prior=read(V/('native-actor-direction-'+label+'-current.json'));prior_folder=Path(prior['directory'])/'candidate';prior_report=read(prior_folder/'report.json');bind(V/('native-actor-direction-'+label+'-current.json'));bind(prior_folder/'report.json');bind(prior_folder/'gameplay-observation.json')
  differences={k:sum(a[k]!=b[k]for a,b in zip(prior_report['frames'],report['frames']))for k in keys};old_pcm=prior_folder/'frontend-PCM.s16le';length=old_pcm.stat().st_size;prefix_equal=sha(old_pcm)==prefix_sha(folder/'frontend-PCM.s16le',length)
  prior_cutoffs[label]=dict(original_frames=prior['frames'],extended_frames=job['frames'],extra_normal_frames=job['frames']-prior['frames'],old_pending={k:prior['observations'][k]for k in pending_keys if prior['observations'][k]},old_errors={k:prior['observations'][k]for k in ['dir_errors','dir_context_errors','ach_errors','ach_context_errors']},prefix_frame_differences=differences,old_PCM_prefix_identical=prefix_equal,new_pending_all_zero=True)
  jobs[label]=job;reports[label]=report
 comparison=dict(candidate_frames=jobs['candidate']['frames'],control_frames=jobs['control']['frames'],aligned_frames=min(job['frames']for job in jobs.values()),differing_frames={k:sum(a[k]!=b[k]for a,b in zip(reports['candidate']['frames'],reports['control']['frames']))for k in keys},PCM={label:dict(bytes=(f:=Path(job['directory'])/'candidate/frontend-PCM.s16le').stat().st_size,sha256=sha(f))for label,job in jobs.items()},adaptive_controller_paths_may_differ=True,whole_state_equivalent=False,timing_differences_unresolved=True)
 comparison['PCM_equal']=comparison['PCM']['candidate']==comparison['PCM']['control'];common=min(x['bytes']for x in comparison['PCM'].values());comparison['PCM_common_prefix_bytes']=common;comparison['PCM_common_prefix_equal']=len({prefix_sha(Path(job['directory'])/'candidate/frontend-PCM.s16le',common)for job in jobs.values()})==1
 save(out/'fresh-pair-comparison.json',comparison);save(out/'observation-cutoff-review.json',prior_cutoffs);bind(out/'fresh-pair-comparison.json');bind(out/'observation-cutoff-review.json')
 o=jobs['candidate']['observations'];oc=jobs['control']['observations'];coverage=dict(candidate_direction_returns=o['dir_returns'],control_original_direction_returns=oc['dir_returns'],candidate_direction_max_depth=o['dir_max_depth'],control_direction_max_depth=oc['dir_max_depth'],candidate_direction_min_task_headroom=o['dir_min_headroom'],candidate_context_entries=o['dir_context_entries'],candidate_context_returns=o['dir_context_returns'],shared_chain_returns=o['ach_returns'],shared_chain_min_headroom=o['ach_min_headroom'],shared_chain_max_depth=o['ach_max_depth'],shared_context_checks=o['ach_context_checks'],navigation_returns=o['an_returns'],actor_dispatch_returns=o['ad_returns'],initializer_returns=o['ai_returns'],sprite_create_returns=o['sc_returns'],selector_successes=o['interior_kind_successes'],selector_failures=o['interior_kind_failures'])
 image=Path(jobs['candidate']['directory'])/'candidate/original-emulator-final-frame.png';report=out/'review.txt';report.write_text('''BIWN — NATIVE ACTOR DIRECTION / FRESH ROUTE REVIEW

The 798-byte native C13440 component is now in a separate30,834-byte experiment.
Both fresh candidate and original-direction control returned outdoors through
ordinary controller input. All watched calls finished with zero pending counts;
all live monitors pass. Direction calls execute high-level C in the candidate
and original13440 instructions in the control. Actual originalE588 division
remains. This is not a full-game source rebuild or physical-console proof.

The control restores only original13440entry(8declared bytes). Both share the
31,104-byte reserve,heap166740,stagingF6800..FE200 and all prior compiled code.
Seven heap operands and two staging-clear operands relocate; other parent
algorithm bytes are identical. Atari trailer and original CDI are preserved.
96startup/192actualheap-initializer cases,3,392native+3,392orderedheap/copy cases
and36capacity requests pass. Fresh initial heap capacity366,784bytes.

Separate direction proofs:2,560prototype and2,560final-address original/native
fullCPU/SR/banks/publicRAM/ordered cases,all61reachable root sites;one unreachable
branch excluded. Caller-context canaries pass2,560cases with minimum8byte
clearance,max224privatebytes. Four semantic defects,one deliberately overlapping
context andfour read-only monitor observation defects reject. The exact live
observer is qualified306original/native executions. Interrupts,faults,arbitrary
concurrency/aliasing and unobserved paths remain outside these finite proofs.

The first two gameplay recordings ended with one watched call still pending,
zero direction/context errors. They remain incomplete receipts. New recordings
extend ordinary outdoor hold until all monitored calls finish,at most512extra
frames. Exact execution-prefix/audio comparison and extra frames are below.
No RAM restore,position patch,manualCPUstep or observation-state reset.

Local roles:Author61.73s, same-weightReviewer32.84s, one informedrepair89.80s.
Both C proposals strictly compile after one outer code fence is removed,but
fail the first fixture. First proposal enters actualE588with stalecontext/zero
divisor; repair still stores before decrementingSP,overwriting the rootreturn
slot with incomingD2. Reviewer output is truncated at600tokens. Neither local
proposal is adopted. Current direction is coordinator adaptation of an earlier
checked portable body. No newweights or independent-modelreview claim. One
proof-mapped developmentSFTexample is prepared but not trained or split.

The installed v11MCP keeps18tools and adds actor_direction to the existing
task/verifier tools. Actualtask fetch,oldtask retention,badlocal rejection,and
positivecoordinator2560case check pass. Actualconfigured source retrieval still
returns original PDF9/20. NativeChat inspection timed out without AX/window
state; Chat display/adoption remain unverified. Raw prompts/responses retained.

Retained native emulatorCPU/GPU/DSP/IRQ/platform/HLE run both discs. Rawrunner
PCM_equal/frame_differences compare an older historical reference;the fresh pair
below is authoritative for this candidate/control. State/video/media/timing and
adaptive-input differences are not waived by successful routes/return checks.
Full readable game,same-console source rebuild,physicalconsole timing,whole-game
audio/speedup,Advertising reliability/nativeChat andfull migration remain open.

'''+json.dumps(dict(coverage=coverage,comparison=comparison,cutoff_review=prior_cutoffs),indent=2)+'\n\nFinal image: '+str(image)+'\n');bind(report);bind(Path(__file__))
 state=dict(status='terminal_native_direction_fresh_quiescent_routes_reviewed',directory=str(out),report=str(report),resident_bytes=30834,reservation_bytes=31104,heap_start=build['heap_start'],staging_address=build['staging_address'],free_reserved_bytes=270,coverage=coverage,comparison=comparison,prior_cutoff_review=prior_cutoffs,live_monitor_pass=True,image=str(image),new_local_code_adopted=False,new_training=False,default_preview_promoted=False,whole_game_complete=False,physical_console_verified=False,dependencies_sha256=deps,scope=__doc__);save(out/'protocol.json',state);save(V/'native-direction-integration-reviewed-current.json',state);print(json.dumps({k:state[k]for k in ['status','directory','resident_bytes','coverage','comparison']}))
if __name__=='__main__':main()
