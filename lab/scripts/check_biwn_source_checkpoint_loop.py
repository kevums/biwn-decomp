"""Preserve the optional preview's continuous building-entry/exit capability.

New source-checkpoint/IRQ profile needs its own uninterrupted exit comparison;
the earlier4000frame entry pass alone cannot replace the old4600frame recipe.
"""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys

from check_biwn_source_checkpoint_route import sha, save

ROOT = Path(__file__).resolve().parents[1]


def main():
    prefix = json.loads((ROOT / 'verification/source-checkpoint-north-route-current.json').read_text())
    prefix_dir = Path(prefix['directory'])
    prior = json.loads((prefix_dir / 'protocol.json').read_text())
    assert prior['status'] == 'terminal_source_checkpoint_route_match'
    old_loop = json.loads((ROOT / 'verification/fast-building570-loop-current.json').read_text())
    source_inputs = json.loads((prefix_dir / 'planning/navigation-input.json').read_text())['windows']
    old_inputs = json.loads((Path(old_loop['directory']) / 'input.json').read_text())['windows']
    exit_inputs = [dict(window, start_frame=max(4001, window['start_frame'])) for window in old_inputs if window['stop_frame'] > 4001]
    assert exit_inputs and all(window['stop_frame'] <= 4601 for window in exit_inputs)
    out = ROOT / 'runs' / ('source-checkpoint-building-loop-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
    out.mkdir(parents=True)
    inputs = out / 'input.json'
    save(inputs, dict(windows=source_inputs + exit_inputs))
    commands = {}
    for phase in ['reference', 'C']:
        cmd = next(row['command'][:] for row in prior['commands'] if row['phase'] == phase)
        cmd[cmd.index('--frames') + 1] = '4600'
        cmd[cmd.index('--frame-controller-script') + 1] = str(inputs)
        cmd[cmd.index('--output') + 1] = str(out / phase)
        cmd += ['--capture-frame', '4159', '--capture-frame', '4600']
        commands[phase] = cmd
    state = dict(status='prepared', recorded_at=datetime.now(timezone.utc).isoformat(), pid=os.getpid(),
                 directory=str(out), frames=4600, commands=commands, children={},
                 initial_source_checkpoint=prefix['source_checkpoint'], inherited_program_repair_bytes=18,
                 new_program_repair_applied=False, no_intermediate_restore=True, whole_game_complete=False)

    def checkpoint():
        save(out / 'protocol.json', state)
        save(ROOT / 'verification/source-checkpoint-building-loop-active.json', state)

    checkpoint()
    try:
        for phase, cmd in commands.items():
            with (out / (phase + '.log')).open('w') as log:
                process = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT,
                                           env={**os.environ, 'BIWN_LIVE_ATTACK_COUNTERS': str(out / phase / 'attack-owner-counts.txt')})
                state.update(status='running_' + phase, child_pid=process.pid)
                state['children'][phase] = process.pid
                checkpoint()
                print(phase, 'PID', process.pid, flush=True)
                code = process.wait()
            assert code == 0, (phase, out / (phase + '.log'))
        old_cpu_count = prefix['CPU_instructions']
        prefix_checks = {}
        for phase in commands:
            report = json.loads((out / phase / 'report.json').read_text())
            old_report = json.loads((prefix_dir / phase / 'report.json').read_text())
            prefix_checks[phase + '_first4000frames'] = report['frames'][:4000] == old_report['frames']
            for name, width in [('CPU-before-instructions.bin', 78), ('retired-instruction-costs.bin', 8)]:
                import hashlib
                with (out / phase / name).open('rb') as stream:
                    remaining, digest = old_cpu_count * width, hashlib.sha256()
                    while remaining:
                        chunk = stream.read(min(8 * 1024 * 1024, remaining))
                        assert chunk
                        digest.update(chunk)
                        remaining -= len(chunk)
                prefix_checks[phase + '_' + name] = digest.hexdigest() == sha(prefix_dir / phase / name)
        assert all(prefix_checks.values()), prefix_checks
        probe = json.loads((ROOT / 'verification/source-checkpoint-probe-candidate.json').read_text())
        comparison = out / 'comparison.json'
        command = [sys.executable, probe['comparator'], '--C-run', str(out / 'C'), '--reference', str(out / 'reference'),
                   '--expected-frames', '4600', '--source-checkpoint-report', prefix['source_checkpoint']['report'],
                   '--source-checkpoint-proof', prefix['source_checkpoint']['source_proof'], '--output', str(comparison)]
        with (out / 'comparison.log').open('w') as log:
            code = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT).returncode
        compared = json.loads(comparison.read_text())
        failed = [key for key, value in compared['checks'].items() if not value]
        assert (code == 0 and not failed) or (code == 1 and failed == ['DSP_owned_positive'] and
                                              compared['DSP_counts'] == dict(Owned=0, Original=0, Rejected=0)), failed
        RAM = (out / 'C/final-RAM.bin').read_bytes()
        get = lambda address, width=2: int.from_bytes(RAM[address:address + width], 'big')
        final = dict(mode=get(0x49c60), floor=get(0x49c62), retained_scene=get(0x49c64), X=get(0x49c50, 4), Z=get(0x49c56, 4))
        assert final['mode'] == 1 and final['floor'] == 0 and final['retained_scene'] == 570, final
        report = json.loads((out / 'C/report.json').read_text())
        irq = json.loads(Path(report['CPU_IRQ_report']).read_text())
        proof = dict(status='source_checkpoint_continuous_building570_entry_exit_match', recorded_at=datetime.now(timezone.utc).isoformat(),
                     directory=str(out), comparison=str(comparison), commands=commands, frames=4600,
                     CPU_instructions=compared['owned_CPU_instructions'], GPU_counts=compared['GPU_counts'],
                     DSP_counts=compared['DSP_counts'], raw_failed_checks=failed,
                     source_IRQ_selection=irq['selection'], source_IRQ_entry=irq['core'],
                     source_checkpoint=report['restored_source_checkpoint'], original_checkpoint_restored=False,
                     inherited_program_repair_bytes=18, new_program_repair_applied=False,
                     no_intermediate_restore=True, prefix_checks=prefix_checks, final_state=final,
                     native_window_verified=False, physical_audio_verified=False, default_preview_promoted=False,
                     whole_game_complete=False,
                     scope='Continuous4600frame ordinary-button outdoor/scene570/outdoor route on the unified source CPU/GPU/IRQ profile. Initial machine is restored from the checked source-owned24738frame run on the exact same core and carries its18byte repair; no original checkpoint, mid-route restore or new game-byte patch. First4000frames reproduce the prior new source-checkpoint entry proof; remaining600frames demonstrate exit. All native CPU/cost/frame/final-machine comparisons pass except inactive DSP-positive gate if listed. Other HLE/OP/device/IRQ ACK/queue services remain; no new cold start, audible-output, native keyboard or standalone/whole-game proof.')
        save(out / 'verdict.json', proof)
        save(ROOT / 'verification/source-checkpoint-building-loop-current.json', proof)
        state.update(status='terminal_source_checkpoint_building_loop_match', comparison=str(comparison), final_state=final)
        checkpoint()
        print(proof['status'], flush=True)
    except BaseException as error:
        state.update(status='terminal_failed', error=repr(error))
        checkpoint()
        raise


if __name__ == '__main__':
    main()
