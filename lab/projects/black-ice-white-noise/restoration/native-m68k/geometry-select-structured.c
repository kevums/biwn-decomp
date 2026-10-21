/* Coordinator native1039C port, lean register ABI, explicit 68000 field layout.
 * Volatile typed fields permit the compiler's direct displacement addressing.
 * Full32bit pointer arithmetic remains separate from24bit bus resolution.
 */
#include <stdint.h>
struct select_object {
    uint32_t unused0, x;
    uint16_t unused8;
    uint32_t z;
    uint8_t unused14[50];
    uint16_t sector, selected;
    uint32_t record, upper_x, lower_x, upper_z, lower_z;
};
struct select_header { uint16_t count; uint8_t unused2[6]; uint32_t records; };
struct select_record { uint8_t unused0[10]; uint16_t x, unused12, z, width, depth; };
#define OFFSET_CHECK(type,field,value) typedef char type##_##field##_offset[__builtin_offsetof(struct type,field)==value?1:-1]
OFFSET_CHECK(select_object,x,4);
OFFSET_CHECK(select_object,z,10);
OFFSET_CHECK(select_object,sector,64);
OFFSET_CHECK(select_object,selected,66);
OFFSET_CHECK(select_object,record,68);
OFFSET_CHECK(select_object,upper_x,72);
OFFSET_CHECK(select_object,lower_x,76);
OFFSET_CHECK(select_object,upper_z,80);
OFFSET_CHECK(select_object,lower_z,84);
OFFSET_CHECK(select_header,count,0);
OFFSET_CHECK(select_header,records,8);
OFFSET_CHECK(select_record,x,10);
OFFSET_CHECK(select_record,z,14);
OFFSET_CHECK(select_record,width,16);
OFFSET_CHECK(select_record,depth,18);
typedef char object_alignment_is_two[__alignof__(struct select_object)==2?1:-1];
static uint32_t shifted_offset(uint16_t value)
{
    return (uint32_t)(int32_t)(int16_t)(uint16_t)((uint32_t)value << 6);
}
uint32_t biwn_geometry_select_lean_kernel(uint32_t object, uint32_t requested, uint32_t *out)
{
    volatile struct select_object *actor = (volatile struct select_object *)object;
    uint16_t index = (uint16_t)requested;
    uint32_t sector = (uint32_t)(int32_t)(int16_t)actor->sector;
    uint32_t offset = sector * 4u;
    uint32_t header_address = *(volatile uint32_t *)(0x49bb4u + offset);
    volatile struct select_header *header = (volatile struct select_header *)header_address;
    uint16_t count = header->count;
    if ((int16_t)index >= (int16_t)count) {
        out[1] = header_address;
        out[3] = 4u | ((sector & 0x40000000u) ? 16u : 0u);
        return offset & 0xffff0000u;
    }
    uint32_t record_address = (uint32_t)((int32_t)(int16_t)index * 20);
    record_address += header->records;
    volatile struct select_record *record = (volatile struct select_record *)record_address;
    actor->selected = index;
    actor->record = record_address;
    uint32_t x = actor->x & 0xfffffc00u;
    uint16_t x_offset = record->x;
    actor->lower_x = x + shifted_offset(x_offset);
    uint32_t z = actor->z & 0xfffffc00u;
    uint16_t z_offset = record->z;
    actor->lower_z = z + shifted_offset(z_offset);
    uint16_t width = record->width;
    uint32_t lower_x = actor->lower_x;
    actor->upper_x = lower_x + shifted_offset(width);
    uint16_t depth = record->depth;
    uint32_t lower_z = actor->lower_z;
    uint32_t upper_z = lower_z + shifted_offset(depth);
    actor->upper_z = upper_z;
    out[0] = z;
    out[1] = upper_z;
    out[2] = record_address;
    out[3] = (depth & 0x400u) ? 16u : 0u;
    return 1;
}
