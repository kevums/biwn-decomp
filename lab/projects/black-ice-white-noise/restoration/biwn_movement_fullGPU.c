/* Generated from the pinned GPU4D80 overlay by
 * scripts/generate_biwn_movement_fullGPU.py. Analyst static recompilation,
 * not recovered original source. Integer primitive behavior is checked
 * against the pinned Virtual Jaguar core; no core runs on the C side. */
#include "biwn_movement_fullGPU.h"
#include <string.h>
static uint32_t sx16(uint32_t v){return(v&0x7fffu)-(v&0x8000u);}
static uint32_t sar(uint32_t v,unsigned n){return n>=32?((v&0x80000000u)?0xffffffffu:0):(v>>n)|((v&0x80000000u)?(0xffffffffu<<(32-n)):0);}
static void zn(struct biwn_movement_fullGPU_state *s,uint32_t v){s->z=v==0;s->n=v>>31;}
static uint32_t add(struct biwn_movement_fullGPU_state *s,uint32_t a,uint32_t b){uint32_t v=a+b;s->c=b>~a;zn(s,v);return v;}
static uint32_t sub(struct biwn_movement_fullGPU_state *s,uint32_t a,uint32_t b){uint32_t v=a-b;s->c=b>a;zn(s,v);return v;}
static int condition(struct biwn_movement_fullGPU_state *s,unsigned code){unsigned flags=s->z|(s->c<<1)|(s->n<<2);return !((code&1u)&&(flags&1u))&&!((code&2u)&&!(flags&1u))&&!((code&4u)&&(flags&(2u<<(code>>4))))&&!((code&8u)&&!(flags&(2u<<(code>>4))));}
static uint32_t be32(const uint8_t *p){return((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
static void put32(uint8_t *p,uint32_t v){p[0]=(uint8_t)(v>>24);p[1]=(uint8_t)(v>>16);p[2]=(uint8_t)(v>>8);p[3]=(uint8_t)v;}
static int local(uint32_t a){return a>=0xf03000u&&a<=0xf03ffcu;}
static int rd32(struct biwn_movement_fullGPU_bus *bus,struct biwn_movement_fullGPU_state *s,uint32_t a,uint32_t *v){if(local(a)){*v=be32(s->local_RAM+a-0xf03000u);return 0;}if(a==0xf02104u){*v=s->matrix_control;return 0;}if(a==0xf02108u){*v=s->matrix_pointer;return 0;}return bus->read32(bus->context,a,v)?2:0;}
static int rd16(struct biwn_movement_fullGPU_bus *bus,struct biwn_movement_fullGPU_state *s,uint32_t a,uint32_t *v){uint16_t h;if(a>=0xf03000u&&a<=0xf03ffeu){unsigned p=a-0xf03000u;*v=((uint32_t)s->local_RAM[p]<<8)|s->local_RAM[p+1];return 0;}if(bus->read16(bus->context,a,&h))return 2;*v=h;return 0;}
static int loadw(struct biwn_movement_fullGPU_bus *bus,struct biwn_movement_fullGPU_state *s,uint32_t a,uint32_t *v){if(a>=0xf03000u&&a<=0xf03fffu)return rd32(bus,s,a&~3u,v);return rd16(bus,s,a,v);}
static int wr32(struct biwn_movement_fullGPU_bus *bus,struct biwn_movement_fullGPU_state *s,uint32_t a,uint32_t v){if(local(a)){put32(s->local_RAM+a-0xf03000u,v);return 0;}if(a==0xf02104u){s->matrix_control=v;return 0;}if(a==0xf02108u){s->matrix_pointer=v&~3u;return 0;}return bus->write32(bus->context,a,v)?2:0;}
static int wr16(struct biwn_movement_fullGPU_bus *bus,struct biwn_movement_fullGPU_state *s,uint32_t a,uint32_t v){if(a>=0xf03000u&&a<=0xf03fffu)return wr32(bus,s,a&~1u,v&0xffffu);return bus->write16(bus->context,a,(uint16_t)v)?2:0;}
#define CHECK(e) do{int status=(e);if(status)return(enum biwn_movement_fullGPU_status)status;}while(0)
enum biwn_movement_fullGPU_status biwn_movement_fullGPU_run(struct biwn_movement_fullGPU_bus *bus,struct biwn_movement_fullGPU_state *state,uint32_t budget){struct biwn_movement_fullGPU_state s;uint32_t v,target=0;unsigned pending=0;if(!bus||!state||!budget||!bus->read16||!bus->read32||!bus->write16||!bus->write32||state->active_bank||state->z>1||state->c>1||state->n>1)return 1;s=*state;while(budget--){unsigned delayed=pending;uint32_t resume=target;pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){
  case 0xf03240u: /* moveq   0,r0 */
   s.registers[0][0]=0u;
   s.pc=0xf03242u;break;
  case 0xf03242u: /* moveq   1,r1 */
   s.registers[0][1]=1u;
   s.pc=0xf03244u;break;
  case 0xf03244u: /* moveta  r0,r0 */
   s.registers[1][0]=s.registers[0][0];
   s.pc=0xf03246u;break;
  case 0xf03246u: /* shlq    $e,r1 */
   s.c=s.registers[0][1]>>31;s.registers[0][1]=s.registers[0][1]<<14;zn(&s,s.registers[0][1]);
   s.pc=0xf03248u;break;
  case 0xf03248u: /* moveta  r0,r1 */
   s.registers[1][1]=s.registers[0][0];
   s.pc=0xf0324au;break;
  case 0xf0324au: /* moveta  r0,r3 */
   s.registers[1][3]=s.registers[0][0];
   s.pc=0xf0324cu;break;
  case 0xf0324cu: /* movei   $f0320c,r3 */
   s.registers[0][3]=0xf0320cu;
   s.pc=0xf03252u;break;
case 0xf03252u: /* load    (r3),r3 */
 CHECK(rd32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],&v));s.registers[0][3]=v;
 s.pc=0xf03254u;break;
  case 0xf03254u: /* or      r3,r3 */
   s.registers[0][3]|=s.registers[0][3];
   zn(&s,s.registers[0][3]);
   s.pc=0xf03256u;break;
  case 0xf03256u: /* storew  r1,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][1]));
   s.pc=0xf03258u;break;
  case 0xf03258u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf0325au;break;
  case 0xf0325au: /* storew  r0,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][0]));
   s.pc=0xf0325cu;break;
  case 0xf0325cu: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf0325eu;break;
  case 0xf0325eu: /* storew  r0,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][0]));
   s.pc=0xf03260u;break;
  case 0xf03260u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf03262u;break;
  case 0xf03262u: /* storew  r0,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][0]));
   s.pc=0xf03264u;break;
  case 0xf03264u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf03266u;break;
  case 0xf03266u: /* storew  r1,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][1]));
   s.pc=0xf03268u;break;
  case 0xf03268u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf0326au;break;
  case 0xf0326au: /* storew  r0,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][0]));
   s.pc=0xf0326cu;break;
  case 0xf0326cu: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf0326eu;break;
  case 0xf0326eu: /* storew  r0,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][0]));
   s.pc=0xf03270u;break;
  case 0xf03270u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf03272u;break;
  case 0xf03272u: /* storew  r0,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][0]));
   s.pc=0xf03274u;break;
  case 0xf03274u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf03276u;break;
  case 0xf03276u: /* storew  r1,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][1]));
   s.pc=0xf03278u;break;
  case 0xf03278u: /* movei   $f0320c,r3 */
   s.registers[0][3]=0xf0320cu;
   s.pc=0xf0327eu;break;
  case 0xf0327eu: /* moveq   1,r8 */
   s.registers[0][8]=1u;
   s.pc=0xf03280u;break;
case 0xf03280u: /* load    (r3),r0 */
 CHECK(rd32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],&v));s.registers[0][0]=v;
 s.pc=0xf03282u;break;
  case 0xf03282u: /* movei   $f034fa,r26 */
   s.registers[0][26]=0xf034fau;
   s.pc=0xf03288u;break;
  case 0xf03288u: /* addq    $4,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],4u);
   s.pc=0xf0328au;break;
  case 0xf0328au: /* shlq    $d,r8 */
   s.c=s.registers[0][8]>>31;s.registers[0][8]=s.registers[0][8]<<13;zn(&s,s.registers[0][8]);
   s.pc=0xf0328cu;break;
case 0xf0328cu: /* load    (r3),r4 */
 CHECK(rd32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],&v));s.registers[0][4]=v;
 s.pc=0xf0328eu;break;
  case 0xf0328eu: /* movei   $f034f8,r25 */
   s.registers[0][25]=0xf034f8u;
   s.pc=0xf03294u;break;
  case 0xf03294u: /* addq    $4,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],4u);
   s.pc=0xf03296u;break;
  case 0xf03296u: /* moveq   4,r23 */
   s.registers[0][23]=4u;
   s.pc=0xf03298u;break;
case 0xf03298u: /* load    (r3),r5 */
 CHECK(rd32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],&v));s.registers[0][5]=v;
 s.pc=0xf0329au;break;
  case 0xf0329au: /* movei   $f03530,r24 */
   s.registers[0][24]=0xf03530u;
   s.pc=0xf032a0u;break;
  case 0xf032a0u: /* addq    $4,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],4u);
   s.pc=0xf032a2u;break;
case 0xf032a2u: /* load    (r3),r6 */
 CHECK(rd32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],&v));s.registers[0][6]=v;
 s.pc=0xf032a4u;break;
  case 0xf032a4u: /* shlq    $4,r23 */
   s.c=s.registers[0][23]>>31;s.registers[0][23]=s.registers[0][23]<<4;zn(&s,s.registers[0][23]);
   s.pc=0xf032a6u;break;
  case 0xf032a6u: /* addq    $4,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],4u);
   s.pc=0xf032a8u;break;
case 0xf032a8u: /* load    (r3),r7 */
 CHECK(rd32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],&v));s.registers[0][7]=v;
 s.pc=0xf032aau;break;
  case 0xf032aau: /* loadw   (r0),r9 */
   CHECK(loadw(bus,&s,s.registers[0][0],&v));s.registers[0][9]=v;
   s.pc=0xf032acu;break;
  case 0xf032acu: /* shlq    $10,r7 */
   s.c=s.registers[0][7]>>31;s.registers[0][7]=s.registers[0][7]<<16;zn(&s,s.registers[0][7]);
   s.pc=0xf032aeu;break;
  case 0xf032aeu: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf032b0u;break;
  case 0xf032b0u: /* sharq   $10,r7 */
   s.c=s.registers[0][7]&1u;s.registers[0][7]=sar(s.registers[0][7],16);zn(&s,s.registers[0][7]);
   s.pc=0xf032b2u;break;
  case 0xf032b2u: /* loadw   (r0),r10 */
   CHECK(loadw(bus,&s,s.registers[0][0],&v));s.registers[0][10]=v;
   s.pc=0xf032b4u;break;
  case 0xf032b4u: /* shlq    $10,r9 */
   s.c=s.registers[0][9]>>31;s.registers[0][9]=s.registers[0][9]<<16;zn(&s,s.registers[0][9]);
   s.pc=0xf032b6u;break;
  case 0xf032b6u: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf032b8u;break;
  case 0xf032b8u: /* shlq    $10,r10 */
   s.c=s.registers[0][10]>>31;s.registers[0][10]=s.registers[0][10]<<16;zn(&s,s.registers[0][10]);
   s.pc=0xf032bau;break;
  case 0xf032bau: /* loadw   (r0),r11 */
   CHECK(loadw(bus,&s,s.registers[0][0],&v));s.registers[0][11]=v;
   s.pc=0xf032bcu;break;
  case 0xf032bcu: /* sharq   $10,r9 */
   s.c=s.registers[0][9]&1u;s.registers[0][9]=sar(s.registers[0][9],16);zn(&s,s.registers[0][9]);
   s.pc=0xf032beu;break;
  case 0xf032beu: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf032c0u;break;
  case 0xf032c0u: /* shlq    $10,r11 */
   s.c=s.registers[0][11]>>31;s.registers[0][11]=s.registers[0][11]<<16;zn(&s,s.registers[0][11]);
   s.pc=0xf032c2u;break;
  case 0xf032c2u: /* loadw   (r0),r12 */
   CHECK(loadw(bus,&s,s.registers[0][0],&v));s.registers[0][12]=v;
   s.pc=0xf032c4u;break;
  case 0xf032c4u: /* sharq   $10,r10 */
   s.c=s.registers[0][10]&1u;s.registers[0][10]=sar(s.registers[0][10],16);zn(&s,s.registers[0][10]);
   s.pc=0xf032c6u;break;
  case 0xf032c6u: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf032c8u;break;
  case 0xf032c8u: /* sharq   $10,r11 */
   s.c=s.registers[0][11]&1u;s.registers[0][11]=sar(s.registers[0][11],16);zn(&s,s.registers[0][11]);
   s.pc=0xf032cau;break;
  case 0xf032cau: /* loadw   (r0),r13 */
   CHECK(loadw(bus,&s,s.registers[0][0],&v));s.registers[0][13]=v;
   s.pc=0xf032ccu;break;
  case 0xf032ccu: /* shlq    $10,r12 */
   s.c=s.registers[0][12]>>31;s.registers[0][12]=s.registers[0][12]<<16;zn(&s,s.registers[0][12]);
   s.pc=0xf032ceu;break;
  case 0xf032ceu: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf032d0u;break;
  case 0xf032d0u: /* shlq    $10,r13 */
   s.c=s.registers[0][13]>>31;s.registers[0][13]=s.registers[0][13]<<16;zn(&s,s.registers[0][13]);
   s.pc=0xf032d2u;break;
  case 0xf032d2u: /* loadw   (r0),r14 */
   CHECK(loadw(bus,&s,s.registers[0][0],&v));s.registers[0][14]=v;
   s.pc=0xf032d4u;break;
  case 0xf032d4u: /* sharq   $10,r12 */
   s.c=s.registers[0][12]&1u;s.registers[0][12]=sar(s.registers[0][12],16);zn(&s,s.registers[0][12]);
   s.pc=0xf032d6u;break;
  case 0xf032d6u: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf032d8u;break;
  case 0xf032d8u: /* shlq    $10,r14 */
   s.c=s.registers[0][14]>>31;s.registers[0][14]=s.registers[0][14]<<16;zn(&s,s.registers[0][14]);
   s.pc=0xf032dau;break;
  case 0xf032dau: /* loadw   (r0),r15 */
   CHECK(loadw(bus,&s,s.registers[0][0],&v));s.registers[0][15]=v;
   s.pc=0xf032dcu;break;
  case 0xf032dcu: /* sharq   $10,r13 */
   s.c=s.registers[0][13]&1u;s.registers[0][13]=sar(s.registers[0][13],16);zn(&s,s.registers[0][13]);
   s.pc=0xf032deu;break;
  case 0xf032deu: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf032e0u;break;
  case 0xf032e0u: /* sharq   $10,r14 */
   s.c=s.registers[0][14]&1u;s.registers[0][14]=sar(s.registers[0][14],16);zn(&s,s.registers[0][14]);
   s.pc=0xf032e2u;break;
  case 0xf032e2u: /* loadw   (r0),r16 */
   CHECK(loadw(bus,&s,s.registers[0][0],&v));s.registers[0][16]=v;
   s.pc=0xf032e4u;break;
  case 0xf032e4u: /* shlq    $10,r15 */
   s.c=s.registers[0][15]>>31;s.registers[0][15]=s.registers[0][15]<<16;zn(&s,s.registers[0][15]);
   s.pc=0xf032e6u;break;
  case 0xf032e6u: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf032e8u;break;
  case 0xf032e8u: /* shlq    $10,r16 */
   s.c=s.registers[0][16]>>31;s.registers[0][16]=s.registers[0][16]<<16;zn(&s,s.registers[0][16]);
   s.pc=0xf032eau;break;
  case 0xf032eau: /* loadw   (r0),r17 */
   CHECK(loadw(bus,&s,s.registers[0][0],&v));s.registers[0][17]=v;
   s.pc=0xf032ecu;break;
  case 0xf032ecu: /* sharq   $10,r15 */
   s.c=s.registers[0][15]&1u;s.registers[0][15]=sar(s.registers[0][15],16);zn(&s,s.registers[0][15]);
   s.pc=0xf032eeu;break;
  case 0xf032eeu: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf032f0u;break;
  case 0xf032f0u: /* shlq    $10,r17 */
   s.c=s.registers[0][17]>>31;s.registers[0][17]=s.registers[0][17]<<16;zn(&s,s.registers[0][17]);
   s.pc=0xf032f2u;break;
  case 0xf032f2u: /* loadw   (r0),r18 */
   CHECK(loadw(bus,&s,s.registers[0][0],&v));s.registers[0][18]=v;
   s.pc=0xf032f4u;break;
  case 0xf032f4u: /* sharq   $10,r16 */
   s.c=s.registers[0][16]&1u;s.registers[0][16]=sar(s.registers[0][16],16);zn(&s,s.registers[0][16]);
   s.pc=0xf032f6u;break;
  case 0xf032f6u: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf032f8u;break;
  case 0xf032f8u: /* sharq   $10,r17 */
   s.c=s.registers[0][17]&1u;s.registers[0][17]=sar(s.registers[0][17],16);zn(&s,s.registers[0][17]);
   s.pc=0xf032fau;break;
  case 0xf032fau: /* loadw   (r0),r19 */
   CHECK(loadw(bus,&s,s.registers[0][0],&v));s.registers[0][19]=v;
   s.pc=0xf032fcu;break;
  case 0xf032fcu: /* shlq    $10,r18 */
   s.c=s.registers[0][18]>>31;s.registers[0][18]=s.registers[0][18]<<16;zn(&s,s.registers[0][18]);
   s.pc=0xf032feu;break;
  case 0xf032feu: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf03300u;break;
  case 0xf03300u: /* shlq    $10,r19 */
   s.c=s.registers[0][19]>>31;s.registers[0][19]=s.registers[0][19]<<16;zn(&s,s.registers[0][19]);
   s.pc=0xf03302u;break;
  case 0xf03302u: /* loadw   (r0),r20 */
   CHECK(loadw(bus,&s,s.registers[0][0],&v));s.registers[0][20]=v;
   s.pc=0xf03304u;break;
  case 0xf03304u: /* sharq   $10,r18 */
   s.c=s.registers[0][18]&1u;s.registers[0][18]=sar(s.registers[0][18],16);zn(&s,s.registers[0][18]);
   s.pc=0xf03306u;break;
  case 0xf03306u: /* shlq    $10,r20 */
   s.c=s.registers[0][20]>>31;s.registers[0][20]=s.registers[0][20]<<16;zn(&s,s.registers[0][20]);
   s.pc=0xf03308u;break;
  case 0xf03308u: /* sharq   $10,r19 */
   s.c=s.registers[0][19]&1u;s.registers[0][19]=sar(s.registers[0][19],16);zn(&s,s.registers[0][19]);
   s.pc=0xf0330au;break;
  case 0xf0330au: /* sharq   $10,r20 */
   s.c=s.registers[0][20]&1u;s.registers[0][20]=sar(s.registers[0][20],16);zn(&s,s.registers[0][20]);
   s.pc=0xf0330cu;break;
  case 0xf0330cu: /* movei   $f03388,r2 */
   s.registers[0][2]=0xf03388u;
   s.pc=0xf03312u;break;
  case 0xf03312u: /* cmpq    $0,r5 */
   (void)sub(&s,s.registers[0][5],0x0u);
   s.pc=0xf03314u;break;
  case 0xf03314u: /* jump    z,(r2) */
   if(condition(&s,2)){pending=1;target=s.registers[0][2];}
   s.pc=0xf03316u;break;
  case 0xf03316u: /* move    r5,r0 */
   s.registers[0][0]=s.registers[0][5];
   s.pc=0xf03318u;break;
  case 0xf03318u: /* move    pc,r27 */
   s.registers[0][27]=0xf03318u;
   s.pc=0xf0331au;break;
  case 0xf0331au: /* jump    (r26) */
   if(condition(&s,0)){pending=1;target=s.registers[0][26];}
   s.pc=0xf0331cu;break;
  case 0xf0331cu: /* addq    $6,r27 */
   s.registers[0][27]=add(&s,s.registers[0][27],6u);
   s.pc=0xf0331eu;break;
  case 0xf0331eu: /* move    r0,r21 */
   s.registers[0][21]=s.registers[0][0];
   s.pc=0xf03320u;break;
  case 0xf03320u: /* move    r5,r0 */
   s.registers[0][0]=s.registers[0][5];
   s.pc=0xf03322u;break;
  case 0xf03322u: /* move    pc,r27 */
   s.registers[0][27]=0xf03322u;
   s.pc=0xf03324u;break;
  case 0xf03324u: /* jump    (r25) */
   if(condition(&s,0)){pending=1;target=s.registers[0][25];}
   s.pc=0xf03326u;break;
  case 0xf03326u: /* addq    $6,r27 */
   s.registers[0][27]=add(&s,s.registers[0][27],6u);
   s.pc=0xf03328u;break;
  case 0xf03328u: /* move    r0,r22 */
   s.registers[0][22]=s.registers[0][0];
   s.pc=0xf0332au;break;
  case 0xf0332au: /* move    r21,r1 */
   s.registers[0][1]=s.registers[0][21];
   s.pc=0xf0332cu;break;
  case 0xf0332cu: /* imult   r15,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][15]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf0332eu;break;
  case 0xf0332eu: /* imult   r9,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][9]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf03330u;break;
  case 0xf03330u: /* sub     r1,r0 */
   s.registers[0][0]=sub(&s,s.registers[0][0],s.registers[0][1]);
   s.pc=0xf03332u;break;
  case 0xf03332u: /* move    r21,r1 */
   s.registers[0][1]=s.registers[0][21];
   s.pc=0xf03334u;break;
  case 0xf03334u: /* add     r8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][8]);
   s.pc=0xf03336u;break;
  case 0xf03336u: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf03338u;break;
  case 0xf03338u: /* imult   r15,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][15]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf0333au;break;
  case 0xf0333au: /* move    r0,r15 */
   s.registers[0][15]=s.registers[0][0];
   s.pc=0xf0333cu;break;
  case 0xf0333cu: /* move    r22,r0 */
   s.registers[0][0]=s.registers[0][22];
   s.pc=0xf0333eu;break;
  case 0xf0333eu: /* imult   r9,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][9]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf03340u;break;
  case 0xf03340u: /* add     r1,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][1]);
   s.pc=0xf03342u;break;
  case 0xf03342u: /* add     r8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][8]);
   s.pc=0xf03344u;break;
  case 0xf03344u: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf03346u;break;
  case 0xf03346u: /* move    r0,r9 */
   s.registers[0][9]=s.registers[0][0];
   s.pc=0xf03348u;break;
  case 0xf03348u: /* move    r22,r0 */
   s.registers[0][0]=s.registers[0][22];
   s.pc=0xf0334au;break;
  case 0xf0334au: /* move    r21,r1 */
   s.registers[0][1]=s.registers[0][21];
   s.pc=0xf0334cu;break;
  case 0xf0334cu: /* imult   r16,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][16]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf0334eu;break;
  case 0xf0334eu: /* imult   r10,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][10]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf03350u;break;
  case 0xf03350u: /* sub     r1,r0 */
   s.registers[0][0]=sub(&s,s.registers[0][0],s.registers[0][1]);
   s.pc=0xf03352u;break;
  case 0xf03352u: /* move    r21,r1 */
   s.registers[0][1]=s.registers[0][21];
   s.pc=0xf03354u;break;
  case 0xf03354u: /* add     r8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][8]);
   s.pc=0xf03356u;break;
  case 0xf03356u: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf03358u;break;
  case 0xf03358u: /* imult   r16,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][16]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf0335au;break;
  case 0xf0335au: /* move    r0,r16 */
   s.registers[0][16]=s.registers[0][0];
   s.pc=0xf0335cu;break;
  case 0xf0335cu: /* move    r22,r0 */
   s.registers[0][0]=s.registers[0][22];
   s.pc=0xf0335eu;break;
  case 0xf0335eu: /* imult   r10,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][10]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf03360u;break;
  case 0xf03360u: /* add     r1,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][1]);
   s.pc=0xf03362u;break;
  case 0xf03362u: /* add     r8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][8]);
   s.pc=0xf03364u;break;
  case 0xf03364u: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf03366u;break;
  case 0xf03366u: /* move    r0,r10 */
   s.registers[0][10]=s.registers[0][0];
   s.pc=0xf03368u;break;
  case 0xf03368u: /* move    r22,r0 */
   s.registers[0][0]=s.registers[0][22];
   s.pc=0xf0336au;break;
  case 0xf0336au: /* move    r21,r1 */
   s.registers[0][1]=s.registers[0][21];
   s.pc=0xf0336cu;break;
  case 0xf0336cu: /* imult   r17,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][17]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf0336eu;break;
  case 0xf0336eu: /* imult   r11,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][11]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf03370u;break;
  case 0xf03370u: /* sub     r1,r0 */
   s.registers[0][0]=sub(&s,s.registers[0][0],s.registers[0][1]);
   s.pc=0xf03372u;break;
  case 0xf03372u: /* move    r21,r1 */
   s.registers[0][1]=s.registers[0][21];
   s.pc=0xf03374u;break;
  case 0xf03374u: /* add     r8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][8]);
   s.pc=0xf03376u;break;
  case 0xf03376u: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf03378u;break;
  case 0xf03378u: /* imult   r17,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][17]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf0337au;break;
  case 0xf0337au: /* move    r0,r17 */
   s.registers[0][17]=s.registers[0][0];
   s.pc=0xf0337cu;break;
  case 0xf0337cu: /* move    r22,r0 */
   s.registers[0][0]=s.registers[0][22];
   s.pc=0xf0337eu;break;
  case 0xf0337eu: /* imult   r11,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][11]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf03380u;break;
  case 0xf03380u: /* add     r1,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][1]);
   s.pc=0xf03382u;break;
  case 0xf03382u: /* add     r8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][8]);
   s.pc=0xf03384u;break;
  case 0xf03384u: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf03386u;break;
  case 0xf03386u: /* move    r0,r11 */
   s.registers[0][11]=s.registers[0][0];
   s.pc=0xf03388u;break;
  case 0xf03388u: /* movei   $f03404,r2 */
   s.registers[0][2]=0xf03404u;
   s.pc=0xf0338eu;break;
  case 0xf0338eu: /* cmpq    $0,r4 */
   (void)sub(&s,s.registers[0][4],0x0u);
   s.pc=0xf03390u;break;
  case 0xf03390u: /* jump    z,(r2) */
   if(condition(&s,2)){pending=1;target=s.registers[0][2];}
   s.pc=0xf03392u;break;
  case 0xf03392u: /* move    r4,r0 */
   s.registers[0][0]=s.registers[0][4];
   s.pc=0xf03394u;break;
  case 0xf03394u: /* move    pc,r27 */
   s.registers[0][27]=0xf03394u;
   s.pc=0xf03396u;break;
  case 0xf03396u: /* jump    (r26) */
   if(condition(&s,0)){pending=1;target=s.registers[0][26];}
   s.pc=0xf03398u;break;
  case 0xf03398u: /* addq    $6,r27 */
   s.registers[0][27]=add(&s,s.registers[0][27],6u);
   s.pc=0xf0339au;break;
  case 0xf0339au: /* move    r0,r21 */
   s.registers[0][21]=s.registers[0][0];
   s.pc=0xf0339cu;break;
  case 0xf0339cu: /* move    r4,r0 */
   s.registers[0][0]=s.registers[0][4];
   s.pc=0xf0339eu;break;
  case 0xf0339eu: /* move    pc,r27 */
   s.registers[0][27]=0xf0339eu;
   s.pc=0xf033a0u;break;
  case 0xf033a0u: /* jump    (r25) */
   if(condition(&s,0)){pending=1;target=s.registers[0][25];}
   s.pc=0xf033a2u;break;
  case 0xf033a2u: /* addq    $6,r27 */
   s.registers[0][27]=add(&s,s.registers[0][27],6u);
   s.pc=0xf033a4u;break;
  case 0xf033a4u: /* move    r0,r22 */
   s.registers[0][22]=s.registers[0][0];
   s.pc=0xf033a6u;break;
  case 0xf033a6u: /* move    r21,r1 */
   s.registers[0][1]=s.registers[0][21];
   s.pc=0xf033a8u;break;
  case 0xf033a8u: /* imult   r12,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][12]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf033aau;break;
  case 0xf033aau: /* imult   r15,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][15]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf033acu;break;
  case 0xf033acu: /* sub     r1,r0 */
   s.registers[0][0]=sub(&s,s.registers[0][0],s.registers[0][1]);
   s.pc=0xf033aeu;break;
  case 0xf033aeu: /* move    r21,r1 */
   s.registers[0][1]=s.registers[0][21];
   s.pc=0xf033b0u;break;
  case 0xf033b0u: /* add     r8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][8]);
   s.pc=0xf033b2u;break;
  case 0xf033b2u: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf033b4u;break;
  case 0xf033b4u: /* imult   r12,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][12]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf033b6u;break;
  case 0xf033b6u: /* move    r0,r12 */
   s.registers[0][12]=s.registers[0][0];
   s.pc=0xf033b8u;break;
  case 0xf033b8u: /* move    r22,r0 */
   s.registers[0][0]=s.registers[0][22];
   s.pc=0xf033bau;break;
  case 0xf033bau: /* imult   r15,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][15]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf033bcu;break;
  case 0xf033bcu: /* add     r1,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][1]);
   s.pc=0xf033beu;break;
  case 0xf033beu: /* add     r8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][8]);
   s.pc=0xf033c0u;break;
  case 0xf033c0u: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf033c2u;break;
  case 0xf033c2u: /* move    r0,r15 */
   s.registers[0][15]=s.registers[0][0];
   s.pc=0xf033c4u;break;
  case 0xf033c4u: /* move    r22,r0 */
   s.registers[0][0]=s.registers[0][22];
   s.pc=0xf033c6u;break;
  case 0xf033c6u: /* move    r21,r1 */
   s.registers[0][1]=s.registers[0][21];
   s.pc=0xf033c8u;break;
  case 0xf033c8u: /* imult   r13,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][13]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf033cau;break;
  case 0xf033cau: /* imult   r16,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][16]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf033ccu;break;
  case 0xf033ccu: /* sub     r1,r0 */
   s.registers[0][0]=sub(&s,s.registers[0][0],s.registers[0][1]);
   s.pc=0xf033ceu;break;
  case 0xf033ceu: /* move    r21,r1 */
   s.registers[0][1]=s.registers[0][21];
   s.pc=0xf033d0u;break;
  case 0xf033d0u: /* add     r8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][8]);
   s.pc=0xf033d2u;break;
  case 0xf033d2u: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf033d4u;break;
  case 0xf033d4u: /* imult   r13,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][13]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf033d6u;break;
  case 0xf033d6u: /* move    r0,r13 */
   s.registers[0][13]=s.registers[0][0];
   s.pc=0xf033d8u;break;
  case 0xf033d8u: /* move    r22,r0 */
   s.registers[0][0]=s.registers[0][22];
   s.pc=0xf033dau;break;
  case 0xf033dau: /* imult   r16,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][16]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf033dcu;break;
  case 0xf033dcu: /* add     r1,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][1]);
   s.pc=0xf033deu;break;
  case 0xf033deu: /* add     r8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][8]);
   s.pc=0xf033e0u;break;
  case 0xf033e0u: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf033e2u;break;
  case 0xf033e2u: /* move    r0,r16 */
   s.registers[0][16]=s.registers[0][0];
   s.pc=0xf033e4u;break;
  case 0xf033e4u: /* move    r22,r0 */
   s.registers[0][0]=s.registers[0][22];
   s.pc=0xf033e6u;break;
  case 0xf033e6u: /* move    r21,r1 */
   s.registers[0][1]=s.registers[0][21];
   s.pc=0xf033e8u;break;
  case 0xf033e8u: /* imult   r14,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][14]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf033eau;break;
  case 0xf033eau: /* imult   r17,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][17]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf033ecu;break;
  case 0xf033ecu: /* sub     r1,r0 */
   s.registers[0][0]=sub(&s,s.registers[0][0],s.registers[0][1]);
   s.pc=0xf033eeu;break;
  case 0xf033eeu: /* move    r21,r1 */
   s.registers[0][1]=s.registers[0][21];
   s.pc=0xf033f0u;break;
  case 0xf033f0u: /* add     r8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][8]);
   s.pc=0xf033f2u;break;
  case 0xf033f2u: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf033f4u;break;
  case 0xf033f4u: /* imult   r14,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][14]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf033f6u;break;
  case 0xf033f6u: /* move    r0,r14 */
   s.registers[0][14]=s.registers[0][0];
   s.pc=0xf033f8u;break;
  case 0xf033f8u: /* move    r22,r0 */
   s.registers[0][0]=s.registers[0][22];
   s.pc=0xf033fau;break;
  case 0xf033fau: /* imult   r17,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][17]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf033fcu;break;
  case 0xf033fcu: /* add     r1,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][1]);
   s.pc=0xf033feu;break;
  case 0xf033feu: /* add     r8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][8]);
   s.pc=0xf03400u;break;
  case 0xf03400u: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf03402u;break;
  case 0xf03402u: /* move    r0,r17 */
   s.registers[0][17]=s.registers[0][0];
   s.pc=0xf03404u;break;
  case 0xf03404u: /* movei   $f03480,r2 */
   s.registers[0][2]=0xf03480u;
   s.pc=0xf0340au;break;
  case 0xf0340au: /* cmpq    $0,r6 */
   (void)sub(&s,s.registers[0][6],0x0u);
   s.pc=0xf0340cu;break;
  case 0xf0340cu: /* jump    z,(r2) */
   if(condition(&s,2)){pending=1;target=s.registers[0][2];}
   s.pc=0xf0340eu;break;
  case 0xf0340eu: /* move    r6,r0 */
   s.registers[0][0]=s.registers[0][6];
   s.pc=0xf03410u;break;
  case 0xf03410u: /* move    pc,r27 */
   s.registers[0][27]=0xf03410u;
   s.pc=0xf03412u;break;
  case 0xf03412u: /* jump    (r26) */
   if(condition(&s,0)){pending=1;target=s.registers[0][26];}
   s.pc=0xf03414u;break;
  case 0xf03414u: /* addq    $6,r27 */
   s.registers[0][27]=add(&s,s.registers[0][27],6u);
   s.pc=0xf03416u;break;
  case 0xf03416u: /* move    r0,r21 */
   s.registers[0][21]=s.registers[0][0];
   s.pc=0xf03418u;break;
  case 0xf03418u: /* move    r6,r0 */
   s.registers[0][0]=s.registers[0][6];
   s.pc=0xf0341au;break;
  case 0xf0341au: /* move    pc,r27 */
   s.registers[0][27]=0xf0341au;
   s.pc=0xf0341cu;break;
  case 0xf0341cu: /* jump    (r25) */
   if(condition(&s,0)){pending=1;target=s.registers[0][25];}
   s.pc=0xf0341eu;break;
  case 0xf0341eu: /* addq    $6,r27 */
   s.registers[0][27]=add(&s,s.registers[0][27],6u);
   s.pc=0xf03420u;break;
  case 0xf03420u: /* move    r0,r22 */
   s.registers[0][22]=s.registers[0][0];
   s.pc=0xf03422u;break;
  case 0xf03422u: /* move    r21,r1 */
   s.registers[0][1]=s.registers[0][21];
   s.pc=0xf03424u;break;
  case 0xf03424u: /* imult   r9,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][9]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf03426u;break;
  case 0xf03426u: /* imult   r12,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][12]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf03428u;break;
  case 0xf03428u: /* sub     r1,r0 */
   s.registers[0][0]=sub(&s,s.registers[0][0],s.registers[0][1]);
   s.pc=0xf0342au;break;
  case 0xf0342au: /* move    r21,r1 */
   s.registers[0][1]=s.registers[0][21];
   s.pc=0xf0342cu;break;
  case 0xf0342cu: /* add     r8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][8]);
   s.pc=0xf0342eu;break;
  case 0xf0342eu: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf03430u;break;
  case 0xf03430u: /* imult   r9,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][9]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf03432u;break;
  case 0xf03432u: /* move    r0,r9 */
   s.registers[0][9]=s.registers[0][0];
   s.pc=0xf03434u;break;
  case 0xf03434u: /* move    r22,r0 */
   s.registers[0][0]=s.registers[0][22];
   s.pc=0xf03436u;break;
  case 0xf03436u: /* imult   r12,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][12]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf03438u;break;
  case 0xf03438u: /* add     r1,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][1]);
   s.pc=0xf0343au;break;
  case 0xf0343au: /* add     r8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][8]);
   s.pc=0xf0343cu;break;
  case 0xf0343cu: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf0343eu;break;
  case 0xf0343eu: /* move    r0,r12 */
   s.registers[0][12]=s.registers[0][0];
   s.pc=0xf03440u;break;
  case 0xf03440u: /* move    r22,r0 */
   s.registers[0][0]=s.registers[0][22];
   s.pc=0xf03442u;break;
  case 0xf03442u: /* move    r21,r1 */
   s.registers[0][1]=s.registers[0][21];
   s.pc=0xf03444u;break;
  case 0xf03444u: /* imult   r10,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][10]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf03446u;break;
  case 0xf03446u: /* imult   r13,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][13]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf03448u;break;
  case 0xf03448u: /* sub     r1,r0 */
   s.registers[0][0]=sub(&s,s.registers[0][0],s.registers[0][1]);
   s.pc=0xf0344au;break;
  case 0xf0344au: /* move    r21,r1 */
   s.registers[0][1]=s.registers[0][21];
   s.pc=0xf0344cu;break;
  case 0xf0344cu: /* add     r8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][8]);
   s.pc=0xf0344eu;break;
  case 0xf0344eu: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf03450u;break;
  case 0xf03450u: /* imult   r10,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][10]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf03452u;break;
  case 0xf03452u: /* move    r0,r10 */
   s.registers[0][10]=s.registers[0][0];
   s.pc=0xf03454u;break;
  case 0xf03454u: /* move    r22,r0 */
   s.registers[0][0]=s.registers[0][22];
   s.pc=0xf03456u;break;
  case 0xf03456u: /* imult   r13,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][13]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf03458u;break;
  case 0xf03458u: /* add     r1,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][1]);
   s.pc=0xf0345au;break;
  case 0xf0345au: /* add     r8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][8]);
   s.pc=0xf0345cu;break;
  case 0xf0345cu: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf0345eu;break;
  case 0xf0345eu: /* move    r0,r13 */
   s.registers[0][13]=s.registers[0][0];
   s.pc=0xf03460u;break;
  case 0xf03460u: /* move    r22,r0 */
   s.registers[0][0]=s.registers[0][22];
   s.pc=0xf03462u;break;
  case 0xf03462u: /* move    r21,r1 */
   s.registers[0][1]=s.registers[0][21];
   s.pc=0xf03464u;break;
  case 0xf03464u: /* imult   r11,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][11]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf03466u;break;
  case 0xf03466u: /* imult   r14,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][14]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf03468u;break;
  case 0xf03468u: /* sub     r1,r0 */
   s.registers[0][0]=sub(&s,s.registers[0][0],s.registers[0][1]);
   s.pc=0xf0346au;break;
  case 0xf0346au: /* move    r21,r1 */
   s.registers[0][1]=s.registers[0][21];
   s.pc=0xf0346cu;break;
  case 0xf0346cu: /* add     r8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][8]);
   s.pc=0xf0346eu;break;
  case 0xf0346eu: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf03470u;break;
  case 0xf03470u: /* imult   r11,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][11]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf03472u;break;
  case 0xf03472u: /* move    r0,r11 */
   s.registers[0][11]=s.registers[0][0];
   s.pc=0xf03474u;break;
  case 0xf03474u: /* move    r22,r0 */
   s.registers[0][0]=s.registers[0][22];
   s.pc=0xf03476u;break;
  case 0xf03476u: /* imult   r14,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][14]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf03478u;break;
  case 0xf03478u: /* add     r1,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][1]);
   s.pc=0xf0347au;break;
  case 0xf0347au: /* add     r8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][8]);
   s.pc=0xf0347cu;break;
  case 0xf0347cu: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf0347eu;break;
  case 0xf0347eu: /* move    r0,r14 */
   s.registers[0][14]=s.registers[0][0];
   s.pc=0xf03480u;break;
  case 0xf03480u: /* movei   $f034a8,r2 */
   s.registers[0][2]=0xf034a8u;
   s.pc=0xf03486u;break;
  case 0xf03486u: /* cmpq    $0,r7 */
   (void)sub(&s,s.registers[0][7],0x0u);
   s.pc=0xf03488u;break;
  case 0xf03488u: /* jump    z,(r2) */
   if(condition(&s,2)){pending=1;target=s.registers[0][2];}
   s.pc=0xf0348au;break;
  case 0xf0348au: /* move    r7,r0 */
   s.registers[0][0]=s.registers[0][7];
   s.pc=0xf0348cu;break;
  case 0xf0348cu: /* move    r7,r1 */
   s.registers[0][1]=s.registers[0][7];
   s.pc=0xf0348eu;break;
  case 0xf0348eu: /* move    r7,r3 */
   s.registers[0][3]=s.registers[0][7];
   s.pc=0xf03490u;break;
  case 0xf03490u: /* imult   r15,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][15]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf03492u;break;
  case 0xf03492u: /* imult   r16,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][16]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf03494u;break;
  case 0xf03494u: /* imult   r17,r3 */
   s.registers[0][3]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][3])*(int32_t)sx16(s.registers[0][17]));
   zn(&s,s.registers[0][3]);
   s.pc=0xf03496u;break;
  case 0xf03496u: /* moveta  r0,r0 */
   s.registers[1][0]=s.registers[0][0];
   s.pc=0xf03498u;break;
  case 0xf03498u: /* moveta  r1,r1 */
   s.registers[1][1]=s.registers[0][1];
   s.pc=0xf0349au;break;
  case 0xf0349au: /* moveta  r3,r3 */
   s.registers[1][3]=s.registers[0][3];
   s.pc=0xf0349cu;break;
  case 0xf0349cu: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf0349eu;break;
  case 0xf0349eu: /* sharq   $e,r1 */
   s.c=s.registers[0][1]&1u;s.registers[0][1]=sar(s.registers[0][1],14);zn(&s,s.registers[0][1]);
   s.pc=0xf034a0u;break;
  case 0xf034a0u: /* sharq   $e,r3 */
   s.c=s.registers[0][3]&1u;s.registers[0][3]=sar(s.registers[0][3],14);zn(&s,s.registers[0][3]);
   s.pc=0xf034a2u;break;
  case 0xf034a2u: /* add     r0,r18 */
   s.registers[0][18]=add(&s,s.registers[0][18],s.registers[0][0]);
   s.pc=0xf034a4u;break;
  case 0xf034a4u: /* add     r1,r19 */
   s.registers[0][19]=add(&s,s.registers[0][19],s.registers[0][1]);
   s.pc=0xf034a6u;break;
  case 0xf034a6u: /* add     r3,r20 */
   s.registers[0][20]=add(&s,s.registers[0][20],s.registers[0][3]);
   s.pc=0xf034a8u;break;
  case 0xf034a8u: /* movei   $f0320c,r3 */
   s.registers[0][3]=0xf0320cu;
   s.pc=0xf034aeu;break;
case 0xf034aeu: /* load    (r3),r0 */
 CHECK(rd32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],&v));s.registers[0][0]=v;
 s.pc=0xf034b0u;break;
  case 0xf034b0u: /* storew  r9,(r0) */
   CHECK(wr16(bus,&s,s.registers[0][0],s.registers[0][9]));
   s.pc=0xf034b2u;break;
  case 0xf034b2u: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf034b4u;break;
  case 0xf034b4u: /* storew  r10,(r0) */
   CHECK(wr16(bus,&s,s.registers[0][0],s.registers[0][10]));
   s.pc=0xf034b6u;break;
  case 0xf034b6u: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf034b8u;break;
  case 0xf034b8u: /* storew  r11,(r0) */
   CHECK(wr16(bus,&s,s.registers[0][0],s.registers[0][11]));
   s.pc=0xf034bau;break;
  case 0xf034bau: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf034bcu;break;
  case 0xf034bcu: /* storew  r12,(r0) */
   CHECK(wr16(bus,&s,s.registers[0][0],s.registers[0][12]));
   s.pc=0xf034beu;break;
  case 0xf034beu: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf034c0u;break;
  case 0xf034c0u: /* storew  r13,(r0) */
   CHECK(wr16(bus,&s,s.registers[0][0],s.registers[0][13]));
   s.pc=0xf034c2u;break;
  case 0xf034c2u: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf034c4u;break;
  case 0xf034c4u: /* storew  r14,(r0) */
   CHECK(wr16(bus,&s,s.registers[0][0],s.registers[0][14]));
   s.pc=0xf034c6u;break;
  case 0xf034c6u: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf034c8u;break;
  case 0xf034c8u: /* storew  r15,(r0) */
   CHECK(wr16(bus,&s,s.registers[0][0],s.registers[0][15]));
   s.pc=0xf034cau;break;
  case 0xf034cau: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf034ccu;break;
  case 0xf034ccu: /* storew  r16,(r0) */
   CHECK(wr16(bus,&s,s.registers[0][0],s.registers[0][16]));
   s.pc=0xf034ceu;break;
  case 0xf034ceu: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf034d0u;break;
  case 0xf034d0u: /* storew  r17,(r0) */
   CHECK(wr16(bus,&s,s.registers[0][0],s.registers[0][17]));
   s.pc=0xf034d2u;break;
  case 0xf034d2u: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf034d4u;break;
  case 0xf034d4u: /* storew  r18,(r0) */
   CHECK(wr16(bus,&s,s.registers[0][0],s.registers[0][18]));
   s.pc=0xf034d6u;break;
  case 0xf034d6u: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf034d8u;break;
  case 0xf034d8u: /* storew  r19,(r0) */
   CHECK(wr16(bus,&s,s.registers[0][0],s.registers[0][19]));
   s.pc=0xf034dau;break;
  case 0xf034dau: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf034dcu;break;
  case 0xf034dcu: /* storew  r20,(r0) */
   CHECK(wr16(bus,&s,s.registers[0][0],s.registers[0][20]));
   s.pc=0xf034deu;break;
  case 0xf034deu: /* addq    $4,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],4u);
   s.pc=0xf034e0u;break;
case 0xf034e0u: /* movefa  r0,r1 */
 s.registers[0][1]=s.registers[1][0];
 s.pc=0xf034e2u;break;
  case 0xf034e2u: /* storew  r1,(r0) */
   CHECK(wr16(bus,&s,s.registers[0][0],s.registers[0][1]));
   s.pc=0xf034e4u;break;
  case 0xf034e4u: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf034e6u;break;
case 0xf034e6u: /* movefa  r1,r1 */
 s.registers[0][1]=s.registers[1][1];
 s.pc=0xf034e8u;break;
  case 0xf034e8u: /* storew  r1,(r0) */
   CHECK(wr16(bus,&s,s.registers[0][0],s.registers[0][1]));
   s.pc=0xf034eau;break;
  case 0xf034eau: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf034ecu;break;
case 0xf034ecu: /* movefa  r3,r1 */
 s.registers[0][1]=s.registers[1][3];
 s.pc=0xf034eeu;break;
  case 0xf034eeu: /* storew  r1,(r0) */
   CHECK(wr16(bus,&s,s.registers[0][0],s.registers[0][1]));
   s.pc=0xf034f0u;break;
  case 0xf034f0u: /* movei   $f031be,r2 */
   s.registers[0][2]=0xf031beu;
   s.pc=0xf034f6u;break;
  case 0xf034f6u: /* jump    (r2) */
   if(condition(&s,0)){pending=1;target=s.registers[0][2];}
   s.pc=0xf034f8u;break;
  case 0xf034f8u: /* add     r23,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][23]);
   s.pc=0xf034fau;break;
  case 0xf034fau: /* shlq    $18,r0 */
   s.c=s.registers[0][0]>>31;s.registers[0][0]=s.registers[0][0]<<24;zn(&s,s.registers[0][0]);
   s.pc=0xf034fcu;break;
  case 0xf034fcu: /* move    r24,r3 */
   s.registers[0][3]=s.registers[0][24];
   s.pc=0xf034feu;break;
  case 0xf034feu: /* jr      n,00F03516 */
   if(condition(&s,24)){pending=1;target=0xf03516u;}
   s.pc=0xf03500u;break;
  case 0xf03500u: /* shrq    $18,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=s.registers[0][0]>>24;zn(&s,s.registers[0][0]);
   s.pc=0xf03502u;break;
  case 0xf03502u: /* cmp     r0,r23 */
   (void)sub(&s,s.registers[0][23],s.registers[0][0]);
   s.pc=0xf03504u;break;
  case 0xf03504u: /* jr      nn,00F0350E */
   if(condition(&s,20)){pending=1;target=0xf0350eu;}
   s.pc=0xf03506u;break;
  case 0xf03506u: /* move    r23,r1 */
   s.registers[0][1]=s.registers[0][23];
   s.pc=0xf03508u;break;
  case 0xf03508u: /* shlq    $1,r1 */
   s.c=s.registers[0][1]>>31;s.registers[0][1]=s.registers[0][1]<<1;zn(&s,s.registers[0][1]);
   s.pc=0xf0350au;break;
  case 0xf0350au: /* sub     r0,r1 */
   s.registers[0][1]=sub(&s,s.registers[0][1],s.registers[0][0]);
   s.pc=0xf0350cu;break;
  case 0xf0350cu: /* move    r1,r0 */
   s.registers[0][0]=s.registers[0][1];
   s.pc=0xf0350eu;break;
  case 0xf0350eu: /* shlq    $2,r0 */
   s.c=s.registers[0][0]>>31;s.registers[0][0]=s.registers[0][0]<<2;zn(&s,s.registers[0][0]);
   s.pc=0xf03510u;break;
  case 0xf03510u: /* add     r0,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],s.registers[0][0]);
   s.pc=0xf03512u;break;
  case 0xf03512u: /* jump    (r27) */
   if(condition(&s,0)){pending=1;target=s.registers[0][27];}
   s.pc=0xf03514u;break;
case 0xf03514u: /* load    (r3),r0 */
 CHECK(rd32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],&v));s.registers[0][0]=v;
 s.pc=0xf03516u;break;
  case 0xf03516u: /* bclr    $7,r0 */
   s.registers[0][0]&=~(1u<<7);
   zn(&s,s.registers[0][0]);
   s.pc=0xf03518u;break;
  case 0xf03518u: /* cmp     r0,r23 */
   (void)sub(&s,s.registers[0][23],s.registers[0][0]);
   s.pc=0xf0351au;break;
  case 0xf0351au: /* jr      nn,00F03524 */
   if(condition(&s,20)){pending=1;target=0xf03524u;}
   s.pc=0xf0351cu;break;
  case 0xf0351cu: /* move    r23,r1 */
   s.registers[0][1]=s.registers[0][23];
   s.pc=0xf0351eu;break;
  case 0xf0351eu: /* shlq    $1,r1 */
   s.c=s.registers[0][1]>>31;s.registers[0][1]=s.registers[0][1]<<1;zn(&s,s.registers[0][1]);
   s.pc=0xf03520u;break;
  case 0xf03520u: /* sub     r0,r1 */
   s.registers[0][1]=sub(&s,s.registers[0][1],s.registers[0][0]);
   s.pc=0xf03522u;break;
  case 0xf03522u: /* move    r1,r0 */
   s.registers[0][0]=s.registers[0][1];
   s.pc=0xf03524u;break;
  case 0xf03524u: /* shlq    $2,r0 */
   s.c=s.registers[0][0]>>31;s.registers[0][0]=s.registers[0][0]<<2;zn(&s,s.registers[0][0]);
   s.pc=0xf03526u;break;
  case 0xf03526u: /* add     r0,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],s.registers[0][0]);
   s.pc=0xf03528u;break;
case 0xf03528u: /* load    (r3),r0 */
 CHECK(rd32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],&v));s.registers[0][0]=v;
 s.pc=0xf0352au;break;
  case 0xf0352au: /* jump    (r27) */
   if(condition(&s,0)){pending=1;target=s.registers[0][27];}
   s.pc=0xf0352cu;break;
  case 0xf0352cu: /* neg     r0 */
   s.registers[0][0]=sub(&s,0,s.registers[0][0]);
   s.pc=0xf0352eu;break;
default:return BIWN_MOVEMENT_FULLGPU_BAD_PC;
}if(delayed){if(pending)return BIWN_MOVEMENT_FULLGPU_BAD_DELAY;s.pc=resume;}if(s.pc==0xf031beu){*state=s;return 0;}}return BIWN_MOVEMENT_FULLGPU_WORK_LIMIT;}
