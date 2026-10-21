#ifndef BIWN_GPU_PROJECTION_SUBMIT_CPU_H
#define BIWN_GPU_PROJECTION_SUBMIT_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_gpu_projection_submit_cpu_status {BIWN_GPU_PROJECTION_SUBMIT_CPU_OK=0,BIWN_GPU_PROJECTION_SUBMIT_CPU_BAD_ARGUMENT=1,
 BIWN_GPU_PROJECTION_SUBMIT_CPU_BUS_ERROR=2,BIWN_GPU_PROJECTION_SUBMIT_CPU_SERVICE_ERROR=3,
 BIWN_GPU_PROJECTION_SUBMIT_CPU_WORK_LIMIT=4,BIWN_GPU_PROJECTION_SUBMIT_CPU_BAD_RETURN=5,
 BIWN_GPU_PROJECTION_SUBMIT_CPU_YIELDED=6,BIWN_GPU_PROJECTION_SUBMIT_CPU_BAD_PC=7};
/* FullCPU14sourceinstructions E19Esubmission. Bothstackbanks. E098wait andGPU52E0behavior are explicit providers; body stops beforeRTS/call consumesit. No runtimeCPUdecode or originalCPUcalls. */
enum biwn_gpu_projection_submit_cpu_status biwn_gpu_projection_submit_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_gpu_projection_submit_cpu_status biwn_gpu_projection_submit_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
