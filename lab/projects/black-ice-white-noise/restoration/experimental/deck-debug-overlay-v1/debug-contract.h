#ifndef BIWN_DECK_DEBUG_OVERLAY_CPU_H
#define BIWN_DECK_DEBUG_OVERLAY_CPU_H
#include "../deck-scene-source/deck-scene-contract.h"
/* Complete 10734..10968 caller, stopping at 10966 RTS. Original MMIO
 * writes remain bus operations. Formatter 1B45A and text 149AE are explicit
 * CPU services stopping before their RTS. No cached host scratch buffer.
 * Added host errors retain earlier bus effects and leave input CPU unchanged.
 */
void biwn_debug_overlay_body(struct biwn_deck_context *);
int biwn_debug_overlay_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_world_cpu_service,void *,uint32_t);
#endif
