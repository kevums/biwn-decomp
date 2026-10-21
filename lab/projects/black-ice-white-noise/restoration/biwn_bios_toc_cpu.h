#ifndef BIWN_BIOS_TOC_CPU_H
#define BIWN_BIOS_TOC_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_bios_toc_cpu_status {BIWN_BIOS_TOC_CPU_OK=0,BIWN_BIOS_TOC_CPU_BAD_ARGUMENT=1,
 BIWN_BIOS_TOC_CPU_BUS_ERROR=2,BIWN_BIOS_TOC_CPU_SERVICE_ERROR=3,
 BIWN_BIOS_TOC_CPU_WORK_LIMIT=4,BIWN_BIOS_TOC_CPU_BAD_RETURN=5,
 BIWN_BIOS_TOC_CPU_YIELDED=6,BIWN_BIOS_TOC_CPU_BAD_PC=7};
/* Actual BIOS305A TOC collection with390E DSA helper. Source clears
 * caller1KB, reads session/track tagged replies, computes MSF lengths,
 * preserves MOVEM/private BSR frames and reports3E00 status. Caller
 * supplies writable1KB and firmware image; bus supplies responses/timing.
 * Fixed source blocks, no runtime decoding/original CPU calls. Body
 * stops before outerRTS; call consumes it. Firmware boot separate. */
enum biwn_bios_toc_cpu_status biwn_bios_toc_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_bios_toc_cpu_status biwn_bios_toc_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
