/* Analyst translation of candidate 68000 bytes [0xe098,0xe148).
 * Read/write callbacks preserve observable order and asynchronous rereads.
 * No hardware, command-purpose, ABI-return or full-game equivalence claim.
 */
#include "biwn_gpu_commands.h"

static enum biwn_gpu_result read_word(struct biwn_gpu_bus *bus,
                                      uint32_t address, uint32_t *value)
{
    if (!bus->read_budget) return BIWN_GPU_READ_LIMIT;
    bus->read_budget--;
    if (bus->read32(bus->context, address, value)) return BIWN_GPU_BUS_ERROR;
    return BIWN_GPU_OK;
}

static enum biwn_gpu_result write_word(struct biwn_gpu_bus *bus,
                                       uint32_t address, uint32_t value)
{
    return bus->write32(bus->context, address, value)
        ? BIWN_GPU_BUS_ERROR : BIWN_GPU_OK;
}

enum biwn_gpu_result biwn_gpu_wait_idle(struct biwn_gpu_bus *bus)
{
    uint32_t value;
    enum biwn_gpu_result result;
    if (!bus || !bus->read32) return BIWN_GPU_BAD_ARGUMENT;
    do {
        result = read_word(bus, 0xf03200u, &value);
        if (result != BIWN_GPU_OK) return result;
    } while (value != 0);
    return BIWN_GPU_OK;
}

static enum biwn_gpu_result finish_command(struct biwn_gpu_bus *bus,
                                          uint32_t command)
{
    uint32_t value;
    enum biwn_gpu_result result;
    do {
        result = read_word(bus, 0xf03204u, &value);
        if (result != BIWN_GPU_OK) return result;
    } while (value == command);
    return biwn_gpu_wait_idle(bus);
}

#define REQUIRE_OK(expression) do { \
    enum biwn_gpu_result checked = (expression); \
    if (checked != BIWN_GPU_OK) return checked; \
} while (0)

enum biwn_gpu_result biwn_gpu_submit_4d80(struct biwn_gpu_bus *bus)
{
    if (!bus || !bus->read32 || !bus->write32) return BIWN_GPU_BAD_ARGUMENT;
    REQUIRE_OK(biwn_gpu_wait_idle(bus));
    REQUIRE_OK(write_word(bus, 0xf0320cu, 0x47b88u));
    REQUIRE_OK(write_word(bus, 0xf03210u, 0x49b8cu));
    REQUIRE_OK(write_word(bus, 0xf03214u, 0x49bb4u));
    REQUIRE_OK(write_word(bus, 0xf03218u, 0x49b88u));
    REQUIRE_OK(write_word(bus, 0xf03204u, 0x4d80u));
    return finish_command(bus, 0x4d80u);
}

enum biwn_gpu_result biwn_gpu_submit_6ae0(struct biwn_gpu_bus *bus)
{
    uint32_t value;
    if (!bus || !bus->read32 || !bus->write32) return BIWN_GPU_BAD_ARGUMENT;
    REQUIRE_OK(biwn_gpu_wait_idle(bus));
    REQUIRE_OK(write_word(bus, 0xf0320cu, 0x47b88u));
    REQUIRE_OK(write_word(bus, 0xf03210u, 0x49b8cu));
    REQUIRE_OK(read_word(bus, 0x49c18u, &value));
    REQUIRE_OK(write_word(bus, 0xf03214u, value));
    REQUIRE_OK(read_word(bus, 0x49c1cu, &value));
    REQUIRE_OK(write_word(bus, 0xf03218u, value));
    REQUIRE_OK(write_word(bus, 0xf0321cu, 0x10d688u));
    REQUIRE_OK(write_word(bus, 0xf03204u, 0x6ae0u));
    return finish_command(bus, 0x6ae0u);
}

enum biwn_gpu_result biwn_gpu_submit_4b00(struct biwn_gpu_bus *bus,
                                        uint32_t base,uint32_t index,uint32_t destination)
{
    if (!bus || !bus->read32 || !bus->write32) return BIWN_GPU_BAD_ARGUMENT;
    REQUIRE_OK(biwn_gpu_wait_idle(bus));
    REQUIRE_OK(write_word(bus,0xf0320cu,base));
    REQUIRE_OK(write_word(bus,0xf03210u,index));
    REQUIRE_OK(write_word(bus,0xf03214u,destination));
    REQUIRE_OK(write_word(bus,0xf03204u,0x4b00u));
    return finish_command(bus,0x4b00u);
}

#undef REQUIRE_OK
