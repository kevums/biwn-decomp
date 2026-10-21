/* Coordinator semantic reconstruction of 18E92..190B8.
 * This is separate from the local-model Author/Reviewer experiment.
 * Guest private registers/stack and scheduling remain outside this API. */
#include "biwn_coordinate_entry.h"

struct coordinate_io {
    struct biwn_world_bus *bus;
    biwn_coordinate_write8 byte_write;
    uint32_t remaining;
};
static int operation(struct coordinate_io *io)
{
    if (!io->remaining) return BIWN_COORDINATE_LIMIT;
    io->remaining--;
    return 0;
}
static int read_byte(struct coordinate_io *io, uint32_t address, uint8_t *value)
{
    int status = operation(io);
    if (status) return status;
    return io->bus->read8(io->bus->context, address, value) ? BIWN_COORDINATE_BUS_ERROR : 0;
}
static int read_word(struct coordinate_io *io, uint32_t address, uint16_t *value)
{
    int status = operation(io);
    if (status) return status;
    return io->bus->read16(io->bus->context, address, value) ? BIWN_COORDINATE_BUS_ERROR : 0;
}
static int read_long(struct coordinate_io *io, uint32_t address, uint32_t *value)
{
    int status = operation(io);
    if (status) return status;
    return io->bus->read32(io->bus->context, address, value) ? BIWN_COORDINATE_BUS_ERROR : 0;
}
static int write_byte(struct coordinate_io *io, uint32_t address, uint8_t value)
{
    int status = operation(io);
    if (status) return status;
    return io->byte_write(io->bus->context, address, value) ? BIWN_COORDINATE_BUS_ERROR : 0;
}
static int write_word(struct coordinate_io *io, uint32_t address, uint16_t value)
{
    int status = operation(io);
    if (status) return status;
    return io->bus->write16(io->bus->context, address, value) ? BIWN_COORDINATE_BUS_ERROR : 0;
}
static int write_long(struct coordinate_io *io, uint32_t address, uint32_t value)
{
    int status = operation(io);
    if (status) return status;
    return io->bus->write32(io->bus->context, address, value) ? BIWN_COORDINATE_BUS_ERROR : 0;
}
static int call(struct coordinate_io *io, uint32_t target,
                const uint32_t *args, uint32_t count, uint32_t *result)
{
    int status = operation(io);
    if (status) return status;
    return io->bus->call(io->bus->context, target, args, count, result) ? BIWN_COORDINATE_DEPENDENCY_ERROR : 0;
}
static int32_t signed_word(uint16_t word)
{
    return word < 32768u ? (int32_t)word : (int32_t)word - 65536;
}
#define CHECK(expression) do { int status = (expression); if (status) return status; } while (0)

enum biwn_coordinate_status biwn_coordinate_entry_with_result(struct biwn_world_bus *bus,
    biwn_coordinate_write8 byte_write, uint32_t max_operations,
    uint32_t incoming_d0, uint32_t *out_d0)
{
    struct coordinate_io io;
    uint16_t mode, cursor = 1, x = 0, z = 0, digit;
    uint32_t pointer, held, deadline, clock, result = incoming_d0;
    const uint32_t one[1] = {1};
    const uint32_t offsets[7] = {0, 1, 2, 3, 5, 6, 7};
    uint8_t byte;
    unsigned i;
    if (!bus || !out_d0 || !byte_write || !max_operations || !bus->read8 || !bus->read16 ||
        !bus->read32 || !bus->write16 || !bus->write32 || !bus->call)
        return BIWN_COORDINATE_BAD_ARGUMENT;
    io = (struct coordinate_io){bus, byte_write, max_operations};
    CHECK(read_word(&io, 0x49c60u, &mode));
    if (mode != 1u) { *out_d0 = result; return BIWN_COORDINATE_OK; }
    for (i = 0; i < 7; i++) {
        CHECK(read_long(&io, 0x40ffcu, &pointer));
        CHECK(write_byte(&io, pointer + offsets[i], i ? 0x5fu : 0x20u));
    }
    for (;;) {
        CHECK(call(&io, 0x12620u, one, 1, &result));
        CHECK(read_long(&io, 0x49ba4u, &held));
        while (held) {
            CHECK(call(&io, 0xe4c0u, 0, 0, &result));
            CHECK(read_long(&io, 0x49ba4u, &held));
        }
        CHECK(read_long(&io, 0x778ccu, &clock));
        deadline = clock + 75u;
        result = deadline;
        do {
            CHECK(read_long(&io, 0x778ccu, &clock));
        } while (deadline > clock);
        CHECK(read_long(&io, 0x49ba4u, &held));
        while (!held) {
            CHECK(call(&io, 0xe4c0u, 0, 0, &result));
            CHECK(read_long(&io, 0x49ba4u, &held));
        }
        /* The pushed input is a fresh read after the preceding test. */
        CHECK(read_long(&io, 0x49ba4u, &held));
        CHECK(call(&io, 0x1b718u, &held, 1, &result));
        digit = (uint16_t)result;
        if (!(digit & 0x8000u)) {
            if (cursor <= 7u) {
                CHECK(read_long(&io, 0x40ffcu, &pointer));
                CHECK(write_byte(&io, pointer + cursor, (uint8_t)(digit + 0x30u)));
                if (cursor <= 3u) {
                    result = (result & 0xffff0000u) | (uint16_t)((uint32_t)x * 10u);
                    x = (uint16_t)(result + digit);
                } else {
                    result = (result & 0xffff0000u) | (uint16_t)((uint32_t)z * 10u);
                    z = (uint16_t)(result + digit);
                }
                cursor++;
                if (cursor == 4u) cursor = 5u;
            }
            continue;
        }
        CHECK(read_byte(&io, 0x49ba4u, &byte));
        if ((byte & 0x20u) && cursor == 8u && signed_word(x) <= 966 &&
            signed_word(z) <= 719 && signed_word(x) > 31 && signed_word(z) > 31) {
            CHECK(write_long(&io, 0x49c50u, ((uint32_t)signed_word(x) << 6) | 0x20u));
            CHECK(write_long(&io, 0x49c56u, ((uint32_t)signed_word(z) << 6) | 0x20u));
            CHECK(write_word(&io, 0x45d98u, 1));
            result = (uint32_t)signed_word(z) << 6;
            CHECK(call(&io, 0x20e8cu, 0, 0, &result));
            CHECK(call(&io, 0xdf60u, 0, 0, &result));
            CHECK(call(&io, 0xdf22u, 0, 0, &result));
            CHECK(call(&io, 0x20f78u, one, 1, &result));
            CHECK(call(&io, 0xdf3eu, 0, 0, &result));
            *out_d0 = result;
            return BIWN_COORDINATE_OK;
        }
        CHECK(read_byte(&io, 0x49ba4u, &byte));
        if (byte & 2u) {
            if (cursor > 1u) cursor--;
            if (cursor == 4u) cursor = 3u;
            CHECK(read_long(&io, 0x40ffcu, &pointer));
            CHECK(write_byte(&io, pointer + cursor, 0x5fu));
            /* Exhaustive original-CPU word comparison supports /10 here. */
            if (cursor <= 3u) {
                int32_t value = signed_word(x);
                result = (uint16_t)(value / 10 - (value < 0));
                x = (uint16_t)(value / 10);
            } else {
                int32_t value = signed_word(z);
                result = (uint16_t)(value / 10 - (value < 0));
                z = (uint16_t)(value / 10);
            }
        }
        CHECK(read_byte(&io, 0x49ba6u, &byte));
        if (byte & 0x20u) { *out_d0 = result; return BIWN_COORDINATE_OK; }
    }
}

enum biwn_coordinate_status biwn_coordinate_entry(struct biwn_world_bus *bus,
    biwn_coordinate_write8 byte_write, uint32_t max_operations)
{
    uint32_t ignored;
    return biwn_coordinate_entry_with_result(bus, byte_write, max_operations, 0, &ignored);
}
