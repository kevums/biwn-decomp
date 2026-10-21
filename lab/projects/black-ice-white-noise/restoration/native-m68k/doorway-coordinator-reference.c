/* Complete native10430 coordinator reference; withheld from new local prompts.
 * Earlier local-model portable body is a semantic reference, not this full ABI.
 */
#include "doorway-native.h"
static uint32_t door_scale(uint16_t value)
{
    return (uint32_t)(int32_t)(int16_t)value << 6;
}
uint32_t biwn_doorway_kernel(uint32_t object,uint32_t requested,uint32_t direction,
                           uint32_t incoming_D1,uint32_t incoming_D3,uint32_t *out)
{
    volatile struct biwn_door_actor *actor=(volatile struct biwn_door_actor *)object;
    uint16_t sector=actor->sector;
    uint32_t offset=(uint32_t)(int32_t)(int16_t)sector*4u;
    uint32_t address=*(volatile uint32_t *)(0x49bb4u+offset);
    volatile struct biwn_door_header *header=(volatile struct biwn_door_header *)address;
    uint16_t count=header->count,index=(uint16_t)requested;
    out[0]=incoming_D1;out[1]=address;
    if((int16_t)index>=(int16_t)count){
        out[2]=4u|((sector&0x8000u)?16u:0u);
        return offset&0xffff0000u;
    }
    uint32_t product=(uint32_t)((int32_t)(int16_t)index*28);
    uint32_t records=header->records;
    address=product+records;
    volatile struct biwn_door_record *record=(volatile struct biwn_door_record *)address;
    out[1]=address;
    uint16_t target=record->target;
    if(target==0xffffu){
        out[2]=4u|((address<product)?16u:0u);
        return address&0xffff0000u;
    }
    uint16_t key=(uint16_t)incoming_D1,compare=(uint16_t)incoming_D3;
    uint16_t side=(uint16_t)direction;
    if(side==0){
        uint16_t first=actor->x_low,second=actor->lower_x_low;
        key=(uint16_t)(first-second);compare=(uint16_t)(int16_t)(int8_t)record->west;
    }else if(side==1){
        uint16_t first=actor->upper_x_low,second=actor->x_low;
        key=(uint16_t)(first-second);compare=(uint16_t)(int16_t)(int8_t)record->east;
    }else if(side==2){
        uint16_t first=actor->upper_z_low,second=actor->z_low;
        key=(uint16_t)(first-second);compare=(uint16_t)(int16_t)(int8_t)record->north;
    }else if(side==3){
        uint16_t first=actor->z_low,second=actor->lower_z_low;
        key=(uint16_t)(first-second);compare=(uint16_t)(int16_t)(int8_t)record->south;
    }
    uint16_t nibble=(uint16_t)((key>>6)&15u);
    out[0]=(incoming_D1&0xffff0000u)|nibble;
    if(compare!=nibble){
        out[2]=4u|((key&32u)?16u:0u);
        return address&0xffff0000u;
    }
    actor->transition=0;
    actor->target=record->target;
    actor->entry_base_x=door_scale(record->x);
    actor->entry_base_z=door_scale(record->z);
    uint32_t width=door_scale(record->width);
    uint32_t base_x=actor->entry_base_x;
    actor->entry_upper_x=width+base_x;
    uint32_t depth=door_scale(record->depth);
    uint32_t base_z=actor->entry_base_z;
    uint32_t upper_z=depth+base_z;
    actor->entry_upper_z=upper_z;
    out[2]=(upper_z<depth)?16u:0u;
    return 1;
}
