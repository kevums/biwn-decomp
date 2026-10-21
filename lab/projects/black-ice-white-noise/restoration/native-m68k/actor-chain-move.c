/* Coordinator original-facing13C9A reconstruction, derived from the existing
 * portable high-level movement body. Actual native helper capture replaces
 * host callbacks; original root/task SP and helper CPU/SR remain explicit. */
#include "actor-chain-native.h"
struct movement {uint32_t *r;};
static uint32_t sx16(uint16_t v){return(uint32_t)(v&0x7fffu)-(uint32_t)(v&0x8000u);}
static void word(struct movement *s,unsigned r,uint16_t v){s->r[r]=(s->r[r]&0xffff0000u)|v;}
static void byte(struct movement *s,unsigned r,uint8_t v){s->r[r]=(s->r[r]&0xffffff00u)|v;}
static void nz(struct movement *s,uint32_t v,unsigned bits){uint32_t mask=bits==32?0xffffffffu:(1u<<bits)-1u,sign=1u<<(bits-1);v&=mask;s->r[16]=(uint16_t)((s->r[16]&0xfff0u)|(v?0:4)|(v&sign?8:0));}
static uint32_t arithmetic(struct movement *s,uint32_t a,uint32_t b,unsigned bits,int subtract)
{uint32_t mask=bits==32?0xffffffffu:(1u<<bits)-1u,sign=1u<<(bits-1),r;unsigned carry,overflow;a&=mask;b&=mask;r=(subtract?a-b:a+b)&mask;carry=subtract?a<b:r<a;overflow=subtract?((a^b)&(a^r)&sign)!=0:((~(a^b))&(a^r)&sign)!=0;nz(s,r,bits);s->r[16]=(uint16_t)((s->r[16]&~0x13u)|(carry?0x11u:0)|(overflow?2u:0));return r;}
static int less(uint32_t a,uint32_t b){return(a^0x80000000u)<(b^0x80000000u);}
#define R8(a,v) do{(v)=AMR8(a);}while(0)
#define R16(a,v) do{(v)=AMR16(a);}while(0)
#define R32(a,v) do{(v)=AMR32(a);}while(0)
#define W16(a,v) do{AMW16(a,v);}while(0)
#define W32(a,v) do{AMW32(a,v);}while(0)
#define CHECK(e) do{(void)(e);}while(0)
static void push(struct movement*s,uint32_t value,unsigned width,int moved){s->r[15]-=width;if(width==2)AMW16(s->r[15],value);else AMW32(s->r[15],value);if(moved)nz(s,value,width*8);}
static void call(struct movement*s,uint32_t target,uint32_t ret){(void)ret;switch(target){case 0x13440:biwn_native_actor_move_direction_capture(s->r);break;case 0xe220:biwn_native_actor_move_submit_capture(s->r);break;case 0x13b5a:case 0x13bb0:s->r[15]-=4;s->r[18]=target;biwn_actor_chain_collision_call(s->r);s->r[15]+=4;break;default:__builtin_trap();}}
#define POP(n) do{s.r[15]+=(n);}while(0)
void biwn_actor_chain_move_body(uint32_t *r)
{
 struct movement s;uint32_t object,table,value,other;uint16_t w,mode;uint8_t b,heading;unsigned offset,i,direction,delta,edgeoff;
 s.r=r;
 for(i=14;i-->2;)if(i<=7||i>=10)CHECK(push(&s,s.r[i],4,0));
 R32(s.r[15]+44u,s.r[11]);R32(s.r[15]+48u,s.r[10]);object=s.r[11];table=s.r[10];
 W16(object+150u,0);W16(object+148u,0);W16(object+146u,0);
 R16(object+192u,w);s.r[0]=sx16(w)<<6;s.r[16]=(s.r[16]&~16u)|((w&0x8000u)?16u:0u);s.r[8]=0x47b88u;
 R16(s.r[8]+s.r[0]+22u,w);CHECK(push(&s,w,2,1));R16(s.r[8]+s.r[0]+18u,w);CHECK(push(&s,w,2,1));
 CHECK(call(&s,0x13440u,0x13cceu));R8(0x49b9fu,b);byte(&s,0,(uint8_t)arithmetic(&s,s.r[0],b,8,0));
 R8(object+110u,heading);byte(&s,4,heading);byte(&s,4,(uint8_t)arithmetic(&s,s.r[4],s.r[0],8,1));byte(&s,0,(uint8_t)s.r[4]);POP(4);
 b=(uint8_t)s.r[0];offset=b<=63u?72u:b<=127u?48u:b<=191u?24u:0u;
 if(!offset){s.r[9]=object+164u;R32(s.r[10],value);s.r[10]+=4;W32(s.r[9],value);s.r[9]+=4;s.r[8]=s.r[10];
  for(i=1;i<6;i++){R32(s.r[8],value);if(i<5)s.r[8]+=4;W32(s.r[9],value);if(i<5)s.r[9]+=4;nz(&s,value,32);}}
 else{s.r[8]=object+164u;for(i=0;i<6;i++){R32(table+offset+i*4u,value);W32(s.r[8],value);if(i<5)s.r[8]+=4;nz(&s,value,32);}}
 R32(object+120u,value);CHECK(push(&s,value,4,1));R32(object+112u,value);CHECK(push(&s,value,4,1));s.r[0]=0;nz(&s,0,32);R8(object+110u,b);byte(&s,0,b);CHECK(push(&s,s.r[0],4,1));R32(object+116u,value);CHECK(push(&s,value,4,1));CHECK(push(&s,object+128u,4,0));CHECK(call(&s,0xe220u,0x13d7au));
 W16(object+196u,0);R32(object+4u,s.r[10]);R16(object+8u,w);s.r[13]=sx16(w);R32(object+10u,s.r[5]);R16(object+14u,w);word(&s,6,w);R16(object+16u,w);word(&s,7,w);R16(object+18u,w);s.r[12]=sx16(w);
 s.r[3]=1;word(&s,2,0x3fffu);
 R16(object+154u,w);word(&s,1,w&0x3fffu);word(&s,0,(uint16_t)s.r[6]&0x3fffu);word(&s,1,(uint16_t)arithmetic(&s,s.r[1],s.r[0],16,0));word(&s,0,(uint16_t)s.r[1]);s.r[4]=14;word(&s,0,(uint16_t)s.r[0]>>14);
 R16(object+146u,w);s.r[9]=sx16(w);s.r[8]=sx16((uint16_t)s.r[0]);s.r[0]=arithmetic(&s,s.r[9],s.r[8],32,0);R32(object+4u,value);value=arithmetic(&s,value,s.r[0],32,0);W32(object+4u,value);word(&s,1,(uint16_t)s.r[1]&0x3fffu);W16(object+14u,s.r[1]);
 R16(object+156u,w);word(&s,1,w&0x3fffu);R16(object+16u,w);word(&s,0,w&0x3fffu);word(&s,1,(uint16_t)arithmetic(&s,s.r[1],s.r[0],16,0));word(&s,0,(uint16_t)s.r[1]>>14);R16(object+148u,w);word(&s,0,(uint16_t)arithmetic(&s,s.r[0],w,16,0));R16(object+8u,w);W16(object+8u,arithmetic(&s,w,s.r[0],16,0));word(&s,1,(uint16_t)s.r[1]&0x3fffu);W16(object+16u,s.r[1]);
 R16(object+158u,w);word(&s,1,w&0x3fffu);R16(object+18u,w);word(&s,0,w&0x3fffu);word(&s,1,(uint16_t)arithmetic(&s,s.r[1],s.r[0],16,0));word(&s,0,(uint16_t)s.r[1]>>14);R16(object+150u,w);s.r[9]=sx16(w);s.r[8]=sx16((uint16_t)s.r[0]);s.r[0]=arithmetic(&s,s.r[9],s.r[8],32,0);R32(object+10u,value);W32(object+10u,arithmetic(&s,value,s.r[0],32,0));word(&s,1,(uint16_t)s.r[1]&0x3fffu);W16(object+18u,s.r[1]);POP(20);
 R16(object+20u,mode);
 if(mode==1){
  W16(object+196u,0);R32(object+10u,s.r[4]);R32(object+80u,value);
  if(!less(s.r[4],value)){delta=5;direction=0;edgeoff=2;}
  else{R32(object+10u,s.r[4]);R32(object+84u,value);
   if(less(s.r[4],value)){delta=0xfffbu;direction=1;edgeoff=4;}
   else{R32(object+4u,s.r[4]);R32(object+72u,value);
    if(!less(s.r[4],value)){delta=1;direction=2;edgeoff=6;}
    else{R32(object+4u,s.r[4]);R32(object+76u,value);if(!less(s.r[4],value))goto finish;delta=0xffffu;direction=3;edgeoff=8;}}}
  CHECK(push(&s,delta,2,1));CHECK(push(&s,direction,2,1));R32(object+68u,s.r[8]);R16(s.r[8]+edgeoff,w);CHECK(push(&s,w,2,1));CHECK(push(&s,object,4,1));CHECK(call(&s,0x13b5au,0x13e8au));word(&s,3,(uint16_t)s.r[0]);W16(object+196u,1);POP(10);
 }else{R16(object+20u,mode);if(mode==2){
  R32(object+10u,s.r[4]);R32(object+56u,value);
  if(!less(s.r[4],value))direction=0;
  else{R32(object+10u,s.r[4]);R32(object+60u,value);
   if(less(s.r[4],value))direction=1;
   else{R32(object+4u,s.r[4]);R32(object+48u,value);
    if(!less(s.r[4],value))direction=2;
    else{R32(object+4u,s.r[4]);R32(object+52u,value);if(!less(s.r[4],value))goto finish;direction=3;}}}
  CHECK(push(&s,direction,2,1));R32(object+44u,value);CHECK(push(&s,value,4,1));CHECK(push(&s,object,4,1));CHECK(call(&s,0x13bb0u,0x13ee6u));word(&s,3,(uint16_t)s.r[0]);POP(10);
 }else word(&s,3,0);}
finish:
 nz(&s,s.r[3],16);
 if(!(uint16_t)s.r[3]){W32(object+4u,s.r[10]);W16(object+8u,s.r[13]);W32(object+10u,s.r[5]);W16(object+14u,s.r[6]);W16(object+16u,s.r[7]);W16(object+18u,s.r[12]);nz(&s,s.r[12],16);}
 for(i=2;i<=13;i++)if(i<=7||i>=10){R32(s.r[15],other);s.r[i]=other;POP(4);}

}
