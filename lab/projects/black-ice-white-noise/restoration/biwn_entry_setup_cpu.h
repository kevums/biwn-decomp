#ifndef BIWN_ENTRY_SETUP_CPU_H
#define BIWN_ENTRY_SETUP_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_entry_setup_cpu_status {BIWN_ENTRY_SETUP_CPU_OK=0,BIWN_ENTRY_SETUP_CPU_BAD_ARGUMENT=1,
 BIWN_ENTRY_SETUP_CPU_BUS_ERROR=2,BIWN_ENTRY_SETUP_CPU_SERVICE_ERROR=3,
 BIWN_ENTRY_SETUP_CPU_WORK_LIMIT=4,BIWN_ENTRY_SETUP_CPU_BAD_RETURN=5,
 BIWN_ENTRY_SETUP_CPU_YIELDED=6,BIWN_ENTRY_SETUP_CPU_BAD_PC=7,BIWN_ENTRY_SETUP_CPU_READY=8};
/* Source4000 caller up toDD40, DFF4 disc-mode/TOC calls,
 * E6A0 region/video/object-list descriptors,1557A allocator,17340 lists,
 * E942/E96C/EA08 music DSP load/mailbox wait. Source private frames/banks.
 * READY8 stops beforeDD40. BIOS/GPU/video/music execution and timer
 * progression are explicit providers; generation alone proves no boot.
 * Source4000 requires supervisor entry; no privilege-exception emulation.
 * No runtime decoder/originalCPU calls. Body stops before outerRTS;
 * call consumesRTS. PriorRAMeffects retained on hosterrors. */
enum biwn_entry_setup_cpu_status biwn_entry_setup_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_entry_setup_cpu_status biwn_entry_setup_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
