#ifndef BIWN_DECK_INPUT_SOURCE_H
#define BIWN_DECK_INPUT_SOURCE_H
#include "../deck-scene-source/deck-scene-contract.h"
/* Complete original 11B4C..11D1A caller. Controller poll and record/texture
 * helpers remain explicit services. This source does not read a physical pad.
 * CPU flags/private frames are retained; no instruction decoding or PC loop.
 * Added host errors retain RAM effects and leave the input CPU unchanged. */
int biwn_deck_input_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_world_cpu_service,void *,uint32_t);
int biwn_deck_input_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_world_cpu_service,void *,uint32_t);
#endif
