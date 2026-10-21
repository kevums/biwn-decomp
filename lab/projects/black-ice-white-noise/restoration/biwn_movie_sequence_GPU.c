/* Generated from the pinned GPU4D80 overlay by
 * scripts/generate_biwn_movie_sequence_GPU.py. Analyst static recompilation,
 * not recovered original source. Integer primitive behavior is checked
 * against the pinned Virtual Jaguar core; no core runs on the C side. */
#include "biwn_movie_sequence_GPU.h"
#include <string.h>
static void zn(struct biwn_movie_sequence_GPU_state *s,uint32_t v){s->z=v==0;s->n=v>>31;}
static uint32_t add(struct biwn_movie_sequence_GPU_state *s,uint32_t a,uint32_t b){uint32_t v=a+b;s->c=b>~a;zn(s,v);return v;}
static uint32_t sub(struct biwn_movie_sequence_GPU_state *s,uint32_t a,uint32_t b){uint32_t v=a-b;s->c=b>a;zn(s,v);return v;}
static int condition(struct biwn_movie_sequence_GPU_state *s,unsigned code){unsigned flags=s->z|(s->c<<1)|(s->n<<2);return !((code&1u)&&(flags&1u))&&!((code&2u)&&!(flags&1u))&&!((code&4u)&&(flags&(2u<<(code>>4))))&&!((code&8u)&&!(flags&(2u<<(code>>4))));}
static uint32_t be32(const uint8_t *p){return((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
static void put32(uint8_t *p,uint32_t v){p[0]=(uint8_t)(v>>24);p[1]=(uint8_t)(v>>16);p[2]=(uint8_t)(v>>8);p[3]=(uint8_t)v;}
static int local(uint32_t a){return a>=0xf03000u&&a<=0xf03ffcu;}
static int rd32(struct biwn_movie_sequence_GPU_bus *bus,struct biwn_movie_sequence_GPU_state *s,uint32_t a,uint32_t *v){if(local(a)){*v=be32(s->local_RAM+a-0xf03000u);return 0;}if(a==0xf02114u){*v=s->control;return 0;}if(a==0xf02104u){*v=s->matrix_control;return 0;}if(a==0xf02108u){*v=s->matrix_pointer;return 0;}return bus->read32(bus->context,a,v)?2:0;}
static int rd16(struct biwn_movie_sequence_GPU_bus *bus,struct biwn_movie_sequence_GPU_state *s,uint32_t a,uint32_t *v){uint16_t h;if(a>=0xf03000u&&a<=0xf03ffeu){unsigned p=a-0xf03000u;*v=((uint32_t)s->local_RAM[p]<<8)|s->local_RAM[p+1];return 0;}if(bus->read16(bus->context,a,&h))return 2;*v=h;return 0;}
static int loadw(struct biwn_movie_sequence_GPU_bus *bus,struct biwn_movie_sequence_GPU_state *s,uint32_t a,uint32_t *v){if(a>=0xf03000u&&a<=0xf03fffu)return rd32(bus,s,a&~3u,v);return rd16(bus,s,a,v);}
static int wr32(struct biwn_movie_sequence_GPU_bus *bus,struct biwn_movie_sequence_GPU_state *s,uint32_t a,uint32_t v){if(local(a)){put32(s->local_RAM+a-0xf03000u,v);return 0;}if(a==0xf02114u){s->control=(s->control&0xf7c0u)|(v&~0xf7c6u);return bus->write32(bus->context,a,v)?2:0;}if(a==0xf02104u){s->matrix_control=v;return 0;}if(a==0xf02108u){s->matrix_pointer=v&~3u;return 0;}return bus->write32(bus->context,a,v)?2:0;}
static int rd8(struct biwn_movie_sequence_GPU_bus *b,struct biwn_movie_sequence_GPU_state *s,uint32_t a,uint32_t *v){uint8_t x;if(a>=0xf03000u&&a<=0xf03fffu)return rd32(b,s,a&~3u,v);if(b->read8(b->context,a,&x))return 2;*v=x;return 0;}
#define CHECK(e) do{int status=(e);if(status)return(enum biwn_movie_sequence_GPU_status)status;}while(0)
enum biwn_movie_sequence_GPU_status biwn_movie_sequence_GPU_run(struct biwn_movie_sequence_GPU_bus *bus,struct biwn_movie_sequence_GPU_state *state,uint32_t budget){struct biwn_movie_sequence_GPU_state s;uint32_t v,target=0;unsigned pending=0;if(!bus||!state||!budget||!bus->read8||!bus->read16||!bus->read32||!bus->write32||state->active_bank||state->z>1||state->c>1||state->n>1)return 1;s=*state;while(budget--){unsigned delayed=pending;uint32_t resume=target;pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){
  case 0xf032c8u: /* movei   $f039f0,r0 */
   s.registers[0][0]=0xf039f0u;
   s.pc=0xf032ceu;break;
case 0xf032ceu: /* load    (r0),r1 */
 CHECK(rd32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],&v));s.registers[0][1]=v;
 s.pc=0xf032d0u;break;
  case 0xf032d0u: /* or      r1,r1 */
   s.registers[0][1]|=s.registers[0][1];
   zn(&s,s.registers[0][1]);
   s.pc=0xf032d2u;break;
  case 0xf032d2u: /* jr      z,00F032C8 */
   if(condition(&s,2)){pending=1;target=0xf032c8u;}
   s.pc=0xf032d4u;break;
  case 0xf032d4u: /* nop */
   s.pc=0xf032d6u;break;
  case 0xf032d6u: /* moveq   0,r1 */
   s.registers[0][1]=0u;
   s.pc=0xf032d8u;break;
  case 0xf032d8u: /* store   r1,(r0) */
   CHECK(wr32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],s.registers[0][1]));
   s.pc=0xf032dau;break;
  case 0xf032dau: /* movei   $f039f4,r0 */
   s.registers[0][0]=0xf039f4u;
   s.pc=0xf032e0u;break;
case 0xf032e0u: /* load    (r0),r1 */
 CHECK(rd32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],&v));s.registers[0][1]=v;
 s.pc=0xf032e2u;break;
  case 0xf032e2u: /* addq    $4,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],4u);
   s.pc=0xf032e4u;break;
  case 0xf032e4u: /* movei   $f03500,r2 */
   s.registers[0][2]=0xf03500u;
   s.pc=0xf032eau;break;
  case 0xf032eau: /* cmpq    $3,r1 */
   (void)sub(&s,s.registers[0][1],0x3u);
   s.pc=0xf032ecu;break;
  case 0xf032ecu: /* jump    nn,(r2) */
   if(condition(&s,20)){pending=1;target=s.registers[0][2];}
   s.pc=0xf032eeu;break;
  case 0xf032eeu: /* nop */
   s.pc=0xf032f0u;break;
case 0xf032f0u: /* load    (r0),r16 */
 CHECK(rd32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],&v));s.registers[0][16]=v;
 s.pc=0xf032f2u;break;
  case 0xf032f2u: /* addq    $4,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],4u);
   s.pc=0xf032f4u;break;
case 0xf032f4u: /* load    (r0),r20 */
 CHECK(rd32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],&v));s.registers[0][20]=v;
 s.pc=0xf032f6u;break;
  case 0xf032f6u: /* addq    $4,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],4u);
   s.pc=0xf032f8u;break;
case 0xf032f8u: /* load    (r0),r5 */
 CHECK(rd32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],&v));s.registers[0][5]=v;
 s.pc=0xf032fau;break;
  case 0xf032fau: /* addq    $4,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],4u);
   s.pc=0xf032fcu;break;
case 0xf032fcu: /* load    (r0),r6 */
 CHECK(rd32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],&v));s.registers[0][6]=v;
 s.pc=0xf032feu;break;
  case 0xf032feu: /* addq    $4,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],4u);
   s.pc=0xf03300u;break;
case 0xf03300u: /* load    (r0),r10 */
 CHECK(rd32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],&v));s.registers[0][10]=v;
 s.pc=0xf03302u;break;
  case 0xf03302u: /* addq    $4,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],4u);
   s.pc=0xf03304u;break;
case 0xf03304u: /* load    (r0),r11 */
 CHECK(rd32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],&v));s.registers[0][11]=v;
 s.pc=0xf03306u;break;
  case 0xf03306u: /* addq    $4,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],4u);
   s.pc=0xf03308u;break;
case 0xf03308u: /* load    (r0),r4 */
 CHECK(rd32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],&v));s.registers[0][4]=v;
 s.pc=0xf0330au;break;
  case 0xf0330au: /* move    r16,r17 */
   s.registers[0][17]=s.registers[0][16];
   s.pc=0xf0330cu;break;
  case 0xf0330cu: /* add     r20,r17 */
   s.registers[0][17]=add(&s,s.registers[0][17],s.registers[0][20]);
   s.pc=0xf0330eu;break;
  case 0xf0330eu: /* move    r17,r18 */
   s.registers[0][18]=s.registers[0][17];
   s.pc=0xf03310u;break;
  case 0xf03310u: /* add     r20,r18 */
   s.registers[0][18]=add(&s,s.registers[0][18],s.registers[0][20]);
   s.pc=0xf03312u;break;
  case 0xf03312u: /* move    r18,r19 */
   s.registers[0][19]=s.registers[0][18];
   s.pc=0xf03314u;break;
  case 0xf03314u: /* add     r20,r19 */
   s.registers[0][19]=add(&s,s.registers[0][19],s.registers[0][20]);
   s.pc=0xf03316u;break;
  case 0xf03316u: /* shlq    $2,r20 */
   s.c=s.registers[0][20]>>31;s.registers[0][20]=s.registers[0][20]<<2;zn(&s,s.registers[0][20]);
   s.pc=0xf03318u;break;
  case 0xf03318u: /* sub     r5,r20 */
   s.registers[0][20]=sub(&s,s.registers[0][20],s.registers[0][5]);
   s.pc=0xf0331au;break;
  case 0xf0331au: /* sub     r5,r20 */
   s.registers[0][20]=sub(&s,s.registers[0][20],s.registers[0][5]);
   s.pc=0xf0331cu;break;
  case 0xf0331cu: /* movei   $f033ea,r21 */
   s.registers[0][21]=0xf033eau;
   s.pc=0xf03322u;break;
  case 0xf03322u: /* movei   $f03444,r23 */
   s.registers[0][23]=0xf03444u;
   s.pc=0xf03328u;break;
  case 0xf03328u: /* movei   $f0347c,r24 */
   s.registers[0][24]=0xf0347cu;
   s.pc=0xf0332eu;break;
  case 0xf0332eu: /* movei   $f034d6,r25 */
   s.registers[0][25]=0xf034d6u;
   s.pc=0xf03334u;break;
  case 0xf03334u: /* cmpq    $0,r1 */
   (void)sub(&s,s.registers[0][1],0x0u);
   s.pc=0xf03336u;break;
  case 0xf03336u: /* jr      z,00F03350 */
   if(condition(&s,2)){pending=1;target=0xf03350u;}
   s.pc=0xf03338u;break;
  case 0xf03338u: /* nop */
   s.pc=0xf0333au;break;
  case 0xf0333au: /* movei   $f03380,r0 */
   s.registers[0][0]=0xf03380u;
   s.pc=0xf03340u;break;
  case 0xf03340u: /* cmpq    $1,r1 */
   (void)sub(&s,s.registers[0][1],0x1u);
   s.pc=0xf03342u;break;
  case 0xf03342u: /* jump    z,(r0) */
   if(condition(&s,2)){pending=1;target=s.registers[0][0];}
   s.pc=0xf03344u;break;
  case 0xf03344u: /* nop */
   s.pc=0xf03346u;break;
  case 0xf03350u: /* movei   $f03364,r22 */
   s.registers[0][22]=0xf03364u;
   s.pc=0xf03356u;break;
  case 0xf03356u: /* movei   $f03376,r26 */
   s.registers[0][26]=0xf03376u;
   s.pc=0xf0335cu;break;
  case 0xf0335cu: /* movei   $f0336c,r27 */
   s.registers[0][27]=0xf0336cu;
   s.pc=0xf03362u;break;
  case 0xf03362u: /* moveq   0,r9 */
   s.registers[0][9]=0u;
   s.pc=0xf03364u;break;
  case 0xf03364u: /* move    r5,r7 */
   s.registers[0][7]=s.registers[0][5];
   s.pc=0xf03366u;break;
  case 0xf03366u: /* subq    $1,r9 */
   s.registers[0][9]=sub(&s,s.registers[0][9],1u);
   s.pc=0xf03368u;break;
  case 0xf03368u: /* jump    n,(r21) */
   if(condition(&s,24)){pending=1;target=s.registers[0][21];}
   s.pc=0xf0336au;break;
  case 0xf0336au: /* moveq   0,r12 */
   s.registers[0][12]=0u;
   s.pc=0xf0336cu;break;
  case 0xf0336cu: /* add     r8,r8 */
   s.registers[0][8]=add(&s,s.registers[0][8],s.registers[0][8]);
   s.pc=0xf0336eu;break;
  case 0xf0336eu: /* jump    nc,(r23) */
   if(condition(&s,4)){pending=1;target=s.registers[0][23];}
   s.pc=0xf03370u;break;
  case 0xf03370u: /* nop */
   s.pc=0xf03372u;break;
  case 0xf03372u: /* jump    (r24) */
   if(condition(&s,0)){pending=1;target=s.registers[0][24];}
   s.pc=0xf03374u;break;
  case 0xf03374u: /* nop */
   s.pc=0xf03376u;break;
  case 0xf03376u: /* subq    $4,r7 */
   s.registers[0][7]=sub(&s,s.registers[0][7],4u);
   s.pc=0xf03378u;break;
  case 0xf03378u: /* jump    z,(r25) */
   if(condition(&s,2)){pending=1;target=s.registers[0][25];}
   s.pc=0xf0337au;break;
  case 0xf0337au: /* nop */
   s.pc=0xf0337cu;break;
  case 0xf0337cu: /* jr      00F03366 */
   if(condition(&s,0)){pending=1;target=0xf03366u;}
   s.pc=0xf0337eu;break;
  case 0xf0337eu: /* nop */
   s.pc=0xf03380u;break;
  case 0xf03380u: /* movei   $f03394,r22 */
   s.registers[0][22]=0xf03394u;
   s.pc=0xf03386u;break;
  case 0xf03386u: /* movei   $f033be,r26 */
   s.registers[0][26]=0xf033beu;
   s.pc=0xf0338cu;break;
  case 0xf0338cu: /* movei   $f0339c,r27 */
   s.registers[0][27]=0xf0339cu;
   s.pc=0xf03392u;break;
  case 0xf03392u: /* moveq   0,r9 */
   s.registers[0][9]=0u;
   s.pc=0xf03394u;break;
  case 0xf03394u: /* move    r5,r7 */
   s.registers[0][7]=s.registers[0][5];
   s.pc=0xf03396u;break;
  case 0xf03396u: /* subq    $1,r9 */
   s.registers[0][9]=sub(&s,s.registers[0][9],1u);
   s.pc=0xf03398u;break;
  case 0xf03398u: /* jump    n,(r21) */
   if(condition(&s,24)){pending=1;target=s.registers[0][21];}
   s.pc=0xf0339au;break;
  case 0xf0339au: /* moveq   0,r12 */
   s.registers[0][12]=0u;
   s.pc=0xf0339cu;break;
  case 0xf0339cu: /* add     r8,r8 */
   s.registers[0][8]=add(&s,s.registers[0][8],s.registers[0][8]);
   s.pc=0xf0339eu;break;
  case 0xf0339eu: /* jr      c,00F033AE */
   if(condition(&s,8)){pending=1;target=0xf033aeu;}
   s.pc=0xf033a0u;break;
  case 0xf033a0u: /* nop */
   s.pc=0xf033a2u;break;
  case 0xf033a2u: /* addq    $8,r16 */
   s.registers[0][16]=add(&s,s.registers[0][16],8u);
   s.pc=0xf033a4u;break;
  case 0xf033a4u: /* addq    $8,r17 */
   s.registers[0][17]=add(&s,s.registers[0][17],8u);
   s.pc=0xf033a6u;break;
  case 0xf033a6u: /* addq    $8,r18 */
   s.registers[0][18]=add(&s,s.registers[0][18],8u);
   s.pc=0xf033a8u;break;
  case 0xf033a8u: /* addq    $8,r19 */
   s.registers[0][19]=add(&s,s.registers[0][19],8u);
   s.pc=0xf033aau;break;
  case 0xf033aau: /* jr      00F033BE */
   if(condition(&s,0)){pending=1;target=0xf033beu;}
   s.pc=0xf033acu;break;
  case 0xf033acu: /* nop */
   s.pc=0xf033aeu;break;
  case 0xf033aeu: /* subq    $1,r9 */
   s.registers[0][9]=sub(&s,s.registers[0][9],1u);
   s.pc=0xf033b0u;break;
  case 0xf033b0u: /* jump    n,(r21) */
   if(condition(&s,24)){pending=1;target=s.registers[0][21];}
   s.pc=0xf033b2u;break;
  case 0xf033b2u: /* moveq   1,r12 */
   s.registers[0][12]=1u;
   s.pc=0xf033b4u;break;
  case 0xf033b4u: /* add     r8,r8 */
   s.registers[0][8]=add(&s,s.registers[0][8],s.registers[0][8]);
   s.pc=0xf033b6u;break;
  case 0xf033b6u: /* jump    nc,(r23) */
   if(condition(&s,4)){pending=1;target=s.registers[0][23];}
   s.pc=0xf033b8u;break;
  case 0xf033b8u: /* nop */
   s.pc=0xf033bau;break;
  case 0xf033bau: /* jump    (r24) */
   if(condition(&s,0)){pending=1;target=s.registers[0][24];}
   s.pc=0xf033bcu;break;
  case 0xf033bcu: /* nop */
   s.pc=0xf033beu;break;
  case 0xf033beu: /* movei   $f03396,r0 */
   s.registers[0][0]=0xf03396u;
   s.pc=0xf033c4u;break;
  case 0xf033c4u: /* subq    $4,r7 */
   s.registers[0][7]=sub(&s,s.registers[0][7],4u);
   s.pc=0xf033c6u;break;
  case 0xf033c6u: /* jump    z,(r25) */
   if(condition(&s,2)){pending=1;target=s.registers[0][25];}
   s.pc=0xf033c8u;break;
  case 0xf033c8u: /* nop */
   s.pc=0xf033cau;break;
  case 0xf033cau: /* jump    (r0) */
   if(condition(&s,0)){pending=1;target=s.registers[0][0];}
   s.pc=0xf033ccu;break;
  case 0xf033ccu: /* nop */
   s.pc=0xf033ceu;break;
  case 0xf033eau: /* moveq   3,r0 */
   s.registers[0][0]=3u;
   s.pc=0xf033ecu;break;
  case 0xf033ecu: /* movei   $f03434,r14 */
   s.registers[0][14]=0xf03434u;
   s.pc=0xf033f2u;break;
  case 0xf033f2u: /* and     r4,r0 */
   s.registers[0][0]&=s.registers[0][4];
   zn(&s,s.registers[0][0]);
   s.pc=0xf033f4u;break;
  case 0xf033f4u: /* shlq    $2,r0 */
   s.c=s.registers[0][0]>>31;s.registers[0][0]=s.registers[0][0]<<2;zn(&s,s.registers[0][0]);
   s.pc=0xf033f6u;break;
case 0xf033f6u: /* load    (r14+r0),r1 */
 {uint32_t a=s.registers[0][14]+s.registers[0][0];CHECK(rd32(bus,&s,local(a)?(a&~3u):a,&v));s.registers[0][1]=v;}
 s.pc=0xf033f8u;break;
  case 0xf033f8u: /* jump    (r1) */
   if(condition(&s,0)){pending=1;target=s.registers[0][1];}
   s.pc=0xf033fau;break;
  case 0xf033fau: /* nop */
   s.pc=0xf033fcu;break;
  case 0xf03412u: /* loadw   (r4),r8 */
   CHECK(loadw(bus,&s,s.registers[0][4],&v));s.registers[0][8]=v;
   s.pc=0xf03414u;break;
  case 0xf03414u: /* addq    $2,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],2u);
   s.pc=0xf03416u;break;
  case 0xf03416u: /* loadw   (r4),r0 */
   CHECK(loadw(bus,&s,s.registers[0][4],&v));s.registers[0][0]=v;
   s.pc=0xf03418u;break;
  case 0xf03418u: /* addq    $2,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],2u);
   s.pc=0xf0341au;break;
  case 0xf0341au: /* shlq    $10,r8 */
   s.c=s.registers[0][8]>>31;s.registers[0][8]=s.registers[0][8]<<16;zn(&s,s.registers[0][8]);
   s.pc=0xf0341cu;break;
  case 0xf0341cu: /* jr      00F03424 */
   if(condition(&s,0)){pending=1;target=0xf03424u;}
   s.pc=0xf0341eu;break;
  case 0xf0341eu: /* or      r0,r8 */
   s.registers[0][8]|=s.registers[0][0];
   zn(&s,s.registers[0][8]);
   s.pc=0xf03420u;break;
  case 0xf03424u: /* or      r12,r12 */
   s.registers[0][12]|=s.registers[0][12];
   zn(&s,s.registers[0][12]);
   s.pc=0xf03426u;break;
  case 0xf03426u: /* jump    z,(r27) */
   if(condition(&s,2)){pending=1;target=s.registers[0][27];}
   s.pc=0xf03428u;break;
  case 0xf03428u: /* moveq   31,r9 */
   s.registers[0][9]=31u;
   s.pc=0xf0342au;break;
  case 0xf0342au: /* movei   $f033b4,r0 */
   s.registers[0][0]=0xf033b4u;
   s.pc=0xf03430u;break;
  case 0xf03430u: /* jump    (r0) */
   if(condition(&s,0)){pending=1;target=s.registers[0][0];}
   s.pc=0xf03432u;break;
  case 0xf03432u: /* nop */
   s.pc=0xf03434u;break;
case 0xf0347cu: /* loadb   (r4),r12 */
 CHECK(rd8(bus,&s,s.registers[0][4],&v));s.registers[0][12]=v;
 s.pc=0xf0347eu;break;
  case 0xf0347eu: /* addq    $1,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],1u);
   s.pc=0xf03480u;break;
case 0xf03480u: /* loadb   (r4),r13 */
 CHECK(rd8(bus,&s,s.registers[0][4],&v));s.registers[0][13]=v;
 s.pc=0xf03482u;break;
  case 0xf03482u: /* addq    $1,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],1u);
   s.pc=0xf03484u;break;
case 0xf03484u: /* loadb   (r4),r14 */
 CHECK(rd8(bus,&s,s.registers[0][4],&v));s.registers[0][14]=v;
 s.pc=0xf03486u;break;
  case 0xf03486u: /* addq    $1,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],1u);
   s.pc=0xf03488u;break;
case 0xf03488u: /* loadb   (r4),r15 */
 CHECK(rd8(bus,&s,s.registers[0][4],&v));s.registers[0][15]=v;
 s.pc=0xf0348au;break;
  case 0xf0348au: /* addq    $1,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],1u);
   s.pc=0xf0348cu;break;
  case 0xf0348cu: /* shlq    $3,r12 */
   s.c=s.registers[0][12]>>31;s.registers[0][12]=s.registers[0][12]<<3;zn(&s,s.registers[0][12]);
   s.pc=0xf0348eu;break;
  case 0xf0348eu: /* shlq    $3,r13 */
   s.c=s.registers[0][13]>>31;s.registers[0][13]=s.registers[0][13]<<3;zn(&s,s.registers[0][13]);
   s.pc=0xf03490u;break;
  case 0xf03490u: /* add     r10,r12 */
   s.registers[0][12]=add(&s,s.registers[0][12],s.registers[0][10]);
   s.pc=0xf03492u;break;
  case 0xf03492u: /* add     r10,r13 */
   s.registers[0][13]=add(&s,s.registers[0][13],s.registers[0][10]);
   s.pc=0xf03494u;break;
  case 0xf03494u: /* shlq    $3,r14 */
   s.c=s.registers[0][14]>>31;s.registers[0][14]=s.registers[0][14]<<3;zn(&s,s.registers[0][14]);
   s.pc=0xf03496u;break;
  case 0xf03496u: /* shlq    $3,r15 */
   s.c=s.registers[0][15]>>31;s.registers[0][15]=s.registers[0][15]<<3;zn(&s,s.registers[0][15]);
   s.pc=0xf03498u;break;
  case 0xf03498u: /* add     r10,r14 */
   s.registers[0][14]=add(&s,s.registers[0][14],s.registers[0][10]);
   s.pc=0xf0349au;break;
  case 0xf0349au: /* add     r10,r15 */
   s.registers[0][15]=add(&s,s.registers[0][15],s.registers[0][10]);
   s.pc=0xf0349cu;break;
case 0xf0349cu: /* load    (r12),r0 */
 CHECK(rd32(bus,&s,local(s.registers[0][12])?(s.registers[0][12]&~3u):s.registers[0][12],&v));s.registers[0][0]=v;
 s.pc=0xf0349eu;break;
  case 0xf0349eu: /* addq    $4,r12 */
   s.registers[0][12]=add(&s,s.registers[0][12],4u);
   s.pc=0xf034a0u;break;
case 0xf034a0u: /* load    (r12),r1 */
 CHECK(rd32(bus,&s,local(s.registers[0][12])?(s.registers[0][12]&~3u):s.registers[0][12],&v));s.registers[0][1]=v;
 s.pc=0xf034a2u;break;
case 0xf034a2u: /* load    (r13),r2 */
 CHECK(rd32(bus,&s,local(s.registers[0][13])?(s.registers[0][13]&~3u):s.registers[0][13],&v));s.registers[0][2]=v;
 s.pc=0xf034a4u;break;
  case 0xf034a4u: /* addq    $4,r13 */
   s.registers[0][13]=add(&s,s.registers[0][13],4u);
   s.pc=0xf034a6u;break;
case 0xf034a6u: /* load    (r13),r3 */
 CHECK(rd32(bus,&s,local(s.registers[0][13])?(s.registers[0][13]&~3u):s.registers[0][13],&v));s.registers[0][3]=v;
 s.pc=0xf034a8u;break;
  case 0xf034a8u: /* store   r0,(r16) */
   CHECK(wr32(bus,&s,local(s.registers[0][16])?(s.registers[0][16]&~3u):s.registers[0][16],s.registers[0][0]));
   s.pc=0xf034aau;break;
  case 0xf034aau: /* addq    $4,r16 */
   s.registers[0][16]=add(&s,s.registers[0][16],4u);
   s.pc=0xf034acu;break;
  case 0xf034acu: /* store   r2,(r16) */
   CHECK(wr32(bus,&s,local(s.registers[0][16])?(s.registers[0][16]&~3u):s.registers[0][16],s.registers[0][2]));
   s.pc=0xf034aeu;break;
  case 0xf034aeu: /* addq    $4,r16 */
   s.registers[0][16]=add(&s,s.registers[0][16],4u);
   s.pc=0xf034b0u;break;
  case 0xf034b0u: /* store   r1,(r17) */
   CHECK(wr32(bus,&s,local(s.registers[0][17])?(s.registers[0][17]&~3u):s.registers[0][17],s.registers[0][1]));
   s.pc=0xf034b2u;break;
  case 0xf034b2u: /* addq    $4,r17 */
   s.registers[0][17]=add(&s,s.registers[0][17],4u);
   s.pc=0xf034b4u;break;
  case 0xf034b4u: /* store   r3,(r17) */
   CHECK(wr32(bus,&s,local(s.registers[0][17])?(s.registers[0][17]&~3u):s.registers[0][17],s.registers[0][3]));
   s.pc=0xf034b6u;break;
  case 0xf034b6u: /* addq    $4,r17 */
   s.registers[0][17]=add(&s,s.registers[0][17],4u);
   s.pc=0xf034b8u;break;
case 0xf034b8u: /* load    (r14),r0 */
 CHECK(rd32(bus,&s,local(s.registers[0][14])?(s.registers[0][14]&~3u):s.registers[0][14],&v));s.registers[0][0]=v;
 s.pc=0xf034bau;break;
  case 0xf034bau: /* addq    $4,r14 */
   s.registers[0][14]=add(&s,s.registers[0][14],4u);
   s.pc=0xf034bcu;break;
case 0xf034bcu: /* load    (r14),r1 */
 CHECK(rd32(bus,&s,local(s.registers[0][14])?(s.registers[0][14]&~3u):s.registers[0][14],&v));s.registers[0][1]=v;
 s.pc=0xf034beu;break;
case 0xf034beu: /* load    (r15),r2 */
 CHECK(rd32(bus,&s,local(s.registers[0][15])?(s.registers[0][15]&~3u):s.registers[0][15],&v));s.registers[0][2]=v;
 s.pc=0xf034c0u;break;
  case 0xf034c0u: /* addq    $4,r15 */
   s.registers[0][15]=add(&s,s.registers[0][15],4u);
   s.pc=0xf034c2u;break;
case 0xf034c2u: /* load    (r15),r3 */
 CHECK(rd32(bus,&s,local(s.registers[0][15])?(s.registers[0][15]&~3u):s.registers[0][15],&v));s.registers[0][3]=v;
 s.pc=0xf034c4u;break;
  case 0xf034c4u: /* store   r0,(r18) */
   CHECK(wr32(bus,&s,local(s.registers[0][18])?(s.registers[0][18]&~3u):s.registers[0][18],s.registers[0][0]));
   s.pc=0xf034c6u;break;
  case 0xf034c6u: /* addq    $4,r18 */
   s.registers[0][18]=add(&s,s.registers[0][18],4u);
   s.pc=0xf034c8u;break;
  case 0xf034c8u: /* store   r2,(r18) */
   CHECK(wr32(bus,&s,local(s.registers[0][18])?(s.registers[0][18]&~3u):s.registers[0][18],s.registers[0][2]));
   s.pc=0xf034cau;break;
  case 0xf034cau: /* addq    $4,r18 */
   s.registers[0][18]=add(&s,s.registers[0][18],4u);
   s.pc=0xf034ccu;break;
  case 0xf034ccu: /* store   r1,(r19) */
   CHECK(wr32(bus,&s,local(s.registers[0][19])?(s.registers[0][19]&~3u):s.registers[0][19],s.registers[0][1]));
   s.pc=0xf034ceu;break;
  case 0xf034ceu: /* addq    $4,r19 */
   s.registers[0][19]=add(&s,s.registers[0][19],4u);
   s.pc=0xf034d0u;break;
  case 0xf034d0u: /* store   r3,(r19) */
   CHECK(wr32(bus,&s,local(s.registers[0][19])?(s.registers[0][19]&~3u):s.registers[0][19],s.registers[0][3]));
   s.pc=0xf034d2u;break;
  case 0xf034d2u: /* jump    (r26) */
   if(condition(&s,0)){pending=1;target=s.registers[0][26];}
   s.pc=0xf034d4u;break;
  case 0xf034d4u: /* addq    $4,r19 */
   s.registers[0][19]=add(&s,s.registers[0][19],4u);
   s.pc=0xf034d6u;break;
  case 0xf034d6u: /* add     r20,r16 */
   s.registers[0][16]=add(&s,s.registers[0][16],s.registers[0][20]);
   s.pc=0xf034d8u;break;
  case 0xf034d8u: /* add     r20,r17 */
   s.registers[0][17]=add(&s,s.registers[0][17],s.registers[0][20]);
   s.pc=0xf034dau;break;
  case 0xf034dau: /* add     r20,r18 */
   s.registers[0][18]=add(&s,s.registers[0][18],s.registers[0][20]);
   s.pc=0xf034dcu;break;
  case 0xf034dcu: /* add     r20,r19 */
   s.registers[0][19]=add(&s,s.registers[0][19],s.registers[0][20]);
   s.pc=0xf034deu;break;
  case 0xf034deu: /* subq    $4,r6 */
   s.registers[0][6]=sub(&s,s.registers[0][6],4u);
   s.pc=0xf034e0u;break;
  case 0xf034e0u: /* jump    nz,(r22) */
   if(condition(&s,1)){pending=1;target=s.registers[0][22];}
   s.pc=0xf034e2u;break;
  case 0xf034e2u: /* nop */
   s.pc=0xf034e4u;break;
  case 0xf034e4u: /* movei   $f036d6,r0 */
   s.registers[0][0]=0xf036d6u;
   s.pc=0xf034eau;break;
  case 0xf034eau: /* jump    (r0) */
   if(condition(&s,0)){pending=1;target=s.registers[0][0];}
   s.pc=0xf034ecu;break;
  case 0xf034ecu: /* nop */
   s.pc=0xf034eeu;break;
case 0xf03500u: /* load    (r0),r4 */
 CHECK(rd32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],&v));s.registers[0][4]=v;
 s.pc=0xf03502u;break;
  case 0xf03502u: /* addq    $4,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],4u);
   s.pc=0xf03504u;break;
case 0xf03504u: /* load    (r0),r5 */
 CHECK(rd32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],&v));s.registers[0][5]=v;
 s.pc=0xf03506u;break;
  case 0xf03506u: /* addq    $4,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],4u);
   s.pc=0xf03508u;break;
case 0xf03508u: /* load    (r0),r6 */
 CHECK(rd32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],&v));s.registers[0][6]=v;
 s.pc=0xf0350au;break;
  case 0xf0350au: /* movei   $f036d6,r24 */
   s.registers[0][24]=0xf036d6u;
   s.pc=0xf03510u;break;
  case 0xf03510u: /* movei   $f0372c,r16 */
   s.registers[0][16]=0xf0372cu;
   s.pc=0xf03516u;break;
  case 0xf03516u: /* movei   $f038ac,r17 */
   s.registers[0][17]=0xf038acu;
   s.pc=0xf0351cu;break;
  case 0xf0351cu: /* addq    $2,r17 */
   s.registers[0][17]=add(&s,s.registers[0][17],2u);
   s.pc=0xf0351eu;break;
  case 0xf0351eu: /* subq    $3,r1 */
   s.registers[0][1]=sub(&s,s.registers[0][1],3u);
   s.pc=0xf03520u;break;
  case 0xf03520u: /* movei   $f034f0,r0 */
   s.registers[0][0]=0xf034f0u;
   s.pc=0xf03526u;break;
  case 0xf03526u: /* move    r1,r2 */
   s.registers[0][2]=s.registers[0][1];
   s.pc=0xf03528u;break;
  case 0xf03528u: /* bclr    $0,r2 */
   s.registers[0][2]&=~(1u<<0);
   zn(&s,s.registers[0][2]);
   s.pc=0xf0352au;break;
  case 0xf0352au: /* shlq    $1,r2 */
   s.c=s.registers[0][2]>>31;s.registers[0][2]=s.registers[0][2]<<1;zn(&s,s.registers[0][2]);
   s.pc=0xf0352cu;break;
  case 0xf0352cu: /* add     r2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][2]);
   s.pc=0xf0352eu;break;
case 0xf0352eu: /* load    (r0),r22 */
 CHECK(rd32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],&v));s.registers[0][22]=v;
 s.pc=0xf03530u;break;
  case 0xf03530u: /* btst    $0,r1 */
   s.z=((~s.registers[0][1])>>0)&1u;
   s.pc=0xf03532u;break;
  case 0xf03532u: /* jr      nz,00F03550 */
   if(condition(&s,1)){pending=1;target=0xf03550u;}
   s.pc=0xf03534u;break;
  case 0xf03534u: /* nop */
   s.pc=0xf03536u;break;
  case 0xf03536u: /* movei   $f03546,r23 */
   s.registers[0][23]=0xf03546u;
   s.pc=0xf0353cu;break;
  case 0xf0353cu: /* moveq   6,r7 */
   s.registers[0][7]=6u;
   s.pc=0xf0353eu;break;
  case 0xf0353eu: /* btst    $2,r1 */
   s.z=((~s.registers[0][1])>>2)&1u;
   s.pc=0xf03540u;break;
  case 0xf03540u: /* jr      z,00F03546 */
   if(condition(&s,2)){pending=1;target=0xf03546u;}
   s.pc=0xf03542u;break;
  case 0xf03542u: /* nop */
   s.pc=0xf03544u;break;
  case 0xf03544u: /* addq    $2,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],2u);
   s.pc=0xf03546u;break;
  case 0xf03546u: /* sub     r7,r6 */
   s.registers[0][6]=sub(&s,s.registers[0][6],s.registers[0][7]);
   s.pc=0xf03548u;break;
  case 0xf03548u: /* jump    nn,(r22) */
   if(condition(&s,20)){pending=1;target=s.registers[0][22];}
   s.pc=0xf0354au;break;
  case 0xf0354au: /* nop */
   s.pc=0xf0354cu;break;
  case 0xf0354cu: /* jump    (r24) */
   if(condition(&s,0)){pending=1;target=s.registers[0][24];}
   s.pc=0xf0354eu;break;
  case 0xf0354eu: /* nop */
   s.pc=0xf03550u;break;
  case 0xf03550u: /* movei   $100,r10 */
   s.registers[0][10]=0x100u;
   s.pc=0xf03556u;break;
  case 0xf03556u: /* movei   $f0357c,r23 */
   s.registers[0][23]=0xf0357cu;
   s.pc=0xf0355cu;break;
  case 0xf0355cu: /* movei   $f03574,r21 */
   s.registers[0][21]=0xf03574u;
   s.pc=0xf03562u;break;
  case 0xf03562u: /* moveq   0,r9 */
   s.registers[0][9]=0u;
   s.pc=0xf03564u;break;
  case 0xf03564u: /* moveq   8,r7 */
   s.registers[0][7]=8u;
   s.pc=0xf03566u;break;
  case 0xf03566u: /* btst    $1,r1 */
   s.z=((~s.registers[0][1])>>1)&1u;
   s.pc=0xf03568u;break;
  case 0xf03568u: /* jr      z,00F0356E */
   if(condition(&s,2)){pending=1;target=0xf0356eu;}
   s.pc=0xf0356au;break;
  case 0xf0356au: /* nop */
   s.pc=0xf0356cu;break;
  case 0xf0356eu: /* subq    $1,r9 */
   s.registers[0][9]=sub(&s,s.registers[0][9],1u);
   s.pc=0xf03570u;break;
  case 0xf03570u: /* jr      n,00F03586 */
   if(condition(&s,24)){pending=1;target=0xf03586u;}
   s.pc=0xf03572u;break;
  case 0xf03572u: /* nop */
   s.pc=0xf03574u;break;
  case 0xf03574u: /* add     r8,r8 */
   s.registers[0][8]=add(&s,s.registers[0][8],s.registers[0][8]);
   s.pc=0xf03576u;break;
  case 0xf03576u: /* jump    c,(r22) */
   if(condition(&s,8)){pending=1;target=s.registers[0][22];}
   s.pc=0xf03578u;break;
  case 0xf03578u: /* nop */
   s.pc=0xf0357au;break;
  case 0xf0357au: /* add     r7,r5 */
   s.registers[0][5]=add(&s,s.registers[0][5],s.registers[0][7]);
   s.pc=0xf0357cu;break;
  case 0xf0357cu: /* subq    $1,r10 */
   s.registers[0][10]=sub(&s,s.registers[0][10],1u);
   s.pc=0xf0357eu;break;
  case 0xf0357eu: /* jr      nz,00F0356E */
   if(condition(&s,1)){pending=1;target=0xf0356eu;}
   s.pc=0xf03580u;break;
  case 0xf03580u: /* nop */
   s.pc=0xf03582u;break;
  case 0xf03582u: /* jump    (r24) */
   if(condition(&s,0)){pending=1;target=s.registers[0][24];}
   s.pc=0xf03584u;break;
  case 0xf03584u: /* nop */
   s.pc=0xf03586u;break;
  case 0xf03586u: /* loadw   (r4),r8 */
   CHECK(loadw(bus,&s,s.registers[0][4],&v));s.registers[0][8]=v;
   s.pc=0xf03588u;break;
  case 0xf03588u: /* addq    $2,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],2u);
   s.pc=0xf0358au;break;
  case 0xf0358au: /* loadw   (r4),r0 */
   CHECK(loadw(bus,&s,s.registers[0][4],&v));s.registers[0][0]=v;
   s.pc=0xf0358cu;break;
  case 0xf0358cu: /* shlq    $10,r8 */
   s.c=s.registers[0][8]>>31;s.registers[0][8]=s.registers[0][8]<<16;zn(&s,s.registers[0][8]);
   s.pc=0xf0358eu;break;
  case 0xf0358eu: /* addq    $2,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],2u);
   s.pc=0xf03590u;break;
  case 0xf03590u: /* or      r0,r8 */
   s.registers[0][8]|=s.registers[0][0];
   zn(&s,s.registers[0][8]);
   s.pc=0xf03592u;break;
  case 0xf03592u: /* jump    nz,(r21) */
   if(condition(&s,1)){pending=1;target=s.registers[0][21];}
   s.pc=0xf03594u;break;
  case 0xf03594u: /* moveq   31,r9 */
   s.registers[0][9]=31u;
   s.pc=0xf03596u;break;
  case 0xf0367au: /* loadw   (r4),r0 */
   CHECK(loadw(bus,&s,s.registers[0][4],&v));s.registers[0][0]=v;
   s.pc=0xf0367cu;break;
  case 0xf0367cu: /* addq    $2,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],2u);
   s.pc=0xf0367eu;break;
  case 0xf0367eu: /* loadw   (r4),r1 */
   CHECK(loadw(bus,&s,s.registers[0][4],&v));s.registers[0][1]=v;
   s.pc=0xf03680u;break;
  case 0xf03680u: /* addq    $2,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],2u);
   s.pc=0xf03682u;break;
  case 0xf03682u: /* loadw   (r4),r2 */
   CHECK(loadw(bus,&s,s.registers[0][4],&v));s.registers[0][2]=v;
   s.pc=0xf03684u;break;
  case 0xf03684u: /* addq    $2,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],2u);
   s.pc=0xf03686u;break;
  case 0xf03686u: /* loadw   (r4),r3 */
   CHECK(loadw(bus,&s,s.registers[0][4],&v));s.registers[0][3]=v;
   s.pc=0xf03688u;break;
  case 0xf03688u: /* addq    $2,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],2u);
   s.pc=0xf0368au;break;
case 0xf0368au: /* rorq    $10,r0 */
 v=s.registers[0][0];s.c=v>>31;s.registers[0][0]=(v>>16)|(v<<16);zn(&s,s.registers[0][0]);
 s.pc=0xf0368cu;break;
case 0xf0368cu: /* rorq    $10,r2 */
 v=s.registers[0][2];s.c=v>>31;s.registers[0][2]=(v>>16)|(v<<16);zn(&s,s.registers[0][2]);
 s.pc=0xf0368eu;break;
  case 0xf0368eu: /* or      r1,r0 */
   s.registers[0][0]|=s.registers[0][1];
   zn(&s,s.registers[0][0]);
   s.pc=0xf03690u;break;
  case 0xf03690u: /* or      r3,r2 */
   s.registers[0][2]|=s.registers[0][3];
   zn(&s,s.registers[0][2]);
   s.pc=0xf03692u;break;
  case 0xf03692u: /* store   r0,(r5) */
   CHECK(wr32(bus,&s,local(s.registers[0][5])?(s.registers[0][5]&~3u):s.registers[0][5],s.registers[0][0]));
   s.pc=0xf03694u;break;
  case 0xf03694u: /* addq    $4,r5 */
   s.registers[0][5]=add(&s,s.registers[0][5],4u);
   s.pc=0xf03696u;break;
  case 0xf03696u: /* store   r2,(r5) */
   CHECK(wr32(bus,&s,local(s.registers[0][5])?(s.registers[0][5]&~3u):s.registers[0][5],s.registers[0][2]));
   s.pc=0xf03698u;break;
  case 0xf03698u: /* jump    (r23) */
   if(condition(&s,0)){pending=1;target=s.registers[0][23];}
   s.pc=0xf0369au;break;
  case 0xf0369au: /* addq    $4,r5 */
   s.registers[0][5]=add(&s,s.registers[0][5],4u);
   s.pc=0xf0369cu;break;
  case 0xf036d6u: /* moveq   3,r0 */
   s.registers[0][0]=3u;
   s.pc=0xf036d8u;break;
  case 0xf036d8u: /* movei   $f02114,r1 */
   s.registers[0][1]=0xf02114u;
   s.pc=0xf036deu;break;
  case 0xf036deu: /* store   r0,(r1) */
   CHECK(wr32(bus,&s,local(s.registers[0][1])?(s.registers[0][1]&~3u):s.registers[0][1],s.registers[0][0]));
   s.pc=0xf036e0u;break;
  case 0xf036e0u: /* movei   $f032c8,r0 */
   s.registers[0][0]=0xf032c8u;
   s.pc=0xf036e6u;break;
  case 0xf036e6u: /* jump    (r0) */
   if(condition(&s,0)){pending=1;target=s.registers[0][0];}
   s.pc=0xf036e8u;break;
  case 0xf036e8u: /* nop */
   s.pc=0xf036eau;break;
default:return BIWN_MOVIE_SEQUENCE_GPU_BAD_PC;
}if(delayed){if(pending)return BIWN_MOVIE_SEQUENCE_GPU_BAD_DELAY;s.pc=resume;}if(s.pc==0xf032c8u&&be32(s.local_RAM+0x9f0)==0){*state=s;return 0;}}return BIWN_MOVIE_SEQUENCE_GPU_WORK_LIMIT;}
