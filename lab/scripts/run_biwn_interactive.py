"""Open the experimental C CPU/GPU preview from the verified mail checkpoint."""
import hashlib
import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--in-app',action='store_true',help='Preserve the application PID when starting the native window')
    parser.add_argument('--recipe',type=Path,help='Explicit separately verified experimental preview recipe')
    parser.add_argument('--check-only',action='store_true',help='Validate the recipe and prepare its command without opening a window')
    args=parser.parse_args()
    recipe_path=args.recipe.resolve()if args.recipe else ROOT/'verification/interactive-preview-recipe.json'
    if not recipe_path.exists():recipe_path=ROOT/'verification/C-space-mail-demo-recipe.json'
    recipe = json.loads(recipe_path.read_text())
    assert recipe['status'] == 'verified_experimental_recipe'
    for name, expected in recipe['hashes'].items():
        assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == expected, name
    proof = json.loads(Path(recipe['verification']).read_text())
    failed=[key for key,value in proof['checks'].items()if not value]
    if recipe.get('DSP_inactive_qualified'):
        assert failed==['DSP_owned_positive']and proof['DSP_counts']==dict(Owned=0,Original=0,Rejected=0)
    else:assert proof['status'] == 'CPU_GPU_frame_comparison_pass' and not failed
    out = ROOT/'runs'/('interactive-BIWN-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
    out.mkdir()
    command = list(recipe['candidate'])
    index = command.index('--frame-controller-script')
    del command[index:index+2]
    command[command.index('--frames')+1] = '24000'
    command[command.index('--output')+1] = str(out/'C')
    command += ['--live-window', '--no-instruction-trace', '--play-audio']
    state = dict(status='starting', command=command, directory=str(out),
                 input='Keyboard in the preview window; no input script',
                 scope=recipe.get('scope','Recorded merchant checkpoint and experimental repairs; source CPU/GPU, original DSP/IRQ/HLE/devices. Stops on unsupported code. Optional frontend audio output; physical audibility/full-game/standalone unverified.'))
    receipt = out/'preview.json'
    receipt.write_text(json.dumps(state, indent=2)+'\n')
    if args.check_only:
        state['status']='validated_not_launched';receipt.write_text(json.dumps(state,indent=2)+'\n');print(json.dumps(state),flush=True);return
    print('Experimental BIWN source preview. P starts/resumes; M mutes; C exits the elevator menu.\nArrows move/turn. 1 then X+C opens Deck; 2 then X+C equips Beretta; Z attacks. Close the window to finish.\nResults: '+str(out), flush=True)
    if args.in_app:
        state.update(status='worker_exec_dispatched',pid=os.getpid(),terminal_report=str(out/'C/report.json'))
        receipt.write_text(json.dumps(state,indent=2)+'\n')
        os.execv(command[0],command)
    with (out/'runtime.log').open('w') as log:
        child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
        state.update(status='running', pid=child.pid)
        receipt.write_text(json.dumps(state, indent=2)+'\n')
        code = child.wait()
    state.update(status='stopped_unreviewed' if code == 0 else 'failed', exit_code=code)
    receipt.write_text(json.dumps(state, indent=2)+'\n')
    if code:
        print((out/'runtime.log').read_text()[-6000:])
        raise SystemExit(code)


if __name__ == '__main__':main()
