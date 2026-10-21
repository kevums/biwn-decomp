#ifndef BIWN_RESOURCES_H
#define BIWN_RESOURCES_H
#include "biwn_world_update.h"
enum biwn_resource_status {BIWN_RESOURCE_OK=0,BIWN_RESOURCE_BAD_ARGUMENT=1,
 BIWN_RESOURCE_BUS_ERROR=2,BIWN_RESOURCE_DEPENDENCY_ERROR=3,BIWN_RESOURCE_WORK_LIMIT=4};
/* Complete source callers 1AF04..1B002,1B002..1B044,1B044..1B154,
 * 1AA40..1AADE. Logical raw stack args and full D0; preserve reads/writes
 * and explicit nested dependencies. These functions do not implement BIOS
 * CD I/O or scheduler/task signaling. Private CPU stack/CCR and other
 * caller-saved registers are excluded. Budget/errors are host behavior;
 * prior effects remain and out_D0 stays unchanged on error.
 * Texture mode1 needs a mapped four-byte virtual private scratch location,
 * corresponding to original A6-4; source loader receives its address.
 */
enum biwn_resource_status biwn_resource_get(struct biwn_world_bus *,uint16_t,uint32_t,uint32_t *);
enum biwn_resource_status biwn_resource_release(struct biwn_world_bus *,uint16_t,uint32_t,uint32_t *);
enum biwn_resource_status biwn_resource_load(struct biwn_world_bus *,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t *);
/* Experimental explicit variant matching the byte-checked18byte1B0EE
 * word-aligned scan repair. Sixteen consecutive matching longwords and
 * payload bound checks retained. Original entry above keeps source behavior.
 * This is not selected automatically by existing callers. */
enum biwn_resource_status biwn_resource_load_word_scan(struct biwn_world_bus *,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t *);
enum biwn_resource_status biwn_resource_textures(struct biwn_world_bus *,uint16_t,uint32_t,uint32_t *);
#endif
