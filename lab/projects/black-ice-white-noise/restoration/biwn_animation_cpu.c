#include "biwn_animation_cpu.h"
struct animation {struct biwn_world_bus *bus;struct biwn_task_cpu cpu;uint32_t budget;};
static uint32_t sx16(uint16_t v){return(uint32_t)(v&0x7fffu)-(uint32_t)(v&0x8000u);}
static uint16_t sx8(uint8_t v){return(uint16_t)((uint16_t)(v&0x7fu)-(uint16_t)(v&0x80u));}
static void bank(struct animation *s){if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];}
static void word(struct animation *s,unsigned r,uint16_t v){s->cpu.registers[r]=(s->cpu.registers[r]&0xffff0000u)|v;}
static void byte(struct animation *s,unsigned r,uint8_t v){s->cpu.registers[r]=(s->cpu.registers[r]&0xffffff00u)|v;}
static void nz(struct animation *s,uint32_t v,unsigned bits){uint32_t mask=bits==32?0xffffffffu:(1u<<bits)-1u,sign=1u<<(bits-1);v&=mask;s->cpu.sr=(uint16_t)((s->cpu.sr&0xfff0u)|(v?0:4)|(v&sign?8:0));}
static uint32_t arithmetic(struct animation *s,uint32_t a,uint32_t b,unsigned bits,int sub,int cmp){uint32_t mask=bits==32?0xffffffffu:(1u<<bits)-1u,sign=1u<<(bits-1),r;unsigned carry,ov;a&=mask;b&=mask;r=(sub?a-b:a+b)&mask;carry=sub?a<b:r<a;ov=sub?((a^b)&(a^r)&sign)!=0:((~(a^b))&(a^r)&sign)!=0;nz(s,r,bits);s->cpu.sr=(uint16_t)((s->cpu.sr&~(cmp?3u:0x13u))|(carry?(cmp?1u:0x11u):0)|(ov?2u:0));return r;}
static void extw(struct animation *s,unsigned r){word(s,r,sx8((uint8_t)s->cpu.registers[r]));nz(s,s->cpu.registers[r],16);}
static void extl(struct animation *s,unsigned r){s->cpu.registers[r]=sx16((uint16_t)s->cpu.registers[r]);nz(s,s->cpu.registers[r],32);}
static void asl(struct animation *s,unsigned r,unsigned n){uint32_t v=s->cpu.registers[r],top=v>>(31u-n),all=(1u<<(n+1))-1u;unsigned c=(v>>(32u-n))&1u;s->cpu.registers[r]=v<<n;nz(s,s->cpu.registers[r],32);s->cpu.sr=(uint16_t)((s->cpu.sr&~0x13u)|(c?0x11u:0)|(top&&top!=all?2u:0));}
#define R8(a,v) do{if(s->bus->read8(s->bus->context,(a),&(v)))return BIWN_ANIM_CPU_BUS_ERROR;}while(0)
#define R16(a,v) do{if(s->bus->read16(s->bus->context,(a),&(v)))return BIWN_ANIM_CPU_BUS_ERROR;}while(0)
#define R32(a,v) do{if(s->bus->read32(s->bus->context,(a),&(v)))return BIWN_ANIM_CPU_BUS_ERROR;}while(0)
#define W16(a,v) do{if(s->bus->write16(s->bus->context,(a),(uint16_t)(v)))return BIWN_ANIM_CPU_BUS_ERROR;}while(0)
#define W32(a,v) do{if(s->bus->write32(s->bus->context,(a),(v)))return BIWN_ANIM_CPU_BUS_ERROR;}while(0)
#define CHECK(e) do{enum biwn_animation_cpu_status status=(e);if(status)return status;}while(0)
static enum biwn_animation_cpu_status push(struct animation *s,uint32_t v,int moved){s->cpu.registers[15]-=4;bank(s);W32(s->cpu.registers[15],v);if(moved)nz(s,v,32);return BIWN_ANIM_CPU_OK;}
static enum biwn_animation_cpu_status queue(struct animation *s)
{
 uint16_t count;uint32_t v,address;unsigned offsets[4]={8,4,12,16},destinations[4]={4,0,8,12},i;
 R16(0x112940u,count);arithmetic(s,count,39,16,1,1);
 if(!(count&0x8000u)&&count>39){word(s,0,0);nz(s,0,16);s->cpu.pc=0xeb02u;return BIWN_ANIM_CPU_OK;}
 R16(0x112940u,count);word(s,0,count);nz(s,count,16);extl(s,0);asl(s,0,4);s->cpu.registers[8]=0x1126c0u;address=s->cpu.registers[8]+s->cpu.registers[0];
 for(i=0;i<4;i++){R32(s->cpu.registers[15]+offsets[i],v);W32(address+destinations[i],v);nz(s,v,32);}
 R16(0x112940u,count);W16(0x112940u,arithmetic(s,count,1,16,0,0));s->cpu.registers[0]=1;nz(s,1,32);s->cpu.pc=0xeafeu;return BIWN_ANIM_CPU_OK;
}
static enum biwn_animation_cpu_status emit(struct animation *s,int reread,uint32_t ret)
{
 uint8_t b;uint32_t object=s->cpu.registers[10],v,sp,pc;unsigned carry;
 R8(object+0xcau,b);byte(s,0,b);nz(s,b,8);v=s->cpu.registers[0];carry=(v>>6)&1u;s->cpu.registers[0]=v>>7;nz(s,s->cpu.registers[0],32);s->cpu.sr=(uint16_t)((s->cpu.sr&~0x11u)|(carry?0x11u:0));
 s->cpu.registers[1]=1;nz(s,1,32);s->cpu.registers[1]&=s->cpu.registers[0];nz(s,s->cpu.registers[1],32);CHECK(push(s,s->cpu.registers[1],1));R32(object+0x5eu,v);CHECK(push(s,v,1));
 if(reread)R32(object+0x64u,s->cpu.registers[8]);R8(s->cpu.registers[8],b);byte(s,0,b);nz(s,b,8);extw(s,0);s->cpu.registers[9]=sx16((uint16_t)s->cpu.registers[0]);CHECK(push(s,s->cpu.registers[9],1));R32(object+0x58u,v);CHECK(push(s,v,1));CHECK(push(s,ret,0));sp=s->cpu.registers[15];s->cpu.pc=0xeac4u;CHECK(queue(s));R32(sp,pc);if(pc!=ret)return BIWN_ANIM_CPU_BAD_RETURN;s->cpu.registers[15]+=20;bank(s);nz(s,s->cpu.registers[0],16);return BIWN_ANIM_CPU_OK;
}
enum biwn_animation_cpu_status biwn_animation_cpu_body(struct biwn_world_bus *bus,struct biwn_task_cpu *state,uint32_t budget)
{
 struct animation storage,*s=&storage;uint32_t object,pointer,v;uint16_t w,delta;uint8_t b,other;
 if(!bus||!state||!bus->read16||!bus->read32||!bus->write16||!bus->write32||(state->pc!=0xeac4u&&state->pc!=0xeb04u)||(state->pc==0xeb04u&&(!budget||!bus->read8)))return BIWN_ANIM_CPU_BAD_ARGUMENT;
 s->bus=bus;s->cpu=*state;s->budget=budget;
 if(state->pc==0xeac4u){CHECK(queue(s));*state=s->cpu;return BIWN_ANIM_CPU_OK;}
 CHECK(push(s,s->cpu.registers[10],1));R32(s->cpu.registers[15]+8u,s->cpu.registers[10]);object=s->cpu.registers[10];R32(object+0x68u,v);nz(s,v,32);
 if(v){R16(object+0xcau,w);word(s,0,w);nz(s,w,16);if(w&0x8000u)word(s,0,(uint16_t)arithmetic(s,0,w,16,1,0));extl(s,0);asl(s,0,2);s->cpu.registers[8]=s->cpu.registers[0];R32(object+0x68u,v);s->cpu.registers[8]+=v;s->cpu.registers[8]-=4;W32(object+0x64u,s->cpu.registers[8]);nz(s,s->cpu.registers[8],32);W32(object+0x68u,0);nz(s,0,32);R32(object+0x64u,s->cpu.registers[8]);R8(s->cpu.registers[8]+1u,b);byte(s,1,b);nz(s,b,8);extw(s,1);W16(object+0x62u,s->cpu.registers[1]);nz(s,s->cpu.registers[1],16);goto emit_pending;}
 R16(object+0x62u,w);word(s,0,w);nz(s,w,16);R16(0x4c24eu,delta);word(s,0,(uint16_t)arithmetic(s,s->cpu.registers[0],delta,16,1,0));W16(object+0x62u,s->cpu.registers[0]);nz(s,s->cpu.registers[0],16);
 if((uint16_t)s->cpu.registers[0]&&!((uint16_t)s->cpu.registers[0]&0x8000u)){R16(object+0xccu,w);nz(s,w,16);if(!w)goto done;
emit_pending:
  CHECK(emit(s,1,0xeb7au));if((uint16_t)s->cpu.registers[0]){W16(object+0xccu,0);nz(s,0,16);}goto done;
 }
 for(;;){
  if(!s->budget--)return BIWN_ANIM_CPU_WORK_LIMIT;
  R32(object+0x64u,s->cpu.registers[8]);R8(s->cpu.registers[8]+3u,b);byte(s,0,b);nz(s,b,8);extw(s,0);extl(s,0);asl(s,0,2);R8(s->cpu.registers[8]+s->cpu.registers[0]+1u,b);byte(s,0,b);nz(s,b,8);extw(s,0);R16(object+0x62u,w);W16(object+0x62u,arithmetic(s,w,s->cpu.registers[0],16,0,0));
  R32(object+0x64u,s->cpu.registers[8]);R8(s->cpu.registers[8]+3u,b);byte(s,0,b);nz(s,b,8);extw(s,0);extl(s,0);asl(s,0,2);R8(s->cpu.registers[8],b);byte(s,1,b);nz(s,b,8);R8(s->cpu.registers[8]+s->cpu.registers[0],other);arithmetic(s,s->cpu.registers[1],other,8,1,1);
  if(b==other){R16(object+0xccu,w);nz(s,w,16);if(!w){R32(object+0x64u,pointer);W32(object+0x64u,arithmetic(s,pointer,s->cpu.registers[0],32,0,0));goto timer;}}
  s->cpu.registers[8]=s->cpu.registers[0];R32(object+0x64u,v);s->cpu.registers[8]+=v;W32(object+0x64u,s->cpu.registers[8]);nz(s,s->cpu.registers[8],32);CHECK(emit(s,0,0xebe8u));if((uint16_t)s->cpu.registers[0]){W16(object+0xccu,0);nz(s,0,16);}
timer:
  R16(object+0x62u,w);nz(s,w,16);if(w&&!(w&0x8000u))break;
 }
done:
 R32(s->cpu.registers[15],s->cpu.registers[10]);s->cpu.registers[15]+=4;bank(s);s->cpu.pc=0xec02u;*state=s->cpu;return BIWN_ANIM_CPU_OK;
}
enum biwn_animation_cpu_status biwn_animation_cpu_call(struct biwn_world_bus *bus,struct biwn_task_cpu *state,uint32_t budget)
{struct biwn_task_cpu cpu;enum biwn_animation_cpu_status status;uint32_t pc;if(!state)return BIWN_ANIM_CPU_BAD_ARGUMENT;cpu=*state;status=biwn_animation_cpu_body(bus,&cpu,budget);if(status)return status;if(bus->read32(bus->context,cpu.registers[15],&pc))return BIWN_ANIM_CPU_BUS_ERROR;cpu.pc=pc;cpu.registers[15]+=4;if(cpu.sr&0x2000u)cpu.ssp=cpu.registers[15];else cpu.usp=cpu.registers[15];*state=cpu;return BIWN_ANIM_CPU_OK;}
