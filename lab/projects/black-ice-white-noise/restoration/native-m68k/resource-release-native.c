#include "resource-release-native.h"

void biwn_native_resource_release_body(uint32_t *r) {
    uint16_t id = RR16(r[15] + 4u);
    for (uint32_t i = 0u; i < 50u; ++i) {
        r[0] = i * 12u;
        uint32_t entry = 0x15b534u + r[0];
        if (RR16(entry) == id) {
            uint16_t refs = RR16(entry + 6u);
            refs = (uint16_t)(refs - 1u);
            RW16(entry + 6u, refs);
            if (refs == 0u) {
                RW16(entry, 0xffffu);
                uint32_t handle = RR32(entry + 2u);
                biwn_native_release_free_capture(r, handle);
            }
        }
    }
    r[16] &= 0xffffffe0u;
}
