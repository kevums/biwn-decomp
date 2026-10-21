#include "biwn_slot_clear.h"

int biwn_slot_clear(struct biwn_slot_bus *bus, uint16_t first_slot,
                    uint16_t count_words, uint32_t *out_D0) {
    if (bus == 0 || bus->write8 == 0 || out_D0 == 0) {
        return 1;
    }

    int32_t slot = (first_slot < 32768) ? (int32_t)first_slot : (int32_t)first_slot - 65536;
    uint32_t addr = (uint32_t)slot * 64u + 0x47b88u;

    int32_t count = (count_words < 32768) ? (int32_t)count_words : (int32_t)count_words - 65536;
    uint32_t limit = (uint32_t)count * 64u;

    if (limit == 0) {
        *out_D0 = 0;
        return 0;
    }

    uint16_t counter = 0;
    while (1) {
        if (bus->write8(bus->context, addr, 0) != 0) {
            return 2;
        }
        addr++;
        counter++;
        int32_t c = (counter < 32768) ? (int32_t)counter : (int32_t)counter - 65536;
        if (limit <= (uint32_t)c) {
            break;
        }
    }

    *out_D0 = limit;
    return 0;
}
