#ifndef BIWN_STARTUP_HUD_CPU_H
#define BIWN_STARTUP_HUD_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_startup_HUD_cpu_status {BIWN_STARTUP_HUD_CPU_OK=0,BIWN_STARTUP_HUD_CPU_BAD_ARGUMENT=1,
 BIWN_STARTUP_HUD_CPU_BUS_ERROR=2,BIWN_STARTUP_HUD_CPU_SERVICE_ERROR=3,
 BIWN_STARTUP_HUD_CPU_WORK_LIMIT=4,BIWN_STARTUP_HUD_CPU_BAD_RETURN=5,
 BIWN_STARTUP_HUD_CPU_YIELDED=6,BIWN_STARTUP_HUD_CPU_BAD_PC=7,BIWN_STARTUP_HUD_CPU_DIVISION_BY_ZERO=8,BIWN_STARTUP_HUD_CPU_DIVISION_OVERFLOW=9};
/* Source1B786 money/status HUD and18888 health/status drawing.
 * Fixed572 instruction blocks/fullCPU/private frames/both stack banks.
 * Text149AE, formatter1B45A and spriteE2B8 execute through helper bodies.
 * No runtime decoding/original CPU calls. Generation alone proves no
 * source path, complete GPU context, scanout, boot or playable game. */
enum biwn_startup_HUD_cpu_status biwn_startup_HUD_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_startup_HUD_cpu_status biwn_startup_HUD_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
