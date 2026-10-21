#ifndef BIWN_ACTOR_MOVEMENT_H
#define BIWN_ACTOR_MOVEMENT_H
#include "biwn_actor_task.h"
enum biwn_actor_movement_status {BIWN_ACTOR_MOVEMENT_OK=0,
 BIWN_ACTOR_MOVEMENT_BAD_ARGUMENT=1,BIWN_ACTOR_MOVEMENT_BUS_ERROR=2,
 BIWN_ACTOR_MOVEMENT_SERVICE_ERROR=3,BIWN_ACTOR_MOVEMENT_BAD_RETURN=4};
/* Original13C9A..13F12 caller. Direction13440, GPU submitE220 and collision
 * helpers13B5A/13BB0 are explicit full-CPU service boundaries. Services stop
 * before RTS and keep A7 pointing to the original return address.
 * Body stops at13F10 RTS; call also performs the return. Full register/SR,
 * private frames, wrapped fractions and selective position rollback retained.
 * User mode only; no interrupts/tracing/cycle timing. Host errors retain prior
 * RAM effects and leave caller CPU unchanged. Not complete movement/physics. */
enum biwn_actor_movement_status biwn_actor_movement_body(struct biwn_world_bus *,
 struct biwn_task_cpu *,biwn_actor_task_service,void *);
enum biwn_actor_movement_status biwn_actor_movement_call(struct biwn_world_bus *,
 struct biwn_task_cpu *,biwn_actor_task_service,void *);
#endif
