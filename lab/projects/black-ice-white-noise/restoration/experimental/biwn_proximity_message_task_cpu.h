#ifndef BIWN_PROXIMITY_MESSAGE_TASK_CPU_H
#define BIWN_PROXIMITY_MESSAGE_TASK_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_proximity_message_task_cpu_status {BIWN_PROXIMITY_MESSAGE_TASK_CPU_OK=0,BIWN_PROXIMITY_MESSAGE_TASK_CPU_BAD_ARGUMENT=1,
 BIWN_PROXIMITY_MESSAGE_TASK_CPU_BUS_ERROR=2,BIWN_PROXIMITY_MESSAGE_TASK_CPU_SERVICE_ERROR=3,
 BIWN_PROXIMITY_MESSAGE_TASK_CPU_WORK_LIMIT=4,BIWN_PROXIMITY_MESSAGE_TASK_CPU_BAD_RETURN=5,
 BIWN_PROXIMITY_MESSAGE_TASK_CPU_YIELDED=6,BIWN_PROXIMITY_MESSAGE_TASK_CPU_BAD_PC=7};
/* Source1B480 task initialization and warm1B4E8 loop. Enable43D98,
 * once46880, (X-24380)^2+(Z-26784)^2 signedcomparison<=1024, then
 * source207CC message3 call and flag1. E540multiply and207CCmessage
 * are explicit service interfaces. FullCPU/privateframes/stackbanks.
 * Task yields atDF60 with actualJSRframe. Allsourceblocks generated,
 * helper/device/globaltiming/game proof separate. */
enum biwn_proximity_message_task_cpu_status biwn_proximity_message_task_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_proximity_message_task_cpu_status biwn_proximity_message_task_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
