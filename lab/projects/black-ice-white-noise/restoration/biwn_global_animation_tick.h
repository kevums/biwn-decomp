#ifndef BIWN_GLOBAL_ANIMATION_TICK_H
#define BIWN_GLOBAL_ANIMATION_TICK_H
#include "biwn_world_update.h"
/* Analyst name for BIWN 10BA4..10C16 (including final RTS).
 * Bus-visible effects and full D0 only; CCR/other registers/private stack,
 * timing and the semantic identity of the selected graphics are excluded.
 * Status: 0 success,1 bad arguments,2 bus error. Errors retain prior bus
 * effects and leave out_D0 unchanged. read16/read32/write16/write32 required. */
int biwn_global_animation_tick(struct biwn_world_bus *,uint32_t,uint32_t *);
#endif
