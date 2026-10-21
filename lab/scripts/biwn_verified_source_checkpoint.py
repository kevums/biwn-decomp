"""Validate source-owned checkpoint provenance without relabeling it original."""
import hashlib
import json
from pathlib import Path


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def verify_source_checkpoint(report_path, proof_path, core_path):
    report_path, proof_path, core_path = map(lambda p: Path(p).resolve(), [report_path, proof_path, core_path])
    proof = json.loads(proof_path.read_text())
    report = json.loads(report_path.read_text())
    assert proof['status'] == 'fresh_start_merchant_two_elevator_floors_outdoor_source_match'
    assert proof['all_comparison_gates_passed'] and proof['continuous_merchant_elevator_outdoor_chain_verified']
    assert proof['original_warm_frames'] == 0 and proof['initial_checkpoint_restored'] is False
    assert report_path == (Path(proof['directory']) / 'C/report.json').resolve()
    assert report['mode'] == 'C' and report['warm_original_frames'] == 0 and not report['errors']
    assert report['restored_original_checkpoint'] is None and report.get('restored_source_checkpoint') is None
    assert report['original_CPU_instructions'] == report['rejected_CPU_instructions'] == 0
    assert report['owned_CPU_instructions'] == proof['CPU_instructions'] > 0
    assert len(report['frames']) == report['requested_frames'] == proof['frames']
    assert report['core_sha256'] == sha(core_path)
    for key in ['GPU_counts', 'DSP_counts', 'source_IRQ_selection', 'source_IRQ_entry']:
        assert proof[key]['Owned'] > 0 and proof[key]['Original'] == proof[key]['Rejected'] == 0
    comparison = json.loads(Path(proof['comparison']).read_text())
    assert all(comparison['checks'].values())
    source = report_path.parent
    for name in ['final-RAM.bin', 'final-video.bin', 'final-serialized-state.bin', 'frontend-PCM.s16le']:
        expected = comparison['sha256'][name]
        assert expected[0] == expected[1] == sha(source / name), name
    assert report['frames'][-1]['RAM'] == sha(source / 'final-RAM.bin')
    repair = report['experimental_code_overlay']
    assert repair['original_disc_modified'] is False and repair['after_exact_restore'] is False
    assert repair['applied_before_frame'] == proof['repair_applied_before_frame']
    assert sum(len(bytes.fromhex(patch['replacement'])) for patch in repair['patches']) == proof['repair_bytes'] == 18
    return dict(origin='verified_source_execution', report=str(report_path), report_sha256=sha(report_path),
                source_proof=str(proof_path), source_proof_sha256=sha(proof_path),
                source_frame=proof['frames'], source_CPU_instructions=proof['CPU_instructions'],
                inherited_program_repair=repair, inherited_repair_bytes=proof['repair_bytes'],
                scope='Checkpoint produced by the checked source CPU/GPU/DSP/IRQ startup and merchant route. It contains the declared18byte repair. This continuation restores that source-owned machine; it is not a new cold start, original-emulator checkpoint, standalone runtime or whole-game proof.')
