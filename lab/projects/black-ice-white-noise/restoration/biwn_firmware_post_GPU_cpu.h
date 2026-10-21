#ifndef BIWN_FIRMWARE_POST_GPU_CPU_H
#define BIWN_FIRMWARE_POST_GPU_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_firmware_post_GPU_cpu_status {BIWN_FIRMWARE_POST_GPU_CPU_OK=0,BIWN_FIRMWARE_POST_GPU_CPU_BAD_ARGUMENT=1,
 BIWN_FIRMWARE_POST_GPU_CPU_BUS_ERROR=2,BIWN_FIRMWARE_POST_GPU_CPU_SERVICE_ERROR=3,
 BIWN_FIRMWARE_POST_GPU_CPU_WORK_LIMIT=4,BIWN_FIRMWARE_POST_GPU_CPU_BAD_RETURN=5,
 BIWN_FIRMWARE_POST_GPU_CPU_YIELDED=6,BIWN_FIRMWARE_POST_GPU_CPU_BAD_PC=7,BIWN_FIRMWARE_POST_GPU_CPU_READY=8};
/* Observed 5028A..502AA GPU GO check, source 228-byte RAM copy to1000,
 * natural JMP1000, then 1000..1014 source video-counter delta-five wait.
 * Exact live instruction words guarded. READY8 stops before1014; work
 * limit4 commits CPU continuation. Service observes each instruction;
 * shared MMIO and external source video events remain providers.
 * No originalCPU execution/runtime instruction decoder. Other main
 * firmware, discboot, global timing and fullgame remain unverified. */
enum biwn_firmware_post_GPU_cpu_status biwn_firmware_post_GPU_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_firmware_post_GPU_cpu_status biwn_firmware_post_GPU_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
