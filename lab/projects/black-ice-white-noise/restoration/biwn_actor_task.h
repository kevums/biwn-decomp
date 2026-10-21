#ifndef BIWN_ACTOR_TASK_H
#define BIWN_ACTOR_TASK_H
#include "biwn_scheduler.h"
typedef int (*biwn_actor_task_write8)(void *,uint32_t,uint8_t);
typedef int (*biwn_actor_task_service)(void *,struct biwn_world_bus *,struct biwn_task_cpu *,uint32_t);
enum biwn_actor_task_status {BIWN_ACTOR_TASK_OK=0,BIWN_ACTOR_TASK_BAD_ARGUMENT=1,
 BIWN_ACTOR_TASK_BUS_ERROR=2,BIWN_ACTOR_TASK_SERVICE_ERROR=3,BIWN_ACTOR_TASK_WORK_LIMIT=4,
 BIWN_ACTOR_TASK_BAD_RETURN=5,BIWN_ACTOR_TASK_EXIT_BOUNDARY=6};
/* F4D8 caller control flow. Resume at F4D8,F56E orF70C. Runs to a pending
 * DF60 yield orDF7A removal boundary; does not perform scheduler/removal here.
 * Services receive original stack arguments andincoming D0; they supply the
 * callee's caller-saved CPU/SR behavior. DFA6 getter is implemented locally.
 * Normal/exit boundaries commitCPU. Host errors retain RAM effects andleave
 * callerCPU unchanged. Retry budget bounds collision-probe retry cycles.
 * This is not implementation of steering/movement/service bodies. */
enum biwn_actor_task_status biwn_actor_task_run(struct biwn_world_bus *,
 struct biwn_task_cpu *,biwn_actor_task_write8,biwn_actor_task_service,void *,uint32_t);
#endif
