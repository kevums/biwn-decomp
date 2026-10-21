#ifndef BIWN_GEOMETRY_CPU_H
#define BIWN_GEOMETRY_CPU_H
#include "biwn_geometry.h"
#include "biwn_scheduler.h"
/* Full CPU/private-frame interface for already counted1028E/102C4/1039C/10652.
 * Body stops at final RTS, call performs RTS. Raw signed indexes, source
 * rereads, word shifts and partial D0 results remain. No nested services.
 * scan_limit bounds102C4 only; zero is rejected for that entry. User mode,
 * no original exceptions/interrupts/tracing/timing or arbitrary code aliases.
 * Host errors retain RAM effects and leave caller CPU unchanged. */
enum biwn_geometry_status biwn_geometry_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,uint32_t);
enum biwn_geometry_status biwn_geometry_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,uint32_t);
#endif
