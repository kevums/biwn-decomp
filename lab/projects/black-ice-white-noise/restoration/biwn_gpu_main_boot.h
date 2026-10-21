#ifndef BIWN_GPU_MAIN_BOOT_H
#define BIWN_GPU_MAIN_BOOT_H
#include <stdint.h>
struct biwn_gpu_main_boot_bus {
 int (*read16)(void *,uint32_t,uint16_t *);
 int (*read32)(void *,uint32_t,uint32_t *);
 int (*write16)(void *,uint32_t,uint16_t);
 int (*write32)(void *,uint32_t,uint32_t);
 void (*observe_PC)(void *,uint32_t);
 void *context;
};
struct biwn_gpu_main_boot_state {
 uint32_t registers[2][32],pc,z,c,n;
 uint32_t matrix_control,matrix_pointer,division_control,remainder,instructions;
 uint32_t accumulator,hidata,flags,data_organization,control,active_bank;
 uint8_t local_RAM[4096];
};
enum biwn_gpu_main_boot_status {BIWN_GPU_MAIN_BOOT_OK=0,
 BIWN_GPU_MAIN_BOOT_BAD_ARGUMENT=1,BIWN_GPU_MAIN_BOOT_BUS_ERROR=2,
 BIWN_GPU_MAIN_BOOT_BAD_PC=3,BIWN_GPU_MAIN_BOOT_WORK_LIMIT=4,
 BIWN_GPU_MAIN_BOOT_BAD_DELAY=5};
/*21execution-proven static GPU initializer instructions, bank0.
 * EntryF03224 setsr31, IRQ enableflags, object-list/VMODE/timing registers,
 * returns atF031BE dispatcher before idle loop. Inherited full banks/flags/
 * localRAM and peripheral callbacks; original GPU never executes. Unknown
 * PCs fail, no runtime decoder. Bank1 is unsupported; no other IRQ/main
 * boot/fullgame/physicalhardware claim. Prior bus stores survive host error,
 * inputstate commits only success. Source callbacks must not introduce a
 * pending enabled GPU IRQ during initializer; that is a separate event. */
enum biwn_gpu_main_boot_status biwn_gpu_main_boot_run(struct biwn_gpu_main_boot_bus *,struct biwn_gpu_main_boot_state *,uint32_t);
#endif
