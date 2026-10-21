#include <stddef.h>
#include "biwn_task_gates.h"

static int biwn_task_walk(struct biwn_world_bus *bus, uint32_t max_nodes,
                          uint32_t incoming_d0, uint32_t *out_d0, int resume)
{
    uint32_t current;
    uint32_t next;
    uint32_t count;
    uint32_t val;

    if (bus == NULL || out_d0 == NULL || max_nodes == 0 ||
        bus->read32 == NULL || bus->write32 == NULL) {
        return BIWN_TASK_GATES_BAD_ARGUMENT;
    }

    if (bus->read32(bus->context, 0x000c0920u, &current) != 0) {
        return BIWN_TASK_GATES_BUS_ERROR;
    }

    if (bus->read32(bus->context, current, &next) != 0) {
        return BIWN_TASK_GATES_BUS_ERROR;
    }

    count = 0u;
    while (next != current) {
        if (count >= max_nodes) {
            return BIWN_TASK_GATES_LIMIT;
        }

        if (resume) {
            if (bus->read32(bus->context, next + 0x22u, &val) != 0) {
                return BIWN_TASK_GATES_BUS_ERROR;
            }
            if (val != 0u) {
                if (bus->read32(bus->context, next + 0x22u, &val) != 0) {
                    return BIWN_TASK_GATES_BUS_ERROR;
                }
                if (bus->write32(bus->context, next + 0x22u, val - 1u) != 0) {
                    return BIWN_TASK_GATES_BUS_ERROR;
                }
            }
        } else {
            if (bus->read32(bus->context, next + 0x22u, &val) != 0) {
                return BIWN_TASK_GATES_BUS_ERROR;
            }
            if (bus->write32(bus->context, next + 0x22u, val + 1u) != 0) {
                return BIWN_TASK_GATES_BUS_ERROR;
            }
        }

        if (bus->read32(bus->context, next, &next) != 0) {
            return BIWN_TASK_GATES_BUS_ERROR;
        }

        count++;
    }

    *out_d0 = incoming_d0;
    return BIWN_TASK_GATES_OK;
}

int biwn_task_pause_others(struct biwn_world_bus *bus, uint32_t max_nodes,
                           uint32_t incoming_d0, uint32_t *out_d0)
{
    return biwn_task_walk(bus, max_nodes, incoming_d0, out_d0, 0);
}

int biwn_task_resume_others(struct biwn_world_bus *bus, uint32_t max_nodes,
                            uint32_t incoming_d0, uint32_t *out_d0)
{
    return biwn_task_walk(bus, max_nodes, incoming_d0, out_d0, 1);
}