#ifndef BIWN_GPU4720_SUBMIT_CPU_H
#define BIWN_GPU4720_SUBMIT_CPU_H
#include "biwn_scheduler.h"
enum biwn_gpu4720_submit_cpu_status {BIWN_GPU4720_SUBMIT_CPU_OK=0,
 BIWN_GPU4720_SUBMIT_CPU_BAD_ARGUMENT=1,BIWN_GPU4720_SUBMIT_CPU_BUS_ERROR=2,
 BIWN_GPU4720_SUBMIT_CPU_READ_LIMIT=3,BIWN_GPU4720_SUBMIT_CPU_BAD_RETURN=4};
/* Full CPU/private-stack interface for E26C/E098 command4720 protocol (four longs plus actual fifthlong read)..
 * GPU execution is performed by the bus device, not this CPU caller.
 * Body stops atE2B6 RTS; call performs RTS. Read budget counts mailbox polls.
 * User/supervisor active stack banks, no interrupts/tracing/timing. Errors retain RAM/device effects
 * and leave caller CPU unchanged. Dispatcher concurrency is not reconstructed. */
enum biwn_gpu4720_submit_cpu_status biwn_gpu4720_submit_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,uint32_t);
enum biwn_gpu4720_submit_cpu_status biwn_gpu4720_submit_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,uint32_t);
#endif
