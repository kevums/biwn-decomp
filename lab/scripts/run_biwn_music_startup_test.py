"""Easy fresh startup DSP comparison with optional visible role transcripts."""
import argparse
import fcntl
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--with-local-review', action='store_true')
    args = parser.parse_args()
    out = ROOT/'runs/music-startup-launcher'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    core = json.loads((ROOT/'verification/DSP-music-context-experimental-candidate.json').read_text())['core_path']
    common = [sys.executable, str(ROOT/'scripts/probe_biwn_fresh_CD_boot.py'), '--boot', 'hle',
              '--frames', '179', '--core', core, '--capture-audio', '--no-publish']
    commands = []
    print('Fresh startup: original CPU/GPU/hardware; reconstructed DSP only in frames176–179.', flush=True)
    print('Commands, prompts and results: '+str(out), flush=True)
    for kind in ['reference', 'C']:
        command = common+['--output', str(out/kind)]
        if kind == 'C':
            command += ['--own-DSP-window', '176', '180', '--DSP-owner-kind', 'router']
        commands.append(command)
        (out/'commands.json').write_text(json.dumps(commands, indent=2)+'\n')
        print('Running '+kind, flush=True)
        with (out/(kind+'.log')).open('w') as log:
            result = subprocess.run(command, cwd=ROOT.parents[1], stdout=log, stderr=subprocess.STDOUT)
        if result.returncode:
            raise SystemExit('Run rejected; inspect '+str(out/(kind+'.log')))
    command = [sys.executable, str(ROOT/'scripts/compare_biwn_fresh_DSP.py'), '--C-run', str(out/'C'),
               '--reference', str(out/'reference'), '--expected-frames', '179', '--output', str(out/'report.json')]
    commands.append(command)
    (out/'commands.json').write_text(json.dumps(commands, indent=2)+'\n')
    result = subprocess.run(command)
    if result.returncode:
        raise SystemExit('Original/C comparison failed; inspect '+str(out/'report.json'))
    proof = json.loads((out/'report.json').read_text())
    print('Passed startupDSP comparison; owned instructions:'+str(proof['DSP_report']['owned']), flush=True)
    if args.with_local_review:
        sys.path.insert(0, str(ROOT))
        import lab
        evidence = dict(status=proof['status'], total_frames=179,
                        DSP_owned_frames=dict(start_inclusive=176, stop_exclusive=180,
                                              all_frames=[176,177,178,179]),
                        DSP_owned_instructions=proof['DSP_report']['owned'],
                        DSP_original_instructions=proof['DSP_report']['core_counts']['Original'],
                        matching=['recorded frame fields', 'final RAM/GPU/full machine state', 'PCM bytes'],
                        audio='Silent startup PCM; audible game music quality remains unverified.',
                        original_providers='CPU,GPU,hardware,IRQ,firmware HLE', whole_game_complete=False,
                        new_training=False, test_execution='The launcher executed both runs and compared them. Local model roles read the saved report.')
        results = []
        with (ROOT/'runs/.inference.lock').open('w') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            for role in ['Explainer', 'Scope reviewer']:
                task = ('Act as '+role+'. In under80words explain the supplied comparison for the owner. '
                        'Clearly state only frames176–179 use reconstructed DSP; CPU/GPU/hardware remain original. '
                        'Silent PCM equivalence does not verify audible music quality. This is a fresh short startup, '
                        'not a full-game decomp. The launcher ran the tests; you read its report. '
                        'Do not say no tests were run, and do not claim you personally ran them or trained weights.')
                payload = dict(task=task, evidence=evidence)
                if results:
                    payload['prior_role_response'] = results[-1]['response']['text']
                    payload['task'] += ' Correct only actual overstatements. If the response is accurate, confirm it; do not invent an error.'
                response = lab.generate('game', lab.COMMON, json.dumps(payload), 400)
                row = dict(role=role, response=response)
                results.append(row)
                print(role+' ('+str(round(response['seconds'], 2))+'s): '+response['text'], flush=True)
                (out/'local-roles.json').write_text(json.dumps(results, indent=2)+'\n')
                with (out/'prompts-and-responses.txt').open('a') as transcript:
                    transcript.write('ROLE: '+role+'\nREQUEST:\n'+json.dumps(response['request'], indent=2)+
                                     '\nRESPONSE:\n'+response['text']+'\n\n')
        (out/'role-scope.json').write_text(json.dumps(dict(same_base_weights=True, independent_validation=False,
                                                         new_training=False), indent=2)+'\n')
    print('Report: '+str(out/'report.json'), flush=True)


if __name__ == '__main__':
    main()
