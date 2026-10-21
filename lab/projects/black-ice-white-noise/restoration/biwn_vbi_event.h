#ifndef BIWN_VBI_EVENT_H
#define BIWN_VBI_EVENT_H
#include "biwn_world_cpu.h"
/* Delivered TOM IRQ2/vector64 event only; period/global timing supplied.
 * Normal68000 user/supervisor private three-word frame. Returns3 when
 * masked; no frame/state changes then. Pending device state is separate. */
int biwn_vbi_event(struct biwn_world_bus *,struct biwn_task_cpu *);
#endif
