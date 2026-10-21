#ifndef BIWN_COORDINATE_SERVICES_H
#define BIWN_COORDINATE_SERVICES_H
#include "biwn_coordinate_flow.h"
#include "biwn_coordinate_entry.h"
enum biwn_coordinate_service_status { BIWN_COORDINATE_SERVICE_COMPLETED=0,
 BIWN_COORDINATE_SERVICE_EXTERNAL=1, BIWN_COORDINATE_SERVICE_BAD_ARGUMENT=2,
 BIWN_COORDINATE_SERVICE_BUS_ERROR=3, BIWN_COORDINATE_SERVICE_BODY_ERROR=4 };
/* Execute one flow request using real readable panel/text, controller poll,
 * digit decode, room/texture/object/allocator cleanup and task pause/resume.
 * DF60/20F78 and unknown helper targets return EXTERNAL without effects or
 * output change: caller must schedule/complete them, never acknowledge a
 * queued request as finished. Input/device/clock values come from the bus.
 * The host owns exactly-once execution/caching of (context,sequence); this
 * function does not deduplicate. Call only once per request. Inner helper
 * work is bounded by20000iterations (task ring1024peers); it is synchronous
 * within this service call. Engine-level requests remain resumable. No
 * physical GPU/IRQ/clock/task execution or full CPU private ABI is implied.
 * Every callback and nonzero request IDs required before effects. On errors
 * out_value stays unchanged and prior bus/helper effects remain in place.
 */
int biwn_coordinate_service_request(struct biwn_world_bus *,biwn_coordinate_write8,
 const struct biwn_coordinate_request *,uint32_t *out_value);
#endif
