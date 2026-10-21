#ifndef BIWN_ELEVATOR_SCENE_H
#define BIWN_ELEVATOR_SCENE_H
#include "biwn_scene_stream.h"
/* Readable1A0F8 input ->20F0Ccleanup ->20F78actual scene stream.
 * Select experimental word scan explicitly, as in biwn_scene_stream.
 * Same remaining scheduler/firmware/device/CPU ABI limits apply.
 */
int biwn_elevator_scene(struct biwn_world_bus *,biwn_actor_write8,
 uint32_t scratch,uint32_t word_scan,uint32_t budget,
 uint32_t incoming_D0,uint32_t *out_D0);
#endif
