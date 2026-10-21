#ifndef BIWN_TASK_CREATE_H
#define BIWN_TASK_CREATE_H
#include "biwn_scheduler.h"
/* Full creation subroutine [DE5C,DEB6) and stack wrapper [DF6C,DF7A).
 * Start CPU.pc at either entry. Callback accesses include logical stack
 * arguments/RTS, all list pointer rereads and original store order.
 * Zero free-list head executes ILLEGAL in the original. C returns NO_FREE,
 * does not invent an original successful return or emulate its exception
 * frame. Host failures retain prior bus effects; CPU structure unchanged.
 */
enum biwn_task_create_status {BIWN_CREATE_OK=0,BIWN_CREATE_BAD_ARGUMENT=1,
 BIWN_CREATE_BUS_ERROR=2,BIWN_CREATE_NO_FREE=3};
enum biwn_task_create_status biwn_task_create(struct biwn_world_bus *,struct biwn_task_cpu *);
/* Logical DF6C(callback,parameter) entry for readable callers. Reuses DE5C
 * body with explicit D0/D1 and a mapped four-byte private RTS slot. Other
 * private CPU registers are zero seeds, not an ABI claim; DE5C never uses
 * them for public task-list effects. Output is the actual new task address.
 * No task execution/context switch is implied. Prior effects persist on
 * error and out_D0 remains unchanged. */
enum biwn_task_create_status biwn_task_create_logical(struct biwn_world_bus *,
 uint32_t callback,uint32_t parameter,uint32_t scratch,uint32_t *out_D0);
#endif
