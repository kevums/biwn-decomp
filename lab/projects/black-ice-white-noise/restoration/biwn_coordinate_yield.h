#ifndef BIWN_COORDINATE_YIELD_H
#define BIWN_COORDINATE_YIELD_H
#include "biwn_coordinate_flow.h"
#include "biwn_scheduler.h"
/* Host bridge for a logical DF60 request and a real coordinate CPU frame.
 * This does not manufacture that frame from logical flow state. The host
 * supplies the actual user CPU at DF60, whose stack returns to18FAA, and
 * keeps running selected game tasks/devices after begin selects one.
 * Poll completes only when the owning task has returned to that exact
 * caller/SP with all eleven saved registers restored. Until then the
 * request stays pending. No other task's D0 may acknowledge this request.
 *
 * Zero-initialize each ticket; use it once. begin dispatches once. Repeated
 * begin is rejected before bus access. Repeated poll after completion never
 * emits another completion. Tickets contain no pointers and may be copied;
 * the host must keep a single authoritative copy to ensure exactly-once
 * service. No IRQ/cycle/device execution is added here. On scheduler error,
 * earlier bus writes remain, while caller CPU/ticket/output are unchanged;
 * host must treat that as failed work, not retry it as an untouched request.
 */
enum biwn_coordinate_yield_status {
 BIWN_COORDINATE_YIELD_PENDING=0, BIWN_COORDINATE_YIELD_COMPLETE=1,
 BIWN_COORDINATE_YIELD_BAD_ARGUMENT=2, BIWN_COORDINATE_YIELD_BAD_FRAME=3,
 BIWN_COORDINATE_YIELD_BUS_ERROR=4, BIWN_COORDINATE_YIELD_SCHEDULER_ERROR=5,
 BIWN_COORDINATE_YIELD_CONSUMED=6
};
struct biwn_coordinate_yield {
 uint64_t context,sequence;
 uint32_t phase,owner,return_sp,saved[11];
};
int biwn_coordinate_yield_begin(struct biwn_world_bus *,struct biwn_coordinate_yield *,
 const struct biwn_coordinate_request *,struct biwn_task_cpu *,uint32_t scan_limit);
int biwn_coordinate_yield_poll(struct biwn_world_bus *,struct biwn_coordinate_yield *,
 const struct biwn_task_cpu *,struct biwn_coordinate_completion *);
#endif
