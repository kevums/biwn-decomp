#ifndef BIWN_MEDIA_SETUP_CPU_H
#define BIWN_MEDIA_SETUP_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_media_setup_cpu_status {BIWN_MEDIA_SETUP_CPU_OK=0,BIWN_MEDIA_SETUP_CPU_BAD_ARGUMENT=1,
 BIWN_MEDIA_SETUP_CPU_BUS_ERROR=2,BIWN_MEDIA_SETUP_CPU_SERVICE_ERROR=3,
 BIWN_MEDIA_SETUP_CPU_WORK_LIMIT=4,BIWN_MEDIA_SETUP_CPU_BAD_RETURN=5,
 BIWN_MEDIA_SETUP_CPU_YIELDED=6,BIWN_MEDIA_SETUP_CPU_BAD_PC=7};
/* Source display18160, DSP loaderE840 and cart-space clearDC7C.
 * Full CPU/private frames/both stack banks. Providers supply hardware bus
 * behavior including ignored ROM writes. body stops before RTS; call consumes
 * RTS. No runtime instruction decoding or original CPU-core execution.
 * Generation alone verifies no source path. GPU/DSP program execution,
 * movie state handlers, timing/audio, dialogue and full game remain separate.
 */
enum biwn_media_setup_cpu_status biwn_media_setup_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_media_setup_cpu_status biwn_media_setup_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
