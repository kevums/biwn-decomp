"""Freeze this finite goal turn without claiming the four-part objective complete."""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification';ND=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
def read(p):return json.loads(Path(p).read_text())
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def main():
 stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out=V/'goal-continuation-handoffs'/('gpu-mailbox-'+stamp);out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir();print(out,flush=True)
 prior=read(V/'goal-continuation-current.json');save(out/'previous-handoff.json',prior);old_integrity=read(V/'native-direction-turn-integrity-current.json');save(out/'previous-integrity.json',old_integrity);deps=dict(old_integrity['dependencies_sha256'])
 for index,(p,h)in enumerate(list(deps.items())):
  assert sha(p)==h,('Prior immutable changed',p)
  if index%400==0:print('Prior bindings checked',index,'/',len(deps),flush=True)
 def bind(p,h=None,mutable=False):
  p=Path(p).resolve();actual=sha(p);assert h is None or actual==h,str(p)
  if mutable or not p.is_relative_to(ROOT)or(p.parent==V and p.name.endswith(('-current.json','-active.json'))):
   target=snap/(hashlib.sha256(str(p).encode()).hexdigest()[:16]+'-'+p.name[-130:]);shutil.copy2(p,target);p=target
  assert str(p)not in deps or deps[str(p)]==actual,('Conflicting binding',str(p));deps[str(p)]=actual
 for p in [Path(__file__),out/'previous-handoff.json',out/'previous-integrity.json']:bind(p)
 # New source versions and immutable run/build records; no prior files edited.
 for pattern in ['*gpu*mailbox*','*gpu_recovery*']:
  for p in(ROOT/'scripts').glob(pattern):
   if p.is_file():bind(p)
 for p in ND.glob('*gpu-mailbox*'):
  if p.is_file():bind(p)
 for pattern in ['gpu_mailbox_workbench*.py','chat_tools_current_v1[2-6].py']:
  for p in ROOT.glob(pattern):bind(p)
 for base,patterns in [(V,['*gpu*mailbox*']),(ROOT/'runs',['*gpu-mailbox*','easy-gpu-recovery-*']),(ROOT/'builds',['BIWN-native-gpu-mailbox*']),(ROOT/'training/game/development-failures',['gpu-mailbox-*'])]:
  for pattern in patterns:
   for folder in base.glob(pattern):
    if folder.is_file():bind(folder)
    elif folder.is_dir():
     for p in folder.rglob('*'):
      if p.is_file()and '__pycache__'not in p.parts:bind(p)
 for p in(ROOT/'reports/model-work-index').glob('*'):
  if p.name.startswith('20261019T135611'):
   for f in p.iterdir():
    if f.is_file():bind(f)
 for name in ['Try Local GPU Recovery.command','reports/Native GPU Commands.txt','BIWN Latest Work.txt','BIWN Latest Result.txt','config/current-model-work-sources.json']:bind(ROOT/name,mutable=True)
 runtime=Path('/Users/kevin/.lmstudio/local-ai-lab')
 for pattern in ['gpu_mailbox_workbench*.py','chat_tools_current_v1[2-6].py']:
  for p in runtime.glob(pattern):bind(p)
 bind(Path.home()/'.lmstudio/mcp.json',mutable=True)
 pub=read(V/'current-biwn-latest-publication-current.json');assert pub['facts']['experimental_build']['resident_bytes']==31758
 for p,h in pub['dependencies_sha256'].items():bind(p,h)
 bind(V/'current-biwn-latest-publication-current.json')
 jobs=[]
 for prefix in ['native-gpu-mailbox-quiescent-','native-gpu-mailbox-v2-quiescent-','native-gpu-mailbox-v3-quiescent-','native-gpu-mailbox-diagnostic-','native-gpu-mailbox-v2-diagnostic-']:
  for label in ['candidate','control']:
   p=V/(prefix+label+'-current.json')
   if not p.exists():continue
   data=read(p);observations=[]
   for key in ['pid','child_pid']:
    pid=data.get(key)
    if not pid:continue
    command=subprocess.run(['ps','-p',str(pid),'-o','command='],capture_output=True,text=True).stdout.strip();matching=bool(command and(str(data['directory'])in command or'native_gpu_mailbox'in command));assert not matching,('Worker still live',pid,command);observations.append(dict(pid=pid,matching_worker_live=False,handle_missing=not bool(command)))
   assert data['status'].startswith('terminal_');jobs.append(dict(pointer=p.name,status=data['status'],process_observations=observations))
 for name in ['gpu-mailbox-native-Author-current.json','gpu-mailbox-native-Repair-current.json','easy-gpu-recovery-current.json','easy-gpu-recovery-first-reviewed-current.json']:
  data=read(V/name);assert data['status'].startswith('terminal_');pid=data.get('pid');command=subprocess.run(['ps','-p',str(pid or 0),'-o','command='],capture_output=True,text=True).stdout.strip();assert not(command and('gpu_mailbox'in command or'gpu_recovery'in command));jobs.append(dict(pointer=name,status=data['status'],pid=pid,matching_worker_live=False))
 ps=subprocess.run(['ps','-p','233,235','-o','pid=,command='],capture_output=True,text=True).stdout;save(out/'preview-processes.json',dict(observed=ps,operated_or_restarted=False,run_keys='C+Up;Ppauses/resumes'));bind(out/'preview-processes.json')
 model=subprocess.run([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],capture_output=True,text=True,check=True);(out/'loaded-models.json').write_text(model.stdout);catalog=json.loads(model.stdout);assert any(x['identifier']=='advertising-scholar'and x['contextLength']==32768 and x['parallel']==1 for x in catalog);bind(out/'loaded-models.json')
 for name in ['configured-gpu-mailbox-final-frontend-current.json','gpu-mailbox-final-default-build-current.json','gpu-mailbox-readable-report-current.json','gpu-mailbox-development-SFT-current.json','current-model-work-index-v4-current.json']:bind(V/name)
 state=dict(prior);state.update(status='active_native_GPU_wrappers_integrated_live_checked_easy_model_reliability_remains',recorded_at=datetime.now(timezone.utc).isoformat(),previous_turn_classification='Progress: prior native direction30834bytebuild/component/live evidence and moved portable SDK workflows inspected; no prior finite work restarted.',this_turn_classification='Progress: complete E220/E2B8 local repaired C body and coordinator124byte ABI/inline profile;2492prototype/final each/current320byte ancestor controls,96startup/192heapinit/3392native+orderedheap/36capacity/232observerexecutions;31758disc fresh24640/24645routes/allmonitors/pending0/17763GPUwrapperreturns. Sixlocalpredictions,4freshsingle-clickattemptsrejected;77savedrecords;v16task/verifier/currentMCPandAdsource9/20verified.',goal_complete=False,previous_handoff=str(out/'previous-handoff.json'),latest_published_live_build_resident_bytes=31758,latest_built_disc_resident_bytes=31758,latest_built_disc_game_frames=24640,latest_native_GPU_build=str(V/'native-gpu-mailbox-disc-build-current.json'),latest_native_GPU_review=str(V/'native-gpu-mailbox-v3-integration-reviewed-current.json'),latest_integrity=str(out/'integrity.json'),latest_local_status_delivery=str(V/'configured-gpu-mailbox-final-frontend-current.json'),latest_model_work_index=str(V/'current-model-work-index-v4-current.json'),finite_jobs=[],finite_jobs_pending=0,completed_finite_jobs=jobs,native_Chat_verified=False,full_goal_not_complete=True,final_integrity_unique_files=len(deps)+1)
 state['full_goal_requirements'][0].update(state='incomplete',evidence=str(ROOT/'reports/Native GPU Commands.txt'),remaining='Native MCPv16/18tools+fixed GPU task/verifier installed.6actualpredictions;selectedmanualrepairpasses;freshone-clickAuthor/repairsequencesstillrejected. NativeChatdisplay/tooladoption notverified;autoloader/coldfirstuseandactionablestackfeedbackneedwork.')
 state['full_goal_requirements'][1].update(state='incomplete',evidence=str(V/'native-gpu-mailbox-v3-integration-reviewed-current.json'),remaining='31758nativebytes including922byteE220/E2B8component;17763checkedlivereturns/allmonitorspass. ActualE098/E588/GPU/DSP/servicesandfullsource/callgraph/same-console source build/unobservedpaths remain. Video/state/input/timing differ;2byte finite ancestor clearance needs stronger ABI design.')
 state['full_goal_requirements'][2].update(evidence=str(V/'configured-gpu-mailbox-final-frontend-current.json'),remaining='Existing optional trainedstep8Reviewerready,base daily27B/32Kavailable;actualAdPDF9/20retrievalpreserved. Advertisinginterpretation/teaching/reviewerreliability remains;no newAdtrainingorqualitygain.')
 state['full_goal_requirements'][3].update(remaining='Frozen movedpackage stillv10/30036;currentlivev16/31758notcopied/retestedthere. Latestbootstrap/workflows/nativeChat/onboarding/cold model startupandfuture256GBacceptance preparation remain. Actualfuturehardwarebenchmark is deferred,not a headless blocker.')
 state['local_model_work_this_continuation']=dict(actual_prediction_rounds=6,roles=['Author','informedrepair','freshAuthor','informedrepair','clarifiedfreshAuthor','informedrepair'],seconds=[79.66,36.13,32.10,30.49,30.68,37.14],new_training=False,new_weights=False,selected_manual_repair_C_adopted=True,fresh_one_click_candidates_adopted=False,quality_gain_demonstrated=False,native_Chat_verified=False)
 state['current_entrypoints']=dict(MCP='chat_tools_current_v16.py;18main tools/four configuredservers',status='Existing v12Reader;actual configured MCP returns31758, no freshReadergeneration this turn',prompts='77saved prompt/transcriptrecords;6actualpredictions thisturn',GPU_trial='Try Local GPU Recovery.command -> try_local_gpu_recovery_v1.py;Terminal/saved output;freshv1/v2both bounded sequences rejected;does not install source',GPU_component_default_build='Makefile.gpu-mailbox-v4;922byteprototype identical defaultsource/profile',Advertising='Existingbase+optionaltrainedstep8Reviewer;source retrieval preserved,quality incomplete',Bootstrap='Existingv9bootstrap remains older;needslatestfrontend/workflow update')
 state['next_actions']=['Continue full readable game/task/callgraph recovery and same-console source build. Address native C ABI/task stack architecture rather than indefinitely relying on2byte ancestor gaps;keep original/public services unless checked replacement.', 'Improve source-verifier feedback with measured private depth/changed protected bytes. Freshone-clickv2Author duplicate reads fixed byrepair,thenfailscase1246caller bound;donotlabelthelogicalalgorithmwrongbeyondactualproof. Oneboundedrepairpolicy/noautoadoption preserved.', 'Use currentlinked320bytedispatcher opcodes/actualcaller SPs. Earlier[-166,-94]ancestorcanary and diagnostic ancestorCSPfields were obsolete256byte estimates;withdrawn. Correct[-230,-158];selected156depth/2bytegap.', 'Keep passed31758/rawfailed31538and31582experiments/receipts immutable;default keyboardpreview unchanged. Fullfreshpaircomparison is authoritative;olderrawrunnerPCM_equal targets historicalreference.', 'Verify nativeLMStudioChat whenUIbridgeevidence changes;no unlockrequests or repeatedunchangedtimed-outAXqueries. CurrentMCP v16 works headlessly.', 'Improve Advertising source interpretation/teaching and trainedReviewer reliability;GPUdevelopmentSFTrecord prepared exposed/untrained,notnewweights or heldoutqualitygain.', 'Advance latestbootstrap andportable/coldfirst-use workflow. Frozenmovedpackagev10/30036doesnotcovernewv16/31758. TryLocaltrial currently assumesadvertising-scholarloaded;use testedassistant_chat.ensure_model readiness path before a futurecoldfirst-use claim.', 'Current publication directlybinds TryLocalGPURecovery.command as as-run source; snapshot that dependency before any futureentrypoint edit. Mutablehandoff/currentnotes/configs are snapshotted here.']
 # Include the finalized state, never this process stdout or its own integrity file.
 save(out/'handoff.json',state);bind(out/'handoff.json');assert state['final_integrity_unique_files']==len(deps)
 for index,(p,h)in enumerate(deps.items()):
  assert sha(p)==h,('Final binding changed',p)
  if index%700==0:print('Final bindings checked',index,'/',len(deps),flush=True)
 integrity=dict(status='terminal_native_gpu_mailbox_full_turn_integrity_pass',directory=str(out),unique_bound_files=len(deps),dependencies_sha256=deps,scope='Previous2706bindings plus all new GPU source/build/run/role/frontend/training/report records. Mutable current/config/notes/external runtime snapshots; no active stdout log bound. Fullgoal incomplete.')
 save(out/'integrity.json',integrity);save(V/'native-gpu-mailbox-turn-integrity-current.json',integrity);save(V/'goal-continuation-current.json',state);print('Terminal GPU goal-turn integrity pass',len(deps),'goal remains active',flush=True)
if __name__=='__main__':main()
