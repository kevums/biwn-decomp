#ifndef BIWN_GPU_GEOMETRY_H
#define BIWN_GPU_GEOMETRY_H
#include <stdint.h>
struct biwn_gpu_geometry_bus {
 int (*read16)(void *,uint32_t,uint16_t *);
 int (*read32)(void *,uint32_t,uint32_t *);
 int (*write16)(void *,uint32_t,uint16_t);
 int (*write32)(void *,uint32_t,uint32_t);
 void (*observe_PC)(void *,uint32_t);
 void *context;
};
struct biwn_gpu_geometry_state {
 uint32_t registers[2][32],pc,z,c,n;
 uint32_t matrix_control,matrix_pointer,division_control,remainder,instructions;
 uint8_t local_RAM[4096];
};
enum biwn_gpu_geometry_status {BIWN_GPU_GEOMETRY_OK=0,
 BIWN_GPU_GEOMETRY_BAD_ARGUMENT=1,BIWN_GPU_GEOMETRY_BUS_ERROR=2,
 BIWN_GPU_GEOMETRY_BAD_PC=3,BIWN_GPU_GEOMETRY_WORK_LIMIT=4,
 BIWN_GPU_GEOMETRY_BAD_DELAY=5};
/* Source-specific GPU4D80 program,434 fixed instructions and source data.
 * No runtime opcode decoding or originalGPU/core calls. init supplies the
 * checked bank0 entry/mailboxes/divider mode and register seed. Optional
 * initialRAM supplies4096bytes of otherwise untouched localRAM; NULL fillsFF.
 * run stops
 * at dispatcher returnF031BE; executes mandatory branch delay slots.
 * Full integer registers/flags/localRAM and external memory effects.
 * No dispatcher acknowledgement, interrupts, bank switching or timing.
 * Budget/bus errors retain prior external stores, leave inputstate unchanged.
 * Valid finite source buffers required; this alone is no full viewport. */
enum biwn_gpu_geometry_status biwn_gpu_geometry_init(struct biwn_gpu_geometry_state *,uint32_t,const uint8_t *);
enum biwn_gpu_geometry_status biwn_gpu_geometry_run(struct biwn_gpu_geometry_bus *,struct biwn_gpu_geometry_state *,uint32_t);
#endif
