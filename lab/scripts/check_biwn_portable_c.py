"""Compare portable C reconstruction with original boot CPU instructions."""
import ctypes
import datetime
import json
from pathlib import Path
import subprocess

import extract_biwn_stage as stage
import check_biwn_68000_slices as slices


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in [
        'packed_binary_msf', 'destination_begin', 'destination_end',
        'partition_marker', 'circular_buffer_bytes', 'selected_track']]


def buffer(data):
    return (ctypes.c_uint8 * len(data)).from_buffer_copy(data)


def main():
    root = stage.ROOT
    session = Path(json.loads((root / 'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory'])
    boot = (session / 'boot-payload-68000-candidate.bin').read_bytes()
    if stage.digest(boot) != stage.BOOT_SHA:
        raise ValueError('Original boot image differs')
    folder = root / 'projects/black-ice-white-noise/restoration'
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    build = root / 'verification/biwn-portable-c' / stamp
    build.mkdir(parents=True)
    library = build / 'libbiwn_boot_slices.dylib'
    command = ['clang', '-dynamiclib', '-std=c11', '-Wall', '-Wextra', '-Werror',
               '-O2', str(folder / 'biwn_boot_slices.c'), '-o', str(library)]
    subprocess.run(command, check=True, capture_output=True, text=True)
    lib = ctypes.CDLL(str(library))
    lib.biwn_plan_cd_read.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t, ctypes.POINTER(Plan)]
    lib.biwn_plan_cd_read.restype = ctypes.c_int
    lib.biwn_copy_gpu_boot.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t,
                                     ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t]
    lib.biwn_copy_gpu_boot.restype = ctypes.c_int
    layout = json.loads((session / 'cdi-layout.json').read_text())
    base_toc = bytes(slices.make_toc(layout))
    fixtures = [('cdi_derived_toc', base_toc)]
    # Different track counts and first session-2 positions exercise the actual
    # pre-decrement scan. Frames straddle frame, second and minute boundaries.
    times = [6, 75, 4500, 4502, 12779, 99 * 4500 + 4]
    for count in [3, 5, 8, 12]:
        for first in [1, count - 2]:
            for frames in times:
                toc = bytearray(0x400)
                toc[2:4] = bytes([1, count])
                for number in range(1, count + 1):
                    toc[number * 8:number * 8 + 8] = bytes([
                        number, *stage.msf(frames + (number - first) * 75 if number >= first else frames),
                        0 if number < first else 1, 0, 10, 0])
                fixtures.append((f'tracks{count}-session2at{first}-frames{frames}', bytes(toc)))
    comparisons = []
    register_map = {
        'packed_binary_msf': 'D0', 'destination_begin': 'A0', 'destination_end': 'A1',
        'partition_marker': 'D1', 'circular_buffer_bytes': 'D2', 'selected_track': 'D3'}
    for name, toc in fixtures:
        original = slices.run_slice(boot, 0x1800c8, 0x18015a, toc)
        result = Plan()
        assert lib.biwn_plan_cd_read(buffer(toc), len(toc), ctypes.byref(result)) == 0
        actual = {field: getattr(result, field) for field in register_map}
        expected = {field: int(original['registers'][register], 16) for field, register in register_map.items()}
        assert actual == expected, name
        # Independent wall-clock calculation also validates MSF borrow semantics.
        n = result.selected_track
        m, s, f = toc[n * 8 + 1:n * 8 + 4]
        em, es, ef = stage.msf((m * 60 + s) * 75 + f - 6)
        assert result.packed_binary_msf == (em << 16) | (es << 8) | ef
        comparisons.append({'fixture': name, 'toc_sha256': stage.digest(toc),
                            'plan': {k: hex(v) for k, v in actual.items()},
                            'original_instruction_count': original['instruction_count']})

    # The write guard and whole-register comparison above do not rely on the C
    # translation. They execute the preserved original bytes under Unicorn.
    original_copy = slices.run_slice(boot, 0x18007e, 0x180094, copy=True)
    destination = buffer(b'\xa5' * 2008)
    boot_buffer = buffer(boot)
    assert lib.biwn_copy_gpu_boot(destination, 2004, boot_buffer, len(boot)) == 0
    assert bytes(destination[:2004]) == boot[0x188:0x95c]
    assert bytes(destination[2004:]) == b'\xa5' * 4
    assert stage.digest(bytes(destination[:2004])) == original_copy['destination_sha256']
    guards = {}
    for name, destination_size, boot_size in [('short_destination', 2003, len(boot)), ('short_source', 2004, 0x95b)]:
        target = buffer(b'\xa5' * 2008)
        assert lib.biwn_copy_gpu_boot(target, destination_size, boot_buffer, boot_size) == 2
        assert bytes(target) == b'\xa5' * 2008
        guards[name] = 'rejected without writing'
    assert lib.biwn_copy_gpu_boot(None, 2004, boot_buffer, len(boot)) == 1
    guards['null_copy_destination'] = 'rejected'
    result = Plan(*([0xa5a5a5a5] * 6))
    before = bytes(result)
    assert lib.biwn_plan_cd_read(buffer(base_toc), 3, ctypes.byref(result)) == 2
    assert bytes(result) == before
    guards['short_toc'] = 'rejected; output plan unchanged'
    missing = bytearray(base_toc)
    for n in range(1, 6):
        missing[n * 8 + 4] = 0
    assert lib.biwn_plan_cd_read(buffer(missing), len(missing), ctypes.byref(result)) == 3
    assert bytes(result) == before
    guards['missing_session2'] = 'bounded error; output plan unchanged; original scanner is unbounded'
    report = {
        'time': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'status': 'two_portable_components_compiled_and_matched_selected_original_cpu_slices',
        'compiler': subprocess.check_output(['clang', '--version'], text=True).splitlines()[0],
        'compile_command': command, 'library': str(library),
        'source_sha256': {p.name: stage.cdi_layout.sha(p) for p in [folder / 'biwn_boot_slices.c', folder / 'biwn_boot_slices.h']},
        'original_boot_sha256': stage.BOOT_SHA,
        'toc_cpu_comparisons': comparisons,
        'gpu_copy': {'bytes': 2004, 'original_cpu_writes': len(original_copy['writes']),
                     'bytes_match_original_cpu_memory': True, 'host_guard_unchanged': True},
        'host_input_guards': guards,
        'limits': [
            'These are analyst-written isolated components; no original source or symbol names were recovered.',
            'TOC fixtures and Unicorn M68000 execution do not establish BIOS/device behavior.',
            'Host bounds errors deliberately replace unsafe out-of-buffer scanning; successful fixture behavior matches the original.',
            'No complete boot, GPU program, CD subsystem, streamed stage or game has been reconstructed or executed.',
        ],
    }
    output = build / 'checks.json'
    output.write_text(json.dumps(report, indent=2) + '\n')
    (root / 'verification/biwn-portable-c-checks.json').write_text(json.dumps({'latest': str(output), **report}, indent=2) + '\n')
    print(output)


if __name__ == '__main__':
    main()
