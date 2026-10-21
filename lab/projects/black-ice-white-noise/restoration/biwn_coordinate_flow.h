#ifndef BIWN_COORDINATE_FLOW_H
#define BIWN_COORDINATE_FLOW_H
#include <stdint.h>
/* Resumable logical reconstruction of18E92..190B8. No callbacks, CPU steps,
 * allocation, polling loop or hidden state run inside advance(). Each call
 * accepts at most one completion and emits at most one next bus/helper
 * request. A host may leave a clock read or helper pending while other jobs
 * run. Helpers remain logical interfaces, not implied implementations.
 *
 * Host must choose a unique nonzero context per active job and execute each
 * (context,sequence) request once. NULL completion repeats the same pending
 * request without advancing or duplicating side effects. Replies must echo
 * both IDs. Wrong/stale replies leave state/output unchanged. A successful
 * reply acknowledges actual completion, not merely queued work. The host
 * owns async cancellation, scheduling, device timing and callback effects.
 *
 * Observable contract: same ordered logical data accesses, helper arguments
 * and fullD0 as the synchronous coordinate API. Other registers/CCR/private
 * CPU frame, instruction timing and live-runtime replacement are excluded.
 * Clock reads retain original unsigned wrap/comparison semantics. Exposed
 * state contains no pointers and is caller owned; do not mutate its fields
 * or reset/reuse a context while old operations remain in flight.
 */
enum biwn_coordinate_flow_status { BIWN_COORDINATE_FLOW_REQUEST=0,
 BIWN_COORDINATE_FLOW_DONE=1, BIWN_COORDINATE_FLOW_FAILED=2,
 BIWN_COORDINATE_FLOW_BAD_ARGUMENT=3, BIWN_COORDINATE_FLOW_BAD_REPLY=4,
 BIWN_COORDINATE_FLOW_ID_EXHAUSTED=5 };
enum biwn_coordinate_request_kind { BIWN_COORDINATE_READ8=1,
 BIWN_COORDINATE_READ16=2, BIWN_COORDINATE_READ32=3,
 BIWN_COORDINATE_WRITE8=4, BIWN_COORDINATE_WRITE16=5,
 BIWN_COORDINATE_WRITE32=6, BIWN_COORDINATE_CALL=7 };
struct biwn_coordinate_request {
 uint64_t context,sequence;
 uint32_t kind,address,value,argument_count,argument,incoming_d0;
};
struct biwn_coordinate_completion {
 uint64_t context,sequence;
 uint32_t value;
 int status;
};
struct biwn_coordinate_flow {
 struct biwn_coordinate_request pending;
 uint32_t magic,phase,terminal,d0,deadline;
 uint16_t cursor,x,z,digit;
 uint32_t initial_index,callback_status;
};
int biwn_coordinate_flow_begin(struct biwn_coordinate_flow *,uint64_t context,uint32_t incoming_d0);
int biwn_coordinate_flow_advance(struct biwn_coordinate_flow *,const struct biwn_coordinate_completion *,struct biwn_coordinate_request *);
/* Commits out_d0 only on DONE. On a failed callback, callback_status records
 * the host's nonzero status. Earlier externally completed effects persist. */
int biwn_coordinate_flow_result(const struct biwn_coordinate_flow *,uint32_t *out_d0);
#endif
