#ifndef BIWN_FORMATTER_CPU_H
#define BIWN_FORMATTER_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_formatter_cpu_status {BIWN_FORMATTER_CPU_OK=0,BIWN_FORMATTER_CPU_BAD_ARGUMENT=1,
 BIWN_FORMATTER_CPU_BUS_ERROR=2,BIWN_FORMATTER_CPU_SERVICE_ERROR=3,
 BIWN_FORMATTER_CPU_WORK_LIMIT=4,BIWN_FORMATTER_CPU_BAD_RETURN=5,
 BIWN_FORMATTER_CPU_YIELDED=6,BIWN_FORMATTER_CPU_BAD_PC=7,BIWN_FORMATTER_CPU_DIVIDE_ZERO=8,BIWN_FORMATTER_CPU_DIVIDE_OVERFLOW=9};
/* Static323sourceinstruction blocks for1B160character,1B1A8string,
 * 1B212numeric,1B29Cformat,1B45Avarargs and E61Cunsigned quotient /
 * E67Cremainder. Bothstackbanks; fullCPU/private/global scratch effects.
 * Services execute nested bodies up toRTS; body stops beforeouterRTS,
 * call consumesit. Embedded null/digit literals remainbus data.
 * No runtime instructiondecode or originalCPUcalls. Zero division and
 * DIVUoverflow are explicit hosterrors, not reproduced processor traps.
 * Source formatting is finite/bounded254characters, not hostprintf. */
enum biwn_formatter_cpu_status biwn_formatter_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_formatter_cpu_status biwn_formatter_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
