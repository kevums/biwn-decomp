#ifndef BIWN_TARGETING_CPU_H
#define BIWN_TARGETING_CPU_H
#include "biwn_world_cpu.h"
/* Full user-task20820 caller, including eight local bytes, eleven saved
 * registers and actual helper argument/JSR frames. Providers execute
 * 13440/E540/E588 bodies up to RTS. body stops at20A9A; call executes RTS.
 * Host errors retain prior RAM effects and leave input CPU unchanged. */
enum biwn_world_cpu_status biwn_targeting_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_world_cpu_service,void *);
enum biwn_world_cpu_status biwn_targeting_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_world_cpu_service,void *);
#endif
