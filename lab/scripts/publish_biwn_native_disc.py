"""Publish experimental fresh-loaded native CDI with finite-scope evidence."""
from datetime import datetime,timezone
from pathlib import Path
import json,hashlib,shutil,subprocess
ROOT=Path(__file__).resolve().parents[1];RT=Path.home()/'.lmstudio/local-ai-lab'
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 now=datetime.now(timezone.utc);out=ROOT/'verification/native-disc-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 cold_path=ROOT/'verification/native-disc-cold-boot-current.json';cold=json.loads(cold_path.read_text());build=json.loads(Path(cold['build_proof']).read_text());entry=json.loads(Path(cold['entry_proof']).read_text());menu_path=ROOT/'verification/native-disc-menu-current.json';menu=json.loads(menu_path.read_text());t=menu['turn'];review=json.loads((ROOT/'verification/local-native-disc-review-current.json').read_text())
 assert cold['frames_per_lane']==24000 and cold['native_component_calls']==1 and cold['game_state_frames_equal']==24000
 assert cold['all_call_boundaries_equal']and cold['comparison_analysis']['video_different_frames']==125 and not cold['comparison_analysis']['strict_whole_run_video_equivalence']
 assert entry['entry_cases']==96 and entry['component_cases']==5151
 assert not t['quality_flags']and '125'in t['answer']
 for path,digest in {**build['source_sha256'],**entry['source_sha256'],**cold['runtime_dependencies_sha256'],**cold['classification_artifacts_sha256']}.items():assert sha(path)==digest,path
 assert sha(build['derived_disc'])==build['derived_disc_sha256']and sha(build['original_disc'])==build['original_disc_sha256']
 menu.update(status='terminal_coordinator_accepted_fresh_native_disc_scope',coordinator_review=dict(accepted=True,words=len(t['answer'].split()),note='Correct fresh HLE load, one native component, early-video mismatch and remaining emulator/whole-game/hardware limits. Prior ambiguous dynamic-instruction wording preserved separately.'))
 save(menu_path,menu);save(Path(menu['directory'])/'protocol.json',menu);save(ROOT/'verification/native-disc-menu-active.json',menu)
 pins={}
 for name in ['interactive-preview-recipe.json','outdoor-restoration-preview-recipe.json']:
  d=json.loads((ROOT/'verification'/name).read_text());assert all(sha(path)==digest for path,digest in d['hashes'].items());pins[name]=dict(files=len(d['hashes']),all_hashes_match=True)
 models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],text=True));assert len(models)==1 and models[0]['status']=='idle'and models[0]['queued']==0
 for name in ['CURRENT DECOMPILATION.txt','CURRENT LOCAL INFERENCE.txt']:shutil.copy2(ROOT/name,out/('previous-'+name))
 decomp=f'''BLACK ICE WHITE NOISE — PARTIAL NATIVE DISC BUILD
Updated {now.isoformat()}

WHAT NOW LOADS FROM DISC
A derived BIWN#23 CDI fresh-boots through the retained emulator HLE path and loads one newly GCC-compiled keypad-digit routine using new native 68000 startup code. This removes the old checkpoint allocation/host RAM-overlay requirement for this component. It is original game code plus a rebuilt component and new startup/memory layout, not a whole-game source rebuild or authenticated physical-console boot.
The disc-stage entry jumps to a temporary loader at0xFF000. That loader performs the original SR/SP setup, preserves the other registers, copies130compiled bytes to0x15EDC0 and resumes original entry at0x400A. Heap initialization and compactor boundary literals are shifted to0x15EE48, reserving136bytes with eight-byte alignment. The loader staging region is used immediately before regular initialization; it is not assumed forever-free. The136byte resident reservation is outside the revised heap, so compaction cannot move or overwrite it through that heap.
Only169CDIbytes differ, all inside declared stage patches. Every other byte and all track metadata match the original. The stage entry's first10bytes overlap the original60000byte boot payload; that overlap is deliberately changed too. The original CDI is unchanged. There are no added game repairs beyond the native code/layout changes.

EXECUTED CHECKS
96native entry cases preserve all16registers, PC and SR and check all130copied bytes. Patched original heap initialization, actual allocations and compaction preserve the resident code.5,151native original/compiled ABI cases pass through the new entry JMP.
Two ordinary fresh loads ran24,000frames each, with no saved machine, host RAMpatch or CPU seed. The derived image naturally called the new keypad routine once, executing11instructions on that input path;11is not the routine's static instruction count. All entry/return registers, PC and SR matched the original call. The candidate executes no original keypad-body instructions on that call. Both runs match all24,000tracked player/UI states. Tracking is limited to player X/Z, scene/mode/tile/equipment, movie flags and controller state; it is not full CPU/RAM equivalence.
23,875video frames match;125frames differ between177and657. All video from658through24,000and the final image match. The cause of the early differences has not been isolated; changed startup timing is a hypothesis. Strict whole-run video equivalence is not proved. PCM captures are identical but silent, so audible playback is not demonstrated. Original CPU/GPU/DSP/device emulator, HLE/CD bootstrap and drive services remain providers.
The earlier1,500frame checkpoint experiment separately exercised8calls from2callers. Its counts must not be relabeled as this fresh-disc run. Earlier movable-code checks covered5,151cases before and after actual compaction; this new disc uses an explicit permanent reservation instead of a movable handle.

FILES / REPRODUCTION
Derived disc: {build['derived_disc']}
Disc SHA256: {build['derived_disc_sha256']}
Double-click Desktop/Local AI Lab/Show BIWN Native Disc.command to reveal it in Finder.
Build from the lab root: .venv/bin/python scripts/build_biwn_native_disc.py
Entry/component checks: .venv/bin/python scripts/check_biwn_native_disc_entry.py
Fresh pair: .venv/bin/python scripts/check_biwn_native_disc_cold_boot.py
Build manifest: {cold['build_proof']}
Fresh execution proof: {cold_path}
Comparison details: {Path(cold['directory'])/'comparison-analysis.json'}

WHO DID WHAT / LOCAL OUTPUT TEST
Coordinator wrote the loader, memory layout/build/observation/check scripts and frontend evidence. Recovered C was reused. The relative-call ABI shim is a coordinator adaptation of an earlier guided local-model shim. No new weights were trained or promoted.
Local Reviewer miscounted DBRA64as64iterations and treated136reserved bytes as code size. Its review was rejected: DBRA64executes65word copies, copying130bytes; six extra reserved bytes provide alignment. The exact raw prompt/response is preserved. A candidate evaluation case was saved without assigning a training/test split; it has not been used for training or a claimed held-out evaluation.
The actual installed local launcher returned{len(t['answer'].split())}words in{t['seconds']}seconds, {t['rounds']}generation(s), with accepted coordinator scope review. It reported the fresh load, video differences and retained services. This is headless local inference, not new LMStudio Chat UI evidence.
Reviewer prompt/response: {Path(review['directory'])/'prompts-and-responses.txt'}
Launcher exact input/output: {Path(menu['run'])/'session.json'}

PREVIEWS / REMAINING GOAL
Your already-running preview was left alone. Main P and optional O profiles retain all112/84pinned hashes; the new disc is not promoted into them. P still opens its checked source-produced merchant checkpoint; O remains the separate outdoor profile. C+Up runs; arrows move/turn; Z=A, X=B, C=C. Ppauses, M mutes, Esc closes.
Next: isolate early-video differences; broaden native components and natural routes; link/package the whole game from recovered source; continue readable engine/scene/coordinate reconstruction and runtime-provider removal; validate performance and physical controls/audio/authenticated console boot. Future256GBhardware is unbenchmarked. Advertising base-plus-retrieval readiness remains available; grounded research/teaching quality work remains. Full objective stays active and incomplete.
'''
 inference=f'''LOCAL AI — CURRENT USER WORKFLOW
Updated {now.isoformat()}

EASY ENTRY
Desktop/Local AI Lab/Start Local AI.command:1Game Assistant,2Advertising Assistant,3game team,4advertising team,5LMStudio Chat,6saved runs,Pmain preview,Ooutdoor preview. Show BIWN Native Disc.command reveals the experimental derived CDI.
Preferred model remains27B6bitbase plus retrieval, identifier advertising-scholar,32Kcontext/one worker shared by both domains. Launcher loads it when needed. Agent roles share weights and are not independent verification. AdvertisingV6/V7were actually trained and quality-rejected. Base plus retrieval remains preferred; broaden grounded research/teaching evaluation before further training. No new weights were trained/promoted in this session.

LATEST OUTPUT TEST
The native-disc question returned{len(t['answer'].split())}words in{t['seconds']}seconds and{t['rounds']}generation(s), no mechanical flags, with coordinator acceptance. It states that an experimental mixed original/new native CDI boots through emulator HLE, loads one rebuilt routine, has125early differing video frames and retains emulator services. A prior answer ambiguously phrased11executed instructions as though it were the static routine size; its raw output was preserved and secondary instruction telemetry removed from the compact status context. The launcher chooses evidence by host code; lookup does not rerun game tests.
Accepted run and exact prompts/responses: {Path(menu['run'])/'session.json'}
Installed MCP proof: {ROOT/'verification/native-disc-installed-MCP-current.json'}

LOCAL REVIEW QUALITY
Local Reviewer returned111words in{review['result']['seconds']}seconds but its technical claim was wrong: D0=64withDBRAcopies65words/130bytes, and136is the aligned heap reservation. The coordinator rejected it against executed native checks. A curated candidate was saved at training/native-review-eval-candidates; it is unassigned, unused for training and not claimed as a held-out result. This is evidence that local review still requires execution checks, not proof of autonomous correctness.
Exact review prompt/response: {Path(review['directory'])/'prompts-and-responses.txt'}
Decision: {ROOT/'verification/local-native-disc-review-current.json'}
Coordinator authored native loader/layout/build/harness changes; recovered C reused and earlier guided model shim adapted. No new local-model C-body authorship or weight training is claimed.

LM STUDIO CHAT
The earlier genuine conversation BIWN — Local game team remains available with actual three-role prompts/responses and generation metadata. This session was headless and was not fabricated/imported into native Chat. The installed team helper retrieves the new evidence on its next genuine turn. New Advertising Chat rendering and cancellation UI remain unverified. Work can continue without screen access.

BUILD / NEXT WORK
Experimental CDI and full scope are in CURRENT DECOMPILATION.txt. Fresh24,000frame tests use no checkpoint or host game-RAM patch; retained emulator HLE/device services remain. One natural native call is covered; the full game is not rebuilt. The earlier8call/1,500frame checkpoint test is separate. Existing P/O previews are unchanged.
Next: early-video analysis, more native components/routes and whole-game source link/package; continue grounded Advertising evaluation and future hardware benchmarking. At publication all finite jobs were terminal, model idle and queue empty. That is a point-in-time receipt, not unattended background computation.
Audit: {ROOT/'runs/agent-work-audit.jsonl'}
'''
 for root in [ROOT,RT]:
  (root/'CURRENT DECOMPILATION.txt').write_text(decomp);(root/'CURRENT LOCAL INFERENCE.txt').write_text(inference)
 launcher=ROOT/'Show BIWN Native Disc.command';launcher.write_text('''#!/bin/zsh
set -eu
LAB_ROOT="${0:A:h}"
"$LAB_ROOT/.venv/bin/python" "$LAB_ROOT/scripts/reveal_biwn_native_disc.py"
''');launcher.chmod(0o755)
 reveal=ROOT/'scripts/reveal_biwn_native_disc.py';reveal.write_text('''from pathlib import Path
import json,subprocess
root=Path(__file__).resolve().parents[1]
build=json.loads((root/'verification/native-disc-build-current.json').read_text())
disc=Path(build['derived_disc']);assert disc.is_file()
subprocess.run(['/usr/bin/open','-R',str(disc)],check=True)
''')
 native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';(native/'README.txt').write_text('''BIWN NATIVE COMPONENT AND EXPERIMENTAL DISC BUILDS
The current experimental derived CDI is built from the lab root with:
.venv/bin/python scripts/build_biwn_native_disc.py
It combines original game data/code with one freshly compiled C routine,
new native stage entry and explicit136byte resident memory reservation.
See CURRENT DECOMPILATION.txt and native-disc-cold-boot-current.json for
fresh HLE boot evidence and125early video mismatches. It is not a complete
source-built game, strict video-equivalent run or physical-console proof.

Historical component targets, run here:
make -f Makefile.movable movable :130byte position-independent component.
make -f Makefile.full-abi full-abi :132byte absolute-call component.
DefaultMakefile retains the older scalar-contract experiment.
Neither payload fits the original104byte body; do not overwrite it directly.
Current disc builder uses a six-byte entry JMP plus native startup copying
into a deliberately excluded heap region. Prior movable-handle experiment
and its compaction proof remain separate historical artifacts.
''')
 reports=['native-disc-build-current.json','native-disc-entry-current.json','native-disc-cold-boot-current.json','native-disc-installed-MCP-current.json','native-disc-menu-current.json','local-native-disc-review-current.json']
 for name in reports:shutil.copy2(ROOT/'verification'/name,out/name)
 for rel in ['scripts/build_biwn_native_disc.py','scripts/check_biwn_native_disc_entry.py','scripts/check_biwn_native_disc_cold_boot.py','scripts/finalize_biwn_native_disc_evidence.py','scripts/check_biwn_native_disc_menu.py','scripts/review_biwn_native_disc_local.py','scripts/publish_biwn_native_disc.py','scripts/reveal_biwn_native_disc.py','chat_tools.py','assistant_chat.py','Show BIWN Native Disc.command']:
  dest=out/'sources'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,dest)
 for name in ['CURRENT DECOMPILATION.txt','CURRENT LOCAL INFERENCE.txt']:shutil.copy2(ROOT/name,out/name)
 ledger_path=ROOT/'verification/goal-continuation-current.json';ledger=json.loads(ledger_path.read_text());shutil.copy2(ledger_path,out/'previous-goal-continuation.json')
 ledger.update(status='fresh_mixed_native_disc_boot_goal_incomplete',recorded_at=now.isoformat(),previous_turn_classification='progress: movable compiled component/actual checkpoint game calls and launcher output tests.',this_turn_classification='progress: build derivedCDI with native startup and explicitheap reservation,96entry/5151ABIchecks,24000frame freshoriginal/derivedHLEboots,1naturalcompiledcall.125earlyvideodifferences preserved; alltrackedgamefields/finalvideo/silentPCMmatch. NewlocalReviewerrorevaluated and fresh installedmenu checked.',goal_complete=False,latest_evidence_snapshot=str(out),latest_native_disc_build=str(ROOT/'verification/native-disc-build-current.json'),latest_native_disc_boot=str(cold_path),latest_native_component_local_inference=str(menu_path),latest_MCP_check=str(ROOT/'verification/native-disc-installed-MCP-current.json'),preview_pin_checks=pins,live_processes=[],live_process_observation=dict(observed_at=now.isoformat(),finite_compute_jobs_running=False,model=models),next_actions=[
 'All sessions this continuation are terminal:36148entry/ABI,13389freshpair,99687Reviewer,47389initialmenu,17512finalmenu. Do not poll/restart them. No finite job remains running.',
 'DerivedCDI nowfreshloads andnewnativeentry copies130bytes into136byteexplicitreservationbelowheap. Originaldisc unchanged;169declaredchangedbytes. First10stagebytesoverlap60000bootpayload intentionally. EmulatorHLE/devices remain; not authenticated physicalconsole orwhole-sourcegame.',
 'Cold24000pair tracks gamefields equalallframes and1naturalkeypadcall matching fullCPUboundary;11compiled instructions is dynamic on that one path.23,875video framesmatch,125differ177..657; allafter657andfinalvideo/silentPCMmatch. Isolate startup timing versus early video effects; strict whole-run video/CPU/RAM equivalence not proved. Do not merge earlier8call1500checkpoint counts into this run.',
 'Advance larger recovered C/nativecomponents and nativegame linker/source packaging, broaden natural scenes/branches, install remaining logicalcoordinate/scene continuations, remove runtime providers and validate physicalcontrols/audio/performance/authenticated hardware. One compiled function is not the full decompilation.',
 'LocalReviewerDBRA/alignmentclaims rejected; actual65words130bytesvs136reserved. Curatedcandidate unassigned/unused; no newtraining. Keep Advertising27Bbase+retrieval, broaden grounded research/teachingeval before furtherSFT. V6/V7qualityrejected. NativeAdvertisingUI/cancellation and future256GBbenchmarks remain unverified. Never askunlock. P/O112/84pins unchanged.'])
 save(ledger_path,ledger)
 with(ROOT/'runs/agent-work-audit.jsonl').open('a')as f:
  for row in [dict(role='Codex coordinator',action='derived_native_CDI_built_and_fresh_HLE_boot_checked',build=cold['build_proof'],proof=str(cold_path),fresh_frames=24000,natural_native_calls=1,early_video_mismatches=125,whole_game_complete=False),dict(role='Local Reviewer',action='DBRA_and_alignment_claims_rejected_against_executed_checks',exact_prompt_response=str(Path(review['directory'])/'prompts-and-responses.txt'),new_training=False),dict(role='Game Assistant',action='actual_installed_menu_fresh_disc_scope_accepted',run=menu['run'],seconds=t['seconds'],generations=t['rounds'],native_Chat=False)]:f.write(json.dumps(dict(recorded_at=now.isoformat(),**row))+'\n')
 publication=dict(status='experimental_mixed_native_CDI_fresh_HLE_boot_published',directory=str(out),recorded_at=now.isoformat(),derived_disc=build['derived_disc'],derived_disc_sha256=build['derived_disc_sha256'],changed_disc_bytes=169,fresh_frames_per_disc=24000,natural_native_calls=1,early_video_differences=125,strict_video_equivalence=False,original_disc_modified=False,whole_game_source_rebuilt=False,physical_console_verified=False,whole_game_complete=False,new_training=False,new_native_Chat=False,preview_pins=pins,finite_jobs_running=False,menu_seconds=t['seconds'],menu_generations=t['rounds'],menu_words=len(t['answer'].split()),artifacts_sha256={str(p.relative_to(out)):sha(p)for p in out.rglob('*')if p.is_file()})
 save(out/'publication.json',publication);save(ROOT/'verification/native-disc-publication-current.json',publication);print(json.dumps({k:publication[k]for k in ['status','directory','menu_seconds','menu_words','whole_game_complete']}))
if __name__=='__main__':main()
