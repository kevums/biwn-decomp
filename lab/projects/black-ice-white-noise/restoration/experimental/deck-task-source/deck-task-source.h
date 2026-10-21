#ifndef BIWN_DECK_TASK_SOURCE_H
#define BIWN_DECK_TASK_SOURCE_H
#include "../deck-scene-source/deck-scene-contract.h"
/* Structured recovery of the outer 11E6C..11F6C task. Services remain explicit.
 * 0: at outer RTS 11F6A; 6: committed continuation at an iteration boundary,
 * a dependency's DF60/DF8C suspension, or a bounded display wait at 11F50.
 * The caller supplies the scheduler/disc/GPU services; no time advances here.
 * Accepted PCs are entry, iteration, and source JSR-return continuations.
 * Host errors 1..5 leave CPU unchanged but retain prior RAM side effects.
 * A suspended dependency must be resumed by its owner through its RTS;
 * only then may this task resume at the original JSR return address. */
int biwn_deck_task_resume(struct biwn_world_bus *,struct biwn_task_cpu *,
 biwn_world_cpu_service,void *,uint32_t helper_budget,uint32_t poll_budget);
int biwn_deck_task_call(struct biwn_world_bus *,struct biwn_task_cpu *,
 biwn_world_cpu_service,void *,uint32_t helper_budget,uint32_t poll_budget);
#endif
