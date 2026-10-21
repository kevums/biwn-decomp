#ifndef BIWN_RENDER_QUEUE_CPU_H
#define BIWN_RENDER_QUEUE_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_render_queue_cpu_status {BIWN_RENDER_QUEUE_CPU_OK=0,
 BIWN_RENDER_QUEUE_CPU_BAD_ARGUMENT=1,BIWN_RENDER_QUEUE_CPU_BUS_ERROR=2,
 BIWN_RENDER_QUEUE_CPU_SERVICE_ERROR=3,BIWN_RENDER_QUEUE_CPU_WORK_LIMIT=4,
 BIWN_RENDER_QUEUE_CPU_BAD_RETURN=5,BIWN_RENDER_QUEUE_CPU_YIELDED=6,
 BIWN_RENDER_QUEUE_CPU_BAD_PC=7};
/* Fixed source CPU effects for17DC2renderloop,EA20reset,EA28consumer,
 * E2B8spriteCPUmailbox,E098GPUwait. FullCPU/internal-PC/sourceframes.
 * body stops at outerRTS, call consumesRTS. Renderloop is unbounded and
 * should use stop_on_yield1, leaving DF60 and its return frame intact.
 * Helper providers execute bodies up toRTS. GPU/device behavior and
 * scene17E0E/overlay181F8 are explicit dependencies; no full-game claim.
 * No runtime CPU instruction decode or original CPU/GPU execution. */
enum biwn_render_queue_cpu_status biwn_render_queue_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_render_queue_cpu_status biwn_render_queue_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
