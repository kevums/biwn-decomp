#ifndef BIWN_GAME_FIRSTBOOT_GPU_H
#define BIWN_GAME_FIRSTBOOT_GPU_H
#include <stdint.h>
struct biwn_game_firstboot_GPU_bus {
 int (*read8)(void *,uint32_t,uint8_t *);
 int (*read16)(void *,uint32_t,uint16_t *);
 int (*read32)(void *,uint32_t,uint32_t *);
 int (*write16)(void *,uint32_t,uint16_t);
 int (*write32)(void *,uint32_t,uint32_t);
 void (*observe_PC)(void *,uint32_t);
 void *context;
};
struct biwn_game_firstboot_GPU_state {
 uint32_t registers[2][32],pc,z,c,n;
 uint32_t matrix_control,matrix_pointer,division_control,remainder,instructions;
 uint32_t accumulator,hidata,flags,data_organization,control,active_bank;
 uint8_t local_RAM[4096];
};
enum biwn_game_firstboot_GPU_status {BIWN_GAME_FIRSTBOOT_GPU_OK=0,
 BIWN_GAME_FIRSTBOOT_GPU_BAD_ARGUMENT=1,BIWN_GAME_FIRSTBOOT_GPU_BUS_ERROR=2,
 BIWN_GAME_FIRSTBOOT_GPU_BAD_PC=3,BIWN_GAME_FIRSTBOOT_GPU_WORK_LIMIT=4,
 BIWN_GAME_FIRSTBOOT_GPU_BAD_DELAY=5};
/* Source game180000 loader GPU initialization/RLE/object-list plus
 * selected poll/shutdown blocks. Fixed observed code addresses, data tables
 * stay data. Supplied exact boot payload/inherited GPU/bus state. Stops at
 * caller-supplied PC. No runtime decoder or original GPU execution.
 * Frame timing/VCOUNT, CPU/BIOS/controller/complete firmware boot separate. */
enum biwn_game_firstboot_GPU_status biwn_game_firstboot_GPU_run(struct biwn_game_firstboot_GPU_bus *,struct biwn_game_firstboot_GPU_state *,uint32_t,uint32_t);
#endif
