#ifndef BIWN_INPUT_DISPATCH_CPU_H
#define BIWN_INPUT_DISPATCH_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_dispatch_cpu_status {BIWN_DISPATCH_CPU_OK=0,BIWN_DISPATCH_CPU_BAD_ARGUMENT=1,
 BIWN_DISPATCH_CPU_BUS_ERROR=2,BIWN_DISPATCH_CPU_SERVICE_ERROR=3,
 BIWN_DISPATCH_CPU_WORK_LIMIT=4,BIWN_DISPATCH_CPU_BAD_RETURN=5,
 BIWN_DISPATCH_CPU_YIELDED=6,BIWN_DISPATCH_CPU_BAD_PC=7};
/* Static C blocks for all816checked instructions; no runtime instruction
 * decoding or CPU-core calls. Exact CPU state permits internal continuation.
 * body stops before19F2A RTS; call executes it. stop_on_yield leaves DF60
 * and its real return/private frames for the scheduler, committing CPU.
 * A nested provider may also suspend at DF60: status6 propagates the
 * provider's complete CPU/private frames without popping the input JSR.
 * Other host errors preserve inputCPU and priorRAM effects. Usermode only.
 * Services execute helper bodies up to RTS; their behavior remains explicit. */
enum biwn_dispatch_cpu_status biwn_input_dispatch_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_dispatch_cpu_status biwn_input_dispatch_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
