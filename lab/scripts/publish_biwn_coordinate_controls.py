"""Publish the exact checked readable coordinate-controls variant and panel."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shlex
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    path = ROOT / 'verification/coordinate-controls-current.json'
    proof = json.loads(path.read_text())
    assert proof['status'] == 'coordinate_input_panel_poll_digit_controls_match' and not proof['preflight_only']
    assert proof['cases'] == 2082 and proof['previous_original_baseline_cases'] == 2069
    assert proof['coordinate_instruction_locations'] == 166 and proof['native_cases'] == 14
    assert proof['integration_error_and_budget_guards'] == 11
    assert proof['source_entry_counts']['0x18e92'] == 15 and proof['source_entry_counts']['0x1b718'] == 85
    assert len(proof['native_scope_exclusions']) == 1
    source, header, library = [Path(proof[k]) for k in ['source', 'header', 'library']]
    for p, key in [(source, 'source_sha256'), (header, 'header_sha256'), (library, 'library_sha256')]:
        assert sha(p) == proof[key]
    for p, digest in proof['sources_sha256'].items(): assert sha(p) == digest
    old = json.loads((ROOT / 'verification/game-controls-current.json').read_text())
    core = Path(old['core'])
    assert sha(core) == old['core_sha256']
    dep_command = ['clang', '-std=c99', '-MM', '-I', str(ROOT / 'projects/black-ice-white-noise/restoration'), str(source)]
    dep_command += [p for p in proof['sources_sha256'] if p.endswith('.c') and not p.endswith('/biwn_game_controls.c')]
    dependency = subprocess.run(dep_command, capture_output=True, text=True)
    assert dependency.returncode == 0, dependency.stderr
    dependencies = set()
    for row in dependency.stdout.replace('\\\n', ' ').splitlines():
        if ': ' in row:
            dependencies.update(shlex.split(row.split(':', 1)[1]))
    assert str(source) in dependencies and str(header) in dependencies
    restore = ROOT / 'projects/black-ice-white-noise/restoration'
    for p in [source, header]:
        assert not (restore / p.name).exists(), 'Review an existing publication before replacing it'
        shutil.copy2(p, restore / p.name)
    out = ROOT / 'verification/coordinate-controls-publication' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    shutil.copy2(path, out / 'proof.json')
    for p in [source, header]: shutil.copy2(p, out / p.name)
    (out / 'compile-dependencies.txt').write_text(dependency.stdout)
    source_manifest = {str(Path(p).resolve()): sha(p) for p in sorted(dependencies)}
    image = Path(proof['directory']) / 'native-coordinate_confirm_123_456-CRY16.png'
    metadata = image.with_suffix('.json')
    target = ROOT / 'verified-previews/coordinate-controls-panel.png'
    shutil.copy2(image, target); shutil.copy2(metadata, target.with_suffix('.json'))
    receipt = dict(status='published_readable_coordinate_controls_with_panel_poll_digit_linkage',
        recorded_at=datetime.now(timezone.utc).isoformat(), directory=str(out), source=str(restore / source.name),
        header=str(restore / header.name), source_sha256=sha(source), header_sha256=sha(header),
        library=str(library), library_sha256=sha(library), compiled_sources_and_headers_sha256=source_manifest,
        proof=str(out / 'proof.json'), original_previous_fixture_cases=2069, original_and_C_cases=2082,
        coordinate_entry_calls=15, digit_decoder_calls=85, coordinate_instruction_locations=166,
        native_CPU_and_real_blitter_cases=14, native_blitter_commands=proof['native_actual_blitter_commands'],
        integration_error_and_budget_guards=11, native_scope_exclusions=proof['native_scope_exclusions'],
        source_panel_text_and_raw_poll_linked=True, coordinate_result_supplied=False,
        coordinate_remaining_fixture_helpers=proof['coordinate_remaining_fixture_helpers'],
        raw_controller_and_clock_values_supplied=True, public_D0_bus_RAM_MMIO_match=True,
        native_core=str(core), native_core_sha256=sha(core), panel_image=str(target), panel_image_sha256=sha(target),
        image_scope='Controlled original/C panel fixture, not a natural game screenshot. CRY16 diagnostic crop using the pinned core palette.',
        original_controls_library_or_source_replaced=False, default_preview_changed=False, live_frame_runtime_changed=False,
        new_training=False, local_model_code_authored_this_integration=False, whole_game_complete=False,
        scope=proof['scope'])
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    (ROOT / 'verification/coordinate-controls-publication-current.json').write_text(json.dumps(receipt, indent=2) + '\n')
    runtime = Path.home() / '.lmstudio/local-ai-lab'
    shutil.copy2(target, runtime / 'verified-previews' / target.name)
    shutil.copy2(target.with_suffix('.json'), runtime / 'verified-previews' / target.with_suffix('.json').name)
    for name in ['coordinate-controls-current.json', 'coordinate-controls-publication-current.json']:
        shutil.copy2(ROOT / 'verification' / name, runtime / 'verification' / name)
    print(receipt['status'], receipt['source'], flush=True)


if __name__ == '__main__':
    main()
