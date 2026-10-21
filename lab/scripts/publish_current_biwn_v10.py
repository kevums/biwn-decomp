"""Publish reviewed19460gap320facts through the unchanged schema2MCP interface."""
import hashlib,json,os,shutil
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def read(p):return json.loads(Path(p).read_text())
def main():
 v=ROOT/'verification';rp=v/'actor-gap320-and-initializer-reviewed-current.json';review=read(rp);assert review['status']=='terminal_gap320_live_and_initializer_components_reviewed'and review['live_monitor_pass']and review['min_observed_context_clearance']==70
 bp=Path(review['build']);build=read(bp);assert sha(bp)==review['build_sha256'];gate=read(build['component_gate']);assert gate['cases']==856 and build['linked_component_bytes']==19460 and build['component_bytes']==20480
 parentp=v/'native-geometry-scan-corrected-live-reviewed-current.json';parent=read(parentp);assert not parent['PCM_equal']
 oldCp=v/'interior-C-processors-reviewed-current.json';oldC=read(oldCp);assert oldC['status']=='terminal_interior_C_processors_independently_reviewed_equal'and oldC['tested_resident_bytes']==18888
 previousp=v/'current-biwn-latest-publication-current.json';previous=read(previousp);assert previous['facts']['experimental_build']['resident_bytes']==18888
 now=datetime.now(timezone.utc);out=v/'current-biwn-latest-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();deps={};aliases={}
 def bind(path,h=None):
  p=Path(path).resolve();assert p.is_relative_to(ROOT);actual=sha(p);assert h is None or h==actual,p
  if p.name.endswith(('-current.json','-active.json')):
   target=snap/(hashlib.sha256(str(p).encode()).hexdigest()[:12]+'-'+p.name);shutil.copy2(p,target);aliases[str(p)]=str(target);p=target
  deps[str(p)]=actual
 for obj in [review,parent]:
  for p,h in obj['dependencies_sha256'].items():bind(p,h)
 for p,h in oldC['source_sha256'].items():bind(p,h)
 for p in [rp,bp,parentp,oldCp,Path(__file__),ROOT/'current_biwn_evidence_v7.py',ROOT/'chat_tools_current_v7.py',ROOT/'scripts/ask_biwn_current_status_v12.py']:bind(p)
 coverage=('Dispatcher13AE0completed13live child/root returns:12actor routes and1sprite route,0full-pool returns. '
           'These are routing/completion counts, not boolean success/failureD0classifications. Full-pool return behavior remains component-only. '
           'Inherited selectors10520/105DAstillhave14actor successes/0actor failures and0sprite successes/1sprite skipped failure; '
           'actor failures, sprite successes and sprite non-skipped misses remain component-only.')
 summary=('Latest published experimental disc:19460resident bytes in unchanged20480reserve,1020free,heap163DC0. '
          'Coordinator13AE0dispatcher572bytes/private gap320passed856fullABIcases/all38sites and96startup. '
          'Fresh retained-native-emulator candidate24983frames/control24996bothreturnoutdoors. '+coverage+
          ' Zero live ABI/context/task-stack errors; actual descendants194bytes belowrootSPleave70context bytes clear, '
          'candidate392private depth/390minimumtaskheadroom on these13calls. Widergap preserves priorvariantvideo/audio/navigation; '
          'fresh original-dispatcher-entry control stilldiffers in video/PCM/state/navigation, so timing/media equivalence remains unresolved. '
          'Original preview remains unchanged. No new localcodepredictions/weights: prior localdispatcherAuthorfailed, currentbody/ABI/integrationcoordinator; '
          'earlier accepted localfunctions retain attribution. Separately, native134DCinitializer1620bytes passes1024cases/all148sites; '
          'joint13AE0+134DCprototype856cases/600private stack passes, but initializer is NOT in the disc and needs600additional bytes. '
          'Five named Cprocessorjobs are terminal on olderidentifieddiscs only;18888jobmatches24996frames/8fields/fullPCM/fullobserver, '
          'noneapplies to19460gap320. Fullreadablegame/consolework, sourceintegration, currentnativeChat,Advertising reliability and migration remain unfinished.')
 facts=dict(project='Black Ice White Noise, Atari Jaguar CD',recorded_at=now.isoformat(),checked_current_summary=summary,
  experimental_build=dict(name='native13AE0dispatcher with320byte private gap',resident_bytes=19460,reserved_bytes=20480,heap_start=hex(build['heap_start']),reservation_free_bytes=1020,derived_disc=build['derived_disc'],derived_disc_sha256=build['derived_disc_sha256']),
  component_verification=dict(original_entries=['0x13ae0'],native_bytes=572,stable_cases=856,changing_read_cases=0,original_instruction_coverage=[38,38],startup_cases=96,private_gap=320,private_stack_bytes=392,source=gate['source'],scope='Full returnedCPU/SR/banks/public2MBRAM/ordered bus plus real original child/helper entryCPU/SR/SP/args. Four leaf helpers prescribed in component proof. Original child algorithms remain; actual external helpers exercised in live13calls. Private code/frames and returnPC exclusions; no arbitraryfault/modifiedtable/IRQtiming proof.'),
  live_path_coverage=coverage,
  gameplay_comparison=dict(candidate_frames=24983,control_frames=24996,compared_prefix_frames=24983,compiled_dispatcher_calls=13,actor_routed_calls=12,sprite_routed_calls=1,pool_exhaustion_returns=0,root_completed_returns=13,live_monitor_pass=True,context_collisions=0,minimum_observed_context_clearance=70,maximum_observed_descendant_depth=194,max_private_stack=392,min_task_headroom=390,video_equal=False,navigation_equal=False,PCM_byte_equal=False,frame_counts_equal=False,all_field_difference_counts=review['same_layout_differences'],exact_whole_state_equivalence=False,timing_disagreement_unresolved=True,control_scope='Only8bytes13AE0entry restored; preceding compiled functions/layout/newunusedcode remain; not unmodifiedgame',processors='Retained native emulator CPU/GPU/DSP/IRQ/platform services'),
  gap_widening_comparison=dict(previous_gap=256,current_gap=320,previous_observed_clearance_estimate=6,current_measured_clearance=70,video_equal=True,PCM_byte_equal=True,navigation_equal=True,CPU_different_frames=[1,0],full_RAM_different_frames=[24810,24823],scope='Each variant compared only to its corresponding previous256gap candidate/control. Not equality to original dispatcher control or general descendant stack bound.'),
  inherited_parent_limits=dict(build_resident_bytes=17812,original_entry_comparison='Scanner102C4compiled versus original entry',video_equal=False,PCM_byte_equal=False,unresolved_timing_state_media_disagreement=True,latest_function_control_does_not_resolve_parent=True,report=parent['report']),
  local_authorship=dict(actual_model_calls=0,current_variant='Coordinator Cbody/ABI/layout/fixtures/oracle/integration',accepted_unchanged_local_output=False,accepted_function_entries=[],accepted_C='Coordinatorreference',prior_dispatcher_trial_calls=2,prior_raw_dispatcher_compile_pass=False,prior_compile_only_diagnostic_semantic_pass=False,independent_review=False,same_weight_reviews_unreliable=True,inherited_functions='Parent10520/105DAkernel remains accepted unedited localrepair; other parent functions retain their own historical attributions.',new_weight_training=False),
  next_source_component=dict(entry='0x134dc',native_bytes=1620,component_cases=1024,original_sites=148,private_depth=564,joint_with_native_dispatcher_cases=856,joint_private_depth=600,disc_integrated=False,additional_reserve_needed_before_alignment=600,report=review['report'],limits='Real original10520child executes; geometry102C4/taskDF6Cscripted in component proof. Needs heap/layout and real nested native-frame/helper/canary/gameplay integration.'),
  older_18888_C_processor_result=dict(terminal_equal=True,frames=24996,eight_fields_equal=True,PCM_byte_equal=True,full_observer_equal=True,applies_to_latest_published_disc=False,report=oldC['report']),
  report=review['report'],component_proof=build['component_gate'],prompts_and_responses=str(Path(read(v/'local-native-actor-dispatch-current.json')['directory'])/'prompts-and-responses.txt'),whole_game_complete=False,physical_console_verified=False,whole_game_speedup_demonstrated=False,new_training=False,default_promoted=False,native_Chat_verified=False,
  remaining_work=['Integrate134DCand remaining actor/sprite C interfaces with explicit layout/real-frame/helper validation','Broaden unexercisedpaths and resolve timing/state/media differences','Complete readable game/original-console rebuild','Verify current native LMStudioChat;SDK/CLIworks','Advertising teaching/source reliability and adaptation quality','Complete workbench migration/future256GBpreparation'])
 result=dict(status='terminal_native_geometry_status_v2_published',schema_version=2,directory=str(out),recorded_at=now.isoformat(),facts=facts,dependencies_sha256=deps,historical_pointer_snapshots=aliases,scope='Reviewed19460gap320native experimentalbuild and separate nonintegrated134DCcomponent. Five named olderprocessorjobs added at read time. Defaultpreviewunchanged.')
 save(out/'publication.json',result);shutil.copy2(previousp,out/'previous-publication.json');temporary=v/'.current-biwn-publication-v10.tmp.json';save(temporary,result);os.replace(temporary,previousp);print(json.dumps(dict(status=result['status'],resident_bytes=19460,bound_files=len(deps),preview_changed=False)))

if __name__=='__main__':main()
