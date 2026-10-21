#ifndef BIWN_TRANSITION_CPU_H
#define BIWN_TRANSITION_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_transition_cpu_status {BIWN_TRANSITION_CPU_OK=0,BIWN_TRANSITION_CPU_BAD_ARGUMENT=1,
 BIWN_TRANSITION_CPU_BUS_ERROR=2,BIWN_TRANSITION_CPU_SERVICE_ERROR=3,
 BIWN_TRANSITION_CPU_WORK_LIMIT=4,BIWN_TRANSITION_CPU_BAD_RETURN=5,
 BIWN_TRANSITION_CPU_YIELDED=6,BIWN_TRANSITION_CPU_BAD_PC=7};
/* Fixed boundary 19F2C/19FDA/1A0F8 and cleanup 1AE56/20CC4/20E40/
 * 20E8C/20F0C. Full registers/SR/both stack banks/private argument frames.
 * Helper providers execute up to RTS. Source DF60 yield may propagate
 * complete CPU/private frames for scheduling and continuation. body stops
 * before RTS; call consumes RTS. No runtime decoding or original core calls.
 * Finite valid source lists required; host failures preserve input CPU and
 * prior RAM effects. Generation alone proves no connected transition. */
enum biwn_transition_cpu_status biwn_transition_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_transition_cpu_status biwn_transition_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
