"""Compile the candidate Ghidra division C verbatim and compare saved CPU cases."""
import ctypes
import datetime
import json
from pathlib import Path
import subprocess
import extract_biwn_stage as stage


def main():
    root = stage.ROOT
    session = Path(json.loads((root / 'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    checks = json.loads((session / 'divu-candidate-pcode-checks.json').read_text())
    if checks['cases'] != 592 or checks['DIVU_failures'] or checks['helper_failures']:
        raise ValueError('Candidate p-code comparison has not passed')
    exported = session / 'nextstage-divu-export/decompiled.c'
    text = exported.read_text()
    start = text.index('uint analyst_u32_div_u16(')
    end = text.index('/* Address ', start)
    function = text[start:end].strip()
    if not function.endswith('}') or 'analyst_cd_offset' in function:
        raise ValueError('Unexpected decompiled function boundary')
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    folder = root / 'verification/biwn-decompiled-division' / stamp
    folder.mkdir(parents=True)
    source = folder / 'decompiled_division.c'
    # Only type/concatenation compatibility scaffolding; function body unchanged.
    prelude = '''#include <stdint.h>
typedef uint16_t ushort;
typedef uint32_t uint;
#define CONCAT22(a,b) (((uint32_t)(uint16_t)(a) << 16) | (uint16_t)(b))
'''
    source.write_text(prelude + function + '\n')
    library = folder / 'libdecompiled_division.dylib'
    # Ghidra omits optional parentheses around & within |. Preserve its body
    # verbatim and suppress only that formatting warning, not semantic warnings.
    command = ['clang', '-dynamiclib', '-std=c11', '-Wall', '-Wextra', '-Werror',
               '-Wno-bitwise-op-parentheses', '-O2', str(source), '-o', str(library)]
    compiled = subprocess.run(command, capture_output=True, text=True)
    (folder / 'compile.log').write_text(compiled.stdout + compiled.stderr)
    compiled.check_returncode()
    lib = ctypes.CDLL(str(library))
    lib.analyst_u32_div_u16.argtypes = [ctypes.c_uint16, ctypes.c_uint32]
    lib.analyst_u32_div_u16.restype = ctypes.c_uint32
    fixtures = json.loads((root / 'verification/biwn-cd-math-checks.json').read_text())
    results = []
    for case in fixtures['division_cases']:
        actual = lib.analyst_u32_div_u16(case['divisor'], case['numerator'])
        assert actual == case['quotient'] == case['numerator'] // case['divisor']
        results.append({**case, 'decompiled_C_quotient': actual})
    report = {
        'time': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'status': 'candidate_decompiled_division_C_compiled_and_matched_saved_original_CPU_cases',
        'cases': len(results), 'results': results,
        'exported_C': str(exported), 'exported_C_sha256': stage.cdi_layout.sha(exported),
        'compiled_source': str(source), 'compiled_source_sha256': stage.cdi_layout.sha(source),
        'function_body_verbatim_from_export': True, 'compatibility_prelude': prelude,
        'compile_command': command,
        'scope': 'One annotated nonzero-divisor helper, not a compiled complete decompilation. Full flags ABI, zero-divisor traps, other functions and whole-game behavior unverified.',
    }
    path = folder / 'checks.json'
    path.write_text(json.dumps(report, indent=2) + '\n')
    (root / 'verification/biwn-decompiled-division-checks.json').write_text(json.dumps({'latest': str(path), **report}, indent=2) + '\n')
    print(path)


if __name__ == '__main__':
    main()
