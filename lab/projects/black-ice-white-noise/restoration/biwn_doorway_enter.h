#ifndef BIWN_DOORWAY_ENTER_H
#define BIWN_DOORWAY_ENTER_H
#include "biwn_world_update.h"
/* Readable source10430 body: fullD0 and ordered public bus effects only.
 * Original private stack, A0/A1/D1 clobbers, CCR and timing are excluded.
 * Invalid source directions retain incomingD1/D3 low words for the key check.
 * Added host errors retain prior writes and leave out_D0 unchanged.
 */
enum biwn_portal_status { BIWN_PORTAL_OK=0, BIWN_PORTAL_BAD_ARGUMENT=1,
                         BIWN_PORTAL_BUS_ERROR=2 };
enum biwn_portal_status biwn_doorway_enter(struct biwn_world_bus *bus,
    uint32_t object, uint16_t door_index, uint16_t direction,
    uint32_t incoming_D1, uint32_t incoming_D3, uint32_t *out_D0);
#endif
