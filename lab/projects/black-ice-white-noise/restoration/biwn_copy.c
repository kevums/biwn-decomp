#include "biwn_copy.h"

enum biwn_result biwn_copy_cpu_bytes(uint8_t *ram, size_t ram_size,
                                    uint32_t source, uint32_t destination,
                                    uint32_t count)
{
    uint32_t i;
    if (!ram || count > 127u) return BIWN_INVALID_ARGUMENT;
    if ((size_t)source > ram_size || (size_t)destination > ram_size ||
        count > ram_size - (size_t)source ||
        count > ram_size - (size_t)destination ||
        count > UINT32_MAX - source || count > UINT32_MAX - destination)
        return BIWN_BUFFER_TOO_SMALL;
    for (i = 0; i < count; ++i) ram[destination + i] = ram[source + i];
    return BIWN_OK;
}

enum biwn_result biwn_copy_device_commands(
    uint32_t source, uint32_t destination, uint32_t count,
    struct biwn_register_command *commands, size_t capacity,
    size_t *command_count, uint32_t *source_end, uint32_t *destination_end)
{
    size_t needed, n = 0;
    uint32_t remaining = count;
    if (!commands || !command_count || !source_end || !destination_end ||
        count < 128u || count >= UINT32_C(0x80000000))
        return BIWN_INVALID_ARGUMENT;
    needed = 2u + 6u * (size_t)(count / 65536u + (count % 65536u != 0u));
    if (capacity < needed) return BIWN_BUFFER_TOO_SMALL;
#define EMIT(a, v) do { commands[n].address = (a); commands[n].value = (v); ++n; } while (0)
    EMIT(UINT32_C(0xf02204), UINT32_C(0x4020));
    EMIT(UINT32_C(0xf02228), UINT32_C(0x4020));
    while (remaining) {
        uint32_t chunk = remaining < 65536u ? remaining : 65536u;
        uint32_t source_half = (source & 7u) >> 1;
        uint32_t destination_half = (destination & 7u) >> 1;
        EMIT(UINT32_C(0xf0223c), UINT32_C(0x10000) | (chunk >> 1));
        EMIT(UINT32_C(0xf02200), destination & UINT32_C(0xfffffff8));
        EMIT(UINT32_C(0xf0220c), destination_half);
        EMIT(UINT32_C(0xf02224), source & UINT32_C(0xfffffff8));
        EMIT(UINT32_C(0xf02230), source_half);
        EMIT(UINT32_C(0xf02238), source_half > destination_half ?
             UINT32_C(0x1800005) : UINT32_C(0x1800001));
        source += chunk;
        destination += chunk;
        remaining -= chunk;
    }
#undef EMIT
    *command_count = n;
    *source_end = source;
    *destination_end = destination;
    return BIWN_OK;
}
