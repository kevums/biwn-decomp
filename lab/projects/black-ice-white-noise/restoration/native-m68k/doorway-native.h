#ifndef BIWN_DOORWAY_NATIVE_H
#define BIWN_DOORWAY_NATIVE_H
#include <stdint.h>
struct biwn_door_actor {
    uint8_t unused0[6]; uint16_t x_low;
    uint8_t unused8[4]; uint16_t z_low;
    uint8_t unused14[8]; uint16_t transition, target;
    uint32_t entry_upper_x, entry_base_x, entry_upper_z, entry_base_z;
    uint8_t unused42[22]; uint16_t sector;
    uint8_t unused66[8]; uint16_t upper_x_low;
    uint8_t unused76[2]; uint16_t lower_x_low;
    uint8_t unused80[2]; uint16_t upper_z_low;
    uint8_t unused84[2]; uint16_t lower_z_low;
};
struct biwn_door_header {uint16_t unused0,count;uint8_t unused4[8];uint32_t records;};
struct biwn_door_record {
    uint8_t unused0[11], west, unused12, east, unused14, north, unused16, south;
    uint16_t x,z,width,depth,target;
};
#define DOOR_OFFSET(t,f,n) typedef char t##_##f##_offset[__builtin_offsetof(struct t,f)==n?1:-1]
DOOR_OFFSET(biwn_door_actor,x_low,6);DOOR_OFFSET(biwn_door_actor,z_low,12);
DOOR_OFFSET(biwn_door_actor,transition,22);DOOR_OFFSET(biwn_door_actor,target,24);
DOOR_OFFSET(biwn_door_actor,entry_upper_x,26);DOOR_OFFSET(biwn_door_actor,entry_base_x,30);
DOOR_OFFSET(biwn_door_actor,entry_upper_z,34);DOOR_OFFSET(biwn_door_actor,entry_base_z,38);
DOOR_OFFSET(biwn_door_actor,sector,64);DOOR_OFFSET(biwn_door_actor,upper_x_low,74);
DOOR_OFFSET(biwn_door_actor,lower_x_low,78);DOOR_OFFSET(biwn_door_actor,upper_z_low,82);
DOOR_OFFSET(biwn_door_actor,lower_z_low,86);DOOR_OFFSET(biwn_door_header,count,2);
DOOR_OFFSET(biwn_door_header,records,12);DOOR_OFFSET(biwn_door_record,west,11);
DOOR_OFFSET(biwn_door_record,east,13);DOOR_OFFSET(biwn_door_record,north,15);
DOOR_OFFSET(biwn_door_record,south,17);DOOR_OFFSET(biwn_door_record,x,18);
DOOR_OFFSET(biwn_door_record,z,20);DOOR_OFFSET(biwn_door_record,width,22);
DOOR_OFFSET(biwn_door_record,depth,24);DOOR_OFFSET(biwn_door_record,target,26);
typedef char doorway_actor_alignment_two[__alignof__(struct biwn_door_actor)==2?1:-1];
uint32_t biwn_doorway_kernel(uint32_t object,uint32_t index,uint32_t direction,
                           uint32_t incoming_D1,uint32_t incoming_D3,uint32_t *out);
#endif
