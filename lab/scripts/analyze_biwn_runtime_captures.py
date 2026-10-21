"""Compare saved emulator captures against preserved stage bytes and each other."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

import extract_biwn_stage as stage
import check_biwn_68000_slices as slices


def ppm(path):
    data = path.read_bytes()
    magic, dimensions, maximum, pixels = data.split(b'\n', 3)
    if magic != b'P6' or maximum != b'255':
        raise ValueError('Unexpected PPM format')
    width, height = map(int, dimensions.split())
    if len(pixels) != width * height * 3:
        raise ValueError('Incomplete framebuffer capture')
    return width, height, pixels


def validate(folder):
    report = json.loads((folder / 'captures.json').read_text())
    if not report['inputs_unchanged']:
        raise ValueError('Input hash guard failed')
    for run in report['runs']:
        if run['status'] != 'terminal' or run['exit_code'] not in [0, 1]:
            raise ValueError('Capture did not finish normally')
        for name, digest in run['artifacts'].items():
            if stage.cdi_layout.sha(Path(run['cwd']) / name) != digest:
                raise ValueError('A recorded capture changed')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--input-run', type=Path, required=True)
    args = parser.parse_args()
    root = stage.ROOT
    session = Path(json.loads((root / 'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    baseline, input_run = args.baseline.resolve(), args.input_run.resolve()
    for folder in [baseline, input_run]:
        if not folder.is_relative_to(session / 'emulator-runtime'):
            raise ValueError('Capture outside this analysis session')
    base_report, input_report = validate(baseline), validate(input_run)
    captured = (session / 'nextstage-68000-candidate.bin').read_bytes()
    if stage.digest(captured) != stage.STAGE_SHA:
        raise ValueError('Static stage candidate changed')
    layout = json.loads((session / 'cdi-layout.json').read_text())
    expected_toc = bytes(slices.make_toc(layout))[:48]
    rows = []
    for mode in ['bios', 'hle']:
        for path in sorted((baseline / mode / 'ram').glob('*.ram'),
                           key=lambda p: int(p.stem.rsplit('f', 1)[1])):
            ram = path.read_bytes()
            if len(ram) != 0x200000:
                raise ValueError('Unexpected RAM size')
            loaded = ram[0x4000:0x100000]
            prefix = next((i for i, (a, b) in enumerate(zip(loaded, captured)) if a != b), len(captured))
            rows.append({'mode': mode, 'frame_label': int(path.stem.rsplit('f', 1)[1]),
                         'RAM': str(path), 'RAM_sha256': stage.digest(ram),
                         'loaded_stage_sha256': stage.digest(loaded),
                         'all_stage_bytes_equal': loaded == captured,
                         'equal_prefix_bytes': prefix,
                         'equal_bytes_in_nominal_stage': sum(a == b for a, b in zip(loaded, captured)),
                         'TOC_first48_hex': ram[0x2c00:0x2c30].hex(),
                         'TOC_first48_matches_static_fixture': ram[0x2c00:0x2c30] == expected_toc})
    exact = [r for r in rows if r['all_stage_bytes_equal']]
    if not exact:
        raise ValueError('No exact whole-stage runtime byte match')
    video = {}
    for mode in ['bios', 'hle']:
        log = (baseline / mode / 'visual/run.log').read_text()
        index = log.rfind('{"summary":')
        if index < 0:
            raise ValueError('No visual probe JSON')
        video[mode] = json.JSONDecoder().raw_decode(log[index:])[0]
    input_checks = []
    for frame in [300, 600, 899]:
        before = (baseline / 'hle/ram' / f'snapshot_f{frame}.ram').read_bytes()
        after = (input_run / 'hle/ram' / f'snapshot_f{frame}.ram').read_bytes()
        input_checks.append({'kind': 'RAM', 'frame_label': frame, 'equal': before == after,
                             'changed_bytes': sum(a != b for a, b in zip(before, after))})
    for frame in [299, 598, 897]:
        name = f'frame_{frame:05}.ppm'
        width, height, before = ppm(baseline / 'hle/visual' / name)
        other_width, other_height, after = ppm(input_run / 'hle/visual' / name)
        if (width, height) != (other_width, other_height):
            raise ValueError('Framebuffer geometry changed between compared runs')
        changed = sum(before[i:i + 3] != after[i:i + 3] for i in range(0, len(before), 3))
        input_checks.append({'kind': 'framebuffer', 'frame_label': frame,
                             'equal': before == after, 'changed_pixels': changed,
                             'total_pixels': width * height})
    if not all(r['equal'] for r in input_checks if r['frame_label'] in [299, 300]):
        raise ValueError('Pre-input state differs; input attribution is not established')
    if not all(not r['equal'] for r in input_checks if r['frame_label'] in [598, 600, 897, 899]):
        raise ValueError('Expected post-input change missing')
    report = {
        'time': datetime.now(timezone.utc).isoformat(),
        'status': 'assisted_emulator_mapping_and_input_response_observed',
        'baseline_capture': str(baseline), 'input_capture': str(input_run),
        'stage_SHA256': stage.STAGE_SHA, 'stage_bytes': len(captured),
        'stage_interval': '[0x4000,0x100000)', 'RAM_comparisons': rows,
        'exact_stage_matches': exact, 'visual_audio_probe': video,
        'input_events': input_report['runs'][0]['input_events'],
        'input_response_comparisons': input_checks,
        'scope': [
            'Exact BIOS-mode RAM equality validates this mapping in the assisted pinned emulator, not an unmodified BIOS or physical hardware.',
            'The BIOS path injects the boot stub, trampoline and synthesized TOC; its later framebuffer is black.',
            'HLE framebuffer inspection shows a character, street and HUD; scripted input changes RAM and the visible viewpoint after matching pre-input states.',
            'HLE audio is fully silent in the measured900frames. BIOS audio presence can be firmware audio; it does not establish game sound.',
            'The RAM probe starts frame callbacks at1; requested frame0 has no artifact. Framebuffer labels are from its separate900frame visual run.',
            'Gameplay correctness, full game coverage, sound/music, timing and physical hardware accuracy remain unverified. None of these runs execute a reconstructed C build.',
        ],
    }
    output = session / 'emulator-runtime/capture-review.json'
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'report': str(output), 'exact_stage_matches': len(exact),
                      'input_comparisons': input_checks}, indent=2))


if __name__ == '__main__':
    main()
