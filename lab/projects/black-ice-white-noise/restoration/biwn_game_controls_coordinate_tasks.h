#ifndef BIWN_GAME_CONTROLS_COORDINATE_TASKS_H
#define BIWN_GAME_CONTROLS_COORDINATE_TASKS_H
#include "biwn_game_controls_coordinate.h"
/* Coordinate controls with actual task-ring pause/resume traversal and
 *25-room texture release, object reset and actor allocation cleanup20E8C.
 * Limits1024peers/20000cleanup iterations. DF60 context switching and
 *20F78 scene streaming remain external. Same logical bus/D0 contract and
 * private-stack/caller-saved-register/CCR/timing exclusions as controls.
 */
enum biwn_dispatch_status biwn_game_controls_coordinate_tasks_with_scratch(
 struct biwn_world_bus *,biwn_input_write8,uint32_t,uint32_t,uint32_t,uint32_t *);
#endif
