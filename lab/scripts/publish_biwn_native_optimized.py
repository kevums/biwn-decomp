"""Publish guided native optimization and precise live/replay/cost scopes."""
from datetime import datetime,timezone
from pathlib import Path
import json,hashlib,shutil,subprocess
ROOT=Path(__file__).resolve().parents[1];RT=Path.home()/'.lmstudio/local-ai-lab'
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 now=datetime.now(timezone.utc);out=ROOT/'verification/native-optimized-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 coldpath=ROOT/'verification/native-optimized-disc-cold-boot-current.json';cold=json.loads(coldpath.read_text());build=json.loads(Path(cold['build_proof']).read_text());math=json.loads(Path(cold['arithmetic_bundle_proof']).read_text());analysis=cold['comparison_analysis'];author=json.loads((ROOT/'verification/local-native-math-optimization-repair-current.json').read_text());cap=json.loads((ROOT/'verification/native-math-live-capture-current.json').read_text());replay=json.loads((ROOT/'verification/native-math-live-replay-current.json').read_text());menu_path=ROOT/'verification/native-optimized-disc-menu-current.json';menu=json.loads(menu_path.read_text());t=menu['turn']
 assert not t['quality_flags']and t['rounds']==1 and t.get('host_evidence_lookup'),'Expected current host-selected evidence and scoped one-generation answer'
 assert analysis['video_different_frames']==141 and analysis['tracked_state_different_frames']==6 and replay['completed_calls']==138014
 deps={**build['source_sha256'],**math['source_sha256'],**math['execution_dependencies_sha256'],**cold['runtime_dependencies_sha256'],**cold['classification_artifacts_sha256'],**cap['source_sha256'],**replay['source_and_dependencies_sha256']}
 for key in ['build_proof','entry_proof','arithmetic_bundle_proof']:deps[cold[key]]=cold[key+'_sha256']
 for path,digest in deps.items():assert sha(path)==digest,path
 assert sha(build['derived_disc'])==build['derived_disc_sha256']and sha(build['original_disc'])==build['original_disc_sha256']
 assert sha(author['candidate'])==author['candidate_sha256']==math['guided_local_candidate_sha256']
 pins={}
 for name in ['interactive-preview-recipe.json','outdoor-restoration-preview-recipe.json']:
  p=json.loads((ROOT/'verification'/name).read_text());assert all(sha(path)==digest for path,digest in p['hashes'].items());pins[name]=dict(files=len(p['hashes']),all_hashes_match=True)
 models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],text=True));assert len(models)==1 and models[0]['status']=='idle'and models[0]['queued']==0
 menu.update(status='terminal_coordinator_accepted_guided_optimization_scope',coordinator_review=dict(accepted=True,words=len(t['answer'].split()),note='Keeps guided model authorship/repair, same prior-input cost/replay scope, fresh-run differences and full-game/provider limits distinct. Prior wrong historical tool-route answer retained.'))
 save(menu_path,menu);save(Path(menu['directory'])/'protocol.json',menu);save(ROOT/'verification/native-optimized-disc-menu-active.json',menu)
 for name in ['CURRENT DECOMPILATION.txt','CURRENT LOCAL INFERENCE.txt']:shutil.copy2(ROOT/name,out/('previous-'+name))
 decomp=f'''BLACK ICE WHITE NOISE — GUIDED OPTIMIZED NATIVE PROTOTYPE
Updated {now.isoformat()}

CURRENT BUILD
Four rebuilt original entry contracts remain: keypad, multiplication, signed division and remainder. The resident bundle is now 1,236 bytes in a 1,240-byte reservation; its native startup clears the temporary 4,096-byte staging window. A new derived CDI fresh-boots through emulator HLE without a checkpoint or host game-RAM patch. It retains original game code and CPU/GPU/DSP/device/HLE/drive providers. This is not the whole source-built game.
The optimized fresh pair ran 24,000 frames per disc. Candidate entry-address counters record 142,753 arithmetic events (81,402 multiply;61,091 division;260 remainder) and zero original arithmetic-body instructions. One natural keypad call matches the original boundary state. Raw reference/native nested-call counts differ and are not direct call-count equivalence. The final image matches, but 141 video frames and 6 tracked-state frames still differ. Tracked-state differences occur at182,206-207,280,340,342; video also differs at23545/23580. PCM matches but is silent. Strict equivalence, audible output and hardware boot remain unproved; P/O are unchanged.
Compared with the first four-entry build, video mismatches fell from178to141 and tracked-state mismatches from19to6. This remains an experimental image and is not promoted into the checked previews.

ACTUAL-CALL SEMANTICS AND COST
A read-only fresh run recorded every138,014completed arithmetic call from the PREVIOUS four-entry prototype. Recording reproduced all24,000frame rows and finalRAM/GPU/machine/video/PCM exactly. Those138,014calls contain1,544distinct(entry,numerator,denominator)tuples; they are not138,014unique arithmetic inputs.1,435calls cross frame boundaries.
Every captured call matches isolated original68000execution for allD/Aregisters,PC,SR,USP/SSP. Python big integers separately matchD0/D1 on the same calls. The original and both compiled variants also match those same incoming CPU/argument snapshots. These are old-profile input replays, not a capture/replay of every new optimized fresh-run call. No zero divisor occurred in that actual-call set.
On that SAME input set, emulated retired arithmetic cycles are: original47,777,590; first compiled355,404,868; optimized165,636,192. The optimization uses about53%fewer emulated arithmetic cycles than the first compiled version. It remains more costly than the original on this measure. This is not whole-game FPS, wall time or physical-console speed.
The new linked bundle separately passes6,552normal arithmetic cases,512native zero-divisor exception cases with an inertRTEhandler,5,151keypad cases and96startup/register/clearing cases. Saved exceptionPCrelocation is expected; arbitrary handlers, tracing/IRQ timing and hardware remain outside that gate.

CONTROLLED DIFFERENCE INVESTIGATION
A1,500frame control holds the previous startup instructions,copy byte count,heap boundary and jump targets fixed, changing only resident code/padding. Against the original, tracked differences improve19to6 and video differences177to141 within that window. This supports lower-work arithmetic as a contributor independent of changing layout. The compact build has139video differences in that same early window and2later differences. Exact remaining causes are not fully isolated; no cycle/whole-run equivalence claim.
Earlier1,000frame controls located the one-entry prototype's125differences in startup/copy changes, not heap-only changes. Do not merge those older profile counts with this build.

LOCAL MODEL AUTHORSHIP
The local Restorer generated the optimized C from the coordinator's explicit plan: three unsigned16x16products, derive the signed product once, and share quotient/remainder computation. Its first draft lacked a runtime declaration and missed quotient/remainder sign restoration; it was rejected. A diagnosis-guided repair compiled and passed the gates, with its fenced source accepted unchanged. Coordinator wrote assembly, build scripts, harnesses and evaluation; recovered algorithms were reused. This is guided repair evidence, not autonomous decompilation or new weights.
Accepted prompt/response: {Path(author['directory'])/'prompts-and-responses.txt'}
Accepted C: {author['candidate']}
Initial failed draft: {ROOT/'verification/local-native-math-optimization-current.json'}
A grouped training candidate is saved at training/native-code-candidates. It is unassigned and unused for training or a held-out quality claim. Preferred model remains the shared27B6bitbase plus retrieval; AdvertisingV6/V7are still quality-rejected.

FILES AND REPRODUCTION
Experimental CDI: {build['derived_disc']}
SHA256: {build['derived_disc_sha256']}
Show BIWN Native Disc.command reveals this latest experimental image. Earlier images are preserved. Original CDI and P/O112/84pins remain unchanged. The current local build entry is make -f Makefile.native; it tracks headers and relinks after runtime/recipe changes, and reproduces the exact accepted machine bytes. The rejected manual default-runtime cache was quarantined as negative evidence.
From lab root: .venv/bin/python scripts/build_biwn_native_optimized_disc.py
Component gate: .venv/bin/python scripts/check_biwn_native_optimized_math.py
Startup gate: .venv/bin/python scripts/check_biwn_native_optimized_disc_entry.py
Fresh pair: .venv/bin/python scripts/check_biwn_native_optimized_disc_cold_boot.py
Actual-call capture/replay: scripts/capture_biwn_native_math_live.py and scripts/replay_biwn_native_math_live.py
Cost comparison: scripts/benchmark_biwn_native_math_live.py --optimized-proof verification/native-optimized-math-current.json
Current fresh proof: {coldpath}
Full difference/cost details: {Path(cold['directory'])/'comparison-analysis.json'}

LOCAL INFERENCE / NEXT WORK
Latest actual installed launcher: {len(t['answer'].split())}words in{t['seconds']}seconds, {t['rounds']}generation(s), coordinator-accepted scope. A prior summary incorrectly routed a noun phrase about repair validation as an action and selected historical formatter evidence. It was rejected; factual routing was corrected while direct repair/compile requests remain actions. A second correct answer triggered a false scope flag because the checker did not recognize no full source-built game; the regex was corrected and the final fresh launcher test passes in one generation. Source selection is host-assisted. New model work was headless, not newly rendered native Chat.
Exact launcher session: {Path(menu['run'])/'session.json'}
Next: explain residual transition/video timing and advance larger logical engine/native modules, broader routes, whole-game source link/package and remaining provider removal. Review pending grounded Advertising research/teaching outputs and strengthen quality before more SFT. Physical controls/audio/authenticated console and future256GBbenchmarks remain. Full objective stays active and incomplete.
'''
 inference=f'''LOCAL AI — CURRENT WORKFLOW
Updated {now.isoformat()}

Desktop/Local AI Lab/Start Local AI.command:1Game Assistant;2Advertising Assistant;3game team;4advertising team;5LMStudio Chat;6saved runs;Pmain preview;Ooutdoors preview. Show BIWN Native Disc.command reveals the latest experimental image. Preferred daily model remains27B6bitbase plus retrieval, identifier advertising-scholar,32Kcontext/one shared worker. Roles share weights; no independent-validator claim.

LOCAL CODE OUTPUT TEST
First optimization draft: rejected for missing declaration and division signs. Guided repair: {author['result']['seconds']}seconds, unchanged fenced C accepted after compilation and original/native component plus138,014prior-input full return-state replays. Coordinator supplied the optimization plan and repair diagnosis; recovered algorithms reused. No new model weight training or autonomous decompilation claim. Same-input emulated arithmetic cycles fell about53%; fresh game differences improved178to141video and19to6tracked-state frames, but strict equivalence remains unproved. Read CURRENT DECOMPILATION.txt for separate live/replay/control scopes.
Exact accepted source/prompt/response: {Path(author['directory'])/'prompts-and-responses.txt'}
Raw code: {author['candidate']}
Grouped candidate: training/native-code-candidates/native-math-guided-optimization-20261018.json (unassigned, unused).

LATEST STATUS INFERENCE
Actual installed launcher: {len(t['answer'].split())}words in{t['seconds']}seconds, {t['rounds']}generation(s), no mechanical flags and accepted coordinator review. It distinguishes the prior-recorded-input benchmark from fresh game execution and discloses residual differences/providers. Host code chooses fresh checked evidence. A prior ordinary-tool answer selected obsolete formatter counts after a factual noun phrase was misclassified as an action; raw output is retained and intent routing corrected. Direct repair/compile commands still use the action workflow. A correct follow-up hit a false whole-game scope flag; the wording checker was fixed, with both valid-limit and overclaim-negative checks, before the final fresh test.
Exact session: {Path(menu['run'])/'session.json'}
Fresh MCP proof: {ROOT/'verification/native-optimized-disc-installed-MCP-current.json'}

ADVERTISING / CHAT / CURRENT LIMITS
AdvertisingV6/V7were actually trained and quality-rejected; base plus retrieval remains preferred. Broader grounded research/teaching evaluations and source review remain needed before further SFT. This session adds a curated game-code candidate, not new weights. New Advertising native-Chat rendering/cancellation and future256GBbenchmarks remain unverified.
The earlier genuine BIWN — Local game team conversation retains actual role prompts/responses. New work was headless and not fabricated/imported into Chat. The team helper reads current evidence on its next genuine turn; no unlock request is needed. P/O and original CDI are unchanged. All finite jobs were terminal at publication; model idle/queue empty is a point-in-time receipt.
Audit: {ROOT/'runs/agent-work-audit.jsonl'}
'''
 for root in [ROOT,RT]:
  (root/'CURRENT DECOMPILATION.txt').write_text(decomp);(root/'CURRENT LOCAL INFERENCE.txt').write_text(inference)
 reveal=ROOT/'scripts/reveal_biwn_native_disc.py';reveal.write_text('''from pathlib import Path
import json,subprocess
root=Path(__file__).resolve().parents[1]
for name in ['native-optimized-publication-current.json','native-bundle-publication-current.json','native-disc-build-current.json']:
 path=root/'verification'/name
 if path.is_file():disc=Path(json.loads(path.read_text())['derived_disc']);break
else:raise RuntimeError('No native disc build found')
assert disc.is_file()
subprocess.run(['/usr/bin/open','-R',str(disc)],check=True)
''')
 native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';(native/'README.txt').write_text('''NATIVE BIWN BUILDS
Current target: make -f Makefile.native
This links the unchanged guided local Restorer repair in math-results-optimized.c,
coordinator ABI/exception shims, keypad C and native staging finalizer.
Explicit68000soft libgcc is required; default compiler archive has68020branches.
Build the derived image from lab root with:
.venv/bin/python scripts/build_biwn_native_optimized_disc.py
Current bundle1236bytes/reservation1240. Fresh24000frame tests retain141video
and6tracked-state differences; not strict equivalence/full-source/hardware proof.
Prior Makefile.bundle/math/movable/full-abi/default targets remain reproducible.
See lab-root CURRENT DECOMPILATION.txt for component/live/replay/cost scopes.
''')
 reports=['native-optimized-disc-build-current.json','native-optimized-disc-entry-current.json','native-optimized-math-current.json','native-optimized-disc-cold-boot-current.json','native-math-live-capture-current.json','native-math-live-replay-current.json','native-math-live-Python-numeric-current.json','native-math-live-cost-current.json','native-math-layout-control-current.json','local-native-math-optimization-current.json','local-native-math-optimization-repair-current.json','native-optimized-disc-menu-current.json','native-optimized-disc-installed-MCP-current.json','native-optimized-build-reproduction-current.json']
 for name in reports:shutil.copy2(ROOT/'verification'/name,out/name)
 scripts=['capture_biwn_native_math_live.py','replay_biwn_native_math_live.py','benchmark_biwn_native_math_live.py','author_biwn_native_math_optimized.py','repair_biwn_native_math_optimized.py','check_biwn_native_optimized_math.py','build_biwn_native_optimized_disc.py','check_biwn_native_optimized_disc_entry.py','check_biwn_native_optimized_disc_cold_boot.py','control_biwn_optimized_math_layout.py','finalize_biwn_native_optimized_evidence.py','check_biwn_native_optimized_disc_menu.py','publish_biwn_native_optimized.py','reveal_biwn_native_disc.py']
 for rel in ['chat_tools.py','assistant_chat.py']+['scripts/'+name for name in scripts]:
  target=out/'sources'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,target)
 shutil.copytree(native,out/'native-m68k')
 for name in ['CURRENT DECOMPILATION.txt','CURRENT LOCAL INFERENCE.txt']:shutil.copy2(ROOT/name,out/name)
 for key in ['directory','repair_of']:
  if key in author and Path(author[key]).is_dir():shutil.copytree(Path(author[key]),out/('author-'+key))
 ledgerpath=ROOT/'verification/goal-continuation-current.json';ledger=json.loads(ledgerpath.read_text());shutil.copy2(ledgerpath,out/'previous-goal-continuation.json')
 ledger.update(status='guided_native_optimization_with_improved_but_remaining_differences_goal_incomplete',recorded_at=now.isoformat(),previous_turn_classification='progress: fourentry native image, runtime fix,138014entry counters,178video/19state differences.',this_turn_classification='progress: read-only capture unchanged game; every138014prior live call matches original full returns andPythonD0/D1. Guided local C repair accepted unchanged,53percentlower same-input emulatedmathcycles. Newfresh24000frame image141video/6state differences, fixed-layout1500control also6states. Fresh intent-routing bug fixed and actualmenu checked. No preview/weights promotion.',goal_complete=False,latest_evidence_snapshot=str(out),latest_native_disc_build=str(ROOT/'verification/native-optimized-disc-build-current.json'),latest_native_disc_boot=str(coldpath),latest_native_arithmetic=str(ROOT/'verification/native-optimized-math-current.json'),latest_actual_call_replay=str(ROOT/'verification/native-math-live-replay-current.json'),latest_native_component_local_inference=str(menu_path),latest_MCP_check=str(ROOT/'verification/native-optimized-disc-installed-MCP-current.json'),preview_pin_checks=pins,live_processes=[],live_process_observation=dict(observed_at=now.isoformat(),finite_compute_jobs_running=False,model=models),next_actions=[
 'All sessions from this continuation are terminal:59744capture;78195firstmodeldraftrejected;88688repair;18733componentgate;26534build/entry;12431freshpair;41486fixed-layoutcontrol;29742wrong historicalmenu;57930correctcontent/falsescopeflag;95942finalmenu. No active finite job; do not poll/restart them.',
 'Current1236byte guided optimized bundle has4entries and1240byte reservation. Fresh24000pair:142753arithmeticevents,0originalmathbody instructions,1keypadcallboundarymatches;141video/6trackedstatedifferences,finalvideo/silentPCMmatch. Not strict equivalence/full-sourcegame/hardware; P/O112/84pins andoriginal unchanged.',
 '138014calls captured from PREVIOUS native profile exactlyreproduce its24000rows/finalmachine; original, priorC andoptimizedC allreturn samefullCPU on those inputs. PythonD0/D1also match.1544distinctargtuples;1435crossframecalls. Do not relabel as every optimizedfreshcall replay or add counts tocomponent cases.',
 'On SAME old capturedinputs, original47,777,590 /priorC355,404,868 /optimized165,636,192emulatedcycles (~53.4percentlowerthanpriorC, stillaboveoriginal). No FPS/walltime/hardware speedclaim. Fixed-layout1500control changesonlyresidentcode/padding andimprovestracked19to6; remainingcauses notfullyisolated.',
 'Accepted rawrepair source was locally generated in60.98s undercoordinator algorithmplan+sign/declarationdiagnosis. Firstdraftwrong; coordinator didnoteditacceptedC. No newweights; groupedtrainingcandidateunassigned/unused. Factualnounrepairvalidation accidentallytriggeredactionrouteandhistoricalfacts; narrowparserfixkeepsdirectactionsintact, finalinstalledmenuaccepted.',
 'Advance broader logicalRNG/engine/native modules andscene/coordinate/task continuations while trackingresidualtiming, then whole-sourcegame link/package/provider removal/physicalcontrols/audio/authenticatedconsole/performance. Avoid repeatingstatus-only loops or overclaimingcycledriftresolved.',
 'Review pending grounded Advertising research/teaching outputs from source and broaden quality beforefurtherSFT. Keep27Bbase+retrieval; V6/V7rejected. NewnativeAdvertisingUI/cancellation andfuture256GBbenchmarks unverified. Neveraskunlock.'])
 save(ledgerpath,ledger)
 with(ROOT/'runs/agent-work-audit.jsonl').open('a')as f:
  for row in [dict(role='Codex coordinator',action='actual_live_math_calls_captured_and_original_replayed',calls=138014,proof=str(ROOT/'verification/native-math-live-replay-current.json'),same_prior_profile=True),dict(role='Local Restorer',action='guided_C_optimization_repair_accepted_unchanged',prompt_response=str(Path(author['directory'])/'prompts-and-responses.txt'),coordinator_supplied_plan_and_diagnosis=True,source_edited_by_coordinator=False,new_training=False),dict(role='Codex coordinator',action='optimized_disc_fresh_run_and_fixed_layout_controls',proof=str(coldpath),video_differences=141,tracked_state_differences=6,preview_promoted=False),dict(role='Game Assistant',action='actual_menu_scope_accepted_after_noun_intent_routing_fix',run=menu['run'],seconds=t['seconds'],generations=t['rounds'],native_Chat=False)]:f.write(json.dumps(dict(recorded_at=now.isoformat(),**row))+'\n')
 pub=dict(status='guided_optimized_native_prototype_published_with_remaining_differences',recorded_at=now.isoformat(),directory=str(out),derived_disc=build['derived_disc'],derived_disc_sha256=build['derived_disc_sha256'],native_entries=4,fresh_frames=24000,arithmetic_entry_events=142753,prior_profile_actual_calls_replayed=138014,video_differences=141,tracked_state_differences=6,raw_guided_model_source_accepted_unchanged=True,preview_promoted=False,whole_game_complete=False,new_training=False,new_native_Chat=False,finite_jobs_running=False,menu_seconds=t['seconds'],menu_generations=t['rounds'],menu_words=len(t['answer'].split()),preview_pins=pins,artifacts_sha256={str(p.relative_to(out)):sha(p)for p in out.rglob('*')if p.is_file()})
 save(out/'publication.json',pub);save(ROOT/'verification/native-optimized-publication-current.json',pub);print(json.dumps({k:pub[k]for k in ['status','directory','menu_seconds','menu_words','whole_game_complete']}))
if __name__=='__main__':main()
