#include <stdint.h>

uint32_t biwn_geometry_outside_kernel(uint32_t object, uint32_t *last_position)
{

    int32_t x = *(volatile int32_t *)(object + 4);
    int32_t x_lower = *(volatile int32_t *)(object + 30);
    *last_position = (uint32_t)x;
    if (x < x_lower) {
        return 2;
    }

    x = *(volatile int32_t *)(object + 4);
    int32_t x_upper = *(volatile int32_t *)(object + 26);
    *last_position = (uint32_t)x;
    if (x >= x_upper) {
        return 2;
    }

    int32_t z = *(volatile int32_t *)(object + 10);
    int32_t z_lower = *(volatile int32_t *)(object + 38);
    *last_position = (uint32_t)z;
    if (z < z_lower) {
        return 2;
    }

    z = *(volatile int32_t *)(object + 10);
    int32_t z_upper = *(volatile int32_t *)(object + 34);
    *last_position = (uint32_t)z;
    if (z >= z_upper) {
        return 1;
    }

    return 0;
}
