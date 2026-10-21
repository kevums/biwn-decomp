#include <stdint.h>

uint8_t biwn_local_bset7(uint8_t value, uint16_t *sr) {
    uint8_t old_bit7 = (value >> 7) & 1u;
    uint8_t new_value = value | 128u;
    uint16_t z_mask = 1u << 2;
    if (old_bit7 == 0u) {
        *sr |= z_mask;
    } else {
        *sr &= (uint16_t)~z_mask;
    }
    return new_value;
}

int biwn_local_divs(uint32_t *d0, uint16_t divisor_bits, uint16_t *sr) {
    if (divisor_bits == 0u) {
        return 9;
    }
    int64_t dividend = (int64_t)(int32_t)(*d0);
    int64_t divisor = (int64_t)(int16_t)divisor_bits;
    int64_t quotient = dividend / divisor;
    int64_t remainder = dividend % divisor;
    if (quotient < -32768 || quotient > 32767) {
        uint16_t c_mask = 1u << 0;
        uint16_t v_mask = 1u << 1;
        uint16_t n_mask = 1u << 3;
        *sr &= (uint16_t)~c_mask;
        *sr |= v_mask;
        *sr |= n_mask;
        return 0;
    }
    uint16_t q16 = (uint16_t)(int16_t)quotient;
    uint16_t r16 = (uint16_t)(int16_t)remainder;
    *d0 = (uint32_t)((uint32_t)r16 << 16) | (uint32_t)q16;
    uint16_t c_mask = 1u << 0;
    uint16_t v_mask = 1u << 1;
    uint16_t z_mask = 1u << 2;
    uint16_t n_mask = 1u << 3;
    *sr &= (uint16_t)~c_mask;
    *sr &= (uint16_t)~v_mask;
    if (quotient == 0) {
        *sr |= z_mask;
    } else {
        *sr &= (uint16_t)~z_mask;
    }
    if (quotient < 0) {
        *sr |= n_mask;
    } else {
        *sr &= (uint16_t)~n_mask;
    }
    return 0;
}
