"""Publish verified four-entry experimental build with unresolved differences."""
from datetime import datetime,timezone
from pathlib import Path
import json,hashlib,shutil,subprocess
ROOT=Path(__file__).resolve().parents[1];RT=Path.home()/'.lmstudio/local-ai-lab'
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 now=datetime.now(timezone.utc);out=ROOT/'verification/native-bundle-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 cold_path=ROOT/'verification/native-bundle-disc-cold-boot-current.json';cold=json.loads(cold_path.read_text());b=json.loads(Path(cold['build_proof']).read_text());math=json.loads(Path(cold['arithmetic_bundle_proof']).read_text());menu_path=ROOT/'verification/native-bundle-disc-menu-current.json';menu=json.loads(menu_path.read_text());t=menu['turn'];review=json.loads((ROOT/'verification/local-native-math-review-current.json').read_text());analysis=cold['comparison_analysis']
 assert cold['native_rebuilt_entries']==4 and analysis['actual_native_arithmetic_entry_events']==138014 and analysis['original_arithmetic_body_instructions_on_candidate']==0
 assert analysis['video_different_frames']==178 and analysis['tracked_state_different_frames']==19
 assert not t['quality_flags']and '178'in t['answer']and '19'in t['answer']
 deps={**b['source_sha256'],**math['source_sha256'],**math['execution_dependencies_sha256'],**cold['classification_artifacts_sha256'],**cold['runtime_dependencies_sha256']}
 for key in ['build_proof','entry_proof','arithmetic_bundle_proof']:deps[cold[key]]=cold[key+'_sha256']
 for path,digest in deps.items():assert sha(path)==digest,path
 assert sha(b['derived_disc'])==b['derived_disc_sha256']and sha(b['original_disc'])==b['original_disc_sha256']
 pins={}
 for name in ['interactive-preview-recipe.json','outdoor-restoration-preview-recipe.json']:
  d=json.loads((ROOT/'verification'/name).read_text());assert all(sha(path)==digest for path,digest in d['hashes'].items());pins[name]=dict(files=len(d['hashes']),all_hashes_match=True)
 models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],text=True));assert len(models)==1 and models[0]['status']=='idle'and models[0]['queued']==0
 menu.update(status='terminal_coordinator_accepted_native_bundle_scope',coordinator_review=dict(accepted=True,words=len(t['answer'].split()),note='Scopes component cases, actual native event counters, both behavioral differences and retained emulator/full-game/hardware limits. Earlier register-width/count wording preserved separately.'))
 save(menu_path,menu);save(ROOT/'verification/native-bundle-disc-menu-active.json',menu);save(Path(menu['directory'])/'protocol.json',menu)
 for name in ['CURRENT DECOMPILATION.txt','CURRENT LOCAL INFERENCE.txt']:shutil.copy2(ROOT/name,out/('previous-'+name))
 decomp=f'''BLACK ICE WHITE NOISE — FOUR-ENTRY NATIVE PROTOTYPE
Updated {now.isoformat()}

CURRENT RESULT
A new derived CDI fresh-boots through emulator HLE with four rebuilt original entry contracts: keypad (1B718), multiplication (E540), signed division (E588) and remainder (E60A). Recovered C arithmetic is compiled to actual M68000 code, with coordinator-written ABI/CCR glue and a new native divide-by-zero exception path. Original arithmetic bodies do not execute on the candidate. The rest of the game and CPU/GPU/DSP/device emulator remain original providers. This is a mixed build, not the whole source-built game.
The resident bundle is 1,650 bytes in a 1,656-byte reservation below the revised heap. New native startup copies the bundle, runs a resident finalizer that clears the original 4,096-byte zero staging window, restores registers and continues at 400A. The original CDI and checked previews are unchanged. The new CDI differs at 1,459 declared bytes, with other bytes/track metadata preserved.

EXECUTED EVIDENCE
The linked bundle passes 6,552 normal arithmetic comparisons against original execution: 2,192 multiplication, 2,180 division and 2,180 remainder cases. A further 512 zero-divisor cases execute native DIVU exceptions, with an inert RTE test handler. Return registers, PC, SR and both stack banks match; saved fault PC changes by the expected code relocation. Arbitrary handler changes, asynchronous timing and physical hardware are not thereby proved. The relocated keypad passes 5,151 cases; startup/clearing/register preservation passes 96 cases. Reference bytes match the extracted original disc stage.
Two fresh disc loads ran 24,000 frames each without a checkpoint, host game-RAM patch or CPU seed. The candidate reached patched arithmetic entry addresses 138,014 times: 78,694 multiply, 59,060 division and 260 remainder entries. No original arithmetic-body instructions executed. These address-entry counts are not direct reference/candidate call-count equivalence because original nested remainder calls differ from C internal calls. One natural keypad call matches the original boundary state. The 23,246,012 resident instruction count includes startup, arithmetic helpers and keypad; it is not a keypad-only count.
The final video matches, but 178 video frames differ (177;183-187;207-212;344-348;514-664;1374-1382;23580). Nineteen tracked-state frames differ, all before frame 347; differences include startup player location/mode/tile and movie flags. Tracked scene, equipment and movie-controller fields match throughout. This is not strict whole-run CPU/RAM/video equivalence. PCM matches but remains silent, so audible output is unproved. The new build remains experimental and is not promoted into P/O.

STARTUP DIFFERENCE INVESTIGATION
Two separate 1,000-frame ablations show heap-boundary changes alone match the original video for every frame, while startup/copy changes alone reproduce the earlier one-entry prototype's 125 differences exactly. This isolates that earlier effect to the startup/copy path; timing alone is not proved as its cause. The new build also clears staging and changes arithmetic execution, so its 178 differences must be investigated separately.

COMPILER RUNTIME FIX
The first math attempt exposed 68020 long-branch instructions in the compiler's default single libgcc archive, despite application compilation using -m68000. The failed attempt is preserved. A separate full runtime was rebuilt with -m68000 -msoft-float and is explicitly linked by Makefile.math/Makefile.bundle. Its linked arithmetic helpers pass the native comparisons; not every archive member is verified. No global compiler binary, PATH or default archive was replaced. Use tools/m68k-elf/m68000-soft/libgcc.a for these builds.

FILES / BUILD
Experimental CDI: {b['derived_disc']}
SHA256: {b['derived_disc_sha256']}
Show BIWN Native Disc.command reveals this new prototype. Earlier one-entry image remains preserved in builds/BIWN-native-partial. Main P/O preview launchers retain their checked profiles.
From lab root: .venv/bin/python scripts/build_biwn_native_bundle_disc.py
Component gate: .venv/bin/python scripts/check_biwn_native_bundle_math.py
Startup gate: .venv/bin/python scripts/check_biwn_native_bundle_disc_entry.py
Fresh disc pair: .venv/bin/python scripts/check_biwn_native_bundle_disc_cold_boot.py
Current execution proof: {cold_path}
Comparison details: {Path(cold['directory'])/'comparison-analysis.json'}
Runtime proof: {ROOT/'verification/m68000-libgcc-current.json'}

LOCAL AGENTS / REMAINING GOAL
Coordinator authored the ABI/flags/exception glue, staging cleanup, compiler-runtime fix and all harness/build changes; existing recovered C reused. No new model-authored C or weights. Local Reviewer returned {len(review['result']['text'].split())} words in {review['result']['seconds']} seconds and correctly rejected a physical-console/full-game claim. Its risk language is advisory, not an observed C defect; component evidence is time-scoped and the built disc requires its separate execution proof.
Exact review prompt/response: {Path(review['directory'])/'prompts-and-responses.txt'}
Installed local launcher: {len(t['answer'].split())} words in {t['seconds']} seconds, {t['rounds']} generation(s), accepted scope review. One earlier answer confused register width with test count; raw output retained and context clarified. No new native LM Studio Chat rendering is claimed.
Launcher exact input/output: {Path(menu['run'])/'session.json'}
Next: isolate and resolve video/state differences; broaden native routines/branches/scene routes; reconstruct/link the whole engine/game from source and remove remaining providers; validate audible output, physical controls/performance and authenticated console boot. Advertising base-plus-retrieval remains available; broader grounded research/teaching quality and future 256 GB hardware benchmarking remain. Full objective stays active and incomplete.
'''
 inference=f'''LOCAL AI — CURRENT WORKFLOW
Updated {now.isoformat()}

Open Desktop/Local AI Lab/Start Local AI.command: 1 Game Assistant; 2 Advertising Assistant; 3 game team; 4 advertising team; 5 LM Studio Chat; 6 saved runs; P main preview; O outdoors preview. Show BIWN Native Disc.command reveals the new experimental four-entry CDI.
Preferred model remains 27B 6-bit base plus retrieval, identifier advertising-scholar, 32K context/one worker shared across domains. Agent roles share weights and are not independent validators. Advertising V6/V7 were actually trained and quality-rejected; base plus retrieval remains preferred. No new weights were trained/promoted here. Broader grounded research/teaching evaluation remains necessary.

LATEST OUTPUT TEST
Actual installed launcher returned {len(t['answer'].split())} words in {t['seconds']} seconds, {t['rounds']} generation(s), no mechanical flags and accepted coordinator review. It distinguishes 6,552 normal and 512 zero-exception component cases from 24,000-frame fresh emulator execution, and discloses 178 video / 19 tracked-state differences. Host code selects checked evidence; lookup does not execute tests. One earlier answer described comparison width as a separate verification count; its raw output is retained and the context now names registers explicitly.
Exact session: {Path(menu['run'])/'session.json'}
Fresh installed MCP evidence: {ROOT/'verification/native-bundle-disc-installed-MCP-current.json'}

WHO DID WHAT
Coordinator: recovered-C reuse, native ABI/CCR/exception glue, startup cleanup, compatible 68000 runtime rebuild, derived discs, original/native checks and frontend evidence. Local Reviewer: {len(review['result']['text'].split())}-word advisory scope review in {review['result']['seconds']} seconds, correctly rejecting full-game/physical-console claims. Its conditional risk language is not an observed defect. Earlier DBRA/range review errors remain preserved; no independent validation or autonomous programming claim.
Reviewer exact prompt/response: {Path(review['directory'])/'prompts-and-responses.txt'}
Audit: {ROOT/'runs/agent-work-audit.jsonl'}

LM STUDIO CHAT / CURRENT LIMITS
The earlier genuine conversation BIWN — Local game team retains real role prompts/responses and generation metadata. New work here was headless and was not fabricated/imported into native Chat. The team helper retrieves current evidence on its next genuine turn. New Advertising Chat rendering and cancellation UI remain unverified; work can continue without screen access.
The native four-entry CDI is experimental, with unresolved video/state differences. P/O are unchanged, with all 112/84 pins matching. The original disc is unchanged. Read CURRENT DECOMPILATION.txt for complete execution scope. Future 256 GB hardware remains unbenchmarked. At publication all finite build/test/inference jobs were terminal, model idle and queue empty; that is a point-in-time receipt.
'''
 for root in [ROOT,RT]:
  (root/'CURRENT DECOMPILATION.txt').write_text(decomp);(root/'CURRENT LOCAL INFERENCE.txt').write_text(inference)
 reveal=ROOT/'scripts/reveal_biwn_native_disc.py';reveal.write_text('''from pathlib import Path
import json,subprocess
root=Path(__file__).resolve().parents[1]
latest=root/'verification/native-bundle-publication-current.json'
if latest.is_file():disc=Path(json.loads(latest.read_text())['derived_disc'])
else:disc=Path(json.loads((root/'verification/native-disc-build-current.json').read_text())['derived_disc'])
assert disc.is_file()
subprocess.run(['/usr/bin/open','-R',str(disc)],check=True)
''')
 native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';(native/'README.txt').write_text('''NATIVE BIWN COMPONENTS / FOUR-ENTRY EXPERIMENTAL DISC
Build this directory with make -f Makefile.bundle bundle.
It compiles keypad, multiply, signed-division and remainder contracts plus
resident startup cleanup. Makefile.math/Makefile.bundle explicitly select
the rebuilt68000soft-float libgcc archive; compiler default archive has
incompatible68020long branches. Full build commands and scope are in the
lab-root CURRENT DECOMPILATION.txt. Build the mixed disc from lab root:
.venv/bin/python scripts/build_biwn_native_bundle_disc.py

The1650byte resident bundle uses1656reserved heap bytes. Native startup
clears4096temporary staging bytes before original startup. The fresh24000
frame pair exercises138014arithmetic entry events, with178video and19tracked
state differences. This remains experimental, not a whole-game source build
or physical-console proof. Main P/O and original CDI remain unchanged.
Historical Makefile.movable/full-abi/default targets remain for reproduction.
Do not directly overwrite original routine bodies with these larger payloads.
''')
 reports=['native-bundle-disc-build-current.json','native-bundle-disc-entry-current.json','native-bundle-math-current.json','native-math-current.json','native-math-reference-original-disc-current.json','m68000-libgcc-current.json','native-startup-video-isolation-current.json','native-bundle-disc-cold-boot-current.json','native-bundle-disc-installed-MCP-current.json','native-bundle-disc-menu-current.json','local-native-math-review-current.json']
 for name in reports:shutil.copy2(ROOT/'verification'/name,out/name)
 scripts=['build_biwn_68000_libgcc.py','isolate_biwn_native_startup_video.py','check_biwn_native_math.py','build_biwn_native_bundle_disc.py','check_biwn_native_bundle_disc_entry.py','check_biwn_native_bundle_math.py','check_biwn_native_bundle_disc_cold_boot.py','finalize_biwn_native_bundle_evidence.py','review_biwn_native_math_local.py','check_biwn_native_bundle_disc_menu.py','publish_biwn_native_bundle.py','reveal_biwn_native_disc.py']
 for rel in ['chat_tools.py','assistant_chat.py']+['scripts/'+name for name in scripts]:
  target=out/'sources'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,target)
 shutil.copytree(native,out/'native-m68k')
 for name in ['CURRENT DECOMPILATION.txt','CURRENT LOCAL INFERENCE.txt']:shutil.copy2(ROOT/name,out/name)
 ledger_path=ROOT/'verification/goal-continuation-current.json';ledger=json.loads(ledger_path.read_text());shutil.copy2(ledger_path,out/'previous-goal-continuation.json')
 ledger.update(status='four_entry_native_disc_progress_with_behavior_differences_goal_incomplete',recorded_at=now.isoformat(),previous_turn_classification='progress: first derivedCDI native startup/keypad freshHLEboot and installed evidence.',this_turn_classification='progress: new Cmath/flags/zeroexception adapters, explicit68000runtime fix, 6552normal/512exception/5151keypad/96entrychecks, startup-control ablations, fresh24000fourentryimage run with138014arithmeticevents and0originalmathbodyinstructions.178video/19trackedstatedifferences recorded. LocalReviewer/menu tested; no previewpromotion.',goal_complete=False,latest_evidence_snapshot=str(out),latest_native_disc_build=str(ROOT/'verification/native-bundle-disc-build-current.json'),latest_native_disc_boot=str(cold_path),latest_native_arithmetic=str(ROOT/'verification/native-bundle-math-current.json'),latest_native_component_local_inference=str(menu_path),latest_MCP_check=str(ROOT/'verification/native-bundle-disc-installed-MCP-current.json'),preview_pin_checks=pins,live_processes=[],live_process_observation=dict(observed_at=now.isoformat(),finite_compute_jobs_running=False,model=models),next_actions=[
 'All sessions in this continuation are terminal:65825startupcontrols;83982math;41362bundleentry;34987bundlemath;48173freshpair;99975Reviewer;75700initialmenu;64489finalmenu. No running finite job; do not poll/restart them.',
 'Resolve178video and19tracked-state differences. New1650byte fourentrybundle is experimental only; P/O112/84pins andoriginalCDI unchanged.19tracked differences occurbefore347; onevideo mismatch persistsat23580; finalvideo/silentPCM match. No strict equivalence, fullsourcegame orhardwareproof.',
 'Earlier1000frame ablations reproduce previous125differences with startup/copyonly; heaponlymatchesoriginal1000. Do not call timing alone proved. Newresidentfinalizer clears4096staging bytes, so analyze currentdifferences afresh ratherthan equatingprofiles.',
 'Nativekernel gate6552normal +512zerotrap cases covers3mathentries; linkedkeypad5151 andentry96 separate. Nativezeroexception hasinertRTEhandler, expectedfaultPCrelocation; arbitraryhandler/aliasing/IRQ/hardware unverified. Actualcoldarithentryevents138014atpatchedaddresses; ref/nestedcalltotals arenot directlyequivalent. Resident23,246,012instructioncount includesstartup/math/keypad.',
 'Crosscompilerdefault68020libgcc contained61fflongbranches caughtbyfailedpreflight. Separatefullruntime rebuiltm68000/soft; Makefile.math/bundle explicitlylinktools/m68k-elf/m68000-soft/libgcc.a. Originalcompiler/defaultarchive unchanged. Linkedhelpers tested, noteveryruntimearchive member.',
 'Continue morelogicalengine/nativecomponents, fullscene/coordinate/task continuations, broaderbranches/routecoverage, source-linkedgame/CDpackaging andproviderremoval; validate performance/physicalcontrol/audio/authenticatedconsoleboot. KeepAdvertising27Bbase+retrieval; V6/V7qualityrejected, broaden groundedresearch/teachingeval beforefurtherSFT. Future256GBbenchmarks/nativeAdvertisingUI remain unverified; neveraskunlock.'])
 save(ledger_path,ledger)
 with(ROOT/'runs/agent-work-audit.jsonl').open('a')as f:
  for row in [dict(role='Codex coordinator',action='native_three_arithmetic_entries_and_runtime_fix',proof=str(ROOT/'verification/native-bundle-math-current.json'),normal_cases=6552,zero_exception_cases=512,new_training=False),dict(role='Codex coordinator',action='fourentry_disc_fresh_execution_with_unresolved_differences',proof=str(cold_path),frames=24000,arithmetic_entry_events=138014,video_differences=178,tracked_state_differences=19,preview_promoted=False),dict(role='Local Reviewer',action='advisory_scope_review_accepted_with_qualifications',exact_prompt_response=str(Path(review['directory'])/'prompts-and-responses.txt')),dict(role='Game Assistant',action='actual_installed_menu_scope_accepted',run=menu['run'],seconds=t['seconds'],generations=t['rounds'],native_Chat=False)]:f.write(json.dumps(dict(recorded_at=now.isoformat(),**row))+'\n')
 publication=dict(status='experimental_four_entry_native_bundle_published_with_differences',recorded_at=now.isoformat(),directory=str(out),derived_disc=b['derived_disc'],derived_disc_sha256=b['derived_disc_sha256'],native_entries=4,fresh_frames=24000,arithmetic_entry_events=138014,original_arithmetic_body_instructions=0,video_differences=178,tracked_state_differences=19,preview_promoted=False,whole_game_complete=False,new_training=False,new_native_Chat=False,finite_jobs_running=False,menu_seconds=t['seconds'],menu_generations=t['rounds'],menu_words=len(t['answer'].split()),preview_pins=pins,artifacts_sha256={str(p.relative_to(out)):sha(p)for p in out.rglob('*')if p.is_file()})
 save(out/'publication.json',publication);save(ROOT/'verification/native-bundle-publication-current.json',publication);print(json.dumps({k:publication[k]for k in ['status','directory','menu_seconds','menu_words','whole_game_complete']}))
if __name__=='__main__':main()
