#ifndef BIWN_ACTOR5_TASK_CPU_H
#define BIWN_ACTOR5_TASK_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_actor5_task_cpu_status {BIWN_ACTOR5_TASK_CPU_OK=0,BIWN_ACTOR5_TASK_CPU_BAD_ARGUMENT=1,
 BIWN_ACTOR5_TASK_CPU_BUS_ERROR=2,BIWN_ACTOR5_TASK_CPU_SERVICE_ERROR=3,
 BIWN_ACTOR5_TASK_CPU_WORK_LIMIT=4,BIWN_ACTOR5_TASK_CPU_BAD_RETURN=5,
 BIWN_ACTOR5_TASK_CPU_YIELDED=6,BIWN_ACTOR5_TASK_CPU_BAD_PC=7};
/* Source type5 actor scan, respawn, follow, approach, dialogue/distance task.
 * Table13116..13122 stays data; reads runtime bus words and signs JMP offset.
 * Source privateframes, both stack banks and nestedDF8C waits retained.
 * Helpers remain explicit; generation is not validation or fullgame proof. */
enum biwn_actor5_task_cpu_status biwn_actor5_task_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_actor5_task_cpu_status biwn_actor5_task_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
