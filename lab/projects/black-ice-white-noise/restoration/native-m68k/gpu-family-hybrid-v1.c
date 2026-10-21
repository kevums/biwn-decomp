#include "gpu-mailbox-native.h"

void biwn_native_gpu_mailbox_body(uint32_t *r) {
    uint32_t entry = r[17];
    uint32_t a7 = r[15];

    if (entry == 0xe0a6u) {
        biwn_native_gpu_mailbox_wait_capture(r);
        GMW32(0xf0320cu, 0x47b88u);
        GMW32(0xf03210u, 0x49b8cu);
        GMW32(0xf03214u, 0x49bb4u);
        GMW32(0xf03218u, 0x49b88u);
        GMW32(0xf03204u, 0x4d80u);
        while (1) {
            uint32_t v = GMR32(0xf03204u);
            gpu_mailbox_compare_flags(r, v, 0x4d80u);
            if (!(r[16] & 4u)) break;
        }
        biwn_native_gpu_mailbox_wait_capture(r);
    } else if (entry == 0xe0f2u) {
        biwn_native_gpu_mailbox_wait_capture(r);
        GMW32(0xf0320cu, 0x47b88u);
        GMW32(0xf03210u, 0x49b8cu);
        GMW32(0xf03214u, GMR32(0x49c18u));
        GMW32(0xf03218u, GMR32(0x49c1cu));
        GMW32(0xf0321cu, 0x10d688u);
        GMW32(0xf03204u, 0x6ae0u);
        while (1) {
            uint32_t v = GMR32(0xf03204u);
            gpu_mailbox_compare_flags(r, v, 0x6ae0u);
            if (!(r[16] & 4u)) break;
        }
        biwn_native_gpu_mailbox_wait_capture(r);
    } else if (entry == 0xe148u) {
        biwn_native_gpu_mailbox_wait_capture(r);
        GMW32(0xf0320cu, 0x47bc8u);
        GMW32(0xf03210u, 0x49b8cu);
        GMW32(0xf03214u, GMR32(0x49c18u));
        GMW32(0xf03218u, GMR32(0x49c1cu));
        GMW32(0xf0321cu, 0x49b88u);
        GMW32(0xf03204u, 0x6da0u);
        while (1) {
            uint32_t v = GMR32(0xf03204u);
            gpu_mailbox_compare_flags(r, v, 0x6da0u);
            if (!(r[16] & 4u)) break;
        }
        biwn_native_gpu_mailbox_wait_capture(r);
    } else if (entry == 0xe19eu) {
        biwn_native_gpu_mailbox_wait_capture(r);
        GMW32(0x10a684u, 1u);
        uint32_t d0 = 0x47b88u;
        gpu_mailbox_move_flags(r, d0);
        GMW32(0xf0320cu, d0);
        d0 += 0x40u;
        r[0] = d0;
        r[16] = (r[16] & 0xffe0u) | (d0 ? 0u : 4u) | (d0 & 0x80000000u ? 8u : 0u);
        GMW32(0xf03210u, d0);
        GMW32(0xf03214u, GMR32(0x49b88u));
        GMW32(0xf03218u, 0x40u);
        GMW32(0xf0321cu, 0x10a684u);
        GMW32(0xf03204u, 0x52e0u);
        while (1) {
            uint32_t v = GMR32(0xf03204u);
            gpu_mailbox_compare_flags(r, v, 0x52e0u);
            if (!(r[16] & 4u)) break;
        }
        biwn_native_gpu_mailbox_wait_capture(r);
    } else if (entry == 0xe202u) {
        biwn_native_gpu_mailbox_wait_capture(r);
        GMW32(0xf03204u, 0x57a0u);
        while (1) {
            uint32_t v = GMR32(0xf03204u);
            gpu_mailbox_compare_flags(r, v, 0x57a0u);
            if (!(r[16] & 4u)) break;
        }
    } else if (entry == 0xe220u) {
        biwn_native_gpu_mailbox_wait_capture(r);
        GMW32(0xf0320cu, GMR32(a7 + 4u));
        GMW32(0xf03210u, GMR32(a7 + 8u));
        GMW32(0xf03214u, GMR32(a7 + 12u));
        GMW32(0xf03218u, GMR32(a7 + 16u));
        GMW32(0xf0321cu, GMR32(a7 + 20u));
        GMW32(0xf03204u, 0x4320u);
        while (1) {
            uint32_t v = GMR32(0xf03204u);
            gpu_mailbox_compare_flags(r, v, 0x4320u);
            if (!(r[16] & 4u)) break;
        }
        biwn_native_gpu_mailbox_wait_capture(r);
    } else if (entry == 0xe26cu) {
        biwn_native_gpu_mailbox_wait_capture(r);
        GMW32(0xf0320cu, GMR32(a7 + 4u));
        GMW32(0xf03210u, GMR32(a7 + 8u));
        GMW32(0xf03214u, GMR32(a7 + 12u));
        GMW32(0xf03218u, GMR32(a7 + 16u));
        GMW32(0xf0321cu, GMR32(a7 + 20u));
        GMW32(0xf03204u, 0x4720u);
        while (1) {
            uint32_t v = GMR32(0xf03204u);
            gpu_mailbox_compare_flags(r, v, 0x4720u);
            if (!(r[16] & 4u)) break;
        }
        biwn_native_gpu_mailbox_wait_capture(r);
    } else if (entry == 0xe2b8u) {
        biwn_native_gpu_mailbox_wait_capture(r);
        GMW32(0xf0320cu, GMR32(a7 + 4u));
        GMW32(0xf03210u, GMR32(a7 + 8u));
        GMW32(0xf03214u, GMR32(a7 + 12u));
        GMW32(0xf03204u, 0x4b00u);
        while (1) {
            uint32_t v = GMR32(0xf03204u);
            gpu_mailbox_compare_flags(r, v, 0x4b00u);
            if (!(r[16] & 4u)) break;
        }
        biwn_native_gpu_mailbox_wait_capture(r);
    }
}
