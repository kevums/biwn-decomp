#ifndef BIWN_GPU_DISPATCHER_H
#define BIWN_GPU_DISPATCHER_H
#include <stdint.h>
struct biwn_gpu_dispatcher_bus {
 int (*read32)(void *,uint32_t,uint32_t *);
 int (*write32)(void *,uint32_t,uint32_t);
 void (*observe_PC)(void *,uint32_t,uint32_t,uint32_t,uint32_t);
 void *context;
};
struct biwn_gpu_dispatcher_state {
 uint32_t registers[2][32],pc,z,c,n,instructions;
};
enum biwn_gpu_dispatcher_status {BIWN_GPU_DISPATCHER_OK=0,
 BIWN_GPU_DISPATCHER_BAD_ARGUMENT=1,BIWN_GPU_DISPATCHER_BUS_ERROR=2,
 BIWN_GPU_DISPATCHER_BAD_PC=3,BIWN_GPU_DISPATCHER_WORK_LIMIT=4,
 BIWN_GPU_DISPATCHER_BAD_DELAY=5};
/* Original31-instruction dispatcher loop F031BE..F03200, bank0.
 * Caller supplies finite valid program headers/payloads and complete GPU/main
 * RAM bus. Return at external program entry or, when yield_idle=1, idle poll
 * F031CE with mailboxFFFF and busy0, matching the draw host's stop boundary.
 * yield_idle=0 follows source polling; caller/device supplies any commands.
 * No program execution, full mainGPUboot, timing/interrupt or fullgame claim.
 * Errors preserve input state but retain prior external stores.
 */
enum biwn_gpu_dispatcher_status biwn_gpu_dispatcher_run(struct biwn_gpu_dispatcher_bus *,struct biwn_gpu_dispatcher_state *,uint32_t,uint32_t);
#endif
