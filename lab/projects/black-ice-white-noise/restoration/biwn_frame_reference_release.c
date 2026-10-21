#include "biwn_frame_reference_release.h"

int biwn_frame_reference_release(struct biwn_world_bus *bus, uint16_t id_word, uint32_t incoming_D0, uint32_t *out_D0) {
    if (!bus || !out_D0 || !bus->read16 || !bus->write16) {
        return 1;
    }

    int32_t signed_id = (int32_t)(id_word < 32768 ? id_word : (int32_t)id_word - 65536);
    if (signed_id < 0) {
        *out_D0 = incoming_D0;
        return 0;
    }

    uint16_t mode_word;
    if (bus->read16(bus->context, 0x15B530, &mode_word) != 0) {
        return 2;
    }

    int32_t mode_int = (int32_t)(mode_word < 32768 ? mode_word : (int32_t)mode_word - 65536);
    uint32_t d0 = (uint32_t)mode_int * 2u;

    uint16_t remaining_word;
    if (bus->read16(bus->context, 0x464A0 + d0, &remaining_word) != 0) {
        return 2;
    }

    int32_t remaining_int = (int32_t)(remaining_word < 32768 ? remaining_word : (int32_t)remaining_word - 65536);
    if (remaining_int <= 0) {
        *out_D0 = d0;
        return 0;
    }

    uint16_t index_word = 0;
    uint16_t wanted_word = id_word;

    while (1) {
        int32_t current_remaining_int = (int32_t)(remaining_word < 32768 ? remaining_word : (int32_t)remaining_word - 65536);
        if (current_remaining_int <= 0) {
            break;
        }

        uint32_t offset = ((uint32_t)(int32_t)(index_word < 32768 ? index_word : (int32_t)index_word - 65536) << 2) & 0xFFFFFFFFu;
        d0 = offset;
        uint16_t stored_id;
        if (bus->read16(bus->context, 0x15B4A0 + offset, &stored_id) != 0) {
            return 2;
        }

        if (stored_id == wanted_word) {
            uint16_t refs_for_tst;
            if (bus->read16(bus->context, 0x15B4A2 + offset, &refs_for_tst) != 0) {
                return 2;
            }

            int32_t refs_int = (int32_t)(refs_for_tst < 32768 ? refs_for_tst : (int32_t)refs_for_tst - 65536);
            if (refs_int > 0) {
                uint16_t refs_for_rmw;
                if (bus->read16(bus->context, 0x15B4A2 + offset, &refs_for_rmw) != 0) {
                    return 2;
                }
                uint16_t new_refs = (uint16_t)((uint16_t)refs_for_rmw - 1u);
                if (bus->write16(bus->context, 0x15B4A2 + offset, new_refs) != 0) {
                    return 2;
                }
            }

            remaining_word = (uint16_t)((uint16_t)remaining_word - 1u);
            wanted_word = (uint16_t)((uint16_t)wanted_word + 1u);
        }

        index_word = (uint16_t)((uint16_t)index_word + 1u);
        int32_t index_int = (int32_t)(index_word < 32768 ? index_word : (int32_t)index_word - 65536);
        if (index_int <= 35) {
            continue;
        } else {
            break;
        }
    }

    *out_D0 = d0;
    return 0;
}
