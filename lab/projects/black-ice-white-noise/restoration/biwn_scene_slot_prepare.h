#ifndef BIWN_SCENE_SLOT_PREPARE_H
#define BIWN_SCENE_SLOT_PREPARE_H
#include "biwn_world_update.h"
/* Analyst interface to complete 11384..1142C. Logical helper110D4 args:
 * source pointer(long), destination pointer(long), face selector(word).
 * The helper can use the verified biwn_face_coordinates implementation.
 * Full D0 and data bus effects only; CCR/other registers/stack/timing excluded.
 * Status0 success,1 badargs,2 bus,3 helper; prior effects persist on errors. */
int biwn_scene_slot_prepare(struct biwn_world_bus *,uint32_t,uint32_t *);
#endif
