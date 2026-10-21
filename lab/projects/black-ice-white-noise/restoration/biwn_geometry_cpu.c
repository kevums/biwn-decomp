#include "biwn_geometry_cpu.h"
static uint32_t sx16(uint16_t v){return(uint32_t)(v&0x7fffu)-(uint32_t)(v&0x8000u);}
static uint32_t asr6(uint32_t v){return(v>>6)|(v&0x80000000u?0xfc000000u:0);}
static int less16(uint16_t a,uint16_t b){return(a^0x8000u)<(b^0x8000u);}
static int less32(uint32_t a,uint32_t b){return(a^0x80000000u)<(b^0x80000000u);}
static void word(struct biwn_task_cpu *s,unsigned r,uint16_t v){s->registers[r]=(s->registers[r]&0xffff0000u)|v;}
static void nz(struct biwn_task_cpu *s,uint32_t v,unsigned bits){uint32_t mask=bits==32?0xffffffffu:0xffffu,sign=1u<<(bits-1);v&=mask;s->sr=(uint16_t)((s->sr&0xfff0u)|(v?0:4)|(v&sign?8:0));}
static void xflag(struct biwn_task_cpu *s,unsigned x){s->sr=(uint16_t)((s->sr&~0x10u)|(x?0x10u:0));}
static void shiftword6(struct biwn_task_cpu *s,unsigned r){uint16_t v=(uint16_t)s->registers[r];word(s,r,(uint16_t)(v<<6));xflag(s,(v>>10)&1u);}
#define R16(a,v) do{if(bus->read16(bus->context,(a),&(v)))return BIWN_GEOMETRY_BUS_ERROR;}while(0)
#define R32(a,v) do{if(bus->read32(bus->context,(a),&(v)))return BIWN_GEOMETRY_BUS_ERROR;}while(0)
#define W16(a,v) do{if(bus->write16(bus->context,(a),(uint16_t)(v)))return BIWN_GEOMETRY_BUS_ERROR;}while(0)
#define W32(a,v) do{if(bus->write32(bus->context,(a),(v)))return BIWN_GEOMETRY_BUS_ERROR;}while(0)
static enum biwn_geometry_status bounds(struct biwn_world_bus *bus,struct biwn_task_cpu *s)
{
 uint16_t w;uint32_t value;uint32_t object=s->registers[10],record=s->registers[9];
 W16(object+66u,s->registers[1]);W32(object+68u,record);s->registers[2]=0xfffffc00u;
 R32(object+4u,s->registers[1]);s->registers[1]&=s->registers[2];R16(record+10u,w);word(s,0,w);shiftword6(s,0);s->registers[11]=s->registers[1]+sx16((uint16_t)s->registers[0]);W32(object+76u,s->registers[11]);
 R32(object+10u,s->registers[1]);s->registers[1]&=s->registers[2];R16(record+14u,w);word(s,0,w);shiftword6(s,0);s->registers[11]=s->registers[1]+sx16((uint16_t)s->registers[0]);W32(object+84u,s->registers[11]);
 R16(record+16u,w);word(s,0,w);shiftword6(s,0);s->registers[8]=sx16((uint16_t)s->registers[0]);R32(object+76u,value);s->registers[8]+=value;W32(object+72u,s->registers[8]);
 R16(record+18u,w);word(s,0,w);shiftword6(s,0);s->registers[8]=sx16((uint16_t)s->registers[0]);R32(object+84u,value);s->registers[8]+=value;W32(object+80u,s->registers[8]);
 s->registers[0]=1;nz(s,1,32);return BIWN_GEOMETRY_OK;
}
enum biwn_geometry_status biwn_geometry_cpu_body(struct biwn_world_bus *bus,struct biwn_task_cpu *state,uint32_t scan_limit)
{
 struct biwn_task_cpu s;uint32_t object,value,base,entry;uint16_t w,index,count,extent;int i,found=0;enum biwn_geometry_status status;
 if(!bus||!state||!bus->read16||!bus->read32||!bus->write16||!bus->write32||state->sr&0x2000u||
    (state->pc!=0x1028eu&&state->pc!=0x102c4u&&state->pc!=0x1039cu&&state->pc!=0x10652u)||(state->pc==0x102c4u&&!scan_limit))return BIWN_GEOMETRY_BAD_ARGUMENT;
 s=*state;entry=s.pc;
 if(entry==0x1028eu){
  R32(s.registers[15]+4u,s.registers[8]);object=s.registers[8];
  R32(object+4u,s.registers[1]);R32(object+30u,value);if(less32(s.registers[1],value))goto outside_early;
  R32(object+4u,s.registers[1]);R32(object+26u,value);if(!less32(s.registers[1],value))goto outside_early;
  R32(object+10u,s.registers[1]);R32(object+38u,value);if(less32(s.registers[1],value))goto outside_early;
  R32(object+10u,s.registers[1]);R32(object+34u,value);found=!less32(s.registers[1],value);word(&s,0,found?1u:0u);xflag(&s,found);nz(&s,(uint16_t)s.registers[0],16);if(found)s.sr|=1u;s.pc=0x102c2u;*state=s;return BIWN_GEOMETRY_OK;
outside_early:
  s.registers[0]=1;nz(&s,1,32);s.pc=0x1029eu;*state=s;return BIWN_GEOMETRY_OK;
 }
 if(entry==0x10652u){
  s.registers[15]-=4;W32(s.registers[15],s.registers[10]);R32(s.registers[15]+8u,s.registers[10]);object=s.registers[10];R16(s.registers[15]+12u,w);word(&s,1,w);index=w;R32(0x49c18u,s.registers[8]);R16(s.registers[8],count);
  if(less16(index,count)){
   s.registers[0]=sx16(index)*24u;s.registers[9]=s.registers[0];R32(s.registers[8]+4u,base);s.registers[9]+=base;W16(object+42u,index);W32(object+44u,s.registers[9]);
   for(i=0;i<4;i++){
    const uint32_t fields[4]={52u,60u,48u,56u},origins[4]={30u,38u,52u,60u};R16(s.registers[9]+2u+(uint32_t)i*2u,w);word(&s,0,w);shiftword6(&s,0);s.registers[8]=sx16((uint16_t)s.registers[0]);R32(object+origins[i],value);s.registers[8]+=value;W32(object+fields[i],s.registers[8]);
   }s.registers[0]=1;nz(&s,1,32);
  }else{word(&s,0,0);nz(&s,0,16);}
  R32(s.registers[15],s.registers[10]);s.registers[15]+=4;s.usp=s.registers[15];s.pc=0x106c2u;*state=s;return BIWN_GEOMETRY_OK;
 }
 for(i=11;i>=2;i--)if(i==2||i==10||i==11||(entry==0x102c4u&&i==3)){s.registers[15]-=4;W32(s.registers[15],s.registers[i]);}
 R32(s.registers[15]+(entry==0x102c4u?20u:16u),s.registers[10]);object=s.registers[10];
 if(entry==0x1039cu){R16(s.registers[15]+20u,w);word(&s,1,w);}
 R16(object+64u,w);s.registers[0]=sx16(w);xflag(&s,(s.registers[0]>>30)&1u);s.registers[0]<<=2;s.registers[8]=0x49bb4u;R32(s.registers[8]+s.registers[0],s.registers[8]);
 if(entry==0x1039cu){
  index=(uint16_t)s.registers[1];R16(s.registers[8],count);
  if(less16(index,count)){s.registers[0]=sx16(index)*20u;s.registers[9]=s.registers[0];R32(s.registers[8]+8u,base);s.registers[9]+=base;status=bounds(bus,&s);if(status)return status;}
  else{word(&s,0,0);nz(&s,0,16);}
 }else{
  R32(object+4u,value);s.registers[0]=asr6(value);xflag(&s,(value>>5)&1u);word(&s,3,(uint16_t)s.registers[0]&15u);
  R32(object+10u,value);s.registers[0]=asr6(value);xflag(&s,(value>>5)&1u);word(&s,2,(uint16_t)s.registers[0]&15u);
  R16(s.registers[8],count);index=(uint16_t)(count-1u);word(&s,1,index);xflag(&s,count==0);
  if(!(index&0x8000u))for(;;){
   if(!scan_limit)return BIWN_GEOMETRY_SCAN_LIMIT;--scan_limit;s.registers[0]=sx16(index)*20u;s.registers[9]=s.registers[0];R32(s.registers[8]+8u,base);s.registers[9]+=base;
   R16(s.registers[9]+10u,w);
   if(!less16((uint16_t)s.registers[3],w)){
    R16(s.registers[9]+10u,w);R16(s.registers[9]+16u,extent);value=(uint32_t)w+extent;word(&s,0,(uint16_t)value);xflag(&s,value>0xffffu);
    if(less16((uint16_t)s.registers[3],(uint16_t)s.registers[0])){
     R16(s.registers[9]+14u,w);
     if(!less16((uint16_t)s.registers[2],w)){
      R16(s.registers[9]+14u,w);R16(s.registers[9]+18u,extent);value=(uint32_t)w+extent;word(&s,0,(uint16_t)value);xflag(&s,value>0xffffu);
      if(less16((uint16_t)s.registers[2],(uint16_t)s.registers[0])){found=1;break;}
     }
    }
   }
   index=(uint16_t)(index-1u);word(&s,1,index);if(index==0xffffu)break;
  }
  if(found){status=bounds(bus,&s);if(status)return status;}else{word(&s,0,0);nz(&s,0,16);}
 }
 for(i=2;i<=11;i++)if(i==2||i==10||i==11||(entry==0x102c4u&&i==3)){R32(s.registers[15],s.registers[i]);s.registers[15]+=4;}
 s.usp=s.registers[15];s.pc=entry==0x102c4u?0x1039au:0x1042eu;*state=s;return BIWN_GEOMETRY_OK;
}
enum biwn_geometry_status biwn_geometry_cpu_call(struct biwn_world_bus *bus,struct biwn_task_cpu *state,uint32_t scan_limit)
{
 struct biwn_task_cpu s;enum biwn_geometry_status status;if(!state)return BIWN_GEOMETRY_BAD_ARGUMENT;s=*state;
 status=biwn_geometry_cpu_body(bus,&s,scan_limit);if(status)return status;R32(s.registers[15],s.pc);s.registers[15]+=4;s.usp=s.registers[15];*state=s;return BIWN_GEOMETRY_OK;
}
