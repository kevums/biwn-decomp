#ifndef BIWN_FRAME_RESOURCE_ACQUIRE_H
#define BIWN_FRAME_RESOURCE_ACQUIRE_H
#include "biwn_world_update.h"
/* Analyst name1AC68..1AE54. scratch is mapped guest A6-4,not hostmemory.
 * 0success,1badargs,2bus,3loader,4worklimit,5dividezero host guard.
 * Prior effects stay; out_D0 unchanged on any hosterror.
 */
int biwn_frame_resource_acquire(struct biwn_world_bus *,uint16_t,uint32_t,uint32_t *);
#endif
