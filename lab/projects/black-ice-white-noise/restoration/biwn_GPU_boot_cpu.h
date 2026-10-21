#ifndef BIWN_GPU_BOOT_CPU_H
#define BIWN_GPU_BOOT_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_GPU_boot_cpu_status {BIWN_GPU_BOOT_CPU_OK=0,BIWN_GPU_BOOT_CPU_BAD_ARGUMENT=1,
 BIWN_GPU_BOOT_CPU_BUS_ERROR=2,BIWN_GPU_BOOT_CPU_SERVICE_ERROR=3,
 BIWN_GPU_BOOT_CPU_WORK_LIMIT=4,BIWN_GPU_BOOT_CPU_BAD_RETURN=5,
 BIWN_GPU_BOOT_CPU_YIELDED=6,BIWN_GPU_BOOT_CPU_BAD_PC=7};
/* SourceE00A159word mainGPU image copy, BIOS3000(A0F03050),
 * PCF03224/GO1. FullCPU/stackbanks/sourceJSRframe. body leaves RTS,
 * call consumes RTS. BIOS3000 is a required explicit provider; no actual
 * firmware/wholeCPUboot/physicalGPU/game proof. No runtime instruction
 * decoder or original CPU execution. GPUprograms require a source provider.
 */
enum biwn_GPU_boot_cpu_status biwn_GPU_boot_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_GPU_boot_cpu_status biwn_GPU_boot_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
