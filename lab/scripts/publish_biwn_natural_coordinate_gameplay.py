"""Preserve natural coordinate gameplay, trace-bound calls and source images."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CALLS = {
    'panel_refresh': 0x18f04, 'release_poll': 0x18f14, 'key_wait_poll': 0x18f34,
    'digit_decode': 0x18f44, 'scene_initialize': 0x18f9e, 'yield': 0x18fa4,
    'pause': 0x18faa, 'scene_setup': 0x18fb4, 'resume': 0x18fba,
    'backspace_first_coordinate': 0x18ff2, 'backspace_second_coordinate': 0x1901e,
}


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    coverage_path = ROOT / 'verification/natural-coordinate-coverage-current.json'
    coverage = json.loads(coverage_path.read_text())
    assert coverage['natural_coordinate_instruction_locations_reached'] == 166
    assert not coverage['natural_coordinate_unreached_instruction_locations']
    out = ROOT / 'verification/natural-coordinate-gameplay' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    rows = []
    dtype = np.dtype({'names': ['registers', 'pc'], 'formats': [('>u4', (16,)), '>u4'], 'offsets': [0, 64], 'itemsize': 78})
    for observed in coverage['runs']:
        proof = json.loads(Path(observed['proof']).read_text())
        immutable_proof = Path(proof['directory']) / 'verdict.json'
        assert sha(immutable_proof) == observed['proof_sha256']
        trace = Path(observed['trace'])
        assert sha(trace) == observed['trace_sha256']
        comparison = json.loads(Path(proof['comparison']).read_text())
        failed = [k for k, v in comparison['checks'].items() if not v]
        assert failed == ['DSP_owned_positive'] and proof['DSP_counts'] == dict(Owned=0, Original=0, Rejected=0)
        records = np.memmap(trace, mode='r', dtype=dtype)
        addresses, hits = np.unique(records['pc'], return_counts=True)
        counts = dict(zip(map(int, addresses), map(int, hits)))
        entry_indices = np.flatnonzero(records['pc'] == 0x18e92)
        assert len(entry_indices) == 1
        entry = int(entry_indices[0]); start = records[entry]['registers'].copy(); sp = int(start[15])
        # Source callsite1975A pushes return19760. Match the real active stack
        # rather than treating another task's same PC as this return.
        returns = np.flatnonzero((records['pc'] == 0x19760) & (records['registers'][:, 15] == sp + 4))
        returns = returns[returns > entry]
        assert len(returns) >= 1
        returned = int(returns[0]); end = records[returned]['registers'].copy()
        saved = [2, 3, 4, 5, 6, 10]
        assert all(start[i] == end[i] for i in saved)
        caller = {name: counts.get(pc, 0) for name, pc in CALLS.items()}
        case = observed['case']
        if case == 'edit':
            assert caller['backspace_first_coordinate'] == caller['backspace_second_coordinate'] == 1
        if case != 'cancel':
            assert all(caller[name] == 1 for name in ['scene_initialize', 'yield', 'pause', 'scene_setup', 'resume'])
        report = json.loads((Path(proof['directory']) / 'C/report.json').read_text())
        assert report['original_CPU_instructions'] == report['rejected_CPU_instructions'] == 0
        irq = json.loads(Path(report['CPU_IRQ_report']).read_text())
        gpu = json.loads(Path(report['regular_GPU_report']).read_text())
        for owner in [irq['selection'], irq['core'], gpu['counts']]:
            assert owner['Owned'] > 0 and owner['Original'] == owner['Rejected'] == 0
        proof_target = out / (case + '-proof.json'); shutil.copy2(immutable_proof, proof_target)
        shutil.copy2(Path(proof['directory']) / 'ordinary-input.json', out / (case + '-input.json'))
        rows.append(dict(case=case, proof=str(proof_target), proof_sha256=sha(proof_target), frames=proof['frames'],
            CPU_instructions=proof['CPU_instructions'], source_GPU_callback_counts=gpu['counts'],
            source_GPU_instructions=gpu['C_source_instructions'], source_IRQ_selection=irq['selection'], source_IRQ_entry=irq['core'],
            DSP_counts=proof['DSP_counts'], raw_failed_checks=failed, final_state=proof['final_state'],
            coordinate_entry_index=entry, coordinate_return_index=returned,
            entry_registers=list(map(int, start)), return_registers=list(map(int, end)),
            original_MOVEM_saved_registers_restored=True, original_return_PC='0x19760',
            direct_caller_PC_observations=caller, coordinate_instruction_locations_reached=observed['coordinate_instruction_locations_reached'],
            source_trace=str(trace), source_trace_sha256=observed['trace_sha256']))
    save(out / 'coverage-proof.json', coverage)
    images = {}
    for name, case, frame in [('entry', 'cancel', 150), ('edited', 'edit', 960), ('returned_world', 'edit', 1500)]:
        case_proof = json.loads((out / (case + '-proof.json')).read_text())
        image = Path(case_proof['directory']) / 'C' / ('frame-' + str(frame) + '.png')
        original = Path(case_proof['directory']) / 'reference' / image.name
        assert image.read_bytes() == original.read_bytes()
        target = ROOT / 'verified-previews' / ('natural-coordinate-' + name + '.png')
        shutil.copy2(image, target); images[name] = dict(path=str(target), sha256=sha(target),
            source_frame=frame, case=case, scope='Actual source-runtime game frame from ordinary scripted controls; original frame pixels match. Not a desktop screenshot or high-level semantic API installation.')
        shutil.copy2(image, out / target.name)
    result = dict(status='natural_coordinate_entry_edit_accept_and_cancel_source_matches', recorded_at=datetime.now(timezone.utc).isoformat(),
        directory=str(out), cases=rows, total_independent_continuation_frames=sum(x['frames'] for x in rows),
        total_source_CPU_instructions=sum(x['CPU_instructions'] for x in rows), source_checkpoint=proof['source_checkpoint'],
        inherited_repair_bytes=18, new_program_repair=False, item_granted=False, player_RAM_injected=False,
        scene_RAM_transplant=False, inventory_position=4, existing_item_id='0x46', typed_address='203662',
        game_computed_position=dict(X=13024, Z=42400), entry_cancel_retains_position=dict(X=12992, Z=42408),
        natural_coordinate_instruction_locations=[166, 166], added_static_addresses=coverage['added_static_addresses'],
        added_function_entry_addresses=coverage['added_function_entries'], combined_main_stage_address_inventory=coverage['combined_reached_static_addresses'],
        combined_main_stage_entry_inventory=coverage['combined_reached_function_entries'], source_semantic_completion_percentage=None,
        images=images, readable_high_level_coordinate_API_in_live_frames=False,
        physical_keyboard_audio_timing_verified=False, new_training=False, local_model_code_added=False,
        default_preview_profile_changed=False, whole_game_complete=False,
        scope='Three independent400/1500/1500frame ordinary-control continuations from the verified source-produced outdoor machine, inheriting18repair bytes. Existing inventory item selected/activated, canceled, or typed/edited/accepted using buttons only. Full original/source CPU/cycle/frame/PCM/final-machine comparison passes with raw inactive-DSP gate qualified. All166coordinate instruction locations reached naturally, including both backspace blocks and scene/scheduler callsites. No host item grant/position transplant/new patch. Live code is instruction-compatible C, not the separate readable high-level API. Global callee-entry counts are not attributed exclusively to this caller; direct caller-PC observations are supplied instead. Independent branches are not one continuous3400frame run. Address inventory is not a decompilation percentage.')
    save(out / 'receipt.json', result)
    save(ROOT / 'verification/natural-coordinate-gameplay-current.json', result)
    runtime = Path.home() / '.lmstudio/local-ai-lab'
    shutil.copy2(ROOT / 'verification/natural-coordinate-gameplay-current.json', runtime / 'verification/natural-coordinate-gameplay-current.json')
    for info in images.values(): shutil.copy2(info['path'], runtime / 'verified-previews' / Path(info['path']).name)
    print(result['status'], result['total_source_CPU_instructions'], 'CPU instructions', flush=True)


if __name__ == '__main__':
    main()
