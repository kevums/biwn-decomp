#ifndef BIWN_WORLD_UPDATE_H
#define BIWN_WORLD_UPDATE_H
#include <stdint.h>

/* Analyst names for the complete CPU caller [1A188,1A544).
 * Helper targets remain explicit dependencies. Args are logical original
 * stack arguments (word values zero-extended); callback returns original D0.
 * Exception: F0FA camera has two logical register seeds, lowD2/lowD3,
 * supplied explicitly rather than hidden in host caller-saved CPU state.
 * read/write callbacks preserve each original global access and its order.
 * This is not a rebuilt GPU movement/collision/entity system or whole game.
 */
typedef int (*biwn_world_read8)(void *,uint32_t,uint8_t *);
typedef int (*biwn_world_read16)(void *,uint32_t,uint16_t *);
typedef int (*biwn_world_read32)(void *,uint32_t,uint32_t *);
typedef int (*biwn_world_write16)(void *,uint32_t,uint16_t);
typedef int (*biwn_world_write32)(void *,uint32_t,uint32_t);
typedef int (*biwn_world_call)(void *,uint32_t,const uint32_t *,uint32_t,uint32_t *);
struct biwn_world_bus {
    biwn_world_read8 read8;
    biwn_world_read16 read16;
    biwn_world_read32 read32;
    biwn_world_write16 write16;
    biwn_world_write32 write32;
    biwn_world_call call;
    void *context;
    uint32_t poll_limit;
};
enum biwn_world_status { BIWN_WORLD_OK=0,BIWN_WORLD_BAD_ARGUMENT=1,
    BIWN_WORLD_BUS_ERROR=2,BIWN_WORLD_DEPENDENCY_ERROR=3,BIWN_WORLD_POLL_LIMIT=4 };
/* Host limits/errors are added behavior; prior stores and helper effects stay.
 * Private stack, full caller-saved registers and CCR are not modeled.
 * Original callee-save contract is assumed at helper boundaries.
 */
enum biwn_world_status biwn_world_update(struct biwn_world_bus *);
#endif
