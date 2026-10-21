"""Publish combined processor evidence without widening the CPU-only long run."""
import json
import subprocess
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

FIRST=ROOT/'verification/native-formatter-C-processors/20261018T232627.290515Z/protocol.json'

def read(path):return json.loads(Path(path).read_text())

def main():
    parent_path=ROOT/'verification/native-formatter-C-runtime-publication-current.json'
    parent=read(parent_path)
    second_path=ROOT/'verification/native-formatter-C-processors-current.json'
    first,second=read(FIRST),read(second_path)
    assert first['status']==second['status']=='terminal_fresh_C_processors_equal'
    assert not first.get('sprint') and second['sprint'] and first['frames']==second['frames']==1600
    for proof in [first,second]:
        assert proof['audio_PCM_equal'] and all(row['different_frames']==0 for row in proof['comparisons'].values())
        assert proof['checkpoint_restores']==proof['host_guest_RAM_writes']==0
    deps=dict(parent['status_dependencies_sha256'])
    aliases=[]
    def add(path,expected=None):
        p=Path(path).resolve()
        assert p.is_relative_to(ROOT),str(p)
        digest=sha(p)
        if expected and digest!=expected:
            if p==ROOT/'scripts/run_native_formatter_C_processors.py':
                snapshot=Path(first['directory'])/'runner-as-run.py'
            elif p==ROOT/'scripts/biwn_live_window.py':
                controls_snapshot=read(ROOT/'verification/BIWN-run-controls-current.json')
                snapshot=Path(controls_snapshot['directory'])/'biwn_live_window-as-run.py'
            else:raise AssertionError('Unexpected mutated input '+str(p))
            assert sha(snapshot)==expected
            aliases.append(dict(as_run_path=str(p),as_run_sha256=expected,immutable_snapshot=str(snapshot)))
            p=snapshot;digest=expected
        if str(p)in deps:assert deps[str(p)]==digest,str(p)
        deps[str(p)]=digest
    add(parent_path)
    for pp,proof in [(FIRST,first),(Path(second['directory'])/'protocol.json',second)]:
        add(pp)
        for p,h in proof['source_sha256'].items():add(p,h)
        for p in Path(proof['directory']).rglob('*'):
            if p.is_file():add(p)
        for lane,expected in proof['report_sha256'].items():
            assert sha(Path(proof['directory'])/lane/'report.json')==expected
    # Freeze the actual dynamically loaded local graph as well as manifests.
    queue=[Path(v['library']) for v in first['C_processor_backends'].values() if 'library'in v]
    queue += [Path(read(ROOT/'verification/CPU-IRQ-bridge-experimental-candidate.json')['library']),
              Path(read(ROOT/'verification/local-CPU-IRQ-selector-author-current.json')['library'])]
    libraries=set()
    while queue:
        p=queue.pop().resolve()
        if p in libraries:continue
        libraries.add(p);add(p)
        output=subprocess.check_output(['otool','-L',str(p)],text=True)
        for line in output.splitlines()[1:]:
            name=line.strip().split(' (',1)[0]
            if name.startswith(str(ROOT)) and Path(name).resolve()not in libraries:queue.append(Path(name))
    controls_path=ROOT/'verification/BIWN-run-controls-current.json'
    controls=read(controls_path)
    add(controls_path)
    for p,h in controls['source_sha256'].items():add(p,h)
    add(ROOT/'scripts/biwn_live_window.py')
    add(Path(__file__))
    for p,h in deps.items():assert sha(p)==h,p
    now=datetime.now(timezone.utc)
    out=ROOT/'verification/native-formatter-C-processors-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    backends=second['C_processor_backends']
    summary=('The repaired 14,690-byte experimental BIWN disc now also passes two separate fresh 1,600-frame comparisons with C CPU, GPU, DSP and interrupt selection/entry providers together: the original movement prefix and a new Up+C run-control input. '
             'Full CPU state, all 2 MB RAM, saved GPU/DSP state, video, navigation and captured PCM match native execution of the same repaired disc at every recorded frame. '
             'The sprint-input pair observes the running state in both lanes. GPU/DSP and source IRQ providers have zero original fallback or rejection; C CPU ownership begins at mainstage4000. '
             'Bootstrap, HLE, devices, blitter/objectprocessor, interrupt queue/lines/ACK/vector resolution, commit/prefetch and cost services remain retained emulator components. These short tests have silent PCM and only the music DSP profile; media playback and hardware audio are not established. '
             'The earlier 24,975-frame merchant/outdoor equality remains a CPU-only replacement test with original GPU/DSP/IRQ providers; the combined providers have not completed that long route. '
             'Earlier formatter-versus-original-helper Deck position/video differences remain separate. No whole-game source rebuild, physical console boot, general speedup or new weight training is proved. '
             'Keyboard C+Up is the verified run mapping; Shift is unmapped. The current live preview remains in place.')
    current=dict(parent['current_status'])
    status='terminal_native_formatter_combined_C_processors_and_run_control_published'
    current.update(status=status,recorded_at=now.isoformat(),checked_answer=summary,checked_current_summary=summary,current_verified_route_summary=summary,
        C_processor_comparison=dict(frames_per_pair=1600,separate_pairs=2,
            first_proof=str(FIRST),first_proof_sha256=sha(FIRST),
            sprint_proof=str(Path(second['directory'])/'protocol.json'),sprint_proof_sha256=sha(Path(second['directory'])/'protocol.json'),
            all_recorded_fields_equal=True,PCM_byte_identical=True,PCM_nonzero_samples=0,
            run_state_frames=second['results']['C']['recorded_run_state_frames'],
            C_CPU_ordinary_steps=second['C_CPU_backend']['stats']['steps'],
            C_GPU_instructions=backends['GPU']['C_source_instructions'],C_DSP_instructions=backends['DSP']['owned'],
            source_IRQ_entries=backends['IRQ']['core']['Owned'],
            CPU_original_opcode_fallback_after_4000=0,GPU_original_fallback=0,DSP_original_fallback=0,
            DSP_profiles=backends['DSP']['profiles'],
            scope=second['scope'],merchant_long_route_with_combined_providers_verified=False),
        preview_run_control=dict(keys='C + Up',Shift_mapped=False,original_routine_proof=str(controls_path),
            fresh_gameplay_proof=str(Path(second['directory'])/'protocol.json'),
            native_keyboard_and_physical_controller_verified=False),
        long_route_scope='The inherited C_runtime_comparison is the earlier CPU-only replacement pair. It retains original GPU/DSP/IRQ providers; do not attach combined-provider claims to its24975frames.')
    report=ROOT/'reports/native-formatter-C-processors-and-controls.txt'
    current['report']=str(report)
    report.write_text(f'''BIWN: COMBINED C PROCESSORS AND RUN CONTROLS
{now.isoformat()}

{summary}

RUN CONTROL
Hold keyboard C with Up to run forward. The original 68000 input poll maps Jaguar C to held bit0x2000. The original dispatcher changes walking state5 to running state8. The established running path uses scale9 versus walking scale3, with a state-update transition. This does not promise a universal threefold displacement or higher emulation FPS.

The new fresh input holds Up+C from frame600 through1600. Both original-native and combined-C lanes record running state8 for {second['results']['C']['recorded_run_state_frames']} frames while those held bits are present. The live preview was not operated or restarted. Existing C is contextual and still backs out in menus. P resumes/pauses the preview.

COMBINED PROVIDERS
The sprint pair implements {second['C_CPU_backend']['stats']['steps']:,} ordinary CPU instruction steps in C after4000, {backends['GPU']['C_source_instructions']:,} GPU instructions and {backends['DSP']['owned']:,} DSP instructions. Source interrupt entry is exercised {backends['IRQ']['core']['Owned']:,} times. These are execution counters, not recovered-function coverage or a decompilation percentage. Full state comparisons occur at frame boundaries; arbitrary intra-frame interleavings and faults remain unverified.

The DSP route selected the music kernel only; its generated PCM is silent. Equal silent PCM is not audible-music evidence. No combined-provider merchant/return route has been proved here. The previous long CPU-only comparison and the earlier native formatter control differences retain their own scopes.

AUTHORSHIP
The coordinator wired these existing C providers and wrote the original-code controls fixture. Existing guided local wait-C and interrupt-selector authorship retain their prior receipts. No new model code or weight updates are attributed to this integration. Local control-help and status output reviews are recorded separately in the operator handoff.

Proofs:
{FIRST}
{Path(second['directory'])/'protocol.json'}
{controls_path}

Remaining: full source recovery and platform replacement, additional scenes and exception/IRQ tests, authenticated console boot, audible/physical audio verification, reliable representative local-model workflows and demonstrated training gains, and the future hardware test.
''')
    add(report)
    publication=dict(status=status,recorded_at=now.isoformat(),directory=str(out),current_status=current,report=str(report),
        status_dependencies_sha256=deps,immutable_input_aliases=aliases,additional_local_libraries_bound=len(libraries),
        integrity_mismatches=0,new_training=False,native_Chat_verified=False,default_promoted=False,goal_complete=False)
    save(out/'publication.json',publication)
    save(ROOT/'verification/native-formatter-C-processors-publication-current.json',publication)
    print(json.dumps(dict(status=status,files=len(deps),integrity_mismatches=0,run_state_frames=second['results']['C']['recorded_run_state_frames'],report=str(report))),flush=True)


if __name__=='__main__':main()
