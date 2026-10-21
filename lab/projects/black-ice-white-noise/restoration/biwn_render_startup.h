#ifndef BIWN_RENDER_STARTUP_H
#define BIWN_RENDER_STARTUP_H
#include "biwn_render_loop.h"
#include "biwn_task_create.h"
/* Startup caller [17C40,17DC2), followed by existing17DC2 render loop.
 * Full task caller control flow, not its opaque startup/GPU services.
 * Retained display-list args and grouped16task-creation calls use original
 * virtual stack layout. Other services receive JSR-entry CPU and stack,
 * return at the same SP, and follow original callee-save ABI. Caller-saved
 * helper outputs needed by later code must be supplied by their adapters.
 * Added host failures retain bus effects and leave caller CPU unchanged.
 */
enum biwn_startup_status {BIWN_STARTUP_OK=0,BIWN_STARTUP_BAD_ARGUMENT=1,
 BIWN_STARTUP_BUS_ERROR=2,BIWN_STARTUP_SERVICE_ERROR=3,BIWN_STARTUP_BAD_RETURN=4};
enum biwn_startup_status biwn_render_startup(struct biwn_world_bus *,struct biwn_task_cpu *,
 biwn_render_service,void *);
#endif
