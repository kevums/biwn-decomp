/* Coordinator implementation of complete original1039C scalar behavior.
 * Both local Author attempts failed. This file is not accepted model output.
 * Addresses are guest byte addresses; LONG accesses may be two-byte aligned.
 */
#include <stdint.h>
static uint16_t read_word(uint32_t address) { return *(volatile uint16_t *)address; }
static uint32_t read_long(uint32_t address) { return *(volatile uint32_t *)address; }
static void write_word(uint32_t address, uint16_t value) { *(volatile uint16_t *)address = value; }
static void write_long(uint32_t address, uint32_t value) { *(volatile uint32_t *)address = value; }
static uint32_t shifted_word_offset(uint16_t value)
{
    return (uint32_t)(int32_t)(int16_t)(uint16_t)((uint32_t)value << 6);
}
void biwn_geometry_select_kernel(uint32_t object, uint32_t requested,
    uint32_t incoming_d1, uint32_t incoming_a1, uint32_t *out)
{
    uint16_t index = (uint16_t)requested;
    uint32_t sector = (uint32_t)(int32_t)(int16_t)read_word(object + 64);
    uint32_t table_offset = sector * 4u;
    uint32_t header = read_long(0x49bb4u + table_offset);
    uint16_t count = read_word(header);
    if ((int16_t)index >= (int16_t)count) {
        out[0] = table_offset & 0xffff0000u;
        out[1] = (incoming_d1 & 0xffff0000u) | index;
        out[2] = header;
        out[3] = incoming_a1;
        out[4] = 4u | ((sector & 0x40000000u) ? 16u : 0u);
        return;
    }
    uint32_t record = (uint32_t)((int32_t)(int16_t)index * 20);
    record += read_long(header + 8);
    write_word(object + 66, index);
    write_long(object + 68, record);
    uint32_t masked_x = read_long(object + 4) & 0xfffffc00u;
    uint16_t x_offset = read_word(record + 10);
    uint32_t lower_x = masked_x + shifted_word_offset(x_offset);
    write_long(object + 76, lower_x);
    uint32_t masked_z = read_long(object + 10) & 0xfffffc00u;
    uint16_t z_offset = read_word(record + 14);
    uint32_t lower_z = masked_z + shifted_word_offset(z_offset);
    write_long(object + 84, lower_z);
    uint16_t x_extent = read_word(record + 16);
    lower_x = read_long(object + 76);
    write_long(object + 72, shifted_word_offset(x_extent) + lower_x);
    uint16_t z_extent = read_word(record + 18);
    lower_z = read_long(object + 84);
    uint32_t upper_z = shifted_word_offset(z_extent) + lower_z;
    write_long(object + 80, upper_z);
    out[0] = 1;
    out[1] = masked_z;
    out[2] = upper_z;
    out[3] = record;
    out[4] = (z_extent & 0x400u) ? 16u : 0u;
}
