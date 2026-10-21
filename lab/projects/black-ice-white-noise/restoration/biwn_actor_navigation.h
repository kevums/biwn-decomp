#ifndef BIWN_ACTOR_NAVIGATION_H
#define BIWN_ACTOR_NAVIGATION_H
#include "biwn_scheduler.h"
enum biwn_actor_navigation_status {
 BIWN_ACTOR_NAVIGATION_OK=0, BIWN_ACTOR_NAVIGATION_BAD_ARGUMENT=1,
 BIWN_ACTOR_NAVIGATION_BUS_ERROR=2, BIWN_ACTOR_NAVIGATION_BAD_TABLE=3
};
/* Execute F368,13F12,13F7C or13FEA through its final RTS instruction boundary.
 * PC identifies the RTS, A7 still points to the caller's return address.
 * Full register/SR effects, internal save slots and bus access order retained.
 * The caller performs RTS. No geometry search, movement or scheduler runs here.
 * Errors retain earlier RAM effects but leave caller CPU unchanged. Inline
 * tables may select only their four original destinations; others are host
 * errors, not emulated arbitrary jumps. User mode only, no exceptions/timing. */
enum biwn_actor_navigation_status biwn_actor_navigation_body(
 struct biwn_world_bus *, struct biwn_task_cpu *);
/* Complete function call, including RTS reading its return PC and advancing
 * user A7/USP by four. Uses the same body; errors leave caller CPU unchanged. */
enum biwn_actor_navigation_status biwn_actor_navigation_call(
 struct biwn_world_bus *, struct biwn_task_cpu *);
#endif
