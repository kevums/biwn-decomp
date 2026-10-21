/* Local concise Author draft, with three explicit coordinator corrections:
 * write D1; preserve incoming X at the early CLR.W return; clear Z on success.
 * Raw local response remains unchanged in its recorded run. */
#include "actor-navigation-native.h"

void biwn_native_actor_nav_left(uint32_t *r)
{
    uint32_t a0 = NAR32(r[15] + 4);
    uint32_t d0 = 3;
    d0 &= NAR32(r[15] + 8);
    if (d0 != 0) {
        d0 = 0;
        r[0] = d0;
        r[8] = a0;
        r[16] = (r[16] & 0xfff0u) | 0x04u;
        return;
    }
    d0 = 0;
    d0 = NAR8(a0 + 0x6e);
    d0 += 0x20;
    d0 >>= 6;
    if (d0 > 4) {
        d0 = 0;
        r[0] = d0;
        r[8] = a0;
        r[16] = (r[16] & 0xffe0u) | 0x04u;
        return;
    }
    d0 &= 7;
    d0 <<= 1;
    uint16_t off = NAR16(0x13f3e + d0);
    uint32_t target = 0x13f3e + off;
    r[1] = 7;
    uint32_t d0b;
    if (target == 0x13f48) {
        a0 = NAR32(a0 + 0x44);
        d0b = NAR16(a0 + 0x8);
    } else if (target == 0x13f5a) {
        a0 = NAR32(a0 + 0x44);
        d0b = NAR16(a0 + 0x4);
    } else if (target == 0x13f64) {
        a0 = NAR32(a0 + 0x44);
        d0b = NAR16(a0 + 0x6);
    } else if (target == 0x13f6e) {
        a0 = NAR32(a0 + 0x44);
        d0b = NAR16(a0 + 0x2);
    } else {
        d0b = 0;
    }
    d0b &= 0xf000;
    if (d0b != 0) {
        d0 = 0;
        r[0] = d0;
        r[8] = a0;
        r[16] = (r[16] & 0xffe0u) | 0x04u;
        return;
    }
    d0 = 1;
    r[0] = d0;
    r[8] = a0;
    r[16] = r[16] & 0xffe0u;
}
