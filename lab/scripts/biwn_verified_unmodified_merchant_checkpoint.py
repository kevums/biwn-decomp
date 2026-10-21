"""Accept only the distinct zero-repair cold-source merchant proof.

Used in a new frozen probe build. The existing outdoor checkpoint verifier
and preview recipes retain their earlier 18-byte-repair provenance.
"""
import hashlib
import json
from pathlib import Path


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def verify_source_checkpoint(report_path, proof_path, core_path):
    report_path, proof_path, core_path = [Path(p).resolve() for p in (report_path, proof_path, core_path)]
    proof = json.loads(proof_path.read_text())
    report = json.loads(report_path.read_text())
    assert proof['status'] == 'fresh_start_unmodified_merchant_source_match'
    assert proof['all_comparison_gates_passed'] is True
    assert proof['frames'] == 23538 and proof['repair_bytes'] == 0
    assert proof['original_warm_frames'] == 0 and proof['initial_checkpoint_restored'] is False
    assert report_path == (Path(proof['directory']) / 'C/report.json').resolve()
    assert report['mode'] == 'C' and report['warm_original_frames'] == 0 and not report['errors']
    assert report['restored_original_checkpoint'] is None and report.get('restored_source_checkpoint') is None
    assert report['experimental_code_overlay'] is None
    assert report['original_CPU_instructions'] == report['rejected_CPU_instructions'] == 0
    assert report['owned_CPU_instructions'] == proof['CPU_instructions'] > 0
    assert len(report['frames']) == report['requested_frames'] == proof['frames']
    assert report['core_sha256'] == sha(core_path)
    comparison = json.loads(Path(proof['comparison']).read_text())
    assert comparison['status'] == 'unmodified_source_merchant_prefix_comparison_pass'
    assert comparison['source_report'] == str(report_path)
    assert comparison['frames'] == proof['frames'] and comparison['CPU_instructions'] == proof['CPU_instructions']
    assert comparison['prefix_reference_core'] == report['core_sha256']
    assert comparison['checks'] and all(value is True for value in comparison['checks'].values())
    assert comparison['checks']['no_source_repair'] and comparison['checks']['reference_gate_is_real']
    source = report_path.parent
    for name in ['final-RAM.bin', 'final-video.bin', 'final-serialized-state.bin', 'frontend-PCM.s16le']:
        expected = comparison['sha256'][name]
        assert expected[0] == expected[1] == sha(source / name), name
    assert sha(source / 'final-RAM.bin') == proof['final_RAM_sha256'] == report['frames'][-1]['RAM']
    assert sha(source / 'final-serialized-state.bin') == proof['final_machine_sha256']
    for proof_key, report_key, count_key in [('GPU_counts', 'regular_GPU_report', 'counts'), ('DSP_counts', 'DSP_report', 'core_counts')]:
        observed = json.loads(Path(report[report_key]).read_text())
        assert observed[count_key] == proof[proof_key]
        assert observed[count_key]['Owned'] > 0 and observed[count_key]['Original'] == observed[count_key]['Rejected'] == 0
        assert not observed['errors']
    irq = json.loads(Path(report['CPU_IRQ_report']).read_text())
    for proof_key, count_key in [('source_IRQ_selection', 'selection'), ('source_IRQ_entry', 'core')]:
        assert irq[count_key] == proof[proof_key]
        assert irq[count_key]['Owned'] > 0 and irq[count_key]['Original'] == irq[count_key]['Rejected'] == 0
    assert irq['source']['errors'] == 0
    state = (source / 'final-RAM.bin').read_bytes()
    read = lambda address, size=2: int.from_bytes(state[address:address + size], 'big')
    final = dict(mode=read(0x49c60), floor=read(0x49c62), retained_scene=read(0x49c64), X=read(0x49c50, 4), Z=read(0x49c56, 4))
    assert final == proof['final_state'] == dict(mode=2, floor=2, retained_scene=314, X=12831, Z=42385)
    return dict(origin='verified_source_execution', report=str(report_path), report_sha256=sha(report_path),
                source_proof=str(proof_path), source_proof_sha256=sha(proof_path),
                source_frame=proof['frames'], source_CPU_instructions=proof['CPU_instructions'],
                inherited_program_repair=None, inherited_repair_bytes=0,
                scope='Exact unmodified merchant machine produced by the checked cold source CPU/GPU/DSP/IRQ run. No original warmup, checkpoint or inherited game-byte repair. This continuation is a source checkpoint restore, not a new cold start or standalone/whole-game proof. Any later repair must be separately declared.')
