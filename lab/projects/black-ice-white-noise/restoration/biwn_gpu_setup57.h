#ifndef BIWN_GPU_SETUP57_H
#define BIWN_GPU_SETUP57_H
#include <stdint.h>
struct biwn_gpu_setup57_bus {
 int (*read32)(void *,uint32_t,uint32_t *);
 int (*write32)(void *,uint32_t,uint32_t);
 void (*observe_PC)(void *,uint32_t);
 void *context;
};
struct biwn_gpu_setup57_state {uint32_t registers[2][32],pc,z,c,n,instructions;};
enum biwn_gpu_setup57_status {BIWN_GPU_SETUP57_OK=0,BIWN_GPU_SETUP57_BAD_ARGUMENT=1,
 BIWN_GPU_SETUP57_BUS_ERROR=2,BIWN_GPU_SETUP57_BAD_PC=3,
 BIWN_GPU_SETUP57_WORK_LIMIT=4,BIWN_GPU_SETUP57_BAD_DELAY=5};
/* Fixed73instruction57A0 program. Incomingbank0/localRAM/control/blitterstate
 * supplied by caller. Bus implements all sharedRAM, GPUlocal/control and
 * pinnedblittereffects. Preserves64registers andZ/C/N; queues6380 thenreturns
 * F031BE. No dispatcher/completion, laterdraw/scanout/viewport/timing claim.
 * Errors preservepriorbuswrites and leaveinputstateunchanged. */
enum biwn_gpu_setup57_status biwn_gpu_setup57_run(struct biwn_gpu_setup57_bus *,struct biwn_gpu_setup57_state *,uint32_t);
#endif
