"""Expose read-only DSP retirement context in a separate diagnostic core.

The live merchant test and its pinned core remain unchanged. This is plumbing
for the source music bridge, not proof of music execution ownership.
"""
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]


def main():
    parent_manifest = json.loads((ROOT/'verification/DSP-owner-experimental-candidate.json').read_text())
    parent = Path(parent_manifest['source'])
    out = ROOT/'verification/DSP-music-context-build'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    source = out/'source'
    shutil.copytree(parent, source, symlinks=True,
                    ignore=shutil.ignore_patterns('.git', '*.o', '*.dylib', '*.so', '*.dll', 'private'))
    path = source/'src/jerry/dsp.c'
    original = path.read_text()
    addition = '''
/* Read-only context omitted from the persistent savestate format. */
void BIWNDSPReadRetirementContext(uint32_t *delay, uint32_t *prestore_bank)
{
   if (delay != NULL)
      *delay = dspFlagsRetireDelay;
   if (prestore_bank != NULL)
      *prestore_bank = dspPreStoreBank == dsp_reg_bank_0 ? 0u : 1u;
}
'''
    path.write_text(original + addition)
    exports = source/'exports-test.list'
    exports.write_text(exports.read_text()+'\n_BIWNDSPReadRetirementContext\n')
    linker = source/'link-test.T'
    linker.write_text(linker.read_text().replace('global:', 'global:\n    BIWNDSPReadRetirementContext;', 1))
    env = {**os.environ, 'DEVELOPER_DIR': '/Library/Developer/CommandLineTools'}
    report = dict(status='building_read_only_retirement_context', directory=str(out),
                  source=str(source), parent_source=str(parent), parent_core_sha256=parent_manifest['core_sha256'],
                  whole_game_complete=False, music_ownership_verified=False)
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(out, flush=True)
    for label, command in [('C89-lint', ['bash', 'scripts/c89-lint.sh', 'src/jerry/dsp.c']),
                           ('compiler', ['make', '-j8', 'TEST_EXPORTS=1']),
                           ('core-tests', ['make', 'TEST_EXPORTS=1', 'test'])]:
        with (out/(label+'.log')).open('w') as log:
            result = subprocess.run(command, cwd=source, env=env, stdout=log, stderr=subprocess.STDOUT)
        report[label+'_exit'] = result.returncode
        (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
        assert result.returncode == 0, (label, out)
    assert (parent/'src/jerry/dsp.c').read_text() == original
    core = source/'virtualjaguar_libretro.dylib'
    report.update(status='compiled_tests_exit_zero_pending_inertness_and_live_music',
                  core_path=str(core), core_sha256=hashlib.sha256(core.read_bytes()).hexdigest(),
                  source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                  audio_gates='Inspect core-tests.log: skipped private-ROM gates do not establish audio completion.',
                  RetroArch_verified=False)
    text = json.dumps(report, indent=2)+'\n'
    (out/'report.json').write_text(text)
    (ROOT/'verification/DSP-music-context-experimental-candidate.json').write_text(text)
    print(report['status'], flush=True)


if __name__ == '__main__':
    main()
