"""Publish scoped native controller progress, retaining failed gameplay evidence."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil,sys
ROOT=Path(__file__).resolve().parents[1];RT=Path.home()/'.lmstudio/local-ai-lab';sys.path.insert(0,str(ROOT))
import native_controller_evidence

def read(p):return json.loads(Path(p).read_text())
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')

def main():
    facts=native_controller_evidence.load(ROOT);assert facts['entries']==13
    bp=ROOT/'verification/native-controller-lean-disc-build-current.json';build=read(bp);fixed=read(facts['proof']);adaptive=read(ROOT/'verification/native-controller-lean-adaptive-merchant-current.json');audio=read(ROOT/'verification/native-controller-audio-current.json')
    author=read(ROOT/'verification/local-native-controller-current.json');cleanup=read(ROOT/'verification/local-native-controller-cleanup-current.json')
    pins={}
    for name in ['interactive-preview-recipe.json','outdoor-restoration-preview-recipe.json']:
        recipe=read(ROOT/'verification'/name)
        for p,digest in recipe['hashes'].items():assert sha(p)==digest,p
        pins[name]=dict(files=len(recipe['hashes']),all_hashes_match=True)
    for name in ['chat_tools.py','lab.py','assistant_chat.py','native_rng_evidence.py','native_route_evidence.py','native_controller_evidence.py']:assert sha(ROOT/name)==sha(RT/name),name
    assert sha(build['original_disc'])==build['original_disc_sha256']
    now=datetime.now(timezone.utc);out=ROOT/'verification/native-controller-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    for root,label in [(ROOT,'workspace'),(RT,'installed')]:
        for name in ['CURRENT DECOMPILATION.txt','CURRENT LOCAL INFERENCE.txt']:shutil.copy2(root/name,out/(label+'-previous-'+name))
    native=ROOT/'projects/black-ice-white-noise/restoration/native-m68k';shutil.copy2(native/'README.txt',out/'previous-native-README.txt')
    decomp=f'''BLACK ICE WHITE NOISE — NATIVE CONTROLLER MODULE
Updated {now.isoformat()}

CURRENT RESULT
A new experimental CDI adds direct native C controller polling to the eight C RNG entries, C keypad and three source-assembled arithmetic helpers:13source-backed entry contracts. Controller code directly writes/reads the Jaguar's four MMIO rows, then updates held-button and press-edge globals. Broader hosted C restoration/preview work remains a separate track;13is not the total decompiled-function count or a completion percentage.
The new image is still mixed original/new. Original game plus retained CPU/GPU/DSP/HLE/CD/device providers remain. Full-game source rebuilding, physical-console and authenticated-boot results remain unverified.

NATIVE SOURCE / CHECKS
Controller C and ABI wrapper compile to118bytes standalone versus124original bytes. Actual emulated two-port pad cases pass1,216fullD/A/PC/SR/USP/SSP/nonprivateRAM checks. Separate1,024arbitrary raw-row cases match ordered MMIO/RAM access widths, values and order. These are development fixtures, not independent examples or physical-controller/keyboard tests. All32original instruction locations are covered; the C body has33decoded instructions restricted to X-preserving operations for the lean wrapper. Private scratch stack/new code bytes are excluded from RAM identity; code immutability is checked.
The linked13entry bundle also passes the same controller checks and1,682RNGCPU/298ordered-access cases. Startup/heap cleanup passes96cases; post-heap keypad checks5,151cases. RNG zero-divisor behavior remains unverified.
The initial coordinator ABI wrapper took622native CPU cycles per controlled poll versus original510. The lean wrapper takes542; actual CDI entry including its JMP measured554cycles. These are retained-core controlled-call costs, notFPS or hardware-bus timing. The loader remains7,625instructions/84,126cycles through400A.
Resident code is2,694bytes padded822bytes to3,516, with the same3,520byte heap reservation. The disc changes2,369bytes; all other CDI bytes/metadata and the preserved original were checked.

GAMEPLAY — PASSES AND FAILURES
Fresh feedback route: original enters building at8538, candidate8536; after two floor ascents and the merchant approach they finish18,538and18,536frames respectively. Both end atX12832/Z42385, mode2/floor2/scene314 and capture nonzeroPCM:968,110original samples,998,216candidate samples. Candidate controller polling is naturally reached1,023,155times; it executes zero original controller-body instructions. Original RNG/keypad body counters are also zero. Arithmetic runs byte-identical source assembly at original addresses, so its address counters are expected nonzero.
Audio streams differ, including after removing leading silence:727,262of4,287,816comparedint16samples differ. This is captured frontend PCM, not a listening test or newly source-built DSP claim.
The separate24,738frame identical-input replay FAILS: the new13entry candidate misses the building and ends outdoors, while original ends loadingfloor1.22,456video frames differ;407of413every60frame actor snapshots differ. The preceding12entry arithmetic profile entered the building late and differed357of413samples. More source coverage has not established better timing fidelity. No whole-machine/whole-game equivalence claim.
All new gameplay runs use ordinary fresh CDI/HLE loads, normal pad input and read-only observers. No checkpoint restores, host guest-state writes or marker repair. Original reference recordings reproduce on recorded fields/video/actor samples.

LOCAL ROLES / EXACT PROMPTS
Author:24.09seconds for complete controller C under coordinator-supplied original assembly, full recovered algorithm and ABI plan. It included two unused helper definitions and failed strict compilation.
Reviewer:4.91seconds, same27Bweights. Correctly flagged unused helpers; its objection to repeated arithmetic on a nonvolatile local value was incorrect.
Repairer:4.88seconds, one exact literal edit deleting both unused definitions. The first host parser wrongly required two edits; the already returned combined deletion was accepted after exact token comparison, without another generation. Final C is Author source plus that model edit, not an unchanged full fenced-source output. Coordinator did not manually edit C.
Coordinator: original semantics/plan, conservative and lean ABI wrappers, X-neutral compiler-output guard, build/link/disc packaging, tests and source review. Roles share weights and are not independent validation. No new training or fresh native Chat UI observation.
Author/Reviewer transcript: {Path(author['directory'])/'prompts-and-responses.txt'}
Cleanup transcript: {Path(cleanup['directory'])/'prompts-and-responses.txt'}
Exact role and CPU evidence: {out}

USE / REBUILD
Latest diagnostic CDI: {build['derived_disc']}
Native sources: {native}
From that directory: make -f Makefile.controller-lean-bundle controller-bundle BUILD=build-controller-lean
This builds the native resident ELF/binary plus fixed-address arithmetic runtime, not the whole game. scripts/build_biwn_native_controller_lean_disc.py makes the declared partial CDI derivative after its component gates. Earlier12entry and conservative13entry artifacts remain available for comparison.
Desktop/Local AI Lab/Show BIWN Native Disc.command reveals the diagnostic CDI. Start Local AI.command opens Game/Advertising assistants. The running preview and P/O112/84pinned dependencies are preserved; this new disc is not promoted into them.
Click the preview first. Hold C+Up to run; arrows move/turn; Z=A, X=B, C=C; Ppause/resume; Mmute; Escclose.

NEXT
Continue full source/link/provider work, clock/actor/audio fidelity and normal gameplay coverage. A source-built on-disc variant of the previously verified marker-scan repair can extend building-to-outdoor testing while retaining this unmodified baseline. NativeChat rendering/cancellation, physical-console/authenticated boot and future256GBhardware benchmarks remain unverified. Advertising base/retrieval workflows are installed; the current broader two-paper source/teaching check and retrieval/repair fixes are recorded separately. V6/V7training candidates remain quality-rejected.
'''
    inference=f'''LOCAL AI — CURRENT WORKFLOW
Updated {now.isoformat()}

Desktop/Local AI Lab/Start Local AI.command:1Game Assistant,2Advertising Assistant,3game team,4advertising team,5LMStudioChat,6saved runs,Pmain preview,Ooutdoor preview.
Daily model:27B6bit advertising-scholar,32Kcontext/one shared worker. Roles execute sequentially on the same weights.

LATEST LOCAL CODE OUTPUT
Guided local Author produced native controller C in24.09s; same-model Reviewer4.91s; model cleanup4.88s. Coordinator supplied original recovered algorithm/plan, ABI shims, build and tests. The unchanged derived C passes1,216native fullCPU/RAM and1,024orderedMMIO cases, also after linking with the existing native game components. No new weights or independent model validation. These are different task sizes from prior code/status/writing examples, not a comparative speed benchmark.
The13entry experimental CDI supports the feedback merchant route and nonzeroaudio, but fixed-input replay still fails and actors/audio differ. Read CURRENT DECOMPILATION.txt for scope, prompts and artifacts. Current Game Assistant and next native visible-team helper process read this latest evidence; no new native Chat display was observed or fabricated.

ADVERTISING
Choose2 for research/copyediting or4 for Researcher→Educator→Reviewer. Correct grammar only: [text] invokes the two-pass writing workflow. /new returns to research mode.
A broader two-paper check exposed that merely naming both sources did not ensure actual methods pages were retrieved, and an automatic repair over-shortened the task. Balanced verified design/methods-page selection and a scope-preserving repair prompt are installed; final quality requires source/operator review. See CURRENT ADVERTISING.txt and ADVERTISING WRITING.txt. Base plus retrieval remains preferred; V6/V7adapters remain quality-rejected.

Your running preview is preserved. Click it and hold C+Up to run. Whole-game rebuilding, timing/actor/audio/provider work, physical console and future256GBbenchmarks remain unfinished.
'''
    for root in [ROOT,RT]:(root/'CURRENT DECOMPILATION.txt').write_text(decomp);(root/'CURRENT LOCAL INFERENCE.txt').write_text(inference)
    (native/'README.txt').write_text(f'''NATIVE M68000 SOURCE — CONTROLLER DIAGNOSTIC BUILD
Updated {now.isoformat()}

make -f Makefile.controller-lean-bundle controller-bundle BUILD=build-controller-lean

13source-backed entry contracts:8C RNG,C keypad,C controller scan,3same-address arithmetic assembly helpers. Linked payload2694bytes; CDI pads822to3516and reserves3520heapbytes. Controller C is local-model Author source plus one local-model helper-deletion edit; coordinator wrote ABI wrappers/build/tests. The lean wrapper requires the verified X-neutral body instruction restriction and full native flags gates. Full controller1216CPU/1024orderedMMIO and RNG1682CPU/298access gates pass. Current fixed-input route fails; feedback route reaches merchant/floor2/nonzeroPCM, with audio/timing/actor differences. This is not the whole source-built game or physical-console proof.
Latest CDI: {build['derived_disc']}
Full evidence/role transcripts: {ROOT/'CURRENT DECOMPILATION.txt'}
Historical Makefile.controller-bundle/Makefile.fast-rng/Makefile.rng recipes retain prior backends.
''')
    reveal=ROOT/'scripts/reveal_biwn_native_disc.py';s=reveal.read_text();marker="for name in ['native-fast-gameplay-publication-current.json',"
    if "'native-controller-publication-current.json'"not in s:
        assert s.count(marker)==1;reveal.write_text(s.replace(marker,"for name in ['native-controller-publication-current.json','native-fast-gameplay-publication-current.json',"))
    names=['local-native-controller-current.json','local-native-controller-cleanup-current.json','native-controller-current.json','native-controller-bundle-current.json','native-controller-rng-current.json','native-controller-disc-build-current.json','native-controller-fixed-analysis-current.json','native-controller-adaptive-merchant-current.json','native-controller-lean-current.json','native-controller-lean-bundle-current.json','native-controller-lean-rng-current.json','native-controller-lean-disc-build-current.json','native-controller-lean-disc-entry-current.json','native-controller-cost-current.json','native-controller-lean-fixed-analysis-current.json','native-controller-lean-adaptive-merchant-current.json','native-controller-audio-current.json']
    proofs={}
    for name in names:
        p=ROOT/'verification'/name;shutil.copy2(p,out/name);proofs[str(p)]=sha(p)
    sources=[Path(__file__),ROOT/'native_controller_evidence.py',ROOT/'native_route_evidence.py',ROOT/'chat_tools.py',ROOT/'lab.py',ROOT/'assistant_chat.py',reveal]
    for p in sources:shutil.copy2(p,out/('source-'+p.name))
    report=dict(status='thirteen_entry_native_controller_published_with_fidelity_failures_goal_incomplete',recorded_at=now.isoformat(),directory=str(out),derived_disc=build['derived_disc'],derived_disc_sha256=build['derived_disc_sha256'],native_entries=13,fixed_input_route_pass=False,feedback_merchant_route_pass=True,controller_natural_calls=facts['natural_controller_public_calls'],PCM_equal=False,final_feedback_player_fields_equal=True,original_disc_unchanged=True,preview_promoted=False,preview_pins=pins,proofs_sha256=proofs,source_sha256={str(p):sha(p)for p in sources},new_training=False,native_Chat=False,whole_game_complete=False,roles=[dict(role='local Author',seconds=24.09),dict(role='local Reviewer',seconds=4.91),dict(role='local Repairer',seconds=4.88)],scope='Native controller addition plus source-backed mixed-game CDI; more source coverage and passing component/feedback checks do not establish timing equivalence or complete decompilation.')
    save(out/'publication.json',report);save(ROOT/'verification/native-controller-publication-current.json',report)
    with (ROOT/'runs/agent-work-audit.jsonl').open('a')as f:f.write(json.dumps(dict(recorded_at=now.isoformat(),action='published_native_C_controller_and_simplified_ABI',publication=str(out/'publication.json'),native_entries=13,fixed_input_pass=False,feedback_merchant_pass=True,new_training=False,native_Chat=False,whole_goal_complete=False))+'\n')
    print('Published',out);print('Previews preserved',pins)
if __name__=='__main__':main()
