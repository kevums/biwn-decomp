"""Add default-off IRQ decision ownership to a frozen fast GPU core copy.

Retains the original decision branches when disabled. Also carries the previously
tested exception-entry handoff; no devices, ACK, timing or serialization changes.
"""
import ast
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parent = json.loads((ROOT / 'verification/GPU-register-state-experimental-candidate.json').read_text())
    core = Path(parent['core_path'])
    assert sha(core) == parent['core_sha256']
    source = core.parent
    out = ROOT / 'verification/CPU-IRQ-selection-core-build' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    build = out / 'source'
    shutil.copytree(source, build, symlinks=True, ignore=shutil.ignore_patterns('.git', '*.o', '*.dylib', '*.so', '*.dll', 'private'))
    path = build / 'src/m68000/m68kinterface.c'
    original = path.read_text()
    # Reuse the exact existing entry handoff rather than reconstructing it again.
    tree = ast.parse((ROOT / 'scripts/build_biwn_CPU_IRQ_owner_core.py').read_text())
    additions = [n.value.value for n in ast.walk(tree) if isinstance(n, ast.Assign)
                 and any(isinstance(t, ast.Name) and t.id == 'addition' for t in n.targets)]
    assert len(additions) == 1
    needle = '// Service an interrupt request and start exception processing\nvoid m68ki_exception_interrupt(uint32_t intLevel)'
    assert original.count(needle) == 1
    text = original.replace(needle, additions[0] + needle, 1)
    needle = '\t// Start exception processing\n\tsr = m68ki_init_exception();'
    assert text.count(needle) == 1
    text = text.replace(needle, '''   if (biwnCPUIRQOwner != NULL)
   {
      if (biwnCPUIRQOwner(intLevel, vector) == 1)
         biwnCPUIRQOwned++;
      else
         biwnCPUIRQRejected++;
      return;
   }
   biwnCPUIRQOriginal++;

''' + needle, 1)
    needle = 'int m68k_execute(int num_cycles)'
    assert text.count(needle) == 1
    selection = '''/* Diagnostic source interrupt decision handoff.  Zero means no service;
 * negative, out-of-range, or a different positive level rejects without an
 * original selection fallback.  Queues, ACK, CPU commit and clocks stay host. */
typedef int (*BIWNCPUInterruptSelector)(unsigned, unsigned, unsigned, unsigned);
static BIWNCPUInterruptSelector biwnCPUInterruptSelector = NULL;
static uint64_t biwnCPUInterruptOwned = 0;
static uint64_t biwnCPUInterruptOriginal = 0;
static uint64_t biwnCPUInterruptRejected = 0;
void BIWNSetCPUInterruptSelector(BIWNCPUInterruptSelector selector)
{
   biwnCPUInterruptSelector = selector;
   biwnCPUInterruptOwned = biwnCPUInterruptOriginal = biwnCPUInterruptRejected = 0;
}
uint64_t BIWNCPUInterruptOwnedCount(void) { return biwnCPUInterruptOwned; }
uint64_t BIWNCPUInterruptOriginalCount(void) { return biwnCPUInterruptOriginal; }
uint64_t BIWNCPUInterruptRejectedCount(void) { return biwnCPUInterruptRejected; }
static int biwnCPUChooseInterrupt(unsigned kind, unsigned previous, unsigned level, unsigned mask)
{
   int chosen;
   chosen = biwnCPUInterruptSelector(kind, previous, level, mask);
   if (chosen < 0 || chosen > 7 || (chosen != 0 && (unsigned)chosen != level))
   {
      biwnCPUInterruptRejected++;
      return 0;
   }
   biwnCPUInterruptOwned++;
   return chosen;
}

'''
    text = text.replace(needle, selection + needle, 1)
    needle = 'int m68k_execute(int num_cycles)\n{'
    text = text.replace(needle, needle + '\n   if (biwnCPUInterruptRejected != 0) return num_cycles;', 1)
    needle = '\t\telse if (regs.intLevel > regs.intmask && TOMIRQRequestActive())'
    assert text.count(needle) == 1
    text = text.replace(needle, '''      else if ((biwnCPUInterruptSelector != NULL
                ? biwnCPUChooseInterrupt(0, regs.intLevel, regs.intLevel, regs.intmask) > 0
                : (biwnCPUInterruptOriginal++, regs.intLevel > regs.intmask)) && TOMIRQRequestActive())''', 1)
    needle = '\n#ifdef M68K_HOOK_FUNCTION\n\t\tM68KInstructionHook();'
    assert text.count(needle) == 1
    text = text.replace(needle, '\n      if (biwnCPUInterruptRejected != 0) { regs.remainingCycles = 0; return num_cycles; }\n' + needle, 1)
    needle = '\tint oldLevel = regs.intLevel;\n\tregs.intLevel = intLevel;'
    assert text.count(needle) == 1
    text = text.replace(needle, '''   int oldLevel = regs.intLevel;
   int selectedLevel;
   regs.intLevel = intLevel;
   if (biwnCPUInterruptSelector != NULL)
   {
      selectedLevel = biwnCPUChooseInterrupt(1, oldLevel, regs.intLevel, regs.intmask);
      if (selectedLevel > 0) m68ki_exception_interrupt((uint32_t)selectedLevel);
      return;
   }
   biwnCPUInterruptOriginal++;''', 1)
    needle = 'static INLINE void m68ki_check_interrupts(void)\n{'
    assert text.count(needle) == 1
    text = text.replace(needle, needle + '''
   int selectedLevel;
   if (biwnCPUInterruptSelector != NULL)
   {
      selectedLevel = biwnCPUChooseInterrupt(0, regs.intLevel, regs.intLevel, regs.intmask);
      if (selectedLevel > 0) m68ki_exception_interrupt((uint32_t)selectedLevel);
      return;
   }
   biwnCPUInterruptOriginal++;
''', 1)
    needle = '// Service an interrupt request and start exception processing'
    text = text.replace(needle, 'void BIWNCPUCheckInterruptsForTest(void) { m68ki_check_interrupts(); }\n\n' + needle, 1)
    path.write_text(text)
    exports = ['BIWNSetCPUIRQOwner', 'BIWNCPUIRQOwnedCount', 'BIWNCPUIRQOriginalCount', 'BIWNCPUIRQRejectedCount',
               'BIWNCommitCPUIRQEntry', 'm68ki_exception_interrupt', 'm68k_set_irq2', 'BIWNSetCPUInterruptSelector',
               'BIWNCPUInterruptOwnedCount', 'BIWNCPUInterruptOriginalCount', 'BIWNCPUInterruptRejectedCount', 'BIWNCPUCheckInterruptsForTest']
    p = build / 'exports-test.list'
    old = p.read_text()
    p.write_text(old + ''.join('\n_' + n for n in exports if '_' + n not in old.splitlines()) + '\n')
    p = build / 'link-test.T'
    p.write_text(p.read_text().replace('global:', 'global:\n    ' + '; '.join(exports) + ';', 1))
    report = dict(status='building', directory=str(out), source=str(build), parent_core=str(core), parent_core_sha256=parent['core_sha256'],
                  default_owners_NULL=True, new_training=False, coordinator_authored=True, whole_game_complete=False,
                  scope='Default-off interrupt level/mask/NMI decision and prior entry handoff. Original branches retained disabled. Queue, line provider, ACK/vector resolution, commit/prefetch/cycle charge and devices unchanged; pinned-emulator compatibility, not hardware accuracy or standalone completion.')
    pointer = ROOT / 'verification/CPU-IRQ-selection-core-experimental-candidate.json'

    def record():
        for dest in [out / 'report.json', pointer]:
            dest.write_text(json.dumps(report, indent=2) + '\n')

    env = dict(os.environ, DEVELOPER_DIR='/Library/Developer/CommandLineTools')
    for label, command in [('C89-lint', ['bash', 'scripts/c89-lint.sh', 'src/m68000/m68kinterface.c']),
                           ('compiler', ['make', '-j8', 'TEST_EXPORTS=1']), ('core-tests', ['make', 'TEST_EXPORTS=1', 'test'])]:
        record()
        with (out / (label + '.log')).open('w') as log:
            result = subprocess.run(command, cwd=build, env=env, stdout=log, stderr=subprocess.STDOUT)
        report[label + '_exit'] = result.returncode
        if result.returncode:
            report.update(status='build_or_core_test_failed', failed_phase=label)
            record()
            raise RuntimeError(str(out / (label + '.log')))
    assert (source / 'src/m68000/m68kinterface.c').read_text() == original and sha(core) == parent['core_sha256']
    result = build / 'virtualjaguar_libretro.dylib'
    report.update(status='compiled_core_tests_passed_pending_behavior_comparison', core_path=str(result), core_sha256=sha(result), source_sha256=sha(path))
    record()
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
