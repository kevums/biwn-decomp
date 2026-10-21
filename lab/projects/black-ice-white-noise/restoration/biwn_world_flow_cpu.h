#ifndef BIWN_WORLD_FLOW_CPU_H
#define BIWN_WORLD_FLOW_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_world_flow_cpu_status {BIWN_WORLD_FLOW_CPU_OK=0,BIWN_WORLD_FLOW_CPU_BAD_ARGUMENT=1,
 BIWN_WORLD_FLOW_CPU_BUS_ERROR=2,BIWN_WORLD_FLOW_CPU_SERVICE_ERROR=3,
 BIWN_WORLD_FLOW_CPU_WORK_LIMIT=4,BIWN_WORLD_FLOW_CPU_BAD_RETURN=5,
 BIWN_WORLD_FLOW_CPU_YIELDED=6,BIWN_WORLD_FLOW_CPU_BAD_PC=7};
/* Fixed source world1A188/taskloop1A544/digit1B718 blocks. Full CPU,
 * both stack banks and source private frames. Arbitrary decoded continuation
 * supported after nested source input/boundary/loading yields at DF60. Nested
 * providers execute up to RTS; body stops before RTS, call consumes it. No
 * runtime instruction decoding or original CPU-core calls. Generation alone
 * proves no input, scheduler, loading, drawing or full-game integration. */
enum biwn_world_flow_cpu_status biwn_world_flow_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_world_flow_cpu_status biwn_world_flow_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
