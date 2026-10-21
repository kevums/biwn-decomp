#ifndef BIWN_INPUT_POLL_CPU_H
#define BIWN_INPUT_POLL_CPU_H
#include "biwn_scheduler.h"
enum biwn_input_poll_cpu_status {BIWN_POLL_CPU_OK=0,BIWN_POLL_CPU_BAD_ARGUMENT=1,BIWN_POLL_CPU_BUS_ERROR=2};
/* E4C0 complete CPU/private-stack interface. The bus supplies actual row
 * select/read device behavior; this does not validate a physical controller.
 * body stops at E53A; call additionally performs the original RTS. */
enum biwn_input_poll_cpu_status biwn_input_poll_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *);
enum biwn_input_poll_cpu_status biwn_input_poll_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *);
#endif
