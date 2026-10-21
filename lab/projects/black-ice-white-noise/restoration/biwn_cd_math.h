#ifndef BIWN_CD_MATH_H
#define BIWN_CD_MATH_H
#include "biwn_boot_slices.h"

/* Analyst names; translated from candidate RAM 0xd1e0..0xd204. Original
 * divisor is D0.w, numerator/result D1.l, D2 preserved. Flags not modeled.
 * Zero divisor returns an error here; original CPU code would trap. */
enum biwn_result biwn_divide_u32_u16(uint32_t numerator, uint16_t divisor,
                                    uint32_t *quotient);

struct biwn_cd_position {
    uint32_t packed_binary_msf;
    uint32_t toc_entry_offset;
};

/* Candidate RAM 0xd206..0xd29e, with two 32-bit stack arguments.
 * The raw selector increments its LOW WORD for each scanned entry whose
 * session byte is zero, then compares its LOW BYTE with the entry track byte.
 * It is deliberately not described as an unconditional track number or index.
 * Offset is divided by 2352, added to TOC time, then moved six frames earlier.
 * Bounds errors replace the original unbounded scanner; output stays unchanged.
 * No BIOS/device operations or claims about actual TOC provenance. */
enum biwn_result biwn_cd_offset_msf(uint32_t selector, uint32_t byte_offset,
                                   const uint8_t *toc, size_t toc_size,
                                   struct biwn_cd_position *position);
#endif
