#ifndef BIWN_GPU_CONSUMER6380_H
#define BIWN_GPU_CONSUMER6380_H
#include <stdint.h>
struct biwn_gpu_consumer6380_bus {
 int (*read16)(void *,uint32_t,uint16_t *);
 int (*read32)(void *,uint32_t,uint32_t *);
 int (*write32)(void *,uint32_t,uint32_t);
 void (*observe_PC)(void *,uint32_t);
 void *context;
};
struct biwn_gpu_consumer6380_state {
 uint32_t registers[2][32],pc,z,c,n,instructions;
};
enum biwn_gpu_consumer6380_status {BIWN_GPU_CONSUMER6380_OK=0,
 BIWN_GPU_CONSUMER6380_BAD_ARGUMENT=1,BIWN_GPU_CONSUMER6380_BUS_ERROR=2,
 BIWN_GPU_CONSUMER6380_BAD_PC=3,BIWN_GPU_CONSUMER6380_WORK_LIMIT=4,
 BIWN_GPU_CONSUMER6380_BAD_DELAY=5};
/* Fixed original6380 list consumer, bank0 entry F03240. Preserve both register
 * banks and flags; caller supplies the actual GPU/main RAM through the bus.
 * Returns at dispatcher F031BE or resident handoff F03440/F03CA0 after delay.
 * Does not run those recipient programs or load source overlays. No runtime
 * opcode decoding/core execution, timing, interrupt or full renderer claim.
 * Errors retain prior external stores but leave input state unchanged.
 * Valid finite source list/record/table buffers required. */
enum biwn_gpu_consumer6380_status biwn_gpu_consumer6380_run(struct biwn_gpu_consumer6380_bus *,struct biwn_gpu_consumer6380_state *,uint32_t);
#endif
