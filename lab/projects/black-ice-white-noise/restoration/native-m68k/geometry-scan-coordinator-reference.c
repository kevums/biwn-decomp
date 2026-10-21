/* Coordinator validation reference, withheld from local Author prompts.
 * No original opcode service or host bus callback; complete native102C4 loop.
 */
#include "geometry-scan-native.h"
uint32_t biwn_geometry_scan_kernel(uint32_t object, uint32_t *out)
{
    volatile struct biwn_scan_actor *actor = (volatile struct biwn_scan_actor *)object;
    uint32_t sector = (uint32_t)(int32_t)(int16_t)actor->sector;
    uint32_t header_address = *(volatile uint32_t *)(0x49bb4u + sector * 4u);
    volatile struct biwn_scan_header *header = (volatile struct biwn_scan_header *)header_address;
    uint16_t x = (uint16_t)((actor->x >> 6) & 15u);
    uint32_t position_z = actor->z;
    uint32_t shifted_z = (position_z >> 6) | ((position_z & 0x80000000u) ? 0xfc000000u : 0u);
    uint16_t z = (uint16_t)(shifted_z & 15u);
    uint16_t count = header->count;
    uint16_t index = (uint16_t)(count - 1u);
    unsigned carry = count == 0;
    out[0] = index;
    out[1] = header_address;
    if (index & 0x8000u) {
        out[3] = 4u | (carry ? 16u : 0u);
        return shifted_z & 0xffff0000u;
    }
    uint32_t address;
    for (;;) {
        uint32_t offset = (uint32_t)((int32_t)(int16_t)index * 20);
        address = offset + header->records;
        volatile struct biwn_scan_tile *tile = (volatile struct biwn_scan_tile *)address;
        uint16_t lower = tile->x;
        if ((int16_t)x >= (int16_t)lower) {
            lower = tile->x;
            uint16_t width = tile->width;
            uint32_t sum = (uint32_t)lower + width;
            carry = sum > 0xffffu;
            if ((int16_t)x < (int16_t)(uint16_t)sum) {
                lower = tile->z;
                if ((int16_t)z >= (int16_t)lower) {
                    lower = tile->z;
                    uint16_t depth = tile->depth;
                    sum = (uint32_t)lower + depth;
                    carry = sum > 0xffffu;
                    if ((int16_t)z < (int16_t)(uint16_t)sum)
                        return biwn_scan_install(actor,tile,address,index,out);
                }
            }
        }
        index = (uint16_t)(index - 1u);
        if (index == 0xffffu) break;
    }
    out[0] = index;
    out[2] = address;
    out[3] = 4u | (carry ? 16u : 0u);
    return 0;
}
