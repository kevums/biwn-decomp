#include "biwn_cd_wrappers.h"

int biwn_cd_read_wrapper(struct biwn_world_bus *bus,uint32_t start,
                         uint32_t end,uint32_t packed_msf,uint32_t *out_D0)
{
    if(!bus||!bus->call||!out_D0)return BIWN_WORLD_BAD_ARGUMENT;
    uint32_t args[3]={start,end,packed_msf};
    uint32_t d0=packed_msf;
    if(bus->call(bus->context,0x303cu,args,3,&d0))return BIWN_WORLD_DEPENDENCY_ERROR;
    *out_D0=d0;
    return BIWN_WORLD_OK;
}

int biwn_cd_stop_wrapper(struct biwn_world_bus *bus,uint32_t incoming_D0,uint32_t *out_D0)
{
    if(!bus||!bus->call||!out_D0)return BIWN_WORLD_BAD_ARGUMENT;
    uint32_t d0=incoming_D0;
    if(bus->call(bus->context,0x3042u,0,0,&d0))return BIWN_WORLD_DEPENDENCY_ERROR;
    *out_D0=d0;
    return BIWN_WORLD_OK;
}
