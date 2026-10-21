/* Coordinator13B5A/13BB0 high-level source, original-facing ABI.
 * Derived from existing portable collision body; geometry executes guest code.
 * Original unbounded list scan retained; fixture runner bounds execution. */
#include "actor-collision-native.h"
struct collision {uint32_t *r;};
static uint32_t sx16(uint16_t v){return(uint32_t)(v&0x7fffu)-(uint32_t)(v&0x8000u);}
static void word(struct collision *s,unsigned i,uint16_t v){s->r[i]=(s->r[i]&0xffff0000u)|v;}
static void nz(struct collision *s,uint32_t v,unsigned bits){uint32_t mask=bits==32?0xffffffffu:0xffffu,sign=1u<<(bits-1);v&=mask;s->r[16]=(uint16_t)((s->r[16]&0xfff0u)|(v?0:4)|(v&sign?8:0));}
static void xflag(struct collision *s,unsigned x){s->r[16]=(uint16_t)((s->r[16]&~0x10u)|(x?0x10u:0));}
static uint16_t add(struct collision *s,uint16_t a,uint16_t b){uint32_t v=(uint32_t)a+b;xflag(s,v>0xffffu);return(uint16_t)v;}
static uint16_t sub(struct collision *s,uint16_t a,uint16_t b){xflag(s,a<b);return(uint16_t)(a-b);}
static uint16_t asr6(struct collision *s,uint16_t v){xflag(s,(v>>5)&1u);return(uint16_t)((v>>6)|(v&0x8000u?0xfc00u:0));}
#define R16(a,v) do{(v)=ACR16(a);}while(0)
#define R32(a,v) do{(v)=ACR32(a);}while(0)
#define W16(a,v) do{ACW16(a,v);}while(0)
#define CHECK(e) do{(void)(e);}while(0)
#define POP(n) do{s.r[15]+=(n);}while(0)
static void push(struct collision*s,uint32_t v,unsigned width){s->r[15]-=width;if(width==2)ACW16(s->r[15],v);else ACW32(s->r[15],v);nz(s,v,width*8);}
static void geometry(struct collision*s,uint32_t target,uint32_t ret){(void)ret;switch(target){case 0x1039c:biwn_native_actor_collision_outside_index_capture(s->r);break;case 0x102c4:biwn_native_actor_collision_outside_scan_capture(s->r);break;case 0x1028e:biwn_native_actor_collision_inside_outside_capture(s->r);break;case 0x10652:biwn_native_actor_collision_inside_index_capture(s->r);break;default:__builtin_trap();}}
void biwn_native_actor_collision_body(uint32_t *r)
{
 struct collision s;uint32_t object,entry,value,old;uint16_t w,b,edge,direction,index,flags,target;
 s.r=r;entry=r[18];CHECK(push(&s,s.r[10],4));
 if(entry==0x13b5au){
  CHECK(push(&s,s.r[2],4));R32(s.r[15]+12u,s.r[10]);object=s.r[10];R16(s.r[15]+16u,edge);word(&s,1,edge);R16(s.r[15]+20u,w);word(&s,2,w);word(&s,0,edge&0xf000u);
  if(!(edge&0xf000u)){word(&s,1,edge&0xfffu);CHECK(push(&s,s.r[1],2));CHECK(push(&s,object,4));CHECK(geometry(&s,0x1039cu,0x13b80u));POP(6);}
  else if(edge==0xffffu){
   R16(object+64u,w);W16(object+64u,add(&s,w,(uint16_t)s.r[2]));CHECK(push(&s,object,4));CHECK(geometry(&s,0x102c4u,0x13b96u));POP(4);
   if((uint16_t)s.r[0]){s.r[0]=1;nz(&s,1,32);}
   else{R16(object+64u,w);W16(object+64u,sub(&s,w,(uint16_t)s.r[2]));word(&s,0,0);nz(&s,0,16);}
  }else{word(&s,0,0);nz(&s,0,16);}
  R32(s.r[15],s.r[2]);POP(4);nz(&s,s.r[2],32);R32(s.r[15],s.r[10]);POP(4);return;
 }
 R32(s.r[15]+8u,s.r[10]);object=s.r[10];R32(s.r[15]+12u,s.r[9]);R16(s.r[15]+16u,direction);word(&s,0,direction);
 switch(direction){
 case 0:R16(object+6u,w);R16(object+54u,b);word(&s,0,asr6(&s,sub(&s,w,b)));word(&s,1,(uint16_t)s.r[0]);R16(s.r[9]+8u,w);word(&s,1,add(&s,(uint16_t)s.r[1],w));break;
 case 1:R16(object+50u,w);R16(object+6u,b);word(&s,1,asr6(&s,sub(&s,w,b)));R16(s.r[9]+8u,w);xflag(&s,(w>>15)&1u);word(&s,0,(uint16_t)(w<<1));R16(s.r[9]+6u,w);word(&s,0,add(&s,(uint16_t)s.r[0],w));word(&s,1,add(&s,(uint16_t)s.r[1],(uint16_t)s.r[0]));break;
 case 2:R16(object+58u,w);R16(object+12u,b);word(&s,0,asr6(&s,sub(&s,w,b)));R16(s.r[9]+8u,w);word(&s,1,w);R16(s.r[9]+6u,w);word(&s,1,add(&s,(uint16_t)s.r[1],w));word(&s,1,add(&s,(uint16_t)s.r[1],(uint16_t)s.r[0]));break;
 case 3:R16(object+12u,w);R16(object+62u,b);word(&s,0,sub(&s,w,b));word(&s,1,asr6(&s,(uint16_t)s.r[0]));break;
 default:break;
 }
 R16(s.r[9]+22u,index);if(index==0xffffu)goto indoor_fail;
 R32(0x49c18u,s.r[8]);R16(s.r[9]+22u,index);s.r[0]=sx16(index)*6u;R32(s.r[8]+8u,value);old=s.r[0];s.r[0]+=value;xflag(&s,s.r[0]<old);s.r[8]=s.r[0];
 for(;;){
  R16(s.r[8],w);
  if((uint16_t)s.r[1]==w)break;
  R16(s.r[8]+2u,flags);if(flags&0x8000u)goto indoor_fail;s.r[8]+=6u;
 }
 R16(s.r[8]+2u,flags);word(&s,0,flags&0x7000u);if(!(flags&0x7000u))goto indoor_fail;
 R16(s.r[8]+4u,target);
 if(target!=0xffffu){R16(s.r[8]+4u,target);CHECK(push(&s,target,2));CHECK(push(&s,object,4));CHECK(geometry(&s,0x10652u,0x13c86u));POP(6);goto indoor_done;}
 R16(object+22u,w);if(w)goto indoor_fail;CHECK(push(&s,object,4));CHECK(geometry(&s,0x1028eu,0x13c66u));POP(4);
 if((uint16_t)s.r[0]){W16(object+20u,1);s.r[0]=2;nz(&s,2,32);goto indoor_done;}
indoor_fail:
 word(&s,0,0);nz(&s,0,16);
indoor_done:
 R32(s.r[15],s.r[10]);POP(4);return;
}