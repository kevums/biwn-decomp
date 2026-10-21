#include "biwn_scene_select.h"
#include "biwn_world_update.h"

int biwn_scene_select(struct biwn_world_bus *bus, uint16_t id_word, uint32_t incoming_D0, uint32_t *out_D0) {
    if (!bus || !out_D0 || !bus->read16 || !bus->read32 || !bus->write16 || !bus->write32 || !bus->call) {
        return BIWN_WORLD_BAD_ARGUMENT;
    }

    uint32_t D0 = incoming_D0;

    if (id_word == 0xFFFF) {
        if (bus->write16(bus->context, 0x403D6, 0x0002) != 0) {
            return BIWN_WORLD_BUS_ERROR;
        }
        *out_D0 = D0;
        return BIWN_WORLD_OK;
    }

    uint32_t D1 = (uint32_t)id_word;
    D1 *= 0x92;
    uint32_t base = 0x3D822 + D1;

    uint16_t tag;
    if (bus->read16(bus->context, base, &tag) != 0) {
        return BIWN_WORLD_BUS_ERROR;
    }
    D0 = (D0 & 0xFFFF0000u) | (uint32_t)tag;

    if (tag == 0x0001) {
        if (bus->write16(bus->context, 0x403D8, 0xFFFF) != 0) {
            return BIWN_WORLD_BUS_ERROR;
        }
        if (bus->write16(bus->context, 0x403CA, id_word) != 0) {
            return BIWN_WORLD_BUS_ERROR;
        }
        if (bus->write32(bus->context, 0x400E6, base) != 0) {
            return BIWN_WORLD_BUS_ERROR;
        }
        if (bus->write16(bus->context, 0x403D6, 0x0003) != 0) {
            return BIWN_WORLD_BUS_ERROR;
        }
        *out_D0 = (D0 & 0xFFFF0000u) | 0x0001;
        return BIWN_WORLD_OK;
    }

    if (tag >= 0x0002) {
        *out_D0 = (D0 & 0xFFFF0000u) | (uint32_t)tag;
        return BIWN_WORLD_OK;
    }

    if (bus->write16(bus->context, 0x403CA, id_word) != 0) {
        return BIWN_WORLD_BUS_ERROR;
    }
    if (bus->write32(bus->context, 0x400E6, base) != 0) {
        return BIWN_WORLD_BUS_ERROR;
    }

    uint16_t old_word;
    if (bus->read16(bus->context, 0x403D8, &old_word) != 0) {
        return BIWN_WORLD_BUS_ERROR;
    }

    uint32_t call_args[1] = { old_word };
    uint32_t call_ret = D0;
    if (bus->call(bus->context, 0x1AE88, call_args, 1, &call_ret) != 0) {
        return BIWN_WORLD_DEPENDENCY_ERROR;
    }
    D0 = call_ret;

    uint32_t A0;
    if (bus->read32(bus->context, 0x400E6, &A0) != 0) {
        return BIWN_WORLD_BUS_ERROR;
    }

    uint16_t val;
    if (bus->read16(bus->context, A0 + 2, &val) != 0) {
        return BIWN_WORLD_BUS_ERROR;
    }
    uint16_t shifted = (uint16_t)(val << 4);
    D0 = (D0 & 0xFFFF0000u) | (uint32_t)shifted;
    if (bus->write16(bus->context, 0x403D8, shifted) != 0) {
        return BIWN_WORLD_BUS_ERROR;
    }

    uint32_t call_args2[1] = { (uint32_t)shifted };
    uint32_t call_ret2 = D0;
    if (bus->call(bus->context, 0x1AC68, call_args2, 1, &call_ret2) != 0) {
        return BIWN_WORLD_DEPENDENCY_ERROR;
    }
    D0 = call_ret2;

    if (bus->write16(bus->context, 0x403DA, (uint16_t)D0) != 0) {
        return BIWN_WORLD_BUS_ERROR;
    }

    uint16_t check_val;
    if (bus->read16(bus->context, 0x403DA, &check_val) != 0) {
        return BIWN_WORLD_BUS_ERROR;
    }

    if (check_val == 0xFFFF) {
        *out_D0 = D0;
        return BIWN_WORLD_OK;
    }

    if (bus->write16(bus->context, 0x403D0, 0x0000) != 0) {
        return BIWN_WORLD_BUS_ERROR;
    }

    if (bus->read32(bus->context, 0x400E6, &A0) != 0) {
        return BIWN_WORLD_BUS_ERROR;
    }

    uint16_t v90, v8e;
    if (bus->read16(bus->context, A0 + 0x90, &v90) != 0) {
        return BIWN_WORLD_BUS_ERROR;
    }
    if (bus->write16(bus->context, 0x403D4, v90) != 0) {
        return BIWN_WORLD_BUS_ERROR;
    }
    if (bus->read16(bus->context, A0 + 0x8E, &v8e) != 0) {
        return BIWN_WORLD_BUS_ERROR;
    }
    if (bus->write16(bus->context, 0x403D2, v8e) != 0) {
        return BIWN_WORLD_BUS_ERROR;
    }

    uint32_t v23f88;
    if (bus->read32(bus->context, 0x23F88, &v23f88) != 0) {
        return BIWN_WORLD_BUS_ERROR;
    }
    if (bus->write32(bus->context, 0x23F84, v23f88) != 0) {
        return BIWN_WORLD_BUS_ERROR;
    }

    uint32_t table_base = 0x4674C;
    uint32_t table_val;

    for (int i = 0; i < 4; i++) {
        uint16_t cur_id;
        if (bus->read16(bus->context, 0x403DA, &cur_id) != 0) {
            return BIWN_WORLD_BUS_ERROR;
        }
        uint16_t offset = (uint16_t)(i * 4);
        uint16_t idx = (uint16_t)(cur_id + offset);
        int32_t sign_ext = (idx < 32768) ? (int32_t)idx : ((int32_t)idx - 65536);
        uint32_t shift_idx = (uint32_t)sign_ext << 3;
        D0 = shift_idx;
        uint32_t table_addr = table_base + shift_idx;

        if (i == 0) {
            if (bus->read32(bus->context, table_addr, &table_val) != 0) {
                return BIWN_WORLD_BUS_ERROR;
            }
            if (bus->write32(bus->context, 0x23F7C, table_val) != 0) {
                return BIWN_WORLD_BUS_ERROR;
            }
        } else if (i == 1) {
            if (bus->read32(bus->context, table_addr, &table_val) != 0) {
                return BIWN_WORLD_BUS_ERROR;
            }
            if (bus->write32(bus->context, 0x24068, table_val) != 0) {
                return BIWN_WORLD_BUS_ERROR;
            }
            if (bus->read32(bus->context, table_addr, &table_val) != 0) {
                return BIWN_WORLD_BUS_ERROR;
            }
            if (bus->write32(bus->context, 0x24070, table_val) != 0) {
                return BIWN_WORLD_BUS_ERROR;
            }
        } else if (i == 2) {
            if (bus->read32(bus->context, table_addr, &table_val) != 0) {
                return BIWN_WORLD_BUS_ERROR;
            }
            if (bus->write32(bus->context, 0x24078, table_val) != 0) {
                return BIWN_WORLD_BUS_ERROR;
            }
            if (bus->read32(bus->context, table_addr, &table_val) != 0) {
                return BIWN_WORLD_BUS_ERROR;
            }
            if (bus->write32(bus->context, 0x24080, table_val) != 0) {
                return BIWN_WORLD_BUS_ERROR;
            }
        } else {
            if (bus->read32(bus->context, table_addr, &table_val) != 0) {
                return BIWN_WORLD_BUS_ERROR;
            }
            if (bus->write32(bus->context, 0x24088, table_val) != 0) {
                return BIWN_WORLD_BUS_ERROR;
            }
            if (bus->read32(bus->context, table_addr, &table_val) != 0) {
                return BIWN_WORLD_BUS_ERROR;
            }
            if (bus->write32(bus->context, 0x24090, table_val) != 0) {
                return BIWN_WORLD_BUS_ERROR;
            }
        }
    }

    if (bus->write16(bus->context, 0x403D6, 0x0000) != 0) {
        return BIWN_WORLD_BUS_ERROR;
    }

    *out_D0 = D0;
    return BIWN_WORLD_OK;
}
