#ifndef BIWN_GPU_MATERIAL6720_H
#define BIWN_GPU_MATERIAL6720_H
#include <stdint.h>
struct biwn_gpu_material6720_bus {
 int (*read8)(void *,uint32_t,uint8_t *);
 int (*read16)(void *,uint32_t,uint16_t *);
 int (*read32)(void *,uint32_t,uint32_t *);
 int (*write16)(void *,uint32_t,uint16_t);
 int (*write32)(void *,uint32_t,uint32_t);
 void (*observe_PC)(void *,uint32_t);
 void *context;
};
struct biwn_gpu_material6720_state {
 uint32_t registers[2][32],pc,z,c,n,instructions;
};
enum biwn_gpu_material6720_status {BIWN_GPU_MATERIAL6720_OK=0,
 BIWN_GPU_MATERIAL6720_BAD_ARGUMENT=1,BIWN_GPU_MATERIAL6720_BUS_ERROR=2,
 BIWN_GPU_MATERIAL6720_BAD_PC=3,BIWN_GPU_MATERIAL6720_WORK_LIMIT=4,
 BIWN_GPU_MATERIAL6720_BAD_DELAY=5};
/* Fixed original6720 material program, bank0 entry F03240.
 * Caller supplies inherited register/flag and complete memory/control state.
 * Stops at resident F03440 after mandatory delay, without running resident.
 * Errors preserve input state but retain prior external stores. Finite valid
 * source descriptors/buffers required. No opcode decoding or core execution. */
enum biwn_gpu_material6720_status biwn_gpu_material6720_run(struct biwn_gpu_material6720_bus *,struct biwn_gpu_material6720_state *,uint32_t);
#endif
