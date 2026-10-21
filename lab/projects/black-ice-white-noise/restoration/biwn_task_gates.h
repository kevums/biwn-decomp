#ifndef BIWN_TASK_GATES_H
#define BIWN_TASK_GATES_H
#include "biwn_world_update.h"
/* Logical public effects of DF22 (pause peers) and DF3E (resume peers).
 * C0920 is the current task; each task's +0 points to the next ring node;
 * +34 is its unsigned pause nesting counter. The current task is excluded.
 * D0 is unchanged. Private A0/A1, CCR, stack, interrupts and timing excluded.
 * max_nodes bounds other nodes processed, with no callback for the next node
 * after exhaustion. Host errors retain prior effects and leave out_d0 intact.
 * Resume performs the original TST read and, when nonzero, a separate RMW
 * read before decrement: changing bus reads must not be collapsed.
 */
enum biwn_task_gates_status { BIWN_TASK_GATES_OK=0,
 BIWN_TASK_GATES_BAD_ARGUMENT=1, BIWN_TASK_GATES_BUS_ERROR=2,
 BIWN_TASK_GATES_LIMIT=4 };
int biwn_task_pause_others(struct biwn_world_bus *,uint32_t max_nodes,
 uint32_t incoming_d0,uint32_t *out_d0);
int biwn_task_resume_others(struct biwn_world_bus *,uint32_t max_nodes,
 uint32_t incoming_d0,uint32_t *out_d0);
#endif
