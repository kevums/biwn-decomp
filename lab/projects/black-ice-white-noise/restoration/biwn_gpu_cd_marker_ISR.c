/* Generated from the pinned GPU4D80 overlay by
 * scripts/generate_biwn_gpu_cd_marker_ISR.py. Analyst static recompilation,
 * not recovered original source. Integer primitive behavior is checked
 * against the pinned Virtual Jaguar core; no core runs on the C side. */
#include "biwn_gpu_cd_marker_ISR.h"
#include <string.h>
static void zn(struct biwn_gpu_cd_marker_ISR_state *s,uint32_t v){s->z=v==0;s->n=v>>31;}
static uint32_t add(struct biwn_gpu_cd_marker_ISR_state *s,uint32_t a,uint32_t b){uint32_t v=a+b;s->c=b>~a;zn(s,v);return v;}
static uint32_t sub(struct biwn_gpu_cd_marker_ISR_state *s,uint32_t a,uint32_t b){uint32_t v=a-b;s->c=b>a;zn(s,v);return v;}
static int condition(struct biwn_gpu_cd_marker_ISR_state *s,unsigned code){unsigned flags=s->z|(s->c<<1)|(s->n<<2);return !((code&1u)&&(flags&1u))&&!((code&2u)&&!(flags&1u))&&!((code&4u)&&(flags&(2u<<(code>>4))))&&!((code&8u)&&!(flags&(2u<<(code>>4))));}
static uint32_t be32(const uint8_t *p){return((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
static void put32(uint8_t *p,uint32_t v){p[0]=(uint8_t)(v>>24);p[1]=(uint8_t)(v>>16);p[2]=(uint8_t)(v>>8);p[3]=(uint8_t)v;}
static int local(uint32_t a){return a>=0xf03000u&&a<=0xf03ffcu;}
static int rd32(struct biwn_gpu_cd_marker_ISR_bus *bus,struct biwn_gpu_cd_marker_ISR_state *s,uint32_t a,uint32_t *v){if(local(a)){*v=be32(s->local_RAM+a-0xf03000u);return 0;}if(a==0xf02100u){s->flags=(s->flags&~7u)|(s->n<<2)|(s->c<<1)|s->z;*v=s->flags&0xffffc1ffu;return 0;}if(a==0xf02104u){*v=s->matrix_control;return 0;}if(a==0xf02108u){*v=s->matrix_pointer;return 0;}return bus->read32(bus->context,a,v)?2:0;}
static int rd16(struct biwn_gpu_cd_marker_ISR_bus *bus,struct biwn_gpu_cd_marker_ISR_state *s,uint32_t a,uint32_t *v){uint16_t h;if(a>=0xf03000u&&a<=0xf03ffeu){unsigned p=a-0xf03000u;*v=((uint32_t)s->local_RAM[p]<<8)|s->local_RAM[p+1];return 0;}if(bus->read16(bus->context,a,&h))return 2;*v=h;return 0;}
static int loadw(struct biwn_gpu_cd_marker_ISR_bus *bus,struct biwn_gpu_cd_marker_ISR_state *s,uint32_t a,uint32_t *v){if(a>=0xf03000u&&a<=0xf03fffu)return rd32(bus,s,a&~3u,v);return rd16(bus,s,a,v);}
static int wr32(struct biwn_gpu_cd_marker_ISR_bus *bus,struct biwn_gpu_cd_marker_ISR_state *s,uint32_t a,uint32_t v){if(local(a)){put32(s->local_RAM+a-0xf03000u,v);return 0;}if(a==0xf02100u){s->flags=(v&~8u)|((v&8u)?(s->flags&8u):0);s->z=s->flags&1u;s->c=(s->flags>>1)&1u;s->n=(s->flags>>2)&1u;s->control&=~((s->flags&0x3e00u)>>3);s->active_bank=(!(s->flags&8u)&&(s->flags&0x4000u))?1u:0u;return bus->write32(bus->context,a,v)?2:0;}if(a==0xf02104u){s->matrix_control=v;return 0;}if(a==0xf02108u){s->matrix_pointer=v&~3u;return 0;}return bus->write32(bus->context,a,v)?2:0;}
static int wr16(struct biwn_gpu_cd_marker_ISR_bus *bus,struct biwn_gpu_cd_marker_ISR_state *s,uint32_t a,uint32_t v){if(a>=0xf03000u&&a<=0xf03fffu)return wr32(bus,s,a&~1u,v&0xffffu);return bus->write16(bus->context,a,(uint16_t)v)?2:0;}
#define CHECK(e) do{int status=(e);if(status)return(enum biwn_gpu_cd_marker_ISR_status)status;}while(0)
enum biwn_gpu_cd_marker_ISR_status biwn_gpu_cd_marker_ISR_run(struct biwn_gpu_cd_marker_ISR_bus *bus,struct biwn_gpu_cd_marker_ISR_state *state,uint32_t budget,uint32_t returnPC){struct biwn_gpu_cd_marker_ISR_state s;uint32_t v,target=0;unsigned pending=0;if(!bus||!state||!budget||!bus->read16||!bus->read32||!bus->write16||!bus->write32||state->active_bank||state->z>1||state->c>1||state->n>1)return 1;s=*state;while(budget--){unsigned delayed=pending;uint32_t resume=target;pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){
  case 0xf03010u: /* movei   $f03064,r30 */
   s.registers[0][30]=0xf03064u;
   s.pc=0xf03016u;break;
  case 0xf03016u: /* jump    (r30) */
   if(condition(&s,0)){pending=1;target=s.registers[0][30];}
   s.pc=0xf03018u;break;
  case 0xf03018u: /* nop */
   s.pc=0xf0301au;break;
  case 0xf03064u: /* movei   $f02100,r30 */
   s.registers[0][30]=0xf02100u;
   s.pc=0xf0306au;break;
  case 0xf0306au: /* load    (r30),r29 */
   CHECK(rd32(bus,&s,s.registers[0][30]&~3u,&v));s.registers[0][29]=v;
   s.pc=0xf0306cu;break;
  case 0xf0306cu: /* subq    $4,r31 */
   s.registers[0][31]=sub(&s,s.registers[0][31],4u);
   s.pc=0xf0306eu;break;
  case 0xf0306eu: /* store   r25,(r31) */
   CHECK(wr32(bus,&s,local(s.registers[0][31])?(s.registers[0][31]&~3u):s.registers[0][31],s.registers[0][25]));
   s.pc=0xf03070u;break;
  case 0xf03070u: /* subq    $4,r31 */
   s.registers[0][31]=sub(&s,s.registers[0][31],4u);
   s.pc=0xf03072u;break;
  case 0xf03072u: /* store   r24,(r31) */
   CHECK(wr32(bus,&s,local(s.registers[0][31])?(s.registers[0][31]&~3u):s.registers[0][31],s.registers[0][24]));
   s.pc=0xf03074u;break;
  case 0xf03074u: /* movei   $dfff00,r24 */
   s.registers[0][24]=0xdfff00u;
   s.pc=0xf0307au;break;
  case 0xf0307au: /* subq    $4,r31 */
   s.registers[0][31]=sub(&s,s.registers[0][31],4u);
   s.pc=0xf0307cu;break;
  case 0xf0307cu: /* store   r27,(r31) */
   CHECK(wr32(bus,&s,local(s.registers[0][31])?(s.registers[0][31]&~3u):s.registers[0][31],s.registers[0][27]));
   s.pc=0xf0307eu;break;
  case 0xf0307eu: /* load    (r24),r27 */
   CHECK(rd32(bus,&s,s.registers[0][24]&~3u,&v));s.registers[0][27]=v;
   s.pc=0xf03080u;break;
  case 0xf03080u: /* subq    $4,r31 */
   s.registers[0][31]=sub(&s,s.registers[0][31],4u);
   s.pc=0xf03082u;break;
  case 0xf03082u: /* store   r26,(r31) */
   CHECK(wr32(bus,&s,local(s.registers[0][31])?(s.registers[0][31]&~3u):s.registers[0][31],s.registers[0][26]));
   s.pc=0xf03084u;break;
  case 0xf03084u: /* subq    $4,r31 */
   s.registers[0][31]=sub(&s,s.registers[0][31],4u);
   s.pc=0xf03086u;break;
  case 0xf03086u: /* store   r23,(r31) */
   CHECK(wr32(bus,&s,local(s.registers[0][31])?(s.registers[0][31]&~3u):s.registers[0][31],s.registers[0][23]));
   s.pc=0xf03088u;break;
  case 0xf03088u: /* subq    $4,r31 */
   s.registers[0][31]=sub(&s,s.registers[0][31],4u);
   s.pc=0xf0308au;break;
  case 0xf0308au: /* store   r22,(r31) */
   CHECK(wr32(bus,&s,local(s.registers[0][31])?(s.registers[0][31]&~3u):s.registers[0][31],s.registers[0][22]));
   s.pc=0xf0308cu;break;
  case 0xf0308cu: /* move    pc,r23 */
   s.registers[0][23]=0xf0308cu;
   s.pc=0xf0308eu;break;
  case 0xf0308eu: /* movei   $3c,r28 */
   s.registers[0][28]=0x3cu;
   s.pc=0xf03094u;break;
  case 0xf03094u: /* sub     r28,r23 */
   s.registers[0][23]=sub(&s,s.registers[0][23],s.registers[0][28]);
   s.pc=0xf03096u;break;
  case 0xf03096u: /* move    pc,r25 */
   s.registers[0][25]=0xf03096u;
   s.pc=0xf03098u;break;
  case 0xf03098u: /* movei   $88,r26 */
   s.registers[0][26]=0x88u;
   s.pc=0xf0309eu;break;
  case 0xf0309eu: /* add     r26,r25 */
   s.registers[0][25]=add(&s,s.registers[0][25],s.registers[0][26]);
   s.pc=0xf030a0u;break;
  case 0xf030a0u: /* btst    $d,r27 */
   s.z=((~s.registers[0][27])>>13)&1u;
   s.pc=0xf030a2u;break;
  case 0xf030a2u: /* jr      z,00F030C2 */
   if(condition(&s,2)){pending=1;target=0xf030c2u;}
   s.pc=0xf030a4u;break;
  case 0xf030a4u: /* bclr    $5,r27 */
   s.registers[0][27]&=~(1u<<5);
   zn(&s,s.registers[0][27]);
   s.pc=0xf030a6u;break;
  case 0xf030a6u: /* bset    $1,r27 */
   s.registers[0][27]|=(1u<<1);
   zn(&s,s.registers[0][27]);
   s.pc=0xf030a8u;break;
  case 0xf030a8u: /* store   r27,(r24) */
   CHECK(wr32(bus,&s,local(s.registers[0][24])?(s.registers[0][24]&~3u):s.registers[0][24],s.registers[0][27]));
   s.pc=0xf030aau;break;
  case 0xf030aau: /* addq    $10,r24 */
   s.registers[0][24]=add(&s,s.registers[0][24],16u);
   s.pc=0xf030acu;break;
  case 0xf030acu: /* load    (r24),r27 */
   CHECK(rd32(bus,&s,s.registers[0][24]&~3u,&v));s.registers[0][27]=v;
   s.pc=0xf030aeu;break;
  case 0xf030aeu: /* bset    $2,r27 */
   s.registers[0][27]|=(1u<<2);
   zn(&s,s.registers[0][27]);
   s.pc=0xf030b0u;break;
  case 0xf030b0u: /* store   r27,(r24) */
   CHECK(wr32(bus,&s,local(s.registers[0][24])?(s.registers[0][24]&~3u):s.registers[0][24],s.registers[0][27]));
   s.pc=0xf030b2u;break;
  case 0xf030b2u: /* subq    $c,r24 */
   s.registers[0][24]=sub(&s,s.registers[0][24],12u);
   s.pc=0xf030b4u;break;
  case 0xf030b4u: /* load    (r24),r26 */
   CHECK(rd32(bus,&s,s.registers[0][24]&~3u,&v));s.registers[0][26]=v;
   s.pc=0xf030b6u;break;
  case 0xf030b6u: /* addq    $6,r24 */
   s.registers[0][24]=add(&s,s.registers[0][24],6u);
   s.pc=0xf030b8u;break;
  case 0xf030b8u: /* loadw   (r24),r27 */
   CHECK(loadw(bus,&s,s.registers[0][24],&v));s.registers[0][27]=v;
   s.pc=0xf030bau;break;
  case 0xf030bau: /* btst    $a,r27 */
   s.z=((~s.registers[0][27])>>10)&1u;
   s.pc=0xf030bcu;break;
  case 0xf030bcu: /* jr      nz,00F030DC */
   if(condition(&s,1)){pending=1;target=0xf030dcu;}
   s.pc=0xf030beu;break;
  case 0xf030beu: /* or      r26,r26 */
   s.registers[0][26]|=s.registers[0][26];
   zn(&s,s.registers[0][26]);
   s.pc=0xf030c0u;break;
  case 0xf030c0u: /* jump    (r25) */
   if(condition(&s,0)){pending=1;target=s.registers[0][25];}
   s.pc=0xf030c2u;break;
  case 0xf030c2u: /* addq    $c,r23 */
   s.registers[0][23]=add(&s,s.registers[0][23],12u);
   s.pc=0xf030c4u;break;
  case 0xf030c4u: /* load    (r23),r26 */
   CHECK(rd32(bus,&s,s.registers[0][23]&~3u,&v));s.registers[0][26]=v;
   s.pc=0xf030c6u;break;
  case 0xf030c6u: /* cmpq    $0,r26 */
   (void)sub(&s,s.registers[0][26],0x0u);
   s.pc=0xf030c8u;break;
  case 0xf030c8u: /* jr      z,00F030D6 */
   if(condition(&s,2)){pending=1;target=0xf030d6u;}
   s.pc=0xf030cau;break;
  case 0xf030cau: /* subq    $c,r23 */
   s.registers[0][23]=sub(&s,s.registers[0][23],12u);
   s.pc=0xf030ccu;break;
  case 0xf030ccu: /* move    r25,r28 */
   s.registers[0][28]=s.registers[0][25];
   s.pc=0xf030ceu;break;
  case 0xf030ceu: /* addq    $1c,r28 */
   s.registers[0][28]=add(&s,s.registers[0][28],28u);
   s.pc=0xf030d0u;break;
  case 0xf030d0u: /* addq    $c,r23 */
   s.registers[0][23]=add(&s,s.registers[0][23],12u);
   s.pc=0xf030d2u;break;
  case 0xf030d2u: /* addq    $1c,r28 */
   s.registers[0][28]=add(&s,s.registers[0][28],28u);
   s.pc=0xf030d4u;break;
  case 0xf030d4u: /* jump    (r28) */
   if(condition(&s,0)){pending=1;target=s.registers[0][28];}
   s.pc=0xf030d6u;break;
  case 0xf030d6u: /* btst    $e,r27 */
   s.z=((~s.registers[0][27])>>14)&1u;
   s.pc=0xf030d8u;break;
  case 0xf030d8u: /* jr      z,00F030EC */
   if(condition(&s,2)){pending=1;target=0xf030ecu;}
   s.pc=0xf030dau;break;
  case 0xf030dau: /* bset    $1f,r27 */
   s.registers[0][27]|=(1u<<31);
   zn(&s,s.registers[0][27]);
   s.pc=0xf030dcu;break;
  case 0xf030dcu: /* addq    $10,r24 */
   s.registers[0][24]=add(&s,s.registers[0][24],16u);
   s.pc=0xf030deu;break;
  case 0xf030deu: /* load    (r24),r28 */
   CHECK(rd32(bus,&s,s.registers[0][24]&~3u,&v));s.registers[0][28]=v;
   s.pc=0xf030e0u;break;
  case 0xf030e0u: /* or      r28,r28 */
   s.registers[0][28]|=s.registers[0][28];
   zn(&s,s.registers[0][28]);
   s.pc=0xf030e2u;break;
  case 0xf030e2u: /* subq    $10,r24 */
   s.registers[0][24]=sub(&s,s.registers[0][24],16u);
   s.pc=0xf030e4u;break;
  case 0xf030e4u: /* load    (r23),r28 */
   CHECK(rd32(bus,&s,s.registers[0][23]&~3u,&v));s.registers[0][28]=v;
   s.pc=0xf030e6u;break;
  case 0xf030e6u: /* addq    $8,r23 */
   s.registers[0][23]=add(&s,s.registers[0][23],8u);
   s.pc=0xf030e8u;break;
  case 0xf030e8u: /* store   r28,(r23) */
   CHECK(wr32(bus,&s,local(s.registers[0][23])?(s.registers[0][23]&~3u):s.registers[0][23],s.registers[0][28]));
   s.pc=0xf030eau;break;
  case 0xf030eau: /* subq    $8,r23 */
   s.registers[0][23]=sub(&s,s.registers[0][23],8u);
   s.pc=0xf030ecu;break;
  case 0xf030ecu: /* load    (r23),r26 */
   CHECK(rd32(bus,&s,s.registers[0][23]&~3u,&v));s.registers[0][26]=v;
   s.pc=0xf030eeu;break;
  case 0xf030eeu: /* addq    $4,r23 */
   s.registers[0][23]=add(&s,s.registers[0][23],4u);
   s.pc=0xf030f0u;break;
  case 0xf030f0u: /* load    (r23),r28 */
   CHECK(rd32(bus,&s,s.registers[0][23]&~3u,&v));s.registers[0][28]=v;
   s.pc=0xf030f2u;break;
  case 0xf030f2u: /* subq    $4,r23 */
   s.registers[0][23]=sub(&s,s.registers[0][23],4u);
   s.pc=0xf030f4u;break;
  case 0xf030f4u: /* cmp     r26,r28 */
   (void)sub(&s,s.registers[0][28],s.registers[0][26]);
   s.pc=0xf030f6u;break;
  case 0xf030f6u: /* jr      nn,00F030FC */
   if(condition(&s,20)){pending=1;target=0xf030fcu;}
   s.pc=0xf030f8u;break;
  case 0xf030f8u: /* bclr    $0,r27 */
   s.registers[0][27]&=~(1u<<0);
   zn(&s,s.registers[0][27]);
   s.pc=0xf030fau;break;
  case 0xf030fau: /* store   r27,(r24) */
   CHECK(wr32(bus,&s,local(s.registers[0][24])?(s.registers[0][24]&~3u):s.registers[0][24],s.registers[0][27]));
   s.pc=0xf030fcu;break;
  case 0xf030fcu: /* movei   $dfff24,r27 */
   s.registers[0][27]=0xdfff24u;
   s.pc=0xf03102u;break;
  case 0xf03102u: /* move    r27,r25 */
   s.registers[0][25]=s.registers[0][27];
   s.pc=0xf03104u;break;
  case 0xf03104u: /* addq    $4,r27 */
   s.registers[0][27]=add(&s,s.registers[0][27],4u);
   s.pc=0xf03106u;break;
  case 0xf03106u: /* moveq   3,r24 */
   s.registers[0][24]=3u;
   s.pc=0xf03108u;break;
  case 0xf03108u: /* load    (r27),r28 */
   CHECK(rd32(bus,&s,s.registers[0][27]&~3u,&v));s.registers[0][28]=v;
   s.pc=0xf0310au;break;
  case 0xf0310au: /* load    (r25),r30 */
   CHECK(rd32(bus,&s,s.registers[0][25]&~3u,&v));s.registers[0][30]=v;
   s.pc=0xf0310cu;break;
  case 0xf0310cu: /* addq    $4,r26 */
   s.registers[0][26]=add(&s,s.registers[0][26],4u);
   s.pc=0xf0310eu;break;
  case 0xf0310eu: /* bclr    $0,r26 */
   s.registers[0][26]&=~(1u<<0);
   zn(&s,s.registers[0][26]);
   s.pc=0xf03110u;break;
  case 0xf03110u: /* store   r28,(r26) */
   CHECK(wr32(bus,&s,local(s.registers[0][26])?(s.registers[0][26]&~3u):s.registers[0][26],s.registers[0][28]));
   s.pc=0xf03112u;break;
  case 0xf03112u: /* addq    $4,r26 */
   s.registers[0][26]=add(&s,s.registers[0][26],4u);
   s.pc=0xf03114u;break;
  case 0xf03114u: /* bclr    $0,r26 */
   s.registers[0][26]&=~(1u<<0);
   zn(&s,s.registers[0][26]);
   s.pc=0xf03116u;break;
  case 0xf03116u: /* subq    $1,r24 */
   s.registers[0][24]=sub(&s,s.registers[0][24],1u);
   s.pc=0xf03118u;break;
  case 0xf03118u: /* jr      nn,00F03108 */
   if(condition(&s,20)){pending=1;target=0xf03108u;}
   s.pc=0xf0311au;break;
  case 0xf0311au: /* store   r30,(r26) */
   CHECK(wr32(bus,&s,local(s.registers[0][26])?(s.registers[0][26]&~3u):s.registers[0][26],s.registers[0][30]));
   s.pc=0xf0311cu;break;
  case 0xf0311cu: /* store   r26,(r23) */
   CHECK(wr32(bus,&s,local(s.registers[0][23])?(s.registers[0][23]&~3u):s.registers[0][23],s.registers[0][26]));
   s.pc=0xf0311eu;break;
  case 0xf0311eu: /* movei   $f10020,r24 */
   s.registers[0][24]=0xf10020u;
   s.pc=0xf03124u;break;
  case 0xf03124u: /* moveq   1,r28 */
   s.registers[0][28]=1u;
   s.pc=0xf03126u;break;
  case 0xf03126u: /* bset    $8,r28 */
   s.registers[0][28]|=(1u<<8);
   zn(&s,s.registers[0][28]);
   s.pc=0xf03128u;break;
  case 0xf03128u: /* storew  r28,(r24) */
   CHECK(wr16(bus,&s,s.registers[0][24],s.registers[0][28]));
   s.pc=0xf0312au;break;
  case 0xf0312au: /* load    (r31),r22 */
   CHECK(rd32(bus,&s,s.registers[0][31]&~3u,&v));s.registers[0][22]=v;
   s.pc=0xf0312cu;break;
  case 0xf0312cu: /* addq    $4,r31 */
   s.registers[0][31]=add(&s,s.registers[0][31],4u);
   s.pc=0xf0312eu;break;
  case 0xf0312eu: /* load    (r31),r23 */
   CHECK(rd32(bus,&s,s.registers[0][31]&~3u,&v));s.registers[0][23]=v;
   s.pc=0xf03130u;break;
  case 0xf03130u: /* addq    $4,r31 */
   s.registers[0][31]=add(&s,s.registers[0][31],4u);
   s.pc=0xf03132u;break;
  case 0xf03132u: /* load    (r31),r26 */
   CHECK(rd32(bus,&s,s.registers[0][31]&~3u,&v));s.registers[0][26]=v;
   s.pc=0xf03134u;break;
  case 0xf03134u: /* addq    $4,r31 */
   s.registers[0][31]=add(&s,s.registers[0][31],4u);
   s.pc=0xf03136u;break;
  case 0xf03136u: /* load    (r31),r27 */
   CHECK(rd32(bus,&s,s.registers[0][31]&~3u,&v));s.registers[0][27]=v;
   s.pc=0xf03138u;break;
  case 0xf03138u: /* addq    $4,r31 */
   s.registers[0][31]=add(&s,s.registers[0][31],4u);
   s.pc=0xf0313au;break;
  case 0xf0313au: /* load    (r31),r24 */
   CHECK(rd32(bus,&s,s.registers[0][31]&~3u,&v));s.registers[0][24]=v;
   s.pc=0xf0313cu;break;
  case 0xf0313cu: /* addq    $4,r31 */
   s.registers[0][31]=add(&s,s.registers[0][31],4u);
   s.pc=0xf0313eu;break;
  case 0xf0313eu: /* load    (r31),r25 */
   CHECK(rd32(bus,&s,s.registers[0][31]&~3u,&v));s.registers[0][25]=v;
   s.pc=0xf03140u;break;
  case 0xf03140u: /* addq    $4,r31 */
   s.registers[0][31]=add(&s,s.registers[0][31],4u);
   s.pc=0xf03142u;break;
  case 0xf03142u: /* movei   $f02100,r30 */
   s.registers[0][30]=0xf02100u;
   s.pc=0xf03148u;break;
  case 0xf03148u: /* bclr    $3,r29 */
   s.registers[0][29]&=~(1u<<3);
   zn(&s,s.registers[0][29]);
   s.pc=0xf0314au;break;
  case 0xf0314au: /* bset    $a,r29 */
   s.registers[0][29]|=(1u<<10);
   zn(&s,s.registers[0][29]);
   s.pc=0xf0314cu;break;
  case 0xf0314cu: /* load    (r31),r28 */
   CHECK(rd32(bus,&s,s.registers[0][31]&~3u,&v));s.registers[0][28]=v;
   s.pc=0xf0314eu;break;
  case 0xf0314eu: /* addq    $2,r28 */
   s.registers[0][28]=add(&s,s.registers[0][28],2u);
   s.pc=0xf03150u;break;
  case 0xf03150u: /* addq    $4,r31 */
   s.registers[0][31]=add(&s,s.registers[0][31],4u);
   s.pc=0xf03152u;break;
  case 0xf03152u: /* jump    (r28) */
   if(condition(&s,0)){pending=1;target=s.registers[0][28];}
   s.pc=0xf03154u;break;
  case 0xf03154u: /* store   r29,(r30) */
   CHECK(wr32(bus,&s,local(s.registers[0][30])?(s.registers[0][30]&~3u):s.registers[0][30],s.registers[0][29]));
   s.pc=0xf03156u;break;
  case 0xf03156u: /* movei   $dfff24,r27 */
   s.registers[0][27]=0xdfff24u;
   s.pc=0xf0315cu;break;
  case 0xf0315cu: /* moveq   3,r30 */
   s.registers[0][30]=3u;
   s.pc=0xf0315eu;break;
  case 0xf0315eu: /* moveq   9,r22 */
   s.registers[0][22]=9u;
   s.pc=0xf03160u;break;
  case 0xf03160u: /* shlq    $2,r30 */
   s.c=s.registers[0][30]>>31;s.registers[0][30]=s.registers[0][30]<<2;zn(&s,s.registers[0][30]);
   s.pc=0xf03162u;break;
  case 0xf03162u: /* addq    $4,r23 */
   s.registers[0][23]=add(&s,s.registers[0][23],4u);
   s.pc=0xf03164u;break;
  case 0xf03164u: /* load    (r23),r24 */
   CHECK(rd32(bus,&s,s.registers[0][23]&~3u,&v));s.registers[0][24]=v;
   s.pc=0xf03166u;break;
  case 0xf03166u: /* subq    $4,r23 */
   s.registers[0][23]=sub(&s,s.registers[0][23],4u);
   s.pc=0xf03168u;break;
  case 0xf03168u: /* jr      00F03170 */
   if(condition(&s,0)){pending=1;target=0xf03170u;}
   s.pc=0xf0316au;break;
  case 0xf0316au: /* nop */
   s.pc=0xf0316cu;break;
  case 0xf0316cu: /* moveq   16,r26 */
   s.registers[0][26]=16u;
   s.pc=0xf0316eu;break;
  case 0xf0316eu: /* store   r26,(r23) */
   CHECK(wr32(bus,&s,local(s.registers[0][23])?(s.registers[0][23]&~3u):s.registers[0][23],s.registers[0][26]));
   s.pc=0xf03170u;break;
  case 0xf03170u: /* subq    $1,r22 */
   s.registers[0][22]=sub(&s,s.registers[0][22],1u);
   s.pc=0xf03172u;break;
  case 0xf03172u: /* jump    z,(r25) */
   if(condition(&s,2)){pending=1;target=s.registers[0][25];}
   s.pc=0xf03174u;break;
  case 0xf03174u: /* nop */
   s.pc=0xf03176u;break;
  case 0xf03176u: /* xor     r30,r27 */ s.registers[0][27]^=s.registers[0][30];zn(&s,s.registers[0][27]);s.pc=0xf03178u;break;
  case 0xf03178u: /* load    (r27),r28 */
   CHECK(rd32(bus,&s,s.registers[0][27]&~3u,&v));s.registers[0][28]=v;
   s.pc=0xf0317au;break;
  case 0xf0317au: /* cmp     r28,r24 */
   (void)sub(&s,s.registers[0][24],s.registers[0][28]);
   s.pc=0xf0317cu;break;
  case 0xf0317cu: /* jr      nz,00F0316C */
   if(condition(&s,1)){pending=1;target=0xf0316cu;}
   s.pc=0xf0317eu;break;
  case 0xf0317eu: /* nop */
   s.pc=0xf03180u;break;
  case 0xf03180u: /* subq    $1,r26 */
   s.registers[0][26]=sub(&s,s.registers[0][26],1u);
   s.pc=0xf03182u;break;
  case 0xf03182u: /* jr      nz,00F03170 */
   if(condition(&s,1)){pending=1;target=0xf03170u;}
   s.pc=0xf03184u;break;
  case 0xf03184u: /* store   r26,(r23) */
   CHECK(wr32(bus,&s,local(s.registers[0][23])?(s.registers[0][23]&~3u):s.registers[0][23],s.registers[0][26]));
   s.pc=0xf03186u;break;
  case 0xf03186u: /* subq    $c,r23 */
   s.registers[0][23]=sub(&s,s.registers[0][23],12u);
   s.pc=0xf03188u;break;
  case 0xf03188u: /* load    (r23),r26 */
   CHECK(rd32(bus,&s,s.registers[0][23]&~3u,&v));s.registers[0][26]=v;
   s.pc=0xf0318au;break;
  case 0xf0318au: /* xor     r30,r27 */ s.registers[0][27]^=s.registers[0][30];zn(&s,s.registers[0][27]);s.pc=0xf0318cu;break;
  case 0xf0318cu: /* addqt   $4,r26 */
   s.registers[0][26]+=4u;
   s.pc=0xf0318eu;break;
  case 0xf0318eu: /* load    (r27),r28 */
   CHECK(rd32(bus,&s,s.registers[0][27]&~3u,&v));s.registers[0][28]=v;
   s.pc=0xf03190u;break;
  case 0xf03190u: /* store   r28,(r26) */
   CHECK(wr32(bus,&s,local(s.registers[0][26])?(s.registers[0][26]&~3u):s.registers[0][26],s.registers[0][28]));
   s.pc=0xf03192u;break;
  case 0xf03192u: /* subq    $1,r22 */
   s.registers[0][22]=sub(&s,s.registers[0][22],1u);
   s.pc=0xf03194u;break;
  case 0xf03194u: /* jr      nz,00F0318A */
   if(condition(&s,1)){pending=1;target=0xf0318au;}
   s.pc=0xf03196u;break;
  case 0xf03196u: /* nop */
   s.pc=0xf03198u;break;
  case 0xf03198u: /* store   r26,(r23) */
   CHECK(wr32(bus,&s,local(s.registers[0][23])?(s.registers[0][23]&~3u):s.registers[0][23],s.registers[0][26]));
   s.pc=0xf0319au;break;
  case 0xf0319au: /* jump    (r25) */
   if(condition(&s,0)){pending=1;target=s.registers[0][25];}
   s.pc=0xf0319cu;break;
  case 0xf0319cu: /* nop */
   s.pc=0xf0319eu;break;default:return BIWN_GPU_CD_MARKER_ISR_BAD_PC;
}if(delayed){if(pending)return BIWN_GPU_CD_MARKER_ISR_BAD_DELAY;s.pc=resume;}if(!pending&&s.pc==returnPC){*state=s;return 0;}}return BIWN_GPU_CD_MARKER_ISR_WORK_LIMIT;}
enum biwn_gpu_cd_marker_ISR_status biwn_gpu_cd_marker_ISR_assert(struct biwn_gpu_cd_marker_ISR_bus *bus,struct biwn_gpu_cd_marker_ISR_state *state){struct biwn_gpu_cd_marker_ISR_state s;uint32_t a;if(!bus||!state||!bus->write32||state->active_bank>1||state->z>1||state->c>1||state->n>1)return 1;s=*state;if(!(s.control&1u))return 6;s.control|=0x80u;if((s.control&8u)||(s.flags&8u)||!(s.flags&0x20u)){*state=s;return 7;}s.flags|=8u;s.active_bank=0;s.registers[0][31]-=4u;a=s.registers[0][31]&~3u;CHECK(wr32(bus,&s,a,s.pc-2u));s.pc=s.registers[0][30]=0xf03010u;*state=s;return 0;}
