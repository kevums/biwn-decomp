#ifndef BIWN_GPU_COMMAND4720_H
#define BIWN_GPU_COMMAND4720_H
#include <stdint.h>
struct biwn_gpu_command4720_bus {
 int (*read16)(void *,uint32_t,uint16_t *);
 int (*read32)(void *,uint32_t,uint32_t *);
 int (*write16)(void *,uint32_t,uint16_t);
 int (*write32)(void *,uint32_t,uint32_t);
 void (*observe_PC)(void *,uint32_t);
 void *context;
};
struct biwn_gpu_command4720_state {
 uint32_t registers[2][32],pc,z,c,n;
 uint32_t matrix_control,matrix_pointer,division_control,remainder,instructions;
 uint32_t accumulator,hidata,flags,data_organization,control,active_bank;
 uint8_t local_RAM[4096];
};
enum biwn_gpu_command4720_status {BIWN_GPU_COMMAND4720_OK=0,
 BIWN_GPU_COMMAND4720_BAD_ARGUMENT=1,BIWN_GPU_COMMAND4720_BUS_ERROR=2,
 BIWN_GPU_COMMAND4720_BAD_PC=3,BIWN_GPU_COMMAND4720_WORK_LIMIT=4,
 BIWN_GPU_COMMAND4720_BAD_DELAY=5};
/* Candidate fixed GPU4720 instructions; full inherited logical GPU state,
 * supplied source-loaded local RAM. Return at residentF031BE; mandatory
 * delay slots execute. No runtime decoder or originalGPU calls on C path.
 * Errors retain prior external writes and leave inputstate unchanged.
 * This generated artifact is unverified until native comparison passes.
 * Pipeline microstate, timing, dispatcher/CPU service and game integration
 * remain outside this module. */
enum biwn_gpu_command4720_status biwn_gpu_command4720_run(struct biwn_gpu_command4720_bus *,struct biwn_gpu_command4720_state *,uint32_t);
#endif
