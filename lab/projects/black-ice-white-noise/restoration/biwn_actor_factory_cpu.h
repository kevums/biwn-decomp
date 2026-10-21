#ifndef BIWN_ACTOR_FACTORY_CPU_H
#define BIWN_ACTOR_FACTORY_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_actor_factory_cpu_status {BIWN_ACTOR_FACTORY_CPU_OK=0,BIWN_ACTOR_FACTORY_CPU_BAD_ARGUMENT=1,
 BIWN_ACTOR_FACTORY_CPU_BUS_ERROR=2,BIWN_ACTOR_FACTORY_CPU_SERVICE_ERROR=3,
 BIWN_ACTOR_FACTORY_CPU_WORK_LIMIT=4,BIWN_ACTOR_FACTORY_CPU_BAD_RETURN=5,
 BIWN_ACTOR_FACTORY_CPU_YIELDED=6,BIWN_ACTOR_FACTORY_CPU_BAD_PC=7};
/* Source-specific actor dispatcher13AE0, actor134DC/table targets13706,
 * taskcreateDE5C/DF6C. Full CPU/private MOVEM/args/JMP/RTS frames; both banks.
 * 13620..13706 table is data, not executable blocks. Static-object137E0 is a
 * provider; empty task pool reaches unsupported DEB4 rather than emulating
 * ILLEGAL. No runtime decoding/core calls. body stops before RTS; call
 * consumes it. Caller supplies valid source records/list indices. Generation
 * alone proves no actor creation, scheduler context reuse or game completion. */
enum biwn_actor_factory_cpu_status biwn_actor_factory_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_actor_factory_cpu_status biwn_actor_factory_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
