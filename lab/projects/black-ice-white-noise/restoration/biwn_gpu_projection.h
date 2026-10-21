#ifndef BIWN_GPU_PROJECTION_H
#define BIWN_GPU_PROJECTION_H
#include <stdint.h>
struct biwn_gpu_projection_bus {
 int (*read16)(void *,uint32_t,uint16_t *);
 int (*read32)(void *,uint32_t,uint32_t *);
 int (*write16)(void *,uint32_t,uint16_t);
 int (*write32)(void *,uint32_t,uint32_t);
 void (*observe_PC)(void *,uint32_t);
 void *context;
};
struct biwn_gpu_projection_state {
 uint32_t registers[2][32],pc,z,c,n;
 uint32_t matrix_control,matrix_pointer,division_control,remainder,instructions;
 uint32_t accumulator;
 uint8_t local_RAM[4096];
};
enum biwn_gpu_projection_status {BIWN_GPU_PROJECTION_OK=0,
 BIWN_GPU_PROJECTION_BAD_ARGUMENT=1,BIWN_GPU_PROJECTION_BUS_ERROR=2,
 BIWN_GPU_PROJECTION_BAD_PC=3,BIWN_GPU_PROJECTION_WORK_LIMIT=4,
 BIWN_GPU_PROJECTION_BAD_DELAY=5};
/* Fixed450-instruction source program. Bank0 active. Preserve both incoming
 * register banks/flags/accumulator/divider/matrix state and all4KBlocalRAM.
 * prepare loads the frozen overlay and sourceE19E mailbox values without
 * resettingGPUstate. Caller supplies E19E's mainRAM10A684=1 store.
 * Positive finite record buffers required. run returns atF031BE; no source
 * dispatcher, timing, interrupts, drawing/rasterization or scanout claim.
 * Errors retain prior external stores and leave inputstate unchanged. */
enum biwn_gpu_projection_status biwn_gpu_projection_prepare(struct biwn_gpu_projection_state *,uint32_t);
enum biwn_gpu_projection_status biwn_gpu_projection_run(struct biwn_gpu_projection_bus *,struct biwn_gpu_projection_state *,uint32_t);
#endif
