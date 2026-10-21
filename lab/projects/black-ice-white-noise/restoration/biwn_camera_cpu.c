#include "biwn_camera_cpu.h"
struct camera {struct biwn_world_bus *bus;struct biwn_task_cpu cpu;biwn_world_cpu_service service;void *context;};
static uint32_t sx16(uint16_t v){return(uint32_t)(v&0x7fffu)-(uint32_t)(v&0x8000u);}
static uint16_t sx8(uint8_t v){return(uint16_t)((uint16_t)(v&0x7fu)-(uint16_t)(v&0x80u));}
static int less32(uint32_t a,uint32_t b){return(a^0x80000000u)<(b^0x80000000u);}
static int greater16(uint16_t a,uint16_t b){return(a^0x8000u)>(b^0x8000u);}
static void word(struct camera *s,unsigned r,uint16_t v){s->cpu.registers[r]=(s->cpu.registers[r]&0xffff0000u)|v;}
static void byte(struct camera *s,unsigned r,uint8_t v){s->cpu.registers[r]=(s->cpu.registers[r]&0xffffff00u)|v;}
static void nz(struct camera *s,uint32_t v,unsigned bits){uint32_t mask=bits==32?0xffffffffu:(1u<<bits)-1u,sign=1u<<(bits-1);v&=mask;s->cpu.sr=(uint16_t)((s->cpu.sr&0xfff0u)|(v?0:4)|(v&sign?8:0));}
static void bit(struct camera *s,uint8_t v,unsigned n){s->cpu.sr=(uint16_t)((s->cpu.sr&~4u)|(v&(1u<<n)?0:4));}
static uint32_t arithmetic(struct camera *s,uint32_t a,uint32_t b,unsigned bits,int sub,int cmp){uint32_t mask=bits==32?0xffffffffu:(1u<<bits)-1u,sign=1u<<(bits-1),r;unsigned carry,ov;a&=mask;b&=mask;r=(sub?a-b:a+b)&mask;carry=sub?a<b:r<a;ov=sub?((a^b)&(a^r)&sign)!=0:((~(a^b))&(a^r)&sign)!=0;nz(s,r,bits);s->cpu.sr=(uint16_t)((s->cpu.sr&~(cmp?3u:0x13u))|(carry?(cmp?1u:0x11u):0)|(ov?2u:0));return r;}
static void shift(struct camera *s,unsigned r,unsigned bits,unsigned n,int arithmetic_shift){uint32_t v=s->cpu.registers[r],mask=bits==32?0xffffffffu:0xffffu,sign=1u<<(bits-1),result;unsigned c;v&=mask;c=(v>>(n-1))&1u;result=v>>n;if(arithmetic_shift&&(v&sign))result|=mask^(mask>>n);if(bits==32)s->cpu.registers[r]=result;else word(s,r,(uint16_t)result);nz(s,result,bits);s->cpu.sr=(uint16_t)((s->cpu.sr&~0x11u)|(c?0x11u:0));}
#define R8(a,v) do{if(s.bus->read8(s.bus->context,(a),&(v)))return BIWN_WORLD_CPU_BUS_ERROR;}while(0)
#define R16(a,v) do{if(s.bus->read16(s.bus->context,(a),&(v)))return BIWN_WORLD_CPU_BUS_ERROR;}while(0)
#define R32(a,v) do{if(s.bus->read32(s.bus->context,(a),&(v)))return BIWN_WORLD_CPU_BUS_ERROR;}while(0)
#define W8(a,v) do{if(write8(s.bus->context,(a),(uint8_t)(v)))return BIWN_WORLD_CPU_BUS_ERROR;}while(0)
#define W16(a,v) do{if(s.bus->write16(s.bus->context,(a),(uint16_t)(v)))return BIWN_WORLD_CPU_BUS_ERROR;}while(0)
#define W32(a,v) do{if(s.bus->write32(s.bus->context,(a),(v)))return BIWN_WORLD_CPU_BUS_ERROR;}while(0)
#define CHECK(e) do{int status=(e);if(status)return(enum biwn_world_cpu_status)status;}while(0)
#define POP(n) do{s.cpu.registers[15]+=(n);s.cpu.usp=s.cpu.registers[15];}while(0)
static int push(struct camera *s,uint32_t v,unsigned width,int moved){s->cpu.registers[15]-=width;s->cpu.usp=s->cpu.registers[15];if(width==2){if(s->bus->write16(s->bus->context,s->cpu.registers[15],(uint16_t)v))return 2;}else if(s->bus->write32(s->bus->context,s->cpu.registers[15],v))return 2;if(moved)nz(s,v,width*8);return 0;}
static int call(struct camera *s,uint32_t target,uint32_t ret){uint32_t sp;int status=push(s,ret,4,0);if(status)return status;s->cpu.pc=target;sp=s->cpu.registers[15];if(s->service(s->context,s->bus,&s->cpu,target))return 3;if(s->cpu.registers[15]!=sp)return 5;if(s->bus->read32(s->bus->context,sp,&s->cpu.pc))return 2;s->cpu.registers[15]+=4;s->cpu.usp=s->cpu.registers[15];return s->cpu.pc==ret?0:5;}
enum biwn_world_cpu_status biwn_camera_cpu_body(struct biwn_world_bus *bus,struct biwn_task_cpu *state,biwn_camera_cpu_write8 write8,biwn_world_cpu_service service,void *context)
{
 struct camera s;uint32_t v,other;uint16_t w;uint8_t b;unsigned i;
 if(!bus||!state||!write8||!service||!bus->read8||!bus->read16||!bus->read32||!bus->write16||!bus->write32||state->sr&0x2000u||state->pc!=0xf0fau)return BIWN_WORLD_CPU_BAD_ARGUMENT;
 s.bus=bus;s.cpu=*state;s.service=service;s.context=context;
 for(i=14;i-->2;)if(i<=4||i>=10)CHECK(push(&s,s.cpu.registers[i],4,0));
 s.cpu.registers[8]=0x49ba4u;R8(0x49ba7u,b);nz(&s,b,8);
 if(b&0x80u){
  R8(s.cpu.registers[8]+1u,b);bit(&s,b,4);if(b&0x10u){R32(0x49b98u,v);v=arithmetic(&s,v,1,32,0,0);W32(0x49b98u,v);R32(0x49b98u,v);arithmetic(&s,v,255,32,1,1);if(less32(255,v)){W32(0x49b98u,0);nz(&s,0,32);}}
  R8(0x49ba5u,b);bit(&s,b,5);if(b&0x20u){R32(0x49b98u,v);v=arithmetic(&s,v,1,32,1,0);W32(0x49b98u,v);if(v&0x80000000u){W32(0x49b98u,255);nz(&s,255,32);}}
  R8(0x49ba5u,b);bit(&s,b,6);if(b&0x40u){R32(0x49b9cu,v);v=arithmetic(&s,v,1,32,0,0);W32(0x49b9cu,v);R32(0x49b9cu,v);arithmetic(&s,v,255,32,1,1);if(less32(255,v)){W32(0x49b9cu,0);nz(&s,0,32);}}
  R8(0x49ba5u,b);nz(&s,b,8);if(b&0x80u){R32(0x49b9cu,v);v=arithmetic(&s,v,1,32,1,0);W32(0x49b9cu,v);if(v&0x80000000u){W32(0x49b9cu,255);nz(&s,255,32);}}
  R8(0x49ba5u,b);bit(&s,b,3);if(b&8u){R32(0x49ba0u,v);v=arithmetic(&s,v,1,32,0,0);W32(0x49ba0u,v);R32(0x49ba0u,v);arithmetic(&s,v,255,32,1,1);if(less32(255,v)){W32(0x49ba0u,0);nz(&s,0,32);}}
  R8(0x49ba7u,b);bit(&s,b,3);if(b&8u){R32(0x49ba0u,v);v=arithmetic(&s,v,1,32,1,0);W32(0x49ba0u,v);if(v&0x80000000u){W32(0x49ba0u,255);nz(&s,255,32);}}
  s.cpu.registers[8]=0x49ba4u;R8(s.cpu.registers[8]+1u,b);bit(&s,b,0);if(b&1u){R16(0x47b9cu,w);W16(0x47b9cu,arithmetic(&s,w,8,16,1,0));R16(0x49b8eu,w);W16(0x49b8eu,arithmetic(&s,w,8,16,1,0));}
  R8(s.cpu.registers[8]+3u,b);bit(&s,b,0);if(b&1u){R16(0x47b9cu,w);W16(0x47b9cu,arithmetic(&s,w,8,16,0,0));R16(0x49b8eu,w);W16(0x49b8eu,arithmetic(&s,w,8,16,0,0));}
 }else{
  R16(0x3c840u,w);arithmetic(&s,w,120,16,1,1);if(greater16(w,120)){W16(0x3c840u,0);nz(&s,0,16);}else{R16(0x3c840u,w);W16(0x3c840u,arithmetic(&s,w,1,16,0,0));}
  R16(0x3c840u,w);arithmetic(&s,w,60,16,1,1);if(greater16(w,60)){R16(0x3c840u,w);word(&s,0,w);nz(&s,w,16);word(&s,0,(uint16_t)arithmetic(&s,s.cpu.registers[0],0xffa6u,16,0,0));}else{s.cpu.registers[0]=30;nz(&s,30,32);R16(0x3c840u,w);word(&s,0,(uint16_t)arithmetic(&s,s.cpu.registers[0],w,16,1,0));}
  s.cpu.registers[13]=sx16((uint16_t)s.cpu.registers[0]);W32(0x3c846u,s.cpu.registers[13]);nz(&s,s.cpu.registers[13],32);s.cpu.registers[10]=0xe540u;s.cpu.registers[4]=27;nz(&s,27,32);W32(0x3c846u,s.cpu.registers[4]);nz(&s,s.cpu.registers[4],32);R16(0x49cdcu,w);s.cpu.registers[12]=sx16(w);CHECK(push(&s,27,4,0));CHECK(push(&s,s.cpu.registers[12],4,1));CHECK(call(&s,s.cpu.registers[10],0xf252u));POP(8);s.cpu.registers[2]=s.cpu.registers[0];nz(&s,s.cpu.registers[2],32);R16(0x49cd8u,w);s.cpu.registers[11]=sx16(w);
  R32(0x3c842u,v);CHECK(push(&s,v,4,1));CHECK(push(&s,s.cpu.registers[11],4,1));CHECK(call(&s,s.cpu.registers[10],0xf266u));POP(8);s.cpu.registers[2]=arithmetic(&s,s.cpu.registers[2],s.cpu.registers[0],32,1,0);s.cpu.registers[3]=s.cpu.registers[2];nz(&s,s.cpu.registers[3],32);s.cpu.registers[4]=14;nz(&s,14,32);shift(&s,3,32,14,1);
  R32(0x3c842u,v);CHECK(push(&s,v,4,1));CHECK(push(&s,s.cpu.registers[12],4,1));CHECK(call(&s,s.cpu.registers[10],0xf27au));POP(8);s.cpu.registers[2]=s.cpu.registers[0];nz(&s,s.cpu.registers[2],32);CHECK(push(&s,27,4,0));CHECK(push(&s,s.cpu.registers[11],4,1));CHECK(call(&s,s.cpu.registers[10],0xf286u));POP(8);s.cpu.registers[2]=arithmetic(&s,s.cpu.registers[2],s.cpu.registers[0],32,0,0);s.cpu.registers[2]=arithmetic(&s,0,s.cpu.registers[2],32,1,0);shift(&s,2,32,14,1);R32(0x49cc0u,s.cpu.registers[13]);s.cpu.registers[13]+=8;W32(0x49b98u,s.cpu.registers[13]);nz(&s,s.cpu.registers[13],32);W32(0x49ba0u,0);nz(&s,0,32);
 }
 s.cpu.registers[9]=0x47b9au;W16(s.cpu.registers[9],s.cpu.registers[3]);nz(&s,s.cpu.registers[3],16);R16(0x49ce0u,w);W16(0x47b9cu,w);nz(&s,w,16);s.cpu.registers[8]=0x47b9eu;W16(s.cpu.registers[8],s.cpu.registers[2]);nz(&s,s.cpu.registers[2],16);s.cpu.registers[10]=0x49cbau;R8(s.cpu.registers[10],b);byte(&s,0,b);nz(&s,b,8);byte(&s,0,(uint8_t)arithmetic(&s,s.cpu.registers[0],0xc0u,8,0,0));arithmetic(&s,s.cpu.registers[0],0x80u,8,1,1);
 if((uint8_t)s.cpu.registers[0]>0x80u){R16(0x49ce2u,w);word(&s,4,w);nz(&s,w,16);word(&s,4,(uint16_t)arithmetic(&s,s.cpu.registers[4],s.cpu.registers[2],16,1,0));CHECK(push(&s,s.cpu.registers[4],2,1));R16(0x49cdeu,w);s.cpu.registers[13]=sx16(w);R16(s.cpu.registers[9],w);s.cpu.registers[13]-=sx16(w);CHECK(push(&s,s.cpu.registers[13],2,1));CHECK(call(&s,0x13440u,0xf2e8u));word(&s,0,sx8((uint8_t)s.cpu.registers[0]));nz(&s,s.cpu.registers[0],16);R8(s.cpu.registers[10],b);byte(&s,1,b);nz(&s,b,8);word(&s,1,sx8((uint8_t)s.cpu.registers[1]));nz(&s,s.cpu.registers[1],16);word(&s,0,(uint16_t)arithmetic(&s,s.cpu.registers[0],s.cpu.registers[1],16,0,0));shift(&s,0,16,1,1);s.cpu.registers[13]=sx16((uint16_t)s.cpu.registers[0]);W32(0x49b9cu,s.cpu.registers[13]);nz(&s,s.cpu.registers[13],32);
 }else{R16(0x49ce2u,w);word(&s,4,w);nz(&s,w,16);R16(s.cpu.registers[8],w);word(&s,4,(uint16_t)arithmetic(&s,s.cpu.registers[4],w,16,1,0));CHECK(push(&s,s.cpu.registers[4],2,1));R16(0x49cdeu,w);s.cpu.registers[13]=sx16(w);R16(s.cpu.registers[9],w);s.cpu.registers[13]-=sx16(w);CHECK(push(&s,s.cpu.registers[13],2,1));CHECK(call(&s,0x13440u,0xf316u));word(&s,0,(uint16_t)s.cpu.registers[0]&255u);nz(&s,s.cpu.registers[0],16);word(&s,1,0);nz(&s,0,16);R8(s.cpu.registers[10],b);byte(&s,1,b);nz(&s,b,8);word(&s,0,(uint16_t)arithmetic(&s,s.cpu.registers[0],s.cpu.registers[1],16,0,0));shift(&s,0,16,1,0);W32(0x49b9cu,0);nz(&s,0,32);W8(0x49b9fu,s.cpu.registers[0]);nz(&s,s.cpu.registers[0],8);}
 W32(s.cpu.registers[15],0);nz(&s,0,32);R32(0x49ba0u,v);CHECK(push(&s,v,4,1));R32(0x49b9cu,v);CHECK(push(&s,v,4,1));R32(0x49b98u,v);CHECK(push(&s,v,4,1));CHECK(push(&s,0x47b88u,4,0));CHECK(call(&s,0xe220u,0xf34eu));R32(0x3c846u,s.cpu.registers[0]);nz(&s,s.cpu.registers[0],32);POP(20);
 for(i=2;i<=13;i++)if(i<=4||i>=10){R32(s.cpu.registers[15],other);s.cpu.registers[i]=other;POP(4);}s.cpu.pc=0xf35cu;*state=s.cpu;return BIWN_WORLD_CPU_OK;
}
enum biwn_world_cpu_status biwn_camera_cpu_call(struct biwn_world_bus *bus,struct biwn_task_cpu *state,biwn_camera_cpu_write8 write8,biwn_world_cpu_service service,void *context)
{struct biwn_task_cpu cpu;enum biwn_world_cpu_status status;uint32_t pc;if(!state)return BIWN_WORLD_CPU_BAD_ARGUMENT;cpu=*state;status=biwn_camera_cpu_body(bus,&cpu,write8,service,context);if(status)return status;if(bus->read32(bus->context,cpu.registers[15],&pc))return BIWN_WORLD_CPU_BUS_ERROR;cpu.pc=pc;cpu.registers[15]+=4;cpu.usp=cpu.registers[15];*state=cpu;return BIWN_WORLD_CPU_OK;}
