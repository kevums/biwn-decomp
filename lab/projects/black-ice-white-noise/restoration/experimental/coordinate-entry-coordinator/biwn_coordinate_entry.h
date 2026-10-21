#ifndef BIWN_COORDINATE_ENTRY_H
#define BIWN_COORDINATE_ENTRY_H
#include "biwn_world_update.h"
typedef int (*biwn_coordinate_write8)(void *, uint32_t, uint8_t);
/* Analyst API for original 18E92..190B8: ordered global bus accesses and
 * logical helper calls. Helpers remain external and preserve callee saves.
 * Excludes private CPU stack, other caller-saved registers/CCR and task timing.
 * max_operations counts each attempted bus/helper callback, including the
 * write8 callback. Exhaustion returns4 before the next callback. Errors
 * retain all earlier effects. No original timeout is inferred.
 * Every declared callback and nonzero budget is required before effects.
 */
enum biwn_coordinate_status { BIWN_COORDINATE_OK=0,
 BIWN_COORDINATE_BAD_ARGUMENT=1, BIWN_COORDINATE_BUS_ERROR=2,
 BIWN_COORDINATE_DEPENDENCY_ERROR=3, BIWN_COORDINATE_LIMIT=4 };
enum biwn_coordinate_status biwn_coordinate_entry(struct biwn_world_bus *,
 biwn_coordinate_write8, uint32_t max_operations);
/* Full original D0 is preserved/computed in this semantic form. On failure
 * out_d0 stays untouched; earlier public effects are retained. */
enum biwn_coordinate_status biwn_coordinate_entry_with_result(struct biwn_world_bus *,
 biwn_coordinate_write8, uint32_t max_operations, uint32_t incoming_d0,
 uint32_t *out_d0);
#endif
