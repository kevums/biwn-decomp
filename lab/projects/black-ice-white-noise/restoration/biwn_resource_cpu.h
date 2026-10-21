#ifndef BIWN_RESOURCE_CPU_H
#define BIWN_RESOURCE_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_resource_cpu_status {BIWN_RESOURCE_CPU_OK=0,BIWN_RESOURCE_CPU_BAD_ARGUMENT=1,
 BIWN_RESOURCE_CPU_BUS_ERROR=2,BIWN_RESOURCE_CPU_SERVICE_ERROR=3,
 BIWN_RESOURCE_CPU_WORK_LIMIT=4,BIWN_RESOURCE_CPU_BAD_RETURN=5,
 BIWN_RESOURCE_CPU_YIELDED=6,BIWN_RESOURCE_CPU_BAD_PC=7};
/* Static fullCPU bodies for1B002release,1AF04acquire,1545Cfree,152A2allocate,
 * 15200compact,1B044load andE3E0/E3EEcopy. A helper provider executes nested
 * bodies up toRTS; callers retain all source argument/save frames. body
 * stops atRTS, call executesRTS. InternalPC resume is supported. DF60 yield
 * and DF8C wait return status6 before their wrappers execute, preserving
 * nested frames for actual scheduler yield/wait and later continuation.
 * commits CPU/frames; otherhosterrors retain RAM and unchanged inputCPU.
 * No runtime instructiondecode or originalCPU/GPUcalls. Devices/services
 * are explicit providers; this alone does not prove disk/model lifetimes. */
enum biwn_resource_cpu_status biwn_resource_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_resource_cpu_status biwn_resource_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
