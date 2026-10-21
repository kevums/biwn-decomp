#ifndef BIWN_FACE_COORDINATES_H
#define BIWN_FACE_COORDINATES_H
#include "biwn_world_update.h"
/* Analyst name for complete 110D4..11382. source points to a word index,
 * destination receives twelve coordinate words at offsets 24..3A (hex).
 * Face selects the original six immutable jump-table entries; code/table
 * reads are excluded from the logical data bus. Preserve data rereads even
 * when source and destination alias. Full D0 returned; CCR, other registers,
 * private stack and timing excluded. Status 0 success, 1 arguments, 2 bus.
 * Retain prior writes and leave out_D0 unchanged on host error. */
int biwn_face_coordinates(struct biwn_world_bus *,uint32_t source,
                          uint32_t destination,uint16_t face,uint32_t *out_D0);
#endif
