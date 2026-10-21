#include <stdint.h>

uint32_t biwn_frame_lookup_body(uint32_t wanted)
{
    volatile uint16_t *tags = (volatile uint16_t *)0x15B4A0;
    uint16_t target = (uint16_t)(wanted & 0xFFFFu);

    for (uint32_t i = 0; i < 36; i++) {
        if (tags[i * 2] == target) {
            return i;
        }
    }
    return 36;
}
