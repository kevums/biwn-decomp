"""Run a named normal-pad experiment and strictly compare original and C."""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scenario', default='ITEM-USE-REPEAT')
    parser.add_argument('--rounds', type=int, default=400)
    parser.add_argument('--with-local-review', action='store_true')
    args = parser.parse_args()
    scenarios = ROOT / 'runs/controller-action-scripts'
    available = {p.stem: p for p in scenarios.glob('*.json')}
    if args.scenario not in available:
        parser.error('Choose a saved scenario: ' + ', '.join(sorted(available)))
    if not 2 <= args.rounds <= 1200:
        parser.error('rounds must be between 2 and 1200')
    try:
        import capstone  # Required by the execution harness, checked before starting workers.
        del capstone
    except ImportError:
        parser.error('Use BIWN Controller Test.command or the lab .venv/bin/python interpreter.')
    windows = json.loads(available[args.scenario].read_text())['windows']
    if windows and args.rounds <= max(w['stop_poll'] for w in windows):
        parser.error('Choose enough rounds to include all saved controller input windows.')
    folder = ROOT / 'runs/controller-test' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    folder.mkdir(parents=True)
    core = json.loads((ROOT / 'verification/BIWN-video-layout-current.json').read_text())['core_path']
    library = json.loads((ROOT / 'verification/controller-runtime-library-current.json').read_text())['library']
    direction_pointer = ROOT / 'verification/controller-direction-library-current.json'
    if direction_pointer.exists():
        direction = json.loads(direction_pointer.read_text())
        if args.scenario in direction['verified_scenarios']:
            library = direction['library']
    base = [sys.executable, str(ROOT / 'scripts/check_biwn_entry_natural_task_rounds.py'),
            '--fresh-hle', '--hle-assets', '--hle-asset-clock', '--loader-cycle-clock',
            '--prefix-instruction-probe', '--prefix-instruction-clock',
            '--startup-clock-probe', '--startup-instruction-probe', '--startup-state-probe',
            '--startup-cost-probe', '--startup-elapsed-clock', '--startup-single-step',
            '--startup-boundary-events', '--world-instruction-probe', '--world-boundary-events',
            '--framebuffer-probe', '--frontend-video-layout', '--world-stable-clock',
            '--cpu-library', library, '--rounds', str(args.rounds), '--music-words',
            '--jerry-events', '--no-publish', '--event-core', core,
            '--input-plan', 'none', '--controller-script', str(available[args.scenario]),
            '--world-step-budget', '20000000']
    jobs, records = [], []
    print('Scenario: ' + args.scenario + '. Inputs use the emulated controller only.', flush=True)
    print('These two workers execute game code; they are not LLM agents.', flush=True)
    print('Logs and exact commands: ' + str(folder), flush=True)
    try:
        for mode in ['native', 'C']:
            command = base + ['--execution-mode', mode]
            if mode == 'C':
                command += ['--OP-GPU-owner', '--world-single-step']
            path = folder / ('world-boundary-' + mode + '-' + args.scenario + '.log')
            log = path.open('w')
            process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
            jobs.append((process, log))
            records.append(dict(mode=mode, plan=args.scenario, command=command,
                                pid=process.pid, log=str(path)))
        save(folder / 'commands.json', records)
        for row, (process, log) in zip(records, jobs):
            row['exit_code'] = process.wait()
            log.close()
            save(folder / 'commands.json', records)
            print(row['mode'] + ' finished with exit ' + str(row['exit_code']), flush=True)
        if any(row['exit_code'] for row in records):
            raise RuntimeError('Execution failed. See the saved logs; no passing result published.')
        check = subprocess.run([sys.executable, str(ROOT / 'scripts/record_biwn_world_boundary_runtime.py'),
                                '--run-root', str(folder), '--no-publish'], capture_output=True, text=True)
        (folder / 'comparison.log').write_text(check.stdout + check.stderr)
        if check.returncode:
            raise RuntimeError('Original/C comparison failed. See comparison.log.')
        report = Path(check.stdout.strip()) / 'report.json'
        proof = json.loads(report.read_text())
        save(ROOT / 'verification/controller-test-current.json', dict(**proof, report=str(report)))
        seen = set()
        for root in [ROOT, Path.home() / '.lmstudio/local-ai-lab']:
            session = json.loads((root / 'projects/black-ice-white-noise/analysis/current-session.json').read_text())
            path = Path(session['directory']) / 'emulator-runtime/summary.json'
            if path in seen:
                continue
            seen.add(path)
            summary = json.loads(path.read_text())
            controller = summary.setdefault('controller_action_runtime_comparison', {})
            controller['latest_named_test'] = dict(scenario=args.scenario, report=str(report),
                                                   **proof['runs'][args.scenario])
            save(path, summary)
        print('PASS: recorded CPU states, RAM, events, GPU states and pixels match.', flush=True)
        print('Verification report: ' + str(report), flush=True)
        print('Audio silent: ' + str(proof['runs'][args.scenario]['all_recorded_PCM_pairs_silent']), flush=True)
        if args.with_local_review:
            question = ('Fetch boot_loader once. Explain verified_controller_action_paths in under100words. '
                        'Distinguish saved controller evidence from the latest strongest world run. '
                        'State audio and standalone limits and who authored the C. Do not claim to run tests.')
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/test_firmware_CD_routing.py'),
                                     '--thinking-off', '--question', question], capture_output=True, text=True)
            (folder / 'local-model.log').write_text(result.stdout + result.stderr)
            if result.returncode:
                print('Game comparison passed; local summary failed. See local-model.log.', flush=True)
            else:
                pointer = json.loads((ROOT / 'verification/easy-firmware-CD-routing-pointer.json').read_text())
                protocol = Path(pointer['directory']) / 'protocol.json'
                answer = json.loads(protocol.read_text())['results'][0]['answer']
                print('Local Assistant (SDK; saved for source review):\n' + answer, flush=True)
                print('Exact prompts/responses: ' + str(protocol), flush=True)
        print('This is a bounded reconstruction test. Whole-game decompilation remains incomplete.', flush=True)
    finally:
        for process, log in jobs:
            if process.poll() is None:
                process.terminate()
                process.wait()
            if not log.closed:
                log.close()


if __name__ == '__main__':
    main()
