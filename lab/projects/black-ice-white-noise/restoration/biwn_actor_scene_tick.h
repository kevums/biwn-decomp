#ifndef BIWN_ACTOR_SCENE_TICK_H
#define BIWN_ACTOR_SCENE_TICK_H
#include "biwn_actor_pipeline.h"
#include "biwn_scene_render_pipeline.h"
enum biwn_actor_scene_status {
 BIWN_ACTOR_SCENE_OK=0,BIWN_ACTOR_SCENE_BAD_ARGUMENT=1,
 BIWN_ACTOR_SCENE_COMPONENT_ERROR=2,BIWN_ACTOR_SCENE_OTHER_CONTINUATION=3,
 BIWN_ACTOR_SCENE_EXIT_BOUNDARY=4,BIWN_ACTOR_SCENE_RENDER_ERROR=5
};
/* Advance one selected F4D8-family actor update through actual scheduling,
 * then draw through the linked scene renderer using the same bus/RAM.
 * expected_task is the selected source task address, not an actor slot.
 * Other task families/contexts require an outer dispatcher: return3 at the
 * handoff boundary rather than running or blocking them here. Return4 keeps
 * the pending DF7A removal boundary for that dispatcher. No clock/input/
 * interrupts, other task execution, GPU global-context or whole-game claim.
 * Each component gets budget. GPU/blitter/device completion is external.
 * Errors retain all earlier RAM and committed continuation effects; this
 * multi-phase operation is not transactional. out_D0 changes only on success.
 * scratch/links have the existing scene-render API requirements. */
enum biwn_actor_scene_status biwn_actor_scene_tick(struct biwn_world_bus *,
 struct biwn_task_cpu *,biwn_actor_task_write8,uint32_t expected_task,
 uint32_t scratch,uint32_t *links,uint32_t capacity,uint32_t budget,
 uint32_t incoming_D0,uint32_t *out_D0,
 biwn_actor_pipeline_observer,void *);
#endif
