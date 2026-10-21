#ifndef BIWN_RECORD4_H
#define BIWN_RECORD4_H
#include "biwn_boot_slices.h"

/* Analyst name for 0xeac4..0xeb04; purpose beyond storing four words unknown.
 * Count at emulated 0x112940 is compared as SIGNED 16-bit against 39.
 * Records at 0x1126c0 contain four big-endian 32-bit stack arguments each.
 * Success sets all D0 to 1. Full sets only D0.w to zero, preserving D0's
 * upper half. Flags, A0 and intermediate store order are not modeled.
 * Host buffers/arguments/count/output must not overlap. Negative counts are
 * rejected without mutation; the original writes before the record array.
 * This bounded host translation is not a complete original-machine ABI. */
enum biwn_result biwn_record4_append(uint8_t *records, size_t records_size,
                                    uint16_t *count_word, const uint32_t args[4],
                                    uint32_t incoming_d0, uint32_t *result_d0);
#endif
