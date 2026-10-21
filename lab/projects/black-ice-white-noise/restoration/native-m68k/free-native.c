#include "free-native.h"

void biwn_native_free_body(uint32_t *r)
{
    uint32_t d0 = r[0];
    uint32_t d1 = r[1];
    uint32_t a0 = r[8];
    uint32_t a1 = r[9];
    uint32_t sp = r[15];
    uint32_t sr = r[16];
    uint32_t X = sr & 16u;

    uint32_t block, handle, v, t, head;

    FW32(sp - 4u, r[11]);
    FW32(sp - 8u, r[10]);
    handle = FR32(sp + 4u);

    if (handle == 0u) {
        goto restore;
    }

    if (FR32(handle) == 0u) {
        goto restore;
    }

    block = FR32(handle) - 8u;

    d1 = FR32(block);
    v = FR32(0x112d64u);
    FW32(0x112d64u, biwn_free_add(v, d1, &X));

    if (FR32(0x112d60u) == 0u) {
        FW32(0x112d60u, block);
        biwn_native_free_clear32(block + 4u);
        biwn_native_free_clear32(block + 8u);
        goto finish_handle;
    }

    head = FR32(0x112d60u);

    if (block < head) {
        a0 = block + FR32(block);
        head = FR32(0x112d60u);

        if (a0 == head) {
            FW32(block + 4u, FR32(a0 + 4u));
            d1 = FR32(a0);
            v = FR32(block);
            FW32(block, biwn_free_add(v, d1, &X));
            if (FR32(a0 + 4u) != 0u) {
                a0 = FR32(a0 + 4u);
                FW32(a0 + 8u, block);
            }
        } else {
            FW32(block + 4u, FR32(0x112d60u));
            a0 = FR32(0x112d60u);
            FW32(a0 + 8u, block);
        }

        biwn_native_free_clear32(block + 8u);
        FW32(0x112d60u, block);
        goto finish_handle;
    }

    a1 = FR32(0x112d60u);

    if (FR32(a1 + 4u) == 0u) {
        goto tail;
    }

scan:
    v = FR32(a1 + 4u);

    if (block >= v) {
        goto advance;
    }

    a0 = block + FR32(block);
    v = FR32(a1 + 4u);

    if (a0 == v) {
        t = FR32(a0 + 4u);
        FW32(block + 4u, t);
        if (t != 0u) {
            a0 = FR32(block + 4u);
            FW32(a0 + 8u, block);
        }
        a0 = FR32(a1 + 4u);
        d1 = FR32(a0);
        v = FR32(block);
        FW32(block, biwn_free_add(v, d1, &X));
    } else {
        FW32(block + 4u, FR32(a1 + 4u));
        a0 = FR32(a1 + 4u);
        FW32(a0 + 8u, block);
    }

    FW32(block + 8u, a1);
    d0 = a1;
    v = FR32(a1);
    d0 = biwn_free_add(d0, v, &X);

    if (block == d0) {
        d1 = FR32(block);
        v = FR32(a1);
        FW32(a1, biwn_free_add(v, d1, &X));
        t = FR32(block + 4u);
        FW32(a1 + 4u, t);
        if (t != 0u) {
            a0 = FR32(block + 4u);
            FW32(a0 + 8u, a1);
        }
    } else {
        FW32(a1 + 4u, block);
    }

    goto finish_handle;

advance:
    a1 = FR32(a1 + 4u);
    if (FR32(a1 + 4u) != 0u) {
        goto scan;
    }

tail:
    d0 = a1;
    v = FR32(a1);
    d0 = biwn_free_add(d0, v, &X);

    if (block == d0) {
        d1 = FR32(block);
        v = FR32(a1);
        FW32(a1, biwn_free_add(v, d1, &X));
    } else {
        FW32(a1 + 4u, block);
        biwn_native_free_clear32(block + 4u);
        FW32(block + 8u, a1);
    }

finish_handle:
    biwn_native_free_clear32(handle);

restore:
    r[10] = FR32(sp - 8u);
    r[11] = FR32(sp - 4u);
    r[0] = d0;
    r[1] = d1;
    r[8] = a0;
    r[9] = a1;
    r[16] = (sr & 0xffe0u) | X | 4u;
}
