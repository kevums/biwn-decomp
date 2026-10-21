#ifndef BIWN_FIRMWARE_GPU_RENDERER_H
#define BIWN_FIRMWARE_GPU_RENDERER_H
#include <stdint.h>
struct biwn_firmware_GPU_renderer_state;
struct biwn_firmware_GPU_renderer_bus {
 int (*read8)(void *,uint32_t,uint8_t *);
 int (*read16)(void *,uint32_t,uint16_t *);
 int (*read32)(void *,uint32_t,uint32_t *);
 int (*write16)(void *,uint32_t,uint16_t);
 int (*write32)(void *,uint32_t,uint32_t);
 void (*observe_PC)(void *,struct biwn_firmware_GPU_renderer_state *,uint32_t);
 int (*sync)(void *,struct biwn_firmware_GPU_renderer_state *,int);
 void *context;
};
struct biwn_firmware_GPU_renderer_state {
 uint32_t registers[2][32],pc,z,c,n;
 uint32_t matrix_control,matrix_pointer,division_control,remainder,instructions;
 uint32_t accumulator,hidata,flags,data_organization,control,active_bank;
 uint8_t local_RAM[4096];
};
enum biwn_firmware_GPU_renderer_status {BIWN_FIRMWARE_GPU_RENDERER_OK=0,
 BIWN_FIRMWARE_GPU_RENDERER_BAD_ARGUMENT=1,BIWN_FIRMWARE_GPU_RENDERER_BUS_ERROR=2,
 BIWN_FIRMWARE_GPU_RENDERER_BAD_PC=3,BIWN_FIRMWARE_GPU_RENDERER_WORK_LIMIT=4,
 BIWN_FIRMWARE_GPU_RENDERER_BAD_DELAY=5,BIWN_FIRMWARE_GPU_RENDERER_CHANGED_CODE=7};
/* Observed initialGPUwait+renderer:1017PCs/1321exact byte variants,
 * including code copied/patched in localRAM by source operations.
 * Guards check all instruction/immediate bytes before each compiled block.
 * No runtime decoder, source overlay hostcopy or originalGPU execution.
 * sync exports C logicalstate to shared peripheralbus before external IO,
 * imports peripheral/DMA effects afterward. Blitter and GPU MMIO/IRQ entry
 * are shared hardware-model dependencies, not reconstructed here.
 * run returns0 atsourceGO clear,4 atbudget withstate retained; othererrors
 * leave inputstate unchanged withprior externalstores retained.
 * Source input/initialCPU-DSP-videoIRQ/providedtail and explicitsequencing
 * remain dependencies. Otherqueues/bytevariants/inputs/clocks/discboot/
 * physicalscanout/playability separate; generated code is unverified. */
enum biwn_firmware_GPU_renderer_status biwn_firmware_GPU_renderer_run(struct biwn_firmware_GPU_renderer_bus *,struct biwn_firmware_GPU_renderer_state *,uint32_t);
#endif
