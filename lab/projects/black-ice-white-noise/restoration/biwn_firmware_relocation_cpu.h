#ifndef BIWN_FIRMWARE_RELOCATION_CPU_H
#define BIWN_FIRMWARE_RELOCATION_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_firmware_relocation_cpu_status {BIWN_FIRMWARE_RELOCATION_CPU_OK=0,BIWN_FIRMWARE_RELOCATION_CPU_BAD_ARGUMENT=1,
 BIWN_FIRMWARE_RELOCATION_CPU_BUS_ERROR=2,BIWN_FIRMWARE_RELOCATION_CPU_SERVICE_ERROR=3,
 BIWN_FIRMWARE_RELOCATION_CPU_WORK_LIMIT=4,BIWN_FIRMWARE_RELOCATION_CPU_BAD_RETURN=5,
 BIWN_FIRMWARE_RELOCATION_CPU_YIELDED=6,BIWN_FIRMWARE_RELOCATION_CPU_BAD_PC=7,BIWN_FIRMWARE_RELOCATION_CPU_READY=8};
/* UserROM802000..8020B6 bootstrap: source stack setup, display/main/
 * resident copies, real BSR/RTS802070, four table-selected resource copies,
 * source patch at196446 and natural JMP500D6. READY8 stops before relocated
 * main's first instruction. Initial ROM/CPU/bus/device state supplied.
 * No runtime decoder/original CPU execution. Firmware authentication,
 * initial game-stub delivery, DSP execution and global clocks separate. */
enum biwn_firmware_relocation_cpu_status biwn_firmware_relocation_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_firmware_relocation_cpu_status biwn_firmware_relocation_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
