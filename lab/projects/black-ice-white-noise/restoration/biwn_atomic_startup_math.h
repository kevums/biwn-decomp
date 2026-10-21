#ifndef BIWN_ATOMIC_STARTUP_MATH_H
#define BIWN_ATOMIC_STARTUP_MATH_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_atomic_startup_math_status {BIWN_ATOMIC_STARTUP_MATH_OK=0,BIWN_ATOMIC_STARTUP_MATH_BAD_ARGUMENT=1,
 BIWN_ATOMIC_STARTUP_MATH_BUS_ERROR=2,BIWN_ATOMIC_STARTUP_MATH_SERVICE_ERROR=3,
 BIWN_ATOMIC_STARTUP_MATH_WORK_LIMIT=4,BIWN_ATOMIC_STARTUP_MATH_BAD_RETURN=5,
 BIWN_ATOMIC_STARTUP_MATH_YIELDED=6,BIWN_ATOMIC_STARTUP_MATH_BAD_PC=7,BIWN_ATOMIC_STARTUP_MATH_DIVISION_BY_ZERO=9};
/* Static C blocks for all816checked instructions; no runtime instruction
 * decoding or CPU-core calls. Exact CPU state permits internal continuation.
 * body stops before19F2A RTS; call executes it. stop_on_yield leaves DF60
 * and its real return/private frames for the scheduler, committing CPU.
 * A nested provider may also suspend at DF60: status6 propagates the
 * provider's complete CPU/private frames without popping the input JSR.
 * Other host errors preserve inputCPU and priorRAM effects. Usermode only.
 * Services execute helper bodies up to RTS; their behavior remains explicit. */
enum biwn_atomic_startup_math_status biwn_atomic_startup_math_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_atomic_startup_math_status biwn_atomic_startup_math_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
