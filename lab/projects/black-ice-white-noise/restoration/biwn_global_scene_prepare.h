#ifndef BIWN_GLOBAL_SCENE_PREPARE_H
#define BIWN_GLOBAL_SCENE_PREPARE_H
#include <stddef.h>
#include "biwn_world_update.h"
/* Analyst interface for complete11AD4..11B4A caller. FullD0 and external
 * bus effects/call arguments only; otherCPU registers/CCR/private stack/
 * timing excluded. Calls10968(word1,word7),11384(),10BA4(),1142E(),10734().
 * The10BA4 dependency may execute the separately verified readable C body.
 * Status0success,1badarguments,2buserror,3dependencyerror. Prior effects
 * remain on errors; out_D0 changes only on success. */
int biwn_global_scene_prepare(struct biwn_world_bus *,uint32_t,uint32_t *);
#endif
