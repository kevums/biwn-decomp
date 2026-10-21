#ifndef BIWN_BOOT_SLICES_H
#define BIWN_BOOT_SLICES_H

#include <stddef.h>
#include <stdint.h>

/* Analyst-assigned names. These are isolated reconstructions, not original
 * source, a BIOS replacement, a complete boot loader, or a working game port. */
enum biwn_result {
    BIWN_OK = 0,
    BIWN_INVALID_ARGUMENT = 1,
    BIWN_BUFFER_TOO_SMALL = 2,
    BIWN_TOC_SCAN_OUT_OF_RANGE = 3
};

struct biwn_cd_read_plan {
    uint32_t packed_binary_msf;
    uint32_t destination_begin;
    uint32_t destination_end;
    uint32_t partition_marker;
    uint32_t circular_buffer_bytes;
    uint32_t selected_track;
};

/* Original CPU range 0x18007e..0x180094. Source GPU block begins at boot+0x188.
 * Destination is a caller-owned host buffer representing GPU RAM at 0xf03200.
 * Buffers must not overlap. No device writes or GPU execution occur. */
enum biwn_result biwn_copy_gpu_boot(uint8_t *destination, size_t destination_size,
                                   const uint8_t *boot, size_t boot_size);

/* Original CPU range 0x1800c8..0x18015a, stopping before JSR CD_read.
 * TOC is the supplied byte buffer that would start at RAM 0x2c00.
 * Retains the original first scanner's omission of the final two entries.
 * Bounds failures return an error rather than reading outside the host buffer;
 * original hardware code has no equivalent bound and can continue scanning.
 * A successful plan does not validate TOC provenance or execute the read. */
enum biwn_result biwn_plan_cd_read(const uint8_t *toc, size_t toc_size,
                                  struct biwn_cd_read_plan *plan);

#endif
