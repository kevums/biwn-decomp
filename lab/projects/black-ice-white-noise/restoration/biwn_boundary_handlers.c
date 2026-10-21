#include "biwn_boundary_handlers.h"
#define R16(a,v) do {if(bus->read16(bus->context,a,&(v)))return BIWN_BOUNDARY_BUS_ERROR;}while(0)
#define R32(a,v) do {if(bus->read32(bus->context,a,&(v)))return BIWN_BOUNDARY_BUS_ERROR;}while(0)
#define W16(a,v) do {if(bus->write16(bus->context,a,(uint16_t)(v)))return BIWN_BOUNDARY_BUS_ERROR;}while(0)
#define CALL(a,args,n) do {if(bus->call(bus->context,a,args,n,&result))return BIWN_BOUNDARY_DEPENDENCY_ERROR;}while(0)
#define RETURN_D0(value) do {*out_d0=(value);return BIWN_BOUNDARY_OK;}while(0)

enum biwn_boundary_status biwn_boundary_type1(struct biwn_world_bus *bus,
    uint16_t edge,uint16_t direction,uint16_t delta,uint32_t incoming_d0,uint32_t *out_d0)
{
    uint32_t result=incoming_d0&0xffff0000u,params[3],kind=edge&0xf000u;
    uint16_t word;
    if(!bus || !out_d0 || !bus->read16 || !bus->write16 || !bus->call)return BIWN_BOUNDARY_BAD_ARGUMENT;
    params[0]=0x49c4cu;
    if(kind==0) {
        params[1]=edge&0xfffu;CALL(0x1039cu,params,2);RETURN_D0(result);
    }
    if(kind==0x1000u) {
        params[1]=edge&0xfffu;params[2]=direction;CALL(0x10430u,params,3);
        if(!(uint16_t)result)RETURN_D0(result&0xffff0000u);
        W16(0x49c60u,0);CALL(0x20e8cu,0,0);CALL(0xdf60u,0,0);
        params[0]=2;CALL(0x1aa40u,params,1);CALL(0x20f78u,params,1);RETURN_D0(2);
    }
    if(edge==0xffffu) {
        R16(0x49c8cu,word);W16(0x49c8cu,(uint32_t)word+delta);
        CALL(0x102c4u,params,1);
        if((uint16_t)result)RETURN_D0(1);
        /* Subtract from the current shared word after the helper, not a
         * cached pre-call value. Source reread and16bit wrap are deliberate. */
        R16(0x49c8cu,word);W16(0x49c8cu,(uint32_t)word-delta);
        RETURN_D0(result&0xffff0000u);
    }
    RETURN_D0(result);
}

static uint16_t asr6(uint16_t value)
{return (uint16_t)((value>>6)|(value&0x8000u ? 0xfc00u : 0));}

enum biwn_boundary_status biwn_boundary_type2(struct biwn_world_bus *bus,
    uint32_t object,uint16_t direction,uint32_t incoming_d0,uint32_t incoming_d1,
    uint32_t scan_limit,uint32_t *out_d0)
{
    uint16_t a,b,key=(uint16_t)incoming_d1,index,flags,target,level;
    uint32_t result=incoming_d0&0xffff0000u,pointer,base,params[2],scans=0;
    int32_t signed_index;
    if(!bus || !out_d0 || !bus->read16 || !bus->read32 || !bus->write16 || !bus->call || !scan_limit)
        return BIWN_BOUNDARY_BAD_ARGUMENT;
    switch(direction) {
    case 0:
        R16(0x49c52u,a);R16(0x49c82u,b);key=asr6((uint16_t)((uint32_t)a-b));
        R16(object+8u,a);key=(uint16_t)((uint32_t)key+a);break;
    case 1:
        R16(0x49c7eu,a);R16(0x49c52u,b);key=asr6((uint16_t)((uint32_t)a-b));
        R16(object+8u,a);a=(uint16_t)((uint32_t)a*2u);R16(object+6u,b);
        key=(uint16_t)((uint32_t)key+a+b);break;
    case 2:
        R16(0x49c86u,a);R16(0x49c58u,b);a=asr6((uint16_t)((uint32_t)a-b));
        R16(object+8u,key);R16(object+6u,b);key=(uint16_t)((uint32_t)key+b+a);break;
    case 3:
        R16(0x49c58u,a);R16(0x49c8au,b);key=asr6((uint16_t)((uint32_t)a-b));break;
    default:break;
    }
    R16(object+0x16u,index);
    if(index==0xffffu)RETURN_D0(result);
    R32(0x49c18u,pointer);R16(object+0x16u,index);
    signed_index=(int32_t)(index&0x7fffu)-(int32_t)(index&0x8000u);
    R32(pointer+8u,base);pointer=base+(uint32_t)(signed_index*6);
    result=pointer;
    for(;;) {
        if(scans++>=scan_limit)return BIWN_BOUNDARY_SCAN_LIMIT;
        R16(pointer,a);
        if(key==a)break;
        R16(pointer+2u,flags);
        if(flags&0x8000u)RETURN_D0(result&0xffff0000u);
        pointer+=6u;
    }
    R16(pointer+2u,flags);
    result=(result&0xffff0000u)|(flags&0x7000u);
    if(!(flags&0x7000u))RETURN_D0(result&0xffff0000u);
    R16(pointer+4u,target);
    if(target!=0xffffu) {
        R16(pointer+4u,target);params[0]=0x49c4cu;params[1]=target;
        CALL(0x10652u,params,2);RETURN_D0(result);
    }
    R16(0x49c62u,level);
    if(level)RETURN_D0(result&0xffff0000u);
    params[0]=0x49c4cu;CALL(0x1028eu,params,1);
    if(!(uint16_t)result)RETURN_D0(result&0xffff0000u);
    W16(0x49c60u,0);CALL(0x20f0cu,0,0);CALL(0xdf60u,0,0);
    params[0]=1;CALL(0x1aa40u,params,1);CALL(0x20f78u,params,1);RETURN_D0(2);
}
