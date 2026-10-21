#ifndef BIWN_DECK_PLANE_LAYOUT_H
#define BIWN_DECK_PLANE_LAYOUT_H
#include "../deck-scene-source/deck-scene-contract.h"
/* Complete110D4..11384 including all six plane layouts and outer RTS.
 * Body stops at the selected original RTS; adapter consumes it.
 * Instruction bytes and the six-word jump table11104..11110 are immutable.
 * RAM aliases among source, destination and caller arguments are permitted;
 * errors leave supplied CPU unchanged but retain completed RAM writes.
 * MMIO, asynchronous mutation, IRQ and timing are outside this host contract.
 */
void biwn_plane_layout_body(struct biwn_deck_context *);
int biwn_plane_layout_call(struct biwn_world_bus *,struct biwn_task_cpu *);
#endif
