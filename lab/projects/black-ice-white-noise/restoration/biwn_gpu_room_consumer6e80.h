#ifndef BIWN_GPU_ROOM_CONSUMER6E80_H
#define BIWN_GPU_ROOM_CONSUMER6E80_H
#include <stdint.h>
struct biwn_gpu_room_consumer6e80_bus {
 int (*read16)(void *,uint32_t,uint16_t *);
 int (*read32)(void *,uint32_t,uint32_t *);
 int (*write16)(void *,uint32_t,uint16_t);
 int (*write32)(void *,uint32_t,uint32_t);
 void (*observe_PC)(void *,uint32_t);
 void *context;
};
struct biwn_gpu_room_consumer6e80_state {
 uint32_t registers[2][32],pc,z,c,n;
 uint32_t matrix_control,matrix_pointer,division_control,remainder,instructions;
 uint8_t local_RAM[4096];
};
enum biwn_gpu_room_consumer6e80_status {BIWN_GPU_ROOM_CONSUMER6E80_OK=0,
 BIWN_GPU_ROOM_CONSUMER6E80_BAD_ARGUMENT=1,BIWN_GPU_ROOM_CONSUMER6E80_BUS_ERROR=2,
 BIWN_GPU_ROOM_CONSUMER6E80_BAD_PC=3,BIWN_GPU_ROOM_CONSUMER6E80_WORK_LIMIT=4,
 BIWN_GPU_ROOM_CONSUMER6E80_BAD_DELAY=5};
/* Fixed222sourceinstructions. Source57A0/dispatcher supplies the entry
 * registers and source overlay. Bank0active; preserve full incoming banks,
 * Z/C/N,matrix/divider and4KBlocalRAM. run returns at residentF03440;
 * mesh data/face records are written through the supplied bus. Mandatory
 * delay slots execute. No runtime decode or original GPU/core calls.
 * Does not run resident transforms/material/raster/dispatcher or fullgame.
 * Finite valid room/dimension/portal buffers required; no physical timing.
 * Errors retain prior stores and leave caller state unchanged. */
enum biwn_gpu_room_consumer6e80_status biwn_gpu_room_consumer6e80_run(struct biwn_gpu_room_consumer6e80_bus *,struct biwn_gpu_room_consumer6e80_state *,uint32_t);
#endif
