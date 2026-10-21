#ifndef BIWN_WORLD_CPU_H
#define BIWN_WORLD_CPU_H
#include "biwn_scheduler.h"
typedef int (*biwn_world_cpu_service)(void *,struct biwn_world_bus *,struct biwn_task_cpu *,uint32_t);
enum biwn_world_cpu_status {BIWN_WORLD_CPU_OK=0,BIWN_WORLD_CPU_BAD_ARGUMENT=1,
 BIWN_WORLD_CPU_BUS_ERROR=2,BIWN_WORLD_CPU_SERVICE_ERROR=3,BIWN_WORLD_CPU_WORK_LIMIT=4,
 BIWN_WORLD_CPU_BAD_RETURN=5,BIWN_WORLD_CPU_SUSPENDED=6};
/* Complete caller [1A188,1A544) with real private local/save/argument frames.
 * Callbacks start at the original helper entry with its JSR return on stack;
 * they execute the body up to RTS, retaining caller-saved CPU/flags effects.
 * Digit helper1B718 is implemented locally with its original partial D0.
 * body stops at1A542; call also performs RTS. An input191F4 service may
 * return SUSPENDED with CPU atDF60 and its source-owned frames intact;
 * caller commits that state without executing a helper RTS. After actual
 * scheduler/input resumption and input RTS, PC1A26C resumes this caller.
 * Poll budget is host behavior.
 * Host errors leave CPU unchanged while retaining prior RAM/helper effects.
 * This interface alone does not reconstruct the external helper bodies. */
enum biwn_world_cpu_status biwn_world_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_world_cpu_service,void *,uint32_t);
enum biwn_world_cpu_status biwn_world_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_world_cpu_service,void *,uint32_t);
#endif
