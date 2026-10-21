"""Publish fresh CD boot failures without promoting them to decompile proofs."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALLED = Path.home()/'.lmstudio/local-ai-lab'


def save(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')


def main():
    out = ROOT/'verification/fresh-CD-boot-progress'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    configurations = [
        ('retail_default', '20261015T212339.775011Z', 'fresh-CD-retail-boot.log'),
        ('dev_default', '20261015T212345.249500Z', 'fresh-CD-dev-boot.log'),
        ('retail_hooks_off', '20261015T212444.738276Z', 'fresh-CD-retail-no-hooks.log'),
        ('retail_all_assists_off', '20261015T212445.885647Z', 'fresh-CD-retail-no-assists.log'),
    ]
    rows = {}; manifest = {}
    for label, stamp, logname in configurations:
        folder = ROOT/'verification/BIWN-fresh-CD-boot'/stamp
        path = folder/'report.json'; report = json.loads(path.read_text())
        status = json.loads((folder/'status.json').read_text())
        assert status['shutdown_completed'] and status['status'] == 'terminal_pass_probe_only'
        assert len(report['frames']) == 600
        assert report['options_read']['virtualjaguar_cd_boot_mode'] == 'bios'
        log = ROOT/'runs'/logname; text = log.read_text()
        stage_reached = any(row['stage_sha256'] == '52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453' for row in report['frames'])
        rows[label] = dict(report=str(path), frames=600, final_CPU=report['frames'][-1]['CPU'],
                           final_GPU=report['frames'][-1]['GPU'],
                           included_BIOS=report['requested_options']['virtualjaguar_cd_bios_type'],
                           source_stage_reference_reached_at_any_frame=stage_reached,
                           boot_stub_injection_logged='[CD-BOOTSTUB] Injected' in text,
                           captured_state_input=False, source_C_execution=False,
                           ordinary_boot_proven=False, process_exit=0,
                           nonzero_audio_samples=report['audio']['nonzero_samples'])
        if label.startswith('retail_') and label != 'retail_default':
            assert not rows[label]['boot_stub_injection_logged']
        assert not stage_reached
        for f in [path, folder/'status.json', log]:
            manifest[str(f)] = hashlib.sha256(f.read_bytes()).hexdigest()
    findings = [
        'Ordinary libretro content loading mounts the preserved CDI and runs all original processors/video/CD from reset without a saved state or host CPU/GPU seed.',
        'Default Real BIOS mode is assisted: source strategy clears ROM cart-auth bit, writes GPU auth magic, and injects boot stub/trampoline/TOC. Retail log confirms stub injection; this is not unassisted authentication/loading.',
        'Retail defaults end in BIOS read polling with GPU outside local program memory. Developer defaults end with CPU outside mapped executable memory; that staged variant logs run address FFFFFFFF. Neither reaches the exact stage reference in 600 frames.',
        'Disabling instruction hooks while retaining the default cart-auth bit bypass leaves retail at CPU50B6/GPUF03596. It does not inject the stub or reach the stage.',
        'Additionally restoring the exact original retail BIOS byte40B removes the cart-auth bypass. That run follows a different firmware path, ends at CPU802022/GPUF0318A, and does not reach the stage. It does not establish a permanent wedge or successful authentication.',
        'Nonzero audio in default/hook-only probes is not proof of game music. Full-assists-off probe is silent.',
    ]
    report = dict(status='fresh_CD_boot_matrix_incomplete_boot_failures_preserved', directory=str(out),
                  configurations=rows, findings=findings, normal_boot_verified=False,
                  source_C_boot_verified=False, whole_game_complete=False, new_training=False,
                  next_action='Trace the unassisted retail firmware authentication/control flow and identify the first failing source/device interaction; keep captured361E C runtime as a separate regression, not a boot claim.')
    save(out/'report.json', report); save(ROOT/'verification/fresh-CD-boot-current.json', report)
    compact = dict(report=str(out/'report.json'), configurations=rows, findings=findings,
                   source_C_execution=False, normal_boot_verified=False, new_training=False,
                   limitation='600 frame discovery probes only; no physical hardware, C boot or playability proof.')
    for base in [ROOT, INSTALLED]:
        current = json.loads((base/'projects/black-ice-white-noise/analysis/current-session.json').read_text())
        path = Path(current['directory'])/'emulator-runtime/summary.json'
        data = json.loads(path.read_text()); data['fresh_libretro_CD_boot_probe'] = compact; save(path, data)
    for filename in ['probe_biwn_fresh_CD_boot.py', 'record_biwn_fresh_boot_probe.py']:
        path = ROOT/'scripts'/filename; manifest[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
    save(out/'input-manifest.json', manifest)
    (out/'who-prompts-and-responses.txt').write_text(
        'COORDINATOR TASK\nInspect ordinary content loading and test fresh boot with the preserved CDI. Separate core assists from source firmware; preserve failures, exact options and logs. Do not claim native Chat, C boot, game music or full playability.\n\n'
        + '\n'.join(findings) + '\n\nREPORT\n' + str(out/'report.json') + '\n')
    print(out, flush=True)


if __name__ == '__main__':
    main()
