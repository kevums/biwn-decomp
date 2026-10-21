"""Publish current operator evidence without invoking a model or starting tests."""
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import chat_tools


def publish():
    snapshot = chat_tools.current_route_evidence()
    now = datetime.now(timezone.utc).isoformat()
    target = ROOT / 'CURRENT DECOMPILATION.txt'
    backup = ROOT / 'config-backups/operator-status'
    backup.mkdir(parents=True, exist_ok=True)
    # Preserve the old narrative once; it contains historical evidence links.
    previous = backup / 'pre-refresh-CURRENT DECOMPILATION.txt'
    if target.exists() and not previous.exists():
        shutil.copy2(target, previous)
    lines = ['BIWN — CURRENT VERIFIED STATE', 'Observed: ' + now,
             'Whole-game decompilation is incomplete. No standalone playable reconstruction.',
             'One-click status: BIWN Live Status.command. This file is a dated evidence snapshot.', '']
    for job in snapshot['jobs']:
        lines += [job['test'] + ': ' + job['status'],
                  'Actual process handle live: ' + str(job['handle_live'])]
        if job.get('comparison'):
            lines += ['Verification: ' + job['comparison'],
                      'Verified frames: ' + str(job.get('frames'))]
        progress = job.get('progress', {})
        completed = progress.get('completed_frames', progress.get('latest', {}).get('frame'))
        if completed is not None:
            lines += ['Last recorded frame: ' + str(completed) + '; verdict pending.']
        if job.get('scope'):
            lines += ['Scope: ' + job['scope']]
        if job['test'] == 'three_processor_startup':
            lines += ['Scope: Source CPU/GPU/DSP from frame 1 through 600. IRQ, firmware HLE and devices original. Startup PCM is silent.']
        if job['test'] == 'three_processor_full_route_from_frame_one':
            lines += ['Scope: All three source processors from frame 1; 23,538-frame ordinary controller route. IRQ, firmware HLE and devices original.']
        if job['test'] == 'whole_route_DSP_router':
            lines += ['Scope: Source DSP from frame 176; CPU/GPU, IRQ, firmware HLE and devices original.']
        if job['test'] == 'CPU_GPU_merchant_DSP':
            lines += ['Scope: Original first 599 frames. Source CPU/GPU on frames 600–23,538; source DSP only on frames 15,907–23,538. IRQ/HLE/devices original.']
        lines += ['']
    inventory_path=ROOT/'verification/main-CPU-multi-route-coverage-current.json'
    if not inventory_path.exists():inventory_path=ROOT/'verification/main-CPU-route-coverage-current.json'
    inventory = json.loads(inventory_path.read_text())
    lines += ['COVERAGE AND REMAINING WORK',
              f"Inspected main CPU stage: {inventory['static_functions']} identified functions; {inventory['function_entries_reached_union']} entries reached across inventoried traces.",
              'Address inventory: '+str(inventory_path),
              'Reachability is not recovered function semantics or a whole-game completion percentage.',
              'Remaining: broader scenes/branches, readable source and data structures, standalone device/runtime replacement, physical audio/timing checks, easy native LM Studio Chat validation, reliable trained models.',
              'Original-emulator agreement proves the declared route and comparison scope; it does not prove physical Jaguar accuracy.',
              'Historical narrative: ' + str(previous), '']
    target.write_text('\n'.join(lines))
    installed = Path.home() / '.lmstudio/local-ai-lab'
    if installed.is_dir():
        shutil.copy2(target, installed / target.name)
    (ROOT / 'verification/operator-status-current.json').write_text(json.dumps(
        dict(observed_at=now, model_inference_invoked=False, snapshot=snapshot,
             output=str(target)), indent=2) + '\n')
    return str(target)


if __name__ == '__main__':
    print(publish())
