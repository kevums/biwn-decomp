#ifndef BIWN_OVERLAY_TEXT_CPU_H
#define BIWN_OVERLAY_TEXT_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_overlay_text_cpu_status {BIWN_OVERLAY_TEXT_CPU_OK=0,BIWN_OVERLAY_TEXT_CPU_BAD_ARGUMENT=1,
 BIWN_OVERLAY_TEXT_CPU_BUS_ERROR=2,BIWN_OVERLAY_TEXT_CPU_SERVICE_ERROR=3,
 BIWN_OVERLAY_TEXT_CPU_WORK_LIMIT=4,BIWN_OVERLAY_TEXT_CPU_BAD_RETURN=5,
 BIWN_OVERLAY_TEXT_CPU_YIELDED=6,BIWN_OVERLAY_TEXT_CPU_BAD_PC=7};
/* Static642sourceinstruction blocks181F8overlay,14776alignment,
 * 147A6font3,149AEtext andE540multiply. Bothstackbanks/fullCPU/private
 * frames; original font3jumptable remainsbus data. body stops beforeRTS;
 * call consumesit. Nested helper providers execute up toRTS, including
 * separate fullCPU1B45Aformatter. No originalCPUcalls/runtimedecode.
 * Drawing device is an explicit bus provider; no scanout/fullgame proof. */
enum biwn_overlay_text_cpu_status biwn_overlay_text_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_overlay_text_cpu_status biwn_overlay_text_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
