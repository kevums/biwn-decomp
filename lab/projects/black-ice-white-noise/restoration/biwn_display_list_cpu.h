#ifndef BIWN_DISPLAY_LIST_CPU_H
#define BIWN_DISPLAY_LIST_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_display_list_cpu_status {BIWN_DISPLAY_LIST_CPU_OK=0,BIWN_DISPLAY_LIST_CPU_BAD_ARGUMENT=1,
 BIWN_DISPLAY_LIST_CPU_BUS_ERROR=2,BIWN_DISPLAY_LIST_CPU_SERVICE_ERROR=3,
 BIWN_DISPLAY_LIST_CPU_WORK_LIMIT=4,BIWN_DISPLAY_LIST_CPU_BAD_RETURN=5,
 BIWN_DISPLAY_LIST_CPU_YIELDED=6,BIWN_DISPLAY_LIST_CPU_BAD_PC=7};
/* Static254sourceinstruction blocks185B2displaylist. Bothstackbanks,
 * full registers/CCR and actualLINK/MOVEM/dynamicprivate link table.
 * body stops beforeRTS;call executesit. No nestedhelpers/originalCPUcalls
 * or runtime instructiondecode. Tabledata read through suppliedbus.
 * Finite valid descriptor lists/source table indices; explicit budget.
 * This alone does not execute the objectprocessor or display scanout. */
enum biwn_display_list_cpu_status biwn_display_list_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_display_list_cpu_status biwn_display_list_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
