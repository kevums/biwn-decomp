#ifndef BIWN_GAME_CONTROLS_COORDINATE_H
#define BIWN_GAME_CONTROLS_COORDINATE_H
#include "biwn_game_controls.h"
/* Coordinate18E92, digit1B718, raw controllerE4C0 and panel/text12620/149AE
 * execute source C in this variant. Scene20E8C/20F78 and scheduler services
 * remain external. Same logical D0/bus contract as existing controls.
 * Coordinate work has an added100000callback limit; nested errors become
 * dispatcher dependency errors with prior effects and unchanged outD0.
 * Other CPU registers/private stack, live frames and timing are excluded.
 */
enum biwn_dispatch_status biwn_game_controls_coordinate(struct biwn_world_bus *,
 biwn_input_write8,uint32_t,uint32_t,uint32_t *);
enum biwn_dispatch_status biwn_game_controls_coordinate_with_scratch(struct biwn_world_bus *,
 biwn_input_write8,uint32_t,uint32_t,uint32_t,uint32_t *);
#endif
