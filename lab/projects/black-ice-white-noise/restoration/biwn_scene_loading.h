#ifndef BIWN_SCENE_LOADING_H
#define BIWN_SCENE_LOADING_H
#include "biwn_world_update.h"
enum biwn_scene_status {BIWN_SCENE_OK=0,BIWN_SCENE_BAD_ARGUMENT=1,
 BIWN_SCENE_BUS_ERROR=2,BIWN_SCENE_DEPENDENCY_ERROR=3,BIWN_SCENE_WORK_LIMIT=4,
 BIWN_SCENE_QUEUE_FULL=5};
/* 20AA0 actor records;20B2A outdoor segment;20C16 outdoor texture fixups;
 * 20CF8 indoor segment;20D7C indoor texture fixups;20F78 scene selection.
 * Raw logical arguments: source,destination,word length for segment entries;
 * mode in argument0 for20F78; no arguments for others. Full D0 is returned.
 * Private stack/CCR/other caller-saved registers are outside this contract.
 * Helpers remain explicit bus calls. Partial effects persist on host error;
 * output remains unchanged. Work budget bounds raw signed-word loops. */
enum biwn_scene_status biwn_scene_loading(struct biwn_world_bus *,uint32_t entry,
 uint32_t argument0,uint32_t argument1,uint16_t argument2,
 uint32_t incoming_D0,uint32_t work_budget,uint32_t *out_D0);
/* Explicit restoration option: original pending textures occupy50 words,
 * immediately followed by their count and actor pointers. Keep the first50
 * words in guest RAM, spill additional ordered IDs into caller storage, and
 * preserve the source count/texture-acquire order without overwriting actor
 * lists. This changes overflow behavior; it is not original equivalence.
 * One fresh queue spans segment parsing through texture fixups. Start with
 * zero pending count and high_water=0; ids must hold capacity words. */
struct biwn_scene_texture_queue {uint16_t *ids;uint32_t capacity,high_water;};
enum biwn_scene_status biwn_scene_loading_with_queue(struct biwn_world_bus *,uint32_t,
 uint32_t,uint32_t,uint16_t,uint32_t,uint32_t,uint32_t *,struct biwn_scene_texture_queue *);
#endif
