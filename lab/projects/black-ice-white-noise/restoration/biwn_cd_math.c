#include "biwn_cd_math.h"

enum biwn_result biwn_divide_u32_u16(uint32_t numerator, uint16_t divisor,
                                    uint32_t *quotient)
{
    if (!quotient || divisor == 0)
        return BIWN_INVALID_ARGUMENT;
    /* The original first tries DIVU.W and handles quotient overflow with
     * two further DIVU operations, preserving D2. Full C division yields
     * the same D1.l quotient; condition codes and divide traps are excluded. */
    *quotient = numerator / divisor;
    return BIWN_OK;
}

enum biwn_result biwn_cd_offset_msf(uint32_t selector, uint32_t byte_offset,
                                   const uint8_t *toc, size_t toc_size,
                                   struct biwn_cd_position *position)
{
    if (!toc || !position)
        return BIWN_INVALID_ARGUMENT;
    uint32_t sectors = byte_offset / 2352;
    uint32_t seconds = sectors / 75;
    uint32_t offset_msf = ((seconds / 60) << 16) |
                          ((seconds % 60) << 8) | (sectors % 75);
    size_t entry = 0;
    for (;;) {
        entry += 8;
        if (entry > toc_size || toc_size - entry < 8)
            return BIWN_TOC_SCAN_OUT_OF_RANGE;
        if (toc[entry + 4] == 0)
            selector = (selector & UINT32_C(0xffff0000)) | (uint16_t)(selector + 1);
        if (toc[entry] == (uint8_t)selector)
            break;
    }
    uint16_t minute = toc[entry + 1];
    uint16_t second = toc[entry + 2];
    uint8_t frame = (uint8_t)(toc[entry + 3] + (uint8_t)offset_msf);
    /* BMI after CMP.B tests the subtraction's N bit (not a signed C <).
     * Retain that exact byte behavior, also for noncanonical supplied TOCs. */
    if (((uint8_t)(frame - 75) & 128) == 0) {
        frame = (uint8_t)(frame - 75);
        second = (uint16_t)(second + 1);
    }
    offset_msf >>= 8;
    second = (second & 0xff00) | (uint8_t)((uint8_t)second + (uint8_t)offset_msf);
    if (((uint8_t)((uint8_t)second - 60) & 128) == 0) {
        second = (second & 0xff00) | (uint8_t)((uint8_t)second - 60);
        minute = (uint16_t)(minute + 1);
    }
    minute = (minute & 0xff00) | (uint8_t)((uint8_t)minute + (uint8_t)(offset_msf >> 8));
    uint32_t packed = ((uint32_t)minute << 16) | ((uint32_t)(uint8_t)second << 8) | frame;
    /* SUBQ.L #6 carries the initial borrow across bytes before TST.B/TST.W
     * decide whether to add binary frame/second bases. */
    packed -= 6;
    if ((packed & 128) != 0) {
        packed = (packed & UINT32_C(0xffffff00)) | (uint8_t)((uint8_t)packed + 75);
        if ((packed & 0x8000) != 0)
            packed = (packed & UINT32_C(0xffff0000)) | (uint16_t)((uint16_t)packed + 0x3c00);
    }
    struct biwn_cd_position result = {packed, (uint32_t)entry};
    *position = result;
    return BIWN_OK;
}
