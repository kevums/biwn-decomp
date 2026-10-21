#ifndef BIWN_MOVIE_CPU_H
#define BIWN_MOVIE_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_movie_cpu_status {BIWN_MOVIE_CPU_OK=0,BIWN_MOVIE_CPU_BAD_ARGUMENT=1,
 BIWN_MOVIE_CPU_BUS_ERROR=2,BIWN_MOVIE_CPU_SERVICE_ERROR=3,
 BIWN_MOVIE_CPU_WORK_LIMIT=4,BIWN_MOVIE_CPU_BAD_RETURN=5,
 BIWN_MOVIE_CPU_YIELDED=6,BIWN_MOVIE_CPU_BAD_PC=7,BIWN_MOVIE_CPU_UNIMPLEMENTED_TRAP=8,BIWN_MOVIE_CPU_DIVISION_BY_ZERO=9};
/* Fixed movie caller/state handlers, marker scan, TOC/MSF conversion,
 * debug-cart writes and E8E2/E902/E918 audio interfaces. Full registers,
 * SR and both stack banks; source pointer table remains data. body stops
 * before RTS; call consumes RTS. Nested providers retain source frames.
 * Direct D414 TRAP0 stops before execution with status6 when requested;
 * scheduler must execute its actual exception separately. Otherwise8.
 * Division-by-zero is host9, not a source exception; DIVU overflow flags
 * follow the pinned reference core (not physical undefined-flag proof).
 * No runtime decoding or original CPU calls. BIOS/progress, video GPU,
 * input and DSP clock/stop completion require explicit providers.
 * Generation alone proves no movie streaming or in-game playback. */
enum biwn_movie_cpu_status biwn_movie_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_movie_cpu_status biwn_movie_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
