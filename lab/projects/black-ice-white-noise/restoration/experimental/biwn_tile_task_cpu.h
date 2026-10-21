#ifndef BIWN_TILE_TASK_CPU_H
#define BIWN_TILE_TASK_CPU_H
#include "biwn_world_cpu.h"
/* Experimental source21D1A task/212E8 tile12 bypass.13fixed instruction
 * cases; mode!=1 or tile12 only. Other tilebranches return7, not no-op.
 * Localmodel casefragment with coordinator flag/stack/bus scaffolding.
 * Native384fixtures+5hosterrorchecks+source-derived live prefix verified.
 * Source task ends beforeDF60 with actual JSRframe, status6. Budget4,
 * bus2, badargument1, unported7; callerCPU unchanged onerror, prior RAM
 * stores retained. No runtime decoder/originalCPU, ordinaryboot or full
 * task/game/globaltiming proof. A7=slot15, D7=slot7. */
int biwn_tile_task_cpu_run(struct biwn_world_bus*,struct biwn_task_cpu*,uint32_t);
#endif
