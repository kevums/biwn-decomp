"""Publish classified gameplay findings without promoting either user preview."""
from datetime import datetime,timezone
import json,shutil,subprocess,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RT=Path.home()/'.lmstudio/local-ai-lab'

def read(p):return json.loads(Path(p).read_text())
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    import sys
    sys.path.insert(0,str(ROOT));import native_route_evidence
    facts=native_route_evidence.load(ROOT)
    menu_path=ROOT/'verification/native-fast-gameplay-menu-current.json';menu=read(menu_path);turn=menu['turn']
    assert turn['rounds']==1 and not turn['quality_flags'] and len(turn['answer'].split())<=180
    build_path=ROOT/'verification/native-fast-rng-disc-build-current.json';build=read(build_path)
    adaptive_path=ROOT/'verification/native-fast-adaptive-elevator-current.json';adaptive=read(adaptive_path);assert adaptive['both_reached_indoor_floor2']
    merchant_path=ROOT/'verification/native-fast-adaptive-merchant-current.json';merchant=read(merchant_path)
    assert merchant['status']=='terminal_fresh_adaptive_merchant_pair_classified'
    audio_analysis=read(ROOT/'verification/native-fast-feedback-audio-current.json');assert audio_analysis['both_nonzero_audio']
    for row in merchant['results'].values():assert not(row['observation']['errors']or row['observation']['copy_errors'])
    for path,digest in merchant['source_sha256'].items():assert sha(path)==digest,path
    assert merchant['build_proof_sha256']==sha(build_path)
    pins={}
    for name in ['interactive-preview-recipe.json','outdoor-restoration-preview-recipe.json']:
        recipe=read(ROOT/'verification'/name)
        for path,digest in recipe['hashes'].items():assert sha(path)==digest,path
        pins[name]=dict(files=len(recipe['hashes']),all_hashes_match=True)
    for name in ['chat_tools.py','assistant_chat.py','native_rng_evidence.py','native_route_evidence.py']:assert sha(ROOT/name)==sha(RT/name),name
    assert sha(build['original_disc'])==build['original_disc_sha256']
    now=datetime.now(timezone.utc);out=ROOT/'verification/native-fast-gameplay-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    for root,label in [(ROOT,'workspace'),(RT,'installed')]:
        for name in ['CURRENT DECOMPILATION.txt','CURRENT LOCAL INFERENCE.txt']:
            shutil.copy2(root/name,out/(label+'-previous-'+name))
    native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
    shutil.copy2(native/'README.txt',out/'previous-native-README.txt')
    audio={lane:row['nonzero_audio_samples']for lane,row in merchant['results'].items()}
    merchant_summary=('Both images reached floor2 and captured nonzero frontend PCM in the merchant route.'if merchant['both_reached_indoor_floor2'] and merchant['both_captured_nonzero_audio']else 'The merchant continuation did not yet prove both images reach the same audio sequence.')
    decomp=f'''BLACK ICE WHITE NOISE — NATIVE GAMEPLAY FINDINGS
Updated {now.isoformat()}

CURRENT RESULT
The latest experimental CDI contains eight C RNG routines, C keypad decoding and three source-assembled arithmetic helpers at their original addresses. This is a mixed original/new game using retained emulator CPU/GPU/DSP/HLE/CD/device providers. Full decompilation and a complete source-built game remain unfinished; physical-console and authenticated-boot results are unverified.

MOVEMENT FIDELITY — FIXED INPUT FAILS
The earlier 24,000-frame mostly idle test is preserved. Its eight tracked-field agreement did not establish normal movement fidelity. In a new 24,738-frame movement route, the prior compiled-math image missed the building entirely. The revised arithmetic image enters building312 atframe9875 versus original8538, misses the recorded elevator inputs and ends indoors onfloor0 while original ends loadingfloor1. Video differs on23,051frames;357of413every60frame actor snapshots differ. Original reference recordings reproduce on all recorded fields/video/actor samples. This is a failed fixed-input route, not whole-game equivalence.
Original movement route captured1,609,546nonzeroPCM samples startingframe15907; revised candidate stayed silent on its different route. That difference does not isolate the audio engine.

SEPARATE FEEDBACK-CONTROLLER ROUTES
A fresh route steers through the same three recovered waypoints using current position/yaw, then waits for each indoor floor before holding ordinary Up. Both images reach floor2/scene314 at identical final player coordinates11294,41344. Original enters building at8538, candidate8536; they finish9638and9636frames respectively. Input timing responds to game state and therefore differs. This functional result does not erase the fixed-input failure.
{merchant_summary}
Merchant continuation nonzeroPCM sample counts: original {audio['reference']}; candidate {audio['candidate']}. The PCM streams differ, including after leading silence is removed;702,940of4,259,044comparedint16samples differ. Audio starts at15859in original and15875in candidate. Final merchant-route playerX differs by2units (12832vs12834), with equalZ42385/mode2/floor2/scene314. These are captured callback samples, not a listening test or physical-console sound proof. See exact merchant results for route outcomes:
{merchant_path}
All new runs use fresh CDI content loads, ordinary pad inputs and read-only observers. No checkpoint restores, host game-state writes, marker repair or preview promotion.

SOURCE / COMPONENT CHECKS
Same guided local-model rng-native.c, unchanged. New arithmetic runtime-original.S assembles85instructions/220bytes byte-identical atE540/E588/E60A, without opcode arrays or an extra entry JMP. New numeric C-ABI bridge preserves required callee registers. Nonzero RNG components pass1,682fullCPU/nonprivateRAM cases and298ordered-access/reread cases. These are overlapping development fixtures, not independent examples. RNG zero-divisor behavior remains unverified.
New raw resident payload2,574bytes is padded942bytes to3,516bytes; heap reserve3,520bytes matches the previous image. Both native loaders execute7,625instructions/84,126cycles through400A in the retained CPU core. New loader/register/cleanup checks pass96cases and post-heap keypad checks5,151cases. Startup-only and actor cadence differences remain; matching loader cost is not whole-machine timing equivalence.

WHO DID WHAT / PROMPTS
Local Restorer/Reviewer previously produced RNG C under coordinator-supplied algorithms, plan and diagnoses, followed by three literal model edits. That C is unchanged here. Coordinator reconstructed the220byte arithmetic assembly, numeric ABI bridge, new build, control experiments and feedback policies. A new local Reviewer response was rejected: its stack arithmetic and caller-saved-register claims contradicted direct CPU execution. No code was changed from that bad review. Same27Bweights serve the roles; no independent-model validation or new weight training.
Latest exact local review and CPU counterevidence:
{ROOT/'verification/local-fast-rng-ABI-review-current.json'}
Earlier RNG author/edit transcripts:
{ROOT/'verification/native-rng-publication-current.json'}
Installed-menu local inference: {len(turn['answer'].split())}words, {turn['seconds']}seconds, {turn['rounds']}generation, no mechanical flags; coordinator source review accepted. The first answer was truthful but was unnecessarily repeated because the host rejected valid full-game hyphenation and lacked explicit numeric scene/floor fields. Those checks were corrected, including negative regression checks. The assistant reads saved evidence; it did not execute these game tests. No fresh native Chat UI observation is claimed.
Exact latest menu prompt/response:
{Path(menu['run'])/'prompts-and-responses.txt'}

ARTIFACTS / USE
Latest diagnostic CDI: {build['derived_disc']}
Rebuild native components: in {native}, run make -f Makefile.fast-rng BUILD=build-fast-rng. This makes the resident ELF/binary plus fixed-address runtime ELF/binary; scripts/build_biwn_native_fast_rng_disc.py assembles the partial CDI. The older recipes/artifacts remain available.
Desktop/Local AI Lab/Show BIWN Native Disc.command reveals this experimental image. Start Local AI.command opens Game/Advertising assistants and previews. Running preview and P/O112/84pinned dependencies were preserved. Click the preview; hold C+Up to run. Arrows move/turn; Z=A, X=B, C=C; Ppause/resume; Mmute; Escclose.

REMAINING WORK
Resolve fixed-input/actor/timing differences, continue natural combat/scene/audio routes, larger source modules and full-game link/package/provider removal. RNG zero divisors, authenticated boot and physical console remain unverified. Advertising Copy Editor/Reviewer and research/teaching workflows remain installed on daily27Bbase; V6/V7training candidates remain quality-rejected. Future256GBhardware and fresh native Chat display/cancellation benchmarks remain unverified.
'''
    inference=f'''LOCAL AI — CURRENT WORKFLOW
Updated {now.isoformat()}

Double-click Desktop/Local AI Lab/Start Local AI.command.
1 Game Assistant;2 Advertising Assistant;3 game team;4 advertising team;5 LM Studio Chat;6 saved runs;P main preview;O outdoor preview.
Daily model:27B6bit base, advertising-scholar,32Kcontext, one shared worker. Roles share weights and execute sequentially.

LATEST GAME OUTPUT TEST
The installed Game Assistant now reads the latest movement evidence. Native component checks pass, but the24738frame fixed-input route fails. A separate feedback controller gets both images tofloor2 at the same final coordinates. {merchant_summary}
Saved status response: {len(turn['answer'].split())}words in{turn['seconds']}seconds, one generation, no mechanical flags; reviewed against sources. Exact prompt/response: {Path(menu['run'])/'prompts-and-responses.txt'}
This is saved-evidence lookup and local inference, not a new test run. See CURRENT DECOMPILATION.txt for native build, source authorship, failed and passed scopes, and audio findings. The visible-local-team plugin reads the same evidence on its next genuine Chat turn. No new native UI check or invented/imported Chat history.

ADVERTISING
Choose2 and type Correct grammar only: [text] for automatic Copy Editor → Copy Reviewer. /new returns to research. See ADVERTISING WRITING.txt for the short development cases and reviewed AI-disclosure activity. Base plus retrieval stays preferred; V6/V7adapters remain quality-rejected. No new training in this continuation.

Whole game source rebuild, timing/actor/provider work, physical-console checks and future256GBbenchmarks remain unfinished. Your running preview is preserved. Click inside it and hold C+Up to run.
'''
    for root in [ROOT,RT]:(root/'CURRENT DECOMPILATION.txt').write_text(decomp);(root/'CURRENT LOCAL INFERENCE.txt').write_text(inference)
    native_readme=f'''NATIVE M68000 SOURCE — LATEST DIAGNOSTIC BACKEND
Updated {now.isoformat()}

make -f Makefile.fast-rng BUILD=build-fast-rng

Builds native-fast-rng.elf/.bin (2574linkedbytes at15EDC0) and runtime-original.elf/.bin (220bytes atE540). The CDI builder pads the resident payload to3516bytes, reserves3520heapbytes and keeps the preceding loader copy/cleanup cost. Eight C RNG entries and C keypad use resident code; three arithmetic helpers are source-assembled at original addresses, byte-identical. The same-address math counters therefore count expected source-backed execution. rng-native.c remains unchanged from the guided local-model parent plus three literal edits. Coordinator authored new assembly/bridge/build/tests. Nonzero RNG component1682CPU/298access gates pass; RNG zero divisors are unverified.
Fixed-input movement24738frame route fails; separate feedback route reachesfloor2 in both. {merchant_summary}
Full details: {ROOT/'CURRENT DECOMPILATION.txt'}
Latest CDI: {build['derived_disc']}
Historical Makefile.rng / Makefile.native preserve prior backend builds. Original game and emulator providers remain; this is not a whole-game source build or physical-console result.
'''
    (native/'README.txt').write_text(native_readme)
    reveal=ROOT/'scripts/reveal_biwn_native_disc.py';text=reveal.read_text();marker="for name in ['native-rng-publication-current.json',";assert text.count(marker)==1;text=text.replace(marker,"for name in ['native-fast-gameplay-publication-current.json','native-rng-publication-current.json',");reveal.write_text(text)
    proof_names=['native-fast-rng-current.json','native-original-runtime-current.json','native-fast-bridge-stack-current.json','local-fast-rng-ABI-review-current.json','native-fast-rng-disc-build-current.json','native-fast-rng-disc-entry-current.json','native-fast-loader-cost-current.json','native-gameplay-analysis-current.json','native-cadence-analysis-current.json','native-cadence-movement-analysis-current.json','native-fast-movement-analysis-current.json','native-fast-gameplay-analysis-current.json','native-fast-adaptive-elevator-current.json','native-fast-adaptive-merchant-current.json','native-fast-gameplay-menu-current.json','native-fast-feedback-audio-current.json']
    proofs={}
    for name in proof_names:
        p=ROOT/'verification'/name;shutil.copy2(p,out/name);proofs[str(p)]=sha(p)
    report=dict(status='experimental_native_fast_rng_gameplay_classified_goal_incomplete',recorded_at=now.isoformat(),directory=str(out),derived_disc=build['derived_disc'],derived_disc_sha256=build['derived_disc_sha256'],fixed_input_route_pass=False,feedback_elevator_route_pass=True,feedback_merchant_results=merchant['results'],preview_promoted=False,preview_pins=pins,original_disc_unchanged=True,proofs_sha256=proofs,menu_session=str(Path(menu['run'])/'session.json'),menu_seconds=turn['seconds'],menu_generations=turn['rounds'],new_training=False,native_Chat=False,whole_game_complete=False,source_sha256={str(p):sha(p)for p in [Path(__file__),ROOT/'chat_tools.py',ROOT/'assistant_chat.py',ROOT/'native_route_evidence.py',reveal]},guides_sha256={str(root/name):sha(root/name)for root in [ROOT,RT]for name in ['CURRENT DECOMPILATION.txt','CURRENT LOCAL INFERENCE.txt']})
    save(out/'publication.json',report);save(ROOT/'verification/native-fast-gameplay-publication-current.json',report)
    goal_path=ROOT/'verification/goal-continuation-current.json';goal=read(goal_path);goal.update(status=report['status'],recorded_at=now.isoformat(),this_turn_classification='Progress: versioned fixed-address arithmetic CDI,1682CPU/298access/96entry/5151keypad gates; old/new full24738movement failures classified; fresh feedback routes now exercised; latest grounded installed-menu answer passes after false host validation fix.',latest_evidence_snapshot=str(out),latest_native_fast_gameplay=str(ROOT/'verification/native-fast-gameplay-analysis-current.json'),latest_native_feedback_elevator=str(adaptive_path),latest_native_feedback_merchant=str(merchant_path),latest_local_inference=report['menu_session'],finite_process_handles={},live_processes=[],next_fidelity_action='Continue from classified native/feedback merchant evidence. Resolve fixed-input timing/actor differences while extending source modules; do not claim complete rebuild or promote preview. Advertising grounded scholarship/native UI/256GB benchmark requirements remain.');save(goal_path,goal)
    with (ROOT/'runs/agent-work-audit.jsonl').open('a')as f:f.write(json.dumps(dict(recorded_at=now.isoformat(),action='published_native_fast_gameplay_findings',publication=str(out/'publication.json'),fixed_input_pass=False,feedback_elevator_pass=True,merchant_nonzero_audio=audio,new_training=False,native_Chat=False,whole_goal_complete=False))+'\n')
    print('Published',out);print('Merchant audio:',audio);print('Menu:',len(turn['answer'].split()),'words',turn['seconds'],'seconds');print('Preview pins:',pins)

if __name__=='__main__':main()
