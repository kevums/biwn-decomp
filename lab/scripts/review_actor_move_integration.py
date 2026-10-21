"""Review26,220disc real-helper routes and original-entry control without timing claims."""
import json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def read(p):return json.loads(Path(p).read_text())
def main():
 v=ROOT/'verification';bp=v/'native-actor-move-disc-build-current.json';build=read(bp);assert build['linked_component_bytes']==26220 and build['component_bytes']==28544 and build['heap_start']==0x165d40 and build['staging_address']==0xf7000 and build['trailer_preserved']
 devp=v/'actor-move-development-reviewed-current.json';dev=read(devp);assert dev['component_cases']==2624 and dev['original_sites']==192 and dev['native_bytes']==2960
 cp=v/'actor-move-live-contexts-current.json';contexts=read(cp);assert contexts['status']=='terminal_final_movement_context_oracle_pass'and contexts['cases']==2624 and contexts['completed']==5248 and len(contexts['negative_controls'])==4
 component=read(build['component_gate']);assert component['cases']==2624 and component['code_address']==0x16489c
 rows=[]
 for kind in ['candidate','control']:
  p=v/f'native-actor-move-{kind}-current.json';s=read(p);assert s['status']=='terminal_native_actor_move_route_pending_review'and s['exit_code']==0 and s['returned_outdoors']and s['live_monitor_pass']and s['actor_move_monitor_pass'],(kind,s.get('status'),s.get('live_monitor_pass'));o=s['observations']
  assert o['am_entries']==o['am_returns']>0 and o['am_helper_entries']==o['am_helper_returns']and o['am_direction_calls']==o['am_submit_calls']==o['am_entries']
  assert o['am_helper_entries']==2*o['am_entries']+o['am_outdoor_calls']+o['am_indoor_calls']
  assert o['am_native_entries']==(o['am_entries']if kind=='candidate'else 0)and(o['am_old_steps']==0 if kind=='candidate'else o['am_old_steps']>0)
  assert o['am_context_checks']==(o['am_helper_entries']if kind=='candidate'else 0)
  for key in ['errors','copy_errors','acquire_monitor_errors','acquire_pending','acquire_user_stack_outside','geometry_errors','geometry_pending','geometry_stack_outside','select_errors','select_pending','select_stack_outside','scan_errors','scan_pending','scan_stack_outside','door_errors','door_pending','door_stack_outside','interior_errors','interior_pending','interior_stack_outside','leaf_pending','heap_floor_errors','ad_errors','ad_pending','ad_context_collisions','ad_context_SP_inside','ad_stack_outside','ai_errors','ai_pending','ai_context_corruptions','ai_stack_outside','sc_errors','sc_pending','sc_context_corruptions','sc_stack_outside','am_errors','am_pending','am_context_corruptions','am_stack_outside']:assert o[key]==0,(kind,key,o[key])
  assert o['heap_base']==0x165d40 and o['heap_inits']>0 and o['ad_entries']==o['ad_returns']==o['ad_native_entries']==13 and o['ai_entries']==o['ai_returns']==o['ai_native_entries']==12 and o['sc_entries']==o['sc_returns']==o['sc_native_entries']==1
  folder=Path(s['directory'])/'candidate';report=read(folder/'report.json');assert sha(folder/'report.json')==s['report_sha256']and read(folder/'gameplay-observation.json')==o
  assert report['C_CPU_backend']['stats']['errors']==0 and report['frames'][-1]['player_mode_word']==1 and report['frames'][-1]['floor_word']==0 and report['frames'][-1]['navigation']['outdoor_hold']>=120
  assert[x['frame']for x in report['frames']]==list(range(1,len(report['frames'])+1));rows.append((s,report,folder))
 delta=rows[1][0]['control_delta'];assert delta['restored_entries']==['13c9a']and delta['declared_bytes']==8 and rows[0][1]['disc_sha256']==build['derived_disc_sha256']and rows[1][1]['disc_sha256']==delta['control_sha256']
 fields=['CPU_full','full_RAM_sha256','full_GPU_state_sha256','full_DSP_state_sha256','video_sha256','navigation','locomotion_state','held_buttons'];diff={k:sum(a[k]!=b[k]for a,b in zip(rows[0][1]['frames'],rows[1][1]['frames']))for k in fields};frames=[len(x[1]['frames'])for x in rows];pcm=[x[2]/'frontend-PCM.s16le'for x in rows];pcm_equal=sha(pcm[0])==sha(pcm[1]);pcmbytes=[p.stat().st_size for p in pcm];co=rows[0][0]['observations'];ctrl=rows[1][0]['observations']
 out=v/'actor-move-integration-reviewed'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();deps={};aliases={}
 def bind(p,h=None):
  p=Path(p).resolve();actual=sha(p);assert h is None or h==actual,p
  if p.name.endswith(('-current.json','-active.json')):
   dest=snap/(hashlib.sha256(str(p).encode()).hexdigest()[:12]+'-'+p.name);shutil.copy2(p,dest);aliases[str(p)]=str(dest);p=dest
  deps[str(p)]=actual
 for obj in [build,component,contexts,*[x[0]for x in rows]]:
  for p,h in obj.get('source_sha256',{}).items():bind(p,h)
 for p,h in dev['dependencies_sha256'].items():bind(p,h)
 for p in [Path(__file__),bp,devp,cp,v/'native-actor-move-candidate-current.json',v/'native-actor-move-control-current.json']:bind(p)
 for _,_,folder in rows:
  for n in ['report.json','frontend-PCM.s16le','gameplay-observation.json']:bind(folder/n)
 report=out/'review.txt';report.write_text(f'''BIWN: actor movement integrated and exercised with real emulated helpers

The26,220byte native experimental payload contains the coordinator's complete high-level13C9Amovement body/original-facingABI (2,960bytes at0x16489C), in28,544reservation with2,324free. StagingF7000/clear28,672endsFE000; Atari trailerFE520preserved. Heap165D40/capacity369,344. Original disc unchanged. Prior layout/startup/heap/capacity provenance and local-output failures remain in the development review.

Component matrices each2,624cases/all192original sites: prescribed-four-helper prototype, actual13440/E588variant, final address. Returned fullCPU/SR/banks, helper-entryCPU/SR/SP/args, orderedpublicRAM/public2MBmemory compare. GPU/collision prescribed in these fixture matrices. Four source/binary defects reject. Fullpayload96startup, heapinitializer192/nativeallocator-copy-blitter3,392+ordered3,392/capacity36pass. Separate final-context matrix executes5,248original/Croots with actual direction/division, prescribedGPU/collision. Read-only monitor qualifies4decodedCPU/mirror-only negatives: calleeD2,helperX,savedcontext,taskboundary. Snapshotr0..17atrootSP-488; r15is working originalSP, so helperentrycontextSP=currentSP+4. Monitor writes neither nativeCPU nor gameRAM.

Fresh native-emulator candidate{frames[0]}frames/control{frames[1]}frames, both return outdoors/hold120frames. Only8bytes13C9Aentry restored in control; new reservation/heap/staging, unused movementcode and nativecreation/previous routines common. Both retain original native emulator CPU/GPU/DSP/IRQ/platform services, including BIOS/device/HLE timing services. No source-instruction processor backend or physical console proof is transferred.

Candidate{co['am_entries']}movement entries/returns, all native, zero original movement-body instructions, {co['am_native_steps']}compiled movement instructions observed. Real original13440direction{co['am_direction_calls']}, E220GPUsubmission{co['am_submit_calls']},13B5Aoutdoor collision{co['am_outdoor_calls']},13BB0indoor collision{co['am_indoor_calls']}. Helper entries/returns/context checks{co['am_helper_entries']}; all ABI/context/task-boundary error counters zero. Private depth{co['am_max_depth']}, minimum observed task headroom{co['am_min_headroom']}. Control{ctrl['am_entries']}movement calls, {ctrl['am_old_steps']}original-body steps, zero native movement entries, {ctrl['am_helper_entries']}helpercalls; depth{ctrl['am_max_depth']}/headroom{ctrl['am_min_headroom']}. Counts need not match across different emulated instruction costs and schedules. These finite observed paths are not a universal stack/resource/concurrency bound. The live monitor does not independently predict the full public-RAM algorithm; its finite comparison and real-helper execution are separate evidence.

Both routes preserve13native dispatcher returns(12actor/1sprite),12native initializers,1native sprite creator with three real position/allocation/decode helpers and zero inherited oracle errors. Current actor/sprite selector success/failure counts remain explicitly scoped in raw observations. Indoormovement13BB0, unexercised result/rollback/animation/mode paths, pool exhaustion/other callbacks and arbitrary concurrency still require broader live coverage. A named helper call does not imply every internal outcome was exercised.

Aligned-prefix frame differences{json.dumps(diff)}. PCM equality{pcm_equal}, byte lengths{pcmbytes}. No whole-frame/video/audio/state/timing equivalence or whole-game speedup claim. Earlier scanner/initializer/creation discrepancies remain unresolved. Functional route completion does not establish a full readable game/same-console rebuild.

Code/ABI/fixtures/monitors/integration/review are coordinator work. No new localAuthor acceptance, training, weights/default-model changes, independent same-weight review or nativeChat display demonstration. Previous7prediction failures are retained separately. Existing interactive preview remains unchanged and uses its older checkpoint. Full game, easy reliable local inference/roles, Advertising reliability and full migration/future256GBpreparation remain open.
''');bind(report)
 result=dict(status='terminal_actor_move_real_helpers_two_routes_reviewed',directory=str(out),report=str(report),build=str(bp),build_sha256=sha(bp),resident_bytes=26220,reservation_bytes=28544,reservation_free=2324,heap_floor='0x165d40',staging='0xf7000',initial_heap_capacity=369344,movement_native_bytes=2960,component_cases=2624,original_sites=192,context_root_executions=5248,startup_cases=96,live_monitor_pass=True,candidate_frames=frames[0],control_frames=frames[1],compared_prefix_frames=min(frames),same_layout_differences=diff,PCM_equal=pcm_equal,PCM_bytes=pcmbytes,movement_live_calls=co['am_entries'],actual_helper_calls=co['am_helper_entries'],outdoor_collision_calls=co['am_outdoor_calls'],indoor_collision_calls=co['am_indoor_calls'],maximum_movement_depth=co['am_max_depth'],minimum_movement_headroom=co['am_min_headroom'],candidate_observations=co,control_observations=ctrl,new_training=False,default_promoted=False,native_Chat_verified=False,whole_game_complete=False,dependencies_sha256=deps,pointer_snapshots=aliases);save(out/'protocol.json',result);save(v/'actor-move-integration-reviewed-current.json',result);print(json.dumps({k:result[k]for k in ['status','resident_bytes','candidate_frames','control_frames','movement_live_calls','actual_helper_calls','minimum_movement_headroom']}))
if __name__=='__main__':main()
