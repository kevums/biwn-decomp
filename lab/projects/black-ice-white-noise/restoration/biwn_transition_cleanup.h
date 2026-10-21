#ifndef BIWN_TRANSITION_CLEANUP_H
#define BIWN_TRANSITION_CLEANUP_H
#include "biwn_world_update.h"
/* Analyst labels for six complete original CPU functions. All nested calls
 * within this group are implemented here, with no dependency callback.
 * Limits/errors are added host behavior, retaining earlier stores while
 * leaving output D0 unchanged on failure. No arbitrary pointer validation,
 * physical hardware, asynchronous access or full CCR contract is implied.
 */
enum biwn_cleanup_status { BIWN_CLEANUP_OK=0,BIWN_CLEANUP_BAD_ARGUMENT=1,
    BIWN_CLEANUP_LIMIT=2,BIWN_CLEANUP_BUS_ERROR=3 };
enum biwn_cleanup_status biwn_cleanup_release_texture(struct biwn_world_bus *,uint16_t,uint32_t,uint32_t *);
enum biwn_cleanup_status biwn_cleanup_release_room(struct biwn_world_bus *,uint32_t,uint32_t,uint32_t,uint32_t *);
enum biwn_cleanup_status biwn_cleanup_release_region(struct biwn_world_bus *,uint32_t,uint32_t,uint32_t,uint32_t *);
enum biwn_cleanup_status biwn_cleanup_free_handle(struct biwn_world_bus *,uint32_t,uint32_t,uint32_t,uint32_t *);
enum biwn_cleanup_status biwn_cleanup_reset_rooms(struct biwn_world_bus *,uint32_t,uint32_t,uint32_t *);
enum biwn_cleanup_status biwn_cleanup_reset_region(struct biwn_world_bus *,uint32_t,uint32_t,uint32_t *);
#endif
