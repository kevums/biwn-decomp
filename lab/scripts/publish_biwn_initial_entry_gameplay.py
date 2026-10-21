"""Publish initial-entry CPU gameplay without changing earlier immutable candidate scopes."""
import json
from datetime import datetime, timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT, sha, save

def read(p):
    return json.loads(Path(p).read_text())

def main():
    parent_path = ROOT/'verification/source-CPU-entry-publication-current.json'
    parent = read(parent_path)
    entry = read(ROOT/'verification/source-CPU-from-entry-gameplay-current.json')
    assert entry['status'] == 'terminal_source_CPU_from_entry_gameplay_equal'
    assert entry['frames'] == 1600 and entry['PCM_equal'] and not any(entry['comparisons'].values())
    CPU, backends = entry['C_CPU_backend'], entry['C_processor_backends']
    assert CPU['entry_gate']['original_before_owner_install'] == 0
    assert CPU['counts']['Original'] == CPU['counts']['Rejected'] == CPU['stats']['errors'] == 0
    assert backends['GPU']['counts']['Original'] == backends['GPU']['counts']['Rejected'] == backends['GPU']['stats']['errors'] == 0
    assert backends['DSP']['core_counts']['Original'] == backends['DSP']['core_counts']['Rejected'] == backends['DSP']['errors'] == 0
    assert all(backends['IRQ'][k][v] == 0 for k in ['core','selection'] for v in ['Original','Rejected'])
    directory = Path(entry['directory'])
    report = read(directory/'C/report.json')
    assert sha(directory/'C/report.json') == entry['report_sha256']
    run_frames = sum(f['locomotion_state'] == 8 for f in report['frames'])
    assert run_frames == 1000
    deps = dict(parent['status_dependencies_sha256'])
    def add(p, expected=None):
        p = Path(p).resolve()
        assert p.is_relative_to(ROOT)
        h = sha(p)
        assert expected is None or h == expected, str(p)
        assert str(p) not in deps or deps[str(p)] == h, str(p)
        deps[str(p)] = h
    frozen_parent = Path(parent['directory'])/'publication.json'
    assert sha(frozen_parent) == sha(parent_path)
    add(frozen_parent)
    for p,h in entry['source_sha256'].items():
        add(p,h)
    for p in directory.rglob('*'):
        if p.is_file():
            add(p)
    add(Path(__file__))
    for p,h in deps.items():
        assert sha(p) == h, p
    now = datetime.now(timezone.utc)
    out = ROOT/'verification/source-CPU-entry-gameplay-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    summary = (
        'The initial-entry C CPU candidate now passes1600freshframes of normal gameplay, including1000run-stateframes under scripted Up+C. '
        'Original CPU opcode execution is0 before owner installation and throughout the HLE-prepared entry-to-gameplay window. '
        'C GPU/DSP and source interrupt selection/entry are active; every recorded fullCPU,all2MBRAM,GPU/DSPstate,video,navigation,locomotion and held-input field matches the immutable same-core/disc native sprint control; silentPCM bytes also match. The native control was reused,not rerun. '
        'The earlier200frame startup proof remains separate historical evidence. The older24975frame merchant/return equality used sourceCPU only after nativebootstrap, with originalGPU/DSP/IRQ providers; do not attach this new initial-entry ownership to that long route. '
        'The independently running combined-provider merchant job is outside this terminal publication. '
        'FirmwareHLE,device/IRQline+ACK/vector resolution,hostcommit/prefetch/cost/clock and blitter/objectprocessor services remain supplied. '
        'This is finite host-C runtime equivalence on a repaired experimental disc, not a complete game decompilation,standalone console rebuild,authenticated BIOS boot,physical audio proof or general speedup. No new model weights or default promotion.')
    current = dict(parent['current_status'])
    current['initial_entry_startup_comparison'] = dict(current['source_CPU_from_initial_entry'])
    current.update(status='terminal_source_CPU_initial_entry_gameplay_published', recorded_at=now.isoformat(),
        checked_answer=summary, checked_current_summary=summary, current_verified_route_summary=summary,
        source_CPU_from_initial_entry=dict(frames=1600, CPU_owned=CPU['counts']['Owned'],
            ordinary_C_CPU_steps=CPU['stats']['steps'], HLE_return_adapters=CPU['stats']['HLE'],
            original_CPU_instructions_before_or_during_window=0, C_rejections=0,
            all_recorded_fields_equal=True, PCM_byte_identical=True, PCM_nonzero_samples=0,
            source_GPU_instructions=backends['GPU']['C_source_instructions'], source_DSP_instructions=backends['DSP']['owned'],
            source_IRQ_entries=backends['IRQ']['core']['Owned'], DSP_profiles=backends['DSP']['profiles'],
            reference_reused=True, scripted_running_frames=run_frames,
            native_keyboard_or_physical_controller_verified=False,
            division_provider_counts=entry['division_provider_counts'],
            proof=str(directory/'protocol.json'), proof_sha256=sha(directory/'protocol.json'),
            scope=entry['scope'], long_route_with_this_candidate_verified=False),
        long_route_scope='Earlier24975frame result: CPUafter4000 only, nativebootstrap/GPU/DSP/IRQ. New1600frame initial-entry result is a distinct candidate. Combined long merchant job is outside this publication.',
        whole_game_complete=False, physical_console_verified=False, new_training=False, default_promoted=False, goal_complete=False)
    report_path = ROOT/'reports/BIWN-initial-entry-gameplay.txt'
    current['report'] = str(report_path)
    report_path.write_text('BIWN — SOURCE CPU FROM INITIAL ENTRY THROUGH GAMEPLAY\n'+now.isoformat()+'\n\n'+summary+'\n\n'
        +f"CPU instructions owned: {CPU['counts']['Owned']}; ordinary C: {CPU['stats']['steps']}; HLE adapters: {CPU['stats']['HLE']}.\n"
        +f"GPU source instructions: {backends['GPU']['C_source_instructions']}; DSP source instructions: {backends['DSP']['owned']}; source IRQ entries: {backends['IRQ']['core']['Owned']}.\n"
        +'Division observations: '+json.dumps(entry['division_provider_counts'])+'\n'
        +'Coordinator reused/integrated the existing compiled instruction providers. This run adds no newly recovered high-level original game function and no new local-model code.\n'
        +'Full run protocol: '+str(directory/'protocol.json')+'\n'
        +'Previous startup publication: '+str(frozen_parent)+'\n')
    publication = dict(status=current['status'], recorded_at=now.isoformat(), directory=str(out),
        current_status=current, report=str(report_path), parent_publication=str(frozen_parent),
        status_dependencies_sha256=deps, evidence_files_verified=len(deps), integrity_mismatches=[],
        whole_game_complete=False, new_training=False, default_promoted=False, goal_complete=False)
    save(out/'publication.json', publication)
    save(ROOT/'verification/source-CPU-entry-gameplay-publication-current.json', publication)
    print(json.dumps(dict(status=publication['status'], files=len(deps), run_frames=run_frames)), flush=True)

if __name__ == '__main__':
    main()
