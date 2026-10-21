#ifndef BIWN_RENDER_LOOP_H
#define BIWN_RENDER_LOOP_H
#include "biwn_render_scene.h"
#include "biwn_scheduler.h"
/* Steady-state task continuation [17DC2,17E0E), NOT the startup at17C40.
 * Step executes through the next yield/service boundary, or the profiling
 * tail/backedge. Service callbacks receive original full CPU and JSR stack,
 * must return with entry SP and callee-save contract. Scheduler is real C.
 * Host failures retain bus effects and leave caller CPU structure unchanged.
 */
typedef int (*biwn_render_service)(void *,struct biwn_world_bus *,struct biwn_task_cpu *,uint32_t);
enum biwn_render_loop_status { BIWN_RENDER_LOOP_OK=0,BIWN_RENDER_LOOP_BAD_ARGUMENT=1,
 BIWN_RENDER_LOOP_BUS_ERROR=2,BIWN_RENDER_LOOP_SERVICE_ERROR=3,
 BIWN_RENDER_LOOP_SCHEDULER_ERROR=4,BIWN_RENDER_LOOP_UNSUPPORTED_PC=5 };
enum biwn_render_loop_status biwn_render_loop_step(struct biwn_world_bus *,struct biwn_task_cpu *,
 biwn_render_service,void *,uint32_t);
#endif
