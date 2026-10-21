#ifndef BIWN_INTERIOR_LOADING_CPU_H
#define BIWN_INTERIOR_LOADING_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_interior_loading_cpu_status {BIWN_INTERIOR_LOADING_CPU_OK=0,BIWN_INTERIOR_LOADING_CPU_BAD_ARGUMENT=1,
 BIWN_INTERIOR_LOADING_CPU_BUS_ERROR=2,BIWN_INTERIOR_LOADING_CPU_SERVICE_ERROR=3,
 BIWN_INTERIOR_LOADING_CPU_WORK_LIMIT=4,BIWN_INTERIOR_LOADING_CPU_BAD_RETURN=5,
 BIWN_INTERIOR_LOADING_CPU_YIELDED=6,BIWN_INTERIOR_LOADING_CPU_BAD_PC=7,BIWN_INTERIOR_LOADING_CPU_DIVISION_BY_ZERO=8,BIWN_INTERIOR_LOADING_CPU_DIVISION_OVERFLOW=9};
/* FullCPU/source private frames for six scene loader/parser bodies,
 * 1AA40texture setup,1AC3Clookup,1AC68acquire and10520/105DAindoor position.
 * Bothstackbanks; fixed build-time decoded blocks, no runtimeCPUdecode or
 * originalCPU/GPUexecution. Nestedbody providers execute up to theirRTS;
 * outercall consumesRTS. Existing sourceDF60yield propagation retained.
 * Finite valid buffers are caller requirements. DIVS normal signed16bit
 * quotient domain; host statuses8/9 for zero/overflow leave callerCPU
 * unchanged with priorRAMeffects retained, not sourceexception/trap or
 * undefinedflag emulation. Disc/BIOS/scheduler/actor helpers are providers.
 * This group alone proves no fullscene loading, boot or playablegame. */
enum biwn_interior_loading_cpu_status biwn_interior_loading_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_interior_loading_cpu_status biwn_interior_loading_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
