#ifndef BIWN_RNG_H
#define BIWN_RNG_H
#include "biwn_world_update.h"
#include "biwn_signed_division.h"
/* Analyst API for original1A6E0..1A91E and signed-remainder wrapperE60A.
 * Logical raw stack args: words zero-extended in bus.call. Keep all original
 * dependency calls (including calls among RNG routines) visible through
 * bus.call; its in/out value is original fullD0. E588/E60A/E540 each have
 * two long args;1A87A one word;1A8C6 one long;1A7F4 no args.
 * Selectors are raw words, not an added validated/clamped array index.
 * Preserve every external read/write width/order, including memory RMW.
 * Use unsigned intermediates for wrapped arithmetic; no signed-overflow or
 * signed-left-shift undefined behavior. Word ASR is signed at16bits.
 * Only fill has a work budget: nonzero required, consumed once per loop.
 * Host errors retain prior effects, leave out_D0 unchanged. Private CPU
 * stack/caller-saved registers exceptfullD0/CCR are outside this interface.
 * Remainder delegates to existing biwn_signed_division; zero is a host
 * dependency error, not emulation of original divide exception.
 */
enum biwn_rng_status {BIWN_RNG_OK=0,BIWN_RNG_BAD_ARGUMENT=1,
 BIWN_RNG_BUS_ERROR=2,BIWN_RNG_DEPENDENCY_ERROR=3,BIWN_RNG_WORK_LIMIT=4};
/* Needed bus callbacks by body: init=call;select=read16/write16;
 * seed=write32/call;fill=read32/write32/call;current=read16/read32/write32/call;
 * indexed=read32/write32/call;get=read16/read32;set=read16/write32. */
/* Original 1A6E0. */
enum biwn_rng_status biwn_rng_init(struct biwn_world_bus *,uint32_t,uint32_t *);
/* Original 1A87A. */
enum biwn_rng_status biwn_rng_select(struct biwn_world_bus *,uint16_t,uint32_t,uint32_t *);
/* Original 1A8C6. */
enum biwn_rng_status biwn_rng_seed(struct biwn_world_bus *,uint32_t,uint32_t *);
/* Original 1A7F4. */
enum biwn_rng_status biwn_rng_fill(struct biwn_world_bus *,uint32_t,uint32_t *);
/* Original 1A6F8. */
enum biwn_rng_status biwn_rng_current(struct biwn_world_bus *,uint32_t *);
/* Original 1A77C. */
enum biwn_rng_status biwn_rng_indexed(struct biwn_world_bus *,uint16_t,uint32_t *);
/* Original 1A8E2. */
enum biwn_rng_status biwn_rng_get(struct biwn_world_bus *,uint32_t *);
/* Original 1A8F8. */
enum biwn_rng_status biwn_rng_set(struct biwn_world_bus *,uint32_t,uint32_t,uint32_t *);
/* Original E60A. */
enum biwn_rng_status biwn_rng_remainder(uint32_t,uint32_t,uint32_t *);
#endif
