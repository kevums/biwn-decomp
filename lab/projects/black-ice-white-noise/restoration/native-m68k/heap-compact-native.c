#include "heap-native.h"

void biwn_native_heap_compact_body(uint32_t *r)
{
    uint32_t destination = HR(0x112D60);
    uint32_t source = destination + HR(destination);
    uint32_t size = 0;

    r[0] = 0x1BFFFF;

    if (source > 0x1BFFFF)
        goto tail;

move_block:
    size = HR(source);
    biwn_native_heap_copy_capture(r, source, destination, size);
    r[8] = HR(destination + 4);
    r[9] = destination + 8;
    HW(r[8], r[9]);
    source += HR(destination);
    if (source > 0x1BFFFF)
        goto next_destination;

    if (HR(source + 4) >= BIWN_HEAP_FLOOR)
        goto skip_block;
    if (HR(source + 4) != 0)
        goto next_destination;
    source += HR(source);
    if (source > 0x1BFFFF)
        goto next_destination;
    if (HR(source + 4) >= BIWN_HEAP_FLOOR)
        goto skip_block;
    if (HR(source + 4) != 0)
        goto next_destination;

skip_block:
    source += HR(source);
    if (source > 0x1BFFFF)
        goto next_destination;
    if (HR(source + 4) >= BIWN_HEAP_FLOOR)
        goto skip_block;
    if (HR(source + 4) == 0)
        goto skip_block;

next_destination:
    destination += size;
    if (source <= 0x1BFFFF)
        goto move_block;

tail:
    r[9] = 0x1C0000u - destination;
    HW(destination, r[9]);
    biwn_native_heap_clear_tail(destination);
    HW(0x112D60, destination);
    r[16] = (r[16] & 0xfff0u) | (destination == 0 ? 4u : 0u) | (destination & 0x80000000u ? 8u : 0u);
}
