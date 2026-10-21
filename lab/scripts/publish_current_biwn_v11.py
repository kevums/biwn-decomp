"""Publish the reviewed21080experimental disc; retain older-job applicability."""
import hashlib,json,os,shutil
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def read(p):return json.loads(Path(p).read_text())
def main():
 v=ROOT/'verification';rp=v/'actor-initialize-integration-reviewed-current.json';review=read(rp);assert review['status']=='terminal_actor_initialize_integrated_two_routes_reviewed'and review['live_monitor_pass'];bp=Path(review['build']);build=read(bp);assert sha(bp)==review['build_sha256'];pathp=v/'actor-initialize-live-paths-current.json';paths=read(pathp);parentp=v/'native-geometry-scan-corrected-live-reviewed-current.json';parent=read(parentp);previousp=v/'current-biwn-latest-publication-current.json';previous=read(previousp);assert previous['facts']['experimental_build']['resident_bytes']==19460
 now=datetime.now(timezone.utc);out=v/'current-biwn-latest-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();deps={};aliases={}
 def bind(path,h=None):
  p=Path(path).resolve();assert p.is_relative_to(ROOT);actual=sha(p);assert h is None or h==actual,p
  if p.name.endswith(('-current.json','-active.json')):
   target=snap/(hashlib.sha256(str(p).encode()).hexdigest()[:12]+'-'+p.name);shutil.copy2(p,target);aliases[str(p)]=str(target);p=target
  deps[str(p)]=actual
 for data in [review,parent]:
  for p,h in data['dependencies_sha256'].items():bind(p,h)
 for p,h in paths['source_sha256'].items():bind(p,h)
 for p in [rp,bp,pathp,parentp,Path(__file__),ROOT/'current_biwn_evidence_v7.py',ROOT/'chat_tools_current_v7.py',ROOT/'scripts/ask_biwn_current_status_v12.py']:bind(p)
 coverage=('Initializer134DCcompleted12live returns and16actual helper calls; dispatcher13AE0completed13returns,12actor routes/1sprite route/0fullpool returns. '
           'These are completed calls/routing, not booleanD0success classifications. Entry modes1and2occur3and9times. Original table yields3distinct task callbacktargets; '
           '12othercallbacktargets,invalid dispatch/ID and no-geometry mode paths remain component-only. The helper-type partition is derived from entry/table data and aggregate count,not directly instrumented per-type counters. '
           'Inherited10520selector14actor successes/0failures;105DA0sprite successes/1skipped failure. Actor failures,sprite successes and non-skipped misses remain component-only.')
 summary=('Latest published experimental disc:21080resident bytes in24512reservation,3432free; heap164D80with373376initialheapbytes after4032byte capacity reduction. '
          'Coordinator134DCinitializer1620bytes passes1024fullABIcases/all148sites atfinal1639C4;96fullpayloadstartup cases pass. '
          'Relocatedallocator/compactor/nativecopy-blitter3392cases and3392orderedcases,192heapinitializer cases and36freshconstructor capacity requests pass. '
          'Final-address856dispatcher and1024initializer original/C roots also pass read-onlycontext checks;3760executions/four corruption controls. '
          'Fresh retained-native-emulator candidate29790frames/control29777bothreturnoutdoors. '+coverage+
          ' Zero ABI/context/taskstack errors;13parent and16initializer savedcontext checks pass; maxnested600private bytes/min182taskheadroom on observed paths. '
          'Deeper native frames legitimately skip parentcontext; actual bytes remain intact. Only134DCentry restored in common enlarged-layout control. '
          'Video,PCM,state/navigation differ; timing/media equivalence remains unresolved and older scanner media limits persist. '
          'Current disc code/ABI/layout/verification is coordinator work; earlier accepted localfunctions retain attribution. Separate local low-reasoning repair spent5999reasoning tokens '
          'and273.37seconds with zero finalC under6000token budget; compiler rejected it and same-weight Reviewer reported noissues. Two predictions,noadoption/weights/defaultprofilechange. '
          'Five named Cprocessorjobs are terminal on older16872/17084/17812/18270/18888discs; noneapplies to21080. NativeChat remains unverified; existing interactive preview unchanged. '
          'Full readable game/originalconsole rebuild,remaining137E0/game logic,broaderstack/resourcepaths,Advertising reliability and fullmigration remain unfinished.')
 facts=dict(project='Black Ice White Noise, Atari Jaguar CD',recorded_at=now.isoformat(),checked_current_summary=summary,
  experimental_build=dict(name='native134DCactor initializer with native13AE0dispatcher and enlarged checked layout',resident_bytes=21080,reserved_bytes=24512,heap_start='0x164d80',reservation_free_bytes=3432,initial_heap_bytes=373376,initial_heap_reduction_bytes=4032,derived_disc=build['derived_disc'],derived_disc_sha256=build['derived_disc_sha256']),
  component_verification=dict(original_entries=['0x134dc'],native_bytes=1620,stable_cases=1024,changing_read_cases=0,original_instruction_coverage=[148,148],startup_cases=96,private_stack_bytes=564,source=build['source'],scope='FullCPU/SR/banks/public2MBRAM/ordered bus and helperentryCPU/SR/SP/args. Finaljoint/context matrix856dispatcher+1024initializer original/C pairs; four leaf services prescribed. Actual real helpers separately exercised live. No arbitrary faults/modified table/IRQtiming/general concurrent path claim.'),
  layout_verification=dict(reservation_bytes=24512,heap_floor='0x164d80',relocated_heap_operands=7,loader_count_WORD='0x2fdf',staging_clear_bytes=24576,staging_remaining_bytes=24,heap_initialize_cases=192,heap_native_blitter_cases=3392,heap_ordered_cases=3392,fresh_heap_capacity_request_cases=36),
  live_path_coverage=coverage,
  gameplay_comparison=dict(candidate_frames=29790,control_frames=29777,compared_prefix_frames=29777,initializer_completed_returns=12,actual_helper_calls=16,compiled_dispatcher_calls=13,actor_routed_calls=12,sprite_routed_calls=1,pool_exhaustion_returns=0,live_monitor_pass=True,parent_context_checks=13,initializer_context_checks=16,context_corruptions=0,maximum_observed_nested_private_depth=600,minimum_task_headroom=182,video_equal=False,navigation_equal=False,PCM_byte_equal=False,PCM_bytes=[95328000,95286400],all_field_difference_counts=review['same_layout_differences'],frame_counts_equal=False,exact_whole_state_equivalence=False,timing_disagreement_unresolved=True,control_scope='Only8bytes134DCentry restored; enlarged layout/unused code/native13AE0/prior functions common,not unmodifiedgame',processors='Retained native emulator CPU/GPU/DSP/IRQ/platform services'),
  initializer_live_entry_paths=dict(entry_modes={'1':3,'2':9},original_table_task_callback_targets={'0xf4d8':2,'0x15140':1,'0xedc4':1},finished_table_cases=8,other_callback_targets_component_only=12,helper_partition_derived=True,report=str(Path(paths['directory'])/'protocol.json')),
  inherited_parent_limits=dict(build_resident_bytes=17812,original_entry_comparison='Scanner102C4compiled versus original entry',video_equal=False,PCM_byte_equal=False,unresolved_timing_state_media_disagreement=True,latest_function_control_does_not_resolve_parent=True,report=parent['report']),
  local_authorship=dict(actual_model_calls_for_current_disc_code=0,current_disc='Coordinator134DC/13AE0source,ABI,layout,fixtures,monitors,integration',accepted_unchanged_local_output=False,accepted_function_entries=[],accepted_C='Coordinatorreference',inherited_functions='Parent10520/105DAkernel remains accepted unedited localrepair; other historical functions retain attribution.',separate_low_reasoning_trial=review['local_profile_trial'],independent_review=False,same_weight_reviews_unreliable=True,new_weight_training=False),
  report=review['report'],component_proof=build['component_gate'],prompts_and_responses=str(Path(review['local_profile_trial']['directory'])/'prompts-and-responses.txt'),whole_game_complete=False,physical_console_verified=False,whole_game_speedup_demonstrated=False,new_training=False,default_promoted=False,native_Chat_verified=False,
  remaining_work=['Recover/integrate remaining137E0and actual game logic/interfaces','Broaden unexercised callback/resource/stack paths and resolve timing/media differences','Complete readable game/original-console source rebuild','Verify current native LMStudioChat;SDK/CLIworks','Advertising research/teaching reliability and effective domain-adaptation evaluation','Complete workbench migration/future256GBconfiguration preparation'])
 result=dict(status='terminal_native_geometry_status_v2_published',schema_version=2,directory=str(out),recorded_at=now.isoformat(),facts=facts,dependencies_sha256=deps,historical_pointer_snapshots=aliases,scope='Reviewed21080experimental native disc. Five older separately identified processor jobs added at read time; no preview/default promotion.')
 save(out/'publication.json',result);shutil.copy2(previousp,out/'previous-publication.json');temporary=v/'.current-biwn-publication-v11.tmp.json';save(temporary,result);os.replace(temporary,previousp);print(json.dumps(dict(status=result['status'],resident_bytes=21080,bound_files=len(deps),preview_changed=False)))

if __name__=='__main__':main()
