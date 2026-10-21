#include "biwn_attack_effect.h"
#include "biwn_world_update.h"

enum biwn_attack_status biwn_attack_effect(struct biwn_world_bus *bus, uint32_t *out_d0) {
    if (!bus || !out_d0) {
        return BIWN_ATTACK_BAD_ARGUMENT;
    }
    if (!bus->read16 || !bus->read32 || !bus->write16 || !bus->call) {
        return BIWN_ATTACK_BAD_ARGUMENT;
    }

    uint16_t v_49d5e;
    if (bus->read16(bus->context, 0x00049d5e, &v_49d5e) != 0) {
        return BIWN_ATTACK_BUS_ERROR;
    }
    if (v_49d5e == 0) {
        goto common_tail;
    }

    uint16_t v_49d5c;
    if (bus->read16(bus->context, 0x00049d5c, &v_49d5c) != 0) {
        return BIWN_ATTACK_BUS_ERROR;
    }
    if (v_49d5c == 0) {
        goto common_tail;
    }

    uint16_t v_49d62;
    if (bus->read16(bus->context, 0x00049d62, &v_49d62) != 0) {
        return BIWN_ATTACK_BUS_ERROR;
    }
    if ((int16_t)v_49d62 > 0) {
        goto common_tail;
    }

    uint16_t v_49d66;
    if (bus->read16(bus->context, 0x00049d66, &v_49d66) != 0) {
        return BIWN_ATTACK_BUS_ERROR;
    }

    uint16_t v_49d12;
    if (bus->read16(bus->context, 0x00049d12, &v_49d12) != 0) {
        return BIWN_ATTACK_BUS_ERROR;
    }

    uint16_t d0w = (uint16_t)((v_49d66 << 1) + v_49d12 + 0xc8);
    int32_t a2 = (int32_t)(int16_t)d0w;

    uint32_t args[1];
    args[0] = 0x64;
    uint32_t d0;
    if (bus->call(bus->context, 0x0001a77c, args, 1, &d0) != 0) {
        return BIWN_ATTACK_DEPENDENCY_ERROR;
    }

    d0 &= 0x3ff;

    if ((int32_t)d0 < a2) {
        uint16_t v_49d60;
        if (bus->read16(bus->context, 0x00049d60, &v_49d60) != 0) {
            return BIWN_ATTACK_BUS_ERROR;
        }

        int32_t d0_full = (int32_t)(int16_t)v_49d60;
        d0_full *= 0xce;

        int32_t a1 = d0_full + 0x49e34;

        uint16_t v_49d5a;
        if (bus->read16(bus->context, 0x00049d5a, &v_49d5a) != 0) {
            return BIWN_ATTACK_BUS_ERROR;
        }

        int32_t d0_ext = (int32_t)(int16_t)v_49d5a;
        d0_ext *= 2;

        uint32_t a0 = 0x461b4;
        uint32_t idx = (uint32_t)d0_ext;

        uint16_t table_val;
        if (bus->read16(bus->context, a0 + idx, &table_val) != 0) {
            return BIWN_ATTACK_BUS_ERROR;
        }

        uint16_t a1_val;
        if (bus->read16(bus->context, (uint32_t)a1, &a1_val) != 0) {
            return BIWN_ATTACK_BUS_ERROR;
        }

        uint16_t new_val = (uint16_t)(a1_val - table_val);
        if (bus->write16(bus->context, (uint32_t)a1, new_val) != 0) {
            return BIWN_ATTACK_BUS_ERROR;
        }
    }

    if (bus->write16(bus->context, 0x00049d62, 0x12c) != 0) {
        return BIWN_ATTACK_BUS_ERROR;
    }

common_tail:;
    uint32_t v_49c50;
    if (bus->read32(bus->context, 0x00049c50, &v_49c50) != 0) {
        return BIWN_ATTACK_BUS_ERROR;
    }

    uint32_t d0_asr = (v_49c50 >> 6) | ((v_49c50 & 0x80000000u) ? 0xFC000000u : 0u);

    if (d0_asr != 0xbf) {
        *out_d0 = d0_asr;
        return BIWN_ATTACK_OK;
    }

    uint32_t v_49c56;
    if (bus->read32(bus->context, 0x00049c56, &v_49c56) != 0) {
        return BIWN_ATTACK_BUS_ERROR;
    }

    uint32_t d0_asr2 = (v_49c56 >> 6) | ((v_49c56 & 0x80000000u) ? 0xFC000000u : 0u);

    if (d0_asr2 != 0x22f) {
        *out_d0 = d0_asr2;
        return BIWN_ATTACK_OK;
    }

    if (bus->write16(bus->context, 0x00043d98, 0x1) != 0) {
        return BIWN_ATTACK_BUS_ERROR;
    }

    *out_d0 = d0_asr2;
    return BIWN_ATTACK_OK;
}
