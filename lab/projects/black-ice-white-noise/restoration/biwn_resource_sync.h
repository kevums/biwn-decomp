#ifndef BIWN_RESOURCE_SYNC_H
#define BIWN_RESOURCE_SYNC_H
#include "biwn_scheduler.h"
enum biwn_sync_status {BIWN_SYNC_OK=0,BIWN_SYNC_BAD_ARGUMENT=1,
 BIWN_SYNC_BUS_ERROR=2,BIWN_SYNC_WORK_LIMIT=3,BIWN_SYNC_BAD_PC=4};
/* Original DF04 clears D0 mask bits across all OTHER ring contexts.
 * DF9C fetches its mask argument and calls DF04 with a real BSR frame.
 * body stops at the outer RTS, call consumes it. All CPU registers/flags,
 * both stack banks and private RAM frames are retained. Scan limits are
 * host guards; failures leave input CPU unchanged and prior RAM effects.
 * These routines alone do not prove real resource readiness or game use. */
enum biwn_sync_status biwn_resource_signal_body(struct biwn_world_bus *,struct biwn_task_cpu *,uint32_t);
enum biwn_sync_status biwn_resource_signal_call(struct biwn_world_bus *,struct biwn_task_cpu *,uint32_t);
/* DF8C loads its argument, saves eleven registers and TRAP4-waits.
 * DEF6 writes the current context's wait mask, then enters DE08 scheduler.
 * wait may switch to another task; wait_dispatch stops after source RTE,
 * wait also restores a selected warm DF66/DF96 continuation through RTS.
 * User/supervisor exception-frame and vector restrictions follow scheduler.
 * No interrupts, hardware timing or whole-game readiness claim. */
enum biwn_scheduler_status biwn_resource_wait(struct biwn_world_bus *,struct biwn_task_cpu *,uint32_t);
enum biwn_scheduler_status biwn_resource_wait_dispatch(struct biwn_world_bus *,struct biwn_task_cpu *,uint32_t);
#endif
