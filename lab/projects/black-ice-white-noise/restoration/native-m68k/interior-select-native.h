#ifndef BIWN_INTERIOR_SELECT_NATIVE_H
#define BIWN_INTERIOR_SELECT_NATIVE_H
#include <stdint.h>
/* Coordinator native ABI for original 10520/105DA. All LONG fields have
 * native M68000 two-byte alignment. Public accesses must stay volatile. */
struct biwn_interior_actor {
    uint32_t unused0, x;
    uint16_t unused8;
    uint32_t z;
    uint8_t unused14[16];
    uint32_t origin_x, unused34, origin_z;
    uint16_t selected;
    uint32_t record, upper_x, lower_x, upper_z, lower_z;
};
struct biwn_interior_sprite {
    uint16_t unused0;
    uint32_t x;
    uint16_t unused6;
    uint32_t z;
    uint8_t unused12[4];
    uint16_t selected;
};
struct biwn_interior_header { uint16_t count, unused2; uint32_t records; };
struct biwn_interior_record {
    uint16_t unused0, x, z, width, depth;
    uint8_t unused10[14];
};
#define INTERIOR_OFFSET(t,f,n) typedef char t##_##f##_offset[__builtin_offsetof(struct t,f)==n?1:-1]
INTERIOR_OFFSET(biwn_interior_actor,x,4);
INTERIOR_OFFSET(biwn_interior_actor,z,10);
INTERIOR_OFFSET(biwn_interior_actor,origin_x,30);
INTERIOR_OFFSET(biwn_interior_actor,origin_z,38);
INTERIOR_OFFSET(biwn_interior_actor,selected,42);
INTERIOR_OFFSET(biwn_interior_actor,record,44);
INTERIOR_OFFSET(biwn_interior_actor,upper_x,48);
INTERIOR_OFFSET(biwn_interior_actor,lower_x,52);
INTERIOR_OFFSET(biwn_interior_actor,upper_z,56);
INTERIOR_OFFSET(biwn_interior_actor,lower_z,60);
INTERIOR_OFFSET(biwn_interior_sprite,x,2);
INTERIOR_OFFSET(biwn_interior_sprite,z,8);
INTERIOR_OFFSET(biwn_interior_sprite,selected,16);
INTERIOR_OFFSET(biwn_interior_header,records,4);
typedef char interior_record_stride[sizeof(struct biwn_interior_record)==24?1:-1];
typedef char interior_long_alignment[__alignof__(struct biwn_interior_actor)==2?1:-1];
/* kind 0=10520 actor, kind 1=105DA sprite. Return FULL original D0.
 * Private out starts [incoming D1,A0,A1,unused]; replace with final
 * [D1,A0,A1,CCR low five bits]. Shim restores all other native registers. */
uint32_t biwn_interior_select_kernel(uint32_t object, uint32_t kind, uint32_t *out);
#endif
