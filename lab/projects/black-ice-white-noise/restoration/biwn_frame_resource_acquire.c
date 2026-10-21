#include "biwn_frame_resource_acquire.h"

static int sx16(uint16_t v) { return (int16_t)(v < 32768 ? v : v - 65536); }

static int load_fill(struct biwn_world_bus *bus, uint16_t id_word, uint32_t scratch_guest_address, uint32_t *out_D0, uint16_t index_word, int16_t adjusted_sx, int16_t count_sx, uint32_t a2, uint32_t a4, uint32_t *remaining) {
    if (count_sx == 0) return 5;
    int32_t q = (int32_t)adjusted_sx / (int32_t)count_sx;
    uint16_t scaled = (uint16_t)(q * 64);
    int32_t scaled_sx = sx16(scaled);
    uint32_t a1 = (uint32_t)(int32_t)(adjusted_sx * 8192 + scaled_sx);
    uint32_t d0_shift = (uint32_t)(uint32_t)sx16(index_word) << 3;
    uint32_t scratch_val = 0;
    if (bus->read32(bus->context, 0x4674c + d0_shift, &scratch_val) != 0) return 2;
    if (bus->write32(bus->context, scratch_guest_address, scratch_val) != 0) return 2;
    uint32_t size = (uint32_t)(uint32_t)count_sx << 13;
    uint32_t args[5] = { a1 + a2, a4, scratch_guest_address, size, 0 };
    uint32_t d0_in = d0_shift;
    if (bus->call(bus->context, 0x1b044, args, 5, &d0_in) != 0) return 3;
    uint16_t j = 0;
    uint32_t last_d0_j = d0_in;
    while (count_sx > (int16_t)j) {
        if (*remaining == 0) return 4;
        (*remaining)--;
        uint16_t idx_j = (uint16_t)(index_word + j);
        uint32_t d0_j = (uint32_t)(uint32_t)sx16(idx_j) << 2;
        last_d0_j = d0_j;
        uint16_t w_val = (uint16_t)(id_word + j);
        if (bus->write16(bus->context, 0x15b4a0 + d0_j, w_val) != 0) return 2;
        if (bus->write16(bus->context, 0x15b4a2 + d0_j, 1) != 0) return 2;
        j++;
    }
    *out_D0 = (last_d0_j & 0xFFFF0000u) | (uint32_t)index_word;
    return 0;
}

int biwn_frame_resource_acquire(struct biwn_world_bus *bus, uint16_t id_word, uint32_t scratch_guest_address, uint32_t *out_D0) {
    if (!bus || !out_D0 || !bus->read16 || !bus->read32 || !bus->write16 || !bus->write32 || !bus->call) return 1;
    if (scratch_guest_address == 0) return 1;
    uint32_t remaining = bus->poll_limit;
    uint16_t mode = 0;
    if (bus->read16(bus->context, 0x15b530, &mode) != 0) return 2;
    if (mode < 1 || mode > 3) { *out_D0 = 0xFFFFFFFF; return 0; }
    uint32_t index2 = (uint32_t)mode * 2u;
    uint16_t base_val = 0;
    if (bus->read16(bus->context, 0x464c8 + index2, &base_val) != 0) return 2;
    uint16_t adjusted = (uint16_t)(id_word - base_val);
    int16_t adjusted_sx = sx16(adjusted);
    uint16_t count_word = 0;
    if (bus->read16(bus->context, 0x464a0 + index2, &count_word) != 0) return 2;
    uint32_t a2 = 0;
    if (bus->read32(bus->context, 0x464a8 + (uint32_t)mode * 4u, &a2) != 0) return 2;
    uint32_t a4 = 0;
    if (bus->read32(bus->context, 0x464b8 + (uint32_t)mode * 4u, &a4) != 0) return 2;
    if (adjusted_sx < 0) { *out_D0 = 0xFFFFFFFF; return 0; }
    uint16_t index_word = 0;
    if (bus->read16(bus->context, 0x15b532, &index_word) != 0) return 2;
    uint16_t limit_word = (uint16_t)(36 - count_word);
    int16_t limit_sx = sx16(limit_word);
    int16_t index_sx = sx16(index_word);
    int16_t count_sx = sx16(count_word);
    if (limit_sx > index_sx) {
        if (remaining == 0) return 4;
        remaining--;
        uint32_t d0_full = (uint32_t)(uint32_t)index_sx << 2;
        uint16_t table_val = 0;
        if (bus->read16(bus->context, 0x15b4a0 + d0_full, &table_val) != 0) return 2;
        if (table_val == id_word) {
            uint16_t j = 0;
            uint32_t last_d0_j = d0_full;
            while (count_sx > (int16_t)j) {
                if (remaining == 0) return 4;
                remaining--;
                uint16_t idx_j = (uint16_t)(index_word + j);
                uint32_t d0_j = (uint32_t)(uint32_t)sx16(idx_j) << 2;
                last_d0_j = d0_j;
                uint16_t val = 0;
                if (bus->read16(bus->context, 0x15b4a2 + d0_j, &val) != 0) return 2;
                if (bus->write16(bus->context, 0x15b4a2 + d0_j, (uint16_t)(val + 1)) != 0) return 2;
                j++;
            }
            *out_D0 = (last_d0_j & 0xFFFF0000u) | (uint32_t)index_word;
            return 0;
        }
        index_word = (uint16_t)(index_word + count_word);
        limit_word = (uint16_t)(36 - count_word);
        limit_sx = sx16(limit_word);
        index_sx = sx16(index_word);
        while (limit_sx > index_sx) {
            if (remaining == 0) return 4;
            remaining--;
            uint32_t d0_loop = (uint32_t)(uint32_t)index_sx << 2;
            uint16_t table_val2 = 0;
            if (bus->read16(bus->context, 0x15b4a0 + d0_loop, &table_val2) != 0) return 2;
            if (table_val2 == id_word) {
                uint16_t j = 0;
                uint32_t last_d0_j = d0_loop;
                while (count_sx > (int16_t)j) {
                    if (remaining == 0) return 4;
                    remaining--;
                    uint16_t idx_j = (uint16_t)(index_word + j);
                    uint32_t d0_j = (uint32_t)(uint32_t)sx16(idx_j) << 2;
                    last_d0_j = d0_j;
                    uint16_t val = 0;
                    if (bus->read16(bus->context, 0x15b4a2 + d0_j, &val) != 0) return 2;
                    if (bus->write16(bus->context, 0x15b4a2 + d0_j, (uint16_t)(val + 1)) != 0) return 2;
                    j++;
                }
                *out_D0 = (last_d0_j & 0xFFFF0000u) | (uint32_t)index_word;
                return 0;
            }
            index_word = (uint16_t)(index_word + count_word);
            limit_word = (uint16_t)(36 - count_word);
            limit_sx = sx16(limit_word);
            index_sx = sx16(index_word);
        }
    }
    if (count_sx == 0) return 5;
    int32_t quotient = (int32_t)adjusted_sx / (int32_t)count_sx;
    a4 = (uint32_t)(int32_t)(a4 + (int32_t)quotient);
    if (bus->read16(bus->context, 0x15b532, &index_word) != 0) return 2;
    limit_word = (uint16_t)(36 - count_word);
    limit_sx = sx16(limit_word);
    index_sx = sx16(index_word);
    if (limit_sx > index_sx) {
        while (limit_sx > index_sx) {
            if (remaining == 0) return 4;
            remaining--;
            uint32_t d0_idx = (uint32_t)(uint32_t)index_sx << 2;
            uint16_t table_val = 0;
            if (bus->read16(bus->context, 0x15b4a0 + d0_idx, &table_val) != 0) return 2;
            if (table_val == 0xFFFF) {
                return load_fill(bus, id_word, scratch_guest_address, out_D0, index_word, adjusted_sx, count_sx, a2, a4, &remaining);
            }
            index_word = (uint16_t)(index_word + count_word);
            limit_word = (uint16_t)(36 - count_word);
            limit_sx = sx16(limit_word);
            index_sx = sx16(index_word);
        }
    }
    if (bus->read16(bus->context, 0x15b532, &index_word) != 0) return 2;
    limit_word = (uint16_t)(36 - count_word);
    limit_sx = sx16(limit_word);
    index_sx = sx16(index_word);
    if (limit_sx <= index_sx) { *out_D0 = 0xFFFFFFFF; return 0; }
    while (limit_sx > index_sx) {
        if (remaining == 0) return 4;
        remaining--;
        uint32_t d0_idx = (uint32_t)(uint32_t)index_sx << 2;
        uint16_t table_val = 0;
        if (bus->read16(bus->context, 0x15b4a2 + d0_idx, &table_val) != 0) return 2;
        if (table_val == 0) {
            return load_fill(bus, id_word, scratch_guest_address, out_D0, index_word, adjusted_sx, count_sx, a2, a4, &remaining);
        }
        index_word = (uint16_t)(index_word + count_word);
        limit_word = (uint16_t)(36 - count_word);
        limit_sx = sx16(limit_word);
        index_sx = sx16(index_word);
    }
    *out_D0 = 0xFFFFFFFF;
    return 0;
}

