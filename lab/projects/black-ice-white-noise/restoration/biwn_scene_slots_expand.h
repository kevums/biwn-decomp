#ifndef BIWN_SCENE_SLOTS_EXPAND_H
#define BIWN_SCENE_SLOTS_EXPAND_H
#include "biwn_world_update.h"
struct biwn_scene_slot_seed { uint32_t D0,D4,D5,D6; };
/* Analyst name for complete 1142E..11760. D4..D6 incoming values matter on
 * invalid face selectors and persist across iterations. E26C remains an
 * explicit GPU service: logical args are four longs (slot,D1,D2,D3) plus a
 * zero WORD; its implementation and overread beyond that word are excluded.
 * bus.poll_limit bounds completed iterations (added host behavior).
 * Status0 success,1 badargs,2 bus,3 helper,4 poll_limit. On error retain prior
 * writes and leave out_D0 unchanged. CCR, stack, other registers and timing
 * are excluded. Preserve data access widths/order and volatile rereads. */
int biwn_scene_slots_expand(struct biwn_world_bus *,
                           const struct biwn_scene_slot_seed *,uint32_t *);
#endif
