"""Review fresh native-navigation gameplay against same-layout original navigation.
Retained native processors/HLE and different timing/adaptive inputs remain limits.
"""
import json,hashlib,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def main():
 out=V/'native-navigation-fresh-route-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();deps={}
 def bind(p,h=None):
  p=Path(p).resolve();actual=sha(p);assert h is None or h==actual,str(p)
  if p.name.endswith(('-current.json','-active.json')):
   dest=snap/(hashlib.sha256(str(p).encode()).hexdigest()[:12]+'-'+p.name);shutil.copy2(p,dest);p=dest
  assert str(p)not in deps or deps[str(p)]==actual,str(p);deps[str(p)]=actual
 development=read(V/'native-navigation-component-reviewed-current.json');bind(V/'native-navigation-component-reviewed-current.json')
 for p,h in development['dependencies_sha256'].items():bind(p,h)
 build=read(V/'native-actor-navigation-build-normalized-current.json');bind(V/'native-actor-navigation-build-normalized-current.json');assert build['linked_component_bytes']==29876 and build['free_reserved_bytes']==204
 parent=read(build['parent_build']);a=Path(parent['linked_component']).read_bytes();b=Path(build['linked_component']).read_bytes();lo=parent['actor_chain_start']-parent['resident_address'];hi=parent['actor_chain_end']-parent['resident_address'];assert a[lo:hi]==b[lo:hi], 'Shared C-chain bytes changed'
 jobs={};reports={}
 for label in ['candidate','control']:
  pointer=V/('native-actor-navigation-'+label+'-current.json');job=read(pointer);assert job['status']=='terminal_native_actor_navigation_route_pending_review'and job['exit_code']==0
  assert job['returned_outdoors']and job['live_monitor_pass']and job['navigation_monitor_pass']and job['actor_chain_monitor_pass']
  assert subprocess.run(['ps','-p',str(job['child_pid']),'-o','command='],capture_output=True).returncode!=0
  bind(pointer)
  for p,h in job['source_sha256'].items():bind(p,h)
  folder=Path(job['directory'])/'candidate';report=read(folder/'report.json')
  for name in ['report.json','gameplay-observation.json','frontend-PCM.s16le','original-emulator-final-frame.png']:bind(folder/name)
  assert sha(folder/'report.json')==job['report_sha256']and report['disc_sha256']==(build['derived_disc_sha256']if label=='candidate'else job['control_delta']['control_sha256'])
  assert not report['captured_state_input']and not report['host_CPU_or_GPU_register_seed']and report['C_CPU_backend']['mode']=='reference'and job['checkpoint_restores']==job['host_guest_RAM_writes']==0
  o=job['observations'];assert o['an_entries']==o['an_returns']and sum(o['an_entries'])>0
  assert all(o[k]==0 for k in ['an_pending','an_errors','an_context_errors','an_stack_outside','ach_pending','ach_errors','ach_context_errors','ach_virtual_errors','ach_stack_outside'])
  assert o['ach_entries']==o['ach_native']==o['ach_returns']and o['ach_old_steps']==[0,0,0]and o['ach_virtual_entries']==o['ach_virtual_returns']
  if label=='candidate':assert o['an_native']==o['an_entries']and o['an_old_steps']==[0,0,0,0]and o['an_context_entries']==o['an_context_returns']==sum(o['an_entries'])
  else:
   assert o['an_native']==[0,0,0,0]and sum(o['an_old_steps'])>0 and o['an_source_steps']==0
   assert job['control_delta']['restored_entries']==['f368','13f12','13f7c','13fea']and job['control_delta']['declared_bytes']==26
  jobs[label]=job;reports[label]=report
 keys=['CPU_full','full_RAM_sha256','full_GPU_state_sha256','full_DSP_state_sha256','video_sha256','navigation','locomotion_state','held_buttons'];differences={k:sum(a[k]!=b[k]for a,b in zip(reports['candidate']['frames'],reports['control']['frames']))for k in keys};pcm={label:dict(bytes=(p:=Path(job['directory'])/'candidate/frontend-PCM.s16le').stat().st_size,sha256=sha(p))for label,job in jobs.items()}
 comparison=dict(candidate_frames=len(reports['candidate']['frames']),control_frames=len(reports['control']['frames']),aligned_frames=min(len(r['frames'])for r in reports.values()),differing_frames=differences,PCM=pcm,PCM_equal=pcm['candidate']==pcm['control'],adaptive_controller_paths_may_differ=True,whole_state_equivalent=False,timing_differences_unresolved=True);save(out/'comparison.json',comparison);bind(out/'comparison.json')
 o=jobs['candidate']['observations'];oc=jobs['control']['observations'];image=Path(jobs['candidate']['directory'])/'candidate/original-emulator-final-frame.png'
 coverage=dict(root_order=['0xf368','0x13f12','0x13f7c','0x13fea'],candidate_native_returns=o['an_returns'],control_original_returns=oc['an_returns'],candidate_max_private_depth=o['an_max_depth'],candidate_minimum_task_headroom=o['an_min_headroom'],context_entries=o['an_context_entries'],context_returns=o['an_context_returns'],shared_chain_movement_returns=o['ach_returns'][0],shared_chain_outdoor_returns=o['ach_virtual_returns'][0],shared_chain_indoor_returns=o['ach_virtual_returns'][1],shared_chain_max_private_depth=o['ach_max_depth'][0],shared_chain_min_task_headroom=o['ach_min_headroom'][0],selector_entries=jobs['candidate']['interior_kind_entries'],selector_successes=jobs['candidate']['interior_kind_successes'],selector_failures=jobs['candidate']['interior_kind_failures'])
 text='''BIWN — FOUR NATIVE NAVIGATION ROOTS / REVIEWED FRESH ROUTES

The new29,876byte source-derived native experiment and its same-layout control
both completed their normal-controller outdoor/interior/outdoor route. Four
navigation public entries are compiled high-level C; reached bodies/returns,
72byte contexts,callee/SP/args andtaskstacks have zero monitor errors. Reached
root counts below are exact; zero entries remain component-only. The shared
movement/collision C chain remains byte-identical and executed natively in both.

The control restores only the4 navigation entries(26declared bytes); installed
unused navigation code,reservation/heap/staging,prior compiled functions and
shared movement/collision remain common. This is not an unmodified game baseline.
Actual changed control bytes are in its delta receipt. Retained native emulator
CPU/GPU/DSP/IRQ/platform/HLE execute both. No host processor replacement claim.

Separate algorithm proofs:6144prototype+6144finalcases/all209sites,fullCPU/SR/banks,
public2MBRAM/ordereddataaccess; no prescribed helpers. Valid stored table targets
only; private frames/installation excluded. Exact monitor440executions/4 decoded
observation negatives;96startup/192heapinitialize,3392native+3392orderedheap/copy,
36capacity requests pass at new floor166340. Fullalgorithm equivalence is not
inferred merely from matching physical CPU to the same C context.

StagingF6C00..FE200,reserve30080,free204,initialheap367808; Atari trailer preserved.
Source:coordinator adaptation of already-recovered portable navigation algorithms;
no localmodel code or newweights adopted. Older inherited local helpers retain
attribution. Indoorcollision and other absent outcomes remain unproved live.
State/video/navigation/PCM differences and adaptive input/timing differences remain.
No full readable game,sameconsole release,physicalconsole or whole-game speedup.

Exact reached coverage:\n'''+json.dumps(coverage,indent=2)+'\n\nFresh pair comparison:\n'+json.dumps(comparison,indent=2)+'\n\nFinal image: '+str(image)+'\n'
 report=out/'review.txt';report.write_text(text);bind(report);bind(Path(__file__))
 result=dict(status='terminal_four_native_navigation_fresh_routes_reviewed',directory=str(out),report=str(report),resident_bytes=29876,candidate_frames=comparison['candidate_frames'],control_frames=comparison['control_frames'],coverage=coverage,live_monitor_pass=True,comparison=comparison,image=str(image),default_preview_promoted=False,whole_game_complete=False,physical_console_verified=False,new_training=False,new_local_code_adopted=False,dependencies_sha256=deps,scope=__doc__);save(out/'protocol.json',result);save(V/'native-navigation-integration-reviewed-current.json',result);print(json.dumps(dict(status=result['status'],coverage=coverage,comparison=comparison)))
if __name__=='__main__':main()
