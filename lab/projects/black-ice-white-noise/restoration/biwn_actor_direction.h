#ifndef BIWN_ACTOR_DIRECTION_H
#define BIWN_ACTOR_DIRECTION_H
#include "biwn_rng_cpu.h"
/* Original13440..134DC, including full CPU/private frames and realE588.
 * Body stops at134DA RTS, call performs RTS. Signed word arguments remain
 * raw, including8000; zeroZ retains incoming D0 upper16bits. Read the original
 * direction thresholds from bus memory. Errors retain RAM effects/CPU input.
 * Same user-mode/exception/timing scope as the full CPU math interface. */
enum biwn_rng_cpu_status biwn_actor_direction_body(struct biwn_world_bus *,struct biwn_task_cpu *);
enum biwn_rng_cpu_status biwn_actor_direction_call(struct biwn_world_bus *,struct biwn_task_cpu *);
#endif
