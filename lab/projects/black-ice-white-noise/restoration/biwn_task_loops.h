#ifndef BIWN_TASK_LOOPS_H
#define BIWN_TASK_LOOPS_H
#include "biwn_scheduler.h"
/* Three original task loops: world [1A544,1A552), idle [F360,F368) and
 * idle [F880,F888). One host step performs one loop instruction/call.
 * The body callback runs reconstructed world-update C and restores virtual
 * A7 to its entry value. World-update caller-saved registers/CCR remain
 * outside that component's contract; the dispatcher must state this limit.
 * A yield returns the selected continuation and can change the active task.
 * A full CPU world callback may return6 atDF60 to suspend within its input
 * dispatcher; frames remain intact and the actual scheduler runs. Input
 * continuation is driven by its own interface; PC1A26C resumes the world
 * callback after the dispatcher RTS without pushing a second world frame.
 */
typedef int (*biwn_task_world_body)(void *,struct biwn_world_bus *,struct biwn_task_cpu *);
enum biwn_task_loop_status { BIWN_TASK_LOOP_OK=0,BIWN_TASK_LOOP_BAD_ARGUMENT=1,
    BIWN_TASK_LOOP_BUS_ERROR=2,BIWN_TASK_LOOP_BODY_ERROR=3,
    BIWN_TASK_LOOP_SCHEDULER_ERROR=4,BIWN_TASK_LOOP_UNSUPPORTED_PC=5 };
enum biwn_task_loop_status biwn_task_loop_step(struct biwn_world_bus *,struct biwn_task_cpu *,
    biwn_task_world_body,void *,uint32_t);
#endif
