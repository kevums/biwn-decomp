#ifndef BIWN_DECK_GEOMETRY_FACES_H
#define BIWN_DECK_GEOMETRY_FACES_H
#include "../deck-scene-source/deck-scene-contract.h"
/* Complete1142E..11762. Body stops at11760RTS. E26C is a declared service;
 * it stops before RTS and may mutate globals/caller-saved registers. All
 * original saved-register and argument stack writes remain observable.
 * Instruction and six-word114C0jump-table bytes are immutable. Finite RAM
 * contract;MMIO/asynchronous mutation/timing are outside the host checker.
 * Added host errors retain prior RAM effects and leave input CPU unchanged.
 */
void biwn_geometry_faces_body(struct biwn_deck_context *,uint32_t);
int biwn_geometry_faces_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_world_cpu_service,void *,uint32_t,uint32_t);
#endif
