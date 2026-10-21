#ifndef BIWN_MOVIE_TRAP_H
#define BIWN_MOVIE_TRAP_H
#include "biwn_scheduler.h"
/* Direct user-mode TRAP0 at D414, then source DE08 dispatcher through RTE.
 * Save only its actual six-byte exception frame, with return PC D416.
 * No DF60 wrapper/MOVEM frame is introduced. Stop at the selected context
 * PC; a selected warm wrapper must subsequently resume its own source code.
 * Source user-mode, no trace/external IRQ/cycle timing. Earlier bus effects
 * survive host errors; CPU structure commits only on success. */
enum biwn_scheduler_status biwn_movie_trap_dispatch(struct biwn_world_bus *,struct biwn_task_cpu *,uint32_t);
#endif
