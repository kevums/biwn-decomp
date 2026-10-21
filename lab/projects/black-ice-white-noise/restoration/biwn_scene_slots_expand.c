#include "biwn_scene_slots_expand.h"

static uint32_t asr32(uint32_t v) {
    return (v >> 1) | (v & 0x80000000u);
}

int biwn_scene_slots_expand(struct biwn_world_bus *bus, const struct biwn_scene_slot_seed *seed, uint32_t *out_D0) {
    if (!bus || !seed || !out_D0) return BIWN_WORLD_BAD_ARGUMENT;
    if (!bus->read16 || !bus->read32 || !bus->write16 || !bus->write32 || !bus->call) return BIWN_WORLD_BAD_ARGUMENT;

    uint32_t A4 = 0;
    uint32_t A1;
    uint16_t count;
    if (bus->read32(bus->context, 0x400E6, &A1) != 0) return BIWN_WORLD_BUS_ERROR;
    if (bus->read16(bus->context, A1 + 0x88, &count) != 0) return BIWN_WORLD_BUS_ERROR;

    if (count == 0) {
        *out_D0 = seed->D0;
        return BIWN_WORLD_OK;
    }

    uint32_t D0 = seed->D0;
    uint32_t D4 = seed->D4;
    uint32_t D5 = seed->D5;
    uint32_t D6 = seed->D6;
    uint32_t D1, D2, D3;

    while (1) {
        if (A4 >= bus->poll_limit) return BIWN_WORLD_POLL_LIMIT;

        uint32_t cur, D0_shifted, A2_base;
        if (bus->read32(bus->context, 0x49B88, &cur) != 0) return BIWN_WORLD_BUS_ERROR;
        cur = (cur + 1) & 0xFFFFFFFFu;
        if (bus->write32(bus->context, 0x49B88, cur) != 0) return BIWN_WORLD_BUS_ERROR;
        if (bus->read32(bus->context, 0x49B88, &cur) != 0) return BIWN_WORLD_BUS_ERROR;
        D0_shifted = cur << 6;
        A2_base = 0x47B88 + D0_shifted;

        uint16_t init_vals[9] = {0x4000, 0, 0, 0, 0x4000, 0, 0, 0, 0x4000};
        for (int i = 0; i < 9; i++) {
            if (bus->write16(bus->context, A2_base + i*2, init_vals[i]) != 0) return BIWN_WORLD_BUS_ERROR;
        }

        uint16_t index;
        if (bus->read16(bus->context, A1, &index) != 0) return BIWN_WORLD_BUS_ERROR;
        uint32_t A0 = 0x400C4 + ((uint32_t)index << 5);

        D1 = 0; D2 = 0; D3 = 0;

        int32_t sx = (int32_t)(A4 & 0xFFFF);
        if (sx >= 32768) sx -= 65536;
        uint32_t face_addr = A1 + 0x10 + ((uint32_t)sx * 20);
        uint16_t face;
        if (bus->read16(bus->context, face_addr, &face) != 0) return BIWN_WORLD_BUS_ERROR;

        if (face <= 5) {
            static const uint32_t face_offsets[6][2] = {
                {4, 0x10}, {4, 0}, {4, 0x10}, {0x10, 0}, {4, 0x10}, {4, 0x10}
            };
            static const uint32_t face_second[6][2] = {
                {8, 0x14}, {8, 0x14}, {8, 0x14}, {8, 0x14}, {8, 0}, {0x14, 0}
            };
            static const uint32_t face_third[6][2] = {
                {0x18, 0}, {0xC, 0x18}, {0xC, 0}, {0xC, 0x18}, {0xC, 0x18}, {0xC, 0x18}
            };
            uint32_t base = 0x3D6CA + (face * 12);
            uint32_t gbase = 0x3D712 + (face * 12);
            uint32_t gx, gy, gz;

            uint32_t cx, cy, cz;
            uint32_t s1, s2;
            if (face_offsets[face][1] == 0) {
                if (bus->read32(bus->context, A0 + face_offsets[face][0], &cx) != 0) return BIWN_WORLD_BUS_ERROR;
            } else {
                if (bus->read32(bus->context, A0 + face_offsets[face][0], &s1) != 0) return BIWN_WORLD_BUS_ERROR;
                if (bus->read32(bus->context, A0 + face_offsets[face][1], &s2) != 0) return BIWN_WORLD_BUS_ERROR;
                cx = asr32(s1 + s2);
            }
            if (bus->read32(bus->context, base, &gx) != 0) return BIWN_WORLD_BUS_ERROR;
            if (face_second[face][1] == 0) {
                if (bus->read32(bus->context, A0 + face_second[face][0], &cy) != 0) return BIWN_WORLD_BUS_ERROR;
            } else {
                if (bus->read32(bus->context, A0 + face_second[face][0], &s1) != 0) return BIWN_WORLD_BUS_ERROR;
                if (bus->read32(bus->context, A0 + face_second[face][1], &s2) != 0) return BIWN_WORLD_BUS_ERROR;
                cy = asr32(s1 + s2);
            }
            if (bus->read32(bus->context, base + 4, &gy) != 0) return BIWN_WORLD_BUS_ERROR;
            if (face_third[face][1] == 0) {
                if (bus->read32(bus->context, A0 + face_third[face][0], &cz) != 0) return BIWN_WORLD_BUS_ERROR;
            } else {
                if (bus->read32(bus->context, A0 + face_third[face][0], &s1) != 0) return BIWN_WORLD_BUS_ERROR;
                if (bus->read32(bus->context, A0 + face_third[face][1], &s2) != 0) return BIWN_WORLD_BUS_ERROR;
                cz = asr32(s1 + s2);
            }

            if (bus->read32(bus->context, base + 8, &gz) != 0) return BIWN_WORLD_BUS_ERROR;
            D6 = cx + gx;
            D5 = cy + gy;
            D4 = cz + gz;

            if (bus->read32(bus->context, gbase, &D3) != 0) return BIWN_WORLD_BUS_ERROR;
            if (bus->read32(bus->context, gbase + 4, &D2) != 0) return BIWN_WORLD_BUS_ERROR;
            if (bus->read32(bus->context, gbase + 8, &D1) != 0) return BIWN_WORLD_BUS_ERROR;
        }

        uint32_t cur2, D0_shifted2, callslot;
        if (bus->read32(bus->context, 0x49B88, &cur2) != 0) return BIWN_WORLD_BUS_ERROR;
        D0_shifted2 = cur2 << 6;
        callslot = 0x47B88 + D0_shifted2;

        if (bus->write16(bus->context, callslot + 0x12, 0) != 0) return BIWN_WORLD_BUS_ERROR;
        if (bus->write16(bus->context, callslot + 0x14, 0) != 0) return BIWN_WORLD_BUS_ERROR;
        if (bus->write16(bus->context, callslot + 0x16, 0) != 0) return BIWN_WORLD_BUS_ERROR;

        uint32_t args[5] = {callslot, D1, D2, D3, 0};
        uint32_t ret = D0_shifted2;
        if (bus->call(bus->context, 0xE26C, args, 5, &ret) != 0) return BIWN_WORLD_DEPENDENCY_ERROR;

        uint32_t cur3, D1_shifted, slot;
        if (bus->read32(bus->context, 0x49B88, &cur3) != 0) return BIWN_WORLD_BUS_ERROR;
        D1_shifted = cur3 << 6;
        slot = 0x47B88 + D1_shifted;

        for (int i = 0; i < 12; i++) {
            uint16_t val;
            if (bus->read16(bus->context, 0x3D75A + i*2, &val) != 0) return BIWN_WORLD_BUS_ERROR;
            if (bus->write16(bus->context, slot + 0x24 + i*2, val) != 0) return BIWN_WORLD_BUS_ERROR;
        }

        uint16_t off_x, off_y, off_z;
        if (bus->read16(bus->context, 0x49B8C, &off_x) != 0) return BIWN_WORLD_BUS_ERROR;
        if (bus->write16(bus->context, slot + 0x12, (uint16_t)(D6 - off_x)) != 0) return BIWN_WORLD_BUS_ERROR;
        if (bus->read16(bus->context, 0x49B8E, &off_y) != 0) return BIWN_WORLD_BUS_ERROR;
        if (bus->write16(bus->context, slot + 0x14, (uint16_t)(D5 - off_y)) != 0) return BIWN_WORLD_BUS_ERROR;
        if (bus->read16(bus->context, 0x49B90, &off_z) != 0) return BIWN_WORLD_BUS_ERROR;
        if (bus->write16(bus->context, slot + 0x16, (uint16_t)(D4 - off_z)) != 0) return BIWN_WORLD_BUS_ERROR;
        if (bus->write16(bus->context, slot + 0x20, 7) != 0) return BIWN_WORLD_BUS_ERROR;

        if (bus->read32(bus->context, 0x400E6, &A1) != 0) return BIWN_WORLD_BUS_ERROR;
        
        int32_t sx2 = (int32_t)(A4 & 0xFFFF);
        if (sx2 >= 32768) sx2 -= 65536;
        uint32_t tex_addr = A1 + 0x14 + ((uint32_t)sx2 * 20);
        uint16_t texture;
        if (bus->read16(bus->context, tex_addr, &texture) != 0) return BIWN_WORLD_BUS_ERROR;
        uint32_t tex_offset = ((uint32_t)texture) << 3;
        uint32_t tex_val;
        if (bus->read32(bus->context, 0x3D772 + tex_offset, &tex_val) != 0) return BIWN_WORLD_BUS_ERROR;
        if (bus->write32(bus->context, slot + 0x3C, tex_val) != 0) return BIWN_WORLD_BUS_ERROR;

        uint32_t cur4, D0_shifted4;
        if (bus->read32(bus->context, 0x49B88, &cur4) != 0) return BIWN_WORLD_BUS_ERROR;
        D0_shifted4 = ((cur4 - 1) & 0xFFFFFFFFu) << 6;
        uint16_t val_49b8a;
        if (bus->read16(bus->context, 0x49B8A, &val_49b8a) != 0) return BIWN_WORLD_BUS_ERROR;
        if (bus->write16(bus->context, 0x47B88 + D0_shifted4 + 0x18, val_49b8a) != 0) return BIWN_WORLD_BUS_ERROR;

        D0 = D0_shifted4;
        A4++;
        if (bus->read16(bus->context, A1 + 0x88, &count) != 0) return BIWN_WORLD_BUS_ERROR;
        if (A4 >= count) break;
    }

    *out_D0 = D0;
    return BIWN_WORLD_OK;
}
