"""Join checked attack/scene-exit bodies with dual marker and source IRQ core.

No core, guest-byte, instruction timing or accepted body changes. Original
and repaired marker variants retain their explicit source implementations.
This build is unverified until its separately recorded frame comparisons.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil

from integrate_biwn_attack_CPU import compile_source

ROOT = Path(__file__).resolve().parents[1]
RESTORE = ROOT / 'projects/black-ice-white-noise/restoration'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')


def main():
    accepted = json.loads((ROOT / 'verification/live-attack-CPU-current.json').read_text())
    assert accepted['CPU_compatible_component_in_frame_runtime'] and accepted['native_fixture_cases'] == 20480
    attack = Path(accepted['reviewable_source'])
    assert sha(attack) == accepted['source_sha256']
    base = json.loads((ROOT / 'verification/building570-exit-CPU-experimental-candidate.json').read_text())
    fast = json.loads((ROOT / 'verification/building570-fast-native-CPU-experimental-candidate.json').read_text())
    dual = json.loads((ROOT / 'verification/dual-marker-native-CPU-experimental-candidate.json').read_text())
    assert fast['CPU_library'] == base['library']
    fast_source = Path(fast['directory']) / 'fast_CPU_bridge.c'
    dual_source = Path(dual['directory']) / 'fast_CPU_bridge.c'
    assert sha(fast_source) == fast['source_sha256'] and sha(dual_source) == dual['source_sha256']
    assert fast['cost_library'] == dual['cost_library']
    out = ROOT / 'verification/unified-restore-runtime-build' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    source = out / 'biwn_attack_cpu.c'
    shutil.copy2(attack, source)
    old_wrapper = Path(accepted['directory']) / 'attack_dispatch.c'
    wrapper = out / 'attack_dispatch.c'
    text = old_wrapper.read_text()
    assert text.count('biwn_main_static_CPU_step') == 2
    text = text.replace('biwn_main_static_CPU_step', base['function'])
    wrapper.write_text(text)
    library = out / 'libunified-restore-CPU.dylib'
    commands = []
    command = ['clang', '-dynamiclib', '-std=c99', '-O2', '-Wall', '-Wextra', '-Werror', '-I', str(RESTORE),
               str(source), str(wrapper), base['library'], '-o', str(library)]
    commands.append(command)
    compile_source(command, out / 'CPU-compiler.log')
    pattern = r'static const struct identity identities\[\]=\{.*?\};'
    new_table = re.findall(pattern, fast_source.read_text(), re.S)
    assert len(new_table) == 1
    text = dual_source.read_text()
    assert len(re.findall(pattern, text, re.S)) == 1
    text = re.sub(pattern, lambda _: new_table[0], text, count=1, flags=re.S)
    assert text.count('biwn_loaded_scene_doorway_CPU_step') == 2
    text = text.replace('biwn_loaded_scene_doorway_CPU_step', 'biwn_live_attack_CPU_step')
    needle = 'const struct stats*biwn_fast_CPU_end(void){'
    assert text.count(needle) == 1
    text = '#include <stdlib.h>\nextern int biwn_attack_stats_write(const char*);\n' + text
    text = text.replace(needle, needle + 'const char*p=getenv("BIWN_LIVE_ATTACK_COUNTERS");if(p&&biwn_attack_stats_write(p))fail(0,178);')
    bridge_source = out / 'fast_CPU_bridge.c'
    bridge_source.write_text(text)
    shutil.copytree(Path(dual['directory']) / 'pinned-CPU-headers', out / 'pinned-CPU-headers')
    bridge_library = out / 'libunified-restore-bridge.dylib'
    command = ['clang', '-dynamiclib', '-std=c99', '-O2', '-Wall', '-Wextra', '-Werror', '-I', str(RESTORE),
               str(bridge_source), str(library), dual['original_marker_CPU_library'], dual['cost_library'], '-o', str(bridge_library)]
    commands.append(command)
    compile_source(command, out / 'bridge-compiler.log')
    cpu_candidate, native_candidate = out / 'CPU-candidate.json', out / 'native-CPU-candidate.json'
    save(cpu_candidate, dict(base, directory=str(out), library=str(library), function='biwn_live_attack_CPU_step',
                             source_sha256=sha(source), movie_privileged_event_tokens=True,
                             checked_attack_body_proof=str(ROOT / 'verification/live-attack-CPU-current.json'),
                             runtime_verified=False))
    save(native_candidate, dict(dual, directory=str(out), library=str(bridge_library), CPU_library=str(library),
                                source_sha256=sha(bridge_source), identity_count=fast['identity_count'],
                                status='compiled_unified_attack_scene_exit_dual_marker_unverified'))
    report = dict(status='compiled_unified_restore_runtime_unverified', recorded_at=datetime.now(timezone.utc).isoformat(),
                  directory=str(out), CPU_candidate=str(cpu_candidate), native_CPU_candidate=str(native_candidate),
                  core=dual['required_core_path'], core_sha256=dual['required_core_sha256'],
                  GPU_candidate=str(ROOT / 'verification/CPU-IRQ-selection-GPU-experimental-candidate.json'),
                  DSP_candidate=str(ROOT / 'verification/CPU-IRQ-selection-DSP-experimental-candidate.json'),
                  commands=commands, attack_body_sha256=sha(source),
                  inputs_sha256={str(p): sha(p) for p in [attack, old_wrapper, fast_source, dual_source,
                      Path(base['library']), Path(dual['original_marker_CPU_library']), Path(dual['cost_library']),
                      Path(dual['required_core_path'])]},
                  artifacts_sha256={str(p): sha(p) for p in [source, wrapper, library, bridge_source, bridge_library,
                                                             cpu_candidate, native_candidate]},
                  whole_game_complete=False, default_preview_promoted=False,
                  scope='Exact accepted attack CPU body, scene570exit instruction coverage and dual original/repaired marker identities, with existing source IRQ-selection core. All other source/device dependencies remain. Compilation alone proves no new route or preview behavior.')
    save(out / 'report.json', report)
    save(ROOT / 'verification/unified-restore-runtime-candidate.json', report)
    print(out, flush=True)


if __name__ == '__main__':
    main()
