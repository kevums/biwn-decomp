#ifndef BIWN_FIRMWARE_TOC_CHECKSUM_H
#define BIWN_FIRMWARE_TOC_CHECKSUM_H
#include <stdint.h>
/* Exactly1024bytes;64source round constants;4output words.
 * Big-endian input words,16MD5-compression blocks, no padding.
 * Semantic digest only; no DSP state/IRQ/clock emulation.
 * Return0 on success,1 on null input with no output mutation.
 */
int biwn_firmware_TOC_checksum(const uint8_t *toc,
    const uint32_t *round_constants, uint32_t *out);
#endif
