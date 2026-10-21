#include <stdint.h>

int biwn_local_portal_key(unsigned direction, uint16_t x, uint16_t z,
                          uint16_t min_x, uint16_t max_x, uint16_t min_z, uint16_t max_z,
                          uint8_t encoded_key, uint16_t *key_out) {
    if (key_out == 0) return -1;
    if (direction >= 4) return -1;

    uint16_t diff;
    if (direction == 0) diff = (uint16_t)(x - min_x);
    else if (direction == 1) diff = (uint16_t)(max_x - x);
    else if (direction == 2) diff = (uint16_t)(max_z - z);
    else diff = (uint16_t)(z - min_z);

    uint16_t shifted_key = (uint16_t)(diff >> 6);
    if (diff & 0x8000u) shifted_key |= 0xFC00u;

    *key_out = shifted_key;

    uint16_t ext_key;
    if (encoded_key & 0x80u) ext_key = (uint16_t)(encoded_key | 0xFF00u);
    else ext_key = (uint16_t)encoded_key;

    if ((shifted_key & 0x000Fu) == ext_key) return 1;
    return 0;
}
