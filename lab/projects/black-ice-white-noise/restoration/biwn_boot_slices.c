#include "biwn_boot_slices.h"
#include <string.h>

enum biwn_result biwn_copy_gpu_boot(uint8_t *destination, size_t destination_size,
                                   const uint8_t *boot, size_t boot_size)
{
    if (!destination || !boot)
        return BIWN_INVALID_ARGUMENT;
    if (destination_size < 2004 || boot_size < 0x95c)
        return BIWN_BUFFER_TOO_SMALL;
    /* MOVE.W #0x1f4,D0; MOVE.L (A0)+,(A1)+; DBF D0 repeats 501 times.
     * Byte copying preserves big-endian words on hosts of either endianness. */
    memcpy(destination, boot + 0x188, 2004);
    return BIWN_OK;
}

static int signed_byte(uint8_t value)
{
    return value < 128 ? value : (int)value - 256;
}

static uint32_t read_be32(const uint8_t *p)
{
    return ((uint32_t)p[0] << 24) | ((uint32_t)p[1] << 16) |
           ((uint32_t)p[2] << 8) | p[3];
}

static uint32_t six_frames_earlier(uint32_t packed)
{
    /* Literal arithmetic widths at 0x180128..0x180140. Values are binary
     * minutes/seconds/frames in separate bytes; they are not BCD digits. */
    uint8_t frame = (uint8_t)packed;
    packed = (packed & UINT32_C(0xffffff00)) | (uint8_t)(frame - 6);
    if (frame < 6) {
        packed = (packed & UINT32_C(0xffffff00)) | (uint8_t)((uint8_t)packed + 75);
        uint16_t word = (uint16_t)packed;
        packed = (packed & UINT32_C(0xffff0000)) | (uint16_t)(word - 0x100);
        if (word < 0x100) {
            packed = (packed & UINT32_C(0xffff0000)) | (uint16_t)((uint16_t)packed + 0x3c00);
            packed -= 0x10000;
        }
    }
    return packed;
}

static int entry_available(size_t offset, size_t size)
{
    return offset <= size && size - offset >= 8;
}

enum biwn_result biwn_plan_cd_read(const uint8_t *toc, size_t toc_size,
                                  struct biwn_cd_read_plan *plan)
{
    if (!toc || !plan)
        return BIWN_INVALID_ARGUMENT;
    if (toc_size < 4)
        return BIWN_BUFFER_TOO_SMALL;
    uint8_t counter = (uint8_t)(toc[3] - 1);
    uint8_t smallest = 100;
    size_t offset = 0;
    /* SUB.B #1,D1 / BEQ precedes each ADDA #8,A0. Do not replace this
     * with a scan of every track: max track 5 examines entries 1,2,3. */
    for (;;) {
        counter = (uint8_t)(counter - 1);
        if (counter == 0)
            break;
        offset += 8;
        if (!entry_available(offset, toc_size))
            return BIWN_TOC_SCAN_OUT_OF_RANGE;
        if (toc[offset + 4] != 1)
            continue;
        uint8_t track = toc[offset];
        if (signed_byte(smallest) < signed_byte(track))
            continue;
        smallest = track;
    }
    /* The second scanner restarts from entry 1; it does not use the A1
     * pointer retained by the first loop. Its original loop is unbounded. */
    offset = 0;
    for (;;) {
        offset += 8;
        if (!entry_available(offset, toc_size))
            return BIWN_TOC_SCAN_OUT_OF_RANGE;
        if (toc[offset + 4] == 1 && toc[offset] == smallest)
            break;
    }
    struct biwn_cd_read_plan result = {
        .packed_binary_msf = six_frames_earlier(read_be32(toc + offset) & 0xffffff),
        .destination_begin = 0x4000,
        .destination_end = 0x100000,
        .partition_marker = 0x53545542,
        .circular_buffer_bytes = 0,
        .selected_track = smallest
    };
    *plan = result;
    return BIWN_OK;
}
