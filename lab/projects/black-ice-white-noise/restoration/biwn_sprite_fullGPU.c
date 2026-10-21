/* Generated from the pinned GPU4D80 overlay by
 * scripts/generate_biwn_sprite_fullGPU.py. Analyst static recompilation,
 * not recovered original source. Integer primitive behavior is checked
 * against the pinned Virtual Jaguar core; no core runs on the C side. */
#include "biwn_sprite_fullGPU.h"
#include <string.h>
static uint32_t sar(uint32_t v,unsigned n){return n>=32?((v&0x80000000u)?0xffffffffu:0):(v>>n)|((v&0x80000000u)?(0xffffffffu<<(32-n)):0);}
static void zn(struct biwn_sprite_fullGPU_state *s,uint32_t v){s->z=v==0;s->n=v>>31;}
static uint32_t add(struct biwn_sprite_fullGPU_state *s,uint32_t a,uint32_t b){uint32_t v=a+b;s->c=b>~a;zn(s,v);return v;}
static uint32_t sub(struct biwn_sprite_fullGPU_state *s,uint32_t a,uint32_t b){uint32_t v=a-b;s->c=b>a;zn(s,v);return v;}
static int condition(struct biwn_sprite_fullGPU_state *s,unsigned code){unsigned flags=s->z|(s->c<<1)|(s->n<<2);return !((code&1u)&&(flags&1u))&&!((code&2u)&&!(flags&1u))&&!((code&4u)&&(flags&(2u<<(code>>4))))&&!((code&8u)&&!(flags&(2u<<(code>>4))));}
static uint32_t be32(const uint8_t *p){return((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
static void put32(uint8_t *p,uint32_t v){p[0]=(uint8_t)(v>>24);p[1]=(uint8_t)(v>>16);p[2]=(uint8_t)(v>>8);p[3]=(uint8_t)v;}
static int local(uint32_t a){return a>=0xf03000u&&a<=0xf03ffcu;}
static int rd32(struct biwn_sprite_fullGPU_bus *bus,struct biwn_sprite_fullGPU_state *s,uint32_t a,uint32_t *v){if(local(a)){*v=be32(s->local_RAM+a-0xf03000u);return 0;}if(a==0xf02104u){*v=s->matrix_control;return 0;}if(a==0xf02108u){*v=s->matrix_pointer;return 0;}return bus->read32(bus->context,a,v)?2:0;}
static int rd16(struct biwn_sprite_fullGPU_bus *bus,struct biwn_sprite_fullGPU_state *s,uint32_t a,uint32_t *v){uint16_t h;if(a>=0xf03000u&&a<=0xf03ffeu){unsigned p=a-0xf03000u;*v=((uint32_t)s->local_RAM[p]<<8)|s->local_RAM[p+1];return 0;}if(bus->read16(bus->context,a,&h))return 2;*v=h;return 0;}
static int loadw(struct biwn_sprite_fullGPU_bus *bus,struct biwn_sprite_fullGPU_state *s,uint32_t a,uint32_t *v){if(a>=0xf03000u&&a<=0xf03fffu)return rd32(bus,s,a&~3u,v);return rd16(bus,s,a,v);}
static int wr32(struct biwn_sprite_fullGPU_bus *bus,struct biwn_sprite_fullGPU_state *s,uint32_t a,uint32_t v){if(local(a)){put32(s->local_RAM+a-0xf03000u,v);return 0;}if(a==0xf0211cu){s->division_control=v;return bus->write32(bus->context,a,v)?2:0;}if(a==0xf02104u){s->matrix_control=v;return 0;}if(a==0xf02108u){s->matrix_pointer=v&~3u;return 0;}return bus->write32(bus->context,a,v)?2:0;}
static int wr16(struct biwn_sprite_fullGPU_bus *bus,struct biwn_sprite_fullGPU_state *s,uint32_t a,uint32_t v){if(a>=0xf03000u&&a<=0xf03fffu)return wr32(bus,s,a&~1u,v&0xffffu);return bus->write16(bus->context,a,(uint16_t)v)?2:0;}
static int rd8(struct biwn_sprite_fullGPU_bus *b,struct biwn_sprite_fullGPU_state *s,uint32_t a,uint32_t *v){uint8_t x;if(a>=0xf03000u&&a<=0xf03fffu)return rd32(b,s,a&~3u,v);if(b->read8(b->context,a,&x))return 2;*v=x;return 0;}
#define CHECK(e) do{int status=(e);if(status)return(enum biwn_sprite_fullGPU_status)status;}while(0)
enum biwn_sprite_fullGPU_status biwn_sprite_fullGPU_run(struct biwn_sprite_fullGPU_bus *bus,struct biwn_sprite_fullGPU_state *state,uint32_t budget){struct biwn_sprite_fullGPU_state s;uint32_t v,target=0;unsigned pending=0;if(!bus||!state||!budget||!bus->read8||!bus->read16||!bus->read32||!bus->write16||!bus->write32||state->active_bank||state->z>1||state->c>1||state->n>1)return 1;s=*state;while(budget--){unsigned delayed=pending;uint32_t resume=target;pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){
  case 0xf03240u: /* movei   $f0320c,r0 */
   s.registers[0][0]=0xf0320cu;
   s.pc=0xf03246u;break;
case 0xf03246u: /* load    (r0),r1 */
 CHECK(rd32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],&v));s.registers[0][1]=v;
 s.pc=0xf03248u;break;
  case 0xf03248u: /* addq    $4,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],4u);
   s.pc=0xf0324au;break;
case 0xf0324au: /* load    (r0),r2 */
 CHECK(rd32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],&v));s.registers[0][2]=v;
 s.pc=0xf0324cu;break;
  case 0xf0324cu: /* addq    $4,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],4u);
   s.pc=0xf0324eu;break;
case 0xf0324eu: /* load    (r0),r3 */
 CHECK(rd32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],&v));s.registers[0][3]=v;
 s.pc=0xf03250u;break;
  case 0xf03250u: /* move    r1,r0 */
   s.registers[0][0]=s.registers[0][1];
   s.pc=0xf03252u;break;
  case 0xf03252u: /* addq    $4,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],4u);
   s.pc=0xf03254u;break;
case 0xf03254u: /* load    (r0),r4 */
 CHECK(rd32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],&v));s.registers[0][4]=v;
 s.pc=0xf03256u;break;
  case 0xf03256u: /* addq    $8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],8u);
   s.pc=0xf03258u;break;
  case 0xf03258u: /* add     r1,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],s.registers[0][1]);
   s.pc=0xf0325au;break;
  case 0xf0325au: /* shlq    $2,r2 */
   s.c=s.registers[0][2]>>31;s.registers[0][2]=s.registers[0][2]<<2;zn(&s,s.registers[0][2]);
   s.pc=0xf0325cu;break;
  case 0xf0325cu: /* add     r2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][2]);
   s.pc=0xf0325eu;break;
case 0xf0325eu: /* load    (r0),r2 */
 CHECK(rd32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],&v));s.registers[0][2]=v;
 s.pc=0xf03260u;break;
  case 0xf03260u: /* add     r2,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],s.registers[0][2]);
   s.pc=0xf03262u;break;
case 0xf03262u: /* loadb   (r1),r2 */
 CHECK(rd8(bus,&s,s.registers[0][1],&v));s.registers[0][2]=v;
 s.pc=0xf03264u;break;
  case 0xf03264u: /* addq    $1,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],1u);
   s.pc=0xf03266u;break;
case 0xf03266u: /* loadb   (r1),r5 */
 CHECK(rd8(bus,&s,s.registers[0][1],&v));s.registers[0][5]=v;
 s.pc=0xf03268u;break;
  case 0xf03268u: /* addq    $1,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],1u);
   s.pc=0xf0326au;break;
case 0xf0326au: /* loadb   (r1),r21 */
 CHECK(rd8(bus,&s,s.registers[0][1],&v));s.registers[0][21]=v;
 s.pc=0xf0326cu;break;
  case 0xf0326cu: /* move    r3,r0 */
   s.registers[0][0]=s.registers[0][3];
   s.pc=0xf0326eu;break;
  case 0xf0326eu: /* shlq    $18,r21 */
   s.c=s.registers[0][21]>>31;s.registers[0][21]=s.registers[0][21]<<24;zn(&s,s.registers[0][21]);
   s.pc=0xf03270u;break;
  case 0xf03270u: /* subq    $c,r0 */
   s.registers[0][0]=sub(&s,s.registers[0][0],12u);
   s.pc=0xf03272u;break;
  case 0xf03272u: /* sharq   $18,r21 */
   s.c=s.registers[0][21]&1u;s.registers[0][21]=sar(s.registers[0][21],24);zn(&s,s.registers[0][21]);
   s.pc=0xf03274u;break;
  case 0xf03274u: /* addq    $1,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],1u);
   s.pc=0xf03276u;break;
  case 0xf03276u: /* storew  r21,(r0) */
   CHECK(wr16(bus,&s,s.registers[0][0],s.registers[0][21]));
   s.pc=0xf03278u;break;
case 0xf03278u: /* loadb   (r1),r21 */
 CHECK(rd8(bus,&s,s.registers[0][1],&v));s.registers[0][21]=v;
 s.pc=0xf0327au;break;
  case 0xf0327au: /* shlq    $18,r21 */
   s.c=s.registers[0][21]>>31;s.registers[0][21]=s.registers[0][21]<<24;zn(&s,s.registers[0][21]);
   s.pc=0xf0327cu;break;
  case 0xf0327cu: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf0327eu;break;
  case 0xf0327eu: /* sharq   $18,r21 */
   s.c=s.registers[0][21]&1u;s.registers[0][21]=sar(s.registers[0][21],24);zn(&s,s.registers[0][21]);
   s.pc=0xf03280u;break;
  case 0xf03280u: /* addq    $1,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],1u);
   s.pc=0xf03282u;break;
  case 0xf03282u: /* storew  r21,(r0) */
   CHECK(wr16(bus,&s,s.registers[0][0],s.registers[0][21]));
   s.pc=0xf03284u;break;
  case 0xf03284u: /* mult    r5,r2 */
   s.registers[0][2]=(s.registers[0][2]&0xffffu)*(s.registers[0][5]&0xffffu);
   zn(&s,s.registers[0][2]);
   s.pc=0xf03286u;break;
  case 0xf03286u: /* subq    $1,r2 */
   s.registers[0][2]=sub(&s,s.registers[0][2],1u);
   s.pc=0xf03288u;break;
  case 0xf03288u: /* moveq   0,r5 */
   s.registers[0][5]=0u;
   s.pc=0xf0328au;break;
  case 0xf0328au: /* moveq   0,r6 */
   s.registers[0][6]=0u;
   s.pc=0xf0328cu;break;
  case 0xf0328cu: /* movei   $f00,r8 */
   s.registers[0][8]=0xf00u;
   s.pc=0xf03292u;break;
  case 0xf03292u: /* movei   $700,r19 */
   s.registers[0][19]=0x700u;
   s.pc=0xf03298u;break;
  case 0xf03298u: /* movei   $f00,r20 */
   s.registers[0][20]=0xf00u;
   s.pc=0xf0329eu;break;
  case 0xf0329eu: /* movei   $f03386,r9 */
   s.registers[0][9]=0xf03386u;
   s.pc=0xf032a4u;break;
  case 0xf032a4u: /* movei   $f03456,r13 */
   s.registers[0][13]=0xf03456u;
   s.pc=0xf032aau;break;
  case 0xf032aau: /* movei   $f032fc,r11 */
   s.registers[0][11]=0xf032fcu;
   s.pc=0xf032b0u;break;
  case 0xf032b0u: /* movei   $f033cc,r14 */
   s.registers[0][14]=0xf033ccu;
   s.pc=0xf032b6u;break;
  case 0xf032b6u: /* movei   $f032c2,r12 */
   s.registers[0][12]=0xf032c2u;
   s.pc=0xf032bcu;break;
  case 0xf032bcu: /* movei   $f0348a,r15 */
   s.registers[0][15]=0xf0348au;
   s.pc=0xf032c2u;break;
  case 0xf032c2u: /* cmpq    $0,r6 */
   (void)sub(&s,s.registers[0][6],0x0u);
   s.pc=0xf032c4u;break;
  case 0xf032c4u: /* jr      nz,00F032CE */
   if(condition(&s,1)){pending=1;target=0xf032ceu;}
   s.pc=0xf032c6u;break;
  case 0xf032c6u: /* nop */
   s.pc=0xf032c8u;break;
case 0xf032c8u: /* loadb   (r1),r7 */
 CHECK(rd8(bus,&s,s.registers[0][1],&v));s.registers[0][7]=v;
 s.pc=0xf032cau;break;
  case 0xf032cau: /* moveq   8,r6 */
   s.registers[0][6]=8u;
   s.pc=0xf032ccu;break;
  case 0xf032ccu: /* addq    $1,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],1u);
   s.pc=0xf032ceu;break;
  case 0xf032ceu: /* btst    $7,r7 */
   s.z=((~s.registers[0][7])>>7)&1u;
   s.pc=0xf032d0u;break;
case 0xf032d0u: /* subqt   $1,r6 */
 s.registers[0][6]-=1u;
 s.pc=0xf032d2u;break;
  case 0xf032d2u: /* jump    z,(r9) */
   if(condition(&s,2)){pending=1;target=s.registers[0][9];}
   s.pc=0xf032d4u;break;
  case 0xf032d4u: /* shlq    $1,r7 */
   s.c=s.registers[0][7]>>31;s.registers[0][7]=s.registers[0][7]<<1;zn(&s,s.registers[0][7]);
   s.pc=0xf032d6u;break;
  case 0xf032d6u: /* subq    $4,r6 */
   s.registers[0][6]=sub(&s,s.registers[0][6],4u);
   s.pc=0xf032d8u;break;
  case 0xf032d8u: /* jr      nn,00F032E6 */
   if(condition(&s,20)){pending=1;target=0xf032e6u;}
   s.pc=0xf032dau;break;
  case 0xf032dau: /* shlq    $4,r7 */
   s.c=s.registers[0][7]>>31;s.registers[0][7]=s.registers[0][7]<<4;zn(&s,s.registers[0][7]);
   s.pc=0xf032dcu;break;
case 0xf032dcu: /* loadb   (r1),r0 */
 CHECK(rd8(bus,&s,s.registers[0][1],&v));s.registers[0][0]=v;
 s.pc=0xf032deu;break;
  case 0xf032deu: /* addq    $1,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],1u);
   s.pc=0xf032e0u;break;
case 0xf032e0u: /* sh      r6,r0 */
 v=s.registers[0][6];if(v&0x80000000u){s.c=s.registers[0][0]>>31;s.registers[0][0]=(v<=0xffffffe0u)?0:s.registers[0][0]<<(0u-v);}else{s.c=s.registers[0][0]&1u;s.registers[0][0]=v>=32?0:s.registers[0][0]>>v;}zn(&s,s.registers[0][0]);
 s.pc=0xf032e2u;break;
  case 0xf032e2u: /* addq    $8,r6 */
   s.registers[0][6]=add(&s,s.registers[0][6],8u);
   s.pc=0xf032e4u;break;
  case 0xf032e4u: /* or      r0,r7 */
   s.registers[0][7]|=s.registers[0][0];
   zn(&s,s.registers[0][7]);
   s.pc=0xf032e6u;break;
  case 0xf032e6u: /* move    r7,r0 */
   s.registers[0][0]=s.registers[0][7];
   s.pc=0xf032e8u;break;
  case 0xf032e8u: /* and     r8,r0 */
   s.registers[0][0]&=s.registers[0][8];
   zn(&s,s.registers[0][0]);
   s.pc=0xf032eau;break;
  case 0xf032eau: /* move    r11,r10 */
   s.registers[0][10]=s.registers[0][11];
   s.pc=0xf032ecu;break;
  case 0xf032ecu: /* shrq    $6,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=s.registers[0][0]>>6;zn(&s,s.registers[0][0]);
   s.pc=0xf032eeu;break;
  case 0xf032eeu: /* add     r0,r10 */
   s.registers[0][10]=add(&s,s.registers[0][10],s.registers[0][0]);
   s.pc=0xf032f0u;break;
  case 0xf032f0u: /* shrq    $2,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=s.registers[0][0]>>2;zn(&s,s.registers[0][0]);
   s.pc=0xf032f2u;break;
  case 0xf032f2u: /* subq    $2,r2 */
   s.registers[0][2]=sub(&s,s.registers[0][2],2u);
   s.pc=0xf032f4u;break;
  case 0xf032f4u: /* sub     r0,r2 */
   s.registers[0][2]=sub(&s,s.registers[0][2],s.registers[0][0]);
   s.pc=0xf032f6u;break;
case 0xf032f6u: /* load    (r10),r0 */
 CHECK(rd32(bus,&s,local(s.registers[0][10])?(s.registers[0][10]&~3u):s.registers[0][10],&v));s.registers[0][0]=v;
 s.pc=0xf032f8u;break;
  case 0xf032f8u: /* jump    (r0) */
   if(condition(&s,0)){pending=1;target=s.registers[0][0];}
   s.pc=0xf032fau;break;
  case 0xf032fau: /* storew  r5,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][5]));
   s.pc=0xf032fcu;break;
  case 0xf0333cu: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf0333eu;break;
  case 0xf0333eu: /* storew  r5,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][5]));
   s.pc=0xf03340u;break;
  case 0xf03340u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf03342u;break;
  case 0xf03342u: /* storew  r5,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][5]));
   s.pc=0xf03344u;break;
  case 0xf03344u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf03346u;break;
  case 0xf03346u: /* storew  r5,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][5]));
   s.pc=0xf03348u;break;
  case 0xf03348u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf0334au;break;
  case 0xf0334au: /* storew  r5,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][5]));
   s.pc=0xf0334cu;break;
  case 0xf0334cu: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf0334eu;break;
  case 0xf0334eu: /* storew  r5,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][5]));
   s.pc=0xf03350u;break;
  case 0xf03350u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf03352u;break;
  case 0xf03352u: /* storew  r5,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][5]));
   s.pc=0xf03354u;break;
  case 0xf03354u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf03356u;break;
  case 0xf03356u: /* storew  r5,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][5]));
   s.pc=0xf03358u;break;
  case 0xf03358u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf0335au;break;
  case 0xf0335au: /* storew  r5,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][5]));
   s.pc=0xf0335cu;break;
  case 0xf0335cu: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf0335eu;break;
  case 0xf0335eu: /* storew  r5,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][5]));
   s.pc=0xf03360u;break;
  case 0xf03360u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf03362u;break;
  case 0xf03362u: /* storew  r5,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][5]));
   s.pc=0xf03364u;break;
  case 0xf03364u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf03366u;break;
  case 0xf03366u: /* storew  r5,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][5]));
   s.pc=0xf03368u;break;
  case 0xf03368u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf0336au;break;
  case 0xf0336au: /* storew  r5,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][5]));
   s.pc=0xf0336cu;break;
  case 0xf0336cu: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf0336eu;break;
  case 0xf0336eu: /* storew  r5,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][5]));
   s.pc=0xf03370u;break;
  case 0xf03370u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf03372u;break;
  case 0xf03372u: /* storew  r5,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][5]));
   s.pc=0xf03374u;break;
  case 0xf03374u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf03376u;break;
  case 0xf03376u: /* storew  r5,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][5]));
   s.pc=0xf03378u;break;
  case 0xf03378u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf0337au;break;
  case 0xf0337au: /* storew  r5,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][5]));
   s.pc=0xf0337cu;break;
  case 0xf0337cu: /* cmpq    $0,r2 */
   (void)sub(&s,s.registers[0][2],0x0u);
   s.pc=0xf0337eu;break;
  case 0xf0337eu: /* jump    nn,(r12) */
   if(condition(&s,20)){pending=1;target=s.registers[0][12];}
   s.pc=0xf03380u;break;
  case 0xf03380u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf03382u;break;
  case 0xf03382u: /* jump    (r15) */
   if(condition(&s,0)){pending=1;target=s.registers[0][15];}
   s.pc=0xf03384u;break;
  case 0xf03384u: /* nop */
   s.pc=0xf03386u;break;
  case 0xf03386u: /* cmpq    $0,r6 */
   (void)sub(&s,s.registers[0][6],0x0u);
   s.pc=0xf03388u;break;
  case 0xf03388u: /* jr      nz,00F03392 */
   if(condition(&s,1)){pending=1;target=0xf03392u;}
   s.pc=0xf0338au;break;
  case 0xf0338au: /* nop */
   s.pc=0xf0338cu;break;
case 0xf0338cu: /* loadb   (r1),r7 */
 CHECK(rd8(bus,&s,s.registers[0][1],&v));s.registers[0][7]=v;
 s.pc=0xf0338eu;break;
  case 0xf0338eu: /* moveq   8,r6 */
   s.registers[0][6]=8u;
   s.pc=0xf03390u;break;
  case 0xf03390u: /* addq    $1,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],1u);
   s.pc=0xf03392u;break;
  case 0xf03392u: /* btst    $7,r7 */
   s.z=((~s.registers[0][7])>>7)&1u;
   s.pc=0xf03394u;break;
case 0xf03394u: /* subqt   $1,r6 */
 s.registers[0][6]-=1u;
 s.pc=0xf03396u;break;
  case 0xf03396u: /* jump    z,(r13) */
   if(condition(&s,2)){pending=1;target=s.registers[0][13];}
   s.pc=0xf03398u;break;
  case 0xf03398u: /* shlq    $1,r7 */
   s.c=s.registers[0][7]>>31;s.registers[0][7]=s.registers[0][7]<<1;zn(&s,s.registers[0][7]);
   s.pc=0xf0339au;break;
  case 0xf0339au: /* subq    $3,r6 */
   s.registers[0][6]=sub(&s,s.registers[0][6],3u);
   s.pc=0xf0339cu;break;
  case 0xf0339cu: /* jr      nn,00F033AA */
   if(condition(&s,20)){pending=1;target=0xf033aau;}
   s.pc=0xf0339eu;break;
  case 0xf0339eu: /* shlq    $3,r7 */
   s.c=s.registers[0][7]>>31;s.registers[0][7]=s.registers[0][7]<<3;zn(&s,s.registers[0][7]);
   s.pc=0xf033a0u;break;
case 0xf033a0u: /* loadb   (r1),r0 */
 CHECK(rd8(bus,&s,s.registers[0][1],&v));s.registers[0][0]=v;
 s.pc=0xf033a2u;break;
  case 0xf033a2u: /* addq    $1,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],1u);
   s.pc=0xf033a4u;break;
case 0xf033a4u: /* sh      r6,r0 */
 v=s.registers[0][6];if(v&0x80000000u){s.c=s.registers[0][0]>>31;s.registers[0][0]=(v<=0xffffffe0u)?0:s.registers[0][0]<<(0u-v);}else{s.c=s.registers[0][0]&1u;s.registers[0][0]=v>=32?0:s.registers[0][0]>>v;}zn(&s,s.registers[0][0]);
 s.pc=0xf033a6u;break;
  case 0xf033a6u: /* addq    $8,r6 */
   s.registers[0][6]=add(&s,s.registers[0][6],8u);
   s.pc=0xf033a8u;break;
  case 0xf033a8u: /* or      r0,r7 */
   s.registers[0][7]|=s.registers[0][0];
   zn(&s,s.registers[0][7]);
   s.pc=0xf033aau;break;
  case 0xf033aau: /* move    r7,r0 */
   s.registers[0][0]=s.registers[0][7];
   s.pc=0xf033acu;break;
  case 0xf033acu: /* and     r19,r0 */
   s.registers[0][0]&=s.registers[0][19];
   zn(&s,s.registers[0][0]);
   s.pc=0xf033aeu;break;
  case 0xf033aeu: /* move    r14,r10 */
   s.registers[0][10]=s.registers[0][14];
   s.pc=0xf033b0u;break;
  case 0xf033b0u: /* shrq    $6,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=s.registers[0][0]>>6;zn(&s,s.registers[0][0]);
   s.pc=0xf033b2u;break;
  case 0xf033b2u: /* add     r0,r10 */
   s.registers[0][10]=add(&s,s.registers[0][10],s.registers[0][0]);
   s.pc=0xf033b4u;break;
  case 0xf033b4u: /* shrq    $2,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=s.registers[0][0]>>2;zn(&s,s.registers[0][0]);
   s.pc=0xf033b6u;break;
  case 0xf033b6u: /* subq    $2,r2 */
   s.registers[0][2]=sub(&s,s.registers[0][2],2u);
   s.pc=0xf033b8u;break;
  case 0xf033b8u: /* sub     r0,r2 */
   s.registers[0][2]=sub(&s,s.registers[0][2],s.registers[0][0]);
   s.pc=0xf033bau;break;
case 0xf033bau: /* loadb   (r1),r0 */
 CHECK(rd8(bus,&s,s.registers[0][1],&v));s.registers[0][0]=v;
 s.pc=0xf033bcu;break;
  case 0xf033bcu: /* addq    $1,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],1u);
   s.pc=0xf033beu;break;
  case 0xf033beu: /* shlq    $1,r0 */
   s.c=s.registers[0][0]>>31;s.registers[0][0]=s.registers[0][0]<<1;zn(&s,s.registers[0][0]);
   s.pc=0xf033c0u;break;
  case 0xf033c0u: /* add     r4,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][4]);
   s.pc=0xf033c2u;break;
  case 0xf033c2u: /* loadw   (r0),r0 */
   CHECK(loadw(bus,&s,s.registers[0][0],&v));s.registers[0][0]=v;
   s.pc=0xf033c4u;break;
case 0xf033c4u: /* load    (r10),r10 */
 CHECK(rd32(bus,&s,local(s.registers[0][10])?(s.registers[0][10]&~3u):s.registers[0][10],&v));s.registers[0][10]=v;
 s.pc=0xf033c6u;break;
  case 0xf033c6u: /* jump    (r10) */
   if(condition(&s,0)){pending=1;target=s.registers[0][10];}
   s.pc=0xf033c8u;break;
  case 0xf033c8u: /* storew  r0,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][0]));
   s.pc=0xf033cau;break;
  case 0xf0340cu: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf0340eu;break;
  case 0xf0340eu: /* storew  r0,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][0]));
   s.pc=0xf03410u;break;
  case 0xf03410u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf03412u;break;
  case 0xf03412u: /* storew  r0,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][0]));
   s.pc=0xf03414u;break;
  case 0xf03414u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf03416u;break;
  case 0xf03416u: /* storew  r0,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][0]));
   s.pc=0xf03418u;break;
  case 0xf03418u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf0341au;break;
  case 0xf0341au: /* storew  r0,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][0]));
   s.pc=0xf0341cu;break;
  case 0xf0341cu: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf0341eu;break;
  case 0xf0341eu: /* storew  r0,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][0]));
   s.pc=0xf03420u;break;
  case 0xf03420u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf03422u;break;
  case 0xf03422u: /* storew  r0,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][0]));
   s.pc=0xf03424u;break;
  case 0xf03424u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf03426u;break;
  case 0xf03426u: /* storew  r0,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][0]));
   s.pc=0xf03428u;break;
  case 0xf03428u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf0342au;break;
  case 0xf0342au: /* storew  r0,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][0]));
   s.pc=0xf0342cu;break;
  case 0xf0342cu: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf0342eu;break;
  case 0xf0342eu: /* storew  r0,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][0]));
   s.pc=0xf03430u;break;
  case 0xf03430u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf03432u;break;
  case 0xf03432u: /* storew  r0,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][0]));
   s.pc=0xf03434u;break;
  case 0xf03434u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf03436u;break;
  case 0xf03436u: /* storew  r0,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][0]));
   s.pc=0xf03438u;break;
  case 0xf03438u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf0343au;break;
  case 0xf0343au: /* storew  r0,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][0]));
   s.pc=0xf0343cu;break;
  case 0xf0343cu: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf0343eu;break;
  case 0xf0343eu: /* storew  r0,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][0]));
   s.pc=0xf03440u;break;
  case 0xf03440u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf03442u;break;
  case 0xf03442u: /* storew  r0,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][0]));
   s.pc=0xf03444u;break;
  case 0xf03444u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf03446u;break;
  case 0xf03446u: /* storew  r0,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][0]));
   s.pc=0xf03448u;break;
  case 0xf03448u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf0344au;break;
  case 0xf0344au: /* storew  r0,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][0]));
   s.pc=0xf0344cu;break;
  case 0xf0344cu: /* cmpq    $0,r2 */
   (void)sub(&s,s.registers[0][2],0x0u);
   s.pc=0xf0344eu;break;
  case 0xf0344eu: /* jump    nn,(r12) */
   if(condition(&s,20)){pending=1;target=s.registers[0][12];}
   s.pc=0xf03450u;break;
  case 0xf03450u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf03452u;break;
  case 0xf03452u: /* jump    (r15) */
   if(condition(&s,0)){pending=1;target=s.registers[0][15];}
   s.pc=0xf03454u;break;
  case 0xf03454u: /* nop */
   s.pc=0xf03456u;break;
  case 0xf03456u: /* subq    $4,r6 */
   s.registers[0][6]=sub(&s,s.registers[0][6],4u);
   s.pc=0xf03458u;break;
  case 0xf03458u: /* jr      nn,00F03466 */
   if(condition(&s,20)){pending=1;target=0xf03466u;}
   s.pc=0xf0345au;break;
  case 0xf0345au: /* shlq    $4,r7 */
   s.c=s.registers[0][7]>>31;s.registers[0][7]=s.registers[0][7]<<4;zn(&s,s.registers[0][7]);
   s.pc=0xf0345cu;break;
case 0xf0345cu: /* loadb   (r1),r0 */
 CHECK(rd8(bus,&s,s.registers[0][1],&v));s.registers[0][0]=v;
 s.pc=0xf0345eu;break;
  case 0xf0345eu: /* addq    $1,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],1u);
   s.pc=0xf03460u;break;
case 0xf03460u: /* sh      r6,r0 */
 v=s.registers[0][6];if(v&0x80000000u){s.c=s.registers[0][0]>>31;s.registers[0][0]=(v<=0xffffffe0u)?0:s.registers[0][0]<<(0u-v);}else{s.c=s.registers[0][0]&1u;s.registers[0][0]=v>=32?0:s.registers[0][0]>>v;}zn(&s,s.registers[0][0]);
 s.pc=0xf03462u;break;
  case 0xf03462u: /* addq    $8,r6 */
   s.registers[0][6]=add(&s,s.registers[0][6],8u);
   s.pc=0xf03464u;break;
  case 0xf03464u: /* or      r0,r7 */
   s.registers[0][7]|=s.registers[0][0];
   zn(&s,s.registers[0][7]);
   s.pc=0xf03466u;break;
  case 0xf03466u: /* move    r7,r0 */
   s.registers[0][0]=s.registers[0][7];
   s.pc=0xf03468u;break;
  case 0xf03468u: /* and     r20,r0 */
   s.registers[0][0]&=s.registers[0][20];
   zn(&s,s.registers[0][0]);
   s.pc=0xf0346au;break;
  case 0xf0346au: /* shrq    $8,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=s.registers[0][0]>>8;zn(&s,s.registers[0][0]);
   s.pc=0xf0346cu;break;
  case 0xf0346cu: /* sub     r0,r2 */
   s.registers[0][2]=sub(&s,s.registers[0][2],s.registers[0][0]);
   s.pc=0xf0346eu;break;
  case 0xf0346eu: /* subq    $1,r2 */
   s.registers[0][2]=sub(&s,s.registers[0][2],1u);
   s.pc=0xf03470u;break;
case 0xf03470u: /* loadb   (r1),r16 */
 CHECK(rd8(bus,&s,s.registers[0][1],&v));s.registers[0][16]=v;
 s.pc=0xf03472u;break;
  case 0xf03472u: /* addq    $1,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],1u);
   s.pc=0xf03474u;break;
  case 0xf03474u: /* shlq    $1,r16 */
   s.c=s.registers[0][16]>>31;s.registers[0][16]=s.registers[0][16]<<1;zn(&s,s.registers[0][16]);
   s.pc=0xf03476u;break;
  case 0xf03476u: /* add     r4,r16 */
   s.registers[0][16]=add(&s,s.registers[0][16],s.registers[0][4]);
   s.pc=0xf03478u;break;
  case 0xf03478u: /* loadw   (r16),r16 */
   CHECK(loadw(bus,&s,s.registers[0][16],&v));s.registers[0][16]=v;
   s.pc=0xf0347au;break;
  case 0xf0347au: /* storew  r16,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][16]));
   s.pc=0xf0347cu;break;
  case 0xf0347cu: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf0347eu;break;
  case 0xf0347eu: /* subq    $1,r0 */
   s.registers[0][0]=sub(&s,s.registers[0][0],1u);
   s.pc=0xf03480u;break;
  case 0xf03480u: /* jr      nn,00F03472 */
   if(condition(&s,20)){pending=1;target=0xf03472u;}
   s.pc=0xf03482u;break;
case 0xf03482u: /* loadb   (r1),r16 */
 CHECK(rd8(bus,&s,s.registers[0][1],&v));s.registers[0][16]=v;
 s.pc=0xf03484u;break;
  case 0xf03484u: /* cmpq    $0,r2 */
   (void)sub(&s,s.registers[0][2],0x0u);
   s.pc=0xf03486u;break;
  case 0xf03486u: /* jump    nn,(r12) */
   if(condition(&s,20)){pending=1;target=s.registers[0][12];}
   s.pc=0xf03488u;break;
  case 0xf03488u: /* nop */
   s.pc=0xf0348au;break;
  case 0xf0348au: /* movei   $f0211c,r18 */
   s.registers[0][18]=0xf0211cu;
   s.pc=0xf03490u;break;
  case 0xf03490u: /* moveq   0,r0 */
   s.registers[0][0]=0u;
   s.pc=0xf03492u;break;
  case 0xf03492u: /* store   r0,(r18) */
   CHECK(wr32(bus,&s,local(s.registers[0][18])?(s.registers[0][18]&~3u):s.registers[0][18],s.registers[0][0]));
   s.pc=0xf03494u;break;
  case 0xf03494u: /* movei   $f031be,r0 */
   s.registers[0][0]=0xf031beu;
   s.pc=0xf0349au;break;
  case 0xf0349au: /* jump    (r0) */
   if(condition(&s,0)){pending=1;target=s.registers[0][0];}
   s.pc=0xf0349cu;break;
  case 0xf0349cu: /* nop */
   s.pc=0xf0349eu;break;
default:return BIWN_SPRITE_FULLGPU_BAD_PC;
}if(delayed){if(pending)return BIWN_SPRITE_FULLGPU_BAD_DELAY;s.pc=resume;}if(s.pc==0xf031beu){*state=s;return 0;}}return BIWN_SPRITE_FULLGPU_WORK_LIMIT;}
