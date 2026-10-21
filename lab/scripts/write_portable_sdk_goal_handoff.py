"""Preserve the full active goal and exact evidence after the portability tests."""
import copy,hashlib,json,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):
 with Path(p).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def main():
 now=datetime.now(timezone.utc);out=V/'goal-continuation-handoffs'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);snap=out/'snapshots';snap.mkdir()
 prior=read(V/'goal-continuation-current.json');save(out/'previous-handoff.json',prior);review=read(V/'portable-sdk-workbench-reviewed-current.json');package=Path(review['package']);live=read(V/'portable-sdk-actual-status-current.json');moved=read(package/'workbench/verification/portable-sdk-actual-status-current.json')
 assert live['status']==moved['status']=='terminal_actual_configured_MCP_portable_status_verified'
 loaded=json.loads(subprocess.check_output(['/Users/kevin/.lmstudio/bin/lms','ps','--json'],text=True));save(out/'loaded-models.json',loaded);assert len(loaded)==1 and loaded[0]['identifier']=='advertising-scholar'and loaded[0]['contextLength']==32768 and loaded[0]['parallel']==1 and loaded[0]['status']=='idle'
 jobs=[]
 for filename,needle in [('portable-assistant-launchers-current.json','test_portable_assistant_launchers.py'),('portable-advertising-launcher-current.json','test_portable_advertising_launcher.py'),('portable-training-update-current.json','test_portable_training_update.py'),('portable-sdk-model-integrity-current.json','verify_portable_sdk_and_models.py')]:
  state=read(V/filename);assert state['status'].startswith('terminal_');pid=state['pid'];r=subprocess.run(['ps','-p',str(pid),'-o','command='],capture_output=True,text=True);assert not(r.returncode==0 and needle in r.stdout);jobs.append(dict(pointer=filename,status=state['status'],pid=pid,matching_worker_live=False,handle_missing=r.returncode!=0))
 preview=[]
 for line in subprocess.check_output(['ps','-axo','pid=,command='],text=True).splitlines():
  if 'run_biwn_interactive.py'in line or('probe_biwn_frame_CPU_owner.py'in line and '--live-window'in line):preview.append(line.strip())
 guide=ROOT/'reports/Portable Setup Test.txt';shutil.copy2(guide,out/'previous-portable-guide.txt');shutil.copy2(package/'READ ME FIRST.txt',out/'previous-package-readme.txt')
 guide_text=f'''LOCAL AI LAB — PORTABLE SETUP TEST

Open the folder named “Portable Setup Test” inside Desktop → Local AI Lab.
Its current location is:
{package}

1. Keep LM Studio open with its local server running at 127.0.0.1:1234.
2. After moving this package, double-click “Restore Local AI Lab.command”.
3. Double-click an assistant, then type your question:
   • Run Game Assistant.command
   • Run Advertising Assistant.command
   • Load Advertising Reviewer.command — experimental trained step 8

The launchers load their copied model at 32K context with one worker. Allow extra
time for loading. Answers appear in Terminal; exact prompts and responses are
saved in the package’s runs folder. This does not demonstrate streaming agents
in native LM Studio Chat. That part of the requested interface needs verification.
The installer registers its own named model resources in your installed LM Studio.

All three launchers produced real answers after the package moved. The copied
SDK, 10,009 dependency files, 39 model resources and ten weight shards passed
checks. Four MCP servers handled ten tested tool kinds. The copied 68000 toolchain
rebuilt the checked 1,588-byte navigation component with an identical binary.

The copied training pipeline completed one real update and saved a separate
adapter. Its observed padded batch was 225 tokens; this does not establish the
maximum supported training size. The test adapter is not selected for daily use.
The normal daily 27B model was restored at 32K context with one worker afterward.

Advertising reliability still needs work. The trained Reviewer caught the
manipulation and causality errors but omitted the timing correction. The base
answer got disclosure and post-ad timing right but omitted beneficiary framing.
These tests show the launchers run, not that adaptation improved model quality.
Exact saved prompts and responses:
{review['model_work_index']}

The workbench folder also contains historical developer launchers. Every legacy
launcher and tool behavior has not been verified. macOS and an installed LM Studio
host service are required. The future 256 GB acceptance profile is in profiles;
performance on that hardware remains untested.

BIWN remains a partial source reconstruction. The latest integrated experiment
has 30,036 native bytes and earlier gameplay evidence. A complete same-console
source rebuild and physical-console verification remain unfinished.
The existing preview is unchanged: click the game, hold C + Up to run, P to pause.

Detailed review:
{review['review']}
'''
 guide.write_text(guide_text);(package/'READ ME FIRST.txt').write_text(guide_text);(out/'portable-guide.txt').write_text(guide_text)
 notes=ROOT/'BIWN Latest Work.txt';shutil.copy2(notes,out/'previous-BIWN Latest Work.txt')
 intro=f'''LOCAL AI LAB — UPDATE {now.isoformat()}

The full four-part goal remains active. This continuation made progress on the
actual portable SDK, inference, toolchain and training pipeline.

Open Desktop → Local AI Lab → Portable Setup Test. The folder contains three
tested assistant launchers and READ ME FIRST.txt. They display answers in
Terminal; native LM Studio Chat display is still unverified for this setup.
Guide: {guide}

The package was physically moved, repaired, then exercised using its copied
Python/SDK and copied model weights. Three actual predictions returned: game,
Advertising base and trained Reviewer. Model metadata and path audit confirm
the copied SDK and own copied model resources. No original-tree read denials
occurred in those clients. The host LM Studio service remains external.

Post-move checks: 10,009 installed dependency files; 39 model resources/10 weight
shards (46.80 GB); actual 8 main MCP calls across 7 kinds, plus 3 specialist read
calls after copying their missing evidence closure (1,057 files). Ten of 25 tool
kinds were tested, not all tool behavior. Five boundary/certificate negatives
reject. The path adapter is diagnostic, not a general security sandbox.

The copied toolchain rebuilt the checked navigation component: 1,588 bytes,
SHA-256 {review['native_binary_sha256']}.
One real copied training update completed on an existing reviewed source dataset:
two layers, rank 8, one 225-token padded batch, three validation batches. The new
adapter remains separate and unpromoted. This is not a complete training repeat,
worst-case capacity test, or evidence of better answers. Daily 27B base restored
at 32K context, one worker, idle. No game behavior or preview version changed.

Advertising review remains partial: trained Reviewer omitted measurement timing;
base answer omitted randomized beneficiary framing. Both raw answers and a
coordinator source-checked correction are saved. Schreiner is exposed reference
material; these are not held-out quality/generalization results. The combined
prompt/transcript index now contains 71 records:
{review['model_work_index']}

Both live and moved configured MCP servers now return the new scoped portability
facts while preserving the 30,036-byte BIWN status. Full readable game/task source,
same-console build, absent gameplay paths, timing/video discrepancies, native Chat,
ordinary workflow reliability and remaining migration work are still open.
Future 256 GB profile is a staged acceptance recipe, not a measured capacity claim.
Detailed review: {review['review']}

All finite jobs in this continuation are terminal. The existing preview remains
running on its previous recipe; click it and hold C + Up to run, P to pause.

PREVIOUS DETAILED GAME / SOURCE / ADVERTISING HANDOFF (PRESERVED BELOW)

'''
 notes.write_text(intro+(out/'previous-BIWN Latest Work.txt').read_text());shutil.copy2(notes,out/'current-BIWN Latest Work.txt')
 deps=dict(read(V/'hybrid-section-turn-integrity-current.json')['dependencies_sha256']);aliases=[]
 def bind(path,expected=None):
  path=Path(path).resolve();digest=sha(path);assert expected is None or digest==expected,str(path)
  mutable=not path.is_relative_to(ROOT)or(path.parent==V and path.name.endswith(('-current.json','-active.json')))or path in [notes,guide,ROOT/'config/current-model-work-sources.json']
  if mutable:
   target=snap/(hashlib.sha256(str(path).encode()).hexdigest()[:14]+'-'+path.name[-140:]);shutil.copy2(path,target);aliases.append(dict(original=str(path),snapshot=str(target),sha256=digest));path=target
  assert str(path)not in deps or deps[str(path)]==digest,str(path);deps[str(path)]=digest
 publication=read(V/'current-biwn-latest-publication-current.json')
 for name,digest in publication['dependencies_sha256'].items():bind(name,digest)
 for name in ['portable-sdk-workbench-reviewed-current.json','portable-sdk-workbench-current.json','portable-sdk-physical-move-current.json','portable-workbench-evidence-current.json','portable-sdk-model-integrity-current.json','portable-native-build-current.json','portable-assistant-launchers-current.json','portable-advertising-launcher-current.json','portable-training-update-current.json','portable-sdk-actual-status-current.json','current-biwn-latest-publication-current.json','current-model-work-index-v4-current.json']:
  bind(V/name)
 for f in [Path(__file__),notes,guide,ROOT/'config/current-model-work-sources.json',package/'READ ME FIRST.txt',package/'workbench/verification/portable-sdk-actual-status-current.json']:
  bind(f)
 for state in [review,live,moved,*[read(V/name)for name in ['portable-assistant-launchers-current.json','portable-advertising-launcher-current.json','portable-training-update-current.json']]]:
  for f in Path(state['directory']).rglob('*'):
   if f.is_file():bind(f)
 job=Path(read(V/'portable-training-update-current.json')['job'])
 for f in job.rglob('*'):
  if f.is_file():bind(f)
 for f in sorted((ROOT/'scripts').glob('*portable*.py')):bind(f)
 for f in sorted((ROOT/'runs').glob('portable-*.log')):bind(f)
 index=read(V/'current-model-work-index-v4-current.json')
 for f in Path(index['directory']).glob('*'):
  if f.is_file():bind(f)
 for f in out.glob('*'):
  if f.is_file():bind(f)
 def verify(row):
  path,digest=row
  try:return None if sha(path)==digest else dict(path=path,error='SHA mismatch')
  except Exception as error:return dict(path=path,error=repr(error))
 with ThreadPoolExecutor(max_workers=4)as pool:issues=[x for x in pool.map(verify,deps.items())if x]
 integrity=dict(status='terminal_portable_SDK_turn_bound_receipt_integrity_pass'if not issues else'terminal_integrity_failed',directory=str(out),unique_bound_files=len(deps),dependencies_sha256=deps,issues=issues,mutable_snapshots=aliases)
 save(out/'integrity.json',integrity);assert not issues,str(issues[:5]);save(V/'portable-sdk-turn-integrity-current.json',integrity)
 state=copy.deepcopy(prior);state.update(status='active_moved_copied_SDK_three_assistants_and_training_update_verified_full_goal_remains',recorded_at=now.isoformat(),previous_turn_classification='Progress: hybrid navigation integrated and gameplay-reviewed; original PDF sections and four advertising role outputs reviewed.',this_turn_classification='Progress: actual moved copied SDK/three assistant launchers/three model predictions, copied1588byte source build,10009dependencies/39modelresources/10shards,ten tool kinds/five negatives,one real unpromoted training update; source-reviewed answer omissions retained and current MCP facts updated.',goal_complete=False,prior_state_archive=str(out/'previous-handoff.json'),latest_portable_review=str(V/'portable-sdk-workbench-reviewed-current.json'),portable_package=str(package),latest_integrity=str(out/'integrity.json'),final_integrity_unique_files=len(deps),completed_finite_jobs=jobs,finite_jobs=[],finite_jobs_pending=0,local_model_work_this_continuation=dict(actual_prediction_rounds=3,actual_training_updates=1,new_unpromoted_adapter=True,quality_gain_demonstrated=False,native_Chat_verified=False,default_daily_restored=True),interactive_preview=dict(observed_processes=preview,operated_or_restarted=False,run_keys='Hold C + Up; P pauses/resumes',recipe='Existing older preview, not the latest native experimental disc'),no_completion_claim=True)
 state['full_goal_requirements'][0].update(state='incomplete',evidence=review['review'],remaining='Three moved-package terminal launchers/copiedSDK now exercised. NativeChat/current visual adoption and complete ordinary workflow reliability remain unverified; exact transcripts71.')
 state['full_goal_requirements'][2].update(state='partially_implemented_reliability_incomplete',evidence=review['review'],remaining='Base and experimental trained step8Reviewer load and infer from copied resources. Reviewer timing omission and base beneficiary omission remain; source-checked coordinator correction retained. No quality gain or new Advertising training this turn.')
 state['full_goal_requirements'][3].update(state='incomplete',evidence=review['review'],remaining='Physically moved package with actual copiedSDK/three launchers/nativecomponentrebuild/one real training update verified. Remaining legacy workflows/alltoolbehaviors/nativeChat/onboarding and actual futurehardware acceptance remain; staged256GBprofile is unbenchmarked.')
 state['next_actions']=['Continue full readable game-source/task/callgraph recovery and same-console rebuild; existing30036native experiment and preserved hybrid attribution are not completegame proof.','Broaden absent game outcomes and resolve timing/video/state discrepancies using original-facing checks; preserve current preview and original images.','Finish easy nativeLMStudioChat/current prompt/tool adoption and source-aware ordinary roles; terminal SDK output does not satisfy visible Chat streaming.','Improve Advertising research/education/reviewer interpretation with source-adjudicated tasks; currentsource is exposed and three portable smoke predictions are not a quality benchmark.','Complete remaining migration/source/training/workflow prerequisites and legacytool behavior. Preserve the successful copied27B one-update adapter as unpromoted capability test,not dailyquality improvement. Do not repeat passed unchanged tests or restart terminal jobs.']
 save(out/'handoff.json',state);save(V/'goal-continuation-current.json',state);print(json.dumps(dict(status=state['status'],integrity_files=len(deps),directory=str(out),goal_complete=False)))
if __name__=='__main__':main()
