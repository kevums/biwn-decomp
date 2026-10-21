#ifndef BIWN_MUSIC_STOP_CPU_H
#define BIWN_MUSIC_STOP_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_music_stop_cpu_status {BIWN_MUSIC_STOP_CPU_OK=0,BIWN_MUSIC_STOP_CPU_BAD_ARGUMENT=1,
 BIWN_MUSIC_STOP_CPU_BUS_ERROR=2,BIWN_MUSIC_STOP_CPU_SERVICE_ERROR=3,
 BIWN_MUSIC_STOP_CPU_WORK_LIMIT=4,BIWN_MUSIC_STOP_CPU_BAD_RETURN=5,
 BIWN_MUSIC_STOP_CPU_YIELDED=6,BIWN_MUSIC_STOP_CPU_BAD_PC=7};
/* Source E9EC writes command1/CPU interrupt and polls EA08.
 * Full source CPU/stackbanks/private JSR frame. DSP acknowledgement is
 * required from a declared source DSP provider; no mailbox completion script
 * or original CPU instruction calls in this translation. Body stops before
 * outer RTS; call consumes it. Generation alone is not verification. */
enum biwn_music_stop_cpu_status biwn_music_stop_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_music_stop_cpu_status biwn_music_stop_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
