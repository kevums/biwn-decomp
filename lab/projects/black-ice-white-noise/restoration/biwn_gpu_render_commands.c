/* Local model draft after one coordinator-directed repair. Original CPU
 * protocol and host-error verification are recorded separately. */
#include "biwn_gpu_render_commands.h"

#include <stdint.h>

static enum biwn_gpu_result
biwn_gpu_read32_budget(struct biwn_gpu_bus *bus,
                       uint32_t addr,
                       uint32_t *out_value)
{
    if (bus == 0 || bus->read32 == 0 || out_value == 0) {
        return BIWN_GPU_BAD_ARGUMENT;
    }
    if (bus->read_budget == 0u) {
        return BIWN_GPU_READ_LIMIT;
    }
    bus->read_budget--;
    if (bus->read32(bus->context, addr, out_value) != 0) {
        return BIWN_GPU_BUS_ERROR;
    }
    return BIWN_GPU_OK;
}

static enum biwn_gpu_result
biwn_gpu_write32_checked(struct biwn_gpu_bus *bus,
                         uint32_t addr,
                         uint32_t value)
{
    if (bus == 0 || bus->write32 == 0) {
        return BIWN_GPU_BAD_ARGUMENT;
    }
    if (bus->write32(bus->context, addr, value) != 0) {
        return BIWN_GPU_BUS_ERROR;
    }
    return BIWN_GPU_OK;
}

static enum biwn_gpu_result
biwn_gpu_poll_command_done(struct biwn_gpu_bus *bus,
                           uint32_t addr,
                           uint32_t command)
{
    for (;;) {
        uint32_t value = 0u;
        enum biwn_gpu_result res = biwn_gpu_read32_budget(bus, addr, &value);
        if (res != BIWN_GPU_OK) {
            return res;
        }
        if (value != command) {
            return BIWN_GPU_OK;
        }
    }
}

enum biwn_gpu_result
biwn_gpu_submit_52e0(struct biwn_gpu_bus *bus, uint32_t *out_D0)
{
    if (bus == 0 || bus->read32 == 0 || bus->write32 == 0 || out_D0 == 0) {
        return BIWN_GPU_BAD_ARGUMENT;
    }

    enum biwn_gpu_result res = biwn_gpu_wait_idle(bus);
    if (res != BIWN_GPU_OK) {
        return res;
    }

    res = biwn_gpu_write32_checked(bus, 0x10a684u, 1u);
    if (res != BIWN_GPU_OK) {
        return res;
    }

    res = biwn_gpu_write32_checked(bus, 0xf0320cu, 0x47b88u);
    if (res != BIWN_GPU_OK) {
        return res;
    }

    res = biwn_gpu_write32_checked(bus, 0xf03210u, 0x47bc8u);
    if (res != BIWN_GPU_OK) {
        return res;
    }

    uint32_t count = 0u;
    res = biwn_gpu_read32_budget(bus, 0x49b88u, &count);
    if (res != BIWN_GPU_OK) {
        return res;
    }

    res = biwn_gpu_write32_checked(bus, 0xf03214u, count);
    if (res != BIWN_GPU_OK) {
        return res;
    }

    res = biwn_gpu_write32_checked(bus, 0xf03218u, 0x40u);
    if (res != BIWN_GPU_OK) {
        return res;
    }

    res = biwn_gpu_write32_checked(bus, 0xf0321cu, 0x10a684u);
    if (res != BIWN_GPU_OK) {
        return res;
    }

    res = biwn_gpu_write32_checked(bus, 0xf03204u, 0x52e0u);
    if (res != BIWN_GPU_OK) {
        return res;
    }

    res = biwn_gpu_poll_command_done(bus, 0xf03204u, 0x52e0u);
    if (res != BIWN_GPU_OK) {
        return res;
    }

    res = biwn_gpu_wait_idle(bus);
    if (res != BIWN_GPU_OK) {
        return res;
    }

    *out_D0 = 0x47bc8u;
    return BIWN_GPU_OK;
}

enum biwn_gpu_result
biwn_gpu_submit_57a0(struct biwn_gpu_bus *bus)
{
    if (bus == 0 || bus->read32 == 0 || bus->write32 == 0) {
        return BIWN_GPU_BAD_ARGUMENT;
    }

    enum biwn_gpu_result res = biwn_gpu_wait_idle(bus);
    if (res != BIWN_GPU_OK) {
        return res;
    }

    res = biwn_gpu_write32_checked(bus, 0xf03204u, 0x57a0u);
    if (res != BIWN_GPU_OK) {
        return res;
    }

    res = biwn_gpu_poll_command_done(bus, 0xf03204u, 0x57a0u);
    if (res != BIWN_GPU_OK) {
        return res;
    }

    return BIWN_GPU_OK;
}
