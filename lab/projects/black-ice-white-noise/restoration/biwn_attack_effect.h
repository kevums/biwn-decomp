#ifndef BIWN_ATTACK_EFFECT_H
#define BIWN_ATTACK_EFFECT_H
#include "biwn_world_update.h"
enum biwn_attack_status {
 BIWN_ATTACK_OK=0, BIWN_ATTACK_BAD_ARGUMENT=1,
 BIWN_ATTACK_BUS_ERROR=2, BIWN_ATTACK_DEPENDENCY_ERROR=3
};
/* Analyst API for original [0x18DF2,0x18E92). Preserve ordered external
 * accesses, word wrapping/signedness, and the final full D0. The 1A77C
 * indexed RNG remains an explicit logical bus.call with one word argument.
 * Required callbacks: read16/read32/write16/call, checked before effects.
 * On callback failure retain earlier stores and leave out_d0 untouched.
 * Original caller-saved registers, CCR/private stack and physical timing
 * are excluded. Field names/attack label are analytical, not original names.
 */
enum biwn_attack_status biwn_attack_effect(struct biwn_world_bus *,uint32_t *out_d0);
#endif
