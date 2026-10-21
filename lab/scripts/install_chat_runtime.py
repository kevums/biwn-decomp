"""Provision the small Chat runtime outside macOS Documents; copy scoped evidence only."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shlex
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent.parent
RUNTIME = Path.home() / '.lmstudio/local-ai-lab'


def launcher_script(name):
    if Path(name).name != name or not name.endswith('.command'):
        raise ValueError('Expected a launcher basename')
    return '''#!/bin/zsh
set -euo pipefail
lab_root="$(cd -- "$(dirname -- "$0")" && pwd)"
source_root="$("$lab_root/.venv/bin/python" - "$lab_root" <<'PYCODE'
import json,sys
from pathlib import Path
print(Path(json.loads((Path(sys.argv[1])/'config/biwn-native-reference.json').read_text())['core']).parents[2])
PYCODE
)"
"$source_root"/''' + shlex.quote(name) + ''' "$@"
'''


def install():
    RUNTIME.mkdir(parents=True, exist_ok=True)
    python_source = ROOT / 'tools/python/cpython-3.12.15-macos-aarch64-none'
    if not (RUNTIME / 'python/bin/python3.12').exists():
        shutil.copytree(python_source, RUNTIME / 'python', symlinks=True)
    uv = ROOT / 'tools/uv-aarch64-apple-darwin/uv'
    python = RUNTIME / '.venv/bin/python'
    if not python.exists():
        subprocess.run([str(uv), 'venv', '--python', str(RUNTIME / 'python/bin/python3.12'),
                        str(RUNTIME / '.venv')], check=True)
    dependencies=ROOT/'chat-runtime.lock'
    packages=['-r',str(dependencies)] if dependencies.exists() else [
        'mcp==1.26.0','capstone==5.0.9','pypdf==6.20.0','fonttools==4.66.1']
    subprocess.run([str(uv), 'pip', 'install', '--python', str(python), *packages], check=True)
    for name in ['chat_tools.py', 'binary_tools.py', 'cpu_fixture.py', 'inventory_renderer.py', 'animation_renderer.py', 'lab.py', 'config.json',
                 'native_cpu_fixture.py','native-fixture-backend.json','frame_test_jobs.py','rubric_scoring.py',
                 'biwn_doorway_planner.py','biwn_indoor_exit_planner.py']:
        shutil.copy2(ROOT / name, RUNTIME / name)
    reference=RUNTIME/'config/biwn-native-reference.json';reference.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/'config/biwn-native-reference.json',reference)
    # All interactive workflows run in the workbench, using the same inference
    # lock as training. The small MCP runtime keeps its scoped evidence only.
    for launcher in ROOT.glob('*.command'):
        text=launcher_script(launcher.name)
        target=RUNTIME/launcher.name;target.write_text(text);target.chmod(0o755)
    for name in ['START HERE.txt','CURRENT ADVERTISING.txt','CURRENT DECOMPILATION.txt','CURRENT LOCAL INFERENCE.txt']:
        if (ROOT/name).exists():shutil.copy2(ROOT/name,RUNTIME/name)
    shutil.copytree(ROOT/'presets',RUNTIME/'presets',dirs_exist_ok=True)
    for name in ['corpus', 'tools/jaguar-disasm']:
        shutil.copytree(ROOT / name, RUNTIME / name, dirs_exist_ok=True)
    if (ROOT/'verified-previews/scene-previews.json').exists():
        shutil.copytree(ROOT/'verified-previews', RUNTIME/'verified-previews', dirs_exist_ok=True)
    # Small pinned render assets: frozen RAM, user-provided BIOS for hardware
    # initialization, native restored-code bridge and existing blitter core.
    # No CD image, raw tracks, modelweights or emulator source checkout copied.
    render_files=['render-assets/biwn-inventory-baseline.bin','render-assets/jaguarcd_bios.bin',
                  'tools/blitter-runtime/virtualjaguar_libretro.dylib',
                  'tools/libbiwn-inventory-device.dylib','tools/libbiwn-inventory-interaction.dylib','tools/pinned-CRY-color-tables.json','tools/libbiwn-animation-images.dylib',
                  'render-assets/animation-preview-assets.json']
    for name in render_files:
        source=ROOT/name;target=RUNTIME/name;target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists()and not target.stat().st_mode&0o200:target.chmod(target.stat().st_mode|0o200)
        shutil.copy2(source,target)
    pointer = json.loads((ROOT / 'projects/black-ice-white-noise/analysis/current-session.json').read_text())
    source_session = Path(pointer['directory']).resolve()
    if not source_session.is_relative_to(ROOT / 'projects/black-ice-white-noise/analysis'):
        raise ValueError('Invalid session source')
    target_session = RUNTIME / 'projects/black-ice-white-noise/analysis' / source_session.name
    target_session.mkdir(parents=True, exist_ok=True)
    names = ['boot-payload-68000-candidate.bin', 'boot-mapping.json', 'image-preservation.json',
             'cdi-layout.json', 'ghidra-full-status.json', 'gpu-opening.json',
             'gpu-target-f0332c.json', 'gpu-parameter-data.json', 'ghidra-full-export/listing.asm']
    files = []
    for name in names:
        source = source_session / name
        target = target_session / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        files.append({'source': str(source), 'snapshot': str(target),
                      'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
    optional_names=['gpu-dispatch-tables.json','nextstage-mapping.json','nextstage-68000-candidate.bin',
                    'nextstage-ghidra-status.json','nextstage-stack2-status.json',
                    'nextstage-profile-comparison.json','nextstage-stack2-export/decompiled.c',
                    'boot-slice-validation.json','processor-programs.json',
                    'helper-gpu-relocations.json','ghidra-divu-review.json',
                    'divu-candidate-summary.json','nextstage-divu-export/decompiled.c',
                    'nextstage-divu-export/manifest.json','emulator-runtime/summary.json']
    for name in optional_names:
        optional=source_session/name
        if optional.exists():
            target=target_session/name;target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(optional,target)
            files.append({'source':str(optional),'snapshot':str(target),
                          'sha256':hashlib.sha256(optional.read_bytes()).hexdigest()})
    (target_session.parent / 'current-session.json').write_text(json.dumps({'directory': str(target_session)}, indent=2)+'\n')
    manifest = {'captured_at': datetime.now(timezone.utc).isoformat(), 'workbench': str(ROOT),
                'scope': 'Selected boot/nextstage evidence plus small pinned inventory-render assets (frozen RAM, user BIOS for initialization, C bridge and emulatorblitter). No disc image/raw tracks/modelweights copied.',
                'render_assets':[{'source':str(ROOT/name),'snapshot':str(RUNTIME/name),'sha256':hashlib.sha256((RUNTIME/name).read_bytes()).hexdigest()}for name in render_files],
                'files': files}
    (RUNTIME / 'evidence-snapshot.json').write_text(json.dumps(manifest, indent=2)+'\n')
    subprocess.run([str(python), '-c',
                    "import lab; lab.ingest('game',lab.ROOT/'corpus/game'); lab.ingest('advertising',lab.ROOT/'corpus/advertising')"],
                   cwd=RUNTIME, check=True)
    return RUNTIME


if __name__ == '__main__':
    print(install())
