#ifndef BIWN_SCENE_RECORD_INSERT_H
#define BIWN_SCENE_RECORD_INSERT_H
#include "biwn_world_update.h"
/* Analyst name; original entry11762. No recovered original symbol. */
int biwn_scene_record_insert(struct biwn_world_bus *bus, uint16_t kind,
 uint32_t x, uint32_t y, uint32_t z, uint32_t incoming_D0, uint32_t *out_D0);
#endif
