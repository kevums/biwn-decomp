#ifndef BIWN_CAMERA_CPU_H
#define BIWN_CAMERA_CPU_H
#include "biwn_world_cpu.h"
typedef int (*biwn_camera_cpu_write8)(void *,uint32_t,uint8_t);
/* Full F0FA user-task caller, including its seven-register save frame and
 * four live direction-argument bytes reused in the E220 parameter frame.
 * Helpers E540,13440,E220 execute body interfaces up to RTS. Full call also
 * executes F35C RTS; body stops there. Host errors retain prior RAM effects
 * and unchanged callerCPU. Helpers/device behavior are explicit providers. */
enum biwn_world_cpu_status biwn_camera_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_camera_cpu_write8,biwn_world_cpu_service,void *);
enum biwn_world_cpu_status biwn_camera_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_camera_cpu_write8,biwn_world_cpu_service,void *);
#endif
