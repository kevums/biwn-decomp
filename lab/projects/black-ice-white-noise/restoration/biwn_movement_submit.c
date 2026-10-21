#include "biwn_movement_submit.h"

enum biwn_gpu_result biwn_movement_submit(struct biwn_gpu_bus *bus,
    uint32_t base,uint32_t angle1,uint32_t angle2,uint32_t angle3,uint32_t speed)
{
    uint32_t params[5]={base,angle1,angle2,angle3,speed},i,ack;
    enum biwn_gpu_result status;
    if(!bus || !bus->read32 || !bus->write32)return BIWN_GPU_BAD_ARGUMENT;
    status=biwn_gpu_wait_idle(bus);if(status)return status;
    for(i=0;i<5;i++)if(bus->write32(bus->context,0xf0320cu+i*4u,params[i]))return BIWN_GPU_BUS_ERROR;
    if(bus->write32(bus->context,0xf03204u,0x4320u))return BIWN_GPU_BUS_ERROR;
    do {
        if(!bus->read_budget)return BIWN_GPU_READ_LIMIT;
        bus->read_budget--;
        if(bus->read32(bus->context,0xf03204u,&ack))return BIWN_GPU_BUS_ERROR;
    }while(ack==0x4320u);
    return biwn_gpu_wait_idle(bus);
}
