#ifndef BIWN_BIOS_CONTROLLER_CPU_H
#define BIWN_BIOS_CONTROLLER_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_bios_controller_cpu_status {BIWN_BIOS_CONTROLLER_CPU_OK=0,BIWN_BIOS_CONTROLLER_CPU_BAD_ARGUMENT=1,
 BIWN_BIOS_CONTROLLER_CPU_BUS_ERROR=2,BIWN_BIOS_CONTROLLER_CPU_SERVICE_ERROR=3,
 BIWN_BIOS_CONTROLLER_CPU_WORK_LIMIT=4,BIWN_BIOS_CONTROLLER_CPU_BAD_RETURN=5,
 BIWN_BIOS_CONTROLLER_CPU_YIELDED=6,BIWN_BIOS_CONTROLLER_CPU_BAD_PC=7};
/* Actual user BIOS entry3048/35DE..3610 controller initialization.
 * ROM84A6..92A6 supplies the resident image at3000; source function
 * writes BUTCH control/DSC/I2S/reset and DSA command7001. Firmware
 * transport/device effects are supplied by the hardware bus.
 * Full CPU/private frame/bothstackbanks; shared hardware bus is supplied.
 * No runtime decoder/originalCPU calls. Boot/firmware relocation, BUTCH
 * transport, other BIOS entries/CDGPUISR execution remain separate. */
enum biwn_bios_controller_cpu_status biwn_bios_controller_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_bios_controller_cpu_status biwn_bios_controller_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
