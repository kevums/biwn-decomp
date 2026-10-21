#ifndef BIWN_HEALTH_TIMEOUT_CPU_H
#define BIWN_HEALTH_TIMEOUT_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_health_timeout_cpu_status {BIWN_HEALTH_TIMEOUT_CPU_OK=0,BIWN_HEALTH_TIMEOUT_CPU_BAD_ARGUMENT=1,
 BIWN_HEALTH_TIMEOUT_CPU_BUS_ERROR=2,BIWN_HEALTH_TIMEOUT_CPU_SERVICE_ERROR=3,
 BIWN_HEALTH_TIMEOUT_CPU_WORK_LIMIT=4,BIWN_HEALTH_TIMEOUT_CPU_BAD_RETURN=5,
 BIWN_HEALTH_TIMEOUT_CPU_SWITCHED=6,BIWN_HEALTH_TIMEOUT_CPU_BAD_PC=7,BIWN_HEALTH_TIMEOUT_CPU_BAD_VECTOR=8};
/* Source18B86 health task, DF7C sleep wrapper andDEE2 deadline handler.
 * SWITCHED6 commits either DF7C/DF7A source-call boundary/privateframe,
 * or the context selected by supplied DE08 dispatch/RTE provider.
 * SourceTRAP3 saves exact SR/PC onSSP and deadline uses raw clock+duration.
 * Body/call retain source MOVEM and nested arguments. No runtime decoding
 * or originalCPUcalls. Generation alone proves no scheduling/boot/game. */
enum biwn_health_timeout_cpu_status biwn_health_timeout_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_health_timeout_cpu_status biwn_health_timeout_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
