"""Preserve the complete four-part objective and current23,260source progress."""
import json,hashlib,shutil,subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def main():
 now=datetime.now(timezone.utc);out=V/'goal-continuation-handoffs'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);pointer=V/'goal-continuation-current.json';state=read(pointer);shutil.copy2(pointer,out/'previous-handoff.json')
 init=read(V/'actor-initialize-integration-reviewed-current.json');sprite=read(V/'sprite-create-integration-reviewed-current.json');pub=read(V/'current-biwn-latest-publication-current.json');index=read(V/'current-model-work-index-v4-current.json');delivery=read(V/'current-sprite-status-delivery-current.json');earlier=read(V/'current-initializer-status-delivery-current.json');ui=read(V/'native-chat-model-picker-retry-current.json');build=read(sprite['build']);profile=read(V/'local-actor-dispatch-low-repair-current.json')
 assert sprite['resident_bytes']==pub['facts']['experimental_build']['resident_bytes']==23260 and sprite['live_monitor_pass']and init['resident_bytes']==21080 and delivery['actual_predictions']==earlier['actual_predictions']==2 and profile['actual_predictions']==2
 finite=[]
 for kind in ['candidate','control']:
  d=read(V/f'native-sprite-create-{kind}-current.json');assert d['status']=='terminal_native_sprite_create_route_pending_review'and d['exit_code']==0
  live=subprocess.run(['ps','-p',str(d['child_pid']),'-o','pid=,command='],capture_output=True,text=True);assert live.returncode!=0,'Recorded game child still live'
  finite.append(dict(kind=kind,status=d['status'],pid=d['pid'],child_pid=d['child_pid'],frames=d['frames'],live_monitor_pass=d['live_monitor_pass']))
 notes=ROOT/'BIWN Latest Work.txt';shutil.copy2(notes,out/'previous-BIWN Latest Work.txt')
 text=f'''BIWN — CURRENT WORK
{now.isoformat()}

LATEST REVIEWED EXPERIMENTAL DISC
Sprite creation (137E0), actor dispatch (13AE0) and actor initialization (134DC) now run as rebuilt C with original-facing interfaces. This is part of the game, not a complete same-console source rebuild. Latest resident payload: 23,260 bytes in a 24,512-byte reservation; 1,252 bytes spare. Heap floor 0x164D80 and initial capacity 373,376 remain unchanged. The new2,180-byte sprite routine is at0x164018; its parent's21,080bytes remain identical. Original disc unchanged. Source, interfaces, fixtures, integration and reviews for these three routines are coordinator work. Prior accepted local functions retain historical attribution.

VERIFIED COMPONENTS AND REAL GAMEPLAY
Sprite:1,228 full CPU/SR/bank/public-RAM/ordered-access/helper-interface cases, all184 decoded original instruction sites. Shared105DAposition executes; allocator/decoder remain prescribed in these component fixtures. Three rebuilt roots together pass2,084cases/max630private bytes. Four seeded source/binary defects reject. Full-payload startup passes96cases. Read-only context monitors pass8,672root executions (2,084dispatcher,1,024initializer,1,228sprite, original and C each), including the decoder's leftover allocator stack argument; five decoded-CPU/mirror-only defects reject.

Fresh game candidate29,787frames/control29,790both return outdoors and hold120frames. Only the eight-byte137E0entry is restored in the control; both retain native13AE0/134DCand the common layout/prior routines. One sprite call invokes real105DAposition,152A2allocation andE2B8decoding once each. Candidate checks3sprite contexts,13parent and16initializer contexts; no reported ABI/context/task-boundary or inherited resource/cache/geometry/door/selector errors. Actual observed dispatcher max630private bytes/min182task headroom; sprite596/min188. Finite observed paths, not general bounds.

TIMING/MEDIA LIMITS
Fresh aligned prefix29,787frames differs in17,114video frames; PCM bytes95,318,400versus95,328,000and hashes differ. CPU/RAM/GPU/DSP/navigation/locomotion/buttons also differ. Full state/media/timing equivalence remains unresolved, including older scanner/initializer discrepancies. Sprite full pool, animated callback variants/double-object and other IDs remain component-only. Inherited selectors still14actor successes/0failures and0sprite successes/1skipped failure; other success/failure paths remain component-only. Retained native emulator CPU/GPU/DSP/IRQ/platform services execute both routes. Five older strict-Cprocessor jobs apply only to16872/17084/17812/18270/18888discs, not23260. No physical Jaguar CD test/full rebuild demonstrated.

PRECEDING INITIALIZER/LAYOUT WORK NOW RECORDED
The21,080disc had integrated1,620-byte134DCat0x1639C4:1,024cases/all148sites,96startup,8-bit/word/long public access order and full helper-entry/register/SR/bank tests. Enlarged reservation/heap relocation checked with192heap-initializer,3,392native-blitter and3,392ordered cases plus36fresh-constructor capacity requests. Two real routes29,790/29,777frames pass12initializers/16helpers,13parent+16initializer canaries, max600/min182. Timing/media differ. Those results remain separate historical evidence; the new23,260disc adds only137E0within the same reservation. A source-path inheritance error in initializer publication metadata was corrected from dispatcher to the actual checked initializer source; binary/test results unchanged.

EASY LOCAL INFERENCE / WHO DID WHAT
Actual Start Local AI -> S was tested twice against21,080then23,260publications: each one configuredMCPcall/two local prediction rounds,140words,20.45and20.79seconds. Latest raw answer gets core size/routing/attribution/media/older-job applicability right but omits required component/startup completion, retained processor and detailed coverage/goal limits. Its build label is awkward. Format passes do not prove a complete or easy-to-read status answer. Detailed delivery review retained.
A separate adaptive13AE0Author repair used reasoning=low and6,000total-output budget:273.37seconds,5,999reasoning tokens,zero finalC. Compiler/linker rejects missing body; same-weight Reviewer reports noissues. Two predictions,noadoption/default-profile/weight change. No local model wrote the new137E0routine. These are sequential roles on the same base weights, not independent agents. No cloud subagents were created. Start Local AI -> I now lists53saved prompt/transcript records (not53newpredictions).

NATIVE LM STUDIO CHAT
A fresh app inventory/getApp works. Model-picker AX entries and simultaneous screenshots disagree; AX selection gives invalid IDs, keyboard/New attempts produce no verified new Chat or generation. Existing unsent preview-controls draft preserved. No model attachment, new generation, restart or unlock request verified. SDK/CLI status works separately. Current native Chat streaming remains unverified.

DEFAULT INTERACTIVE PREVIEW
ExistingPIDs233/235retain their older verified sourceCPU/GPU checkpoint/overlay recipe. It is not this23,260experimental disc and was not operated or restarted. HoldC+Up to run;Ppauses/resumes. No preview/default promotion.

MODELS / ADVERTISING / FUTURE MACHINE
Game native-repair-v3completed64updates/step32selected but is unpromoted after code-output failures. Advertising optional trained step8Reviewer remains exported/loadable; latest source-transfer comparison shows no observed gain over the base and remaining review/teaching reliability limits. Daily base remains the27Blocal model. No new weight training this turn. Model migration inventory:39files/46.80GB, prior10shard hash audit; this metadata/source integrity check is not a fresh full-weight audit. Current-host cold runtime install exists; whole-workbench relocation/off-machine restoration and future256GBconfiguration verification remain unfinished.

FULL GOAL STILL ACTIVE
Finish readable game/same-console source reconstruction and remaining actual game interfaces; broaden currently component-only behavior and resolve timing/media; make native local inference and useful roles reliable; improve/evaluate game and Advertising adaptation; complete portable workbench migration/future256GBpreparation. Do not mark complete based on these components.

Sprite source/live review: {sprite['report']}
Initializer source/live review: {init['report']}
Latest local status review: {delivery['report']}
Prompt viewer: {index['report']}
'''
 notes.write_text(text);shutil.copy2(notes,out/'current-BIWN Latest Work.txt')
 old=read(V/'gap320-initializer-turn-integrity-current.json');hashes=dict(old['dependencies_sha256']);resolutions=[];snap=out/'snapshots';snap.mkdir()
 def bind(p,h=None):
  p=Path(p).resolve();actual=sha(p);assert h is None or actual==h,(str(p),'dependency changed')
  if p.name.endswith(('-current.json','-active.json')):
   q=snap/(hashlib.sha256(str(p).encode()).hexdigest()[:12]+'-'+p.name);shutil.copy2(p,q);resolutions.append(dict(mutable_pointer=str(p),immutable_exact_bytes=str(q),sha256=actual));p=q
  if str(p)in hashes:assert hashes[str(p)]==actual,p
  hashes[str(p)]=actual
 for obj in [init,sprite,pub]:
  for p,h in obj['dependencies_sha256'].items():bind(p,h)
 for obj in [earlier,delivery]:
  for p,h in obj['source_sha256'].items():bind(p,h)
 paths=[Path(__file__),out/'current-BIWN Latest Work.txt',out/'previous-handoff.json',out/'previous-BIWN Latest Work.txt',Path(init['directory'])/'protocol.json',Path(sprite['directory'])/'protocol.json',Path(pub['directory'])/'publication.json',Path(index['directory'])/'manifest.json',Path(index['report']),Path(index['source_list_snapshot']),Path(ui['directory'])/'protocol.json',ROOT/'projects/black-ice-white-noise/restoration/native-m68k/sprite-create-readme.txt',ROOT/'scripts/check_biwn_native_sprite_create.py',ROOT/'scripts/qualify_biwn_native_sprite_create.py',ROOT/'runs/native-sprite-create-negatives.log',V/'native-sprite-create-final-current.json',V/'native-sprite-create-linked-current.json',V/'native-actor-triple-current.json',V/'sprite-create-live-contexts-current.json',V/'sprite-create-integration-reviewed-current.json',V/'current-sprite-status-delivery-current.json',V/'current-initializer-status-delivery-current.json',V/'native-chat-model-picker-retry-current.json']
 for p in paths:bind(p)
 def check(item):
  p,h=item
  try:return None if sha(p)==h else dict(path=p,error='hash changed')
  except OSError as e:return dict(path=p,error=str(e))
 with ThreadPoolExecutor(max_workers=4)as pool:issues=[x for x in pool.map(check,hashes.items())if x]
 integrity=dict(status='terminal_sprite_initializer_and_inherited_integrity_pass'if not issues else'terminal_integrity_failed',directory=str(out),unique_bound_files=len(hashes),issues=issues,dependencies_sha256=hashes,historical_mutable_pointer_resolutions=resolutions,scope='Bound source/protocol/report/binary integrity and historical snapshots; not new full model-weight audit, full game, hardware or model reliability proof.');save(out/'integrity.json',integrity);save(V/'sprite-integration-turn-integrity-current.json',integrity);assert not issues,issues
 preview=[]
 for pid in [233,235]:
  p=subprocess.run(['ps','-p',str(pid),'-o','pid=,command='],capture_output=True,text=True)
  if p.returncode==0:preview.append(dict(pid=pid,command=p.stdout.strip()))
 state.update(status='active_sprite_creation_integrated_readable_game_and_model_work_remain',recorded_at=now.isoformat(),prior_state_archive=str(out/'previous-handoff.json'),goal_complete=False,previous_turn_classification='Progress: prior substantive continuation integrated134DCand24512layout, two real routes and separate failed local low-reasoning trial. Intervening preview-controls reply verifiedC+Up; no source changes there.',this_turn_classification='Progress: reconciled/published21080initializer results; recovered original-facing137E0C/ABI2180bytes,1228cases/all184sites,2084triplecases,4source negatives,23260disc+96startup,8672read-onlycontext executions/5negatives, two fresh routes29787/29790with real allocation/decode and zero ABI/context errors; media/state differences retained. Published23260via unchanged configuredMCP. Actual local Reader4rounds across two menuSdeliveries corecorrectwithomissions. NativeChat app access works but AX/pixels disagree/no generation.53savedpromptrecords. Full four-part objective remains open.',latest_built_disc_resident_bytes=23260,latest_published_live_build_resident_bytes=23260,latest_built_disc_game_frames=29787,latest_actor_initialize_component=str(V/'native-actor-initialize-final-current.json'),latest_actor_initialize_review=str(V/'actor-initialize-integration-reviewed-current.json'),latest_sprite_component=str(V/'native-sprite-create-linked-current.json'),latest_sprite_build=str(V/'native-sprite-create-disc-build-current.json'),latest_sprite_review=str(V/'sprite-create-integration-reviewed-current.json'),latest_joint_actor_component=str(V/'native-actor-triple-current.json'),latest_context_oracle=str(V/'sprite-create-live-contexts-current.json'),latest_local_status_delivery=str(V/'current-sprite-status-delivery-current.json'),latest_integrity=str(out/'integrity.json'),final_integrity_unique_files=len(hashes),finite_jobs=[],finite_jobs_pending=0,completed_finite_jobs=finite,completed_current_turn_sessions=[93785,5601,70716,27511,74692,82997,21968,44539,7001,51877,81424],local_model_work_this_continuation=dict(Reader_prediction_rounds=4,menuS_deliveries=2,evidence_calls=2,words_each=140,seconds=[earlier['seconds'],delivery['seconds']],new_code_Author_predictions=0,new_training=False,native_Chat_verified=False),local_model_work_since_previous_handoff=dict(total_actual_predictions=6,Reader_rounds=4,failed_low_reasoning_Author=1,same_weight_Reviewer=1,accepted_new_local_code=False,weights_changed=False),interactive_preview=dict(observed_processes=preview,operated_or_restarted=False,run_keys='HoldC+Up;Ppauses/resumes',recipe='Older verified sourceCPU/GPU checkpoint/overlay, not23260experimental native disc'),next_actions=['Continue actual game-source/interfaces after the three original-facing creation routines; original-console/full readable game rebuild remains unfinished. Preserve finite API/RAM/helper coverage and compare real callers, not just translated isolated kernels.','Broaden137E0live animated callbacks/double-object/fullpool, initializer currently component-only callbacks, failures/resource/stack paths and investigate unresolved timing/media/state differences. New23260pair29787/29790has17114video differences/unequalPCM; do not promote the default preview or claim console/media equivalence.','NativeChatfreshinventory/getAppwork,but simultaneous AXmodelpicker/pixels disagree and selectionIDsinvalid; fresh/New/keyboardattemptsproducednoverifiedresponse. Do not askunlock or repeat identical failing UI actions; continueSDK/local roles and seek a materially different verifiable UI route.','Improve easy local output: latestSReader140words20.79s/2rounds/oneMCPcall/corecorrect but misses required completion lead, retainedprocessors and exactcomponent-only/whole-goal limits. Buildlabelconcatenation hurtsreadability. Keeprawprompts/responses andsame-weightreviewlimits.','Game step32 remains unpromoted; Advertising optionalstep8loadable but no observed source-transfer gain. Plan/evaluate adaptation with exposure/heldout labels and output correctness rather than trainingloss. No newweights this continuation.','Complete portableworkbench relocation/migration/future256GBconfiguration preparation; prior39file46.80GBinventory/full10shard audit and currenthostcleaninstall do not establish fullrestore. Preserve four-partscope.','CurrentpreviewPIDs233/235runoldercheckpoint,not23260disc. C+Up runs,Ppauses. Do not silentlyreplaceit. Allfinitejobsfromthiscontinuationterminated;do not restart alreadycompletedroutes.'],no_completion_claim=True,handoff_script_sha256=sha(Path(__file__)))
 state['current_entrypoints']['prompts_I']='53saved prompt/transcript records, including failed low-reasoning trial; not53newpredictions'
 state['full_goal_requirements'][0]['remaining']='SDK/CLI/MCP and local role/training artifacts work. Latest two actualmenuSoutputs each140words/~21seconds/corecorrect but omit required scope/completion; nativeChat freshAX/pixel mismatch preventsverifiedmodel attachment/generation. Reliability/easyinference unfinished.'
 state['full_goal_requirements'][1]['evidence']=sprite['report'];state['full_goal_requirements'][1]['remaining']='Original-facing13AE0/134DC/137E0now integrated in23260experimental disc.1228sprite/all184sites,2084joint,96startup,8672context executions and two real routes pass finiteABI/context checks. Full readable game/same-console source rebuild, remaining actualgameinterfaces, broader callbacks/resources/stack coverage and timing/media/state agreement remain unfinished.'
 save(out/'protocol.json',state);save(pointer,state)
 with(ROOT/'runs/agent-work-audit.jsonl').open('a')as f:f.write(json.dumps(dict(recorded_at=now.isoformat(),event='sprite137E0native_integration_and_full_goal_handoff',coordinator='Source/ABI/fixtures/negatives/triplecontext/layout-preservingintegration/two real routes/review/publication',local_model='Actualone-keylocalSDKReader4rounds/twoMCPcalls; previouslow-reasoningAuthor+Reviewer2predictions separatelyreconciled',new_code_Author_predictions=0,new_training=False,published_resident_bytes=23260,frames=[29787,29790],report=sprite['report'],bound_files_verified=len(hashes),goal_complete=False))+'\n')
 print(json.dumps(dict(status=state['status'],verified_files=len(hashes),pending_jobs=0,published=23260,goal_complete=False,notes=str(notes))))
if __name__=='__main__':main()
