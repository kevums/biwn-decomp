#include "biwn_input_dispatch.h"
#define R8(a,v) do {if(bus->read8(bus->context,(a),&(v)))return BIWN_DISPATCH_BUS_ERROR;}while(0)
#define R16(a,v) do {if(bus->read16(bus->context,(a),&(v)))return BIWN_DISPATCH_BUS_ERROR;}while(0)
#define R32(a,v) do {if(bus->read32(bus->context,(a),&(v)))return BIWN_DISPATCH_BUS_ERROR;}while(0)
#define W8(a,v) do {if(write8(bus->context,(a),(uint8_t)(v)))return BIWN_DISPATCH_BUS_ERROR;}while(0)
#define W16(a,v) do {if(bus->write16(bus->context,(a),(uint16_t)(v)))return BIWN_DISPATCH_BUS_ERROR;}while(0)
#define W32(a,v) do {if(bus->write32(bus->context,(a),(uint32_t)(v)))return BIWN_DISPATCH_BUS_ERROR;}while(0)
#define CALL(a,args,n) do {if(bus->call(bus->context,(a),(args),(n),&d0))return BIWN_DISPATCH_DEPENDENCY_ERROR;}while(0)
#define TRY(expr) do {enum biwn_dispatch_status status=(expr);if(status)return status;}while(0)
#define STEP() do {if(!budget--)return BIWN_DISPATCH_LIMIT;}while(0)
static uint32_t sx(uint16_t v){return (uint32_t)(v&0x7fffu)-(uint32_t)(v&0x8000u);}
static int positive(uint16_t v){return v && !(v&0x8000u);}
static uint16_t asr14(uint16_t v){return (uint16_t)((v>>14)|((v&0x8000u)?0xfffcu:0));}

static enum biwn_dispatch_status animation(struct biwn_world_bus *bus,
 uint32_t table,uint32_t *d0,int fixed_slot)
{
 uint16_t actor,slot;uint32_t pointer,value;
 R16(0x49c4cu,actor);pointer=table+sx(actor)*20u;
 if(fixed_slot)*d0=sx(actor);
 else {R16(0x49d5au,slot);*d0=sx(slot)*4u;pointer+=*d0;}
 R32(pointer,value);W32(0x49cb4u,value);return BIWN_DISPATCH_OK;
}
static enum biwn_dispatch_status turn(struct biwn_world_bus *bus,
 biwn_input_write8 write8,int right)
{
 uint32_t counter=right?0x4624eu:0x4624cu;
 uint16_t word;uint8_t delta,angle;
 R16(counter,word);W16(counter,(uint32_t)word+1u);
 R8(counter+1u,delta);R8(0x49cbau,angle);
 W8(0x49cbau,right?(uint32_t)angle+delta:(uint32_t)angle-delta);
 /* Original adds the pre-clamp low byte, then clamps the signed counter. */
 R16(counter,word);if(positive(word)&&word>7u)W16(counter,7);
 W16(right?0x4624cu:0x4624eu,0);return BIWN_DISPATCH_OK;
}

static enum biwn_dispatch_status animate_wait(struct biwn_world_bus *bus,
 uint32_t *remaining,uint32_t *result)
{
 uint32_t d0=*result,pointer,arg=0x49c4cu,budget=*remaining;uint8_t byte;
 do {STEP();CALL(0xeb04u,&arg,1);CALL(0xdf60u,0,0);
  R32(0x49cb0u,pointer);R8(pointer+2u,byte);
 }while(!byte);
 *remaining=budget;*result=d0;return BIWN_DISPATCH_OK;
}

static enum biwn_dispatch_status equipment(struct biwn_world_bus *bus,
 uint32_t *remaining,uint32_t *result)
{
 uint16_t slot,actor,index,item,id,mode,stored_y;
 uint32_t d0=*result,pointer,handle,bytes,params[1],clock,stored_x,stored_z,saved;
 uint8_t byte;
 R16(0x49d5au,slot);
 if(positive(slot)) {
  TRY(animation(bus,0x45db8u,&d0,0));TRY(animate_wait(bus,remaining,&d0));
  R16(0x49c4cu,actor);R16(0x49d5au,slot);
  R16(0x45d9au+sx(actor)*10u+sx(slot)*2u,id);params[0]=id;CALL(0x1b002u,params,1);
  W16(0x49d5au,0);R16(0x49c4cu,actor);
  R16(0x45d9au+sx(actor)*10u,id);params[0]=id;CALL(0x1af04u,params,1);
  W32(0x49ca4u,d0);R32(0x49caau,handle);params[0]=handle;CALL(0x1545cu,params,1);
  R32(0x49ca4u,pointer);R32(pointer,pointer);R32(pointer+8u,bytes);
  params[0]=bytes*2u+16u;CALL(0x152a2u,params,1);W32(0x49caau,d0);
  R32(0x49caau,pointer);R32(pointer,pointer);W32(pointer,0x2c000u);
 }else {
  R16(0x49d54u,index);R16(0x49d2cu+sx(index)*2u,item);
  R8(0x461beu+sx(item),byte);
  if(byte) {
   R16(0x49c4cu,actor);R16(0x49d5au,slot);
   R16(0x45d9au+sx(actor)*10u+sx(slot)*2u,id);params[0]=id;CALL(0x1b002u,params,1);
   R16(0x49d54u,index);R16(0x49d2cu+sx(index)*2u,item);R8(0x461beu+sx(item),byte);
   slot=(uint16_t)((uint16_t)(byte&0x7fu)-(uint16_t)(byte&0x80u));W16(0x49d5au,slot);
   R16(0x49c4cu,actor);R16(0x45d9au+sx(actor)*10u+sx(slot)*2u,id);
   params[0]=id;CALL(0x1af04u,params,1);W32(0x49ca4u,d0);
   R32(0x49caau,handle);params[0]=handle;CALL(0x1545cu,params,1);
   R32(0x49ca4u,pointer);R32(pointer,pointer);R32(pointer+8u,bytes);
   params[0]=bytes*2u+16u;CALL(0x152a2u,params,1);W32(0x49caau,d0);
   R32(0x49caau,pointer);R32(pointer,pointer);W32(pointer,0x2c000u);
   TRY(animation(bus,0x45df4u,&d0,0));TRY(animate_wait(bus,remaining,&d0));
  }else {
   /* Repeated reads of the selected inventory item are deliberate. */
   R16(0x49d2cu+sx(index)*2u,item);d0=(d0&0xffff0000u)|(uint16_t)(item+0xffbfu);
   if((uint16_t)d0>1u) {
    R16(0x49d2cu+sx(index)*2u,item);d0=(d0&0xffff0000u)|(uint16_t)(item+0xffbdu);
    if((uint16_t)d0>1u) {
     R16(0x49d2cu+sx(index)*2u,item);if(item==0x45u)goto transition;
     R16(0x49d2cu+sx(index)*2u,item);if(item!=0x66u)goto item_done;
    }
   }
transition:
   R32(0x778ccu,clock);R16(0x49b8cu,item);stored_x=sx(item);
   R16(0x49b8eu,stored_y);R16(0x49b90u,item);stored_z=sx(item);
   CALL(0x1aadeu,0,0);saved=d0;CALL(0xdf22u,0,0);CALL(0x11e6cu,0,0);
   W16(0x49b8cu,stored_x);W16(0x49b8eu,stored_y);W16(0x49b90u,stored_z);
   CALL(0x18160u,0,0);R16(0x49c60u,mode);params[0]=mode==1u?1u:2u;
   CALL(0x1aa40u,params,1);params[0]=saved;CALL(0x1ab2au,params,1);
   CALL(0xdf3eu,0,0);W32(0x778ccu,clock);
item_done:
   R16(0x49d54u,index);d0=sx(index)*2u;R16(0x49d2cu+d0,item);
   if(item==0x46u){CALL(0x18e92u,0,0);*result=d0;return BIWN_DISPATCH_OK;}
  }
 }
 R32(0x49cb0u,pointer);W32(0x49cb4u,pointer);*result=d0;return BIWN_DISPATCH_OK;
}

enum biwn_dispatch_status biwn_input_dispatch(struct biwn_world_bus *bus,
 biwn_input_write8 write8,uint32_t loop_budget,uint32_t incoming_d0,uint32_t *out_d0)
{
 static const uint16_t offsets[13]={0x0c84,0x001a,0x05c6,0x05e0,0x0610,0x0640,0x0774,0x07c8,0x0952,0x0a50,0x0ad6,0x0bdc,0x0c2c};
 uint32_t d0=incoming_d0,pointer,value,params[2],budget=loop_budget,scale=3u;
 uint16_t word,delta,state,offset;uint8_t byte;int negative=0;
 if(!bus||!write8||!out_d0||!loop_budget||!bus->read8||!bus->read16||!bus->read32||!bus->write16||!bus->write32||!bus->call)return BIWN_DISPATCH_BAD_ARGUMENT;
 R16(0x4624au,word);if(!word){W16(0x4624cu,0);W16(0x4624eu,0);}W16(0x4624au,0);
 R16(0x49d62u,word);if(positive(word)){R16(0x4c24eu,delta);R16(0x49d62u,word);W16(0x49d62u,(uint32_t)word-delta);}
 R16(0x49c4eu,word);
 if(word) {
  R16(0x49c4eu,delta);R16(0x49d14u,word);W16(0x49d14u,(uint32_t)word-delta);W16(0x49c4eu,0);
  TRY(animation(bus,0x4613cu,&d0,0));W16(0x49cb8u,12);W32(0x49cc4u,0);W32(0x49cc8u,0);
 }
 R16(0x49cb8u,word);if(word!=1u)W16(0x46250u,300);
 R16(0x49cb8u,word);if(word>12u)goto done;
 R16(0x49cb8u,state);d0=(uint32_t)state*2u;R16(0x192a2u+d0,offset);d0=(d0&0xffff0000u)|offset;
 if(state>12u||offset!=offsets[state])return BIWN_DISPATCH_UNSUPPORTED_TABLE;
 switch(state) {
 case 0:goto done;
 case 1:
  R16(0x49c60u,word);
  if(word==2u){R32(0x49c78u,pointer);R16(pointer,word);
   if(word&0x8000u){R16(0x46250u,word);
    if(positive(word)){R16(0x4c24eu,delta);R16(0x46250u,word);W16(0x46250u,(uint32_t)word-delta);}
    else {do {STEP();CALL(0x190bcu,0,0);
      do {STEP();CALL(0xe4c0u,0,0);R32(0x49ba4u,value);}while(!value);
      CALL(0x1a0f8u,0,0);R32(0x49ba4u,d0);d0&=0x300000u;
     }while(d0);W16(0x46250u,300);}
   }
  }
  R8(0x49ba4u,byte);
  if(byte&0x20u){R8(0x49ba4u,byte);
   if(byte&2u){R8(0x49ba5u,byte);if(!(byte&0x10u))goto action2;
    R16(0x49d5au,word);if(word)goto action2;
    TRY(animation(bus,0x46088u,&d0,1));W16(0x49cb8u,2);goto done;
   }
   TRY(animation(bus,0x46010u,&d0,0));W16(0x49cb8u,2);goto done;
  }
  R8(0x49ba4u,byte);
  if(byte&2u){
   R8(0x49ba5u,byte);if(byte&0x40u){TRY(animation(bus,0x45f20u,&d0,0));W16(0x49cb8u,3);goto done;}
   R8(0x49ba5u,byte);if(byte&0x80u){TRY(animation(bus,0x45f5cu,&d0,0));W16(0x49cb8u,4);goto done;}
   R8(0x49ba5u,byte);if(byte&0x20u){TRY(animation(bus,0x45f98u,&d0,0));W32(0x49cc4u,0);W32(0x49cc8u,0);W16(0x49cb8u,10);goto done;}
   R8(0x49ba5u,byte);if(byte&0x10u){TRY(animation(bus,0x460c4u,&d0,0));W16(0x49cb8u,11);goto done;}
   R8(0x49ba6u,byte);if(byte&0x20u)TRY(equipment(bus,&budget,&d0));goto done;
  }
  R8(0x49ba5u,byte);if(byte&0x10u){TRY(animation(bus,0x45e6cu,&d0,0));W16(0x49cb8u,5);goto done;}
  R8(0x49ba5u,byte);if(byte&0x20u){TRY(animation(bus,0x45ea8u,&d0,0));W16(0x49cb8u,7);goto done;}
  R8(0x49ba5u,byte);if(byte&0x40u){TRY(turn(bus,write8,1));goto turn_idle;}
  R8(0x49ba5u,byte);if(!(byte&0x80u))goto done;TRY(turn(bus,write8,0));
turn_idle:W16(0x4624au,1);W16(0x46250u,300);goto done;
 case 2:
  R32(0x49cb0u,pointer);R8(pointer+2u,byte);if(byte&2u)CALL(0x18df2u,0,0);goto finished_animation;
 case 3:case 4:
  for(unsigned i=0;i<3u;i++){
   R16(0x49cccu+i*2u,word);d0=(d0&0xffff0000u)|asr14(word);
   R16(0x49cdeu+i*2u,word);W16(0x49cdeu+i*2u,state==3u?(uint32_t)word-(uint16_t)d0:(uint32_t)word+(uint16_t)d0);
  }goto finished_animation;
 case 5:
  R8(0x49ba6u,byte);if(byte&0x20u){TRY(animation(bus,0x45ee4u,&d0,0));W16(0x49cb8u,8);}
  R8(0x49ba5u,byte);if(!(byte&0x10u))goto reset_idle;
  R8(0x49ba5u,byte);if(byte&0x40u){TRY(turn(bus,write8,1));W16(0x4624au,1);goto forward;}
  R8(0x49ba5u,byte);if(byte&0x80u){TRY(turn(bus,write8,0));W16(0x4624au,1);goto forward;}
  R8(0x49ba4u,byte);if(byte&2u){TRY(animation(bus,0x46100u,&d0,0));W16(0x49cb8u,6);goto done;}
forward:scale=3u;goto integrate;
 case 6:
  R32(0x49cb0u,pointer);R8(pointer+2u,byte);if(byte&1u){TRY(animation(bus,0x45e6cu,&d0,0));W16(0x49cb8u,5);}goto forward;
 case 7:
  R8(0x49ba5u,byte);if(!(byte&0x20u))goto reset_idle;
  R8(0x49ba4u,byte);if(byte&2u){TRY(animation(bus,0x45f98u,&d0,0));W32(0x49cc4u,0);W16(0x49cb8u,10);goto done;}
  R8(0x49ba5u,byte);if(byte&0x40u){TRY(turn(bus,write8,1));W16(0x4624au,1);}
  else {R8(0x49ba5u,byte);if(byte&0x80u){TRY(turn(bus,write8,0));W16(0x4624au,1);}}
  scale=3u;negative=1;goto integrate;
 case 8:
  R8(0x49ba6u,byte);if(!(byte&0x20u)){TRY(animation(bus,0x45e6cu,&d0,0));W16(0x49cb8u,5);}
  R8(0x49ba5u,byte);if(!(byte&0x10u))goto reset_idle;
  R8(0x49ba5u,byte);if(byte&0x40u){TRY(turn(bus,write8,1));W16(0x4624au,1);goto run;}
  R8(0x49ba5u,byte);if(byte&0x80u){TRY(turn(bus,write8,0));W16(0x4624au,1);goto run;}
  R8(0x49ba4u,byte);if(byte&2u){TRY(animation(bus,0x46100u,&d0,0));W16(0x49cb8u,9);goto done;}
run:scale=9u;goto integrate;
 case 9:
  R32(0x49cb0u,pointer);R8(pointer+2u,byte);if(byte&1u){TRY(animation(bus,0x45ee4u,&d0,0));W16(0x49cb8u,8);}goto run;
 case 10:
  R8(0x49ba5u,byte);if(byte&0x40u){TRY(turn(bus,write8,1));W16(0x4624au,1);}
  else {R8(0x49ba5u,byte);if(byte&0x80u){TRY(turn(bus,write8,0));W16(0x4624au,1);}}
  R32(0x49ba4u,d0);d0&=0x2200000u;
  if(d0!=0x2200000u){TRY(animation(bus,0x45fd4u,&d0,0));W16(0x49cb8u,1);goto done;}
  R8(0x49ba4u,byte);if(!(byte&0x20u))goto done;R16(0x49d5au,word);if(!word)goto done;goto action2;
 case 11:goto finished_animation;
 case 12:
  R32(0x49cb0u,pointer);R8(pointer+2u,byte);if(byte&1u){TRY(animation(bus,0x45e30u,&d0,0));W32(0x49cc4u,0);W32(0x49cc8u,0);W16(0x49cb8u,1);}
  W32(0x49cc4u,0);W32(0x49cc8u,0);goto done;
 }
finished_animation:R32(0x49cb0u,pointer);R8(pointer+2u,byte);if(!(byte&1u))goto done;
reset_idle:TRY(animation(bus,0x45e30u,&d0,0));W32(0x49cc4u,0);W32(0x49cc8u,0);W16(0x49cb8u,1);goto done;
action2:TRY(animation(bus,0x4604cu,&d0,0));W16(0x49cb8u,2);goto done;
integrate:
 R32(0x4c24cu,value);
 /* Long scale, then word shift/swap/clear: upper half of the scaled
  * long is discarded, not a 32-bit shift of the full scaled value. */
 d0=(uint32_t)(uint16_t)(value*scale*8u)<<16;
 if(negative){d0=0u-d0;}
 params[0]=d0;params[1]=300;CALL(0xe588u,params,2);
 R32(0x49cc8u,value);d0=negative?d0-value:d0+value;W32(0x49cc4u,d0);
 R16(0x49cc6u,word);value=negative?0u-word:word;W32(0x49cc8u,value);
 d0=sx((uint16_t)(d0>>16));W32(0x49cc4u,d0);
done:*out_d0=d0;return BIWN_DISPATCH_OK;
}
