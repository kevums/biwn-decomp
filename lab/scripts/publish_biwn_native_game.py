"""Publish partial native game integration and honest local-output tests."""
from datetime import datetime,timezone
from pathlib import Path
import json,hashlib,shutil,subprocess
ROOT=Path(__file__).resolve().parents[1];RT=Path.home()/'.lmstudio/local-ai-lab'
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 now=datetime.now(timezone.utc);out=ROOT/'verification/native-game-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 game=json.loads((ROOT/'verification/native-button-game-current.json').read_text());movable=json.loads((ROOT/'verification/native-button-movable-current.json').read_text());menu=json.loads((ROOT/'verification/native-game-menu-current.json').read_text());review=json.loads((ROOT/'verification/local-native-movable-review-current.json').read_text());t=menu['turn']
 assert game['matched_video_frames']==game['identical_frame_end_CPU_count']==1500 and game['actual_game_calls']==8
 assert movable['cases']==5151 and movable['native_candidate_comparisons']==10302 and movable['payload_bytes']==130
 assert not t['quality_flags']and not t['answer'].lstrip().lower().startswith('no.')
 for path,digest in {**movable['source_sha256'],**game['artifacts_sha256']}.items():assert sha(path)==digest,path
 assert game['movable_proof_sha256']==sha(ROOT/'verification/native-button-movable-current.json')
 menu['status']='terminal_coordinator_accepted_scoped_native_game_answer';menu['coordinator_review']=dict(accepted=True,words=len(t['answer'].split()),note='Correct positive in-game emulator execution; discloses setup overlay/repair and unfinished bootable game. Retrieval is host-selected and prior failures are preserved.')
 save(ROOT/'verification/native-game-menu-current.json',menu);save(ROOT/'verification/native-game-menu-active.json',menu);save(Path(menu['directory'])/'protocol.json',menu)
 pins={}
 for name in ['interactive-preview-recipe.json','outdoor-restoration-preview-recipe.json']:
  p=json.loads((ROOT/'verification'/name).read_text());assert all(sha(path)==digest for path,digest in p['hashes'].items());pins[name]=dict(files=len(p['hashes']),all_hashes_match=True)
 model=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],text=True));assert len(model)==1 and model[0]['status']=='idle'and model[0]['queued']==0
 for name in ['CURRENT DECOMPILATION.txt','CURRENT LOCAL INFERENCE.txt']:shutil.copy2(ROOT/name,out/('previous-'+name))
 native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
 native_text=f'''NATIVE M68000 GAME INTEGRATION — PARTIAL
The recovered keypad-digit C function now runs as GCC-generated M68000 code during actual game frames. A 130-byte position-independent payload lives in memory reserved by the original game allocator. An 18-byte trampoline at the original entry resolves the returned memory handle. The original compactor moved the payload from {hex(movable['allocated_address'])} to {hex(movable['compacted_address'])}, updating its handle. All 5,151 original/compiled register, PC and SR cases pass before and after that move: 10,302 candidate comparisons. This tests real native compaction with the pinned emulated blitter, not an assumption that zero RAM is free.
Two isolated 1,500-frame runs replayed the coordinate-entry sequence with identical heap reservation. The candidate ran the new routine eight times, executing 179 compiled instructions. All eight call boundaries match all registers, PC and SR. Every frame's video hash and end-of-frame CPU match; final RAM differs only in the 17 changed bytes of the declared 18-byte entry trampoline. Final video and PCM also directly match the earlier unallocated baseline. PCM is silent in this route; audible playback is not proved.
This is retained-emulator execution of original game code plus one newly compiled routine. It uses explicit checkpoint setup, inherits the source checkpoint's 18 repair bytes and does not install a native cold-loader. Code-handle lifetime across new games, broader timing/routes, game linker/startup/disc packaging, remaining game code and physical-console validation remain unfinished. Original disc and both user previews are unchanged.
The coordinator adapted the earlier guided local-model shim to a relative call and wrote the trampoline, build changes and checks. The recovered C body was reused. The current movable assembly is coordinator-edited; the earlier absolute-call model shim remains a separate unchanged accepted artifact. No new weights were trained or promoted.
Build: make -f Makefile.movable movable (from {native})
Component/compaction proof: {ROOT/'verification/native-button-movable-current.json'}
Game-frame proof: {ROOT/'verification/native-button-game-current.json'}
'''
 old=(ROOT/'CURRENT DECOMPILATION.txt').read_text();tail=old.split('CLOCKED COORDINATE REQUEST\n',1)[1].split('\nREMAINING FULL GOAL\n',1)[0]
 decomp='BLACK ICE WHITE NOISE — PARTIAL RECONSTRUCTION\nUpdated '+now.isoformat()+'\n\n'+native_text+'\nCLOCKED COORDINATE REQUEST\n'+tail+'''\nREMAINING FULL GOAL
Native cold-loader and allocation lifetime, larger native components, linker/startup/Jaguar CD packaging; whole readable engine/game/branch reconstruction; logical coordinate and scene continuations; runtime-provider removal; uninterrupted combined preview profile; performance, physical controller/audio and console checks. Future 256 GB hardware remains unbenchmarked. Advertising research/education quality work remains as described in CURRENT LOCAL INFERENCE.txt. The full goal is active and incomplete.
'''
 inference=f'''LOCAL AI — CURRENT USER WORKFLOW
Updated {now.isoformat()}

EASY ENTRY
Open Desktop/Local AI Lab/Start Local AI.command.
1: Game Assistant. 2: Advertising Assistant. 3: Analyst/Restorer/Reviewer. 4: Researcher/Educator/Reviewer. 5: LM Studio Chat. 6: Saved runs. P: Main BIWN preview. O: Optional outdoors preview.
Preferred daily model: 27B 6-bit base plus retrieval, identifier advertising-scholar, 32K context, one worker shared across both domains. The launcher loads it when needed. Sequential agent roles share the same weights and are not independent verification. Advertising V6/V7 were actually trained and quality-rejected; base plus retrieval remains preferred. Broader grounded research/teaching evaluation remains necessary before further training. No new weights were trained or promoted in this session.

LATEST ACTUAL LAUNCHER TEST
The native-game question returned {len(t['answer'].split())} words in {t['seconds']} seconds, {t['rounds']} generation(s), with no mechanical quality flags and accepted coordinator review. The launcher fetched checked evidence; it did not rerun game tests. One compiled keypad routine actually ran eight times during 1,500 emulator-hosted game frames; a bootable native game remains unfinished. This is headless local inference through the real installed launcher, not new native Chat UI evidence.
Four earlier answers were rejected: one misleadingly began No despite describing successful in-game calls; the second repeated that lead and inflated 179 instructions to 1,790, correctly triggering a numeric guard; the third described eight calls as eight caller sites, while the trace shows eight calls from two distinct callers; the fourth invented a repair application frame after a host rewrite instruction asked for one. That instruction was fixed to distinguish inherited repairs and forbid unsupplied frame values. A separate numeric 68000 flag was a missing typed context value, also fixed. Their raw inputs and outputs remain saved. The context was simplified to distinguish actual in-game emulator execution from a new native cold-loader/physical-console build; successful retrieval is host-assisted, not autonomous source selection.
Accepted run: {menu['run']}
Exact system/input/response: {Path(menu['run'])/'session.json'}

WHO DID WHAT
Coordinator: relative-call adaptation, handle trampoline, build files, real allocator/compactor tests, paired game runs, evidence checks and frontend integration. Local Restorer supplied the earlier guided absolute-call ABI shim; the current movable version is coordinator-edited. Recovered C was reused.
Local Reviewer: advisory review in {review['result']['seconds']} seconds. Its scope summary was useful, but its claim that moving the whole blob breaks its internal relative call was wrong. The caller and callee move together. The review also exceeded its 180-word request ({len(review['result']['text'].split())} words). Raw output was preserved and the error explicitly rejected; no independent verification or model-quality pass is claimed.
Reviewer exact prompt/response: {Path(review['directory'])/'prompts-and-responses.txt'}
Reviewer decision: {ROOT/'verification/local-native-movable-review-current.json'}
Audit: {ROOT/'runs/agent-work-audit.jsonl'}

LM STUDIO CHAT
The earlier genuine conversation BIWN — Local game team remains available with actual role prompts/responses and generation metadata. The new work above was headless; it was not fabricated or imported into that native conversation. The native team helper reads current evidence on its next genuine turn. New Advertising Chat rendering and UI cancellation remain unverified. Work can continue without screen access.

BUILD / NEXT WORK
Isolated GCC 15.2.0/Binutils 2.45 toolchain: {ROOT/'tools/m68k-elf'}. Its 64 synthetic compiler smoke cases are separate from the 5,151 BIWN component cases. Current build: make -f Makefile.movable movable in {native}.
Next: native cold-loader integration and handle lifetime, broader game routes/timing, larger components and a linked/packaged console image. Continue whole-game reconstruction and grounded Advertising evaluation. User previews were left untouched; no native component was promoted into them. Future 256 GB hardware has not been benchmarked.
At publication all finite build/test/inference jobs were terminal; model idle, queue empty. This is a point-in-time receipt, not a promise of unattended background computation.
'''
 for root in [ROOT,RT]:
  (root/'CURRENT DECOMPILATION.txt').write_text(decomp);(root/'CURRENT LOCAL INFERENCE.txt').write_text(inference)
 (native/'README.txt').write_text('BIWN NATIVE COMPONENT BUILDS\n\n'+native_text+'''\nHistorical full-ABI component: make -f Makefile.full-abi full-abi.
That separate 132-byte absolute-call binary passed 5,151 isolated cases.
Do not directly overwrite the original 104-byte routine with either payload.
The movable target adds an allocated blob plus a handle-resolving entry.
The default Makefile retains the older scalar-contract experiment.
''')
 reports=['native-button-movable-current.json','native-button-game-current.json','native-game-menu-current.json','native-game-installed-MCP-current.json','local-native-movable-review-current.json']
 for name in reports:shutil.copy2(ROOT/'verification'/name,out/name)
 for relative in ['chat_tools.py','assistant_chat.py','scripts/check_biwn_native_button_movable.py','scripts/check_biwn_native_button_game.py','scripts/enrich_biwn_native_game_evidence.py','scripts/review_biwn_native_movable_local.py','scripts/check_biwn_native_game_menu.py','scripts/publish_biwn_native_game.py']:
  dest=out/'sources'/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/relative,dest)
 shutil.copytree(native,out/'native-m68k')
 for name in ['CURRENT DECOMPILATION.txt','CURRENT LOCAL INFERENCE.txt']:shutil.copy2(ROOT/name,out/name)
 ledger_path=ROOT/'verification/goal-continuation-current.json';ledger=json.loads(ledger_path.read_text());shutil.copy2(ledger_path,out/'previous-goal-continuation.json')
 ledger.update(status='native_compiled_component_game_integration_goal_incomplete',recorded_at=now.isoformat(),previous_turn_classification='no progress: preceding conversational turn answered preview running controls only; current sources and native proof were revalidated before implementation.',this_turn_classification='progress: movable native C component allocated and compacted by original game code; 5151 ABI cases at both locations; 1500 paired game frames, 8 real calls, all video/frame-end CPU match. Installed evidence/menu updated with preserved failed output tests.',goal_complete=False,latest_evidence_snapshot=str(out),latest_native_component=str(ROOT/'verification/native-button-movable-current.json'),latest_native_game_integration=str(ROOT/'verification/native-button-game-current.json'),latest_native_component_local_inference=str(ROOT/'verification/native-game-menu-current.json'),latest_MCP_check=str(ROOT/'verification/native-game-installed-MCP-current.json'),preview_pin_checks=pins,live_processes=[],live_process_observation=dict(observed_at=now.isoformat(),finite_compute_jobs_running=False,model=model),next_actions=[
 'All sessions from this continuation are terminal:64483movableABI,59891gamepair,78237Reviewer,97299/77121rejectedmenus,91537thirdmenu,49802fourthmenu,70608finalmenu. Do not poll or restart them.',
 'Implement actual native cold-loader/code-handle lifetime and linked image pipeline. Current host checkpoint setup called original allocator once and supplied explicit RAM patches; no native loader, disc patch or preview promotion. Trampoline resolves one allocated handle slot; startup must construct it from its returned handle, retain allocation and handle resets/releases safely.',
 'Movable130byte C payload plus18byte trampoline survives actual original compaction and passes5151full-register/SRcases both before and after. In paired1500frames,8actual game calls/179compiled instructions, all1500video hashes/frame-endCPU match. FinalRAM differs only17changedentrybytes. PCM matches but is silent. This is retained original emulator CPU executing original game plus one new native C routine; do not relabel it source-CPU-owned frames.',
 'Local Reviewer range warning wrong because internal relative caller/callee move together; advisory review partially rejected. First4status outputs failed (misleadingNo;wrong1790;eightcalls mislabeled eightcallsites;inventedrepairframe from misleadinghostrewriteprompt). Context simplified, final actualmenu accepted; no new weights. Preserve all prompts/rawresponses and correction provenance.',
 'Continue full readable coordinate caller/private frame/20F78scene integration, remaining game/branches, service-provider removal, uninterrupted current combined profile, performance and physical control/audio/console checks.',
 'Keep Advertising27Bbase+retrieval. V6/V7qualityrejected; broaden source-grounded research/education evaluation before further training. NativeAdvertisingrendering/cancellation and future256GBperformance unverified. Never ask unlock. P/O112/84pins unchanged.'])
 save(ledger_path,ledger)
 with(ROOT/'runs/agent-work-audit.jsonl').open('a')as f:
  for row in [dict(role='Codex coordinator',action='native_movable_payload_and_actual_game_call_integration',proof=str(ROOT/'verification/native-button-game-current.json'),coordinator_edited_relative_shim=True,frames=1500,calls=8,whole_game_complete=False),dict(role='Local Reviewer',action='advisory_review_partially_rejected_internal_relative_range_error',exact_prompt_response=str(Path(review['directory'])/'prompts-and-responses.txt')),dict(role='Game Assistant',action='actual_installed_menu_output_test_accepted_after_four_rejected_answers',run=menu['run'],seconds=t['seconds'],generations=t['rounds'],native_Chat=False)]:f.write(json.dumps(dict(recorded_at=now.isoformat(),**row))+'\n')
 publication=dict(status='partial_native_component_game_integration_published',recorded_at=now.isoformat(),directory=str(out),frames_per_lane=1500,actual_game_calls=8,compiled_instructions=179,component_cases_per_location=5151,movable_locations=2,all1500video_and_frame_endCPU_match=True,native_cold_loader=False,bootable_Jaguar_CD=False,whole_game_complete=False,new_training=False,preview_pins=pins,finite_jobs_running=False,menu_seconds=t['seconds'],menu_generations=t['rounds'],menu_words=len(t['answer'].split()),new_native_Chat_verified=False,artifacts_sha256={str(p.relative_to(out)):sha(p)for p in out.rglob('*')if p.is_file()})
 save(out/'publication.json',publication);save(ROOT/'verification/native-game-publication-current.json',publication);print(json.dumps({k:publication[k]for k in ['status','directory','menu_seconds','menu_words','whole_game_complete']}))
if __name__=='__main__':main()
