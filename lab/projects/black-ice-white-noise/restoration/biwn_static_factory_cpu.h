#ifndef BIWN_STATIC_FACTORY_CPU_H
#define BIWN_STATIC_FACTORY_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_static_factory_cpu_status {BIWN_STATIC_FACTORY_CPU_OK=0,BIWN_STATIC_FACTORY_CPU_BAD_ARGUMENT=1,
 BIWN_STATIC_FACTORY_CPU_BUS_ERROR=2,BIWN_STATIC_FACTORY_CPU_SERVICE_ERROR=3,
 BIWN_STATIC_FACTORY_CPU_WORK_LIMIT=4,BIWN_STATIC_FACTORY_CPU_BAD_RETURN=5,
 BIWN_STATIC_FACTORY_CPU_YIELDED=6,BIWN_STATIC_FACTORY_CPU_BAD_PC=7};
/* Source137E0 static/sprite factory,184 fixed instruction blocks.
 * Inline138BC..13902 callback/jump table stays source data read via bus.
 * Full CPU/private frames/both stack banks; helpers run up to outer RTS.
 * 105DA position,152A2 allocator andE2B8 sprite submission are providers.
 * No runtime decoding or original CPU calls. Generated code alone proves
 * no scene, GPU/context, source boot or complete game behavior. */
enum biwn_static_factory_cpu_status biwn_static_factory_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_static_factory_cpu_status biwn_static_factory_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
