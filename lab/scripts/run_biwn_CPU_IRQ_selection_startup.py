"""Three-lane fresh startup: parent, NULL handoffs, then source processors/IRQs."""
from datetime import datetime, timezone
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reuse-references', type=Path)
    args = parser.parse_args()
    core = json.loads((ROOT / 'verification/CPU-IRQ-selection-core-experimental-candidate.json').read_text())
    unit = json.loads((ROOT / 'verification/CPU-IRQ-selection-current.json').read_text())
    assert core['core-tests_exit'] == 0 and unit['core_sha256'] == core['core_sha256']
    assert unit['status'] == 'native_original_and_source_interrupt_selection_match'
    parent = Path(core['parent_core']).parent
    child = Path(core['core_path']).parent
    unchanged = ['src/tom/gpu.c', 'src/tom/gpu.h', 'src/jerry/dsp.c', 'src/jerry/dsp.h',
                 'src/core/state.h', 'src/m68000/cpudefs.h', 'src/m68000/sysdeps.h']
    for name in unchanged:
        assert (parent / name).read_bytes() == (child / name).read_bytes(), name
    rebound = {}
    for kind, original_name in [('GPU', 'GPU-register-bridge-experimental-candidate.json'),
                                ('native-CPU', 'GPU-register-native-CPU-experimental-candidate.json'),
                                ('DSP', 'GPU-register-DSP-router-experimental-candidate.json')]:
        original_path = ROOT / 'verification' / original_name
        data = json.loads(original_path.read_text())
        assert data['required_core_sha256'] == core['parent_core_sha256']
        data.update(status='isolated_IRQ_core_rebind_pending_startup_comparison',
                    required_core_sha256=core['core_sha256'], required_core_path=core['core_path'], previous_required_core_sha256=core['parent_core_sha256'],
                    core_rebind_scope='Identical GPU/DSP source+headers, private CPU headers and serialization; same immutable source bridge library. New default-off CPU interrupt handoffs only; runtime comparison pending.')
        if kind == 'GPU':
            # The register bridge deliberately checks its exact core path in C.
            # Recompile only that binding; retain every identity/kernel/ABI guard.
            old_source = Path(data['directory']) / 'register_GPU_bridge.c'
            text = old_source.read_text()
            assert sha(old_source) == data['source_sha256']
            old_literal = json.dumps(core['parent_core'])
            assert text.count(old_literal) == 1
            text = text.replace(old_literal, json.dumps(core['core_path']))
            build = ROOT / 'verification/CPU-IRQ-selection-GPU-bridge-build' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
            build.mkdir(parents=True)
            new_source = build / 'register_GPU_bridge.c'
            new_source.write_text(text)
            library = build / 'libregister-GPU-bridge.dylib'
            command = ['clang', '-dynamiclib', '-std=c99', '-O2', '-Wall', '-Wextra', '-Werror',
                       str(new_source), data['kernel_library'], '-o', str(library)]
            with (build / 'compiler.log').open('w') as stream:
                subprocess.run(command, env=dict(os.environ, DEVELOPER_DIR='/Library/Developer/CommandLineTools'),
                               stdout=stream, stderr=subprocess.STDOUT, check=True)
            data.update(directory=str(build), library=str(library), source_sha256=sha(new_source),
                        source_change='Only the strict expected core path literal changed; same24 source kernel library and all runtime guards.',
                        previous_source_sha256=sha(old_source), library_sha256=sha(library),
                        core_rebind_scope='Identical GPU source/headers/serialization and source kernels. Recompiled register bridge with the exact new core path; no relaxed path check. IRQ runtime comparison pending.')
        dest = ROOT / 'verification' / ('CPU-IRQ-selection-' + kind + '-experimental-candidate.json')
        dest.write_text(json.dumps(data, indent=2) + '\n')
        rebound[kind] = str(dest)
    source_probe = ROOT / 'scripts/probe_biwn_frame_CPU_owner.py'
    probe = source_probe.read_text()
    assert probe.count('import biwn_CPU_IRQ_owner') == 1 and probe.count('biwn_CPU_IRQ_owner.install(core,out)') == 1
    probe = probe.replace('import biwn_CPU_IRQ_owner', 'import biwn_CPU_IRQ_select_owner').replace(
        'biwn_CPU_IRQ_owner.install(core,out)', 'biwn_CPU_IRQ_select_owner.install(core,out)')
    needle = "if CPU_IRQ_owner and core.BIWNCPUIRQRejectedCount():"
    assert probe.count(needle) == 1
    probe = probe.replace(needle, 'if CPU_IRQ_owner and (core.BIWNCPUIRQRejectedCount() or core.BIWNCPUInterruptRejectedCount()):')
    probe = probe.replace("errors.append('Source CPU IRQ entry rejected; no original entry fallback')",
                          "errors.append('Source interrupt selection/entry rejected; no original IRQ fallback')")
    needle = "if args.source_CPU_IRQ_entry and hasattr(core,'BIWNSetCPUIRQOwner'):core.BIWNSetCPUIRQOwner(None)"
    assert probe.count(needle) == 1
    probe = probe.replace(needle, needle + '\n        if args.source_CPU_IRQ_entry:core.BIWNSetCPUInterruptSelector(None)')
    probe = probe.replace('Portable IRQ entry after original device ACK; C mode and diagnostic core only',
                          'Source interrupt selection plus portable entry; isolated selection core only')
    target_probe = ROOT / 'scripts/probe_biwn_frame_CPU_IRQ_selection.py'
    if target_probe.exists():
        assert target_probe.read_text() == probe, 'Preserve a different previous derivative probe for audit'
    else:
        target_probe.write_text(probe)
    active = json.loads((ROOT / 'verification/fast-fresh-outdoor-route-active.json').read_text())
    out = ROOT / 'runs' / ('CPU-IRQ-selection-startup-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
    out.mkdir()
    full_input_path = Path(active['commands']['reference'][active['commands']['reference'].index('--frame-controller-script') + 1])
    full_input = json.loads(full_input_path.read_text())
    short_input = dict(full_input)
    short_input['windows'] = [dict(window, stop_frame=min(window['stop_frame'], 601))
                              for window in full_input['windows'] if window['start_frame'] <= 600]
    (out / 'input.json').write_text(json.dumps(short_input, indent=2) + '\n')
    commands = {}
    for phase in ['parent_original', 'new_original', 'new_C']:
        mode = 'C' if phase == 'new_C' else 'reference'
        command = list(active['commands'][mode])
        command[1] = str(target_probe)
        command[command.index('--frames') + 1] = '600'
        command[command.index('--output') + 1] = str(out / phase)
        command[command.index('--frame-controller-script') + 1] = str(out / 'input.json')
        while '--capture-frame' in command:
            i = command.index('--capture-frame')
            del command[i:i + 2]
        command += ['--capture-frame', '600']
        if phase != 'parent_original':
            command[command.index('--core') + 1] = core['core_path']
            command[command.index('--native-CPU-candidate') + 1] = rebound['native-CPU']
            if mode == 'C':
                command[command.index('--native-GPU-candidate') + 1] = rebound['GPU']
                command[command.index('--DSP-router-candidate') + 1] = rebound['DSP']
                command += ['--source-CPU-IRQ-entry']
        commands[phase] = command
    report = dict(status='prepared', pid=os.getpid(), directory=str(out), frames=600, commands=commands, children={},
                  core_sha256=core['core_sha256'], parent_core_sha256=core['parent_core_sha256'],
                  original_probe_sha256=sha(source_probe), derivative_probe_sha256=sha(target_probe),
                  input_origin=str(full_input_path), full_input_sha256=sha(full_input_path),
                  startup_input_sha256=sha(out / 'input.json'), input_policy='Exact first600frame prefix; later input windows omitted and crossing interval clipped to601.',
                  scope='Independent600frame emulator starts; no warmup/checkpoint/scene transplant. Parent original versus new NULL handoffs establishes bounded core inertness; new original versus reconstructed CPU/GPU/DSP plus source IRQ decision/entry. Original queue/line, ACK/vector resolution, commit/prefetch/cycle charge, HLE/OP/devices remain. Not whole-game, hardware accuracy or standalone proof.')
    pointer = ROOT / 'verification/CPU-IRQ-selection-startup-active.json'

    def record():
        for path in [out / 'protocol.json', pointer]:
            path.write_text(json.dumps(report, indent=2) + '\n')

    processes = []
    try:
        reused = None
        if args.reuse_references:
            previous = args.reuse_references.resolve()
            reused = json.loads((previous / 'protocol.json').read_text())
            assert reused['frames'] == 600 and reused['core_sha256'] == core['core_sha256']
            assert reused['parent_core_sha256'] == core['parent_core_sha256']
            assert reused['derivative_probe_sha256'] == report['derivative_probe_sha256']
            assert sha(previous / 'input.json') == report['startup_input_sha256']
            report['reused_reference_protocol'] = str(previous / 'protocol.json')
            report['reused_reference_protocol_sha256'] = sha(previous / 'protocol.json')
        for phase, command in commands.items():
            if reused and phase != 'new_C':
                previous_report = json.loads((previous / phase / 'report.json').read_text())
                expected_core = core['parent_core_sha256'] if phase == 'parent_original' else core['core_sha256']
                assert reused['children'][phase]['exit_code'] == 0 and previous_report['core_sha256'] == expected_core
                assert len(previous_report['frames']) == 600 and not previous_report['errors']
                (out / phase).symlink_to(previous / phase, target_is_directory=True)
                report['children'][phase] = dict(status='reused_completed_reference', exit_code=0,
                                               source=str(previous / phase), command_executed_this_run=False)
                record()
                continue
            stream = (out / (phase + '.log')).open('w')
            process = subprocess.Popen(command, stdout=stream, stderr=subprocess.STDOUT)
            processes.append((phase, process, stream))
            report['children'][phase] = dict(pid=process.pid, status='running')
            record()
            print(phase, process.pid, flush=True)
        failed = []
        for phase, process, stream in processes:
            code = process.wait()
            stream.close()
            report['children'][phase].update(status='terminal_completed' if code == 0 else 'terminal_failed', exit_code=code)
            record()
            if code:
                failed.append((phase, code, str(out / (phase + '.log'))))
        assert not failed, failed
        files = ['warm-RAM.bin', 'CPU-before-instructions.bin', 'retired-instruction-costs.bin',
                 'final-RAM.bin', 'final-video.bin', 'final-serialized-state.bin', 'frontend-PCM.s16le']
        reports = {phase: json.loads((out / phase / 'report.json').read_text()) for phase in commands}
        baseline = reports['parent_original']
        checks = {}
        hashes = {phase: {name: sha(out / phase / name) for name in files} for phase in commands}
        for phase, observed in reports.items():
            checks[phase + '_complete'] = len(observed['frames']) == 600 and not observed['errors']
            checks[phase + '_frames_match'] = observed['frames'] == baseline['frames']
            for name in files:
                checks[phase + '_' + name] = hashes[phase][name] == hashes['parent_original'][name]
        comparison = out / 'source-comparison.json'
        with (out / 'comparison.log').open('w') as stream:
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/compare_biwn_frame_CPU_only.py'),
                                     '--C-run', str(out / 'new_C'), '--reference', str(out / 'new_original'),
                                     '--expected-frames', '600', '--experimental-code-overlay',
                                     commands['new_C'][commands['new_C'].index('--experimental-mainstage-overlay') + 1],
                                     '--output', str(comparison)], stdout=stream, stderr=subprocess.STDOUT)
        checks['combined_CPU_GPU_DSP_gate'] = result.returncode == 0
        irq = json.loads((out / 'new_C/CPU-IRQ-owner-report.json').read_text())
        checks['source_decision_positive_no_fallback'] = irq['selection']['Owned'] > 0 and irq['selection']['Original'] == irq['selection']['Rejected'] == 0
        checks['source_entry_positive_no_fallback'] = irq['core']['Owned'] > 0 and irq['core']['Original'] == irq['core']['Rejected'] == 0
        report.update(checks=checks, file_hashes=hashes, source_IRQ=irq, comparison=str(comparison))
        assert all(checks.values()), [k for k, v in checks.items() if not v]
        report.update(status='terminal_three_lane_startup_processors_and_IRQ_selection_entry_match', whole_game_complete=False,
                      original_probe_unchanged=sha(source_probe) == report['original_probe_sha256'])
        record()
        (ROOT / 'verification/CPU-IRQ-selection-startup-current.json').write_text(json.dumps(report, indent=2) + '\n')
        print(report['status'], flush=True)
    except BaseException as error:
        report.update(status='terminal_failed_partial_evidence_preserved', error=repr(error))
        record()
        raise


if __name__ == '__main__':
    main()
