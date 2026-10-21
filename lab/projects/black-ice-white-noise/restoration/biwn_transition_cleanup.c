#include "biwn_transition_cleanup.h"
struct state { struct biwn_world_bus *bus; uint32_t remaining; };
#define R16(a,v) do {if(s->bus->read16(s->bus->context,(a),&(v)))return BIWN_CLEANUP_BUS_ERROR;}while(0)
#define R32(a,v) do {if(s->bus->read32(s->bus->context,(a),&(v)))return BIWN_CLEANUP_BUS_ERROR;}while(0)
#define W16(a,v) do {if(s->bus->write16(s->bus->context,(a),(uint16_t)(v)))return BIWN_CLEANUP_BUS_ERROR;}while(0)
#define W32(a,v) do {if(s->bus->write32(s->bus->context,(a),(uint32_t)(v)))return BIWN_CLEANUP_BUS_ERROR;}while(0)
#define STEP() do {if(!s->remaining)return BIWN_CLEANUP_LIMIT;--s->remaining;}while(0)
#define CALL(f) do {enum biwn_cleanup_status status=(f);if(status)return status;}while(0)
static int32_t signed16(uint16_t v){return (int32_t)(v&0x7fffu)-(int32_t)(v&0x8000u);}
static int less16(uint16_t a,uint16_t b){return (a^0x8000u)<(b^0x8000u);}

/* [1AE56,1AE88): first matching reference, including negative counts. */
static enum biwn_cleanup_status texture(struct state *s,uint16_t id,uint32_t *d0)
{
    uint32_t i;uint16_t value;
    for(i=0;i<36u;++i){
        STEP();*d0=i*4u;R16(0x15b4a0u+*d0,value);
        if(value==id){R16(0x15b4a2u+*d0,value);if(value){R16(0x15b4a2u+*d0,value);W16(0x15b4a2u+*d0,(uint32_t)value-1u);}break;}
    }
    return BIWN_CLEANUP_OK;
}
/* [20CC4,20CF8): count and table pointer are deliberately reread. */
static enum biwn_cleanup_status room(struct state *s,uint32_t object,uint32_t *d0)
{
    uint16_t i=0,count,id;uint32_t table;
    R16(object+6u,count);
    while(less16(i,count)){
        STEP();*d0=(uint32_t)signed16(i)*2u;R32(object+20u,table);R16(table+*d0,id);CALL(texture(s,id,d0));
        i=(uint16_t)((uint32_t)i+1u);R16(object+6u,count);
    }
    return BIWN_CLEANUP_OK;
}
/* [20E40,20E8C): six consecutive IDs per group, base ID reread six times. */
static enum biwn_cleanup_status region(struct state *s,uint32_t object,uint32_t *d0)
{
    uint16_t index,count,group,k,id;uint32_t table;
    R16(object+2u,index);*d0=(uint32_t)(signed16(index)*6);R32(object+8u,table);table+=*d0;
    R16(table,count);table+=2u;
    for(group=0;less16(group,count);group=(uint16_t)((uint32_t)group+1u)){
        STEP();*d0=(uint32_t)signed16(group)*2u;
        for(k=0;k<6u;++k){R16(table+(uint32_t)group*2u,id);id=(uint16_t)((uint32_t)id+k);CALL(texture(s,id,d0));}
    }
    return BIWN_CLEANUP_OK;
}
/* [1545C,1557A): address-ordered free-list insertion/coalescing. */
static enum biwn_cleanup_status free_handle(struct state *s,uint32_t handle,uint32_t *d0)
{
    uint32_t block,size,value,head,next,previous,end;
    if(!handle)return BIWN_CLEANUP_OK;
    R32(handle,value);if(!value)return BIWN_CLEANUP_OK;
    R32(handle,block);block-=8u;R32(block,size);R32(0x112d64u,value);W32(0x112d64u,value+size);
    R32(0x112d60u,head);
    if(!head){W32(0x112d60u,block);W32(block+4u,0);W32(block+8u,0);}
    else{
        R32(0x112d60u,head);
        if(block<head){
            R32(block,size);end=block+size;R32(0x112d60u,head);
            if(end==head){
                R32(end+4u,next);W32(block+4u,next);R32(end,size);R32(block,value);W32(block,value+size);
                R32(end+4u,next);
                if(next){R32(end+4u,next);W32(next+8u,block);}
            }else{
                R32(0x112d60u,head);W32(block+4u,head);R32(0x112d60u,head);W32(head+8u,block);
            }
            W32(block+8u,0);W32(0x112d60u,block);
        }else{
            R32(0x112d60u,previous);R32(previous+4u,next);
            while(next){
                STEP();R32(previous+4u,next);
                if(block<next)break;
                R32(previous+4u,previous);R32(previous+4u,next);
            }
            if(next){
                R32(block,size);end=block+size;R32(previous+4u,next);
                if(end==next){
                    R32(end+4u,value);W32(block+4u,value);
                    if(value){R32(block+4u,value);W32(value+8u,block);}
                    R32(previous+4u,next);R32(next,size);R32(block,value);W32(block,value+size);
                }else{
                    R32(previous+4u,next);W32(block+4u,next);R32(previous+4u,next);W32(next+8u,block);
                }
                W32(block+8u,previous);R32(previous,size);*d0=previous+size;
                if(block==*d0){
                    R32(block,size);R32(previous,value);W32(previous,value+size);R32(block+4u,next);W32(previous+4u,next);
                    if(next){R32(block+4u,next);W32(next+8u,previous);}
                }else W32(previous+4u,block);
            }else{
                R32(previous,size);*d0=previous+size;
                if(block==*d0){R32(block,size);R32(previous,value);W32(previous,value+size);}
                else{W32(previous+4u,block);W32(block+4u,0);W32(block+8u,previous);}
            }
        }
    }
    W32(handle,0);return BIWN_CLEANUP_OK;
}
static enum biwn_cleanup_status reset_objects(struct state *s,uint32_t *d0)
{
    uint32_t i,handle;uint16_t active;
    for(i=0;i<40u;++i){STEP();*d0=i*206u;W16(0x49d6eu+*d0,1);}
    for(i=0;i<40u;++i){
        STEP();*d0=i*30u;R16(0x4bd9cu+*d0,active);
        if(active){R32(0x4bdb0u+*d0,handle);if(handle){R32(0x4bdb0u+*d0,handle);CALL(free_handle(s,handle,d0));}}
        *d0=i*30u;W16(0x4bd9cu+*d0,0);
    }
    return BIWN_CLEANUP_OK;
}
static enum biwn_cleanup_status reset_rooms(struct state *s,uint32_t *d0)
{
    uint32_t i,object;
    for(i=0;i<25u;++i){STEP();*d0=i*4u;R32(0x49bb4u+*d0,object);CALL(room(s,object,d0));}
    return reset_objects(s,d0);
}
static enum biwn_cleanup_status reset_region(struct state *s,uint32_t *d0)
{
    uint32_t object;R32(0x49c18u,object);CALL(region(s,object,d0));return reset_objects(s,d0);
}
/* Public wrappers commit original D0 only after complete success. */
#define BEGIN(mask) struct state state;uint32_t d0=incoming_d0;enum biwn_cleanup_status status; \
    if(!bus||!out_d0||!limit||((mask)&1u&&!bus->read16)||((mask)&2u&&!bus->read32)||((mask)&4u&&!bus->write16)||((mask)&8u&&!bus->write32))return BIWN_CLEANUP_BAD_ARGUMENT; \
    state.bus=bus;state.remaining=limit
#define END(f) status=(f);if(!status)*out_d0=d0;return status
enum biwn_cleanup_status biwn_cleanup_release_texture(struct biwn_world_bus *bus,uint16_t id,uint32_t limit,uint32_t *out_d0)
{uint32_t incoming_d0=0;BEGIN(5u);END(texture(&state,id,&d0));}
enum biwn_cleanup_status biwn_cleanup_release_room(struct biwn_world_bus *bus,uint32_t object,uint32_t incoming_d0,uint32_t limit,uint32_t *out_d0)
{BEGIN(7u);END(room(&state,object,&d0));}
enum biwn_cleanup_status biwn_cleanup_release_region(struct biwn_world_bus *bus,uint32_t object,uint32_t incoming_d0,uint32_t limit,uint32_t *out_d0)
{BEGIN(7u);END(region(&state,object,&d0));}
enum biwn_cleanup_status biwn_cleanup_free_handle(struct biwn_world_bus *bus,uint32_t handle,uint32_t incoming_d0,uint32_t limit,uint32_t *out_d0)
{BEGIN(10u);END(free_handle(&state,handle,&d0));}
enum biwn_cleanup_status biwn_cleanup_reset_rooms(struct biwn_world_bus *bus,uint32_t incoming_d0,uint32_t limit,uint32_t *out_d0)
{BEGIN(15u);END(reset_rooms(&state,&d0));}
enum biwn_cleanup_status biwn_cleanup_reset_region(struct biwn_world_bus *bus,uint32_t incoming_d0,uint32_t limit,uint32_t *out_d0)
{BEGIN(15u);END(reset_region(&state,&d0));}
