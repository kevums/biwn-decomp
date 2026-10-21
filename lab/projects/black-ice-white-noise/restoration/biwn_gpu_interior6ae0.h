#ifndef BIWN_GPU_INTERIOR6AE0_H
#define BIWN_GPU_INTERIOR6AE0_H
#include <stdint.h>
struct biwn_gpu_interior6ae0_bus {
 int (*read16)(void *,uint32_t,uint16_t *);
 int (*read32)(void *,uint32_t,uint32_t *);
 int (*write16)(void *,uint32_t,uint16_t);
 int (*write32)(void *,uint32_t,uint32_t);
 void (*observe_PC)(void *,uint32_t);
 void *context;
};
struct biwn_gpu_interior6ae0_state {
 uint32_t registers[2][32],pc,z,c,n;
 uint32_t matrix_control,matrix_pointer,division_control,remainder,instructions;
 uint8_t local_RAM[4096];
};
enum biwn_gpu_interior6ae0_status {BIWN_GPU_INTERIOR6AE0_OK=0,
 BIWN_GPU_INTERIOR6AE0_BAD_ARGUMENT=1,BIWN_GPU_INTERIOR6AE0_BUS_ERROR=2,
 BIWN_GPU_INTERIOR6AE0_BAD_PC=3,BIWN_GPU_INTERIOR6AE0_WORK_LIMIT=4,
 BIWN_GPU_INTERIOR6AE0_BAD_DELAY=5};
/* Fixed276source instructions, source-specific reconstruction.
 * Bank0 active. prepare preserves incoming banks/flags/matrix/divider/RAM,
 * installs the original overlay and sourceE0F2/E148 arguments. Valid finite
 * relocated interior scene and in-range room sector are caller requirements.
 * run stops atF031BE after mandatory delay. No dispatcher/CPU wrapper,
 * boot/load integration, timing, interrupts, raster/scanout/fullgame claim.
 * Errors retain prior bus stores and leave caller state unchanged. */
enum biwn_gpu_interior6ae0_status biwn_gpu_interior6ae0_prepare(struct biwn_gpu_interior6ae0_state *,uint32_t,uint32_t);
enum biwn_gpu_interior6ae0_status biwn_gpu_interior6ae0_run(struct biwn_gpu_interior6ae0_bus *,struct biwn_gpu_interior6ae0_state *,uint32_t);
#endif
