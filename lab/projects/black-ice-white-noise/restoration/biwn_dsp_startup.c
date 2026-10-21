/* Portable translation of the original 68000 CPU protocol [E942,EA16).
 * Observable bus ordering and completed D1/A0/A1 are retained.
 * No device scheduling, DSP execution, CCR, audio or full-game equivalence.
 */
#include "biwn_dsp_startup.h"

static enum biwn_dsp_result read32(struct biwn_dsp_bus *bus, uint32_t address, uint32_t *value)
{
    if (!bus->read_budget) return BIWN_DSP_READ_LIMIT;
    bus->read_budget--;
    return bus->read32(bus->context, address, value) ? BIWN_DSP_BUS_ERROR : BIWN_DSP_OK;
}

static enum biwn_dsp_result write_value(struct biwn_dsp_bus *bus, uint32_t address, unsigned width, uint32_t value)
{
    return bus->write(bus->context, address, width, value) ? BIWN_DSP_BUS_ERROR : BIWN_DSP_OK;
}

#define CHECK(expression) do { \
    enum biwn_dsp_result checked = (expression); \
    if (checked != BIWN_DSP_OK) return checked; \
} while (0)

enum biwn_dsp_result biwn_dsp_wait_mailbox(struct biwn_dsp_bus *bus)
{
    uint32_t value;
    if (!bus || !bus->read32) return BIWN_DSP_BAD_ARGUMENT;
    do { CHECK(read32(bus, 0xf1badcu, &value)); } while (value != 0);
    return BIWN_DSP_OK;
}

enum biwn_dsp_result biwn_dsp_signal_one(struct biwn_dsp_bus *bus)
{
    if (!bus || !bus->read32 || !bus->write) return BIWN_DSP_BAD_ARGUMENT;
    CHECK(write_value(bus, 0xf1badcu, 4, 1));
    CHECK(write_value(bus, 0xf1a114u, 4, 5));
    return biwn_dsp_wait_mailbox(bus);
}

enum biwn_dsp_result biwn_dsp_load_start(struct biwn_dsp_bus *bus, struct biwn_dsp_cpu_state *cpu)
{
    uint32_t value, copies;
    if (!bus || !bus->read32 || !bus->write || !cpu) return BIWN_DSP_BAD_ARGUMENT;
    cpu->a0 = 0x7240u;
    CHECK(read32(bus, cpu->a0, &cpu->a1)); cpu->a0 += 4;
    CHECK(read32(bus, cpu->a0, &value)); cpu->a0 += 4;
    /* Unsigned operations give ASR.L semantics without signed-shift UB. */
    cpu->d1 = ((value >> 2) | ((value & 0x80000000u) ? 0xc0000000u : 0u)) - 1u;
    copies = (cpu->d1 & 0xffffu) + 1u;
    do {
        CHECK(read32(bus, cpu->a0, &value));
        CHECK(write_value(bus, cpu->a1, 4, value));
        cpu->a0 += 4; cpu->a1 += 4;
        cpu->d1 = (cpu->d1 & 0xffff0000u) | ((cpu->d1 - 1u) & 0xffffu);
    } while (--copies);
    CHECK(write_value(bus, 0xf1bafcu, 4, 0x7fffu));
    CHECK(write_value(bus, 0xf1bb00u, 4, 0x7fffu));
    CHECK(write_value(bus, 0xf1a110u, 4, 0xf1b126u));
    CHECK(write_value(bus, 0xf1a114u, 4, 1));
    CHECK(write_value(bus, 0xf1a150u, 4, 0x1au));
    CHECK(write_value(bus, 0xf1a154u, 4, 0x15u));
    CHECK(write_value(bus, 0xf1badcu, 4, 2));
    CHECK(write_value(bus, 0xf1bae0u, 4, 0x3bce0u));
    CHECK(write_value(bus, 0xf1bae4u, 4, 0));
    CHECK(write_value(bus, 0xf1a114u, 4, 5));
    return biwn_dsp_wait_mailbox(bus);
}

enum biwn_dsp_result biwn_dsp_setup(struct biwn_dsp_bus *bus, struct biwn_dsp_cpu_state *cpu)
{
    if (!bus || !bus->read32 || !bus->write || !cpu) return BIWN_DSP_BAD_ARGUMENT;
    CHECK(write_value(bus, 0xf1a10cu, 4, 0x70007u));
    CHECK(write_value(bus, 0xf10000u, 2, 0));
    CHECK(write_value(bus, 0xf10002u, 2, 0));
    CHECK(write_value(bus, 0xf14000u, 2, 0x100u));
    return biwn_dsp_load_start(bus, cpu);
}

#undef CHECK
