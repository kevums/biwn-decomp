"""Review fresh native Deck-image runs and the qualified observer correction."""
import hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
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
 out=V/'native-Deck-route-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
 b=read(V/'native-Deck-coordinate-disc-build-current.json');component=read(V/'native-deck-coordinate-v2-current.json');connected=read(V/'native-deck-connected-v2-current.json');layout=read(V/'native-Deck-layout-startup-heap-initialize-current.json');heap=read(V/'native-Deck-layout-heap-operations-current.json');capacity=read(V/'native-Deck-layout-capacity-witness-current.json');observer=read(V/'native-Deck-region-observer-current.json');stack=read(V/'native-deck-stack-watermark-current.json')
 assert component['completed']==576 and component['task_slots_covered']==101 and component['fallback_cases']==3
 assert connected['paired_checkpoints']==31 and connected['GPU_commands']==[149,149]
 nativeproof=read(Path(connected['proof_directory'])/'report.json');assert nativeproof['compiled_native_coordinate_calls']==17 and nativeproof['active_compiled_helper_yields']==0
 assert layout['startup_cases']==6 and layout['heap_initialize_cases']==192 and heap['native_cases']==heap['ordered_cases']==3392 and capacity['cases']==36 and capacity['initial_capacity']==223680
 assert len(observer['mutations'])==8 and stack['maximum_C_stack_bytes']==266
 assert sha(b['derived_disc'])==b['derived_disc_sha256'];jobs={};reports={};same_lane={}
 for lane in ['candidate','control']:
  job=read(V/('native-Deck-coordinate-v2-quiescent-'+lane+'-current.json'));assert job['status']=='terminal_native_Deck_coordinate_route_pending_review'and job['exit_code']==0 and job['returned_outdoors']and job['live_monitor_pass']and job['arena_monitor_pass']and job['pool_monitor_pass']
  assert subprocess.run(['ps','-p',str(job['child_pid']),'-o','command='],capture_output=True).returncode!=0
  o=job['observations'];assert all(value==0 for key,value in o.items()if (key.endswith('errors')or key.endswith('pending'))and isinstance(value,int)),[(k,x)for k,x in o.items()if k.endswith('errors')and x]
  assert o['deck_entries']==o['deck_native_entries']==o['deck_native_returns']==o['deck_source_steps']==o['deck_invalid_entries']==0
  assert o['pool_returns']==1 and o['mb_entries']==o['mb_returns']
  folder=Path(job['directory'])/'candidate';report=read(folder/'report.json');assert not report['captured_state_input']and not report['host_CPU_or_GPU_register_seed']and report['C_CPU_backend']['mode']=='reference'and job['host_guest_RAM_writes']==job['checkpoint_restores']==0
  oldjob=read(V/('native-Deck-coordinate-quiescent-'+lane+'-current.json'));oldfolder=Path(oldjob['directory'])/'candidate';oldreport=read(oldfolder/'report.json');assert oldjob['observations']['arena_errors']==(1 if lane=='candidate'else 0) and oldjob['returned_outdoors']
  assert report['frames']==oldreport['frames'],'Observer changed frame records for '+lane
  assert sha(folder/'frontend-PCM.s16le')==sha(oldfolder/'frontend-PCM.s16le'),'Observer changed PCM for '+lane
  assert sha(folder/'RAM-final.bin')==sha(oldfolder/'RAM-final.bin')
  same_lane[lane]=dict(frames=len(report['frames']),all_frame_fields_identical=True,final_RAM_identical=True,PCM_identical=True,old_false_arena_errors=oldjob['observations']['arena_errors'],new_arena_errors=0)
  if lane=='candidate':assert o['mb_native']==o['mb_entries']and o['mb_old_steps']==0 and o['pool_native_entries']==1 and o['pool_old_steps']==0 and report['disc_sha256']==b['derived_disc_sha256']
  else:assert o['mb_native']==[0]*8 and o['pool_native_entries']==0 and job['control_delta']['declared_bytes']==62 and len(job['control_delta']['restored_entries'])==10
  data=(folder/'RAM-final.bin').read_bytes();payload=Path(b['component']).read_bytes();assert data[b['deck_arena_address']:b['deck_arena_address']+b['deck_arena_bytes']]==payload[b['deck_arena_address']-b['resident_address']:b['deck_arena_address']-b['resident_address']+b['deck_arena_bytes']]
  jobs[lane]=job;reports[lane]=report
 fields=['CPU_full','full_RAM_sha256','full_GPU_state_sha256','full_DSP_state_sha256','video_sha256','navigation','locomotion_state','held_buttons'];comparison=dict(candidate_frames=len(reports['candidate']['frames']),control_frames=len(reports['control']['frames']),differing_aligned_frames={k:sum(a[k]!=c[k]for a,c in zip(reports['candidate']['frames'],reports['control']['frames']))for k in fields},whole_state_equivalent=False,timing_equivalence_verified=False,control_restores_10_original_roots=True)
 pcm={lane:dict(bytes=(p:=Path(j['directory'])/'candidate/frontend-PCM.s16le').stat().st_size,sha256=sha(p))for lane,j in jobs.items()};n=min(x['bytes']for x in pcm.values());comparison['PCM']=pcm;comparison['PCM_common_prefix_bytes']=n;comparison['PCM_common_prefix_equal']=len({prefix_sha(Path(j['directory'])/'candidate/frontend-PCM.s16le',n)for j in jobs.values()})==1
 coverage=dict(native_component_cases=576,actual_task_slots=101,source_fallback_cases=3,C_stack_bytes=266,C_frame_clearance=626,controlled_connected_native_calls=17,connected_checkpoint_pairs=31,connected_GPU_commands=149,active_helper_yields_observed=0,ordinary_native_coordinate_calls=0,ordinary_GPU_returns=jobs['candidate']['observations']['mb_returns'],ordinary_unobserved_GPU_roots=jobs['candidate']['mailbox_unobserved_roots'],all_16_retained_monitor_families_pass=True,all_101_Deck_arenas_unused_and_unchanged=True,same_lane_observer_correction=same_lane)
 report=out/'review.json';state=dict(status='terminal_native_Deck_image_boot_heap_fresh_routes_reviewed',directory=str(out),native_build=str(V/'native-Deck-coordinate-disc-build-current.json'),native_build_sha256=sha(V/'native-Deck-coordinate-disc-build-current.json'),code_bytes=44430,copy_bytes=70784,total_reservation_bytes=174208,GPU_arena_bytes=26112,Deck_arena_bytes=103424,heap_start=b['heap_start'],initial_heap_bytes=223680,coverage=coverage,comparison=comparison,source_sha256={str(p):sha(p)for p in[Path(__file__),V/'native-Deck-coordinate-disc-build-current.json',V/'native-deck-coordinate-v2-current.json',V/'native-deck-connected-v2-current.json',V/'native-Deck-layout-startup-heap-initialize-current.json',V/'native-Deck-layout-heap-operations-current.json',V/'native-Deck-layout-capacity-witness-current.json',V/'native-Deck-region-observer-current.json',V/'native-deck-stack-watermark-current.json',*[V/('native-Deck-coordinate-v2-quiescent-'+lane+'-current.json')for lane in jobs]]},new_predictions=0,new_training=False,default_preview_promoted=False,whole_game_complete=False,physical_console_verified=False,scope=__doc__+' Ordinaryfreshroute doesnotcallnewcoordinate/E26C;do notconfusecontrolled17nativecallswithordinary/hardwarecoverage. Currentcode/localhybrid includes10coordinatorflagfixes. Pairrestores10roots,soframetimingdifferencescannotbeattributedsolelytoDeck. Activehelperyield/IRQ/physicalproofremainopen.')
 save(report,state);save(V/'native-Deck-image-reviewed-current.json',state);print(state['status'],comparison['candidate_frames'],comparison['control_frames'],flush=True)
if __name__=='__main__':main()
