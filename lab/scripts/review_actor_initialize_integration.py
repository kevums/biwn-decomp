"""Audit the actual21,080disc pair and separate failed local profile trial."""
import json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def read(p):return json.loads(Path(p).read_text())
def main():
 v=ROOT/'verification';bp=v/'native-actor-initialize-disc-build-current.json';build=read(bp);assert build['linked_component_bytes']==21080 and build['component_bytes']==24512 and build['heap_start']==0x164d80
 gates={name:read(v/name)for name in ['actor-layout-startup-heap-initialize-current.json','actor-layout-heap-operations-current.json','actor-initialize-final-startup-current.json','actor-initialize-live-contexts-current.json','actor-layout-capacity-witness-current.json']}
 assert gates['actor-layout-startup-heap-initialize-current.json']['heap_initialize_cases']==192
 assert gates['actor-layout-heap-operations-current.json']['native_cases']==gates['actor-layout-heap-operations-current.json']['ordered_cases']==3392
 assert gates['actor-initialize-final-startup-current.json']['cases']==96
 contexts=gates['actor-initialize-live-contexts-current.json'];assert contexts['dispatch_cases']==856 and contexts['initializer_cases']==1024 and len(contexts['negative_controls'])==4
 assert gates['actor-layout-capacity-witness-current.json']['cases']==36
 component=read(build['component_gate']);assert component['cases']==1024 and len(component['original_sites'])==148 and component['binary_bytes']==1620
 pair=[]
 for kind in ['candidate','control']:
  p=v/f'native-actor-initialize-{kind}-current.json';s=read(p);assert s['status']=='terminal_native_actor_initialize_route_pending_review'and s['exit_code']==0 and s['returned_outdoors']and s['live_monitor_pass']and s['actor_initialize_monitor_pass']
  o=s['observations'];assert o['ad_entries']==o['ad_returns']==13 and o['ad_actor']==12 and o['ad_sprite']==1 and o['ad_context_checks']==13
  assert o['ai_entries']==o['ai_returns']==12 and o['ai_helper_entries']==o['ai_helper_returns']==16
  assert o['ad_context_collisions']==o['ad_context_SP_inside']==o['ad_errors']==o['ai_context_corruptions']==o['ai_errors']==o['ad_pending']==o['ai_pending']==o['ad_stack_outside']==o['ai_stack_outside']==0
  assert o['ai_native_entries']==(12 if kind=='candidate'else 0)and o['ai_old_steps']==(0 if kind=='candidate'else 961)and o['ai_context_checks']==(16 if kind=='candidate'else 0)
  assert o['ad_max_depth']==(600 if kind=='candidate'else 392)and o['ad_min_headroom']==(182 if kind=='candidate'else 390)
  folder=Path(s['directory'])/'candidate';report=read(folder/'report.json');assert sha(folder/'report.json')==s['report_sha256']and read(folder/'gameplay-observation.json')==o
  assert report['C_CPU_backend']['stats']['errors']==0 and report['frames'][-1]['player_mode_word']==1 and report['frames'][-1]['floor_word']==0 and report['frames'][-1]['navigation']['outdoor_hold']>=120
  assert [x['frame']for x in report['frames']]==list(range(1,len(report['frames'])+1))
  for key in ['errors','copy_errors','acquire_monitor_errors','acquire_pending','acquire_user_stack_outside','geometry_errors','geometry_pending','geometry_stack_outside','select_errors','select_pending','select_stack_outside','scan_errors','scan_pending','scan_stack_outside','door_errors','door_pending','door_stack_outside','interior_errors','interior_pending','interior_stack_outside','leaf_pending','heap_floor_errors']:assert o[key]==0,key
  assert o['heap_base']==0x164d80 and o['heap_inits']>0;pair.append((s,report,folder))
 assert [len(x[1]['frames'])for x in pair]==[29790,29777]
 delta=pair[1][0]['control_delta'];assert delta['restored_entries']==['134dc']and delta['declared_bytes']==8
 assert pair[0][1]['disc_sha256']==build['derived_disc_sha256']and pair[1][1]['disc_sha256']==delta['control_sha256']
 fields=['CPU_full','full_RAM_sha256','full_GPU_state_sha256','full_DSP_state_sha256','video_sha256','navigation','locomotion_state','held_buttons'];diff={k:sum(a[k]!=b[k]for a,b in zip(pair[0][1]['frames'],pair[1][1]['frames']))for k in fields};assert diff==dict(CPU_full=25987,full_RAM_sha256=29766,full_GPU_state_sha256=29072,full_DSP_state_sha256=13905,video_sha256=23406,navigation=25118,locomotion_state=210,held_buttons=282)
 pcm=[x[2]/'frontend-PCM.s16le'for x in pair];assert sha(pcm[0])!=sha(pcm[1])and[p.stat().st_size for p in pcm]==[95328000,95286400]
 trialp=v/'local-actor-dispatch-low-repair-current.json';trial=read(trialp);assert trial['status']=='terminal_low_reasoning_dispatch_repair_pending_coordinator_review'and not trial['raw_gate_pass']and trial['actual_predictions']==2
 assert trial['usage']['completion_tokens']==trial['usage']['completion_tokens_details']['reasoning_tokens']==5999 and not Path(trial['source']).read_text().strip()and trial['reviewer_issues']==0
 out=v/'actor-initialize-integration-reviewed'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();deps={};aliases={}
 def bind(path,h=None):
  p=Path(path).resolve();actual=sha(p);assert h is None or h==actual,p
  if p.name.endswith(('-current.json','-active.json')):
   target=snap/(hashlib.sha256(str(p).encode()).hexdigest()[:12]+'-'+p.name);shutil.copy2(p,target);aliases[str(p)]=str(target);p=target
  deps[str(p)]=actual
 for obj in [build,component,*gates.values(),*[x[0]for x in pair]]:
  for p,h in obj.get('source_sha256',{}).items():bind(p,h)
 for p in [Path(__file__),bp,Path(build['component_gate']),trialp,*[v/n for n in gates],v/'native-actor-initialize-candidate-current.json',v/'native-actor-initialize-control-current.json']:bind(p)
 for _,_,folder in pair:
  for name in ['report.json','frontend-PCM.s16le','gameplay-observation.json']:bind(folder/name)
 for p in Path(trial['directory']).iterdir():
  if p.is_file():bind(p)
 report=ROOT/'reports/native-actor-initialize-integration.txt';assert not report.exists()
 report.write_text('''BIWN —134DCACTOR INITIALIZER INTEGRATED INTO AN EXPERIMENTAL DISC

Native resident code21080bytes in a24512byte reservation; heapfloor164D80,
3432bytes spare. Larger reservation reduces initial heap capacity4032bytes to
373376. Original disc unchanged; experimental APFSclone derivatives retain byte
provenance. Seven decoded heap-floor/+4/+8operands and loaderWORD27FF→2FDFare
relocated. Layout-only clone differs16actualdisc bytes; adding1620initializer
bytes and the8byte134DCentry redirect changes1340more actual bytes. Parent
code remains identical relative to that explicitly relocated layout.

VERIFICATION
96layout startup and192heap-initializer cases; original raised-boundary heap
init matches the source assembly transcription byte-for-byte after its five
explicit operands change. Newfullpayload passes96startup cases. Native
allocator/compactor/copy+emulatedblitter3392cases and a separate3392ordered-bus
comparison pass against original routines at the same declared heap boundary.
36actual-native-constructor capacity requests cover zero/small/exact/over-capacity
sizes. These do not establish arbitrary allocation sequences or all resources.

134DCfinal-address1639C4passes1024cases/all148original sites. Both final-address
C routines together pass856dispatcher-rooted cases; direct initializer1024cases
also execute through the read-only context monitor, original and C lanes each:
3760root executions. Original10520or the common parent's compiled10520is used as
declared by the proof; four leaf services remain prescribed in component lanes.
Monitor callbacks run before those scripts mutate returns. Wrong rootD0, childX,
parent context and initializer context inputs are rejected. Context negatives
change only a RAM mirror; the monitor never writes fixture or native gameRAM.
Unknown modified jump-table targets, faults/interrupt/device concurrency remain
outside the finite algorithm proof.

REAL GAMEPLAY / REAL HELPERS
Candidate29790frames; matching layout control29777. Both return outdoors and
hold120frames. Only8bytes of134DCentry are restored in the control; enlarged
heap/reservation, unused initializer code and prior compiled routines including
13AE0remain common. Both dispatch13calls(12actor/1sprite); initializer12calls,
helper16calls. Candidate executes12native initializers/zero original-body steps;
control executes961original initializer steps. All caller/helperSP/args/callback,
loaded full contextCPU/SR,callee-save/root-return and task-stack checks pass.
13parent and16initializer saved-context canary checks pass in the candidate;
control has13parent checks and no initializer context because its body is
original. No monitor errors,pending calls,context corruption or task-stack-outside.
Prior resource/cache/geometry/door/interior/heap monitors also report zero errors.

Actual nested private depth600bytes/minimum182task-stack bytes of headroom;
initializer564relative to its own entry. There are4008valid observations below
parent context, zero observations inside its occupied interval. The oldSP-only
rule would reject legitimate deeper private frames; actual saved bytes remain
unchanged. This finite route is not a bound for every future caller/helper path.

Fresh aligned prefix29777differs in25987CPUframes,29766RAMhashes,29072GPUstate,
13905DSPstate,23406video,25118navigation,210locomotion and282button records.
PCMhash and length differ95328000versus95286400bytes. Functional completion and
ABI/context agreement do not establish timing/media/full-state equivalence.
The earlier scanner media differences and unexercised fullpool/selector paths
remain. Native emulator CPU/GPU/DSP/IRQandplatform services execute both routes;
no new strict-Cprocessor job or physical-console test applies to this21080disc.

LOCAL MODEL PROFILE TEST — SEPARATE, NO SOURCE ADOPTION
One adaptive13AE0repair Author used supported reasoning=low,6000token budget,
temperature0,32768context. It received saved compiler/native mismatch evidence
and explicitCCR/index findings, with the coordinator reference withheld. In
273.37seconds it emitted5999reasoning tokens and zero final C; the linker then
rejected the missing function. Same-weight structured Reviewer returned empty
issues in4.36seconds despite that empty candidate/error. Two actual predictions;
no code acceptance,source edit,weights or default-profile change. Feedback and
reasoning setting both changed, so this is not an isolated reasoning comparison
or independent held-out benchmark. It demonstrates failure to deliver within
this profile's budget, not executed semantic quality of nonexistent code.
Exact prompts/final outputs/stats are saved and indexed under StartLocalAI→I.

Current disc source/ABI/layout/verification is coordinator work. Prior accepted
local functions retain their historical attribution. Full readable game/original
console rebuild,137E0andremaining actual game logic/interfaces, broader resources
and stack paths,timing/media,native LMStudioChat usability,Advertising reliability
and complete workbench migration/future256GBpreparation remain unfinished.
''');bind(report)
 record=dict(status='terminal_actor_initialize_integrated_two_routes_reviewed',directory=str(out),report=str(report),build=str(bp),build_sha256=sha(bp),resident_bytes=21080,reservation_bytes=24512,heap_floor='0x164d80',reservation_free=3432,initial_heap_capacity=373376,native_initializer_bytes=1620,initializer_cases=1024,initializer_sites=148,dispatcher_joint_cases=856,context_root_executions=3760,heap_native_cases=3392,heap_ordered_cases=3392,heap_initialize_cases=192,capacity_request_cases=36,startup_cases=96,candidate_frames=29790,control_frames=29777,compared_prefix_frames=29777,same_layout_differences=diff,PCM_equal=False,PCM_bytes=[95328000,95286400],live_monitor_pass=True,initializer_live_calls=12,actual_helper_live_calls=16,parent_context_checks=13,initializer_context_checks=16,max_nested_private_depth=600,min_task_headroom=182,context_corruptions=0,candidate_observations=pair[0][0]['observations'],control_observations=pair[1][0]['observations'],local_profile_trial=dict(actual_predictions=2,author_seconds=273.37,reasoning_tokens=5999,final_C_tokens=0,Reviewer_issues=0,code_adopted=False,source=trial['source'],directory=trial['directory']),new_training=False,default_promoted=False,native_Chat_verified=False,new_logical_functions=0,whole_game_complete=False,dependencies_sha256=deps,pointer_snapshots=aliases)
 save(out/'protocol.json',record);save(v/'actor-initialize-integration-reviewed-current.json',record);print(json.dumps({k:record[k]for k in ['status','resident_bytes','candidate_frames','control_frames','initializer_live_calls','min_task_headroom','report']}))

if __name__=='__main__':main()
