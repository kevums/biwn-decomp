"""Summarize existing per-frame CPU/GPU/DSP samples without claiming code identity."""
from collections import Counter
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import extract_biwn_stage as stage


def main():
    root = stage.ROOT
    session = Path(json.loads((root / 'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    observer = json.loads((session / 'emulator-runtime/pc-observer-summary.json').read_text())
    runs = []
    for run in observer['runs']:
        path = Path(run['cwd']) / 'frame_pcs.csv'
        digest = stage.cdi_layout.sha(path)
        assert digest == run['artifact_sha256'][path.name]
        rows = list(csv.DictReader(path.open()))
        assert len(rows) == 900
        low = [row for row in rows if int(row['gpu_pc'], 16) < 0x4000]
        waits = [row for row in rows if int(row['cpu_pc'], 16) in [0x180178, 0x18017e, 0x180182]]
        runs.append({'name': run['name'], 'source': str(path), 'source_sha256': digest, 'frames': len(rows),
                     'GPU_PC_below_0x4000_samples': len(low), 'first_GPU_PC_below_0x4000': low[0] if low else None,
                     'GPU_PC_odd_samples': sum(int(row['gpu_pc'], 16) & 1 for row in rows),
                     'CPU_boot_GPU_wait_samples': len(waits), 'first_CPU_boot_GPU_wait': waits[0] if waits else None,
                     'GPU_PC_most_frequent': [{'pc': hex(int(pc, 16)), 'frames': count} for pc, count in Counter(row['gpu_pc'] for row in rows).most_common(8)],
                     'DSP_PC_most_frequent': [{'pc': hex(int(pc, 16)), 'frames': count} for pc, count in Counter(row['dsp_pc'] for row in rows).most_common(8)],
                     'distinct_GPU_PC_samples': len({row['gpu_pc'] for row in rows}),
                     'distinct_DSP_PC_samples': len({row['dsp_pc'] for row in rows}), 'final_sample': rows[-1]})
    report = {'time': datetime.now(timezone.utc).isoformat(), 'status': 'existing_processor_PC_samples_analyzed', 'runs': runs,
              'observations': ['Assisted BIOS run has406GPU-PC samples below0x4000, first at frame431; CPU boot-wait samples begin at620 and continue through900.',
                               'HLE and HLE-input have no GPU-PC samples below0x4000 and no CPU samples in that boot-wait loop.',
                               'GPU and DSP PC values vary in HLE runs; silent audio does not establish that the DSP PC never changed.'],
              'next_probe': 'Capture GPU control state, localGPU/DSP RAM bytes and relevant mailbox/DAC state around these transitions without altering core behavior.',
              'limits': ['One post-frame sample per processor; no complete instruction trace, original function boundary or instruction-time bytes.',
                         'GPU PC outside local GPU RAM is an observation, not by itself proof of invalid execution or an emulator bug.',
                         'Odd PC samples are retained without assuming hardware alignment behavior.',
                         'No GPU/DSP RAM snapshots in this observer; PC membership cannot identify which candidate program was resident.',
                         'BIOS path is assisted and retains its boot-wait failure; no physical hardware accuracy or audio recovery established.']}
    (session / 'emulator-runtime/processor-PC-review.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'bios_low_GPU_PC_samples': runs[0]['GPU_PC_below_0x4000_samples'],
                      'bios_CPU_wait_samples': runs[0]['CPU_boot_GPU_wait_samples']}))


if __name__ == '__main__': main()
