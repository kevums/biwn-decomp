#ifndef BIWN_OVERLAY_FORMAT_H
#define BIWN_OVERLAY_FORMAT_H
#include "biwn_overlay.h"
#include "biwn_input_dispatch.h"
/* Image-specific adapter for the two literal formats at181DA/181E9.
 * Not a reconstruction of whole1B45A/generalprintf; only output string
 * and fullD0(character count) are checked. Original formatter internal
 * scratch effects are not reproduced. All numeric arguments are words.
 */
enum biwn_overlay_status biwn_overlay_format(struct biwn_world_bus *,biwn_input_write8,
 uint32_t,uint32_t,uint16_t,uint16_t,uint16_t,uint32_t *);
#endif
