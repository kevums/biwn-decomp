#ifndef BIWN_CD_CPU_H
#define BIWN_CD_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_cd_cpu_status {BIWN_CD_CPU_OK=0,BIWN_CD_CPU_BAD_ARGUMENT=1,
 BIWN_CD_CPU_BUS_ERROR=2,BIWN_CD_CPU_SERVICE_ERROR=3,BIWN_CD_CPU_WORK_LIMIT=4,
 BIWN_CD_CPU_BAD_RETURN=5,BIWN_CD_CPU_YIELDED=6,BIWN_CD_CPU_BAD_PC=7,
 BIWN_CD_CPU_DIVIDE_ZERO=8};
/* Fixed source-specific CPU blocks: D1E0 division, D206 offset/MSF,
 * D2F0 start and D306 stop. Body stops at outer RTS (or BIOS tail RTS);
 * call consumes it. D1E0 nested calls execute through the provider.
 * BIOS303C/3042 remain explicit providers, not reconstructed firmware.
 * Zero divisor returns host status8, not a reproduced CPU exception.
 * DIVU overflow N/Z are architecturally undefined; subsequent source
 * instructions replace them before return. No asynchronous loading,
 * hardware timing or full-game claim. No runtime CPU instruction decode. */
enum biwn_cd_cpu_status biwn_cd_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_cd_cpu_status biwn_cd_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
