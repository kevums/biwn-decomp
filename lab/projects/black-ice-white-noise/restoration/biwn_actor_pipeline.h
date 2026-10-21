#ifndef BIWN_ACTOR_PIPELINE_H
#define BIWN_ACTOR_PIPELINE_H
#include "biwn_actor_task.h"
typedef void (*biwn_actor_pipeline_observer)(void *,uint32_t,const struct biwn_task_cpu *);
enum biwn_actor_pipeline_status {BIWN_ACTOR_PIPELINE_OK=0,
 BIWN_ACTOR_PIPELINE_BAD_ARGUMENT=1,BIWN_ACTOR_PIPELINE_COMPONENT_ERROR=2,
 BIWN_ACTOR_PIPELINE_UNSUPPORTED_PC=3};
/* One user-mode continuation step: DF60 scheduler yield; F4D8/F56E/F70C
 * actor body to pendingDF60orDF7A; DF7A scheduler removal. Real RNG,
 * navigation, movement, collision, direction and GPU-submit C are linked.
 * Observer sees helper entry states and must not mutate bus/CPU/RAM.
 * A selected continuation can belong to another actor family; caller must
 * dispatch it rather than assuming this API supports arbitrary PCs.
 * Each helper gets budget; no global cycle/time bound or device/scheduler
 * concurrency proof. Host errors retain earlier RAM effects and leave CPU
 * unchanged. GPU/device execution and clock/interrupt evolution external. */
enum biwn_actor_pipeline_status biwn_actor_pipeline_step(struct biwn_world_bus *,
 struct biwn_task_cpu *,biwn_actor_task_write8,uint32_t,
 biwn_actor_pipeline_observer,void *);
#endif
