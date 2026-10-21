#ifndef BIWN_COORDINATE_YIELD_ATTACH_H
#define BIWN_COORDINATE_YIELD_ATTACH_H
#include "biwn_coordinate_yield.h"
/* Attach a request to an actual DF60/18FAA user frame without executing
 * scheduler instructions or modifying guest CPU/RAM. The host's existing
 * instruction-compatible source scheduler and device clock must then run.
 * biwn_coordinate_yield_poll emits completion only for the returned owner.
 *
 * This alternative backend avoids collapsing a scheduler operation into an
 * atomic host call when device/IRQ timing must proceed between instructions.
 * Zero-initialize the ticket, attach once, and keep one authoritative copy.
 * A native caller may issue this request at its actual DF60 boundary; that
 * alone does not install the entire logical coordinate engine in frames.
 * Required bus callback: read32. Errors preserve ticket and guest state;
 * bus reads are observable and any earlier read effects remain.
 */
int biwn_coordinate_yield_attach(struct biwn_world_bus *,struct biwn_coordinate_yield *,
 const struct biwn_coordinate_request *,const struct biwn_task_cpu *);
#endif
