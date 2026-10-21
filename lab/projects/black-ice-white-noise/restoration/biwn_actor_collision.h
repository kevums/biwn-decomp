#ifndef BIWN_ACTOR_COLLISION_H
#define BIWN_ACTOR_COLLISION_H
#include "biwn_geometry_cpu.h"
enum biwn_actor_collision_status {BIWN_ACTOR_COLLISION_OK=0,
 BIWN_ACTOR_COLLISION_BAD_ARGUMENT=1,BIWN_ACTOR_COLLISION_SCAN_LIMIT=2,
 BIWN_ACTOR_COLLISION_BUS_ERROR=3,BIWN_ACTOR_COLLISION_BAD_RETURN=4};
/* Original13B5A/13BB0, with real1028E/102C4/1039C/10652 fullCPU geometry.
 * Body stops before RTS; call performs RTS. Finite scan budget bounds each
 * indoor lookup and nested geometry scan. Raw signed fields/partial D0, source
 * rereads, room rollback and mode changes retained. No opaque service calls.
 * User mode only, no exceptions/interrupts/tracing/timing or arbitrary code
 * aliases. Host errors retain prior RAM effects and unchanged caller CPU. */
enum biwn_actor_collision_status biwn_actor_collision_body(struct biwn_world_bus *,struct biwn_task_cpu *,uint32_t);
enum biwn_actor_collision_status biwn_actor_collision_call(struct biwn_world_bus *,struct biwn_task_cpu *,uint32_t);
#endif
