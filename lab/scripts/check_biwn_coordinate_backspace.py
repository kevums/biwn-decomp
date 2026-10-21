"""Exhaust the original coordinate backspace word arithmetic in Unicorn."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time

from unicorn import Uc, UC_ARCH_M68K, UC_MODE_BIG_ENDIAN
from unicorn.m68k_const import UC_CPU_M68K_M68000, UC_M68K_REG_D0, UC_M68K_REG_D4, UC_M68K_REG_SR

ROOT = Path(__file__).resolve().parents[1]


def main():
    atlas = ROOT / 'verification/zero-warm-startup-instruction-atlas.bin'
    memory = atlas.read_bytes()
    cpu = Uc(UC_ARCH_M68K, UC_MODE_BIG_ENDIAN)
    cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000)
    cpu.mem_map(0, 0x200000)
    cpu.mem_write(0, memory)
    cpu.reg_write(UC_M68K_REG_SR, 0x2000)
    start, outputs = time.monotonic(), bytearray()
    for word in range(65536):
        cpu.reg_write(UC_M68K_REG_D4, word)
        cpu.emu_start(0x18ff2, 0x1901c, count=100)
        result = cpu.reg_read(UC_M68K_REG_D4) & 65535
        signed = word if word < 32768 else word - 65536
        expected = (abs(signed) // 10 * (-1 if signed < 0 else 1)) & 65535
        assert result == expected, (word, result, expected)
        quotient = abs(signed) // 10 * (-1 if signed < 0 else 1)
        expected_d0 = (quotient - (signed < 0)) & 65535
        assert cpu.reg_read(UC_M68K_REG_D0) == expected_d0, (word, cpu.reg_read(UC_M68K_REG_D0), expected_d0)
        outputs += expected_d0.to_bytes(4, 'big') + result.to_bytes(2, 'big')
    out = ROOT / 'verification/coordinate-backspace-exhaustive' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    (out / 'outputs.bin').write_bytes(outputs)
    report = dict(status='all_signed_word_backspace_results_equal_C99_truncating_division_by10', cases=65536,
        source_start='0x18ff2', stop_before='0x1901c', atlas=str(atlas), atlas_sha256=hashlib.sha256(memory).hexdigest(),
        source_bytes_sha256=hashlib.sha256(memory[0x18ff2:0x1901c]).hexdigest(),
        outputs_sha256=hashlib.sha256(outputs).hexdigest(), source_checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        seconds=time.monotonic() - start, directory=str(out),
        full_D0_result_also_exhaustively_checked=True,
        scope='Original M68000 instructions in Unicorn for every low16bit input. LowD4 and fullD0 results checked, not other registers/CCR/state or a new full game function.')
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    (ROOT / 'verification/coordinate-backspace-exhaustive-current.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], report['cases'], flush=True)


if __name__ == '__main__':
    main()
