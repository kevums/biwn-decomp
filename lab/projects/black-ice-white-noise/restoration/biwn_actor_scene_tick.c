#include "biwn_actor_scene_tick.h"

#include <stdint.h>
#include <stddef.h>

enum biwn_actor_scene_status biwn_actor_scene_tick(struct biwn_world_bus *bus,
                                                   struct biwn_task_cpu *cpu,
                                                   biwn_actor_task_write8 write8,
                                                   uint32_t expected_task,
                                                   uint32_t scratch,
                                                   uint32_t *links,
                                                   uint32_t capacity,
                                                   uint32_t budget,
                                                   uint32_t incoming_D0,
                                                   uint32_t *out_D0,
                                                   biwn_actor_pipeline_observer observer,
                                                   void *opaque)
{
    if (bus == NULL || cpu == NULL || write8 == NULL || links == NULL || out_D0 == NULL) {
        return BIWN_ACTOR_SCENE_BAD_ARGUMENT;
    }

    if (bus->read8 == NULL || bus->read16 == NULL || bus->read32 == NULL ||
        bus->write16 == NULL || bus->write32 == NULL) {
        return BIWN_ACTOR_SCENE_BAD_ARGUMENT;
    }

    if (capacity == 0 || budget == 0) {
        return BIWN_ACTOR_SCENE_BAD_ARGUMENT;
    }

    if (scratch < 256 || (scratch & 1u) != 0u) {
        return BIWN_ACTOR_SCENE_BAD_ARGUMENT;
    }

    if (expected_task == 0u || (expected_task & 1u) != 0u) {
        return BIWN_ACTOR_SCENE_BAD_ARGUMENT;
    }

    if ((cpu->sr & 0x2000u) != 0u) {
        return BIWN_ACTOR_SCENE_BAD_ARGUMENT;
    }

    uint32_t inputPC = cpu->pc;

    if (inputPC != 0xDF60u && inputPC != 0xF4D8u && inputPC != 0xF56Eu && inputPC != 0xF70Cu) {
        return BIWN_ACTOR_SCENE_OTHER_CONTINUATION;
    }

    /* Phase 1: If inputPC=DF60, call pipeline_step once */
    if (inputPC == 0xDF60u) {
        enum biwn_actor_pipeline_status st = biwn_actor_pipeline_step(bus, cpu, write8, budget, observer, opaque);
        if (st != BIWN_ACTOR_PIPELINE_OK) {
            return BIWN_ACTOR_SCENE_COMPONENT_ERROR;
        }
    }

    /* Phase 2: Read current task, validate */
    uint32_t current = 0;
    if (bus->read32(bus->context, 0xC0920u, &current) != 0) {
        return BIWN_ACTOR_SCENE_COMPONENT_ERROR;
    }

    if (current != expected_task ||
        (cpu->pc != 0xF4D8u && cpu->pc != 0xF56Eu && cpu->pc != 0xF70Cu)) {
        return BIWN_ACTOR_SCENE_OTHER_CONTINUATION;
    }

    /* Phase 3: Call pipeline_step once for actor body */
    {
        enum biwn_actor_pipeline_status st = biwn_actor_pipeline_step(bus, cpu, write8, budget, observer, opaque);
        if (st != BIWN_ACTOR_PIPELINE_OK) {
            return BIWN_ACTOR_SCENE_COMPONENT_ERROR;
        }
    }

    if (cpu->pc == 0xDF7Au) {
        return BIWN_ACTOR_SCENE_EXIT_BOUNDARY;
    }

    if (cpu->pc != 0xDF60u) {
        return BIWN_ACTOR_SCENE_OTHER_CONTINUATION;
    }

    /* Phase 4: Call pipeline_step once for actual yield/resumption */
    {
        enum biwn_actor_pipeline_status st = biwn_actor_pipeline_step(bus, cpu, write8, budget, observer, opaque);
        if (st != BIWN_ACTOR_PIPELINE_OK) {
            return BIWN_ACTOR_SCENE_COMPONENT_ERROR;
        }
    }

    /* Read current task again */
    if (bus->read32(bus->context, 0xC0920u, &current) != 0) {
        return BIWN_ACTOR_SCENE_COMPONENT_ERROR;
    }

    if (current != expected_task || cpu->pc != 0xF70Cu) {
        return BIWN_ACTOR_SCENE_OTHER_CONTINUATION;
    }

    /* Phase 5: Call scene render pipeline */
    uint32_t local_result = 0;
    int render_rc = biwn_scene_render_pipeline(bus, write8, scratch, links, capacity, budget, incoming_D0, &local_result);
    if (render_rc != 0) {
        return BIWN_ACTOR_SCENE_RENDER_ERROR;
    }

    *out_D0 = local_result;
    return BIWN_ACTOR_SCENE_OK;
}
