#ifndef BIWN_SCENE_DRAW_CPU_H
#define BIWN_SCENE_DRAW_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_scene_draw_cpu_status {BIWN_SCENE_DRAW_CPU_OK=0,
 BIWN_SCENE_DRAW_CPU_BAD_ARGUMENT=1,BIWN_SCENE_DRAW_CPU_BUS_ERROR=2,
 BIWN_SCENE_DRAW_CPU_SERVICE_ERROR=3,BIWN_SCENE_DRAW_CPU_WORK_LIMIT=4,
 BIWN_SCENE_DRAW_CPU_BAD_RETURN=5,BIWN_SCENE_DRAW_CPU_YIELDED=6,
 BIWN_SCENE_DRAW_CPU_BAD_PC=7};
/* Static full CPU/source frames for E03A clear,17E0E scene caller and
 * 17F14 buffer rotation. Both stack banks. body stops at outer RTS;
 * call consumes it. Dependencies execute up to RTS through a provider.
 * Device rasterization, six scene/geometry helpers,E098 wait and185B2
 * display-list builder are separate dependencies. No whole viewport claim.
 * No runtime instruction decoding or original CPU calls. */
enum biwn_scene_draw_cpu_status biwn_scene_draw_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_scene_draw_cpu_status biwn_scene_draw_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
