#ifndef BIWN_SCENE_DEVICE_INITIALIZE_H
#define BIWN_SCENE_DEVICE_INITIALIZE_H
#include "biwn_world_update.h"
/* Analyst name18160..181D8. Ordered MMIO/RAM writes through the bus.
 * No emulated device implementation, private CPU frame or timing claim.
 * Status0success,1badargs,2bus error. Prior effects retained; output unchanged on error.
 */
int biwn_scene_device_initialize(struct biwn_world_bus *,uint32_t *);
#endif
