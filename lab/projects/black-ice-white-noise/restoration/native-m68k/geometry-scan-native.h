#ifndef BIWN_NATIVE_GEOMETRY_SCAN_H
#define BIWN_NATIVE_GEOMETRY_SCAN_H
#include <stdint.h>
/* Coordinator-supplied native68000 layout and previously checked bounds update.
 * Byte offsets are explicit; default M68000 LONG alignment is two bytes.
 * Pointer bits are preserved in32bit arithmetic; the bus resolves24bit addresses.
 */
struct biwn_scan_actor {
    uint32_t unused0, x;
    uint16_t unused8;
    uint32_t z;
    uint8_t unused14[50];
    uint16_t sector, selected;
    uint32_t record, upper_x, lower_x, upper_z, lower_z;
};
struct biwn_scan_header { uint16_t count; uint8_t unused2[6]; uint32_t records; };
struct biwn_scan_tile { uint8_t unused0[10]; uint16_t x, unused12, z, width, depth; };
#define BIWN_SCAN_OFFSET(type,field,value) typedef char type##_##field##_offset[__builtin_offsetof(struct type,field)==value?1:-1]
BIWN_SCAN_OFFSET(biwn_scan_actor,x,4);
BIWN_SCAN_OFFSET(biwn_scan_actor,z,10);
BIWN_SCAN_OFFSET(biwn_scan_actor,sector,64);
BIWN_SCAN_OFFSET(biwn_scan_actor,selected,66);
BIWN_SCAN_OFFSET(biwn_scan_actor,record,68);
BIWN_SCAN_OFFSET(biwn_scan_actor,upper_x,72);
BIWN_SCAN_OFFSET(biwn_scan_actor,lower_x,76);
BIWN_SCAN_OFFSET(biwn_scan_actor,upper_z,80);
BIWN_SCAN_OFFSET(biwn_scan_actor,lower_z,84);
BIWN_SCAN_OFFSET(biwn_scan_header,count,0);
BIWN_SCAN_OFFSET(biwn_scan_header,records,8);
BIWN_SCAN_OFFSET(biwn_scan_tile,x,10);
BIWN_SCAN_OFFSET(biwn_scan_tile,z,14);
BIWN_SCAN_OFFSET(biwn_scan_tile,width,16);
BIWN_SCAN_OFFSET(biwn_scan_tile,depth,18);
typedef char biwn_scan_actor_alignment[__alignof__(struct biwn_scan_actor)==2?1:-1];
static uint32_t biwn_scan_offset(uint16_t value)
{
    return (uint32_t)(int32_t)(int16_t)(uint16_t)((uint32_t)value << 6);
}
/* Complete original10336..10390 bounds path, with scalar register results.
 * Re-reads actor coordinates and tile fields after search; caches neither.
 */
static uint32_t biwn_scan_install(volatile struct biwn_scan_actor *actor,
    volatile struct biwn_scan_tile *tile, uint32_t address, uint16_t index, uint32_t *out)
{
    actor->selected = index;
    actor->record = address;
    uint32_t x = actor->x & 0xfffffc00u;
    uint16_t lower_x = tile->x;
    actor->lower_x = x + biwn_scan_offset(lower_x);
    uint32_t z = actor->z & 0xfffffc00u;
    uint16_t lower_z = tile->z;
    actor->lower_z = z + biwn_scan_offset(lower_z);
    uint16_t width = tile->width;
    uint32_t installed_x = actor->lower_x;
    actor->upper_x = installed_x + biwn_scan_offset(width);
    uint16_t depth = tile->depth;
    uint32_t installed_z = actor->lower_z;
    uint32_t upper_z = installed_z + biwn_scan_offset(depth);
    actor->upper_z = upper_z;
    out[0] = z;
    out[1] = upper_z;
    out[2] = address;
    out[3] = (depth & 0x400u) ? 16u : 0u;
    return 1;
}
uint32_t biwn_geometry_scan_kernel(uint32_t object, uint32_t *out);
#endif
