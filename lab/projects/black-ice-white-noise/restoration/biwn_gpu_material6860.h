#ifndef BIWN_GPU_MATERIAL6860_H
#define BIWN_GPU_MATERIAL6860_H
#include <stdint.h>
struct biwn_gpu_material6860_bus {
 int (*read8)(void *,uint32_t,uint8_t *);
 int (*read16)(void *,uint32_t,uint16_t *);
 int (*read32)(void *,uint32_t,uint32_t *);
 int (*write16)(void *,uint32_t,uint16_t);
 int (*write32)(void *,uint32_t,uint32_t);
 void (*observe_PC)(void *,uint32_t);
 void *context;
};
struct biwn_gpu_material6860_state {
 uint32_t registers[2][32],pc,z,c,n,instructions;
};
enum biwn_gpu_material6860_status {BIWN_GPU_MATERIAL6860_OK=0,
 BIWN_GPU_MATERIAL6860_BAD_ARGUMENT=1,BIWN_GPU_MATERIAL6860_BUS_ERROR=2,
 BIWN_GPU_MATERIAL6860_BAD_PC=3,BIWN_GPU_MATERIAL6860_WORK_LIMIT=4,
 BIWN_GPU_MATERIAL6860_BAD_DELAY=5};
/* Fixed original6860 material program, bank0 entry F03240.
 * Caller supplies inherited register/flag and complete memory/control state.
 * Stops at resident F03440 after mandatory delay, without running resident.
 * Errors preserve input state but retain prior external stores. Finite valid
 * source descriptors/buffers required. No opcode decoding or core execution. */
enum biwn_gpu_material6860_status biwn_gpu_material6860_run(struct biwn_gpu_material6860_bus *,struct biwn_gpu_material6860_state *,uint32_t);
#endif
