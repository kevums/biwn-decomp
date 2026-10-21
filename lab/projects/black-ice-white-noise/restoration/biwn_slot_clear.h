#ifndef BIWN_SLOT_CLEAR_H
#define BIWN_SLOT_CLEAR_H
#include <stdint.h>
/* Analyst interface for 10968..1098E. Logical byte stores and full D0 only.
 * Native CLR dummy reads, CCR, other registers, stack and timing excluded.
 * The 16-bit loop counter is sign extended for an unsigned comparison;
 * count_words is not an ordinary memset length. Callback nonzero stops
 * with status 2; prior stores remain and out_D0 stays unchanged. */
typedef int (*biwn_slot_write8)(void *,uint32_t,uint8_t);
struct biwn_slot_bus { biwn_slot_write8 write8; void *context; };
int biwn_slot_clear(struct biwn_slot_bus *,uint16_t first_slot,
                    uint16_t count_words,uint32_t *out_D0);
#endif
