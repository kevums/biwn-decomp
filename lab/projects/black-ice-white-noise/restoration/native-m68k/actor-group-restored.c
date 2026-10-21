#include "actor-group-native-api.h"

static uint32_t sx16(uint16_t v){return (uint32_t)(v&0x7fffu)-(uint32_t)(v&0x8000u);}
static uint32_t sx8(uint8_t v){return (uint32_t)(v&0x7fu)-(uint32_t)(v&0x80u);}
static int less16(uint16_t a,uint16_t b){return (a^0x8000u)<(b^0x8000u);}
static uint32_t asr10(uint32_t v){return (v>>10)|((v&0x80000000u)?0xffc00000u:0u);}
static uint32_t word16(uint32_t old,uint16_t v){return (old&0xffff0000u)|v;}

static int m10520(uint32_t object,uint32_t *d0){
    uint32_t base,origin,value,record,dx,dz;
    uint16_t w,v,count,i;
    base=ag_r32(0x49c18u);
    *d0=ag_r32(object+4u);
    origin=ag_r32(object+30u);
    *d0-=origin;
    dx=*d0>>6;
    *d0=ag_r32(object+10u);
    origin=ag_r32(object+38u);
    *d0-=origin;
    dz=*d0>>6;
    count=ag_r16(base);
    i=(uint16_t)(count-1u);
    if(!(i&0x8000u)){
        do{
            *d0=sx16(i)*24u;
            value=ag_r32(base+4u);
            record=value+*d0;
            w=ag_r16(record+2u);
            if(!less16((uint16_t)dx,w)){
                w=ag_r16(record+2u);
                v=ag_r16(record+6u);
                *d0=word16(*d0,(uint16_t)(w+v));
                if(less16((uint16_t)dx,(uint16_t)*d0)){
                    w=ag_r16(record+4u);
                    if(!less16((uint16_t)dz,w)){
                        w=ag_r16(record+4u);
                        v=ag_r16(record+8u);
                        *d0=word16(*d0,(uint16_t)(w+v));
                        if(less16((uint16_t)dz,(uint16_t)*d0)){
                            ag_w16(object+42u,i);
                            ag_w32(object+44u,record);
                            w=ag_r16(record+2u);
                            *d0=word16(*d0,(uint16_t)(w<<6));
                            origin=ag_r32(object+30u);
                            ag_w32(object+52u,origin+sx16((uint16_t)*d0));
                            w=ag_r16(record+4u);
                            *d0=word16(*d0,(uint16_t)(w<<6));
                            origin=ag_r32(object+38u);
                            ag_w32(object+60u,origin+sx16((uint16_t)*d0));
                            w=ag_r16(record+6u);
                            *d0=word16(*d0,(uint16_t)(w<<6));
                            origin=ag_r32(object+52u);
                            ag_w32(object+48u,origin+sx16((uint16_t)*d0));
                            w=ag_r16(record+8u);
                            *d0=word16(*d0,(uint16_t)(w<<6));
                            origin=ag_r32(object+60u);
                            ag_w32(object+56u,origin+sx16((uint16_t)*d0));
                            *d0=1;
                            return AG_OK;
                        }
                    }
                }
            }
            i=(uint16_t)(i-1u);
        }while(i!=0xffffu);
    }
    *d0&=0xffff0000u;
    return AG_OK;
}

static int m105da(uint32_t object,uint32_t *d0){
    uint32_t base,origin,value,record,dx,dz;
    uint16_t w,v,count,i;
    base=ag_r32(0x49c18u);
    *d0=ag_r32(object+2u);
    origin=ag_r32(0x49c6au);
    *d0-=origin;
    dx=*d0>>6;
    *d0=ag_r32(object+8u);
    origin=ag_r32(0x49c72u);
    *d0-=origin;
    dz=*d0>>6;
    count=ag_r16(base);
    i=(uint16_t)(count-1u);
    if(!(i&0x8000u)){
        do{
            *d0=sx16(i)*24u;
            value=ag_r32(base+4u);
            record=value+*d0;
            w=ag_r16(record+2u);
            if(!less16((uint16_t)dx,w)){
                w=ag_r16(record+2u);
                v=ag_r16(record+6u);
                *d0=word16(*d0,(uint16_t)(w+v));
                if(less16((uint16_t)dx,(uint16_t)*d0)){
                    w=ag_r16(record+4u);
                    if(!less16((uint16_t)dz,w)){
                        w=ag_r16(record+4u);
                        v=ag_r16(record+8u);
                        *d0=word16(*d0,(uint16_t)(w+v));
                        if(less16((uint16_t)dz,(uint16_t)*d0)){
                            ag_w16(object+16u,i);
                            *d0=1;
                            return AG_OK;
                        }
                    }
                }
            }
            i=(uint16_t)(i-1u);
        }while(i!=0xffffu);
    }
    *d0&=0xffff0000u;
    return AG_OK;
}

static int m134dc(const uint32_t *args,uint32_t *d0){
    uint16_t id,slot,heading,mode,w;
    uint32_t object,x,z,value,dx,dz,small,target,callback=0;
    id=(uint16_t)args[0];
    slot=(uint16_t)args[1];
    object=0x49d6cu+sx16(slot)*206u;
    x=args[2];
    z=args[4];
    heading=(uint16_t)args[5];
    ag_w16(object,id);
    ag_w16(object+2u,0);
    ag_w32(object+4u,x);
    ag_w16(object+8u,args[3]);
    ag_w32(object+10u,z);
    ag_w16(object+14u,0);
    ag_w16(object+16u,0);
    ag_w16(object+18u,0);
    w=ag_r16(0x49c60u);ag_w16(object+20u,w);
    w=ag_r16(0x49c62u);ag_w16(object+22u,w);
    w=ag_r16(0x49c64u);ag_w16(object+24u,w);
    for(uint32_t i=0;i<4;i++){value=ag_r32(0x49c66u+i*4u);ag_w32(object+26u+i*4u,value);}
    *d0=ag_r32(0x49c56u);
    dz=asr10((z&0xfffffc00u)-(*d0&0xfffffc00u));
    small=(uint16_t)(dz*5u+12u);
    *d0=ag_r32(0x49c50u);
    *d0&=0xfffffc00u;
    dx=asr10((x&0xfffffc00u)-*d0);
    ag_w16(object+64u,(uint16_t)(small+(uint16_t)dx));
    ag_w32(object+88u,0);
    ag_w16(object+92u,0);
    ag_w32(object+94u,0);
    ag_w16(object+98u,0);
    ag_w32(object+100u,0);
    ag_w32(object+104u,0);
    ag_w16(object+108u,0);
    ag_w8(object+110u,heading);
    ag_w8(object+111u,heading);
    ag_w32(object+112u,0);
    ag_w32(object+116u,0);
    ag_w32(object+120u,0);
    ag_w32(object+124u,0);
    ag_w16(object+150u,0);
    ag_w16(object+148u,0);
    ag_w16(object+146u,0);
    ag_w16(object+196u,0);
    ag_w16(object+202u,1);
    mode=ag_r16(object+20u);
    if(mode==1){
        uint32_t p[1]={object};
        {int status=biwn_actor_group_call(0,0x102c4u,p,1,d0);if(status)return status;}
    }else{
        mode=ag_r16(object+20u);
        if(mode==2){
            uint32_t p[1]={object};
            {int status=biwn_actor_group_call(0,0x10520u,p,1,d0);if(status)return status;}
        }
    }
    *d0=word16(*d0,(uint16_t)(id-4u));
    if((uint16_t)*d0>114u){
        *d0=sx16(slot)*206u;
        ag_w16(0x49d6cu+*d0,0);
        return AG_OK;
    }
    *d0=(uint16_t)*d0;
    *d0+=*d0;
    w=ag_r16(0x13620u+*d0);
    *d0=word16(*d0,w);
    target=0x13620u+sx16(w);
    switch(target){
        case 0x13706u:callback=0xf4d8u;break;
        case 0x13714u:callback=0xedc4u;break;
        case 0x13722u:callback=0xfcc2u;break;
        case 0x13730u:callback=0x17f80u;break;
        case 0x1373eu:callback=0x178e0u;break;
        case 0x1374au:callback=0xf720u;break;
        case 0x13756u:callback=0x21d40u;break;
        case 0x13762u:callback=0x15080u;break;
        case 0x1376eu:callback=0x14fc0u;break;
        case 0x1377au:callback=0xf888u;break;
        case 0x13786u:callback=0x15140u;break;
        case 0x13792u:callback=0x14100u;break;
        case 0x1379eu:callback=0x11f80u;break;
        case 0x137aau:callback=0x128a0u;break;
        case 0x137b6u:callback=0x15a80u;break;
        case 0x137cau:
            *d0=sx16(slot)*206u;
            ag_w16(0x49d6cu+*d0,0);
            return AG_OK;
        case 0x137dau:
            return AG_OK;
        default:
            return AG_UNSUPPORTED_DISPATCH;
    }
    uint32_t p[2]={callback,sx16(slot)};
    {int status=biwn_actor_group_call(0,0xdf6cu,p,2,d0);if(status)return status;}
    return AG_OK;
}

static int m137e0(const uint32_t *args,uint32_t *d0){
    uint16_t id,heading,slot,small,w;
    uint32_t object,x,z,value,payload,model,byte,target,callback=0;
    uint32_t offset,i;
    id=(uint16_t)args[0];
    x=args[1];
    z=args[3];
    heading=(uint16_t)args[4];
    for(i=0;i<40;i++){
        *d0=sx16((uint16_t)i)*30u;
        w=ag_r16(0x4bd9cu+*d0);
        if(!w)break;
    }
    if(i==40)return AG_OK;
    slot=(uint16_t)i;
    offset=sx16(slot)*30u;
    object=0x4bd9cu+offset;
    ag_w16(object,id);
    ag_w32(object+2u,x);
    ag_w16(object+6u,args[2]);
    ag_w32(object+8u,z);
    *d0=z&0xfffffc00u;
    value=ag_r32(0x49c56u);
    *d0-=value&0xfffffc00u;
    *d0=asr10(*d0);
    small=(uint16_t)(*d0*5u+12u);
    *d0=x&0xfffffc00u;
    value=ag_r32(0x49c50u);
    *d0-=value&0xfffffc00u;
    *d0=asr10(*d0);
    ag_w16(object+14u,(uint16_t)(small+(uint16_t)*d0));
    uint32_t p1[1]={object};
    {int status=biwn_actor_group_call(0,0x105dau,p1,1,d0);if(status)return status;}
    byte=ag_r8(0x4208cu+id);
    if(byte&2u){
        heading=(uint16_t)(heading<<8);
        ag_w8(object+12u,heading);
        *d0=word16(*d0,(uint16_t)(id-104u));
        if((uint16_t)*d0>34u)return AG_OK;
        *d0=(uint16_t)*d0;
        *d0+=*d0;
        w=ag_r16(0x138bcu+*d0);
        *d0=word16(*d0,w);
        target=0x138bcu+sx16(w);
        switch(target){
            case 0x13902u:callback=0x8f54u;break;
            case 0x1391au:callback=0x9de0u;break;
            case 0x13932u:callback=0xa2b8u;break;
            case 0x1394au:callback=0x9908u;break;
            case 0x139ceu:callback=0x8db0u;break;
            case 0x139e6u:callback=0xce20u;break;
            case 0x139feu:callback=0xb390u;break;
            case 0x13a16u:callback=0xc648u;break;
            case 0x13a2eu:
                *d0=offset;
                ag_w16(object,0);
                return AG_OK;
            case 0x13ad8u:
                return AG_OK;
            case 0x13962u:
                *d0=offset;
                ag_w32(object+24u,0x8b80u);
                value=ag_r32(object+2u);
                ag_w32(object+2u,value-32u);
                small=ag_r16(object+16u);
                for(i=0;i<40;i++){
                    *d0=sx16((uint16_t)i)*30u;
                    w=ag_r16(0x4bd9cu+*d0);
                    if(!w)break;
                }
                if(i==40)return AG_OK;
                *d0=sx16((uint16_t)i)*30u;
                object=0x4bd9cu+*d0;
                ag_w16(object+16u,small);
                ag_w16(object,id);
                ag_w32(object+2u,x);
                ag_w16(object+6u,args[2]);
                ag_w32(object+8u,z+32u);
                ag_w8(object+12u,0);
                ag_w32(object+24u,0x8c98u);
                return AG_OK;
            default:
                return AG_UNSUPPORTED_DISPATCH;
        }
        *d0=offset;
        ag_w32(object+24u,callback);
        return AG_OK;
    }
    *d0=ag_r32(0x6e6a8u);
    *d0+=*d0;
    uint32_t p2[3]={*d0+16u,0,0};
    {int status=biwn_actor_group_call(0,0x152a2u,p2,1,d0);if(status)return status;}
    ag_w32(object+20u,*d0);
    payload=ag_r32(*d0);
    ag_w32(payload,0x20000u);
    value=ag_r32(object+20u);
    payload=ag_r32(value);
    byte=ag_r8(0x42000u+id);
    *d0=sx8(byte)<<2;
    value=ag_r32(0x6e6acu+*d0);
    model=0x6e6a0u+value;
    byte=ag_r8(model);
    value=(uint32_t)byte<<16;
    byte=ag_r8(model+1u);
    *d0=byte;
    value|=*d0;
    ag_w32(payload+8u,value);
    byte=ag_r8(model);
    *d0=(uint32_t)byte<<2;
    value=ag_r32(0x3bd20u+*d0);
    ag_w32(payload+12u,value);
    value=ag_r32(object+20u);
    p2[2]=ag_r32(value);
    p2[2]+=16u;
    byte=ag_r8(0x42000u+id);
    *d0=word16(*d0,(uint16_t)sx8(byte));
    p2[1]=sx16((uint16_t)*d0);
    p2[0]=0x6e6a0u;
    {int status=biwn_actor_group_call(0,0xe2b8u,p2,3,d0);if(status)return status;}
    return AG_OK;
}

static int m13ae0(const uint32_t *args,uint32_t *d0){
    uint16_t id;
    uint8_t byte;
    uint32_t p[6],i;
    id=(uint16_t)args[0];
    byte=ag_r8(0x4208cu+sx16(id));
    if(byte&1u){
        for(i=0;i<40;i++){
            *d0=sx16((uint16_t)i)*206u;
            uint16_t w=ag_r16(0x49d6cu+*d0);
            if(!w)break;
        }
        if(i==40)return AG_OK;
        p[0]=id;
        p[1]=(uint16_t)i;
        p[2]=args[1];
        p[3]=(uint16_t)args[2];
        p[4]=args[3];
        p[5]=(uint16_t)args[4];
        {int status=biwn_actor_group_call(0,0x134dcu,p,6,d0);if(status)return status;}
    }else{
        for(uint32_t i=0;i<5;i++)p[i]=args[i];
        {int status=biwn_actor_group_call(0,0x137e0u,p,5,d0);if(status)return status;}
    }
    return AG_OK;
}

int biwn_actor_group_invoke(uint32_t entry,const uint32_t *args,uint32_t incoming_D0,uint32_t *out){
    uint32_t d0=incoming_D0;
    int st;
    switch(entry){
        case 0x13ae0u:st=m13ae0(args,&d0);break;
        case 0x134dcu:st=m134dc(args,&d0);break;
        case 0x137e0u:st=m137e0(args,&d0);break;
        case 0x10520u:st=m10520(args[0],&d0);break;
        case 0x105dau:st=m105da(args[0],&d0);break;
        default:return AG_BAD_ARGUMENT;
    }
    if(st)return st;
    *out=d0;
    return AG_OK;
}

int biwn_actor_group_call(void *context,uint32_t target,const uint32_t *args,uint32_t n,uint32_t *out){
    (void)context;
    uint32_t d0=*out;
    int st;
    switch(target){
        case 0x13ae0u:st=m13ae0(args,&d0);break;
        case 0x134dcu:st=m134dc(args,&d0);break;
        case 0x137e0u:st=m137e0(args,&d0);break;
        case 0x10520u:st=m10520(args[0],&d0);break;
        case 0x105dau:st=m105da(args[0],&d0);break;
        default:st=biwn_actor_external_call(target,args,n,&d0);break;
    }
    if(st)return st;
    *out=d0;
    return AG_OK;
}
