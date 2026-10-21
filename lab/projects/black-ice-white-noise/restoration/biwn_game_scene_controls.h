#ifndef BIWN_GAME_SCENE_CONTROLS_H
#define BIWN_GAME_SCENE_CONTROLS_H
#include "biwn_game_controls.h"
/* Selectable linked dispatcher with readable20F78scene setup in addition to
 * the existing controls/cleanup/display bodies. No CPU fallback.
 * display_scratch follows biwn_game_controls_with_scratch; stream_scratch is
 * a separate mapped private four-byte texture handle. word_scan is0or1 and
 * explicitly selects the experimental loader repair. Scene nested loops
 * retain a32768step host bound. Firmware, scheduler and device services
 * described by biwn_scene_stream remain external, as do other dispatcher
 * services and equipment-cache loader/wait/wake boundaries. No full game,
 * interrupt handling, CPU ABI or cycle-timing claim is made by this API.
 */
enum biwn_dispatch_status biwn_game_scene_controls(struct biwn_world_bus *,
 biwn_input_write8,uint32_t display_scratch,uint32_t stream_scratch,
 uint32_t word_scan,uint32_t loop_budget,uint32_t incoming_D0,uint32_t *out_D0);
#endif
