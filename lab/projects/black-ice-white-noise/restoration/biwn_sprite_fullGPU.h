#ifndef BIWN_SPRITE_FULLGPU_H
#define BIWN_SPRITE_FULLGPU_H
#include <stdint.h>
struct biwn_sprite_fullGPU_bus {
 int (*read8)(void *,uint32_t,uint8_t *);
 int (*read16)(void *,uint32_t,uint16_t *);
 int (*read32)(void *,uint32_t,uint32_t *);
 int (*write16)(void *,uint32_t,uint16_t);
 int (*write32)(void *,uint32_t,uint32_t);
 void (*observe_PC)(void *,uint32_t);
 void *context;
};
struct biwn_sprite_fullGPU_state {
 uint32_t registers[2][32],pc,z,c,n;
 uint32_t matrix_control,matrix_pointer,division_control,remainder,instructions;
 uint32_t accumulator,hidata,flags,data_organization,control,active_bank;
 uint8_t local_RAM[4096];
};
enum biwn_sprite_fullGPU_status {BIWN_SPRITE_FULLGPU_OK=0,
 BIWN_SPRITE_FULLGPU_BAD_ARGUMENT=1,BIWN_SPRITE_FULLGPU_BUS_ERROR=2,
 BIWN_SPRITE_FULLGPU_BAD_PC=3,BIWN_SPRITE_FULLGPU_WORK_LIMIT=4,
 BIWN_SPRITE_FULLGPU_BAD_DELAY=5};
/* Fixed source GPU4B00 movement instructions, bank0, supplied inherited
 * full logical GPU state and source-loaded local RAM. Stops at resident
 * dispatcher F031BE; executes taken branch delay slots. No init/reset,
 * runtime decoder, original GPU calls or high-level matrix substitution.
 * Errors leave input state unchanged and retain external writes. Finite
 * source buffers/budget required. No timing/interrupt/full game claim. */
enum biwn_sprite_fullGPU_status biwn_sprite_fullGPU_run(struct biwn_sprite_fullGPU_bus *,struct biwn_sprite_fullGPU_state *,uint32_t);
#endif
