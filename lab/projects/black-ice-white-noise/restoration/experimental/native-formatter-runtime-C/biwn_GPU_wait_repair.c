#include "biwn_scheduler.h"

int biwn_GPU_wait_repair_step(struct biwn_world_bus *bus, struct biwn_task_cpu *state)
{
    if (!bus || !state || !bus->read32)
        return 1;

    struct biwn_task_cpu local = *state;
    uint32_t pc = local.pc;

    if (pc == 0xE098u) {
        local.pc = 0x162708u;
        *state = local;
        return 0;
    }

    if (pc == 0x162708u) {
        uint32_t mem;
        if (bus->read32(bus->context, 0xF03204u, &mem) != 0)
            return 2;
        uint32_t result = mem - 0xFFFFFFFFu;
        uint16_t ccr = local.sr & 0xFFF0u;
        uint16_t n = (result >> 31) & 1u;
        uint16_t z = (result == 0u) ? 1u : 0u;
        uint16_t v = (((mem ^ 0xFFFFFFFFu) & (mem ^ result)) >> 31) & 1u;
        uint16_t c = (mem < 0xFFFFFFFFu) ? 1u : 0u;
        local.sr = ccr | (n << 3) | (z << 2) | (v << 1) | c;
        local.pc = 0x162712u;
        *state = local;
        return 0;
    }

    if (pc == 0x162712u) {
        if ((local.sr & 0x0004u) == 0u)
            local.pc = 0x162708u;
        else
            local.pc = 0x162714u;
        *state = local;
        return 0;
    }

    if (pc == 0x162714u) {
        uint32_t mem;
        if (bus->read32(bus->context, 0xF03200u, &mem) != 0)
            return 2;
        uint32_t result = mem - 0x00000000u;
        uint16_t ccr = local.sr & 0xFFF0u;
        uint16_t n = (result >> 31) & 1u;
        uint16_t z = (result == 0u) ? 1u : 0u;
        uint16_t v = (((mem ^ 0x00000000u) & (mem ^ result)) >> 31) & 1u;
        uint16_t c = (mem < 0x00000000u) ? 1u : 0u;
        local.sr = ccr | (n << 3) | (z << 2) | (v << 1) | c;
        local.pc = 0x16271Eu;
        *state = local;
        return 0;
    }

    if (pc == 0x16271Eu) {
        if ((local.sr & 0x0004u) == 0u)
            local.pc = 0x162708u;
        else
            local.pc = 0x162720u;
        *state = local;
        return 0;
    }

    if (pc == 0x162720u) {
        uint32_t sp_addr = local.registers[15];
        uint32_t ret;
        if (bus->read32(bus->context, sp_addr, &ret) != 0)
            return 2;
        local.pc = ret;
        local.registers[15] = sp_addr + 4u;
        if (local.sr & 0x2000u)
            local.ssp = sp_addr + 4u;
        else
            local.usp = sp_addr + 4u;
        *state = local;
        return 0;
    }

    return 7;
}