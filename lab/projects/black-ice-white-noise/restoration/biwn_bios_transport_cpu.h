#ifndef BIWN_BIOS_TRANSPORT_CPU_H
#define BIWN_BIOS_TRANSPORT_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_bios_transport_cpu_status {BIWN_BIOS_TRANSPORT_CPU_OK=0,BIWN_BIOS_TRANSPORT_CPU_BAD_ARGUMENT=1,
 BIWN_BIOS_TRANSPORT_CPU_BUS_ERROR=2,BIWN_BIOS_TRANSPORT_CPU_SERVICE_ERROR=3,
 BIWN_BIOS_TRANSPORT_CPU_WORK_LIMIT=4,BIWN_BIOS_TRANSPORT_CPU_BAD_RETURN=5,
 BIWN_BIOS_TRANSPORT_CPU_YIELDED=6,BIWN_BIOS_TRANSPORT_CPU_BAD_PC=7};
/* Actual resident BIOS303C read/seek setup and3712 TX wait,3042 I2S
 * disable and304E progress-pointer query. Source GPU transfer descriptor,
 * optional3072bit7 instruction patches and private BSR frames retained.
 * Bus/controller progression supplied; this group does not move payload
 * bytes or execute CDGPU ISR. No runtime decoding/originalCPU calls.
 * Body stops before outerRTS; call consumes it. Firmware boot separate. */
enum biwn_bios_transport_cpu_status biwn_bios_transport_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_bios_transport_cpu_status biwn_bios_transport_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
