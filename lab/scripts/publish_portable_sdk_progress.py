"""Publish recorded portability evidence without changing game build/preview."""
import copy,hashlib,json,os,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):
 with Path(p).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def main():
 review=read(V/'portable-sdk-workbench-reviewed-current.json');p=Path(review['package']);pointer=V/'current-biwn-latest-publication-current.json';prior=read(pointer);out=V/'portable-sdk-status-publication'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();save(out/'previous-publication.json',prior)
 deps=dict(prior['dependencies_sha256'])
 def bind(path):
  path=Path(path).resolve();digest=sha(path)
  mutable=not path.is_relative_to(ROOT)or(path.parent==V and path.name.endswith(('-current.json','-active.json')))or path==ROOT/'reports/Portable Setup Test.txt'
  if mutable:
   target=snap/(hashlib.sha256(str(path).encode()).hexdigest()[:12]+'-'+path.name[-140:]);shutil.copy2(path,target);path=target
  assert str(path)not in deps or deps[str(path)]==digest,str(path);deps[str(path)]=digest
 for f in [Path(__file__),V/'portable-sdk-workbench-reviewed-current.json',V/'portable-sdk-physical-move-current.json',V/'portable-native-build-current.json',V/'portable-sdk-model-integrity-current.json',V/'portable-training-update-current.json',V/'portable-assistant-launchers-current.json',V/'portable-advertising-launcher-current.json',p/'portable-secondary-test-current.json',p/'portable-boundaries-current.json',p/'model-registration-receipt.json',p/'portable-model-bindings.json',p/'restore-layout.json',p/'READ ME FIRST.txt',p/'workbench/portable_ask.py',p/'workbench/portable_models.py',p/'runtime/portable_runtime_paths_v5.py']:
  bind(f)
 for directory in [Path(review['directory']),Path(review['source_records']['training']['directory']),Path(review['source_records']['integrity']['directory'])]:
  for f in directory.rglob('*'):
   if f.is_file():bind(f)
 for name in ['portable-game-inference-current.json','portable-advertising-reviewer-inference-current.json','portable-advertising-research-inference-current.json']:
  state=read(V/name);bind(V/name)
  for f in Path(state['directory']).glob('*'):
   if f.is_file():bind(f)
 f=copy.deepcopy(prior['facts']);old=f['migration_progress'];f['previous_cold_migration_progress']=old
 f['migration_progress']=dict(package=str(p),same_host_different_root=True,physical_move_verified=True,registered_MCP_servers=4,main_registered_tools=18,total_registered_tools=25,main_tested_tool_kinds=7,secondary_tested_tool_kinds=3,tested_tool_kinds=10,main_actual_calls=8,secondary_read_calls=3,boundary_controls=5,origin_read_denials_for_actual_SDK_clients=0,origin_fallback_allowed=False,copied_dependency_files_verified=10009,model_files_copied=39,model_weight_shards_verified=10,copied_model_final_responses=3,copied_model_context_length=32768,SDK_control_client='CopiedpackagePython/SDK;hostLMStudioAPIserviceexternal',copied_SDK_inference_verified=True,three_actual_assistant_launchers_verified=True,full_CLI_workflows_verified=False,all_tools_behavior_verified=False,full_workbench_restored=False,copied_m68k_toolchain_build_verified=True,recompiled_native_component_bytes=1588,recompiled_native_component_SHA256=review['native_binary_sha256'],training_pipeline_one_update_verified=True,training_updates=1,training_actual_padded_tokens=225,training_adapter_promoted=False,full_training_workflow_restored=False,current_daily_restored=True,current_daily_context_length=32768,native_Chat_verified=False,off_machine_restore_verified=False,future_hardware_verified=False,new_source_section_frontend_copied_to_cold_package=True,cold_package_frontend_entrypoint_version='v10 plusportablev5pathadapter',canonical_publication_snapshot_resident_bytes=30036,report=review['review'],quick_start=review['guide'],quality_gain_demonstrated=False,trained_Reviewer_timing_omission=True,base_beneficiary_framing_omission=True,scope='Recorded same-host moved-package tests:copiedSDK/threeassistantlaunchers/selectedmodels/sourcecomponentbuild andoneactualtrainingupdate. Tenof25toolkinds,notalllegacylaunchers/fullgame/fulltraining/futurehardware. Historicalreceiptsunmodified;in-memorypathadapterguardisnotageneralsecuritysandbox.')
 f['portable_model_output_progress']=dict(actual_predictions=3,roles=['GameAssistant','AdvertisingResearchAssistant','trainedSourceReviewer'],trained_Reviewer_timing_omission=True,base_beneficiary_framing_omission=True,quality_gain_demonstrated=False,source_heldout=False,report=review['review'],saved_transcript_records=71)
 f['new_training']=True;f['new_training_scope']='One unpromoted copied-pipeline migration test update on existing reviewedgame-source data;noqualitygain or defaultpromotion.';f['recorded_at']=datetime.now(timezone.utc).isoformat()
 f['remaining_work'][-1]='Complete remainingportableworkflows/legacytools/nativeChat/onboarding andactualfuture256GBacceptance. CopiedSDK/three launchers/nativecomponentbuild andone trainingupdate nowverifiedwithin recordedscopes.'
 result=dict(prior,directory=str(out),recorded_at=f['recorded_at'],facts=f,dependencies_sha256=deps,scope=__doc__+' ThreeactualSDKpredictionsandoneunpromotedtrainingupdate;fullgoalactive.')
 save(out/'publication.json',result);save(pointer,result)
 # Overlay only new verified publication dependencies, keeping copied raw files.
 backups=p/'backups'/('publication-'+out.name)
 for name,digest in deps.items():
  source=Path(name);assert source.is_relative_to(ROOT)and sha(source)==digest,str(source);target=p/'workbench'/source.relative_to(ROOT)
  if target.is_file()and sha(target)==digest:continue
  if target.exists()or target.is_symlink():
   backup=backups/source.relative_to(ROOT);backup.parent.mkdir(parents=True,exist_ok=True);os.rename(target,backup)
  target.parent.mkdir(parents=True,exist_ok=True);subprocess.run(['/bin/cp','-cL',str(source),str(target)],check=True);assert sha(target)==digest
 target=p/'workbench/verification/current-biwn-latest-publication-current.json';backup=backups/'current-biwn-latest-publication-current.json';backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,backup);shutil.copy2(pointer,target)
 state=dict(status='terminal_portability_progress_published_pending_actual_MCP_read',directory=str(out),package=str(p),publication=str(out/'publication.json'),bound_files=len(deps),new_predictions=0,new_training=0);save(out/'protocol.json',state);save(V/'portable-sdk-status-publication-current.json',state);print(json.dumps(state))
if __name__=='__main__':main()
