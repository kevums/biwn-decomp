#ifndef BIWN_NPC_CPU_H
#define BIWN_NPC_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_npc_cpu_status {BIWN_NPC_CPU_OK=0,BIWN_NPC_CPU_BAD_ARGUMENT=1,
 BIWN_NPC_CPU_BUS_ERROR=2,BIWN_NPC_CPU_SERVICE_ERROR=3,
 BIWN_NPC_CPU_WORK_LIMIT=4,BIWN_NPC_CPU_BAD_RETURN=5,
 BIWN_NPC_CPU_YIELDED=6,BIWN_NPC_CPU_BAD_PC=7,BIWN_NPC_CPU_READY=8};
/* Fixed EDC4 task/101E0asset init/10252distance squared/1404Cfacing/
 * ED60choice/207CCmessage caller. Full CPU/private frames, both stack banks.
 * DF60 and DF7A stop with complete state/private frames for scheduler yield
 * or removal. Nested resource DF8C waits retain CPU/private frames.
 * Internal PC continuation supported. Helpers remain providers;
 * some message/video/input branches are unported. body stops before RTS;
 * call consumes RTS. No runtime decoding/core calls. Generation does not
 * prove dialog, sprite rendering, NPC behavior or whole-game completion. */
enum biwn_npc_cpu_status biwn_npc_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_npc_cpu_status biwn_npc_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
/* Added host observation boundary only: commit state before EE20's first
 * loop instruction, returning READY. Existing body/call behavior unchanged.
 * This lets declared external inputs be applied at the same source PC on
 * native and C paths; it is not a guest instruction or completion claim. */
enum biwn_npc_cpu_status biwn_npc_cpu_until_loop(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
