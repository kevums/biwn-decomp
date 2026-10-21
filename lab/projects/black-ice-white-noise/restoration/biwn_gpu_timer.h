#ifndef BIWN_GPU_TIMER_H
#define BIWN_GPU_TIMER_H
#include <stdint.h>
struct biwn_gpu_timer_bus {
 int (*read16)(void *,uint32_t,uint16_t *);
 int (*read32)(void *,uint32_t,uint32_t *);
 int (*write16)(void *,uint32_t,uint16_t);
 int (*write32)(void *,uint32_t,uint32_t);
 void (*observe_PC)(void *,uint32_t);
 void *context;
};
struct biwn_gpu_timer_state {
 uint32_t registers[2][32],pc,z,c,n;
 uint32_t matrix_control,matrix_pointer,division_control,remainder,instructions;
 uint32_t accumulator,hidata,flags,data_organization,control,active_bank;
 uint8_t local_RAM[4096];
};
enum biwn_gpu_timer_status {BIWN_GPU_TIMER_OK=0,
 BIWN_GPU_TIMER_BAD_ARGUMENT=1,BIWN_GPU_TIMER_BUS_ERROR=2,
 BIWN_GPU_TIMER_BAD_PC=3,BIWN_GPU_TIMER_WORK_LIMIT=4,
 BIWN_GPU_TIMER_BAD_DELAY=5,BIWN_GPU_TIMER_HALTED=6,BIWN_GPU_TIMER_LATCHED=7};
/* Resident GPU IRQ2 vector/clock handler and common return epilogue.
 * Fixed source blocks, own timer event/PC-2 frame, full logical state.
 * Handler uses bank0; event may enter from bank1 and return to it.
 * Clock778CC increments; BD854+BD858 carry increments wordBD852.
 * No runtime decoder/originalGPU calls. run stops on returned originalPC.
 * Timer delivery/period and other IRQs remain explicit host dependencies. */
enum biwn_gpu_timer_status biwn_gpu_timer_run(struct biwn_gpu_timer_bus *,struct biwn_gpu_timer_state *,uint32_t,uint32_t);
enum biwn_gpu_timer_status biwn_gpu_timer_assert(struct biwn_gpu_timer_bus *,struct biwn_gpu_timer_state *);
#endif
