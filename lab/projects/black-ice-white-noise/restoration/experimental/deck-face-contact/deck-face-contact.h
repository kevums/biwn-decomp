#ifndef BIWN_DECK_FACE_CONTACT_H
#define BIWN_DECK_FACE_CONTACT_H
#include "../deck-scene-source/deck-scene-contract.h"
/* Complete 1186A..11AD4 face-bound contact caller, with original pinned
 * six-entry jump table. 10C6E/10CB6 remain explicit service dependencies.
 * Body stops at outer RTS 11AD2; call also consumes it. No CPU decoding.
 * budget bounds records and helper calls. Errors retain prior RAM effects
 * and leave the input CPU unchanged. No IRQ, timing or alias guarantees. */
int biwn_deck_face_contact_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_world_cpu_service,void *,uint32_t);
int biwn_deck_face_contact_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_world_cpu_service,void *,uint32_t);
#endif
