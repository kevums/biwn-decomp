#ifndef BIWN_ANIMATION_IMAGES_H
#define BIWN_ANIMATION_IMAGES_H
#include "biwn_world_update.h"
#include "biwn_input_dispatch.h"
enum biwn_animation_images_status {BIWN_IMAGES_OK=0,BIWN_IMAGES_BAD_ARGUMENT=1,
 BIWN_IMAGES_BUS_ERROR=2,BIWN_IMAGES_DEPENDENCY_ERROR=3,BIWN_IMAGES_WORK_LIMIT=4};
/* Analyst names for EA20..EA28 reset and EA28..EAC4 consumer. Requests hold
 * model handle, frame index, output handle and nonzero flip flag. The sprite
 * E2B8 callback receives three original long stack args and preserves its
 * D0 input/result. Reset preserves all CPU registers; its C return is host
 * status only. Consumer full D0 is separate from host status. Source widths,
 * signed queue-count comparisons and rereads stay explicit. Errors retain
 * earlier writes and preserve outputD0. Added nonzero work budget bounds
 * request processing; the original CPU routine has no timeout. */
enum biwn_animation_images_status biwn_animation_images_reset(struct biwn_world_bus *);
enum biwn_animation_images_status biwn_animation_images_consume(struct biwn_world_bus *,
 biwn_input_write8,uint32_t work_budget,uint32_t incoming_d0,uint32_t *out_d0);
#endif
