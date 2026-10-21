#ifndef BIWN_TEXTURE_CACHE_H
#define BIWN_TEXTURE_CACHE_H
#include "biwn_world_update.h"
enum biwn_texture_status {BIWN_TEXTURE_OK=0,BIWN_TEXTURE_BAD_ARGUMENT=1,
 BIWN_TEXTURE_BUS_ERROR=2,BIWN_TEXTURE_DEPENDENCY_ERROR=3,
 BIWN_TEXTURE_WORK_LIMIT=4,BIWN_TEXTURE_DIVISION_BY_ZERO=5};
/* 1AC3C..1AC68 lookup and1AC68..1AE56 acquisition. Source raw signed-word
 * arithmetic, exact table accesses, refcount wrap, logical loader arguments
 * and incoming/returned D0. CCR/other caller-saved regs/private stack excluded.
 * Acquisition requires mapped private scratch matching original A6-4.
 * Added errors retain prior effects and leave out_D0 unchanged. Raw zero
 * divisor returns host error; original CPU exception frame is not emulated. */
enum biwn_texture_status biwn_texture_lookup(struct biwn_world_bus *,uint16_t,uint32_t,uint32_t *);
enum biwn_texture_status biwn_texture_acquire(struct biwn_world_bus *,uint16_t,uint32_t,uint32_t,uint32_t,uint32_t *);
#endif
