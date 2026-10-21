#include "biwn_record4.h"

enum biwn_result biwn_record4_append(uint8_t *records, size_t records_size,
                                    uint16_t *count_word, const uint32_t args[4],
                                    uint32_t incoming_d0, uint32_t *result_d0)
{
    size_t offset, i;
    uint16_t count;
    if (!records || !count_word || !args || !result_d0)
        return BIWN_INVALID_ARGUMENT;
    count = *count_word;
    if (count >= 0x8000u)
        return BIWN_INVALID_ARGUMENT;
    if (count > 39u) {
        *result_d0 = incoming_d0 & UINT32_C(0xffff0000);
        return BIWN_OK;
    }
    offset = (size_t)count * 16u;
    if (records_size < offset + 16u)
        return BIWN_BUFFER_TOO_SMALL;
    for (i = 0; i < 4; ++i) {
        records[offset + i * 4] = (uint8_t)(args[i] >> 24);
        records[offset + i * 4 + 1] = (uint8_t)(args[i] >> 16);
        records[offset + i * 4 + 2] = (uint8_t)(args[i] >> 8);
        records[offset + i * 4 + 3] = (uint8_t)args[i];
    }
    *count_word = (uint16_t)(count + 1u);
    *result_d0 = 1;
    return BIWN_OK;
}
