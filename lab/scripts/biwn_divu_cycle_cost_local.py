"""LM Studio local Restorer-authored cost-only helper, accepted after repair.

Source: pinned GPLv3-or-later UAE/Virtual Jaguar getDivu68kCycles calculation.
100056 arithmetic comparisons pass; no CPU instruction emulation or global
cycle scheduling. Exact source/prompt/response/gate provenance is stored at:
verification/easy-firmware-CD-routing/20261015T224427.439981Z/cycle-code-gate
"""
def divu_cycles(dividend, divisor):
    dividend &= 0xFFFFFFFF
    divisor &= 0xFFFF
    if divisor == 0:
        return -4
    if (dividend >> 16) >= divisor:
        return 5 * 2 - 4
    mcycles = 38
    hdivisor = (divisor << 16) & 0xFFFFFFFF
    for _ in range(15):
        temp = dividend
        dividend = (dividend << 1) & 0xFFFFFFFF
        if temp & 0x80000000:
            dividend = (dividend - hdivisor) & 0xFFFFFFFF
        else:
            mcycles += 2
            if dividend >= hdivisor:
                dividend = (dividend - hdivisor) & 0xFFFFFFFF
                mcycles -= 1
    return mcycles * 2 - 4
