"""Publish current native build milestone without implying a full game."""
from datetime import datetime,timezone
from pathlib import Path
import hashlib,json,shutil,subprocess
ROOT=Path(__file__).resolve().parents[1];RUNTIME=Path.home()/'.lmstudio/local-ai-lab'
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def sha(p):
 with Path(p).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def main():
 now=datetime.now(timezone.utc);out=ROOT/'verification/native-build-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 native_path=ROOT/'verification/native-button-full-ABI-current.json';native=json.loads(native_path.read_text());assert native['status']=='terminal_recovered_C_native_button_digit_full_register_ABI_matches'and native['cases']==5151
 dependencies=dict(native['source_sha256']);dependencies.update(native['native_execution_dependencies_sha256']);dependencies[native['compiled_binary']]=native['compiled_binary_sha256'];dependencies[native['compiled_ELF']]=native['compiled_ELF_sha256']
 dependencies[native['toolchain_proof']]=native['toolchain_proof_sha256']
 for path,digest in dependencies.items():assert sha(path)==digest,path
 tools=json.loads(Path(native['toolchain_proof']).read_text());assert tools['status']=='terminal_toolchain_smoke_pass'
 for path,digest in tools['binaries_sha256'].items():assert sha(path)==digest,path
 native_menu_path=ROOT/'verification/native-button-menu-current.json';menu=json.loads(native_menu_path.read_text());t=menu['turn'];assert not t['quality_flags']and t['rounds']==1 and len(t['answer'].split())==93
 menu['coordinator_review']=dict(accepted=True,words=93,note='Correctly scopes one native component, guided assembly, emulator execution and no bootable game.64smoke cases belong to compiler checks, separate from5151BIWNcomparisons.')
 save(native_menu_path,menu);save(ROOT/'verification/native-button-menu-active.json',menu)
 clocked=json.loads((ROOT/'verification/clocked-coordinate-yield-current.json').read_text());assert all(clocked['direct_original_reference_files_match'].values())
 models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],text=True));assert len(models)==1 and models[0]['status']=='idle'and models[0]['queued']==0
 pins={}
 for name in ['interactive-preview-recipe.json','outdoor-restoration-preview-recipe.json']:
  d=json.loads((ROOT/'verification'/name).read_text());assert all(sha(path)==digest for path,digest in d['hashes'].items());pins[name]=dict(files=len(d['hashes']),all_hashes_match=True)
 reports=['native-button-full-ABI-current.json','native-button-digit-current.json','m68k-toolchain-current.json','m68k-toolchain-active.json','native-button-installed-MCP-current.json','native-button-menu-current.json','local-native-button-shim-current.json','local-native-button-full-abi-current.json','clocked-coordinate-yield-current.json','coordinate-yield-attach-current.json','clocked-coordinate-menu-current.json','local-clocked-coordinate-review-current.json','coordinate-task-bus-current.json','coordinate-task-execution-active.json']
 for name in reports:shutil.copy2(ROOT/'verification'/name,out/name)
 shutil.copytree(ROOT/'projects/black-ice-white-noise/restoration/native-m68k',out/'native-m68k')
 sources=['scripts/build_biwn_m68k_toolchain.py','scripts/check_biwn_native_button_digit.py','scripts/check_biwn_native_button_full_ABI.py','scripts/author_biwn_native_button_shim.py','scripts/check_biwn_clocked_coordinate_yield.py','scripts/check_biwn_coordinate_yield_attach.py','scripts/publish_biwn_native_build.py','chat_tools.py','assistant_chat.py','scripts/native_chat_team_context.py','projects/black-ice-white-noise/restoration/biwn_coordinate_yield_attach.c','projects/black-ice-white-noise/restoration/biwn_coordinate_yield_attach.h']
 for rel in sources:
  p=out/'sources'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,p)
 for folder in sorted((ROOT/'runs').glob('local-native-button-*')):
  if folder.is_dir():shutil.copytree(folder,out/'model-proposals'/folder.name)
 for name in ['CURRENT DECOMPILATION.txt','CURRENT LOCAL INFERENCE.txt']:shutil.copy2(ROOT/name,out/('previous-'+name))
 native_dir=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
 decomp=f'''BLACK ICE WHITE NOISE — PARTIAL RECONSTRUCTION
Updated {now.isoformat()}

NATIVE68000BUILD MILESTONE
The isolated GNU m68k-elf toolchain is installed: GCC15.2.0/Binutils2.45. Its64synthetic compiler smoke cases pass. They are separate from the BIWNroutine comparisons below. Official GNU release sources were used; GCC's officialSHA512manifest and prerequisite script checks passed. No systemPATHwas changed. The first bundled-zlib host build failed against Apple SDK headers and is preserved; supported system-zlib configuration resolved it. A checksum-manifest URL404was corrected to the official GCC release directory; the final build completed.
The existing recovered keypad-digit C function now compiles to132bytes of realM68000machinecode, with a native ABI shim.5,151unique comparisons against the original routine pass on the pinned native68000emulator core:3,072button/inputD0cases plus2,079additionalCCR/modecases. The2,112case condition-code matrix contains33overlaps with the base cases. All16registers,PC,SR, original argument/returnSPand nonprivate finalRAM match. All32CCRinputs and both user/supervisor modes are represented. Original function code does not execute on the candidate. Its104referencebytes match the extracted original disc stage. This is not physical console execution or a game-frame test.
The first model draft was incomplete/invalid and rejected. A guided scalar shim passed its3,072case contract but leftD1different from the original. A stricter proposal restoredD1withMOVEand failed flags. The coordinator supplied the MOVEMcorrection; the final localRestorer output was accepted byte-for-byte after the5,151case gate. Existing recovered C was reused; the model did not write that C body this turn. Full-register/SR comparison uses the pinned native core on both lanes; an original-case SRread differed in Unicorn. The rejectedMOVEvariant also fails the native core's SRcheck, so it was not accepted by switching references.
No game/disc image was patched. Link address0x10000is only an isolated component-test address. Native game call-site/frame integration, safe code placement/relocation, timing, game linker layout/startup/disc packaging and the remaining game code are unfinished.132bytes do not fit the original104byte function slot; do not treat the test binary as an in-place game patch.
Build files: {native_dir}
Build from that directory: make -f Makefile.full-abi full-abi
Checker from lab root: .venv/bin/python scripts/check_biwn_native_button_full_ABI.py
Proof: {native_path}

CLOCKED COORDINATE REQUEST
New coordinator-written attach code binds one native-boundaryDF60request to its actual coordinate CPU frame. The existing clocked instruction-compatible source runtime executes user instructions in17other task contexts, GPU work, firmware and five source interrupts, then completes once for the returned owning18FAA/SP/11saved registers.13,883CPUinstructions elapse;13,884completed monitor polls are not a current queue count. Twenty attach guards pass. No intermediate task snapshots or recorded MMIO/OP/firmware outputs are supplied by this check host.
All1,500frames/23,768,194CPUinstructions directly reproduce the earlier original reference's CPU/cost/warmRAM/finalRAM/video/finalmachine/PCMfiles. The source checkpoint inherits18repairbytes, with no new game-byte patch. CPU/GPU/IRQselection/entry have zero original/rejected execution fallback in this profile. DSP is inactive0and qualified; sound is not newly exercised. GPU internal instruction states and physical controls/hardware are not compared. The whole high-level logical coordinate caller is not installed in frames. Native frame/ABIand20F78scene streaming remain; HLE/CD/drive, ObjectProcessor/blitter/devices and core clock/queue/ACK-vector/commit/prefetch/cycle services remain providers.
Proof: {ROOT/'verification/clocked-coordinate-yield-current.json'}

EXISTING GAME PREVIEWS
Desktop/Local AI Lab/Play BIWN Preview.command is the main launcher. Click inside the window; arrows move/turn, C+Up runs, ZisJaguarA, XisB, CisC. Pstarts/pauses preview, Mmute, Esccloses.1thenX+CopensDeck;2thenX+CequipsBeretta;Zattacks/reads. Native code above is not promoted into either preview; the user's already-running instance was left untouched.
The primaryPprofile restores an unmodified source-produced merchant checkpoint, then applies56declared repairbytes in3patches. Its Deck/mail200, unarmed120, Beretta300 and elevator/outdoor1200frame checks pass. OptionalOretains the18byte outdoor profile and4,600frame building570loop; a separate6,000frame route reaches532. All112Pand84Opins still match.
Earlier source startup reaches unmodified merchant after23,538frames/395,449,715CPUinstructions with no original warmup/checkpoint or repair. The separate continuous merchant/elevator/outdoor chain reaches24,738frames/416,052,785CPUinstructions, applying18bytes after merchant. Those are bounded routes, not whole-game or standalone proof. The newer coordinate branches total3,400independent continuationframes; source reachability6,825/18,306instructionlocations and145/206entries is not decompilation percentage or all-disc coverage.

REMAINING FULL GOAL
Native code placement/game integration and console image pipeline; whole readable engine/game/branch reconstruction; logical coordinate/scene continuations; runtime-provider removal; uninterrupted current combined profile; performance and physical controller/audio/console checks. Future256GBhardware is unbenchmarked. Whole-game decompilation and a complete source-built JaguarCDremain incomplete. Advertising readiness and training decisions are in CURRENT LOCAL INFERENCE.txt.
Exact agent actions: {ROOT/'runs/agent-work-audit.jsonl'}
'''
 inference=f'''LOCAL AI — CURRENT USER WORKFLOW
Updated {now.isoformat()}

EASY ENTRY
Open Desktop/Local AI Lab/Start Local AI.command.
1 chats with Game Assistant;2 chats with Advertising Assistant;3 runs Analyst/Restorer/Reviewer;4 runs Researcher/Educator/Reviewer;5 opens LM Studio Chat;6 opens saved runs;Popens the BIWNpreview;Oopens optional outdoor preview. The trained v6option remains experimental and weaker.
Preferred daily model is27B6bitbase+retrieval, identifier advertising-scholar,32Kcontext/one worker shared across both domains. Sequential roles share weights and are not independent verification. The launcher loads it when needed. No newly trained specialist weights were promoted this turn. AdvertisingV6/V7really trained but were quality-rejected; base+retrieval remains preferred. Broader grounded research/education quality and new Advertising native-Chat rendering remain work.

FRESH OUTPUT TESTS
InstalledMCP/native-build question passed. Actual menu1returned93words in8.16seconds, one generation, no quality flags. It says one keypad routine compiles natively, gives5,151comparisoncases, identifies guided model assembly and emulator execution, and says no bootableJaguarCDimage exists.64compiler smoke cases are separate synthetic checks. The clocked-coordinate question separately returned129words in12.15seconds, one generation, no quality flags. Exact context selection is host code; lookup does not rerun game tests.
New typed evidence includes native_M68000_button_digit and native_m68k_toolchain. It validates current code/binary/compiler hashes. Current native result compares all16registers,SRand stack; it is one132byte component in a68000emulator, not a whole game image. Game call sites, safe placement/relocation, timing and packaging remain.
Native menu record: {menu['run']}
Native proof: {native_path}

WHO DID WHAT
Coordinator wrote the attach API/runtime wiring, toolchain/build files, native harnesses, ABI diagnosis and retrieval checks. LocalReviewer performed a headless scope/code audit in11.9seconds and correctly rejected a whole-engine/standalone claim. LocalRestorer proposed native ABI shims. Two proposals were rejected; the final strict-register version passed unchanged after coordinator-guided corrections, including an explicitMOVEMinstruction correction. The recovered C function body was reused, not newly model-authored. Exact prompts/responses and failed proposals are preserved in this publication and individual runs. This is guided output-test evidence, not proof of autonomous programming ability or new training.
Final accepted model prompt/response: {json.loads((ROOT/'verification/local-native-button-full-abi-current.json').read_text())['directory']}/prompts-and-responses.txt
Audit: {ROOT/'runs/agent-work-audit.jsonl'}

LM STUDIO CHAT
Earlier genuine Chat BIWN — Local game team contains actual native3role prompts/responses; its saved preset adoption and per-role generation metadata were verified. The new UI inspection timed out120seconds; lock state is unknown. This turn's model/code/menu work is headless and was not fabricated/imported into native Chat. The installed team helper reads current checked evidence on the next genuine Chat turn. No unlock request is needed. New Advertising rendering and cancellation UI remain unverified.

BUILD / NEXT WORK
GNU m68k-elf GCC15.2.0andBinutils2.45are installed under {ROOT/'tools/m68k-elf'};64compiler smoke cases pass. No build/model/testjob is currently queued or running; model is idle. All current native and clocked-request jobs are terminal. The native component build is make -f Makefile.full-abi full-abi in {native_dir}.
Next: safe code placement/relocation and real game call-site tests for this native routine, then larger native components and linker/startup/CDimage pipeline. Continue full decompilation and grounded Advertising research/teaching evaluation before more SFT. Current previews remain on their checked instruction-compatible runtime; future256GBhardware has not been benchmarked.
'''
 (ROOT/'CURRENT DECOMPILATION.txt').write_text(decomp);(ROOT/'CURRENT LOCAL INFERENCE.txt').write_text(inference)
 for name in ['CURRENT DECOMPILATION.txt','CURRENT LOCAL INFERENCE.txt']:shutil.copy2(ROOT/name,RUNTIME/name)
 for name in ['native-button-full-ABI-current.json','native-button-digit-current.json','m68k-toolchain-current.json']:shutil.copy2(ROOT/'verification'/name,RUNTIME/'verification'/name)
 ledger_path=ROOT/'verification/goal-continuation-current.json';ledger=json.loads(ledger_path.read_text());shutil.copy2(ledger_path,out/'previous-goal-continuation.json')
 ledger.update(status='concrete_native_build_and_clocked_request_progress_goal_incomplete',recorded_at=now.isoformat(),previous_turn_classification='progress: captured scheduler/77guards and genuine nativeChatfollowup plus installed menu.',this_turn_classification='progress: clocked native-boundary request/20guards with17other user contexts/5IRQs/13883CPUinstructions and1500frame direct original comparison; installed GNUm68ktoolchain64smokes; real recovered C+guided local assembly132byte native component passes5151full16register/PC/SRcases. Native menu93words8.16sonegeneration; clocked menu129words12.15sonegeneration.',goal_complete=False,latest_evidence_snapshot=str(out),latest_native_toolchain=str(ROOT/'verification/m68k-toolchain-current.json'),latest_native_component=str(native_path),latest_clocked_coordinate_backend=str(ROOT/'verification/clocked-coordinate-yield-current.json'),latest_coordinate_local_inference=str(ROOT/'verification/clocked-coordinate-menu-current.json'),latest_native_component_local_inference=str(native_menu_path),latest_MCP_check=str(ROOT/'verification/native-button-installed-MCP-current.json'),native_UI_observation='New CUA inspection timed out. Prior genuine BIWNteam Chat retained. New code proposals/review/menu are headless.',screen_locked=None,preview_pin_checks=pins,live_processes=[],live_process_observation=dict(observed_at=now.isoformat(),finite_compute_jobs_running=False,model=models),next_actions=[
 'All builds/tests/model calls are terminal. Do not poll/restart closed sessions13478/50204/7188(toolchain nowcomplete),24751/95875/8483/27772(modelproposals),18083/49499(nativechecks),87701/69868(native menus),8853/6101/19377/10622/43004/99042. No current queued work.',
 'Native toolchain ready attools/m68k-elf. First complete C+native-shim132byte component matches5151cases/all16regsPCSR. Original routine104bytes, next entry1B786leaves only110bytes: direct overwrite would overlap it. Design safe placement/relocation and original-callsite/game-frame tests before game patch. Consider code lifetime/allocator compaction and absoluteJSRrelocations; do not assume testaddress10000is free. Build toward native game linker/startup/CDpackaging, with retained-original mixed builds labeled partial.',
 'Final guided model MOVEMshimacceptedunchanged; first raw draft and first strict-registerMOVEproposal rejected. Earlier scalar126byte/3072case proof remains historical and does not include originalD1contract. Full SRgate uses pinned nativeM68000core; Unicorn originalSRread disagreed, but badMOVEalso fails native. Preserve both failed evidence and exact coordinator guidance; no new model Cbody or weights.',
 'Clocked DF60request backend executes actual source tasks/device/IRQwork and acknowledges owner once. Integrate entire high-level logical coordinate caller/private CPUframeABI and20F78scene streaming. Native-boundary request proof is not full logical-caller installation. Continue whole-game/branch/readable-engine coverage, runtime-provider removal, continuous combined profile and performance.',
 'Keep Advertising preferred27Bbase+retrieval. V6/V7qualityrejected; broaden source-grounded research/teaching evaluation before more training. New nativeAdvertisingrendering and cancellation remain unverified. UI timeout does not block headless work; never ask unlock.',
 'P/O unchanged112/84pinsmatch. No native component promoted into preview or disc. Whole-game/standalone console image, physicalhardware/controller/audio and future256GBperformance incomplete.'])
 save(ledger_path,ledger)
 with(ROOT/'runs/agent-work-audit.jsonl').open('a')as stream:
  for row in [dict(recorded_at=now.isoformat(),role='Codex coordinator',action='GNU_native_toolchain_built_and_recovered_C_cross_compiled',toolchain=str(ROOT/'verification/m68k-toolchain-current.json'),proof=str(native_path),model_wrote_C_body=False,game_image_patched=False),dict(recorded_at=now.isoformat(),role='Local Restorer',action='guided_native_ABI_shim_accepted_unchanged',prompt_and_response=inference.split('Final accepted model prompt/response: ')[1].split('\n')[0],full_ABI_cases=5151,coordinator_supplied_exact_MOVEM_correction=True,source_edited_by_coordinator=False,new_training=False),dict(recorded_at=now.isoformat(),role='Codex coordinator',action='native_installed_menu_accepted',run=menu['run'],words=93,seconds=8.16,generations=1,native_Chat=False)]:stream.write(json.dumps(row)+'\n')
 publication=dict(status='native_compiler_and_first_recovered_component_published',recorded_at=now.isoformat(),directory=str(out),toolchain_ready=True,toolchain_smoke_cases=64,native_game_function_cases=5151,native_binary_bytes=132,full_registers=16,CCR_input_states=32,execution_modes=2,guided_model_source_accepted_unchanged=True,model_wrote_recovered_C_body=False,native_game_frames_verified=False,bootable_Jaguar_CD=False,whole_game_complete=False,new_training=False,menu_words=93,menu_seconds=8.16,menu_generations=1,new_native_Chat_verified=False,preview_pins=pins,finite_jobs_running=False,model_status='idle',artifacts_sha256={str(p.relative_to(out)):sha(p)for p in out.rglob('*')if p.is_file()})
 save(out/'publication.json',publication);save(ROOT/'verification/native-build-publication-current.json',publication)
 print(json.dumps({key:publication[key]for key in ['status','directory','native_game_function_cases','menu_seconds','whole_game_complete']}))

if __name__=='__main__':main()
