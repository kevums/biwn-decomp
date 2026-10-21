#include "biwn_world_cpu.h"
struct world {struct biwn_world_bus *bus;struct biwn_task_cpu cpu;biwn_world_cpu_service service;void *context;uint32_t budget;};
static uint32_t sx16(uint16_t v){return(uint32_t)(v&0x7fffu)-(uint32_t)(v&0x8000u);}
static int less(uint32_t a,uint32_t b){return(a^0x80000000u)<(b^0x80000000u);}
static void bank(struct world *s){if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];}
static void nz(struct world *s,uint32_t v,unsigned bits){uint32_t mask=bits==32?0xffffffffu:(1u<<bits)-1u,sign=1u<<(bits-1);v&=mask;s->cpu.sr=(uint16_t)((s->cpu.sr&0xfff0u)|(v?0:4)|(v&sign?8:0));}
static void word(struct world *s,unsigned r,uint16_t v){s->cpu.registers[r]=(s->cpu.registers[r]&0xffff0000u)|v;}
static uint32_t add(struct world *s,uint32_t a,uint32_t b,unsigned bits,int sub,int cmp){uint32_t mask=bits==32?0xffffffffu:(1u<<bits)-1u,sign=1u<<(bits-1),r;unsigned carry,ov;a&=mask;b&=mask;r=(sub?a-b:a+b)&mask;carry=sub?a<b:r<a;ov=sub?((a^b)&(a^r)&sign)!=0:((~(a^b))&(a^r)&sign)!=0;nz(s,r,bits);s->cpu.sr=(uint16_t)((s->cpu.sr&~(cmp?3u:0x13u))|(carry?(cmp?1u:0x11u):0)|(ov?2u:0));return r;}
static void bit(struct world *s,uint32_t v,unsigned n){s->cpu.sr=(uint16_t)((s->cpu.sr&~4u)|(v&(1u<<n)?0:4));}
static void shift14(struct world *s){uint16_t v=(uint16_t)s->cpu.registers[0];word(s,0,v>>14);nz(s,s->cpu.registers[0],16);s->cpu.sr=(uint16_t)((s->cpu.sr&~0x11u)|(v&0x2000u?0x11u:0));}
#define R8(a,v) do{if(s.bus->read8(s.bus->context,(a),&(v)))return BIWN_WORLD_CPU_BUS_ERROR;}while(0)
#define R16(a,v) do{if(s.bus->read16(s.bus->context,(a),&(v)))return BIWN_WORLD_CPU_BUS_ERROR;}while(0)
#define R32(a,v) do{if(s.bus->read32(s.bus->context,(a),&(v)))return BIWN_WORLD_CPU_BUS_ERROR;}while(0)
#define W16(a,v) do{if(s.bus->write16(s.bus->context,(a),(uint16_t)(v)))return BIWN_WORLD_CPU_BUS_ERROR;}while(0)
#define W32(a,v) do{if(s.bus->write32(s.bus->context,(a),(v)))return BIWN_WORLD_CPU_BUS_ERROR;}while(0)
#define CHECK(e) do{int status=(e);if(status){if(status==BIWN_WORLD_CPU_SUSPENDED)*state=s.cpu;return(enum biwn_world_cpu_status)status;}}while(0)
#define POP(n) do{s.cpu.registers[15]+=(n);bank(&s);}while(0)
static int push(struct world *s,uint32_t v,unsigned width,int moved){s->cpu.registers[15]-=width;bank(s);if(width==2){if(s->bus->write16(s->bus->context,s->cpu.registers[15],(uint16_t)v))return 2;}else if(s->bus->write32(s->bus->context,s->cpu.registers[15],v))return 2;if(moved)nz(s,v,width*8);return 0;}
static int digit(struct world *s){uint32_t input;unsigned i;static const unsigned bits[9]={19,18,17,7,6,5,4,3,2};static const uint32_t values[9]={1,4,7,2,5,8,0,3,6};if(s->bus->read32(s->bus->context,s->cpu.registers[15]+4,&input))return 2;s->cpu.registers[1]=input;
 for(i=0;i<9;i++)if(input&(1u<<bits[i])){if(bits[i]==4)word(s,0,0);else s->cpu.registers[0]=values[i];nz(s,s->cpu.registers[0],bits[i]==4?16:32);return 0;}
 s->cpu.registers[0]=input&2u?9u:0xffffffffu;nz(s,s->cpu.registers[0],32);return 0;}
static int call(struct world *s,uint32_t target,uint32_t ret){uint32_t sp;int status=push(s,ret,4,0);if(status)return status;s->cpu.pc=target;sp=s->cpu.registers[15];
 if(target==0x1b718u){status=digit(s);if(status)return status;}
 else {int service_status=s->service(s->context,s->bus,&s->cpu,target);if(service_status==BIWN_WORLD_CPU_SUSPENDED&&target==0x191f4u&&s->cpu.pc==0xdf60u)return BIWN_WORLD_CPU_SUSPENDED;if(service_status)return 3;}
 if(s->cpu.registers[15]!=sp)return 5;if(s->bus->read32(s->bus->context,sp,&s->cpu.pc))return 2;s->cpu.registers[15]+=4;bank(s);return s->cpu.pc==ret?0:5;}
enum biwn_world_cpu_status biwn_world_cpu_body(struct biwn_world_bus *bus,struct biwn_task_cpu *state,biwn_world_cpu_service service,void *context,uint32_t budget)
{
 struct world s;uint32_t value,other,a,b;uint16_t w,mode;uint8_t byte;unsigned i,direction,delta,edgeoff;
 if(!bus||!state||!service||!budget||!bus->read8||!bus->read16||!bus->read32||!bus->write16||!bus->write32||(state->pc!=0x1a188u&&state->pc!=0x1a26cu))return BIWN_WORLD_CPU_BAD_ARGUMENT;
 s.bus=bus;s.cpu=*state;s.service=service;s.context=context;s.budget=budget;if(state->pc==0x1a26cu)goto after_dispatch;s.cpu.registers[15]-=12;bank(&s);
 for(i=15;i-->2;)if(i<=7||i>=10)CHECK(push(&s,s.cpu.registers[i],4,0));
 CHECK(call(&s,0xe4c0u,0x1a196u));--s.budget;R8(0x49bacu,byte);bit(&s,byte,4);
 if(byte&0x10u){do{if(!s.budget)return BIWN_WORLD_CPU_WORK_LIMIT;--s.budget;CHECK(call(&s,0xe4c0u,0x1a1a6u));R8(0x49bacu,byte);bit(&s,byte,4);}while(!(byte&0x10u));
  W32(0x49ba4u,0x10000000u);nz(&s,0x10000000u,32);W32(0x49bacu,0x10000000u);nz(&s,0x10000000u,32);R32(0x778ccu,value);W32(0x46252u,value);nz(&s,value,32);}
 R32(0x778ccu,s.cpu.registers[4]);nz(&s,s.cpu.registers[4],32);R32(0x46252u,value);s.cpu.registers[4]=add(&s,s.cpu.registers[4],value,32,1,0);W32(0x4c24cu,s.cpu.registers[4]);nz(&s,s.cpu.registers[4],32);s.cpu.registers[4]=30;nz(&s,30,32);R32(0x4c24cu,value);add(&s,30,value,32,1,1);if(less(30,value)){W32(0x4c24cu,30);nz(&s,30,32);}
 s.cpu.registers[8]=0x49bacu;R32(s.cpu.registers[8],s.cpu.registers[0]);s.cpu.registers[0]&=0xe02feu;nz(&s,s.cpu.registers[0],32);
 if(s.cpu.registers[0]){R8(s.cpu.registers[8]+2u,byte);bit(&s,byte,1);
  if(byte&2u){word(&s,0,0);nz(&s,0,16);R16(0x49d54u,w);add(&s,w,9,16,1,1);if(w!=9){R16(0x49d54u,w);word(&s,0,w);nz(&s,w,16);word(&s,0,(uint16_t)add(&s,s.cpu.registers[0],1,16,0,0));}W16(0x49d54u,s.cpu.registers[0]);nz(&s,s.cpu.registers[0],16);}
  else{R32(s.cpu.registers[8],value);CHECK(push(&s,value,4,1));CHECK(call(&s,0x1b718u,0x1a22cu));W16(0x49d54u,s.cpu.registers[0]);nz(&s,s.cpu.registers[0],16);POP(4);if(!(uint16_t)s.cpu.registers[0]){W16(0x49d54u,10);nz(&s,10,16);}R16(0x49d54u,w);w=(uint16_t)add(&s,w,1,16,1,0);W16(0x49d54u,w);}
  R16(0x49d54u,w);W16(0x49d56u,w);nz(&s,w,16);CHECK(call(&s,0x1b786u,0x1a254u));}
 R32(0x778ccu,value);W32(0x46252u,value);nz(&s,value,32);R8(0x49ba7u,byte);nz(&s,byte,8);if(!(byte&0x80u))CHECK(call(&s,0x191f4u,0x1a26cu));
after_dispatch:
 s.cpu.registers[13]=0x49c50u;R32(s.cpu.registers[13],value);W32(s.cpu.registers[15]+44u,value);nz(&s,value,32);
 s.cpu.registers[12]=0x49c54u;R16(s.cpu.registers[12],w);word(&s,5,w);nz(&s,w,16);s.cpu.registers[14]=0x49c56u;R32(s.cpu.registers[14],s.cpu.registers[6]);nz(&s,s.cpu.registers[6],32);
 s.cpu.registers[10]=0x49c5au;R16(s.cpu.registers[10],w);word(&s,7,w);nz(&s,w,16);s.cpu.registers[11]=0x49c5cu;R16(s.cpu.registers[11],w);W16(s.cpu.registers[15]+50u,w);nz(&s,w,16);R16(0x49c5eu,w);W16(s.cpu.registers[15]+48u,w);nz(&s,w,16);
 s.cpu.registers[3]=1;nz(&s,1,32);R32(0x49cc4u,value);CHECK(push(&s,value,4,1));CHECK(push(&s,0,4,1));s.cpu.registers[0]=0;nz(&s,0,32);R8(0x49cbau,byte);s.cpu.registers[0]=byte;nz(&s,byte,8);CHECK(push(&s,s.cpu.registers[0],4,1));CHECK(push(&s,0,4,1));CHECK(push(&s,0x49cccu,4,0));CHECK(call(&s,0xe220u,0x1a2c2u));
 word(&s,2,0x3fffu);nz(&s,0x3fffu,16);
 /* First coordinate pass: X/Z are32bits, Y and fractions are16bits. */
 for(i=0;i<3;i++){
  R16(0x49ce6u+i*2u,w);word(&s,1,w);word(&s,1,(uint16_t)s.cpu.registers[1]&0x3fffu);a=i==0?s.cpu.registers[10]:i==1?s.cpu.registers[11]:0x49c5eu;R16(a,w);word(&s,0,w&0x3fffu);word(&s,1,(uint16_t)add(&s,s.cpu.registers[1],s.cpu.registers[0],16,0,0));word(&s,0,(uint16_t)s.cpu.registers[1]);
  if(!i){s.cpu.registers[4]=14;nz(&s,14,32);}shift14(&s);
  if(i==1){R16(0x49ce0u,w);word(&s,0,(uint16_t)add(&s,s.cpu.registers[0],w,16,0,0));R16(s.cpu.registers[12],w);w=(uint16_t)add(&s,w,s.cpu.registers[0],16,0,0);W16(s.cpu.registers[12],w);}
  else{R16(i?0x49ce2u:0x49cdeu,w);s.cpu.registers[9]=sx16(w);s.cpu.registers[8]=sx16((uint16_t)s.cpu.registers[0]);s.cpu.registers[0]=s.cpu.registers[9];nz(&s,s.cpu.registers[0],32);s.cpu.registers[0]=add(&s,s.cpu.registers[0],s.cpu.registers[8],32,0,0);b=i?s.cpu.registers[14]:s.cpu.registers[13];R32(b,value);W32(b,add(&s,value,s.cpu.registers[0],32,0,0));}
  word(&s,1,(uint16_t)s.cpu.registers[1]&0x3fffu);nz(&s,s.cpu.registers[1],16);W16(a,s.cpu.registers[1]);nz(&s,s.cpu.registers[1],16);
 }
 s.cpu.registers[8]=0x49c60u;POP(20);R16(s.cpu.registers[8],mode);add(&s,mode,1,16,1,1);
 if(mode==1){R32(s.cpu.registers[14],s.cpu.registers[4]);nz(&s,s.cpu.registers[4],32);R32(0x49c9cu,value);add(&s,s.cpu.registers[4],value,32,1,1);
  if(!less(s.cpu.registers[4],value)){delta=5;direction=0;edgeoff=2;}
  else{R32(s.cpu.registers[14],s.cpu.registers[14]);R32(0x49ca0u,value);add(&s,s.cpu.registers[14],value,32,1,1);
   if(less(s.cpu.registers[14],value)){delta=0xfffbu;direction=(uint16_t)s.cpu.registers[3];edgeoff=4;}
   else{R32(s.cpu.registers[13],s.cpu.registers[4]);nz(&s,s.cpu.registers[4],32);R32(0x49c94u,value);add(&s,s.cpu.registers[4],value,32,1,1);
    if(!less(s.cpu.registers[4],value)){delta=(uint16_t)s.cpu.registers[3];direction=2;edgeoff=6;}
    else{R32(s.cpu.registers[13],s.cpu.registers[13]);R32(0x49c98u,value);add(&s,s.cpu.registers[13],value,32,1,1);if(!less(s.cpu.registers[13],value))goto collision_result;delta=0xffffu;direction=3;edgeoff=8;}}}
  CHECK(push(&s,delta,2,1));CHECK(push(&s,direction,2,1));R32(0x49c90u,s.cpu.registers[8]);R16(s.cpu.registers[8]+edgeoff,w);CHECK(push(&s,w,2,1));CHECK(call(&s,0x19f2cu,edgeoff==2?0x1a368u:edgeoff==4?0x1a38cu:edgeoff==6?0x1a3b0u:0x1a3d4u));word(&s,3,(uint16_t)s.cpu.registers[0]);nz(&s,s.cpu.registers[3],16);POP(6);
 }else{R16(s.cpu.registers[8],mode);add(&s,mode,2,16,1,1);if(mode==2){R32(s.cpu.registers[14],s.cpu.registers[4]);nz(&s,s.cpu.registers[4],32);R32(0x49c84u,value);add(&s,s.cpu.registers[4],value,32,1,1);
   if(!less(s.cpu.registers[4],value))direction=0;
   else{R32(s.cpu.registers[14],s.cpu.registers[14]);R32(0x49c88u,value);add(&s,s.cpu.registers[14],value,32,1,1);
    if(less(s.cpu.registers[14],value))direction=(uint16_t)s.cpu.registers[3];
    else{R32(s.cpu.registers[13],s.cpu.registers[4]);nz(&s,s.cpu.registers[4],32);R32(0x49c7cu,value);add(&s,s.cpu.registers[4],value,32,1,1);
     if(!less(s.cpu.registers[4],value))direction=2;
     else{R32(s.cpu.registers[13],s.cpu.registers[13]);R32(0x49c80u,value);add(&s,s.cpu.registers[13],value,32,1,1);if(!less(s.cpu.registers[13],value))goto collision_result;direction=3;}}}
   CHECK(push(&s,direction,2,1));R32(0x49c78u,value);CHECK(push(&s,value,4,1));CHECK(call(&s,0x19fdau,0x1a422u));word(&s,3,(uint16_t)s.cpu.registers[0]);nz(&s,s.cpu.registers[3],16);POP(6);
  }else{word(&s,3,0);nz(&s,0,16);}}
collision_result:
 nz(&s,s.cpu.registers[3],16);
 if(!(uint16_t)s.cpu.registers[3]){R32(s.cpu.registers[15]+44u,value);W32(0x49c50u,value);nz(&s,value,32);W16(0x49c54u,s.cpu.registers[5]);nz(&s,s.cpu.registers[5],16);W32(0x49c56u,s.cpu.registers[6]);nz(&s,s.cpu.registers[6],32);W16(0x49c5au,s.cpu.registers[7]);nz(&s,s.cpu.registers[7],16);R16(s.cpu.registers[15]+50u,w);W16(0x49c5cu,w);nz(&s,w,16);R16(s.cpu.registers[15]+48u,w);W16(0x49c5eu,w);nz(&s,w,16);}
 else{add(&s,s.cpu.registers[3],1,16,1,1);if((uint16_t)s.cpu.registers[3]==1){word(&s,2,0x3fffu);nz(&s,0x3fffu,16);
  for(i=0;i<3;i++){R16(0x49ce6u+i*2u,w);word(&s,1,w&0x3fffu);R16(0x49b92u+i*2u,w);word(&s,0,w&0x3fffu);word(&s,1,(uint16_t)add(&s,s.cpu.registers[1],s.cpu.registers[0],16,0,0));word(&s,0,(uint16_t)s.cpu.registers[1]);if(!i){s.cpu.registers[4]=14;nz(&s,14,32);}shift14(&s);R16(0x49cdeu+i*2u,w);word(&s,0,(uint16_t)add(&s,s.cpu.registers[0],w,16,0,0));R16(0x49b8cu+i*2u,w);W16(0x49b8cu+i*2u,add(&s,w,s.cpu.registers[0],16,0,0));word(&s,1,(uint16_t)s.cpu.registers[1]&0x3fffu);nz(&s,s.cpu.registers[1],16);W16(0x49b92u+i*2u,s.cpu.registers[1]);nz(&s,s.cpu.registers[1],16);}
 }}
 W16(0x49ce2u,0);nz(&s,0,16);W16(0x49ce0u,0);nz(&s,0,16);W16(0x49cdeu,0);nz(&s,0,16);s.cpu.registers[10]=0x49d16u;R16(s.cpu.registers[10],w);word(&s,2,w);nz(&s,w,16);CHECK(call(&s,0xf0fau,0x1a508u));nz(&s,s.cpu.registers[0],32);w=s.cpu.registers[0]&0x80000000u?0xffffu:1u;W16(s.cpu.registers[10],w);nz(&s,w,16);R16(0x49d16u,w);add(&s,s.cpu.registers[2],w,16,1,1);if((uint16_t)s.cpu.registers[2]!=w){W16(0x49d18u,1);nz(&s,1,16);}
 CHECK(push(&s,0x49c4cu,4,0));CHECK(call(&s,0xeb04u,0x1a532u));CHECK(call(&s,0x20820u,0x1a538u));POP(4);
 for(i=2;i<=14;i++)if(i<=7||i>=10){R32(s.cpu.registers[15],other);s.cpu.registers[i]=other;POP(4);}POP(12);s.cpu.pc=0x1a542u;*state=s.cpu;return BIWN_WORLD_CPU_OK;
}
enum biwn_world_cpu_status biwn_world_cpu_call(struct biwn_world_bus *bus,struct biwn_task_cpu *state,biwn_world_cpu_service service,void *context,uint32_t budget)
{struct biwn_task_cpu cpu;enum biwn_world_cpu_status status;uint32_t pc;if(!state)return BIWN_WORLD_CPU_BAD_ARGUMENT;cpu=*state;status=biwn_world_cpu_body(bus,&cpu,service,context,budget);if(status){if(status==BIWN_WORLD_CPU_SUSPENDED)*state=cpu;return status;}if(bus->read32(bus->context,cpu.registers[15],&pc))return BIWN_WORLD_CPU_BUS_ERROR;cpu.pc=pc;cpu.registers[15]+=4;if(cpu.sr&0x2000u)cpu.ssp=cpu.registers[15];else cpu.usp=cpu.registers[15];*state=cpu;return BIWN_WORLD_CPU_OK;}
