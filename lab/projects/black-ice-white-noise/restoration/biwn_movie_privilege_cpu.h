#ifndef BIWN_MOVIE_PRIVILEGE_CPU_H
#define BIWN_MOVIE_PRIVILEGE_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_movie_privilege_cpu_status {BIWN_MOVIE_PRIVILEGE_CPU_OK=0,BIWN_MOVIE_PRIVILEGE_CPU_BAD_ARGUMENT=1,
 BIWN_MOVIE_PRIVILEGE_CPU_BUS_ERROR=2,BIWN_MOVIE_PRIVILEGE_CPU_SERVICE_ERROR=3,
 BIWN_MOVIE_PRIVILEGE_CPU_WORK_LIMIT=4,BIWN_MOVIE_PRIVILEGE_CPU_BAD_RETURN=5,
 BIWN_MOVIE_PRIVILEGE_CPU_YIELDED=6,BIWN_MOVIE_PRIVILEGE_CPU_BAD_PC=7,BIWN_MOVIE_PRIVILEGE_CPU_PRIVILEGE_UNIMPLEMENTED=9};
/* Source DDfe privilege STOP, de02 saved-PC+2, de06 RTE and observed
 * 22A10 operand execution (2000=move.lD0,D0) before normal22A12.
 * Four static source instructions. User STOP exception and nested GPU IRQ
 * use separate real sixbyte frames. No original CPU/runtime decoder.
 * Source STOP yields6 before execution; event API applies its architectural
 * state. RTE commits/restores both stackbanks. Handler/noop handoffs return0.
 * No other privilege instruction, trace, scheduler or physicaltiming proof. */
enum biwn_movie_privilege_cpu_status biwn_movie_privilege_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_movie_privilege_cpu_status biwn_movie_privilege_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
int biwn_movie_user_STOP_exception(struct biwn_world_bus *,struct biwn_task_cpu *);
int biwn_movie_privilege_STOP_event(struct biwn_task_cpu *);
int biwn_movie_wait_GPU_interrupt(struct biwn_world_bus *,struct biwn_task_cpu *);
int biwn_movie_user_VBI_event(struct biwn_world_bus *,struct biwn_task_cpu *);
#endif
