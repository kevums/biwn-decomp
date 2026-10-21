#include "gpu-mailbox-native.h"

void biwn_native_gpu_mailbox_body(uint32_t *r) {
    uint32_t sp = r[15];
    uint32_t entry = r[17];

    if (entry == 0xe220) {
        biwn_native_gpu_mailbox_wait_capture(r);
        sp = r[15];

        uint32_t v = GMR32(sp + 4);
        GMW32(0xf0320c, v);
        gpu_mailbox_move_flags(r, v);

        v = GMR32(sp + 8);
        GMW32(0xf03210, v);
        gpu_mailbox_move_flags(r, v);

        v = GMR32(sp + 12);
        GMW32(0xf03214, v);
        gpu_mailbox_move_flags(r, v);

        v = GMR32(sp + 16);
        GMW32(0xf03218, v);
        gpu_mailbox_move_flags(r, v);

        v = GMR32(sp + 20);
        GMW32(0xf0321c, v);
        gpu_mailbox_move_flags(r, v);

        v = 0x4320;
        GMW32(0xf03204, v);
        gpu_mailbox_move_flags(r, v);

        while (1) {
            uint32_t mem_val = GMR32(0xf03204);
            gpu_mailbox_compare_flags(r, mem_val, 0x4320);
            if (mem_val == 0x4320) continue;
            break;
        }

        biwn_native_gpu_mailbox_wait_capture(r);
    } else if (entry == 0xe2b8) {
        biwn_native_gpu_mailbox_wait_capture(r);
        sp = r[15];

        uint32_t v = GMR32(sp + 4);
        GMW32(0xf0320c, v);
        gpu_mailbox_move_flags(r, v);

        v = GMR32(sp + 8);
        GMW32(0xf03210, v);
        gpu_mailbox_move_flags(r, v);

        v = GMR32(sp + 12);
        GMW32(0xf03214, v);
        gpu_mailbox_move_flags(r, v);

        v = 0x4b00;
        GMW32(0xf03204, v);
        gpu_mailbox_move_flags(r, v);

        while (1) {
            uint32_t mem_val = GMR32(0xf03204);
            gpu_mailbox_compare_flags(r, mem_val, 0x4b00);
            if (mem_val == 0x4b00) continue;
            break;
        }

        biwn_native_gpu_mailbox_wait_capture(r);
    }
}
