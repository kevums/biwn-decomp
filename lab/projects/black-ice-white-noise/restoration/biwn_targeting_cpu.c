#include "biwn_targeting_cpu.h"
struct target {struct biwn_world_bus *bus;struct biwn_task_cpu cpu;biwn_world_cpu_service service;void *context;};
static uint32_t sx16(uint16_t v){return(uint32_t)(v&0x7fffu)-(uint32_t)(v&0x8000u);}
static uint16_t sx8(uint8_t v){return(uint16_t)((uint16_t)(v&0x7fu)-(uint16_t)(v&0x80u));}
static int lt(uint32_t a,uint32_t b,unsigned bits){uint32_t mask=bits==32?0xffffffffu:(1u<<bits)-1u,sign=1u<<(bits-1);return((a&mask)^sign)<((b&mask)^sign);}
static void word(struct target *s,unsigned r,uint16_t v){s->cpu.registers[r]=(s->cpu.registers[r]&0xffff0000u)|v;}
static void byte(struct target *s,unsigned r,uint8_t v){s->cpu.registers[r]=(s->cpu.registers[r]&0xffffff00u)|v;}
static void nz(struct target *s,uint32_t v,unsigned bits){uint32_t mask=bits==32?0xffffffffu:(1u<<bits)-1u,sign=1u<<(bits-1);v&=mask;s->cpu.sr=(uint16_t)((s->cpu.sr&0xfff0u)|(v?0:4)|(v&sign?8:0));}
static uint32_t alu(struct target *s,uint32_t a,uint32_t b,unsigned bits,int sub,int cmp){uint32_t mask=bits==32?0xffffffffu:(1u<<bits)-1u,sign=1u<<(bits-1),r;unsigned carry,ov;a&=mask;b&=mask;r=(sub?a-b:a+b)&mask;carry=sub?a<b:r<a;ov=sub?((a^b)&(a^r)&sign)!=0:((~(a^b))&(a^r)&sign)!=0;nz(s,r,bits);s->cpu.sr=(uint16_t)((s->cpu.sr&~(cmp?3u:0x13u))|(carry?(cmp?1u:0x11u):0)|(ov?2u:0));return r;}
static void shift(struct target *s,unsigned r,unsigned bits,unsigned n,int left){uint32_t mask=bits==32?0xffffffffu:(1u<<bits)-1u,sign=1u<<(bits-1),v=s->cpu.registers[r]&mask;unsigned c=0,ov=0,i;
 for(i=0;i<n;i++){if(left){uint32_t old=v;c=(v&sign)!=0;v=(v<<1)&mask;ov|=((old^v)&sign)!=0;}else{c=v&1u;v=(v>>1)|(v&sign);}}
 if(bits==32)s->cpu.registers[r]=v;else word(s,r,(uint16_t)v);nz(s,v,bits);s->cpu.sr=(uint16_t)((s->cpu.sr&~0x13u)|(c?0x11u:0)|(ov?2u:0));}
static void muls(struct target *s,unsigned r,uint16_t b){s->cpu.registers[r]=sx16((uint16_t)s->cpu.registers[r])*sx16(b);nz(s,s->cpu.registers[r],32);}
#define R8(a,v) do{if(s.bus->read8(s.bus->context,(a),&(v)))return BIWN_WORLD_CPU_BUS_ERROR;}while(0)
#define R16(a,v) do{if(s.bus->read16(s.bus->context,(a),&(v)))return BIWN_WORLD_CPU_BUS_ERROR;}while(0)
#define R32(a,v) do{if(s.bus->read32(s.bus->context,(a),&(v)))return BIWN_WORLD_CPU_BUS_ERROR;}while(0)
#define W16(a,v) do{if(s.bus->write16(s.bus->context,(a),(uint16_t)(v)))return BIWN_WORLD_CPU_BUS_ERROR;}while(0)
#define CHECK(e) do{int status=(e);if(status)return(enum biwn_world_cpu_status)status;}while(0)
#define POP(n) do{s.cpu.registers[15]+=(n);s.cpu.usp=s.cpu.registers[15];}while(0)
static int push(struct target *s,uint32_t v,unsigned width,int moved){s->cpu.registers[15]-=width;s->cpu.usp=s->cpu.registers[15];if(width==2){if(s->bus->write16(s->bus->context,s->cpu.registers[15],(uint16_t)v))return 2;}else if(s->bus->write32(s->bus->context,s->cpu.registers[15],v))return 2;if(moved)nz(s,v,width*8);return 0;}
static int call(struct target *s,uint32_t target,uint32_t ret){uint32_t sp;int status=push(s,ret,4,0);if(status)return status;s->cpu.pc=target;sp=s->cpu.registers[15];if(s->service(s->context,s->bus,&s->cpu,target))return 3;if(s->cpu.registers[15]!=sp)return 5;if(s->bus->read32(s->bus->context,sp,&s->cpu.pc))return 2;s->cpu.registers[15]+=4;s->cpu.usp=s->cpu.registers[15];return s->cpu.pc==ret?0:5;}
/* Cursor branches reread memory separately, retaining each partial register
 * write and arithmetic flag rather than reducing the code to one formula. */
static int approach(struct target *state,uint32_t address,unsigned target_register)
{
 struct target s=*state;uint16_t w;R16(address,w);alu(&s,s.cpu.registers[target_register],w,16,1,1);
 if(lt(s.cpu.registers[target_register],w,16)){
  R16(address,w);word(&s,1,w);nz(&s,w,16);word(&s,1,(uint16_t)alu(&s,s.cpu.registers[1],1,16,1,0));R16(address,w);word(&s,0,w);nz(&s,w,16);
  word(&s,0,(uint16_t)alu(&s,s.cpu.registers[0],s.cpu.registers[target_register],16,1,0));shift(&s,0,16,3,0);word(&s,1,(uint16_t)alu(&s,s.cpu.registers[1],s.cpu.registers[0],16,1,0));W16(address,s.cpu.registers[1]);nz(&s,s.cpu.registers[1],16);
 }
 R16(address,w);alu(&s,s.cpu.registers[target_register],w,16,1,1);
 if(lt(w,s.cpu.registers[target_register],16)){
  R16(address,w);word(&s,1,w);nz(&s,w,16);word(&s,1,(uint16_t)alu(&s,s.cpu.registers[1],1,16,0,0));word(&s,0,(uint16_t)s.cpu.registers[target_register]);nz(&s,s.cpu.registers[0],16);R16(address,w);
  word(&s,0,(uint16_t)alu(&s,s.cpu.registers[0],w,16,1,0));shift(&s,0,16,3,0);word(&s,1,(uint16_t)alu(&s,s.cpu.registers[1],s.cpu.registers[0],16,0,0));W16(address,s.cpu.registers[1]);nz(&s,s.cpu.registers[1],16);
 }
 *state=s;return 0;
}
enum biwn_world_cpu_status biwn_targeting_cpu_body(struct biwn_world_bus *bus,struct biwn_task_cpu *state,biwn_world_cpu_service service,void *context)
{
 struct target s;uint32_t v,record,matrix,other;uint16_t w;uint8_t b;unsigned i;int aligned;
 if(!bus||!state||!service||!bus->read8||!bus->read16||!bus->read32||!bus->write16||!bus->write32||state->sr&0x2000u||state->pc!=0x20820u)return BIWN_WORLD_CPU_BAD_ARGUMENT;
 s.bus=bus;s.cpu=*state;s.service=service;s.context=context;s.cpu.registers[15]-=8;s.cpu.usp=s.cpu.registers[15];
 for(i=15;i-->2;)if(i<=7||i>=10)CHECK(push(&s,s.cpu.registers[i],4,0));
 s.cpu.registers[4]=0xfffffu;nz(&s,s.cpu.registers[4],32);s.cpu.registers[5]=0xffffffffu;nz(&s,s.cpu.registers[5],32);R16(0x49d5cu,w);W16(s.cpu.registers[15]+0x2eu,w);nz(&s,w,16);W16(0x49d5cu,0);nz(&s,0,16);word(&s,3,0);nz(&s,0,16);s.cpu.registers[12]=0x49d6cu;s.cpu.registers[14]=0x47b88u;s.cpu.registers[13]=0xe540u;
 do{
  word(&s,1,(uint16_t)s.cpu.registers[3]);nz(&s,s.cpu.registers[1],16);muls(&s,1,206);record=s.cpu.registers[12]+s.cpu.registers[1];R16(record,w);nz(&s,w,16);if(!w)goto next;
  R16(record+0x6cu,w);nz(&s,w,16);if(!w)goto next;
  s.cpu.registers[8]=record;R16(s.cpu.registers[8]+0xc0u,w);word(&s,0,w);nz(&s,w,16);s.cpu.registers[0]=sx16((uint16_t)s.cpu.registers[0]);nz(&s,s.cpu.registers[0],32);shift(&s,0,32,6,1);matrix=s.cpu.registers[14]+s.cpu.registers[0];R16(matrix+0x16u,w);alu(&s,w,15,16,1,1);if(!lt(15,w,16))goto next;R16(matrix+0x16u,w);alu(&s,w,1024,16,1,1);if(lt(1024,w,16))goto next;
  R32(0x49c50u,s.cpu.registers[10]);R32(s.cpu.registers[12]+s.cpu.registers[1]+4u,v);s.cpu.registers[10]-=v;R32(0x49c56u,s.cpu.registers[11]);R32(s.cpu.registers[12]+s.cpu.registers[1]+10u,v);s.cpu.registers[11]-=v;
  word(&s,7,(uint16_t)s.cpu.registers[11]);nz(&s,s.cpu.registers[7],16);word(&s,7,(uint16_t)alu(&s,0,s.cpu.registers[7],16,1,0));CHECK(push(&s,s.cpu.registers[7],2,1));word(&s,7,(uint16_t)s.cpu.registers[10]);nz(&s,s.cpu.registers[7],16);word(&s,7,(uint16_t)alu(&s,0,s.cpu.registers[7],16,1,0));CHECK(push(&s,s.cpu.registers[7],2,1));CHECK(call(&s,0x13440u,0x208aau));R8(0x49cbau,b);byte(&s,0,(uint8_t)alu(&s,s.cpu.registers[0],b,8,1,0));POP(4);alu(&s,s.cpu.registers[0],5,8,1,1);if(lt(5,s.cpu.registers[0],8))goto next;alu(&s,s.cpu.registers[0],0xfbu,8,1,1);if(lt(s.cpu.registers[0],0xfbu,8))goto next;
  word(&s,0,sx8((uint8_t)s.cpu.registers[0]));nz(&s,s.cpu.registers[0],16);s.cpu.registers[0]=sx16((uint16_t)s.cpu.registers[0]);nz(&s,s.cpu.registers[0],32);s.cpu.registers[1]=s.cpu.registers[0];nz(&s,s.cpu.registers[1],32);shift(&s,1,32,2,1);s.cpu.registers[1]=alu(&s,s.cpu.registers[1],s.cpu.registers[0],32,0,0);shift(&s,1,32,2,1);CHECK(push(&s,s.cpu.registers[1],4,1));CHECK(push(&s,s.cpu.registers[0],4,1));CHECK(call(&s,s.cpu.registers[13],0x208d0u));POP(8);s.cpu.registers[2]=s.cpu.registers[0];nz(&s,s.cpu.registers[2],32);
  CHECK(push(&s,s.cpu.registers[10],4,1));CHECK(push(&s,s.cpu.registers[10],4,1));CHECK(call(&s,s.cpu.registers[13],0x208dau));POP(8);s.cpu.registers[10]=s.cpu.registers[0];s.cpu.registers[2]=alu(&s,s.cpu.registers[2],s.cpu.registers[10],32,0,0);CHECK(push(&s,s.cpu.registers[11],4,1));CHECK(push(&s,s.cpu.registers[11],4,1));CHECK(call(&s,s.cpu.registers[13],0x208e6u));POP(8);s.cpu.registers[2]=alu(&s,s.cpu.registers[2],s.cpu.registers[0],32,0,0);alu(&s,s.cpu.registers[4],s.cpu.registers[2],32,1,1);if(!lt(s.cpu.registers[2],s.cpu.registers[4],32))goto next;
  s.cpu.registers[4]=s.cpu.registers[2];nz(&s,s.cpu.registers[4],32);word(&s,5,(uint16_t)s.cpu.registers[3]);nz(&s,s.cpu.registers[5],16);s.cpu.registers[6]=s.cpu.registers[10];nz(&s,s.cpu.registers[6],32);s.cpu.registers[6]=alu(&s,s.cpu.registers[6],s.cpu.registers[0],32,0,0);
next:
  word(&s,3,(uint16_t)alu(&s,s.cpu.registers[3],1,16,0,0));alu(&s,s.cpu.registers[3],39,16,1,1);
 }while(!lt(39,s.cpu.registers[3],16));
 alu(&s,s.cpu.registers[5],0xffffu,16,1,1);if((uint16_t)s.cpu.registers[5]==0xffffu)goto done;
 R16(0x49d5au,w);word(&s,0,w);nz(&s,w,16);s.cpu.registers[0]=sx16((uint16_t)s.cpu.registers[0]);nz(&s,s.cpu.registers[0],32);s.cpu.registers[8]=0x4c280u;shift(&s,0,32,2,1);R32(s.cpu.registers[8]+s.cpu.registers[0],v);alu(&s,s.cpu.registers[6],v,32,1,1);if(!lt(s.cpu.registers[6],v,32))goto done;
 word(&s,0,(uint16_t)s.cpu.registers[5]);nz(&s,s.cpu.registers[0],16);muls(&s,0,206);s.cpu.registers[8]=s.cpu.registers[0];s.cpu.registers[8]+=0x49e2cu;R16(s.cpu.registers[8],w);word(&s,2,w);nz(&s,w,16);s.cpu.registers[2]=sx16((uint16_t)s.cpu.registers[2]);nz(&s,s.cpu.registers[2],32);shift(&s,2,32,6,1);s.cpu.registers[10]=0x47b88u;R16(s.cpu.registers[10]+s.cpu.registers[2]+0x16u,w);s.cpu.registers[11]=sx16(w);s.cpu.registers[12]=0xe588u;
 CHECK(push(&s,s.cpu.registers[11],4,1));R16(s.cpu.registers[10]+s.cpu.registers[2]+0x12u,w);word(&s,7,w);nz(&s,w,16);muls(&s,7,173);CHECK(push(&s,s.cpu.registers[7],4,1));CHECK(call(&s,s.cpu.registers[12],0x20952u));POP(8);word(&s,3,(uint16_t)s.cpu.registers[0]);nz(&s,s.cpu.registers[3],16);word(&s,3,(uint16_t)alu(&s,s.cpu.registers[3],112,16,0,0));R16(s.cpu.registers[10]+s.cpu.registers[2]+0x14u,w);word(&s,0,w);nz(&s,w,16);word(&s,0,(uint16_t)alu(&s,s.cpu.registers[0],0xffecu,16,0,0));CHECK(push(&s,s.cpu.registers[11],4,1));muls(&s,0,173);CHECK(push(&s,s.cpu.registers[0],4,1));CHECK(call(&s,s.cpu.registers[12],0x2096cu));POP(8);word(&s,2,(uint16_t)s.cpu.registers[0]);nz(&s,s.cpu.registers[2],16);word(&s,2,(uint16_t)alu(&s,s.cpu.registers[2],90,16,0,0));
 CHECK(approach(&s,0x49d68u,3));CHECK(approach(&s,0x49d6au,2));R16(0x49d68u,w);alu(&s,s.cpu.registers[3],w,16,1,1);aligned=(uint16_t)s.cpu.registers[3]==w;if(aligned){R16(0x49d6au,w);alu(&s,s.cpu.registers[2],w,16,1,1);aligned=(uint16_t)s.cpu.registers[2]==w;}W16(0x49d5eu,aligned?1:0);nz(&s,aligned?1:0,16);
 R16(0x49d68u,w);word(&s,0,w);nz(&s,w,16);word(&s,0,(uint16_t)alu(&s,s.cpu.registers[0],1,16,1,0));alu(&s,s.cpu.registers[0],222,16,1,1);if((uint16_t)s.cpu.registers[0]>222u)goto radius;
 R16(0x49d6au,w);word(&s,0,w);nz(&s,w,16);word(&s,0,(uint16_t)alu(&s,s.cpu.registers[0],0xfff7u,16,0,0));alu(&s,s.cpu.registers[0],162,16,1,1);if((uint16_t)s.cpu.registers[0]>162u)goto radius;
 R16(s.cpu.registers[15]+0x2eu,w);nz(&s,w,16);if(!w){W16(0x49d68u,112);nz(&s,112,16);W16(0x49d6au,90);nz(&s,90,16);}W16(0x49d5cu,1);nz(&s,1,16);
radius:
 W16(0x49d60u,s.cpu.registers[5]);nz(&s,s.cpu.registers[5],16);W16(0x49d64u,s.cpu.registers[6]);nz(&s,s.cpu.registers[6],16);s.cpu.registers[2]=1;nz(&s,1,32);
 do{R16(0x49d64u,w);s.cpu.registers[10]=sx16(w);CHECK(push(&s,s.cpu.registers[2],4,1));CHECK(push(&s,s.cpu.registers[2],4,1));CHECK(call(&s,0xe540u,0x20a84u));POP(8);alu(&s,s.cpu.registers[0],s.cpu.registers[10],32,1,1);if(lt(s.cpu.registers[10],s.cpu.registers[0],32)){word(&s,7,256);nz(&s,256,16);word(&s,7,(uint16_t)alu(&s,s.cpu.registers[7],s.cpu.registers[2],16,1,0));W16(0x49d66u,s.cpu.registers[7]);nz(&s,s.cpu.registers[7],16);goto done;}
  s.cpu.registers[2]=alu(&s,s.cpu.registers[2],1,32,0,0);alu(&s,s.cpu.registers[2],255,32,1,1);
 }while(!lt(255,s.cpu.registers[2],32));
done:
 for(i=2;i<=14;i++)if(i<=7||i>=10){R32(s.cpu.registers[15],other);s.cpu.registers[i]=other;POP(4);}POP(8);s.cpu.pc=0x20a9au;*state=s.cpu;return BIWN_WORLD_CPU_OK;
}
enum biwn_world_cpu_status biwn_targeting_cpu_call(struct biwn_world_bus *bus,struct biwn_task_cpu *state,biwn_world_cpu_service service,void *context)
{struct biwn_task_cpu cpu;enum biwn_world_cpu_status status;uint32_t pc;if(!state)return BIWN_WORLD_CPU_BAD_ARGUMENT;cpu=*state;status=biwn_targeting_cpu_body(bus,&cpu,service,context);if(status)return status;if(bus->read32(bus->context,cpu.registers[15],&pc))return BIWN_WORLD_CPU_BUS_ERROR;cpu.pc=pc;cpu.registers[15]+=4;cpu.usp=cpu.registers[15];*state=cpu;return BIWN_WORLD_CPU_OK;}
