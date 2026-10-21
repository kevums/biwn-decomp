#include <stdint.h>

uint32_t biwn_native_controller_poll_body(void)
{
    volatile uint16_t *sel = (volatile uint16_t *)0xF14000u;
    volatile uint32_t *dat = (volatile uint32_t *)0xF14000u;
    volatile uint32_t *prev_p = (volatile uint32_t *)0x49BA4u;
    volatile uint32_t *edge_p = (volatile uint32_t *)0x49BACu;

    uint32_t acc = 0xFFFFFFFFu;
    uint32_t v;

    *sel = 0x810Eu;
    v = *dat;
    v = (v | 0xF0FFFFFCu) >> 4u | (v | 0xF0FFFFFCu) << 28u;
    acc &= v;

    *sel = 0x810Du;
    v = *dat;
    v = (v | 0xF0FFFFFCu) >> 8u | (v | 0xF0FFFFFCu) << 24u;
    acc &= v;

    *sel = 0x810Bu;
    v = *dat;
    v = (v | 0xF0FFFFFCu) << 12u | (v | 0xF0FFFFFCu) >> 20u;
    acc &= v;

    *sel = 0x8107u;
    v = *dat;
    v = (v | 0xF0FFFFFCu) << 8u | (v | 0xF0FFFFFCu) >> 24u;
    acc &= v;

    uint32_t held = ~acc;
    uint32_t previous = *prev_p;
    *prev_p = held;
    uint32_t edge = (previous ^ held) & held;
    *edge_p = edge;
    return edge;
}
