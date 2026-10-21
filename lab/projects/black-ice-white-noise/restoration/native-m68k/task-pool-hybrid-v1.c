#include "task-pool-native.h"

void biwn_native_task_pool_body(uint32_t *r) {
    TPW32(0x80, 0x0000de08u);
    TPW32(0x88, 0x0000deb6u);
    TPW32(0x8c, 0x0000dee2u);
    TPW32(0x90, 0x0000def6u);
    TPW32(0x20, 0x0000ddfeu);

    r[0] = (r[0] & 0xffff0000u) | 0x00000062u;
    r[8] = 0x000c0d28u;

    for (uint32_t i = 0; i <= 0x62u; ++i) {
        r[9] = r[8] + 0x400u;
        TPW32(r[8], r[9]);
        r[8] = r[9];
        r[0] = (r[0] & 0xffff0000u) | (uint16_t)((r[0] & 0xffffu) - 1u);
    }

    TPW32(r[8], 0u);
    task_pool_move_flags(r, 0u, 32);

    TPW32(0x000c0924, 0x000c0d28u);
    r[8] = 0x000c0928u;
    TPW32(0x000c0920, r[8]);
    TPW32(r[8] + 0x00u, r[8]);
    TPW32(r[8] + 0x04u, r[8]);
    r[9] = r[8] + 0x400u;
    TPW32(r[8] + 0x0cu, r[9]);

    biwn_native_task_pool_set_usp(r[9]);
    r[17] = r[9];

    TPW16(r[8] + 0x14u, 0u);
    task_pool_move_flags(r, 0u, 16);

    TPW32(r[8] + 0x1au, 0u);
    task_pool_move_flags(r, 0u, 32);

    TPW32(r[8] + 0x16u, 0u);
    task_pool_move_flags(r, 0u, 32);

    TPW32(r[8] + 0x22u, 0u);
    task_pool_move_flags(r, 0u, 32);

    TPW32(r[8] + 0x08u, 0x0000ddccu);
    task_pool_move_flags(r, 0x0000ddccu, 32);
}

