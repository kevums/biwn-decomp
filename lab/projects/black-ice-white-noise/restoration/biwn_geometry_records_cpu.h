#ifndef BIWN_GEOMETRY_RECORDS_CPU_H
#define BIWN_GEOMETRY_RECORDS_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_geometry_records_cpu_status {BIWN_GEOMETRY_RECORDS_CPU_OK=0,
 BIWN_GEOMETRY_RECORDS_CPU_BAD_ARGUMENT=1,BIWN_GEOMETRY_RECORDS_CPU_BUS_ERROR=2,
 BIWN_GEOMETRY_RECORDS_CPU_SERVICE_ERROR=3,BIWN_GEOMETRY_RECORDS_CPU_WORK_LIMIT=4,
 BIWN_GEOMETRY_RECORDS_CPU_BAD_RETURN=5,BIWN_GEOMETRY_RECORDS_CPU_YIELDED=6,
 BIWN_GEOMETRY_RECORDS_CPU_BAD_PC=7};
/* Full CPU/source-frame record builder170A0 plus E220/E098 submission.
 * body stops before outer RTS; call consumes it. Both stack banks.
 * Actual E3E0 memory-copy body and GPU4320 math are explicit providers.
 * Builds rendering records from40actors/40static records, without bounds
 * checks absent from source. Use valid finite input/handle/buffer fixtures.
 * No runtime instruction decode/original CPU calls or whole3Dviewport claim. */
enum biwn_geometry_records_cpu_status biwn_geometry_records_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_geometry_records_cpu_status biwn_geometry_records_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
