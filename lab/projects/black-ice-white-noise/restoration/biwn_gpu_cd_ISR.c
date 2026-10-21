/* Generated from the pinned GPU4D80 overlay by
 * scripts/generate_biwn_gpu_cd_ISR.py. Analyst static recompilation,
 * not recovered original source. Integer primitive behavior is checked
 * against the pinned Virtual Jaguar core; no core runs on the C side. */
#include "biwn_gpu_cd_ISR.h"
#include <string.h>
static void zn(struct biwn_gpu_cd_ISR_state *s,uint32_t v){s->z=v==0;s->n=v>>31;}
static uint32_t add(struct biwn_gpu_cd_ISR_state *s,uint32_t a,uint32_t b){uint32_t v=a+b;s->c=b>~a;zn(s,v);return v;}
static uint32_t sub(struct biwn_gpu_cd_ISR_state *s,uint32_t a,uint32_t b){uint32_t v=a-b;s->c=b>a;zn(s,v);return v;}
static int condition(struct biwn_gpu_cd_ISR_state *s,unsigned code){unsigned flags=s->z|(s->c<<1)|(s->n<<2);return !((code&1u)&&(flags&1u))&&!((code&2u)&&!(flags&1u))&&!((code&4u)&&(flags&(2u<<(code>>4))))&&!((code&8u)&&!(flags&(2u<<(code>>4))));}
static uint32_t be32(const uint8_t *p){return((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
static void put32(uint8_t *p,uint32_t v){p[0]=(uint8_t)(v>>24);p[1]=(uint8_t)(v>>16);p[2]=(uint8_t)(v>>8);p[3]=(uint8_t)v;}
static int local(uint32_t a){return a>=0xf03000u&&a<=0xf03ffcu;}
static int rd32(struct biwn_gpu_cd_ISR_bus *bus,struct biwn_gpu_cd_ISR_state *s,uint32_t a,uint32_t *v){if(local(a)){*v=be32(s->local_RAM+a-0xf03000u);return 0;}if(a==0xf02100u){s->flags=(s->flags&~7u)|(s->n<<2)|(s->c<<1)|s->z;*v=s->flags&0xffffc1ffu;return 0;}if(a==0xf02104u){*v=s->matrix_control;return 0;}if(a==0xf02108u){*v=s->matrix_pointer;return 0;}return bus->read32(bus->context,a,v)?2:0;}
static int rd16(struct biwn_gpu_cd_ISR_bus *bus,struct biwn_gpu_cd_ISR_state *s,uint32_t a,uint32_t *v){uint16_t h;if(a>=0xf03000u&&a<=0xf03ffeu){unsigned p=a-0xf03000u;*v=((uint32_t)s->local_RAM[p]<<8)|s->local_RAM[p+1];return 0;}if(bus->read16(bus->context,a,&h))return 2;*v=h;return 0;}
static int loadw(struct biwn_gpu_cd_ISR_bus *bus,struct biwn_gpu_cd_ISR_state *s,uint32_t a,uint32_t *v){if(a>=0xf03000u&&a<=0xf03fffu)return rd32(bus,s,a&~3u,v);return rd16(bus,s,a,v);}
static int wr32(struct biwn_gpu_cd_ISR_bus *bus,struct biwn_gpu_cd_ISR_state *s,uint32_t a,uint32_t v){if(local(a)){put32(s->local_RAM+a-0xf03000u,v);return 0;}if(a==0xf02100u){s->flags=(v&~8u)|((v&8u)?(s->flags&8u):0);s->z=s->flags&1u;s->c=(s->flags>>1)&1u;s->n=(s->flags>>2)&1u;s->control&=~((s->flags&0x3e00u)>>3);s->active_bank=(!(s->flags&8u)&&(s->flags&0x4000u))?1u:0u;return bus->write32(bus->context,a,v)?2:0;}if(a==0xf02104u){s->matrix_control=v;return 0;}if(a==0xf02108u){s->matrix_pointer=v&~3u;return 0;}return bus->write32(bus->context,a,v)?2:0;}
static int wr16(struct biwn_gpu_cd_ISR_bus *bus,struct biwn_gpu_cd_ISR_state *s,uint32_t a,uint32_t v){if(a>=0xf03000u&&a<=0xf03fffu)return wr32(bus,s,a&~1u,v&0xffffu);return bus->write16(bus->context,a,(uint16_t)v)?2:0;}
#define CHECK(e) do{int status=(e);if(status)return(enum biwn_gpu_cd_ISR_status)status;}while(0)
enum biwn_gpu_cd_ISR_status biwn_gpu_cd_ISR_run(struct biwn_gpu_cd_ISR_bus *bus,struct biwn_gpu_cd_ISR_state *state,uint32_t budget,uint32_t returnPC){struct biwn_gpu_cd_ISR_state s;uint32_t v,target=0;unsigned pending=0;if(!bus||!state||!budget||!bus->read16||!bus->read32||!bus->write16||!bus->write32||state->active_bank||state->z>1||state->c>1||state->n>1)return 1;s=*state;while(budget--){unsigned delayed=pending;uint32_t resume=target;pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){
  case 0xf03010u: /* movei   $f0305c,r30 */
   s.registers[0][30]=0xf0305cu;
   s.pc=0xf03016u;break;
  case 0xf03016u: /* jump    (r30) */
   if(condition(&s,0)){pending=1;target=s.registers[0][30];}
   s.pc=0xf03018u;break;
  case 0xf03018u: /* nop */
   s.pc=0xf0301au;break;
  case 0xf0305cu: /* movei   $f02100,r30 */
   s.registers[0][30]=0xf02100u;
   s.pc=0xf03062u;break;
  case 0xf03062u: /* load    (r30),r29 */
   CHECK(rd32(bus,&s,s.registers[0][30]&~3u,&v));s.registers[0][29]=v;
   s.pc=0xf03064u;break;
  case 0xf03064u: /* subq    $4,r31 */
   s.registers[0][31]=sub(&s,s.registers[0][31],4u);
   s.pc=0xf03066u;break;
  case 0xf03066u: /* store   r25,(r31) */
   CHECK(wr32(bus,&s,local(s.registers[0][31])?(s.registers[0][31]&~3u):s.registers[0][31],s.registers[0][25]));
   s.pc=0xf03068u;break;
  case 0xf03068u: /* subq    $4,r31 */
   s.registers[0][31]=sub(&s,s.registers[0][31],4u);
   s.pc=0xf0306au;break;
  case 0xf0306au: /* store   r24,(r31) */
   CHECK(wr32(bus,&s,local(s.registers[0][31])?(s.registers[0][31]&~3u):s.registers[0][31],s.registers[0][24]));
   s.pc=0xf0306cu;break;
  case 0xf0306cu: /* movei   $dfff00,r24 */
   s.registers[0][24]=0xdfff00u;
   s.pc=0xf03072u;break;
  case 0xf03072u: /* subq    $4,r31 */
   s.registers[0][31]=sub(&s,s.registers[0][31],4u);
   s.pc=0xf03074u;break;
  case 0xf03074u: /* store   r27,(r31) */
   CHECK(wr32(bus,&s,local(s.registers[0][31])?(s.registers[0][31]&~3u):s.registers[0][31],s.registers[0][27]));
   s.pc=0xf03076u;break;
  case 0xf03076u: /* subq    $4,r31 */
   s.registers[0][31]=sub(&s,s.registers[0][31],4u);
   s.pc=0xf03078u;break;
  case 0xf03078u: /* store   r26,(r31) */
   CHECK(wr32(bus,&s,local(s.registers[0][31])?(s.registers[0][31]&~3u):s.registers[0][31],s.registers[0][26]));
   s.pc=0xf0307au;break;
  case 0xf0307au: /* subq    $4,r31 */
   s.registers[0][31]=sub(&s,s.registers[0][31],4u);
   s.pc=0xf0307cu;break;
  case 0xf0307cu: /* store   r23,(r31) */
   CHECK(wr32(bus,&s,local(s.registers[0][31])?(s.registers[0][31]&~3u):s.registers[0][31],s.registers[0][23]));
   s.pc=0xf0307eu;break;
  case 0xf0307eu: /* move    pc,r23 */
   s.registers[0][23]=0xf0307eu;
   s.pc=0xf03080u;break;
  case 0xf03080u: /* movei   $2e,r28 */
   s.registers[0][28]=0x2eu;
   s.pc=0xf03086u;break;
  case 0xf03086u: /* sub     r28,r23 */
   s.registers[0][23]=sub(&s,s.registers[0][23],s.registers[0][28]);
   s.pc=0xf03088u;break;
  case 0xf03088u: /* move    pc,r25 */
   s.registers[0][25]=0xf03088u;
   s.pc=0xf0308au;break;
  case 0xf0308au: /* movei   $72,r27 */
   s.registers[0][27]=0x72u;
   s.pc=0xf03090u;break;
  case 0xf03090u: /* add     r27,r25 */
   s.registers[0][25]=add(&s,s.registers[0][25],s.registers[0][27]);
   s.pc=0xf03092u;break;
  case 0xf03092u: /* load    (r24),r27 */
   CHECK(rd32(bus,&s,s.registers[0][24]&~3u,&v));s.registers[0][27]=v;
   s.pc=0xf03094u;break;
  case 0xf03094u: /* btst    $d,r27 */
   s.z=((~s.registers[0][27])>>13)&1u;
   s.pc=0xf03096u;break;
  case 0xf03096u: /* jr      z,00F030B6 */
   if(condition(&s,2)){pending=1;target=0xf030b6u;}
   s.pc=0xf03098u;break;
  case 0xf03098u: /* bclr    $5,r27 */
   s.registers[0][27]&=~(1u<<5);
   zn(&s,s.registers[0][27]);
   s.pc=0xf0309au;break;
  case 0xf0309au: /* bset    $1,r27 */
   s.registers[0][27]|=(1u<<1);
   zn(&s,s.registers[0][27]);
   s.pc=0xf0309cu;break;
  case 0xf0309cu: /* store   r27,(r24) */
   CHECK(wr32(bus,&s,local(s.registers[0][24])?(s.registers[0][24]&~3u):s.registers[0][24],s.registers[0][27]));
   s.pc=0xf0309eu;break;
  case 0xf0309eu: /* addq    $10,r24 */
   s.registers[0][24]=add(&s,s.registers[0][24],16u);
   s.pc=0xf030a0u;break;
  case 0xf030a0u: /* load    (r24),r27 */
   CHECK(rd32(bus,&s,s.registers[0][24]&~3u,&v));s.registers[0][27]=v;
   s.pc=0xf030a2u;break;
  case 0xf030a2u: /* bset    $2,r27 */
   s.registers[0][27]|=(1u<<2);
   zn(&s,s.registers[0][27]);
   s.pc=0xf030a4u;break;
  case 0xf030a4u: /* store   r27,(r24) */
   CHECK(wr32(bus,&s,local(s.registers[0][24])?(s.registers[0][24]&~3u):s.registers[0][24],s.registers[0][27]));
   s.pc=0xf030a6u;break;
  case 0xf030a6u: /* subq    $c,r24 */
   s.registers[0][24]=sub(&s,s.registers[0][24],12u);
   s.pc=0xf030a8u;break;
  case 0xf030a8u: /* load    (r24),r26 */
   CHECK(rd32(bus,&s,s.registers[0][24]&~3u,&v));s.registers[0][26]=v;
   s.pc=0xf030aau;break;
  case 0xf030aau: /* addq    $6,r24 */
   s.registers[0][24]=add(&s,s.registers[0][24],6u);
   s.pc=0xf030acu;break;
  case 0xf030acu: /* loadw   (r24),r27 */
   CHECK(loadw(bus,&s,s.registers[0][24],&v));s.registers[0][27]=v;
   s.pc=0xf030aeu;break;
  case 0xf030aeu: /* btst    $a,r27 */
   s.z=((~s.registers[0][27])>>10)&1u;
   s.pc=0xf030b0u;break;
  case 0xf030b0u: /* jr      nz,00F030BC */
   if(condition(&s,1)){pending=1;target=0xf030bcu;}
   s.pc=0xf030b2u;break;
  case 0xf030b2u: /* or      r26,r26 */
   s.registers[0][26]|=s.registers[0][26];
   zn(&s,s.registers[0][26]);
   s.pc=0xf030b4u;break;
  case 0xf030b4u: /* jump    (r25) */
   if(condition(&s,0)){pending=1;target=s.registers[0][25];}
   s.pc=0xf030b6u;break;
  case 0xf030b6u: /* btst    $e,r27 */
   s.z=((~s.registers[0][27])>>14)&1u;
   s.pc=0xf030b8u;break;
  case 0xf030b8u: /* jr      z,00F030CC */
   if(condition(&s,2)){pending=1;target=0xf030ccu;}
   s.pc=0xf030bau;break;
  case 0xf030bau: /* bset    $1f,r27 */
   s.registers[0][27]|=(1u<<31);
   zn(&s,s.registers[0][27]);
   s.pc=0xf030bcu;break;
  case 0xf030bcu: /* addq    $10,r24 */
   s.registers[0][24]=add(&s,s.registers[0][24],16u);
   s.pc=0xf030beu;break;
  case 0xf030beu: /* load    (r24),r28 */
   CHECK(rd32(bus,&s,s.registers[0][24]&~3u,&v));s.registers[0][28]=v;
   s.pc=0xf030c0u;break;
  case 0xf030c0u: /* or      r28,r28 */
   s.registers[0][28]|=s.registers[0][28];
   zn(&s,s.registers[0][28]);
   s.pc=0xf030c2u;break;
  case 0xf030c2u: /* subq    $10,r24 */
   s.registers[0][24]=sub(&s,s.registers[0][24],16u);
   s.pc=0xf030c4u;break;
  case 0xf030c4u: /* load    (r23),r28 */
   CHECK(rd32(bus,&s,s.registers[0][23]&~3u,&v));s.registers[0][28]=v;
   s.pc=0xf030c6u;break;
  case 0xf030c6u: /* addq    $8,r23 */
   s.registers[0][23]=add(&s,s.registers[0][23],8u);
   s.pc=0xf030c8u;break;
  case 0xf030c8u: /* store   r28,(r23) */
   CHECK(wr32(bus,&s,local(s.registers[0][23])?(s.registers[0][23]&~3u):s.registers[0][23],s.registers[0][28]));
   s.pc=0xf030cau;break;
  case 0xf030cau: /* subq    $8,r23 */
   s.registers[0][23]=sub(&s,s.registers[0][23],8u);
   s.pc=0xf030ccu;break;
  case 0xf030ccu: /* load    (r23),r26 */
   CHECK(rd32(bus,&s,s.registers[0][23]&~3u,&v));s.registers[0][26]=v;
   s.pc=0xf030ceu;break;
  case 0xf030ceu: /* addq    $4,r23 */
   s.registers[0][23]=add(&s,s.registers[0][23],4u);
   s.pc=0xf030d0u;break;
  case 0xf030d0u: /* load    (r23),r28 */
   CHECK(rd32(bus,&s,s.registers[0][23]&~3u,&v));s.registers[0][28]=v;
   s.pc=0xf030d2u;break;
  case 0xf030d2u: /* subq    $4,r23 */
   s.registers[0][23]=sub(&s,s.registers[0][23],4u);
   s.pc=0xf030d4u;break;
  case 0xf030d4u: /* cmp     r26,r28 */
   (void)sub(&s,s.registers[0][28],s.registers[0][26]);
   s.pc=0xf030d6u;break;
  case 0xf030d6u: /* jr      nn,00F030DC */
   if(condition(&s,20)){pending=1;target=0xf030dcu;}
   s.pc=0xf030d8u;break;
  case 0xf030d8u: /* bclr    $0,r27 */
   s.registers[0][27]&=~(1u<<0);
   zn(&s,s.registers[0][27]);
   s.pc=0xf030dau;break;
  case 0xf030dau: /* store   r27,(r24) */
   CHECK(wr32(bus,&s,local(s.registers[0][24])?(s.registers[0][24]&~3u):s.registers[0][24],s.registers[0][27]));
   s.pc=0xf030dcu;break;
  case 0xf030dcu: /* movei   $dfff24,r27 */
   s.registers[0][27]=0xdfff24u;
   s.pc=0xf030e2u;break;
  case 0xf030e2u: /* move    r27,r25 */
   s.registers[0][25]=s.registers[0][27];
   s.pc=0xf030e4u;break;
  case 0xf030e4u: /* addq    $4,r27 */
   s.registers[0][27]=add(&s,s.registers[0][27],4u);
   s.pc=0xf030e6u;break;
  case 0xf030e6u: /* moveq   3,r24 */
   s.registers[0][24]=3u;
   s.pc=0xf030e8u;break;
  case 0xf030e8u: /* load    (r27),r28 */
   CHECK(rd32(bus,&s,s.registers[0][27]&~3u,&v));s.registers[0][28]=v;
   s.pc=0xf030eau;break;
  case 0xf030eau: /* load    (r25),r30 */
   CHECK(rd32(bus,&s,s.registers[0][25]&~3u,&v));s.registers[0][30]=v;
   s.pc=0xf030ecu;break;
  case 0xf030ecu: /* addq    $4,r26 */
   s.registers[0][26]=add(&s,s.registers[0][26],4u);
   s.pc=0xf030eeu;break;
  case 0xf030eeu: /* subq    $1,r24 */
   s.registers[0][24]=sub(&s,s.registers[0][24],1u);
   s.pc=0xf030f0u;break;
  case 0xf030f0u: /* store   r28,(r26) */
   CHECK(wr32(bus,&s,local(s.registers[0][26])?(s.registers[0][26]&~3u):s.registers[0][26],s.registers[0][28]));
   s.pc=0xf030f2u;break;
  case 0xf030f2u: /* addqt   $4,r26 */
   s.registers[0][26]+=4u;
   s.pc=0xf030f4u;break;
  case 0xf030f4u: /* jr      nn,00F030E8 */
   if(condition(&s,20)){pending=1;target=0xf030e8u;}
   s.pc=0xf030f6u;break;
  case 0xf030f6u: /* store   r30,(r26) */
   CHECK(wr32(bus,&s,local(s.registers[0][26])?(s.registers[0][26]&~3u):s.registers[0][26],s.registers[0][30]));
   s.pc=0xf030f8u;break;
  case 0xf030f8u: /* store   r26,(r23) */
   CHECK(wr32(bus,&s,local(s.registers[0][23])?(s.registers[0][23]&~3u):s.registers[0][23],s.registers[0][26]));
   s.pc=0xf030fau;break;
  case 0xf030fau: /* movei   $f10020,r24 */
   s.registers[0][24]=0xf10020u;
   s.pc=0xf03100u;break;
  case 0xf03100u: /* moveq   1,r28 */
   s.registers[0][28]=1u;
   s.pc=0xf03102u;break;
  case 0xf03102u: /* bset    $8,r28 */
   s.registers[0][28]|=(1u<<8);
   zn(&s,s.registers[0][28]);
   s.pc=0xf03104u;break;
  case 0xf03104u: /* storew  r28,(r24) */
   CHECK(wr16(bus,&s,s.registers[0][24],s.registers[0][28]));
   s.pc=0xf03106u;break;
  case 0xf03106u: /* load    (r31),r23 */
   CHECK(rd32(bus,&s,s.registers[0][31]&~3u,&v));s.registers[0][23]=v;
   s.pc=0xf03108u;break;
  case 0xf03108u: /* addq    $4,r31 */
   s.registers[0][31]=add(&s,s.registers[0][31],4u);
   s.pc=0xf0310au;break;
  case 0xf0310au: /* load    (r31),r26 */
   CHECK(rd32(bus,&s,s.registers[0][31]&~3u,&v));s.registers[0][26]=v;
   s.pc=0xf0310cu;break;
  case 0xf0310cu: /* addq    $4,r31 */
   s.registers[0][31]=add(&s,s.registers[0][31],4u);
   s.pc=0xf0310eu;break;
  case 0xf0310eu: /* load    (r31),r27 */
   CHECK(rd32(bus,&s,s.registers[0][31]&~3u,&v));s.registers[0][27]=v;
   s.pc=0xf03110u;break;
  case 0xf03110u: /* addq    $4,r31 */
   s.registers[0][31]=add(&s,s.registers[0][31],4u);
   s.pc=0xf03112u;break;
  case 0xf03112u: /* load    (r31),r24 */
   CHECK(rd32(bus,&s,s.registers[0][31]&~3u,&v));s.registers[0][24]=v;
   s.pc=0xf03114u;break;
  case 0xf03114u: /* addq    $4,r31 */
   s.registers[0][31]=add(&s,s.registers[0][31],4u);
   s.pc=0xf03116u;break;
  case 0xf03116u: /* load    (r31),r25 */
   CHECK(rd32(bus,&s,s.registers[0][31]&~3u,&v));s.registers[0][25]=v;
   s.pc=0xf03118u;break;
  case 0xf03118u: /* addq    $4,r31 */
   s.registers[0][31]=add(&s,s.registers[0][31],4u);
   s.pc=0xf0311au;break;
  case 0xf0311au: /* movei   $f02100,r30 */
   s.registers[0][30]=0xf02100u;
   s.pc=0xf03120u;break;
  case 0xf03120u: /* bclr    $3,r29 */
   s.registers[0][29]&=~(1u<<3);
   zn(&s,s.registers[0][29]);
   s.pc=0xf03122u;break;
  case 0xf03122u: /* bset    $a,r29 */
   s.registers[0][29]|=(1u<<10);
   zn(&s,s.registers[0][29]);
   s.pc=0xf03124u;break;
  case 0xf03124u: /* load    (r31),r28 */
   CHECK(rd32(bus,&s,s.registers[0][31]&~3u,&v));s.registers[0][28]=v;
   s.pc=0xf03126u;break;
  case 0xf03126u: /* addq    $2,r28 */
   s.registers[0][28]=add(&s,s.registers[0][28],2u);
   s.pc=0xf03128u;break;
  case 0xf03128u: /* addq    $4,r31 */
   s.registers[0][31]=add(&s,s.registers[0][31],4u);
   s.pc=0xf0312au;break;
  case 0xf0312au: /* jump    (r28) */
   if(condition(&s,0)){pending=1;target=s.registers[0][28];}
   s.pc=0xf0312cu;break;
  case 0xf0312cu: /* store   r29,(r30) */
   CHECK(wr32(bus,&s,local(s.registers[0][30])?(s.registers[0][30]&~3u):s.registers[0][30],s.registers[0][29]));
   s.pc=0xf0312eu;break;default:return BIWN_GPU_CD_ISR_BAD_PC;
}if(delayed){if(pending)return BIWN_GPU_CD_ISR_BAD_DELAY;s.pc=resume;}if(!pending&&s.pc==returnPC){*state=s;return 0;}}return BIWN_GPU_CD_ISR_WORK_LIMIT;}
enum biwn_gpu_cd_ISR_status biwn_gpu_cd_ISR_assert(struct biwn_gpu_cd_ISR_bus *bus,struct biwn_gpu_cd_ISR_state *state){struct biwn_gpu_cd_ISR_state s;uint32_t a;if(!bus||!state||!bus->write32||state->active_bank>1||state->z>1||state->c>1||state->n>1)return 1;s=*state;if(!(s.control&1u))return 6;s.control|=0x80u;if((s.control&8u)||(s.flags&8u)||!(s.flags&0x20u)){*state=s;return 7;}s.flags|=8u;s.active_bank=0;s.registers[0][31]-=4u;a=s.registers[0][31]&~3u;CHECK(wr32(bus,&s,a,s.pc-2u));s.pc=s.registers[0][30]=0xf03010u;*state=s;return 0;}
