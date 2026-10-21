"""Build an isolated LTO GPU-IRQ bridge and compare its existing preview output.

No game algorithm, scheduling quantum, ownership guard or active recipe is
changed. A local symbol rename lets the linker optimize the existing OP
slice and its bridge together, keeping all other kernels as dependencies.
"""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def save(p, value):
    p.write_text(json.dumps(value, indent=2) + '\n')


def main():
    runtime = json.loads((ROOT / 'verification/unified-restore-runtime-candidate.json').read_text())
    base_path = Path(runtime['GPU_candidate'])
    base = json.loads(base_path.read_text())
    bridge = Path(base['directory']) / 'register_GPU_bridge.c'
    assert sha(bridge) == base['source_sha256']
    kernel = ROOT / 'verification/shared-GPU-RAM-build/20261017T014443.328498Z/kernel-source/biwn_gpu_OP_slice.c'
    headers = kernel.parent
    baseline_proof = json.loads((ROOT / 'verification/primary-preview-throughput-current.json').read_text())
    baseline = Path(baseline_proof['directory'])
    command = next(row['command'][:] for row in json.loads((baseline / 'protocol.json').read_text())['commands'] if row['phase'] == 'C')
    out = ROOT / 'verification/GPU-OP-LTO' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    print(out, flush=True)
    shutil.copy2(bridge, out / 'register_GPU_bridge.c')
    shutil.copy2(kernel, out / 'biwn_gpu_OP_slice.c')
    shutil.copy2(headers / 'biwn_gpu_OP_slice.h', out / 'biwn_gpu_OP_slice.h')
    library = out / 'libGPU-OP-LTO-bridge.dylib'
    compile_command = ['clang', '-dynamiclib', '-std=c99', '-O3', '-flto', '-Wall', '-Wextra', '-Werror',
        '-Wno-deprecated-declarations', '-Dbiwn_gpu_OP_slice_run=biwn_gpu_OP_slice_run_local',
        str(out / 'register_GPU_bridge.c'), str(out / 'biwn_gpu_OP_slice.c'), base['kernel_library'], runtime['core'],
        '-Wl,-unexported_symbol,_biwn_gpu_OP_slice_run_local', '-o', str(library)]
    state = dict(status='compiling', pid=os.getpid(), directory=str(out), compile_command=compile_command,
                 baseline=str(baseline), algorithm_changed=False, default_recipe_changed=False, whole_game_complete=False,
                 source_files={str(p): sha(p) for p in [bridge, kernel, headers / 'biwn_gpu_OP_slice.h', Path(base['kernel_library']), Path(runtime['core'])]})
    def mark():
        save(out / 'protocol.json', state); save(ROOT / 'verification/GPU-OP-LTO-active.json', state)
    mark()
    try:
        result = subprocess.run(compile_command, capture_output=True, text=True, env={**os.environ, 'DEVELOPER_DIR': '/Library/Developer/CommandLineTools'})
        (out / 'compiler.log').write_text(result.stdout + result.stderr)
        assert result.returncode == 0, result.stderr
        candidate = dict(base, status='isolated_LTO_OP_bridge_pending_output_check', directory=str(out), library=str(library),
                         source_sha256=sha(out / 'register_GPU_bridge.c'), prior_candidate=str(base_path),
                         compiler_optimization_only=True, compiler_command=compile_command)
        save(out / 'candidate.json', candidate)
        command[0] = sys.executable
        command[command.index('--native-GPU-candidate') + 1] = str(out / 'candidate.json')
        command[command.index('--output') + 1] = str(out / 'C')
        state.update(status='running_isolated_600_frames', command=command, library_sha256=sha(library)); mark()
        with (out / 'runtime.log').open('w') as log:
            start = time.monotonic()
            child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
            state['child_pid'] = child.pid; mark()
            code = child.wait()
            state.update(child_exit_code=code, wall_seconds=time.monotonic() - start)
        assert code == 0, out / 'runtime.log'
        old = json.loads((baseline / 'C/report.json').read_text())
        new = json.loads((out / 'C/report.json').read_text())
        checks = dict(all_600_frame_records=old['frames'] == new['frames'], no_errors=not new['errors'],
                      CPU_count=old['owned_CPU_instructions'] == new['owned_CPU_instructions'],
                      no_original_CPU=new['original_CPU_instructions'] == new['rejected_CPU_instructions'] == 0,
                      no_instruction_trace=new['instruction_trace_recorded'] is False)
        for name in ['warm-RAM.bin', 'final-RAM.bin', 'final-video.bin', 'final-serialized-state.bin', 'frontend-PCM.s16le']:
            checks[name] = sha(baseline / 'C' / name) == sha(out / 'C' / name)
        before = json.loads(Path(old['regular_GPU_report']).read_text())
        after = json.loads(Path(new['regular_GPU_report']).read_text())
        checks['GPU_ownership_and_source_counts'] = before['counts'] == after['counts'] and before['C_source_instructions'] == after['C_source_instructions']
        checks['no_GPU_errors'] = not after['errors']
        state['checks'] = checks
        assert all(checks.values()), checks
        state.update(status='terminal_LTO_600_frame_output_match', frames=600,
                     baseline_wall_seconds=next(x['wall_seconds'] for x in baseline_proof['phases'] if x['phase'] == 'C'),
                     speed_comparison_qualified='Single runs, concurrent local inference and different thermal/system state; no stable speedup or native-window FPS claim.',
                     native_window_verified=False, instruction_trace_compared=False)
        mark(); save(out / 'report.json', state); save(ROOT / 'verification/GPU-OP-LTO-current.json', state)
        print(state['status'], 'seconds', state['wall_seconds'], flush=True)
    except BaseException as error:
        state.update(status='terminal_failed', error=repr(error)); mark(); raise


if __name__ == '__main__':
    main()
