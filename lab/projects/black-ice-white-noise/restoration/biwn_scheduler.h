#ifndef BIWN_SCHEDULER_H
#define BIWN_SCHEDULER_H
#include "biwn_world_update.h"
/* Analyst labels for original handler [DE08,DE5C), yield [DF60,DF6C),
 * removal handler [DEB6,DEE2) and removal trap [DF7A,DF7C).
 * Explicit CPU continuation: execution may transfer to a different task.
 * registers are D0-D7/A0-A7. USP/SSP include the active A7 bank's value.
 * Tests target M68000 six-byte exception frames, SR bits0x271f, no external
 * interrupts, tracing, cycle timing or arbitrary aliases into code/stacks.
 * Host budget/vector/bus failures keep earlier memory effects and leave the
 * caller's CPU-state structure unchanged. These are added host behaviors.
 */
struct biwn_task_cpu { uint32_t registers[16],pc,usp,ssp; uint16_t sr; };
enum biwn_scheduler_status { BIWN_SCHEDULER_OK=0,BIWN_SCHEDULER_BAD_ARGUMENT=1,
    BIWN_SCHEDULER_SCAN_LIMIT=2,BIWN_SCHEDULER_BUS_ERROR=3,BIWN_SCHEDULER_BAD_VECTOR=4 };
enum biwn_scheduler_status biwn_scheduler_dispatch(struct biwn_world_bus *,struct biwn_task_cpu *,uint32_t);
enum biwn_scheduler_status biwn_scheduler_yield(struct biwn_world_bus *,struct biwn_task_cpu *,uint32_t);
/* Restore a selected warm DF66 yield or DF96 wait continuation, including
 * its eleven saved registers and RTS. Fresh task entries are unchanged.
 * This also runs automatically after yield/removal context selection. */
enum biwn_scheduler_status biwn_scheduler_resume_saved(struct biwn_world_bus *,struct biwn_task_cpu *);
/* Removal dispatch starts supervisor-side at DEB6 and stops after RTE.
 * Removal starts user-side at DF7A and also restores a selected warm DF66
 * yield continuation. The removed task is linked onto C0924, unlinked from
 * its ring, and never has its current registers/SP/PC saved for resumption.
 * The raw game behavior requires a runnable remaining context; host scan
 * limits bound malformed/blocked rings without inventing an idle task. */
enum biwn_scheduler_status biwn_scheduler_remove_dispatch(struct biwn_world_bus *,struct biwn_task_cpu *,uint32_t);
enum biwn_scheduler_status biwn_scheduler_remove(struct biwn_world_bus *,struct biwn_task_cpu *,uint32_t);
#endif
