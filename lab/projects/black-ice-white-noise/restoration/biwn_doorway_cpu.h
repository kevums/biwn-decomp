#ifndef BIWN_DOORWAY_CPU_H
#define BIWN_DOORWAY_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_doorway_cpu_status {BIWN_DOORWAY_CPU_OK=0,BIWN_DOORWAY_CPU_BAD_ARGUMENT=1,
 BIWN_DOORWAY_CPU_BUS_ERROR=2,BIWN_DOORWAY_CPU_SERVICE_ERROR=3,
 BIWN_DOORWAY_CPU_WORK_LIMIT=4,BIWN_DOORWAY_CPU_BAD_RETURN=5,
 BIWN_DOORWAY_CPU_YIELDED=6,BIWN_DOORWAY_CPU_BAD_PC=7};
/* Source-specific static 10430 entrance selection, full registers/SR,
 * both stack banks, MOVEM frames and object writes. body stops before RTS;
 * call consumes RTS. No helper calls, runtime CPU decoding or core execution.
 * Caller supplies valid mapped records and pointers. A successful entrance
 * check alone does not load a scene or prove doorway reachability/gameplay.
 * Host errors preserve input CPU and retain earlier RAM stores. */
enum biwn_doorway_cpu_status biwn_doorway_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_doorway_cpu_status biwn_doorway_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
