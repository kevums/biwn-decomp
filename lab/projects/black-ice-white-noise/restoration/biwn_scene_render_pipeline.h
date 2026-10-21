#ifndef BIWN_SCENE_RENDER_PIPELINE_H
#define BIWN_SCENE_RENDER_PIPELINE_H
#include "biwn_render_scene.h"
#include "biwn_input_dispatch.h"
/* Selectable linked17E0E scene draw: readable clear/dispatch/rotation and
 * GPU command protocols, generated source-specific170A0 record builder,
 * C memory copy and readable185B2 display-list packing. E148 interior
 * preparation remains an explicit outer dependency. Device callbacks own
 * GPU programs, blitter and acknowledgement. scratch is a private mapped
 * stack top with at least256 bytes below it; links is bounded host work
 * space. Logical public RAM/D0 contract, not full CPU ABI or scheduling.
 * Each component receives budget; it is not a global instruction count.
 * Host errors retain earlier effects and leave out_D0 untouched. */
int biwn_scene_render_pipeline(struct biwn_world_bus *,biwn_input_write8,
 uint32_t,uint32_t *,uint32_t,uint32_t,uint32_t,uint32_t *);
#endif
