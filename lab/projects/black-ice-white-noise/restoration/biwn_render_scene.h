#ifndef BIWN_RENDER_SCENE_H
#define BIWN_RENDER_SCENE_H
#include "biwn_world_update.h"
/* Original full routines: E03A..E098 clear submission, 17E0E..17F14
 * scene dispatch, 17F14..17F68 display buffer rotation. Dependencies are
 * original logical stack arguments and D0; no GPU/OP execution implied.
 * Host budgets/errors preserve earlier effects and leave out_D0 unchanged.
 * Full caller-saved registers, private stacks/CCR and concurrency excluded.
 */
enum biwn_render_status { BIWN_RENDER_OK=0,BIWN_RENDER_BAD_ARGUMENT=1,
 BIWN_RENDER_BUS_ERROR=2,BIWN_RENDER_DEPENDENCY_ERROR=3,BIWN_RENDER_WORK_LIMIT=4 };
enum biwn_render_status biwn_render_clear(struct biwn_world_bus *,uint32_t,uint32_t,uint32_t);
enum biwn_render_status biwn_render_rotate(struct biwn_world_bus *,uint32_t,uint32_t *);
enum biwn_render_status biwn_render_scene(struct biwn_world_bus *,uint32_t,uint32_t,uint32_t *);
#endif
