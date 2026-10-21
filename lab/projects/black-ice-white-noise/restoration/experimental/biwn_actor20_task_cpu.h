#ifndef BIWN_ACTOR20_TASK_CPU_H
#define BIWN_ACTOR20_TASK_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_actor20_task_cpu_status {BIWN_ACTOR20_TASK_CPU_OK=0,BIWN_ACTOR20_TASK_CPU_BAD_ARGUMENT=1,
 BIWN_ACTOR20_TASK_CPU_BUS_ERROR=2,BIWN_ACTOR20_TASK_CPU_SERVICE_ERROR=3,
 BIWN_ACTOR20_TASK_CPU_WORK_LIMIT=4,BIWN_ACTOR20_TASK_CPU_BAD_RETURN=5,
 BIWN_ACTOR20_TASK_CPU_YIELDED=6,BIWN_ACTOR20_TASK_CPU_BAD_PC=7};
/* SourceEC20..ED4E type20actor scan/lifecycle task. Scans40records
 * at49D6C,stride206; initializes/updates type20 through declared
 * 101E0/10252/1404C/EB04/13C9A/resource/sound helper interfaces.
 * Real source privateframes/stackbanks/yields. Generation is not
 * verification of lifecycle/helpers/audio/game/globaltiming. */
enum biwn_actor20_task_cpu_status biwn_actor20_task_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_actor20_task_cpu_status biwn_actor20_task_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
