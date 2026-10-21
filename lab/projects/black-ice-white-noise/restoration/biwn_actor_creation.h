#ifndef BIWN_ACTOR_CREATION_H
#define BIWN_ACTOR_CREATION_H
#include "biwn_world_update.h"
typedef int (*biwn_actor_write8)(void *,uint32_t,uint8_t);
enum biwn_actor_status {BIWN_ACTOR_OK=0,BIWN_ACTOR_BAD_ARGUMENT=1,
 BIWN_ACTOR_BUS_ERROR=2,BIWN_ACTOR_DEPENDENCY_ERROR=3,BIWN_ACTOR_WORK_LIMIT=4,
 BIWN_ACTOR_UNSUPPORTED_DISPATCH=5};
/* Complete callers13AE0,134DC,137E0 andindoor position10520/105DA.
 * Raw logical args: dispatcher/static [id,x,yword,z,headingword]; actor init
 * [id,slotword,x,yword,z,headingword]; positions[object]. Nested helpers
 * are bus calls. Inline jump tables are read through the bus and mapped to
 * original known handlers; unsupported targets return an explicit host error.
 * Private stack/CCR/othercaller-saved regs excluded, fullD0/incominghelperD0
 * retained. Errors preserve earlier effects andleave output unchanged. */
enum biwn_actor_status biwn_actor_service(struct biwn_world_bus *,biwn_actor_write8,
 uint32_t,const uint32_t *,uint32_t,uint32_t,uint32_t,uint32_t *);
#endif
