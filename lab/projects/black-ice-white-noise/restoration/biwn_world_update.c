#include "biwn_world_update.h"
#include "biwn_inventory_select.h"

static uint32_t sx16(uint16_t value)
{ return value & 0x8000u ? (uint32_t)value|0xffff0000u : value; }
static int signed_less(uint32_t a,uint32_t b)
{ return (a^0x80000000u)<(b^0x80000000u); }
static int redraw(void *context)
{
    struct biwn_world_bus *bus=context;
    uint32_t result;
    return bus->call(bus->context,0x1b786u,0,0,&result);
}
static int select_read8(void *p,uint32_t a,uint8_t *v)
{struct biwn_world_bus *b=p;return b->read8(b->context,a,v);}
static int select_read16(void *p,uint32_t a,uint16_t *v)
{struct biwn_world_bus *b=p;return b->read16(b->context,a,v);}
static int select_read32(void *p,uint32_t a,uint32_t *v)
{struct biwn_world_bus *b=p;return b->read32(b->context,a,v);}
static int select_write16(void *p,uint32_t a,uint16_t v)
{struct biwn_world_bus *b=p;return b->write16(b->context,a,v);}

#define R8(a,v) do { if(bus->read8(bus->context,a,&(v)))return BIWN_WORLD_BUS_ERROR; }while(0)
#define R16(a,v) do { if(bus->read16(bus->context,a,&(v)))return BIWN_WORLD_BUS_ERROR; }while(0)
#define R32(a,v) do { if(bus->read32(bus->context,a,&(v)))return BIWN_WORLD_BUS_ERROR; }while(0)
#define W16(a,v) do { if(bus->write16(bus->context,a,(uint16_t)(v)))return BIWN_WORLD_BUS_ERROR; }while(0)
#define W32(a,v) do { if(bus->write32(bus->context,a,(uint32_t)(v)))return BIWN_WORLD_BUS_ERROR; }while(0)
#define CALL(a,args,n) do { if(bus->call(bus->context,a,args,n,&result))return BIWN_WORLD_DEPENDENCY_ERROR; }while(0)

static enum biwn_world_status integrate(struct biwn_world_bus *bus,int camera)
{
    uint32_t axis,p,position,delta_address,fraction_address;
    uint16_t delta_fraction,old_fraction,delta_integer,position_word,total;
    for(axis=0;axis<3;axis++) {
        delta_address=0x49cdeu+axis*2u;
        fraction_address=camera ? 0x49b92u+axis*2u : 0x49c5au+axis*2u;
        R16(0x49ce6u+axis*2u,delta_fraction);
        R16(fraction_address,old_fraction);
        total=(uint16_t)((delta_fraction&0x3fffu)+(old_fraction&0x3fffu));
        R16(delta_address,delta_integer);
        if(camera || axis==1) {
            p=camera ? 0x49b8cu+axis*2u : 0x49c54u;
            R16(p,position_word);
            W16(p,(uint32_t)position_word+delta_integer+(total>>14));
        } else {
            p=axis==0 ? 0x49c50u : 0x49c56u;
            R32(p,position);
            W32(p,position+sx16(delta_integer)+(total>>14));
        }
        W16(fraction_address,total&0x3fffu);
    }
    return BIWN_WORLD_OK;
}

enum biwn_world_status biwn_world_update(struct biwn_world_bus *bus)
{
    uint8_t byte;
    uint16_t y,fx,fy,fz,mode,decision=1,old_status,new_status,edge;
    uint32_t x,z,clock,previous,result,params[5],polls=0,a,b,pointer,direction;
    enum biwn_world_status status;
    struct biwn_selection_cpu selection_cpu={0,0,0};
    struct biwn_ui_bus selection_bus={select_read8,select_read16,select_read32,select_write16,redraw,bus};
    int selection_result;
    if(!bus || !bus->read8 || !bus->read16 || !bus->read32 || !bus->write16 || !bus->write32 || !bus->call || !bus->poll_limit)
        return BIWN_WORLD_BAD_ARGUMENT;
    CALL(0xe4c0u,0,0);polls++;
    R8(0x49bacu,byte);
    if(byte&0x10u) {
        do {
            if(polls>=bus->poll_limit)return BIWN_WORLD_POLL_LIMIT;
            CALL(0xe4c0u,0,0);polls++;
            R8(0x49bacu,byte);
        }while(!(byte&0x10u));
        W32(0x49ba4u,0x10000000u);W32(0x49bacu,0x10000000u);
        R32(0x778ccu,clock);W32(0x46252u,clock);
    }
    R32(0x778ccu,clock);R32(0x46252u,previous);
    W32(0x4c24cu,clock-previous);
    R32(0x4c24cu,a);
    if(signed_less(30u,a))W32(0x4c24cu,30u);
    selection_result=biwn_inventory_select(&selection_bus,&selection_cpu);
    if(selection_result!=BIWN_SELECTION_OK)return selection_result==BIWN_SELECTION_REDRAW_ERROR ? BIWN_WORLD_DEPENDENCY_ERROR : BIWN_WORLD_BUS_ERROR;
    R32(0x778ccu,clock);W32(0x46252u,clock);
    R8(0x49ba7u,byte);
    if(!(byte&0x80u))CALL(0x191f4u,0,0);
    R32(0x49c50u,x);R16(0x49c54u,y);R32(0x49c56u,z);
    R16(0x49c5au,fx);R16(0x49c5cu,fy);R16(0x49c5eu,fz);
    R32(0x49cc4u,params[4]);R8(0x49cbau,byte);
    params[0]=0x49cccu;params[1]=0;params[2]=byte;params[3]=0;
    CALL(0xe220u,params,5);
    status=integrate(bus,0);if(status)return status;
    R16(0x49c60u,mode);
    if(mode==1) {
        R32(0x49c56u,a);R32(0x49c9cu,b);
        if(!signed_less(a,b)){direction=0;params[2]=5;}
        else {
            R32(0x49c56u,a);R32(0x49ca0u,b);
            if(signed_less(a,b)){direction=1;params[2]=0xfffbu;}
            else {
                R32(0x49c50u,a);R32(0x49c94u,b);
                if(!signed_less(a,b)){direction=2;params[2]=1;}
                else {
                    R32(0x49c50u,a);R32(0x49c98u,b);
                    if(!signed_less(a,b))goto collision_done;
                    direction=3;params[2]=0xffffu;
                }
            }
        }
        R32(0x49c90u,pointer);R16(pointer+2u+direction*2u,edge);
        params[0]=edge;params[1]=direction;CALL(0x19f2cu,params,3);decision=(uint16_t)result;
    } else {
        R16(0x49c60u,mode);
        if(mode!=2){decision=0;goto collision_done;}
        R32(0x49c56u,a);R32(0x49c84u,b);
        if(!signed_less(a,b))direction=0;
        else {
            R32(0x49c56u,a);R32(0x49c88u,b);
            if(signed_less(a,b))direction=1;
            else {
                R32(0x49c50u,a);R32(0x49c7cu,b);
                if(!signed_less(a,b))direction=2;
                else {
                    R32(0x49c50u,a);R32(0x49c80u,b);
                    if(!signed_less(a,b))goto collision_done;
                    direction=3;
                }
            }
        }
        R32(0x49c78u,params[0]);params[1]=direction;
        CALL(0x19fdau,params,2);decision=(uint16_t)result;
    }
collision_done:
    if(decision==0) {
        W32(0x49c50u,x);W16(0x49c54u,y);W32(0x49c56u,z);
        W16(0x49c5au,fx);W16(0x49c5cu,fy);W16(0x49c5eu,fz);
    } else if(decision==1) {
        status=integrate(bus,1);if(status)return status;
    }
    W16(0x49ce2u,0);W16(0x49ce0u,0);W16(0x49cdeu,0);
    R16(0x49d16u,old_status);params[0]=old_status;params[1]=decision;
    /* Explicit low-word D2/D3 seeds for the camera debug branch. These
     * are register inputs, not original stack arguments. */
    CALL(0xf0fau,params,2);
    W16(0x49d16u,result&0x80000000u ? 0xffffu : 1u);
    R16(0x49d16u,new_status);
    if(old_status!=new_status)W16(0x49d18u,1);
    params[0]=0x49c4cu;CALL(0xeb04u,params,1);CALL(0x20820u,0,0);
    return BIWN_WORLD_OK;
}
