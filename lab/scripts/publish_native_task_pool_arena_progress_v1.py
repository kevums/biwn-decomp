"""Publish reviewed native stack/initializer work and the actual cold local output trial.
Keep full goal limitations and frozen historical publications intact.
"""
import copy,hashlib,json,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def main():
 now=datetime.now(timezone.utc);out=V/'native-task-pool-arena-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();pointer=V/'current-biwn-latest-publication-current.json';previous=read(pointer);save(out/'previous-publication.json',previous)
 review=read(V/'native-task-pool-arena-integration-reviewed-current.json');build=read(V/'native-task-pool-arena-disc-build-current.json');gate=read(V/'task-pool-arena-final-current.json');easy=read(V/'easy-gpu-arena-recovery-current.json');front=read(V/'gpu-mailbox-arena-frontend-v17-current.json')
 assert review['live_monitor_pass'] and review['resident_code_bytes']==32980 and easy['component_pass'] and easy['new_predictions']==2 and easy['cold_start_test'] and easy['completed_cases']==2512 and front['local_repair_positive_cases']==2512
 model_list=ROOT/'config/current-model-work-sources.json';shutil.copy2(model_list,out/'previous-model-work-sources.json');rows=read(model_list)
 add=[['task-pool-Author-current.json','Task-pool initializer: local Author lost high D0 and loop counter; rejected'],['task-pool-Repair-current.json','Task-pool initializer: local repair rejected; one coordinator uint16_t wrap cast yields chosen hybrid'],['easy-gpu-arena-recovery-current.json','Cold one-click GPU output test: automatic model load, Author rejected, sole repair passes2512current-owner arena cases; no automatic integration']]
 assert not any(x[0]in{y[0]for y in rows}for x in add);save(model_list,add+rows)
 subprocess.run([str(ROOT/'.venv/bin/python3.12'),str(ROOT/'scripts/show_current_model_work_v4.py'),'--no-open'],capture_output=True,text=True,check=True);index=read(V/'current-model-work-index-v4-current.json');assert index['saved_prompt_or_transcript_records']>=81
 deps=dict(previous['dependencies_sha256'])
 def bind(p,h=None):
  p=Path(p).resolve();actual=sha(p);assert h is None or actual==h,str(p)
  if not p.is_relative_to(ROOT)or(p.parent==V and p.name.endswith(('-current.json','-active.json')))or p==model_list:
   target=snap/(hashlib.sha256(str(p).encode()).hexdigest()[:12]+'-'+p.name[-140:]);shutil.copy2(p,target);p=target
  assert str(p)not in deps or deps[str(p)]==actual;deps[str(p)]=actual
 for p,h in review['dependencies_sha256'].items():bind(p,h)
 for p,h in front['source_sha256'].items():bind(p,h)
 for name in ['task-pool-Author-current.json','task-pool-Repair-current.json','easy-gpu-arena-recovery-current.json']:
  data=read(V/name);bind(V/name)
  for path in Path(data['directory']).rglob('*'):
   if path.is_file():bind(path)
 for role in easy['roles']:
  verdict=role['verdict']
  if verdict.get('directory'):
   for path in Path(verdict['directory']).rglob('*'):
    if path.is_file():bind(path)
 for path in [Path(__file__),out/'previous-publication.json',out/'previous-model-work-sources.json',V/'native-task-pool-arena-integration-reviewed-current.json',V/'native-task-pool-arena-disc-build-current.json',V/'gpu-mailbox-arena-frontend-v17-current.json',model_list,Path(index['report']),Path(index['directory'])/'manifest.json',Path(index['source_list_snapshot']),ROOT/'scripts/check_gpu_mailbox_arena_workbench_candidate_v1.py',ROOT/'scripts/try_local_gpu_arena_recovery_v1.py',ROOT/'Try Local GPU Arena Recovery.command',ROOT/'gpu_mailbox_arena_workbench_v1.py',ROOT/'chat_tools_current_v17.py']:bind(path)
 report=ROOT/'reports/Native Task Pool and GPU Stacks.txt';shutil.copy2(review['report'],report);bind(report)
 f=copy.deepcopy(previous['facts']);f['recorded_at']=now.isoformat()
 for field in ['component_verification','layout_verification','gameplay_comparison','frontend_progress']:f['previous_GPU_original_stack_'+field]=copy.deepcopy(f[field])
 f['experimental_build'].update(name='complete task-pool initialization and per-task GPU stacks plus prior native functions',resident_bytes=32980,resident_code_bytes=32980,reserved_bytes=59200,reserved_arena_data_bytes=26112,heap_start='0x16d500',reservation_free_bytes=108,initial_heap_bytes=338688,latest_heap_reduction_bytes=27072,heap_layout_change_in_current_build_bytes=27072,staging_address='0xefa40',derived_disc=build['derived_disc'],derived_disc_sha256=build['derived_disc_sha256'],includes_superseded_GPU_bridge=True)
 f['component_verification']=dict(original_entries=['0xdd40','0xe220','0xe2b8'],initializer_native_bytes=406,GPU_native_bytes=812,pool_final_address_cases=512,GPU_final_address_cases=2512,original_GPU_stack_bytes=10,per_task_arena_slot_bytes=256,per_task_arena_usable_bytes=224,guards_each_end_bytes=16,max_arena_stack_bytes=204,minimum_arena_stack_headroom_bytes=20,task_pool_base='0xc0928',task_count=101,task_stride_bytes=1024,task_header_bytes=38,task_stack_top_offset=1024,arena_slots=102,boot_fallback_slot=101,initializer_USP_and_mode_transition_actual=True,actual_original_helper_entries=['0xe098'],scripted_GPU_replies_in_component_tests=True,pool_live_observer_replays=1024,GPU_live_observer_replays=458,ownership_boundary_cases=1016,startup_cases=96,heap_initializer_cases=192,heap_native_cases=3392,heap_ordered_cases=3392,capacity_cases=36,initializer_source=gate['pool_source'],GPU_source=gate['GPU_source'],authorship='Initializer: local repair plus one coordinator uint16_t cast. GPU: unchanged fresh one-clickv2 repair; new task-owned stack ABI/flags/mode transition supplied by coordinator.',scope='Finite noIRQ component domains and live sampled route. Arbitrary IRQ/fault/concurrency/timing/hardware and complete game source rebuild remain unproved.')
 f['layout_verification'].update(reservation_bytes=59200,heap_floor='0x16d500',initial_heap_bytes=338688,staging_address='0xefa40',staging_clear_bytes=59328,staging_clear_end='0xfe200',current_resident_bytes=32980,current_free_bytes=108,reserved_mutable_arena_data_bytes=26112,arena_data_is_not_recovered_code=True)
 f['gameplay_comparison']=dict(review['comparison'],coverage=review['coverage'],live_monitor_pass=True,all_pending_zero=True,control_scope='OnlyDD40/E220/E2B8entries restored20declaredbytes; same59200reservation/layout/other compiled code.',processors='Retained emulator CPU/GPU/DSP/IRQ/platform/HLE; ordinary adaptive inputs, no guest RAM/register seed or savestate restore.')
 coverage=review['coverage'];f['live_path_coverage']=f"Complete initializer checked once; GPU returns{coverage['candidate_GPU_returns']};all16monitor families pass/pending0. Original stack10bytes;arena{coverage['arena_max_stack_bytes']}/224bytes,slots{coverage['arena_used_slots']},other96arenasunchanged."
 f['local_authorship']['current_disc']='Task initializer: local repair with one coordinator cast. GPU: unchanged earlier one-clickv2 repair, newly viable with coordinator per-task arena ABI. Current cold-output repair passes prototype checks but is not substituted into this disc.'
 f['local_authorship']['current_turn_predictions']=dict(task_pool_Author_seconds=29.65,task_pool_repair_seconds=34.41,task_pool_both_unchanged_proposals_rejected=True,cold_GPU_Author_seconds=easy['roles'][0]['seconds'],cold_GPU_repair_seconds=easy['roles'][1]['seconds'],cold_GPU_Author_rejected=True,cold_GPU_repair_component_pass=True,new_weights=False,quality_generalization_demonstrated=False)
 f['task_pool_arena_progress']=dict(status=review['status'],report=str(report),review=review['report'],coverage=coverage,earlier_stack_rejection_reclassified_as_ABI_fix_not_weight_gain=True)
 f['frontend_progress']=dict(status=front['status'],entrypoint=front['entrypoint'],tool_count=18,new_fixed_function_task='gpu_mailbox',arena_cases=2512,semantic_negative_rejected=True,one_click_launcher=str(ROOT/'Try Local GPU Arena Recovery.command'),cold_start_test=True,automatic_model_setup_seconds=easy['model_setup_seconds'],Author_then_one_repair_pass=True,new_predictions=2,automatic_source_promotion=False,native_Chat_display_verified=False,transcript=str(Path(easy['directory'])/'prompts-and-responses.txt'))
 f['migration_progress'].update(live_frontend_entrypoint_version='v17',latest_live_resident_bytes=32980,new_GPU_frontend_or_disc_copied_to_cold_package=False)
 f['checked_current_summary']='Latest reviewed experimental disc:32980code bytes,26112separate arena-data bytes,59200total reservation;heap16D500/stagingEFA40,trailerpreserved. Complete task initializer and per-task GPU stacks integrated. Freshcandidate24628/control24631frames both returnedoutdoors,all16monitorfamiliespass/pending0;17512GPUreturnschecked. Arena204/224bytes;10originalstackbytes. Freshcoldlocalmodel loadsautomatically in7.61s;Authorrejected,sole repairpasses2512cases. No newweights/generalizationclaim. Common78809600PCMbytes and alignedDSPstatesmatch;video/state/timingdiffer. Completegame/source-consolerebuild,hardware,nativeLMChat,Adreliability andlatestmigration unfinished.'
 f.update(report=str(report),component_proof=build['final_component_gate'],prompts_and_responses=index['report'],new_training=False,new_training_scope='Four new base-model predictions: two task-pool proposals rejected as-is; fresh cold GPU Author rejected and repair passes prototype cases. No optimizer update or held-out gain.',whole_game_complete=False,physical_console_verified=False,native_Chat_verified=False,default_promoted=False)
 f['remaining_work']=['Continue complete readable game/callgraph and same-console source rebuild; originalGPU/DSP/services and unobserved paths remain.','Broaden task-owned stack/IRQ/concurrency/timing/resource coverage; one fresh route is finite evidence.','Continue easy local output reliability beyond this exposed development example; cold repair pass is not model training or held-out generalization.','Verify native LM Studio Chat prompt/tool display when UI access works; no unlock requests.','Improve Advertising research/education/reviewer reliability; trained option remains loadable without demonstrated quality gain.','Migrate and cold-test latestv17/32980workflows; frozen movedpackage remainsv10/30036.']
 for p,h in deps.items():assert sha(p)==h,p
 result=dict(previous,directory=str(out),recorded_at=now.isoformat(),facts=f,dependencies_sha256=deps,scope=__doc__+' Full four-part goal active; interactive preview unchanged.');save(out/'publication.json',result);save(pointer,result)
 state=dict(status='terminal_native_task_pool_arena_progress_published_pending_actual_MCP_read',directory=str(out),resident_code_bytes=32980,saved_prompt_or_transcript_records=index['saved_prompt_or_transcript_records'],bound_files=len(deps));save(out/'protocol.json',state);save(V/'native-task-pool-arena-status-publication-current.json',state);print(state)
if __name__=='__main__':main()
