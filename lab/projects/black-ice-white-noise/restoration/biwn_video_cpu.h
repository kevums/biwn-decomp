#ifndef BIWN_VIDEO_CPU_H
#define BIWN_VIDEO_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_video_cpu_status {BIWN_VIDEO_CPU_OK=0,BIWN_VIDEO_CPU_BAD_ARGUMENT=1,
 BIWN_VIDEO_CPU_BUS_ERROR=2,BIWN_VIDEO_CPU_SERVICE_ERROR=3,
 BIWN_VIDEO_CPU_WORK_LIMIT=4,BIWN_VIDEO_CPU_BAD_RETURN=5,
 BIWN_VIDEO_CPU_YIELDED=6,BIWN_VIDEO_CPU_BAD_PC=7,BIWN_VIDEO_CPU_STOP_UNIMPLEMENTED=8,BIWN_VIDEO_CPU_PRIVILEGE_UNIMPLEMENTED=9};
/* Source D340 GPU relocation copy/start/copyback, E7AA IRQ setup,
 * E7D4 IRQ handler/RTE and22780/227A0/228D4/229F4 video interfaces.
 * Full CPU/private LINK/MOVEM/args/both stack banks. body stops before
 * RTS; call consumes it. RTE consumes its real six-byte source frame.
 * STOP22A0E suspends before execution with status6 when requested;
 * separate stop/GPU interrupt event APIs perform the architectural event.
 * Other host errors preserve input CPU with prior bus writes retained.
 * Privilege violations return9, not a fabricated source exception. No
 * runtime instruction decoder or original CPU instructions. GPU/device,
 * BIOS progress and timing remain explicit providers. */
enum biwn_video_cpu_status biwn_video_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_video_cpu_status biwn_video_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_video_cpu_status biwn_video_cpu_stop(struct biwn_task_cpu *);
enum biwn_video_cpu_status biwn_video_cpu_GPU_interrupt(struct biwn_world_bus *,struct biwn_task_cpu *);
#endif
