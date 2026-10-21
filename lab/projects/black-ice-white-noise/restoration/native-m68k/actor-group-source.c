#include "biwn_actor_creation.h"

/* Experimental source-owned C ABI, not the original register/stack ABI.
 * Internal calls stay in the five-function source group. The remaining
 * original helpers use an explicit external service boundary. */
extern int biwn_actor_external_call(uint32_t, const uint32_t *, uint32_t, uint32_t *);
static int actor_read8(void *context,uint32_t address,uint8_t *out)
{(void)context;*out=*(volatile uint8_t *)address;return 0;}
static int actor_read16(void *context,uint32_t address,uint16_t *out)
{(void)context;*out=*(volatile uint16_t *)address;return 0;}
static int actor_read32(void *context,uint32_t address,uint32_t *out)
{(void)context;*out=*(volatile uint32_t *)address;return 0;}
static int actor_write8(void *context,uint32_t address,uint8_t value)
{(void)context;*(volatile uint8_t *)address=value;return 0;}
static int actor_write16(void *context,uint32_t address,uint16_t value)
{(void)context;*(volatile uint16_t *)address=value;return 0;}
static int actor_write32(void *context,uint32_t address,uint32_t value)
{(void)context;*(volatile uint32_t *)address=value;return 0;}

int biwn_actor_group_call(void *,uint32_t,const uint32_t *,uint32_t,uint32_t *);
static const struct biwn_world_bus actor_bus={
    actor_read8,actor_read16,actor_read32,actor_write16,actor_write32,
    biwn_actor_group_call,0,0
};
static int member(uint32_t entry)
{return entry==0x13ae0u||entry==0x134dcu||entry==0x137e0u||entry==0x10520u||entry==0x105dau;}

/* Keep this boundary observable in the coupling verifier even under LTO. */
__attribute__((noinline,used,externally_visible))
int biwn_actor_group_call(void *context,uint32_t target,const uint32_t *args,uint32_t n,uint32_t *out)
{
    (void)context;
    if(member(target))return biwn_actor_service((struct biwn_world_bus *)&actor_bus,
        actor_write8,target,args,n,*out,UINT32_MAX,out);
    return biwn_actor_external_call(target,args,n,out);
}

/* All logical arguments are zero-extended LONGs in args. Status is separate
 * from the complete original D0 in out. Errors retain the source API rules. */
int biwn_actor_group_invoke(uint32_t entry,const uint32_t *args,uint32_t incoming_D0,uint32_t *out)
{
    if(!member(entry))return BIWN_ACTOR_BAD_ARGUMENT;
    uint32_t n=entry==0x134dcu?6u:(entry==0x13ae0u||entry==0x137e0u)?5u:1u;
    return biwn_actor_service((struct biwn_world_bus *)&actor_bus,
        actor_write8,entry,args,n,incoming_D0,UINT32_MAX,out);
}
