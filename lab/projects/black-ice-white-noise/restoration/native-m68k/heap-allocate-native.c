#include "heap-native.h"

void biwn_native_heap_allocate_body(uint32_t *r)
{
    uint32_t requested = HR(r[15] + 4);
    uint32_t sum = requested + 15u;
    uint32_t need = sum & 0xfffffff8u;
    r[0] = sum;
    r[16] = (r[16] & 0xffe0u) | (sum < requested ? 16u : 0u);

    r[9] = HR(0x112D60);
    int from_head = 1;
    int compacted = 0;

check:
    {
        uint32_t size = HR(r[9]);
        if ((int32_t)need > (int32_t)size) {
            if (compacted) {
                biwn_heap_zero_result(r);
                return;
            }
            r[8] = r[9];
            r[9] = HR(r[9] + 4);
            while (r[9] != 0u) {
                uint32_t bsize = HR(r[9]);
                if ((int32_t)need <= (int32_t)bsize) {
                    from_head = 0;
                    goto fit;
                }
                r[8] = r[9];
                r[9] = HR(r[9] + 4);
            }
            biwn_native_heap_compact_capture(r);
            r[9] = HR(0x112D60);
            from_head = 1;
            compacted = 1;
            goto check;
        }
    }

fit:
    {
        uint32_t value = HR(r[9]);
        uint32_t left = value - need;
        if ((int32_t)left > 15) {
            HW(r[9], left);
            r[9] += left;
            HW(r[9], need);
        } else {
            uint32_t next = HR(r[9] + 4);
            if (from_head) {
                HW(0x112D60, next);
            } else {
                HW(r[8] + 4, next);
            }
        }
    }

    {
        uint32_t index = 255u;
        for (;;) {
            r[1] = index * 4u;
            r[8] = 0x112960u + r[1];
            uint32_t h = HR(r[8]);
            if (h == 0u) {
                goto success;
            }
            if (index == 0u) {
                r[8] = 0x11295Cu;
                r[16] = (r[16] & 0xffe0u) | 16u;
                biwn_heap_zero_result(r);
                return;
            }
            index--;
        }
    }

success:
    {
        HW(0x112960u + r[1], r[9] + 8u);
        r[0] = 0x112960u + r[1];
        HW(r[9] + 4, r[0]);
        uint32_t allocated = HR(r[9]);
        uint32_t before = HR(0x112D64);
        uint32_t after = before - allocated;
        HW(0x112D64, after);
        r[16] = (r[16] & 0xffe0u) | biwn_heap_sub_ccr(before, allocated, after);
        return;
    }
}
