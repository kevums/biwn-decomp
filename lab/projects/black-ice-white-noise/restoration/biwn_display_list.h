#ifndef BIWN_DISPLAY_LIST_H
#define BIWN_DISPLAY_LIST_H
#include "biwn_world_update.h"
/* Complete185B2..18854, including10bytes of jump-table data. Analyst label
 * display-list builder. Three passes over36byte records ending with type4.
 * links is bounded host workspace replacing the original private stack
 * table. Only valid table references/finite declared record lists are
 * supported; arbitrary private-stack aliases are excluded. Fixed link
 * origin776F0 is preserved independently of output argument.
 * Host errors retain prior bus/workspace effects; out_D0 stays unchanged.
 */
enum biwn_display_status {BIWN_DISPLAY_OK=0,BIWN_DISPLAY_BAD_ARGUMENT=1,
 BIWN_DISPLAY_BUS_ERROR=2,BIWN_DISPLAY_WORK_LIMIT=3,BIWN_DISPLAY_BAD_LINK=4};
enum biwn_display_status biwn_display_list(struct biwn_world_bus *,uint32_t,uint32_t,
 uint32_t *,uint32_t,uint32_t,uint32_t *);
#endif
