/* Generated from the pinned GPU4D80 overlay by
 * scripts/generate_biwn_gpu_timer.py. Analyst static recompilation,
 * not recovered original source. Integer primitive behavior is checked
 * against the pinned Virtual Jaguar core; no core runs on the C side. */
#include "biwn_gpu_timer.h"
#include <string.h>
static void zn(struct biwn_gpu_timer_state *s,uint32_t v){s->z=v==0;s->n=v>>31;}
static uint32_t add(struct biwn_gpu_timer_state *s,uint32_t a,uint32_t b){uint32_t v=a+b;s->c=b>~a;zn(s,v);return v;}
static uint32_t sub(struct biwn_gpu_timer_state *s,uint32_t a,uint32_t b){uint32_t v=a-b;s->c=b>a;zn(s,v);return v;}
static int condition(struct biwn_gpu_timer_state *s,unsigned code){unsigned flags=s->z|(s->c<<1)|(s->n<<2);return !((code&1u)&&(flags&1u))&&!((code&2u)&&!(flags&1u))&&!((code&4u)&&(flags&(2u<<(code>>4))))&&!((code&8u)&&!(flags&(2u<<(code>>4))));}
static uint32_t be32(const uint8_t *p){return((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
static void put32(uint8_t *p,uint32_t v){p[0]=(uint8_t)(v>>24);p[1]=(uint8_t)(v>>16);p[2]=(uint8_t)(v>>8);p[3]=(uint8_t)v;}
static int local(uint32_t a){return a>=0xf03000u&&a<=0xf03ffcu;}
static int rd32(struct biwn_gpu_timer_bus *bus,struct biwn_gpu_timer_state *s,uint32_t a,uint32_t *v){if(local(a)){*v=be32(s->local_RAM+a-0xf03000u);return 0;}if(a==0xf02100u){s->flags=(s->flags&~7u)|(s->n<<2)|(s->c<<1)|s->z;*v=s->flags&0xffffc1ffu;return 0;}if(a==0xf02104u){*v=s->matrix_control;return 0;}if(a==0xf02108u){*v=s->matrix_pointer;return 0;}return bus->read32(bus->context,a,v)?2:0;}
static int rd16(struct biwn_gpu_timer_bus *bus,struct biwn_gpu_timer_state *s,uint32_t a,uint32_t *v){uint16_t h;if(a>=0xf03000u&&a<=0xf03ffeu){unsigned p=a-0xf03000u;*v=((uint32_t)s->local_RAM[p]<<8)|s->local_RAM[p+1];return 0;}if(bus->read16(bus->context,a,&h))return 2;*v=h;return 0;}
static int loadw(struct biwn_gpu_timer_bus *bus,struct biwn_gpu_timer_state *s,uint32_t a,uint32_t *v){if(a>=0xf03000u&&a<=0xf03fffu)return rd32(bus,s,a&~3u,v);return rd16(bus,s,a,v);}
static int wr32(struct biwn_gpu_timer_bus *bus,struct biwn_gpu_timer_state *s,uint32_t a,uint32_t v){if(local(a)){put32(s->local_RAM+a-0xf03000u,v);return 0;}if(a==0xf02100u){s->flags=(v&~8u)|((v&8u)?(s->flags&8u):0);s->z=s->flags&1u;s->c=(s->flags>>1)&1u;s->n=(s->flags>>2)&1u;s->control&=~((s->flags&0x3e00u)>>3);s->active_bank=(!(s->flags&8u)&&(s->flags&0x4000u))?1u:0u;return bus->write32(bus->context,a,v)?2:0;}if(a==0xf02104u){s->matrix_control=v;return 0;}if(a==0xf02108u){s->matrix_pointer=v&~3u;return 0;}return bus->write32(bus->context,a,v)?2:0;}
static int wr16(struct biwn_gpu_timer_bus *bus,struct biwn_gpu_timer_state *s,uint32_t a,uint32_t v){if(a>=0xf03000u&&a<=0xf03fffu)return wr32(bus,s,a&~1u,v&0xffffu);return bus->write16(bus->context,a,(uint16_t)v)?2:0;}
#define CHECK(e) do{int status=(e);if(status)return(enum biwn_gpu_timer_status)status;}while(0)
enum biwn_gpu_timer_status biwn_gpu_timer_run(struct biwn_gpu_timer_bus *bus,struct biwn_gpu_timer_state *state,uint32_t budget,uint32_t returnPC){struct biwn_gpu_timer_state s;uint32_t v,target=0;unsigned pending=0;if(!bus||!state||!budget||!bus->read16||!bus->read32||!bus->write16||!bus->write32||state->active_bank||state->z>1||state->c>1||state->n>1)return 1;s=*state;while(budget--){unsigned delayed=pending;uint32_t resume=target;pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){
  case 0xf03020u: /* movei   $f03140,r28 */
   s.registers[0][28]=0xf03140u;
   s.pc=0xf03026u;break;
  case 0xf03026u: /* movei   $f02100,r30 */
   s.registers[0][30]=0xf02100u;
   s.pc=0xf0302cu;break;
  case 0xf0302cu: /* jump    (r28) */
   if(condition(&s,0)){pending=1;target=s.registers[0][28];}
   s.pc=0xf0302eu;break;
  case 0xf0302eu: /* load    (r30),r29 */
   CHECK(rd32(bus,&s,s.registers[0][30]&~3u,&v));s.registers[0][29]=v;
   s.pc=0xf03030u;break;
  case 0xf03140u: /* movei   $778cc,r28 */
   s.registers[0][28]=0x778ccu;
   s.pc=0xf03146u;break;
  case 0xf03146u: /* load    (r28),r30 */
   CHECK(rd32(bus,&s,s.registers[0][28]&~3u,&v));s.registers[0][30]=v;
   s.pc=0xf03148u;break;
  case 0xf03148u: /* addq    $1,r30 */
   s.registers[0][30]=add(&s,s.registers[0][30],1u);
   s.pc=0xf0314au;break;
  case 0xf0314au: /* store   r30,(r28) */
   CHECK(wr32(bus,&s,local(s.registers[0][28])?(s.registers[0][28]&~3u):s.registers[0][28],s.registers[0][30]));
   s.pc=0xf0314cu;break;
  case 0xf0314cu: /* subq    $4,r31 */
   s.registers[0][31]=sub(&s,s.registers[0][31],4u);
   s.pc=0xf0314eu;break;
  case 0xf0314eu: /* store   r0,(r31) */
   CHECK(wr32(bus,&s,local(s.registers[0][31])?(s.registers[0][31]&~3u):s.registers[0][31],s.registers[0][0]));
   s.pc=0xf03150u;break;
  case 0xf03150u: /* movei   $bd858,r28 */
   s.registers[0][28]=0xbd858u;
   s.pc=0xf03156u;break;
  case 0xf03156u: /* load    (r28),r30 */
   CHECK(rd32(bus,&s,s.registers[0][28]&~3u,&v));s.registers[0][30]=v;
   s.pc=0xf03158u;break;
  case 0xf03158u: /* subq    $4,r28 */
   s.registers[0][28]=sub(&s,s.registers[0][28],4u);
   s.pc=0xf0315au;break;
  case 0xf0315au: /* load    (r28),r0 */
   CHECK(rd32(bus,&s,s.registers[0][28]&~3u,&v));s.registers[0][0]=v;
   s.pc=0xf0315cu;break;
  case 0xf0315cu: /* add     r30,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][30]);
   s.pc=0xf0315eu;break;
  case 0xf0315eu: /* jr      nc,00F0316A */
   if(condition(&s,4)){pending=1;target=0xf0316au;}
   s.pc=0xf03160u;break;
  case 0xf03160u: /* store   r0,(r28) */
   CHECK(wr32(bus,&s,local(s.registers[0][28])?(s.registers[0][28]&~3u):s.registers[0][28],s.registers[0][0]));
   s.pc=0xf03162u;break;
  case 0xf03162u: /* subq    $2,r28 */
   s.registers[0][28]=sub(&s,s.registers[0][28],2u);
   s.pc=0xf03164u;break;
  case 0xf03164u: /* loadw   (r28),r0 */
   CHECK(loadw(bus,&s,s.registers[0][28],&v));s.registers[0][0]=v;
   s.pc=0xf03166u;break;
  case 0xf03166u: /* addq    $1,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],1u);
   s.pc=0xf03168u;break;
  case 0xf03168u: /* storew  r0,(r28) */
   CHECK(wr16(bus,&s,s.registers[0][28],s.registers[0][0]));
   s.pc=0xf0316au;break;
  case 0xf0316au: /* load    (r31),r0 */
   CHECK(rd32(bus,&s,s.registers[0][31]&~3u,&v));s.registers[0][0]=v;
   s.pc=0xf0316cu;break;
  case 0xf0316cu: /* addq    $4,r31 */
   s.registers[0][31]=add(&s,s.registers[0][31],4u);
   s.pc=0xf0316eu;break;
  case 0xf0316eu: /* movei   $f031ac,r30 */
   s.registers[0][30]=0xf031acu;
   s.pc=0xf03174u;break;
  case 0xf03174u: /* jump    (r30) */
   if(condition(&s,0)){pending=1;target=s.registers[0][30];}
   s.pc=0xf03176u;break;
  case 0xf03176u: /* bset    $b,r29 */
   s.registers[0][29]|=(1u<<11);
   zn(&s,s.registers[0][29]);
   s.pc=0xf03178u;break;
  case 0xf031acu: /* load    (r31),r28 */
   CHECK(rd32(bus,&s,s.registers[0][31]&~3u,&v));s.registers[0][28]=v;
   s.pc=0xf031aeu;break;
  case 0xf031aeu: /* movei   $f02100,r30 */
   s.registers[0][30]=0xf02100u;
   s.pc=0xf031b4u;break;
  case 0xf031b4u: /* addq    $2,r28 */
   s.registers[0][28]=add(&s,s.registers[0][28],2u);
   s.pc=0xf031b6u;break;
  case 0xf031b6u: /* addq    $4,r31 */
   s.registers[0][31]=add(&s,s.registers[0][31],4u);
   s.pc=0xf031b8u;break;
  case 0xf031b8u: /* bclr    $3,r29 */
   s.registers[0][29]&=~(1u<<3);
   zn(&s,s.registers[0][29]);
   s.pc=0xf031bau;break;
  case 0xf031bau: /* jump    (r28) */
   if(condition(&s,0)){pending=1;target=s.registers[0][28];}
   s.pc=0xf031bcu;break;
  case 0xf031bcu: /* store   r29,(r30) */
   CHECK(wr32(bus,&s,local(s.registers[0][30])?(s.registers[0][30]&~3u):s.registers[0][30],s.registers[0][29]));
   s.pc=0xf031beu;break;default:return BIWN_GPU_TIMER_BAD_PC;
}if(delayed){if(pending)return BIWN_GPU_TIMER_BAD_DELAY;s.pc=resume;}if(!pending&&s.pc==returnPC){*state=s;return 0;}}return BIWN_GPU_TIMER_WORK_LIMIT;}
enum biwn_gpu_timer_status biwn_gpu_timer_assert(struct biwn_gpu_timer_bus *bus,struct biwn_gpu_timer_state *state){struct biwn_gpu_timer_state s;uint32_t a;if(!bus||!state||!bus->write32||state->active_bank>1||state->z>1||state->c>1||state->n>1)return 1;s=*state;if(!(s.control&1u))return 6;s.control|=0x100u;if((s.control&8u)||(s.flags&8u)||!(s.flags&0x40u)){*state=s;return 7;}s.flags|=8u;s.active_bank=0;s.registers[0][31]-=4u;a=s.registers[0][31]&~3u;CHECK(wr32(bus,&s,a,s.pc-2u));s.pc=s.registers[0][30]=0xf03020u;*state=s;return 0;}
