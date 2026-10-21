#ifndef BIWN_BIOS_RESIDENT_INSTALL_CPU_H
#define BIWN_BIOS_RESIDENT_INSTALL_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
/* Actual ROM80203E resident-image copy stops before BSR802070 at802054.
 * Copies2540bytes ROM8084A6..808E92 intoRAM3000..39EC: long copy
 * overshoots nominal ROM end808E90 by2bytes. InitialROM/RAM/CPU/bus
 * supplied; preceding/following firmware, initial game-load and clocks
 * remain separate. No decoder or original CPU execution. */
enum biwn_bios_resident_install_status { BIWN_BIOS_RESIDENT_INSTALL_OK=0,
 BIWN_BIOS_RESIDENT_INSTALL_BAD_ARGUMENT=1,BIWN_BIOS_RESIDENT_INSTALL_BUS_ERROR=2,
 BIWN_BIOS_RESIDENT_INSTALL_WORK_LIMIT=4,BIWN_BIOS_RESIDENT_INSTALL_BAD_PC=7 };
enum biwn_bios_resident_install_status biwn_bios_resident_install_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
