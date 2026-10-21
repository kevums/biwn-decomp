"""Publish a checked partial RNG source build and explicit remaining limits."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1];RT=Path.home()/'.lmstudio/local-ai-lab'
sys.path.insert(0,str(ROOT))
import native_rng_evidence


def read(path):return json.loads(Path(path).read_text())
def save(path,value):Path(path).write_text(json.dumps(value,indent=2)+'\n')
def sha(path):
    with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def main():
    summary=native_rng_evidence.load(ROOT);assert summary and summary['entries']==12
    cold=read(summary['proof']);build=read(cold['build_proof']);component=read(cold['rng_component_proof'])
    author=read(ROOT/'verification/local-native-rng-bounded-edit-current.json')
    menu_path=ROOT/'verification/native-rng-menu-current.json';menu=read(menu_path);turn=menu['turn']
    assert turn['rounds']==1 and not turn['quality_flags'] and len(turn['answer'].split())<=180,turn
    assert turn['host_evidence_lookup']['selected_model_context']['native_M68000_button_digit']['entries']==12
    assert sha(build['original_disc'])==build['original_disc_sha256']
    pins={}
    for name in ['interactive-preview-recipe.json','outdoor-restoration-preview-recipe.json']:
        recipe=read(ROOT/'verification'/name)
        assert all(sha(path)==digest for path,digest in recipe['hashes'].items())
        pins[name]=dict(files=len(recipe['hashes']),all_hashes_match=True)
    for name in ['chat_tools.py','assistant_chat.py','native_rng_evidence.py']:
        assert sha(ROOT/name)==sha(RT/name)
    models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],text=True))
    assert len(models)==1 and models[0]['identifier']=='advertising-scholar' and models[0]['status']=='idle' and models[0]['queued']==0
    now=datetime.now(timezone.utc);out=ROOT/'verification/native-rng-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    for name in ['CURRENT DECOMPILATION.txt','CURRENT LOCAL INFERENCE.txt']:
        shutil.copy2(ROOT/name,out/('previous-'+name))
    native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k'
    shutil.copy2(native/'README.txt',out/'previous-native-README.txt')
    analysis=cold['comparison_analysis']
    menu.update(status='terminal_coordinator_accepted_native_rng_status',
        coordinator_review=dict(accepted=True,words=len(turn['answer'].split()),
            note='Correctly separates eight tracked fields from actor snapshots/video, guided model authorship and retained emulator/full-game limits. Source lookup is host selected, not new test execution.'))
    save(menu_path,menu);save(Path(menu['directory'])/'protocol.json',menu)
    decomp=f'''BLACK ICE WHITE NOISE — NATIVE RNG PROTOTYPE
Updated {now.isoformat()}

CURRENT RESULT
Twelve original entry contracts now have native M68000 source implementations in an experimental CDI: eight RNG routines plus keypad decoding, multiplication, division and remainder. The resident bundle is 3,516 bytes in a 3,520-byte heap reservation. Startup copies it from the disc-delivered staging window, clears that 4,096-byte window and resumes the original game. The image changes 3,090 CDI bytes; all other disc bytes and metadata were checked against the preserved original.
This remains a mixed original/new game. Original game code and CPU/GPU/DSP/device emulation, HLE/CD bootstrap and drive providers remain. It is not a whole-game source rebuild or a physical-console result.

FRESH DISC EXECUTION
Original and derived images each ran 24,000 frames without a restored checkpoint, host RAM/code patch or host CPU seed. The candidate executed zero original RNG-body instructions and zero original arithmetic-body instructions. Public RNG entry counters observe init once and indexed four times; C-internal select/seed/fill calls do not revisit those original addresses. This does not mean all eight public entries were naturally reached.
All eight tracked player/scene fields match on all 24,000 frames. Video differs on 112 frames, versus 141 in the prior four-entry prototype. Actor records still differ on 393 of 400 samples taken every 60 frames, versus 394 previously; final actor positions also differ. The final RNG state table and final video match. PCM matches but contains no nonzero samples, so audible playback is unverified. The new original reference matches the prior reference on every recorded comparison field. Exact causes of residual actor/video differences are not fully isolated. No strict whole-run equivalence or FPS claim.

COMPONENT CHECKS
The eight RNG entry contracts match original execution in 1,682 fixed-RAM full-CPU/nonprivate-RAM cases, covering all 181 original RNG instructions. A separate 298-case Unicorn trace check matches ordered external reads/writes, mutable Q reads, selector rereads, raw signed selectors, overlapping selector/state storage and normalization. These fixtures overlap and are development checks; do not add their counts as independent examples. Private stack scratch and new resident code addresses are excluded from RAM identity; code immutability is checked separately.
Startup/register restoration/staging cleanup passed 96 cases. Heap allocation/compaction followed by native keypad behavior passed 5,151 cases. Relocated arithmetic passed 1,536 normal cases and 512 public-entry zero-exception cases. Those 512 cases use a declared inert RTE handler and expected fault-PC relocation. They do not establish zero-divisor behavior inside the new C RNG interface or arbitrary exception-handler behavior.

WHO DID WHAT
Coordinator: recovered logical algorithms and assembly evidence, full implementation plan, static diagnoses, ABI shims, linker/build/disc patches and verification.
Local Restorer: first full draft hit its 6,999-token limit after 342.165 seconds and was incomplete. Guided compact rewrite took 150.551 seconds but used the wrong header and failed static review.
Local Reviewer: complete correction took 165.607 seconds but left an unused variable and wrong CCR bit positions. A bounded JSON edit request then returned three exact edits in 10.411 seconds. Host code applied those literal edits to the local-model parent source, without manual C edits. That derived source compiled and passed the gates. It is not an unchanged full fenced-source response or autonomous decompilation. All roles used the same 27B base weights, so their agreement is not independent validation. No new weight training occurred.
Exact role prompts and responses are preserved in the four run directories listed in the publication report:
{ROOT/'verification/native-rng-publication-current.json'}
Latest bounded edit transcript:
{Path(author['directory'])/'prompts-and-responses.txt'}

ARTIFACTS / USE
Experimental CDI: {build['derived_disc']}
Checked C source: {component['canonical_source']}
ABI/header/build: {native}
From that directory, make -f Makefile.rng BUILD=build-rng builds the native ELF/binary with the explicit M68000 runtime. The existing Makefile.native retains the earlier four-entry build.
Desktop/Local AI Lab/Show BIWN Native Disc.command reveals the latest experimental image. Desktop/Local AI Lab/Start Local AI.command opens the assistants. Main P and optional O previews retain their112/84pinned dependencies; this CDI is not promoted into them. Click the preview before keyboard input; hold C+Up to run in normal gameplay. Arrows move/turn, Z=A, X=B, C=C, P pauses/resumes, M mutes and Esc closes.

NEXT
Investigate actor/video cadence at meaningful game boundaries; extend natural movement, combat and scene routes; finish larger logical/native engine modules and source link/package/provider removal. RNG zero-divisor behavior, authenticated/physical-console boot and audible output remain unverified. Full decompilation remains incomplete.
Advertising writing uses the installed same-model Copy Editor/Reviewer pair; see ADVERTISING WRITING.txt and the saved teaching example. V6/V7 training was real but quality-rejected; the daily27Bbase plus retrieval remains preferred. New native Chat rendering/cancellation and future256GBhardware benchmarks remain unverified. The LM Studio window observation timed out; no new Chat history was fabricated or imported.
'''
    inference=f'''LOCAL AI — CURRENT WORKFLOW
Updated {now.isoformat()}

Double-click Desktop/Local AI Lab/Start Local AI.command.
1 Game Assistant; 2 Advertising Assistant; 3 game team; 4 advertising team; 5 LM Studio Chat; 6 saved runs; P main preview; O outdoor preview.
Daily model:27B6bit base, advertising-scholar,32Kcontext, one shared worker. Roles share weights and run sequentially.

LATEST GAME OUTPUT TEST
The local model produced a native eight-routine RNG module with coordinator-provided algorithms/plan/diagnoses, followed by three model-proposed literal edits. No manual C edits or new weights. Full-source attempts took150–342seconds; the final targeted edit request took10.411seconds. Those are different task sizes, not a comparative speed benchmark.
The final derived source passed1,682full-CPU/RAM cases and298ordered-access cases. Its twelve-entry experimental CDI fresh-booted24,000frames through retained emulation. Eight tracked player/scene fields match every frame;112video frames and393of400actor snapshots still differ. Read CURRENT DECOMPILATION.txt for exact scope and limits.
Actual installed-menu status answer: {len(turn['answer'].split())}words in{turn['seconds']}seconds, one generation, no mechanical flags, coordinator source review accepted. The launcher selected saved checked evidence; the model did not execute tests. An earlier correct172-word answer was repeated because host checks falsely rejected its sampling interval and valid scope/authorship wording. Those false flags were fixed and an overclaim-negative check retained.
Exact current session: {Path(menu['run'])/'session.json'}
All RNG role prompts: {ROOT/'verification/native-rng-publication-current.json'}

ADVERTISING
Choose2 and type Correct grammar only: [text] for automatic Copy Editor → Copy Reviewer. /new returns to research. See ADVERTISING WRITING.txt for the nine short development cases, three headless plugin checks and reviewed AI-disclosure activity.27Bbase plus retrieval stays preferred; V6/V7adapters remain quality-rejected. No new training in this continuation.

CHAT / REMAINING WORK
The installed visible-local-team plugin can show exact role prompts/responses on a genuine Chat turn. Its helper now reads the latest native RNG evidence. The window observation timed out; no new native Chat display/cancellation proof or fabricated/imported history. Existing earlier BIWN Chat history remains separate from these saved local API runs. No unlock request is needed.
Previews and original CDI are unchanged. Full-game source rebuild, further gameplay/actor/timing/provider work, physical-console/audio checks and future256GBbenchmarks remain unfinished.
'''
    native_readme=f'''NATIVE M68000 SOURCE — CURRENT RNG PROTOTYPE
Updated {now.isoformat()}

make -f Makefile.rng BUILD=build-rng

Builds native-rng.elf/.bin: 3,516bytes at0x15EDC0, used by the checked experimental CDI with a3,520byte heap reservation. The Makefile includes dependency tracking and explicitly uses tools/m68k-elf/m68000-soft/libgcc.a. CFLAGS target -m68000 -msoft-float.
rng-native.c is a local-model full rewrite followed by three exact model-proposed edits. Coordinator supplied the recovered algorithm/ABI plan and diagnoses. rng-shims.S/rng-native.h preserve the caller frame, full registers and final CCR under the checked nonzero-divisor conditions. No original RNG instructions execute inside this module. Public math zero handling remains separately tested; C RNG zero-divisor behavior is unverified.
Eight RNG entries:1A6E0(init),1A6F8(current),1A77C(indexed),1A7F4(fill),1A87A(select),1A8C6(seed),1A8E2(get),1A8F8(set). Original remainderE60A is one of the already compiled three arithmetic entries, alongside keypad1B718.
Component proof: {cold['rng_component_proof']}
Fresh execution: {summary['proof']}
Experimental CDI: {build['derived_disc']}
CURRENT DECOMPILATION.txt explains retained original/emulator providers and actor/video differences. This is not the whole source-built game or a physical-console proof.
Historical Makefile.native/Makefile.optimized reproduce the earlier four-entry prototype. Earlier Makefiles, sources and rejected default-runtime build remain preserved.
'''
    for root in [ROOT,RT]:
        (root/'CURRENT DECOMPILATION.txt').write_text(decomp);(root/'CURRENT LOCAL INFERENCE.txt').write_text(inference)
        start=root/'START HERE.txt';text=start.read_text()
        if 'Hold C+Up to run'in text:pass
        else:text=text.replace('Arrows move/turn.','Arrows move/turn. Hold C+Up to run during normal gameplay.')
        start.write_text(text)
    (native/'README.txt').write_text(native_readme)
    reveal=ROOT/'scripts/reveal_biwn_native_disc.py';text=reveal.read_text()
    if "'native-rng-publication-current.json'"not in text:text=text.replace("['native-optimized-publication-current.json'","['native-rng-publication-current.json','native-optimized-publication-current.json'")
    reveal.write_text(text);shutil.copy2(reveal,RT/'scripts/reveal_biwn_native_disc.py')
    roles=[]
    for name in ['local-native-rng-current.json','local-native-rng-rewrite-current.json','local-native-rng-review-current.json','local-native-rng-bounded-edit-current.json']:
        role=read(ROOT/'verification'/name);roles.append(dict(proof=str(ROOT/'verification'/name),directory=role['directory'],status=role['status'],seconds=role.get('result',{}).get('seconds'),transcript=str(Path(role['directory'])/'prompts-and-responses.txt')))
        shutil.copytree(role['directory'],out/'model-runs'/Path(role['directory']).name)
    for path in native.iterdir():
        if path.is_file():dst=out/'native-source'/path.name;dst.parent.mkdir(exist_ok=True);shutil.copy2(path,dst)
    artifacts=[ROOT/name for name in ['CURRENT DECOMPILATION.txt','CURRENT LOCAL INFERENCE.txt','native_rng_evidence.py','chat_tools.py','assistant_chat.py','scripts/publish_biwn_native_rng.py','scripts/check_biwn_native_rng.py','scripts/build_biwn_native_rng_disc.py','scripts/check_biwn_native_rng_disc_entry.py','scripts/check_biwn_native_rng_disc_cold_boot.py','scripts/check_biwn_native_rng_linked_math.py','scripts/finalize_biwn_native_rng_evidence.py','scripts/check_biwn_native_rng_menu.py','scripts/reveal_biwn_native_disc.py']]
    for path in artifacts:
        dst=out/'workspace-source'/path.relative_to(ROOT);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dst)
    proof_names=['native-rng-original-reference-current.json','native-rng-current.json','native-rng-disc-build-current.json','native-rng-disc-entry-current.json','native-rng-linked-math-current.json','native-rng-disc-cold-boot-current.json','native-rng-menu-current.json']
    for name in proof_names:shutil.copy2(ROOT/'verification'/name,out/name)
    report=dict(status='experimental_twelve_entry_native_rng_build_published_with_remaining_differences',recorded_at=now.isoformat(),directory=str(out),
        derived_disc=build['derived_disc'],derived_disc_sha256=build['derived_disc_sha256'],native_entries=12,native_rng_entries=8,
        resident_bytes=3516,reserved_bytes=3520,CPU_component_cases=1682,ordered_access_cases=298,original_rng_instructions=181,
        fresh_frames_per_disc=24000,video_differences=112,eight_tracked_field_differences=0,actor_samples=400,actor_sample_differences=393,
        final_rng_table_equal=True,final_actors_equal=False,whole_game_complete=False,physical_console_verified=False,
        rng_zero_divisor_verified=False,new_training=False,new_native_Chat=False,preview_promoted=False,
        source_derivation=author['source_derivation'],coordinator_manually_edited_C=False,coordinator_supplied_algorithm_plan_and_diagnoses=True,
        role_runs=roles,preview_pins=pins,menu_seconds=turn['seconds'],menu_generations=turn['rounds'],menu_words=len(turn['answer'].split()),
        menu_session=str(Path(menu['run'])/'session.json'),model_idle_receipt=models,
        artifacts_sha256={str(path):sha(path)for path in artifacts},next='Investigate actor/video cadence and extend real movement/combat/scene routes; continue larger native/logical engine modules and whole-game source link/provider removal.')
    save(out/'publication.json',report);save(ROOT/'verification/native-rng-publication-current.json',report)
    candidate_dir=ROOT/'training/native-code-candidates';candidate_dir.mkdir(parents=True,exist_ok=True)
    save(candidate_dir/'native-rng-guided-20261018.json',dict(group_id='BIWN23_eight_rng_native_entry_family_20261018',assignment='unassigned',used_in_training=False,heldout=False,
        roles=roles,accepted_source=component['canonical_source'],accepted_source_sha256=component['canonical_source_sha256'],
        component_proof=cold['rng_component_proof'],fresh_execution=summary['proof'],
        rules='Keep all initial failures, guided rewrites, literal edits, original fixtures and nested math dependencies in the same source group. Development-only evidence, not an independent holdout or new weight training. Nonzero-divisor scope, private-stack exclusions and remaining actor/video differences must travel with this candidate.'))
    ledger_path=ROOT/'verification/goal-continuation-current.json';ledger=read(ledger_path);save(out/'previous-goal-continuation.json',ledger)
    ledger.update(status='twelve_entry_native_rng_and_local_assistants_goal_incomplete',recorded_at=now.isoformat(),goal_complete=False,
        previous_turn_classification='progress: installed and checked Advertising copyeditor/reviewer workflow and reviewed teaching activity.',
        this_turn_classification='progress: eight native C RNG contracts,1682fullCPU/298access cases, new twelve-entry CDI,96startup/5151keypad/1536math/512publiczero cases, fresh24000pair;112video differences,0eight-field differences,393/400actor-sample differences. Guided local source and three literal model edits; no new weights or manual C edits.',
        latest_native_rng_publication=str(ROOT/'verification/native-rng-publication-current.json'),latest_native_disc_build=cold['build_proof'],
        latest_native_disc_boot=summary['proof'],latest_native_RNG_component=cold['rng_component_proof'],latest_native_RNG_authorship=roles,
        latest_local_inference=report['menu_session'],latest_evidence_snapshot=str(out),preview_pin_checks=pins,live_processes=[],
        native_UI_observation='CUA LM Studio getApp timed out after120.6455s; no fresh UI generation or known lock state. Continue headless without asking for unlock.')
    ledger['next_actions']=[
        'All finite jobs from this continuation are terminal:34711truncatedauthor;69688originalreference;27264compactrewrite;84672review;82216literaledit;80057preflight;10144fullcomponent;17181build/entry;31694freshpair;14072relocatedmath;63131correctanswer/falsereviewflags;38787finalmenu. Do not poll/restart them.',
        'New native RNG source has eight nonzero-divisor contracts;12total source-backed native entries in the mixed CDI. Complete whole-game source rebuild is still unproved. P/O112/84pins and original remain unchanged.',
        'Investigate393/400sampled actor differences and112video frames, despite all eight tracked player/scene fields and final RNGtable matching. Same original reference verified; exact causes not fully isolated. Do not equate tracked-field agreement with complete state equivalence.',
        'Extend ordinary native-CDI movement/combat/elevator/outdoor routes and broader logical/native engine modules, including coordinate caller/20F78continuations. Finish whole-game link/package/provider removal; zero-divisor RNG, authenticated/physical console and audible output remain unverified.',
        'Local full-source attempts were incomplete/rejected; guided same-model review plus three bounded literal edits passed. Grouped training candidate is unused/unassigned. Avoid another narrow SFT loop or status-only polishing; pursue broader source tasks and grounded Advertising quality review.',
        'Advertising copyediting and source-grounded teaching workflows remain installed on daily27Bbase; V6/V7quality rejected. NativeChat display/cancellation and future256GBbenchmarks remain unverified. No unlock request and no preview restart.'
    ];save(ledger_path,ledger)
    save(ROOT/'verification/native-rng-continuation-active.json',dict(status='terminal_evidence_published_goal_incomplete',recorded_at=now.isoformat(),publication=str(ROOT/'verification/native-rng-publication-current.json'),candidate_accepted=True,disc_built=True,whole_goal_complete=False,live_finite_jobs=[]))
    with(ROOT/'runs/agent-work-audit.jsonl').open('a')as stream:stream.write(json.dumps(dict(recorded_at=now.isoformat(),action='published_eight_native_rng_contracts_and_fresh_twelve_entry_disc',publication=str(ROOT/'verification/native-rng-publication-current.json'),new_training=False,native_Chat=False,whole_goal_complete=False,authorship=summary['authorship']))+'\n')
    print(json.dumps({key:report[key]for key in ['status','derived_disc','native_entries','video_differences','eight_tracked_field_differences','actor_sample_differences','menu_seconds']},indent=2))


if __name__=='__main__':main()
