#ifndef BIWN_GPU_RESIDENT_H
#define BIWN_GPU_RESIDENT_H
#include <stdint.h>
struct biwn_gpu_resident_bus {
 int (*read16)(void *,uint32_t,uint16_t *);
 int (*read32)(void *,uint32_t,uint32_t *);
 int (*write32)(void *,uint32_t,uint32_t);
 int (*blitter_write32)(void *,uint32_t,uint32_t,uint8_t *);
 void (*observe_PC)(void *,uint32_t);
 void *context;
};
struct biwn_gpu_resident_state {
 uint32_t registers[2][32],pc,z,c,n;
 uint32_t matrix_control,matrix_pointer,division_control,remainder,instructions;
 uint32_t accumulator;
 uint8_t local_RAM[4096];
};
enum biwn_gpu_resident_status {BIWN_GPU_RESIDENT_OK=0,
 BIWN_GPU_RESIDENT_BAD_ARGUMENT=1,BIWN_GPU_RESIDENT_BUS_ERROR=2,
 BIWN_GPU_RESIDENT_BAD_PC=3,BIWN_GPU_RESIDENT_WORK_LIMIT=4,
 BIWN_GPU_RESIDENT_BAD_DELAY=5};
/* Fixed1275-instruction resident drawing candidate, entry F03440 or F03CA0.
 * Preserve both banks, flags, accumulator/divider/matrix and complete GPU RAM.
 * Source image is already installed by57A0; caller supplies actual inherited
 * state and finite valid source buffers. Stop at dispatcher F031BE, without
 * running dispatcher. No opcode decoder/original GPU execution on C side.
 * blitter_write32 receives current4096byte localRAM on command writeF02238;
 * backend must publish it before DMA and copy any DMA localRAM effects back.
 * Other external writes use write32. Synchronous blitter backend required.
 * Errors retain prior external stores/DMA effects; input state unchanged.
 * No async timing, interrupts, scanout/fullgame or hardware accuracy claim. */
enum biwn_gpu_resident_status biwn_gpu_resident_run(struct biwn_gpu_resident_bus *,struct biwn_gpu_resident_state *,uint32_t);
#endif
