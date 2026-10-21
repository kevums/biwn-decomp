#ifndef BIWN_ACTOR_GROUP_NATIVE_API_H
#define BIWN_ACTOR_GROUP_NATIVE_API_H
#include <stdint.h>
/* Coordinator-supplied memory I/O and source-owned C ABI only.
 * Original logical WORD arguments are zero-extended LONGs in args.
 * The M68000 bus handles24bit address resolution; fields are two-byte aligned.
 * This ABI does not expose original caller-saved registers or SR. */
static inline uint8_t ag_r8(uint32_t a){return *(volatile uint8_t *)a;}
static inline uint16_t ag_r16(uint32_t a){return *(volatile uint16_t *)a;}
static inline uint32_t ag_r32(uint32_t a){return *(volatile uint32_t *)a;}
static inline void ag_w8(uint32_t a,uint8_t v){*(volatile uint8_t *)a=v;}
static inline void ag_w16(uint32_t a,uint16_t v){*(volatile uint16_t *)a=v;}
static inline void ag_w32(uint32_t a,uint32_t v){*(volatile uint32_t *)a=v;}
enum {AG_OK=0,AG_BAD_ARGUMENT=1,AG_UNSUPPORTED_DISPATCH=5};
int biwn_actor_group_invoke(uint32_t entry,const uint32_t *args,uint32_t incoming_D0,uint32_t *out);
__attribute__((noinline,used,externally_visible))
int biwn_actor_group_call(void *context,uint32_t target,const uint32_t *args,uint32_t n,uint32_t *out);
/* This helper boundary remains a prescribed service in the component test.
 * Its status and full original D0 are separate; *out contains incoming D0. */
int biwn_actor_external_call(uint32_t target,const uint32_t *args,uint32_t n,uint32_t *out);
#endif
