#ifndef BIWN_RNG_CPU_H
#define BIWN_RNG_CPU_H
#include "biwn_scheduler.h"
enum biwn_rng_cpu_status {BIWN_RNG_CPU_OK=0,BIWN_RNG_CPU_BAD_ARGUMENT=1,
 BIWN_RNG_CPU_BUS_ERROR=2,BIWN_RNG_CPU_ZERO_DIVISOR=3,BIWN_RNG_CPU_BAD_RETURN=4};
/* Full CPU/stack interface for already counted routines1A77C/E60A/E588/E540.
 * Body stops at final RTS; call also executes RTS. Indexed RNG calls its real
 * remainder/division/multiply bodies, retaining private frames and data access
 * widths/order. Raw signed-word selectors and mutable Q/R reads are preserved.
 * User mode, no interrupts/tracing/cycle timing. Zero division is a host error,
 * not the original exception. Errors retain RAM effects, leave CPU unchanged. */
enum biwn_rng_cpu_status biwn_rng_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *);
enum biwn_rng_cpu_status biwn_rng_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *);
#endif
