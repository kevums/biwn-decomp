#ifndef BIWN_ANIMATION_CPU_H
#define BIWN_ANIMATION_CPU_H
#include "biwn_scheduler.h"
enum biwn_animation_cpu_status {BIWN_ANIM_CPU_OK=0,BIWN_ANIM_CPU_BAD_ARGUMENT=1,
 BIWN_ANIM_CPU_BUS_ERROR=2,BIWN_ANIM_CPU_WORK_LIMIT=3,BIWN_ANIM_CPU_BAD_RETURN=4};
/* Full CPU/stack interfaces for EAC4queue and EB04update through pre-RTS;
 * call additionally executes RTS. The update uses the actual queue body.
 * Signed record/count arithmetic and caller-saved effects are retained.
 * Host errors keep RAM effects and unchanged callerCPU. A nonzero update
 * work budget bounds catch-up; not an original exception or timer source. */
enum biwn_animation_cpu_status biwn_animation_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,uint32_t);
enum biwn_animation_cpu_status biwn_animation_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,uint32_t);
#endif
