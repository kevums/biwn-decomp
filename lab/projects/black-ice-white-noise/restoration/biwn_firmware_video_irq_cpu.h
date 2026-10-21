#ifndef BIWN_FIRMWARE_VIDEO_IRQ_CPU_H
#define BIWN_FIRMWARE_VIDEO_IRQ_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_firmware_video_irq_cpu_status {BIWN_FIRMWARE_VIDEO_IRQ_CPU_OK=0,BIWN_FIRMWARE_VIDEO_IRQ_CPU_BAD_ARGUMENT=1,
 BIWN_FIRMWARE_VIDEO_IRQ_CPU_BUS_ERROR=2,BIWN_FIRMWARE_VIDEO_IRQ_CPU_SERVICE_ERROR=3,
 BIWN_FIRMWARE_VIDEO_IRQ_CPU_WORK_LIMIT=4,BIWN_FIRMWARE_VIDEO_IRQ_CPU_BAD_RETURN=5,
 BIWN_FIRMWARE_VIDEO_IRQ_CPU_YIELDED=6,BIWN_FIRMWARE_VIDEO_IRQ_CPU_BAD_PC=7,BIWN_FIRMWARE_VIDEO_IRQ_CPU_RETURNED=8};
/* Observed firmware video handler194C90 and327 reached CPU instructions,
 * including graphics helpers and source-patched RTS196446. No runtime
 * decoder/originalCPU; internal source BSR/JSR/RTS stay in one fixed body.
 * RETURNED8 consumes real six-byte RTE frame and stops at interruptedPC.
 * Service observes sourcePC before each instruction. Initial live firmware
 * RAM/CPU/GPU/peripheral state and explicit VBI event are dependencies.
 * Reached path only; other graphics inputs/events/helper branches, GPU
 * execution, global timing/disc loading/fullboot/playability separate. */
enum biwn_firmware_video_irq_cpu_status biwn_firmware_video_irq_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_firmware_video_irq_cpu_status biwn_firmware_video_irq_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
