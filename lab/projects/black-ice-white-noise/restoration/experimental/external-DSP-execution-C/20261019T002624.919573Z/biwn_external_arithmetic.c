#include <stdint.h>
#include "biwn_dsp_external_engine.h"

uint32_t biwn_external_addc(struct biwn_dsp_external_engine_state *s, uint32_t a, uint32_t b) {
    uint64_t sum = (uint64_t)a + (uint64_t)b + (uint64_t)s->c;
    uint32_t r = (uint32_t)sum;
    s->c = (uint32_t)((sum >> 32) & 1u);
    s->z = (r == 0u) ? 1u : 0u;
    s->n = (r >> 31) & 1u;
    return r;
}

/* Coordinator correction: pinned MTOI sign-extends the upper9bits and preserves low23bits. */
uint32_t biwn_external_mtoi(uint32_t a) {
    return (a & 0x007fffffu) | ((a & 0x80000000u) ? 0xff800000u : 0u);
}
