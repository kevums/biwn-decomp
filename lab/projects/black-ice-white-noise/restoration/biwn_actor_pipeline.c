/* Local model integration draft after one directed coordinator repair.
 * Markdown fences removed; original/native CPU evidence is separate. */
#include "biwn_actor_pipeline.h"
#include "biwn_actor_navigation.h"
#include "biwn_actor_movement.h"
#include "biwn_actor_direction.h"
#include "biwn_actor_collision.h"
#include "biwn_rng_cpu.h"
#include "biwn_movement_submit_cpu.h"
#include "biwn_scheduler.h"

#include <stddef.h>

struct pipeline_context {
    uint32_t budget;
    biwn_actor_pipeline_observer observer;
    void *observer_context;
};

static int movement_service(void *opaque, struct biwn_world_bus *bus,
                            struct biwn_task_cpu *cpu, uint32_t target)
{
    struct pipeline_context *ctx = (struct pipeline_context *)opaque;
    if (ctx->observer)
        ctx->observer(ctx->observer_context, target, cpu);

    switch (target) {
    case 0x13440:
        return (int)biwn_actor_direction_body(bus, cpu);
    case 0xE220:
        return (int)biwn_movement_submit_cpu_body(bus, cpu, ctx->budget);
    case 0x13B5A:
    case 0x13BB0:
        return (int)biwn_actor_collision_body(bus, cpu, ctx->budget);
    default:
        return -1;
    }
}

static int primary_service(void *opaque, struct biwn_world_bus *bus,
                           struct biwn_task_cpu *cpu, uint32_t target)
{
    struct pipeline_context *ctx = (struct pipeline_context *)opaque;
    if (ctx->observer)
        ctx->observer(ctx->observer_context, target, cpu);

    switch (target) {
    case 0x1A77C:
        return (int)biwn_rng_cpu_body(bus, cpu);
    case 0xF368:
    case 0x13F12:
    case 0x13F7C:
    case 0x13FEA:
        return (int)biwn_actor_navigation_body(bus, cpu);
    case 0x13C9A:
        return (int)biwn_actor_movement_body(bus, cpu,
                                             (biwn_actor_task_service)movement_service,
                                             ctx);
    default:
        return -1;
    }
}

enum biwn_actor_pipeline_status biwn_actor_pipeline_step(
    struct biwn_world_bus *bus,
    struct biwn_task_cpu *cpu,
    biwn_actor_task_write8 write8,
    uint32_t budget,
    biwn_actor_pipeline_observer observer,
    void *observer_ctx)
{
    if (!bus || !cpu || !write8 || budget == 0)
        return BIWN_ACTOR_PIPELINE_BAD_ARGUMENT;

    if ((cpu->sr & 0x2000u) != 0)
        return BIWN_ACTOR_PIPELINE_BAD_ARGUMENT;

    if (!bus->read8 || !bus->read16 || !bus->read32 ||
        !bus->write16 || !bus->write32)
        return BIWN_ACTOR_PIPELINE_BAD_ARGUMENT;

    struct biwn_task_cpu local = *cpu;
    uint32_t pc = local.pc;

    if (pc == 0xDF60) {
        enum biwn_scheduler_status st = biwn_scheduler_yield(bus, &local, budget);
        if (st != BIWN_SCHEDULER_OK)
            return BIWN_ACTOR_PIPELINE_COMPONENT_ERROR;
        *cpu = local;
        return BIWN_ACTOR_PIPELINE_OK;
    }

    if (pc == 0xDF7A) {
        enum biwn_scheduler_status st = biwn_scheduler_remove(bus, &local, budget);
        if (st != BIWN_SCHEDULER_OK)
            return BIWN_ACTOR_PIPELINE_COMPONENT_ERROR;
        *cpu = local;
        return BIWN_ACTOR_PIPELINE_OK;
    }

    if (pc == 0xF4D8 || pc == 0xF56E || pc == 0xF70C) {
        struct pipeline_context ctx;
        ctx.budget = budget;
        ctx.observer = observer;
        ctx.observer_context = observer_ctx;

        enum biwn_actor_task_status st = biwn_actor_task_run(
            bus, &local, write8,
            (biwn_actor_task_service)primary_service,
            &ctx, budget);

        if (st == BIWN_ACTOR_TASK_OK || st == BIWN_ACTOR_TASK_EXIT_BOUNDARY) {
            *cpu = local;
            return BIWN_ACTOR_PIPELINE_OK;
        }
        return BIWN_ACTOR_PIPELINE_COMPONENT_ERROR;
    }

    return BIWN_ACTOR_PIPELINE_UNSUPPORTED_PC;
}
