#ifndef BIWN_SYSTEM_CPU_H
#define BIWN_SYSTEM_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_system_cpu_status {BIWN_SYSTEM_CPU_OK=0,BIWN_SYSTEM_CPU_BAD_ARGUMENT=1,
 BIWN_SYSTEM_CPU_BUS_ERROR=2,BIWN_SYSTEM_CPU_SERVICE_ERROR=3,
 BIWN_SYSTEM_CPU_WORK_LIMIT=4,BIWN_SYSTEM_CPU_BAD_RETURN=5,
 BIWN_SYSTEM_CPU_SWITCHED=6,BIWN_SYSTEM_CPU_BAD_PC=7,BIWN_SYSTEM_CPU_BAD_VECTOR=8};
/* Source DD40 pool/system-context/vector setup, DDCC/DDF2 render
 * creation and DDD2 clock loop/TRAP0. DDEE..DDF2 is data, not CPU blocks.
 * Source USP/SR bank transition and exact TRAP exception frame retained.
 * DE5C task creation and DE08 dispatch/RTE are explicit body providers.
 * SWITCHED6 commits selected context; WORK_LIMIT4 commits completed fixed
 * instructions, allowing host stepping at source clock observations.
 * Other errors preserve input CPU and earlier RAM effects. No runtime
 * decoding/original CPU calls. Generation proves no whole boot or game. */
enum biwn_system_cpu_status biwn_system_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_system_cpu_status biwn_system_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
