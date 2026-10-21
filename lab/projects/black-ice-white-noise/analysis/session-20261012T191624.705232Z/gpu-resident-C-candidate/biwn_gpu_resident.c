/* Generated from the pinned GPU58A0 overlay by
 * scripts/generate_biwn_gpu_resident.py. Analyst static recompilation,
 * not recovered original source. Integer primitive behavior is checked
 * against the pinned Virtual Jaguar core; no core runs on the C side. */
#include "biwn_gpu_resident.h"
#include <string.h>
static uint32_t sx16(uint32_t v){return(v&0x7fffu)-(v&0x8000u);}
static uint32_t sar(uint32_t v,unsigned n){return n>=32?((v&0x80000000u)?0xffffffffu:0):(v>>n)|((v&0x80000000u)?(0xffffffffu<<(32-n)):0);}
static void zn(struct biwn_gpu_resident_state *s,uint32_t v){s->z=v==0;s->n=v>>31;}
static uint32_t add(struct biwn_gpu_resident_state *s,uint32_t a,uint32_t b){uint32_t v=a+b;s->c=b>~a;zn(s,v);return v;}
static uint32_t sub(struct biwn_gpu_resident_state *s,uint32_t a,uint32_t b){uint32_t v=a-b;s->c=b>a;zn(s,v);return v;}
static int condition(struct biwn_gpu_resident_state *s,unsigned code){unsigned flags=s->z|(s->c<<1)|(s->n<<2);return !((code&1u)&&(flags&1u))&&!((code&2u)&&!(flags&1u))&&!((code&4u)&&(flags&(2u<<(code>>4))))&&!((code&8u)&&!(flags&(2u<<(code>>4))));}
static uint32_t be32(const uint8_t *p){return((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
static void put32(uint8_t *p,uint32_t v){p[0]=(uint8_t)(v>>24);p[1]=(uint8_t)(v>>16);p[2]=(uint8_t)(v>>8);p[3]=(uint8_t)v;}
static int local(uint32_t a){return a>=0xf03000u&&a<=0xf03ffcu;}
static int rd32(struct biwn_gpu_resident_bus *bus,struct biwn_gpu_resident_state *s,uint32_t a,uint32_t *v){if(local(a)){*v=be32(s->local_RAM+a-0xf03000u);return 0;}if(a==0xf02104u){*v=s->matrix_control;return 0;}if(a==0xf02108u){*v=s->matrix_pointer;return 0;}return bus->read32(bus->context,a,v)?2:0;}
static int rd16(struct biwn_gpu_resident_bus *bus,struct biwn_gpu_resident_state *s,uint32_t a,uint32_t *v){uint16_t h;if(a>=0xf03000u&&a<=0xf03ffeu){unsigned p=a-0xf03000u;*v=((uint32_t)s->local_RAM[p]<<8)|s->local_RAM[p+1];return 0;}if(bus->read16(bus->context,a,&h))return 2;*v=h;return 0;}
static int loadw(struct biwn_gpu_resident_bus *bus,struct biwn_gpu_resident_state *s,uint32_t a,uint32_t *v){if(a>=0xf03000u&&a<=0xf03fffu)return rd32(bus,s,a&~3u,v);return rd16(bus,s,a,v);}
static int wr32(struct biwn_gpu_resident_bus *bus,struct biwn_gpu_resident_state *s,uint32_t a,uint32_t v){if(local(a)){put32(s->local_RAM+a-0xf03000u,v);return 0;}if(a==0xf02104u){s->matrix_control=v;return 0;}if(a==0xf02108u){s->matrix_pointer=v&~3u;return 0;}if(a==0xf02238u)return bus->blitter_write32(bus->context,a,v,s->local_RAM)?2:0;return bus->write32(bus->context,a,v)?2:0;}
static void divide(struct biwn_gpu_resident_state *s,unsigned m,unsigned n){uint32_t q=s->registers[0][n],r=0,d=s->registers[0][m];unsigned i;if(s->division_control&1u){r=q>>16;q<<=16;}for(i=0;i<32;i++){uint32_t sign=r&0x80000000u;r=(r<<1)|(q>>31);r+=sign?d:0u-d;q=(q<<1)|((~r)>>31);}s->registers[0][n]=q;s->remainder=r;}
static int matrix(struct biwn_gpu_resident_bus *bus,struct biwn_gpu_resident_state *s,unsigned m,unsigned n){unsigned i,count=s->matrix_control&15u;uint32_t a=s->matrix_pointer,v;int64_t sum=0;for(i=0;i<count;i++){uint32_t packed=s->registers[1][m+(i>>1)];int32_t x=(int32_t)sx16(packed>>(i&1u?16:0));int status=rd16(bus,s,a+2,&v);if(status)return status;sum+=(int64_t)x*(int32_t)sx16(v);a+=(s->matrix_control&16u)?4u*count:4u;}s->registers[0][n]=(uint32_t)sum;zn(s,(uint32_t)sum);return 0;}
#define CHECK(e) do{int status=(e);if(status)return(enum biwn_gpu_resident_status)status;}while(0)
enum biwn_gpu_resident_status biwn_gpu_resident_run(struct biwn_gpu_resident_bus *bus,struct biwn_gpu_resident_state *state,uint32_t budget){struct biwn_gpu_resident_state s;uint32_t v,target=0;unsigned pending=0;if(!bus||!state||!budget||!bus->read16||!bus->read32||!bus->write32||!bus->blitter_write32||state->z>1||state->c>1||state->n>1)return 1;s=*state;while(budget--){unsigned delayed=pending;uint32_t resume=target;pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){
  case 0xf03440u: /* movei   $f0320c,r11 */
   s.registers[0][11]=0xf0320cu;
   s.pc=0xf03446u;break;
  case 0xf03446u: /* load    (r11),r1 */
   CHECK(rd32(bus,&s,s.registers[0][11]&~3u,&v));s.registers[0][1]=v;
   s.pc=0xf03448u;break;
  case 0xf03448u: /* addq    $8,r11 */
   s.registers[0][11]=add(&s,s.registers[0][11],8u);
   s.pc=0xf0344au;break;
  case 0xf0344au: /* load    (r11),r25 */
   CHECK(rd32(bus,&s,s.registers[0][11]&~3u,&v));s.registers[0][25]=v;
   s.pc=0xf0344cu;break;
  case 0xf0344cu: /* subq    $4,r11 */
   s.registers[0][11]=sub(&s,s.registers[0][11],4u);
   s.pc=0xf0344eu;break;
  case 0xf0344eu: /* loadw   (r1),r26 */
   CHECK(loadw(bus,&s,s.registers[0][1],&v));s.registers[0][26]=v;
   s.pc=0xf03450u;break;
  case 0xf03450u: /* addq    $2,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],2u);
   s.pc=0xf03452u;break;
  case 0xf03452u: /* loadw   (r1),r2 */
   CHECK(loadw(bus,&s,s.registers[0][1],&v));s.registers[0][2]=v;
   s.pc=0xf03454u;break;
  case 0xf03454u: /* addq    $2,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],2u);
   s.pc=0xf03456u;break;
  case 0xf03456u: /* load    (r1),r27 */
   CHECK(rd32(bus,&s,s.registers[0][1]&~3u,&v));s.registers[0][27]=v;
   s.pc=0xf03458u;break;
  case 0xf03458u: /* addq    $4,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],4u);
   s.pc=0xf0345au;break;
  case 0xf0345au: /* load    (r1),r3 */
   CHECK(rd32(bus,&s,s.registers[0][1]&~3u,&v));s.registers[0][3]=v;
   s.pc=0xf0345cu;break;
  case 0xf0345cu: /* addq    $4,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],4u);
   s.pc=0xf0345eu;break;
  case 0xf0345eu: /* load    (r1),r4 */
   CHECK(rd32(bus,&s,s.registers[0][1]&~3u,&v));s.registers[0][4]=v;
   s.pc=0xf03460u;break;
  case 0xf03460u: /* addq    $4,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],4u);
   s.pc=0xf03462u;break;
  case 0xf03462u: /* movei   $f03ecc,r0 */
   s.registers[0][0]=0xf03eccu;
   s.pc=0xf03468u;break;
  case 0xf03468u: /* store   r2,(r0) */
   CHECK(wr32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],s.registers[0][2]));
   s.pc=0xf0346au;break;
  case 0xf0346au: /* addq    $4,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],4u);
   s.pc=0xf0346cu;break;
  case 0xf0346cu: /* store   r3,(r0) */
   CHECK(wr32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],s.registers[0][3]));
   s.pc=0xf0346eu;break;
  case 0xf0346eu: /* addq    $4,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],4u);
   s.pc=0xf03470u;break;
  case 0xf03470u: /* store   r4,(r0) */
   CHECK(wr32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],s.registers[0][4]));
   s.pc=0xf03472u;break;
  case 0xf03472u: /* moveta  r1,r13 */
   s.registers[1][13]=s.registers[0][1];
   s.pc=0xf03474u;break;
  case 0xf03474u: /* moveta  r25,r14 */
   s.registers[1][14]=s.registers[0][25];
   s.pc=0xf03476u;break;
  case 0xf03476u: /* movei   $400,r21 */
   s.registers[0][21]=0x400u;
   s.pc=0xf0347cu;break;
  case 0xf0347cu: /* movei   $ad,r16 */
   s.registers[0][16]=0xadu;
   s.pc=0xf03482u;break;
  case 0xf03482u: /* movei   $ad,r17 */
   s.registers[0][17]=0xadu;
   s.pc=0xf03488u;break;
  case 0xf03488u: /* move    r21,r20 */
   s.registers[0][20]=s.registers[0][21];
   s.pc=0xf0348au;break;
  case 0xf0348au: /* movei   $6f,r18 */
   s.registers[0][18]=0x6fu;
   s.pc=0xf03490u;break;
  case 0xf03490u: /* movei   $59,r19 */
   s.registers[0][19]=0x59u;
   s.pc=0xf03496u;break;
  case 0xf03496u: /* neg     r20 */
   s.registers[0][20]=sub(&s,0,s.registers[0][20]);
   s.pc=0xf03498u;break;
  case 0xf03498u: /* load    (r11),r5 */
   CHECK(rd32(bus,&s,s.registers[0][11]&~3u,&v));s.registers[0][5]=v;
   s.pc=0xf0349au;break;
case 0xf0349au: /* movefa  r7,r12 */
 s.registers[0][12]=s.registers[1][7];
 s.pc=0xf0349cu;break;
  case 0xf0349cu: /* moveq   9,r6 */
   s.registers[0][6]=9u;
   s.pc=0xf0349eu;break;
  case 0xf0349eu: /* loadw   (r5),r7 */
   CHECK(loadw(bus,&s,s.registers[0][5],&v));s.registers[0][7]=v;
   s.pc=0xf034a0u;break;
  case 0xf034a0u: /* shlq    $10,r7 */
   s.c=s.registers[0][7]>>31;s.registers[0][7]=s.registers[0][7]<<16;zn(&s,s.registers[0][7]);
   s.pc=0xf034a2u;break;
  case 0xf034a2u: /* addq    $2,r5 */
   s.registers[0][5]=add(&s,s.registers[0][5],2u);
   s.pc=0xf034a4u;break;
  case 0xf034a4u: /* sharq   $10,r7 */
   s.c=s.registers[0][7]&1u;s.registers[0][7]=sar(s.registers[0][7],16);zn(&s,s.registers[0][7]);
   s.pc=0xf034a6u;break;
  case 0xf034a6u: /* subq    $1,r6 */
   s.registers[0][6]=sub(&s,s.registers[0][6],1u);
   s.pc=0xf034a8u;break;
  case 0xf034a8u: /* store   r7,(r12) */
   CHECK(wr32(bus,&s,local(s.registers[0][12])?(s.registers[0][12]&~3u):s.registers[0][12],s.registers[0][7]));
   s.pc=0xf034aau;break;
  case 0xf034aau: /* jr      nz,00F0349E */
   if(condition(&s,1)){pending=1;target=0xf0349eu;}
   s.pc=0xf034acu;break;
  case 0xf034acu: /* addqt   $4,r12 */
   s.registers[0][12]+=4u;
   s.pc=0xf034aeu;break;
  case 0xf034aeu: /* move    r5,r7 */
   s.registers[0][7]=s.registers[0][5];
   s.pc=0xf034b0u;break;
  case 0xf034b0u: /* subq    $c,r12 */
   s.registers[0][12]=sub(&s,s.registers[0][12],12u);
   s.pc=0xf034b2u;break;
  case 0xf034b2u: /* addq    $8,r5 */
   s.registers[0][5]=add(&s,s.registers[0][5],8u);
   s.pc=0xf034b4u;break;
  case 0xf034b4u: /* loadw   (r7),r13 */
   CHECK(loadw(bus,&s,s.registers[0][7],&v));s.registers[0][13]=v;
   s.pc=0xf034b6u;break;
  case 0xf034b6u: /* loadw   (r5),r8 */
   CHECK(loadw(bus,&s,s.registers[0][5],&v));s.registers[0][8]=v;
   s.pc=0xf034b8u;break;
  case 0xf034b8u: /* addq    $2,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],2u);
   s.pc=0xf034bau;break;
  case 0xf034bau: /* addq    $2,r5 */
   s.registers[0][5]=add(&s,s.registers[0][5],2u);
   s.pc=0xf034bcu;break;
  case 0xf034bcu: /* loadw   (r7),r14 */
   CHECK(loadw(bus,&s,s.registers[0][7],&v));s.registers[0][14]=v;
   s.pc=0xf034beu;break;
  case 0xf034beu: /* loadw   (r5),r9 */
   CHECK(loadw(bus,&s,s.registers[0][5],&v));s.registers[0][9]=v;
   s.pc=0xf034c0u;break;
  case 0xf034c0u: /* addq    $2,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],2u);
   s.pc=0xf034c2u;break;
  case 0xf034c2u: /* addq    $2,r5 */
   s.registers[0][5]=add(&s,s.registers[0][5],2u);
   s.pc=0xf034c4u;break;
  case 0xf034c4u: /* loadw   (r7),r15 */
   CHECK(loadw(bus,&s,s.registers[0][7],&v));s.registers[0][15]=v;
   s.pc=0xf034c6u;break;
  case 0xf034c6u: /* loadw   (r5),r10 */
   CHECK(loadw(bus,&s,s.registers[0][5],&v));s.registers[0][10]=v;
   s.pc=0xf034c8u;break;
  case 0xf034c8u: /* shlq    $10,r13 */
   s.c=s.registers[0][13]>>31;s.registers[0][13]=s.registers[0][13]<<16;zn(&s,s.registers[0][13]);
   s.pc=0xf034cau;break;
  case 0xf034cau: /* shlq    $10,r14 */
   s.c=s.registers[0][14]>>31;s.registers[0][14]=s.registers[0][14]<<16;zn(&s,s.registers[0][14]);
   s.pc=0xf034ccu;break;
  case 0xf034ccu: /* shlq    $10,r15 */
   s.c=s.registers[0][15]>>31;s.registers[0][15]=s.registers[0][15]<<16;zn(&s,s.registers[0][15]);
   s.pc=0xf034ceu;break;
  case 0xf034ceu: /* sharq   $2,r13 */
   s.c=s.registers[0][13]&1u;s.registers[0][13]=sar(s.registers[0][13],2);zn(&s,s.registers[0][13]);
   s.pc=0xf034d0u;break;
  case 0xf034d0u: /* sharq   $2,r14 */
   s.c=s.registers[0][14]&1u;s.registers[0][14]=sar(s.registers[0][14],2);zn(&s,s.registers[0][14]);
   s.pc=0xf034d2u;break;
  case 0xf034d2u: /* sharq   $2,r15 */
   s.c=s.registers[0][15]&1u;s.registers[0][15]=sar(s.registers[0][15],2);zn(&s,s.registers[0][15]);
   s.pc=0xf034d4u;break;
  case 0xf034d4u: /* or      r8,r13 */
   s.registers[0][13]|=s.registers[0][8];
   zn(&s,s.registers[0][13]);
   s.pc=0xf034d6u;break;
  case 0xf034d6u: /* or      r9,r14 */
   s.registers[0][14]|=s.registers[0][9];
   zn(&s,s.registers[0][14]);
   s.pc=0xf034d8u;break;
  case 0xf034d8u: /* or      r10,r15 */
   s.registers[0][15]|=s.registers[0][10];
   zn(&s,s.registers[0][15]);
   s.pc=0xf034dau;break;
  case 0xf034dau: /* movei   $f02108,r22 */
   s.registers[0][22]=0xf02108u;
   s.pc=0xf034e0u;break;
case 0xf034e0u: /* movefa  r0,r0 */
 s.registers[0][0]=s.registers[1][0];
 s.pc=0xf034e2u;break;
  case 0xf034e2u: /* move    pc,r1 */
   s.registers[0][1]=0xf034e2u;
   s.pc=0xf034e4u;break;
  case 0xf034e4u: /* moveq   30,r2 */
   s.registers[0][2]=30u;
   s.pc=0xf034e6u;break;
  case 0xf034e6u: /* addq    $6,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],6u);
   s.pc=0xf034e8u;break;
  case 0xf034e8u: /* move    r27,r10 */
   s.registers[0][10]=s.registers[0][27];
   s.pc=0xf034eau;break;
  case 0xf034eau: /* moveq   1,r3 */
   s.registers[0][3]=1u;
   s.pc=0xf034ecu;break;
  case 0xf034ecu: /* move    r27,r11 */
   s.registers[0][11]=s.registers[0][27];
   s.pc=0xf034eeu;break;
  case 0xf034eeu: /* shlq    $13,r3 */
   s.c=s.registers[0][3]>>31;s.registers[0][3]=s.registers[0][3]<<19;zn(&s,s.registers[0][3]);
   s.pc=0xf034f0u;break;
  case 0xf034f0u: /* addq    $2,r10 */
   s.registers[0][10]=add(&s,s.registers[0][10],2u);
   s.pc=0xf034f2u;break;
  case 0xf034f2u: /* addq    $4,r11 */
   s.registers[0][11]=add(&s,s.registers[0][11],4u);
   s.pc=0xf034f4u;break;
  case 0xf034f4u: /* loadw   (r27),r23 */
   CHECK(loadw(bus,&s,s.registers[0][27],&v));s.registers[0][23]=v;
   s.pc=0xf034f6u;break;
  case 0xf034f6u: /* loadw   (r10),r5 */
   CHECK(loadw(bus,&s,s.registers[0][10],&v));s.registers[0][5]=v;
   s.pc=0xf034f8u;break;
  case 0xf034f8u: /* loadw   (r11),r24 */
   CHECK(loadw(bus,&s,s.registers[0][11],&v));s.registers[0][24]=v;
   s.pc=0xf034fau;break;
  case 0xf034fau: /* addq    $6,r27 */
   s.registers[0][27]=add(&s,s.registers[0][27],6u);
   s.pc=0xf034fcu;break;
  case 0xf034fcu: /* shlq    $10,r5 */
   s.c=s.registers[0][5]>>31;s.registers[0][5]=s.registers[0][5]<<16;zn(&s,s.registers[0][5]);
   s.pc=0xf034feu;break;
  case 0xf034feu: /* subq    $18,r12 */
   s.registers[0][12]=sub(&s,s.registers[0][12],24u);
   s.pc=0xf03500u;break;
  case 0xf03500u: /* or      r5,r23 */
   s.registers[0][23]|=s.registers[0][5];
   zn(&s,s.registers[0][23]);
   s.pc=0xf03502u;break;
  case 0xf03502u: /* store   r12,(r22) */
   CHECK(wr32(bus,&s,local(s.registers[0][22])?(s.registers[0][22]&~3u):s.registers[0][22],s.registers[0][12]));
   s.pc=0xf03504u;break;
  case 0xf03504u: /* moveta  r23,r23 */
   s.registers[1][23]=s.registers[0][23];
   s.pc=0xf03506u;break;
  case 0xf03506u: /* moveta  r24,r24 */
   s.registers[1][24]=s.registers[0][24];
   s.pc=0xf03508u;break;
  case 0xf03508u: /* mmult   r23,r4 */
   CHECK(matrix(bus,&s,23,4));
   s.pc=0xf0350au;break;
  case 0xf0350au: /* addq    $c,r12 */
   s.registers[0][12]=add(&s,s.registers[0][12],12u);
   s.pc=0xf0350cu;break;
  case 0xf0350cu: /* add     r13,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],s.registers[0][13]);
   s.pc=0xf0350eu;break;
  case 0xf0350eu: /* store   r12,(r22) */
   CHECK(wr32(bus,&s,local(s.registers[0][22])?(s.registers[0][22]&~3u):s.registers[0][22],s.registers[0][12]));
   s.pc=0xf03510u;break;
  case 0xf03510u: /* moveta  r23,r23 */
   s.registers[1][23]=s.registers[0][23];
   s.pc=0xf03512u;break;
  case 0xf03512u: /* moveta  r24,r24 */
   s.registers[1][24]=s.registers[0][24];
   s.pc=0xf03514u;break;
  case 0xf03514u: /* mmult   r23,r5 */
   CHECK(matrix(bus,&s,23,5));
   s.pc=0xf03516u;break;
  case 0xf03516u: /* addq    $c,r12 */
   s.registers[0][12]=add(&s,s.registers[0][12],12u);
   s.pc=0xf03518u;break;
  case 0xf03518u: /* add     r14,r5 */
   s.registers[0][5]=add(&s,s.registers[0][5],s.registers[0][14]);
   s.pc=0xf0351au;break;
  case 0xf0351au: /* store   r12,(r22) */
   CHECK(wr32(bus,&s,local(s.registers[0][22])?(s.registers[0][22]&~3u):s.registers[0][22],s.registers[0][12]));
   s.pc=0xf0351cu;break;
  case 0xf0351cu: /* moveta  r23,r23 */
   s.registers[1][23]=s.registers[0][23];
   s.pc=0xf0351eu;break;
  case 0xf0351eu: /* moveta  r24,r24 */
   s.registers[1][24]=s.registers[0][24];
   s.pc=0xf03520u;break;
  case 0xf03520u: /* mmult   r23,r6 */
   CHECK(matrix(bus,&s,23,6));
   s.pc=0xf03522u;break;
  case 0xf03522u: /* sharq   $e,r4 */
   s.c=s.registers[0][4]&1u;s.registers[0][4]=sar(s.registers[0][4],14);zn(&s,s.registers[0][4]);
   s.pc=0xf03524u;break;
  case 0xf03524u: /* add     r15,r6 */
   s.registers[0][6]=add(&s,s.registers[0][6],s.registers[0][15]);
   s.pc=0xf03526u;break;
  case 0xf03526u: /* sharq   $e,r5 */
   s.c=s.registers[0][5]&1u;s.registers[0][5]=sar(s.registers[0][5],14);zn(&s,s.registers[0][5]);
   s.pc=0xf03528u;break;
  case 0xf03528u: /* sharq   $e,r6 */
   s.c=s.registers[0][6]&1u;s.registers[0][6]=sar(s.registers[0][6],14);zn(&s,s.registers[0][6]);
   s.pc=0xf0352au;break;
  case 0xf0352au: /* move    r6,r9 */
   s.registers[0][9]=s.registers[0][6];
   s.pc=0xf0352cu;break;
  case 0xf0352cu: /* move    r5,r8 */
   s.registers[0][8]=s.registers[0][5];
   s.pc=0xf0352eu;break;
  case 0xf0352eu: /* cmp     r2,r6 */
   (void)sub(&s,s.registers[0][6],s.registers[0][2]);
   s.pc=0xf03530u;break;
  case 0xf03530u: /* jr      nn,00F03536 */
   if(condition(&s,20)){pending=1;target=0xf03536u;}
   s.pc=0xf03532u;break;
  case 0xf03532u: /* move    r4,r7 */
   s.registers[0][7]=s.registers[0][4];
   s.pc=0xf03534u;break;
  case 0xf03534u: /* moveq   31,r6 */
   s.registers[0][6]=31u;
   s.pc=0xf03536u;break;
  case 0xf03536u: /* abs     r4 */
   s.c=s.registers[0][4]>>31;if(s.registers[0][4]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[0][4]=0u-s.registers[0][4];s.n=0;s.z=s.registers[0][4]==0;}
   s.pc=0xf03538u;break;
  case 0xf03538u: /* div     r6,r3 */
   divide(&s,6,3);
   s.pc=0xf0353au;break;
  case 0xf0353au: /* abs     r5 */
   s.c=s.registers[0][5]>>31;if(s.registers[0][5]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[0][5]=0u-s.registers[0][5];s.n=0;s.z=s.registers[0][5]==0;}
   s.pc=0xf0353cu;break;
  case 0xf0353cu: /* mult    r16,r4 */
   s.registers[0][4]=(s.registers[0][4]&0xffffu)*(s.registers[0][16]&0xffffu);
   zn(&s,s.registers[0][4]);
   s.pc=0xf0353eu;break;
  case 0xf0353eu: /* mult    r17,r5 */
   s.registers[0][5]=(s.registers[0][5]&0xffffu)*(s.registers[0][17]&0xffffu);
   zn(&s,s.registers[0][5]);
   s.pc=0xf03540u;break;
  case 0xf03540u: /* move    r4,r10 */
   s.registers[0][10]=s.registers[0][4];
   s.pc=0xf03542u;break;
  case 0xf03542u: /* move    r5,r11 */
   s.registers[0][11]=s.registers[0][5];
   s.pc=0xf03544u;break;
  case 0xf03544u: /* mult    r3,r10 */
   s.registers[0][10]=(s.registers[0][10]&0xffffu)*(s.registers[0][3]&0xffffu);
   zn(&s,s.registers[0][10]);
   s.pc=0xf03546u;break;
  case 0xf03546u: /* shrq    $10,r4 */
   s.c=s.registers[0][4]&1u;s.registers[0][4]=s.registers[0][4]>>16;zn(&s,s.registers[0][4]);
   s.pc=0xf03548u;break;
  case 0xf03548u: /* mult    r3,r11 */
   s.registers[0][11]=(s.registers[0][11]&0xffffu)*(s.registers[0][3]&0xffffu);
   zn(&s,s.registers[0][11]);
   s.pc=0xf0354au;break;
  case 0xf0354au: /* shrq    $10,r5 */
   s.c=s.registers[0][5]&1u;s.registers[0][5]=s.registers[0][5]>>16;zn(&s,s.registers[0][5]);
   s.pc=0xf0354cu;break;
  case 0xf0354cu: /* shrq    $10,r10 */
   s.c=s.registers[0][10]&1u;s.registers[0][10]=s.registers[0][10]>>16;zn(&s,s.registers[0][10]);
   s.pc=0xf0354eu;break;
  case 0xf0354eu: /* mult    r3,r4 */
   s.registers[0][4]=(s.registers[0][4]&0xffffu)*(s.registers[0][3]&0xffffu);
   zn(&s,s.registers[0][4]);
   s.pc=0xf03550u;break;
  case 0xf03550u: /* shrq    $10,r11 */
   s.c=s.registers[0][11]&1u;s.registers[0][11]=s.registers[0][11]>>16;zn(&s,s.registers[0][11]);
   s.pc=0xf03552u;break;
  case 0xf03552u: /* mult    r3,r5 */
   s.registers[0][5]=(s.registers[0][5]&0xffffu)*(s.registers[0][3]&0xffffu);
   zn(&s,s.registers[0][5]);
   s.pc=0xf03554u;break;
  case 0xf03554u: /* add     r10,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],s.registers[0][10]);
   s.pc=0xf03556u;break;
  case 0xf03556u: /* add     r11,r5 */
   s.registers[0][5]=add(&s,s.registers[0][5],s.registers[0][11]);
   s.pc=0xf03558u;break;
  case 0xf03558u: /* shrq    $3,r4 */
   s.c=s.registers[0][4]&1u;s.registers[0][4]=s.registers[0][4]>>3;zn(&s,s.registers[0][4]);
   s.pc=0xf0355au;break;
  case 0xf0355au: /* shrq    $3,r5 */
   s.c=s.registers[0][5]&1u;s.registers[0][5]=s.registers[0][5]>>3;zn(&s,s.registers[0][5]);
   s.pc=0xf0355cu;break;
  case 0xf0355cu: /* btst    $1f,r7 */
   s.z=((~s.registers[0][7])>>31)&1u;
   s.pc=0xf0355eu;break;
  case 0xf0355eu: /* jr      z,00F03564 */
   if(condition(&s,2)){pending=1;target=0xf03564u;}
   s.pc=0xf03560u;break;
  case 0xf03560u: /* shlq    $10,r7 */
   s.c=s.registers[0][7]>>31;s.registers[0][7]=s.registers[0][7]<<16;zn(&s,s.registers[0][7]);
   s.pc=0xf03562u;break;
  case 0xf03562u: /* neg     r4 */
   s.registers[0][4]=sub(&s,0,s.registers[0][4]);
   s.pc=0xf03564u;break;
  case 0xf03564u: /* btst    $1f,r8 */
   s.z=((~s.registers[0][8])>>31)&1u;
   s.pc=0xf03566u;break;
  case 0xf03566u: /* jr      z,00F0356C */
   if(condition(&s,2)){pending=1;target=0xf0356cu;}
   s.pc=0xf03568u;break;
  case 0xf03568u: /* and     r0,r8 */
   s.registers[0][8]&=s.registers[0][0];
   zn(&s,s.registers[0][8]);
   s.pc=0xf0356au;break;
  case 0xf0356au: /* neg     r5 */
   s.registers[0][5]=sub(&s,0,s.registers[0][5]);
   s.pc=0xf0356cu;break;
  case 0xf0356cu: /* cmp     r4,r20 */
   (void)sub(&s,s.registers[0][20],s.registers[0][4]);
   s.pc=0xf0356eu;break;
  case 0xf0356eu: /* jr      n,00F03574 */
   if(condition(&s,24)){pending=1;target=0xf03574u;}
   s.pc=0xf03570u;break;
  case 0xf03570u: /* cmp     r5,r20 */
   (void)sub(&s,s.registers[0][20],s.registers[0][5]);
   s.pc=0xf03572u;break;
  case 0xf03572u: /* move    r20,r4 */
   s.registers[0][4]=s.registers[0][20];
   s.pc=0xf03574u;break;
  case 0xf03574u: /* jr      n,00F0357A */
   if(condition(&s,24)){pending=1;target=0xf0357au;}
   s.pc=0xf03576u;break;
  case 0xf03576u: /* cmp     r21,r4 */
   (void)sub(&s,s.registers[0][4],s.registers[0][21]);
   s.pc=0xf03578u;break;
  case 0xf03578u: /* move    r20,r5 */
   s.registers[0][5]=s.registers[0][20];
   s.pc=0xf0357au;break;
  case 0xf0357au: /* jr      n,00F03580 */
   if(condition(&s,24)){pending=1;target=0xf03580u;}
   s.pc=0xf0357cu;break;
  case 0xf0357cu: /* cmp     r21,r5 */
   (void)sub(&s,s.registers[0][5],s.registers[0][21]);
   s.pc=0xf0357eu;break;
  case 0xf0357eu: /* move    r21,r4 */
   s.registers[0][4]=s.registers[0][21];
   s.pc=0xf03580u;break;
  case 0xf03580u: /* jr      n,00F03586 */
   if(condition(&s,24)){pending=1;target=0xf03586u;}
   s.pc=0xf03582u;break;
  case 0xf03582u: /* or      r8,r7 */
   s.registers[0][7]|=s.registers[0][8];
   zn(&s,s.registers[0][7]);
   s.pc=0xf03584u;break;
  case 0xf03584u: /* move    r21,r5 */
   s.registers[0][5]=s.registers[0][21];
   s.pc=0xf03586u;break;
  case 0xf03586u: /* add     r18,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],s.registers[0][18]);
   s.pc=0xf03588u;break;
  case 0xf03588u: /* add     r19,r5 */
   s.registers[0][5]=add(&s,s.registers[0][5],s.registers[0][19]);
   s.pc=0xf0358au;break;
  case 0xf0358au: /* shlq    $10,r4 */
   s.c=s.registers[0][4]>>31;s.registers[0][4]=s.registers[0][4]<<16;zn(&s,s.registers[0][4]);
   s.pc=0xf0358cu;break;
  case 0xf0358cu: /* and     r0,r5 */
   s.registers[0][5]&=s.registers[0][0];
   zn(&s,s.registers[0][5]);
   s.pc=0xf0358eu;break;
  case 0xf0358eu: /* shlq    $10,r3 */
   s.c=s.registers[0][3]>>31;s.registers[0][3]=s.registers[0][3]<<16;zn(&s,s.registers[0][3]);
   s.pc=0xf03590u;break;
  case 0xf03590u: /* and     r0,r9 */
   s.registers[0][9]&=s.registers[0][0];
   zn(&s,s.registers[0][9]);
   s.pc=0xf03592u;break;
  case 0xf03592u: /* or      r5,r4 */
   s.registers[0][4]|=s.registers[0][5];
   zn(&s,s.registers[0][4]);
   s.pc=0xf03594u;break;
  case 0xf03594u: /* or      r3,r9 */
   s.registers[0][9]|=s.registers[0][3];
   zn(&s,s.registers[0][9]);
   s.pc=0xf03596u;break;
  case 0xf03596u: /* move    r25,r10 */
   s.registers[0][10]=s.registers[0][25];
   s.pc=0xf03598u;break;
  case 0xf03598u: /* move    r25,r11 */
   s.registers[0][11]=s.registers[0][25];
   s.pc=0xf0359au;break;
  case 0xf0359au: /* addq    $4,r10 */
   s.registers[0][10]=add(&s,s.registers[0][10],4u);
   s.pc=0xf0359cu;break;
  case 0xf0359cu: /* addq    $8,r11 */
   s.registers[0][11]=add(&s,s.registers[0][11],8u);
   s.pc=0xf0359eu;break;
  case 0xf0359eu: /* store   r7,(r25) */
   CHECK(wr32(bus,&s,local(s.registers[0][25])?(s.registers[0][25]&~3u):s.registers[0][25],s.registers[0][7]));
   s.pc=0xf035a0u;break;
  case 0xf035a0u: /* store   r4,(r10) */
   CHECK(wr32(bus,&s,local(s.registers[0][10])?(s.registers[0][10]&~3u):s.registers[0][10],s.registers[0][4]));
   s.pc=0xf035a2u;break;
  case 0xf035a2u: /* store   r9,(r11) */
   CHECK(wr32(bus,&s,local(s.registers[0][11])?(s.registers[0][11]&~3u):s.registers[0][11],s.registers[0][9]));
   s.pc=0xf035a4u;break;
  case 0xf035a4u: /* subq    $1,r26 */
   s.registers[0][26]=sub(&s,s.registers[0][26],1u);
   s.pc=0xf035a6u;break;
  case 0xf035a6u: /* jump    nz,(r1) */
   if(condition(&s,1)){pending=1;target=s.registers[0][1];}
   s.pc=0xf035a8u;break;
  case 0xf035a8u: /* addq    $c,r25 */
   s.registers[0][25]=add(&s,s.registers[0][25],12u);
   s.pc=0xf035aau;break;
case 0xf035aau: /* movefa  r13,r7 */
 s.registers[0][7]=s.registers[1][13];
 s.pc=0xf035acu;break;
case 0xf035acu: /* movefa  r7,r11 */
 s.registers[0][11]=s.registers[1][7];
 s.pc=0xf035aeu;break;
  case 0xf035aeu: /* loadw   (r7),r4 */
   CHECK(loadw(bus,&s,s.registers[0][7],&v));s.registers[0][4]=v;
   s.pc=0xf035b0u;break;
  case 0xf035b0u: /* addq    $2,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],2u);
   s.pc=0xf035b2u;break;
  case 0xf035b2u: /* loadw   (r7),r5 */
   CHECK(loadw(bus,&s,s.registers[0][7],&v));s.registers[0][5]=v;
   s.pc=0xf035b4u;break;
  case 0xf035b4u: /* addq    $2,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],2u);
   s.pc=0xf035b6u;break;
  case 0xf035b6u: /* loadw   (r7),r9 */
   CHECK(loadw(bus,&s,s.registers[0][7],&v));s.registers[0][9]=v;
   s.pc=0xf035b8u;break;
  case 0xf035b8u: /* addq    $2,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],2u);
   s.pc=0xf035bau;break;
  case 0xf035bau: /* loadw   (r7),r6 */
   CHECK(loadw(bus,&s,s.registers[0][7],&v));s.registers[0][6]=v;
   s.pc=0xf035bcu;break;
case 0xf035bcu: /* movefa  r0,r19 */
 s.registers[0][19]=s.registers[1][0];
 s.pc=0xf035beu;break;
  case 0xf035beu: /* addq    $2,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],2u);
   s.pc=0xf035c0u;break;
  case 0xf035c0u: /* shlq    $10,r19 */
   s.c=s.registers[0][19]>>31;s.registers[0][19]=s.registers[0][19]<<16;zn(&s,s.registers[0][19]);
   s.pc=0xf035c2u;break;
case 0xf035c2u: /* movefa  r0,r18 */
 s.registers[0][18]=s.registers[1][0];
 s.pc=0xf035c4u;break;
  case 0xf035c4u: /* move    r19,r21 */
   s.registers[0][21]=s.registers[0][19];
   s.pc=0xf035c6u;break;
  case 0xf035c6u: /* move    r18,r20 */
   s.registers[0][20]=s.registers[0][18];
   s.pc=0xf035c8u;break;
  case 0xf035c8u: /* move    r19,r23 */
   s.registers[0][23]=s.registers[0][19];
   s.pc=0xf035cau;break;
  case 0xf035cau: /* move    r18,r22 */
   s.registers[0][22]=s.registers[0][18];
   s.pc=0xf035ccu;break;
  case 0xf035ccu: /* shlq    $3,r9 */
   s.c=s.registers[0][9]>>31;s.registers[0][9]=s.registers[0][9]<<3;zn(&s,s.registers[0][9]);
   s.pc=0xf035ceu;break;
  case 0xf035ceu: /* move    pc,r3 */
   s.registers[0][3]=0xf035ceu;
   s.pc=0xf035d0u;break;
  case 0xf035d0u: /* moveq   0,r8 */
   s.registers[0][8]=0u;
   s.pc=0xf035d2u;break;
  case 0xf035d2u: /* addq    $6,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],6u);
   s.pc=0xf035d4u;break;
  case 0xf035d4u: /* loadw   (r7),r0 */
   CHECK(loadw(bus,&s,s.registers[0][7],&v));s.registers[0][0]=v;
   s.pc=0xf035d6u;break;
case 0xf035d6u: /* movefa  r14,r1 */
 s.registers[0][1]=s.registers[1][14];
 s.pc=0xf035d8u;break;
  case 0xf035d8u: /* shlq    $2,r0 */
   s.c=s.registers[0][0]>>31;s.registers[0][0]=s.registers[0][0]<<2;zn(&s,s.registers[0][0]);
   s.pc=0xf035dau;break;
  case 0xf035dau: /* add     r0,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],s.registers[0][0]);
   s.pc=0xf035dcu;break;
  case 0xf035dcu: /* shlq    $1,r0 */
   s.c=s.registers[0][0]>>31;s.registers[0][0]=s.registers[0][0]<<1;zn(&s,s.registers[0][0]);
   s.pc=0xf035deu;break;
  case 0xf035deu: /* addq    $2,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],2u);
   s.pc=0xf035e0u;break;
  case 0xf035e0u: /* add     r1,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][1]);
   s.pc=0xf035e2u;break;
  case 0xf035e2u: /* addq    $4,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],4u);
   s.pc=0xf035e4u;break;
  case 0xf035e4u: /* load    (r0),r12 */
   CHECK(rd32(bus,&s,s.registers[0][0]&~3u,&v));s.registers[0][12]=v;
   s.pc=0xf035e6u;break;
  case 0xf035e6u: /* addq    $4,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],4u);
   s.pc=0xf035e8u;break;
  case 0xf035e8u: /* load    (r0),r14 */
   CHECK(rd32(bus,&s,s.registers[0][0]&~3u,&v));s.registers[0][14]=v;
   s.pc=0xf035eau;break;
  case 0xf035eau: /* store   r12,(r11) */
   CHECK(wr32(bus,&s,local(s.registers[0][11])?(s.registers[0][11]&~3u):s.registers[0][11],s.registers[0][12]));
   s.pc=0xf035ecu;break;
  case 0xf035ecu: /* addq    $4,r11 */
   s.registers[0][11]=add(&s,s.registers[0][11],4u);
   s.pc=0xf035eeu;break;
  case 0xf035eeu: /* store   r14,(r11) */
   CHECK(wr32(bus,&s,local(s.registers[0][11])?(s.registers[0][11]&~3u):s.registers[0][11],s.registers[0][14]));
   s.pc=0xf035f0u;break;
  case 0xf035f0u: /* move    r12,r13 */
   s.registers[0][13]=s.registers[0][12];
   s.pc=0xf035f2u;break;
  case 0xf035f2u: /* subq    $4,r11 */
   s.registers[0][11]=sub(&s,s.registers[0][11],4u);
   s.pc=0xf035f4u;break;
  case 0xf035f4u: /* shlq    $10,r13 */
   s.c=s.registers[0][13]>>31;s.registers[0][13]=s.registers[0][13]<<16;zn(&s,s.registers[0][13]);
   s.pc=0xf035f6u;break;
  case 0xf035f6u: /* shlq    $10,r14 */
   s.c=s.registers[0][14]>>31;s.registers[0][14]=s.registers[0][14]<<16;zn(&s,s.registers[0][14]);
   s.pc=0xf035f8u;break;
  case 0xf035f8u: /* sharq   $10,r12 */
   s.c=s.registers[0][12]&1u;s.registers[0][12]=sar(s.registers[0][12],16);zn(&s,s.registers[0][12]);
   s.pc=0xf035fau;break;
  case 0xf035fau: /* sharq   $10,r13 */
   s.c=s.registers[0][13]&1u;s.registers[0][13]=sar(s.registers[0][13],16);zn(&s,s.registers[0][13]);
   s.pc=0xf035fcu;break;
  case 0xf035fcu: /* sharq   $10,r14 */
   s.c=s.registers[0][14]&1u;s.registers[0][14]=sar(s.registers[0][14],16);zn(&s,s.registers[0][14]);
   s.pc=0xf035feu;break;
  case 0xf035feu: /* cmp     r19,r13 */
   (void)sub(&s,s.registers[0][13],s.registers[0][19]);
   s.pc=0xf03600u;break;
  case 0xf03600u: /* jr      n,00F03608 */
   if(condition(&s,24)){pending=1;target=0xf03608u;}
   s.pc=0xf03602u;break;
  case 0xf03602u: /* cmp     r13,r18 */
   (void)sub(&s,s.registers[0][18],s.registers[0][13]);
   s.pc=0xf03604u;break;
  case 0xf03604u: /* move    r13,r19 */
   s.registers[0][19]=s.registers[0][13];
   s.pc=0xf03606u;break;
  case 0xf03606u: /* move    r8,r25 */
   s.registers[0][25]=s.registers[0][8];
   s.pc=0xf03608u;break;
  case 0xf03608u: /* jr      nz,00F0360E */
   if(condition(&s,1)){pending=1;target=0xf0360eu;}
   s.pc=0xf0360au;break;
  case 0xf0360au: /* nop */
   s.pc=0xf0360cu;break;
  case 0xf0360cu: /* cmp     r12,r16 */
   (void)sub(&s,s.registers[0][16],s.registers[0][12]);
   s.pc=0xf0360eu;break;
  case 0xf0360eu: /* jr      n,00F0361C */
   if(condition(&s,24)){pending=1;target=0xf0361cu;}
   s.pc=0xf03610u;break;
  case 0xf03610u: /* cmp     r12,r20 */
   (void)sub(&s,s.registers[0][20],s.registers[0][12]);
   s.pc=0xf03612u;break;
  case 0xf03612u: /* move    r11,r15 */
   s.registers[0][15]=s.registers[0][11];
   s.pc=0xf03614u;break;
  case 0xf03614u: /* move    r12,r16 */
   s.registers[0][16]=s.registers[0][12];
   s.pc=0xf03616u;break;
  case 0xf03616u: /* move    r13,r17 */
   s.registers[0][17]=s.registers[0][13];
   s.pc=0xf03618u;break;
  case 0xf03618u: /* move    r8,r24 */
   s.registers[0][24]=s.registers[0][8];
   s.pc=0xf0361au;break;
  case 0xf0361au: /* move    r13,r18 */
   s.registers[0][18]=s.registers[0][13];
   s.pc=0xf0361cu;break;
  case 0xf0361cu: /* jr      n,00F03624 */
   if(condition(&s,24)){pending=1;target=0xf03624u;}
   s.pc=0xf0361eu;break;
  case 0xf0361eu: /* cmp     r21,r12 */
   (void)sub(&s,s.registers[0][12],s.registers[0][21]);
   s.pc=0xf03620u;break;
  case 0xf03620u: /* move    r12,r20 */
   s.registers[0][20]=s.registers[0][12];
   s.pc=0xf03622u;break;
  case 0xf03622u: /* move    r8,r26 */
   s.registers[0][26]=s.registers[0][8];
   s.pc=0xf03624u;break;
  case 0xf03624u: /* jr      n,00F0362C */
   if(condition(&s,24)){pending=1;target=0xf0362cu;}
   s.pc=0xf03626u;break;
  case 0xf03626u: /* cmp     r14,r22 */
   (void)sub(&s,s.registers[0][22],s.registers[0][14]);
   s.pc=0xf03628u;break;
  case 0xf03628u: /* move    r12,r21 */
   s.registers[0][21]=s.registers[0][12];
   s.pc=0xf0362au;break;
  case 0xf0362au: /* move    r8,r27 */
   s.registers[0][27]=s.registers[0][8];
   s.pc=0xf0362cu;break;
  case 0xf0362cu: /* jr      n,00F03632 */
   if(condition(&s,24)){pending=1;target=0xf03632u;}
   s.pc=0xf0362eu;break;
  case 0xf0362eu: /* cmp     r23,r14 */
   (void)sub(&s,s.registers[0][14],s.registers[0][23]);
   s.pc=0xf03630u;break;
  case 0xf03630u: /* move    r14,r22 */
   s.registers[0][22]=s.registers[0][14];
   s.pc=0xf03632u;break;
  case 0xf03632u: /* jr      n,00F03638 */
   if(condition(&s,24)){pending=1;target=0xf03638u;}
   s.pc=0xf03634u;break;
  case 0xf03634u: /* addq    $8,r8 */
   s.registers[0][8]=add(&s,s.registers[0][8],8u);
   s.pc=0xf03636u;break;
  case 0xf03636u: /* move    r14,r23 */
   s.registers[0][23]=s.registers[0][14];
   s.pc=0xf03638u;break;
  case 0xf03638u: /* cmp     r8,r9 */
   (void)sub(&s,s.registers[0][9],s.registers[0][8]);
   s.pc=0xf0363au;break;
  case 0xf0363au: /* jump    nz,(r3) */
   if(condition(&s,1)){pending=1;target=s.registers[0][3];}
   s.pc=0xf0363cu;break;
  case 0xf0363cu: /* addq    $8,r11 */
   s.registers[0][11]=add(&s,s.registers[0][11],8u);
   s.pc=0xf0363eu;break;
case 0xf0363eu: /* movefa  r6,r3 */
 s.registers[0][3]=s.registers[1][6];
 s.pc=0xf03640u;break;
  case 0xf03640u: /* cmp     r19,r18 */
   (void)sub(&s,s.registers[0][18],s.registers[0][19]);
   s.pc=0xf03642u;break;
  case 0xf03642u: /* jump    nn,(r3) */
   if(condition(&s,20)){pending=1;target=s.registers[0][3];}
   s.pc=0xf03644u;break;
  case 0xf03644u: /* moveta  r7,r13 */
   s.registers[1][13]=s.registers[0][7];
   s.pc=0xf03646u;break;
  case 0xf03646u: /* moveq   31,r1 */
   s.registers[0][1]=31u;
   s.pc=0xf03648u;break;
  case 0xf03648u: /* movei   $300,r2 */
   s.registers[0][2]=0x300u;
   s.pc=0xf0364eu;break;
  case 0xf0364eu: /* cmp     r1,r23 */
   (void)sub(&s,s.registers[0][23],s.registers[0][1]);
   s.pc=0xf03650u;break;
  case 0xf03650u: /* jump    n,(r3) */
   if(condition(&s,24)){pending=1;target=s.registers[0][3];}
   s.pc=0xf03652u;break;
  case 0xf03652u: /* cmp     r22,r2 */
   (void)sub(&s,s.registers[0][2],s.registers[0][22]);
   s.pc=0xf03654u;break;
  case 0xf03654u: /* jump    n,(r3) */
   if(condition(&s,24)){pending=1;target=s.registers[0][3];}
   s.pc=0xf03656u;break;
  case 0xf03656u: /* moveq   0,r1 */
   s.registers[0][1]=0u;
   s.pc=0xf03658u;break;
case 0xf03658u: /* movefa  r2,r2 */
 s.registers[0][2]=s.registers[1][2];
 s.pc=0xf0365au;break;
  case 0xf0365au: /* cmp     r1,r21 */
   (void)sub(&s,s.registers[0][21],s.registers[0][1]);
   s.pc=0xf0365cu;break;
  case 0xf0365cu: /* jump    n,(r3) */
   if(condition(&s,24)){pending=1;target=s.registers[0][3];}
   s.pc=0xf0365eu;break;
  case 0xf0365eu: /* cmp     r20,r2 */
   (void)sub(&s,s.registers[0][2],s.registers[0][20]);
   s.pc=0xf03660u;break;
  case 0xf03660u: /* jump    n,(r3) */
   if(condition(&s,24)){pending=1;target=s.registers[0][3];}
   s.pc=0xf03662u;break;
  case 0xf03662u: /* moveq   0,r1 */
   s.registers[0][1]=0u;
   s.pc=0xf03664u;break;
case 0xf03664u: /* movefa  r3,r2 */
 s.registers[0][2]=s.registers[1][3];
 s.pc=0xf03666u;break;
  case 0xf03666u: /* cmp     r1,r19 */
   (void)sub(&s,s.registers[0][19],s.registers[0][1]);
   s.pc=0xf03668u;break;
  case 0xf03668u: /* jump    n,(r3) */
   if(condition(&s,24)){pending=1;target=s.registers[0][3];}
   s.pc=0xf0366au;break;
  case 0xf0366au: /* cmp     r18,r2 */
   (void)sub(&s,s.registers[0][2],s.registers[0][18]);
   s.pc=0xf0366cu;break;
  case 0xf0366cu: /* jump    n,(r3) */
   if(condition(&s,24)){pending=1;target=s.registers[0][3];}
   s.pc=0xf0366eu;break;
case 0xf0366eu: /* movefa  r7,r10 */
 s.registers[0][10]=s.registers[1][7];
 s.pc=0xf03670u;break;
  case 0xf03670u: /* move    r15,r7 */
   s.registers[0][7]=s.registers[0][15];
   s.pc=0xf03672u;break;
  case 0xf03672u: /* subq    $8,r11 */
   s.registers[0][11]=sub(&s,s.registers[0][11],8u);
   s.pc=0xf03674u;break;
  case 0xf03674u: /* move    r15,r8 */
   s.registers[0][8]=s.registers[0][15];
   s.pc=0xf03676u;break;
  case 0xf03676u: /* subq    $8,r7 */
   s.registers[0][7]=sub(&s,s.registers[0][7],8u);
   s.pc=0xf03678u;break;
  case 0xf03678u: /* addq    $8,r8 */
   s.registers[0][8]=add(&s,s.registers[0][8],8u);
   s.pc=0xf0367au;break;
  case 0xf0367au: /* cmp     r10,r7 */
   (void)sub(&s,s.registers[0][7],s.registers[0][10]);
   s.pc=0xf0367cu;break;
  case 0xf0367cu: /* jr      nn,00F03682 */
   if(condition(&s,20)){pending=1;target=0xf03682u;}
   s.pc=0xf0367eu;break;
  case 0xf0367eu: /* cmp     r8,r11 */
   (void)sub(&s,s.registers[0][11],s.registers[0][8]);
   s.pc=0xf03680u;break;
  case 0xf03680u: /* move    r11,r7 */
   s.registers[0][7]=s.registers[0][11];
   s.pc=0xf03682u;break;
  case 0xf03682u: /* jr      nn,00F03688 */
   if(condition(&s,20)){pending=1;target=0xf03688u;}
   s.pc=0xf03684u;break;
  case 0xf03684u: /* nop */
   s.pc=0xf03686u;break;
  case 0xf03686u: /* move    r10,r8 */
   s.registers[0][8]=s.registers[0][10];
   s.pc=0xf03688u;break;
  case 0xf03688u: /* load    (r7),r12 */
   CHECK(rd32(bus,&s,s.registers[0][7]&~3u,&v));s.registers[0][12]=v;
   s.pc=0xf0368au;break;
  case 0xf0368au: /* load    (r8),r1 */
   CHECK(rd32(bus,&s,s.registers[0][8]&~3u,&v));s.registers[0][1]=v;
   s.pc=0xf0368cu;break;
  case 0xf0368cu: /* move    r12,r13 */
   s.registers[0][13]=s.registers[0][12];
   s.pc=0xf0368eu;break;
  case 0xf0368eu: /* move    r1,r2 */
   s.registers[0][2]=s.registers[0][1];
   s.pc=0xf03690u;break;
  case 0xf03690u: /* shlq    $10,r13 */
   s.c=s.registers[0][13]>>31;s.registers[0][13]=s.registers[0][13]<<16;zn(&s,s.registers[0][13]);
   s.pc=0xf03692u;break;
  case 0xf03692u: /* shlq    $10,r2 */
   s.c=s.registers[0][2]>>31;s.registers[0][2]=s.registers[0][2]<<16;zn(&s,s.registers[0][2]);
   s.pc=0xf03694u;break;
  case 0xf03694u: /* sharq   $10,r12 */
   s.c=s.registers[0][12]&1u;s.registers[0][12]=sar(s.registers[0][12],16);zn(&s,s.registers[0][12]);
   s.pc=0xf03696u;break;
  case 0xf03696u: /* sharq   $10,r1 */
   s.c=s.registers[0][1]&1u;s.registers[0][1]=sar(s.registers[0][1],16);zn(&s,s.registers[0][1]);
   s.pc=0xf03698u;break;
  case 0xf03698u: /* sharq   $10,r13 */
   s.c=s.registers[0][13]&1u;s.registers[0][13]=sar(s.registers[0][13],16);zn(&s,s.registers[0][13]);
   s.pc=0xf0369au;break;
  case 0xf0369au: /* sharq   $10,r2 */
   s.c=s.registers[0][2]&1u;s.registers[0][2]=sar(s.registers[0][2],16);zn(&s,s.registers[0][2]);
   s.pc=0xf0369cu;break;
  case 0xf0369cu: /* sub     r16,r1 */
   s.registers[0][1]=sub(&s,s.registers[0][1],s.registers[0][16]);
   s.pc=0xf0369eu;break;
  case 0xf0369eu: /* sub     r17,r2 */
   s.registers[0][2]=sub(&s,s.registers[0][2],s.registers[0][17]);
   s.pc=0xf036a0u;break;
  case 0xf036a0u: /* sub     r12,r16 */
   s.registers[0][16]=sub(&s,s.registers[0][16],s.registers[0][12]);
   s.pc=0xf036a2u;break;
  case 0xf036a2u: /* sub     r13,r17 */
   s.registers[0][17]=sub(&s,s.registers[0][17],s.registers[0][13]);
   s.pc=0xf036a4u;break;
  case 0xf036a4u: /* neg     r1 */
   s.registers[0][1]=sub(&s,0,s.registers[0][1]);
   s.pc=0xf036a6u;break;
  case 0xf036a6u: /* neg     r2 */
   s.registers[0][2]=sub(&s,0,s.registers[0][2]);
   s.pc=0xf036a8u;break;
  case 0xf036a8u: /* imult   r1,r17 */
   s.registers[0][17]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][17])*(int32_t)sx16(s.registers[0][1]));
   zn(&s,s.registers[0][17]);
   s.pc=0xf036aau;break;
  case 0xf036aau: /* imult   r2,r16 */
   s.registers[0][16]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][16])*(int32_t)sx16(s.registers[0][2]));
   zn(&s,s.registers[0][16]);
   s.pc=0xf036acu;break;
  case 0xf036acu: /* cmp     r16,r17 */
   (void)sub(&s,s.registers[0][17],s.registers[0][16]);
   s.pc=0xf036aeu;break;
  case 0xf036aeu: /* jump    n,(r3) */
   if(condition(&s,24)){pending=1;target=s.registers[0][3];}
   s.pc=0xf036b0u;break;
case 0xf036b0u: /* movefa  r0,r2 */
 s.registers[0][2]=s.registers[1][0];
 s.pc=0xf036b2u;break;
  case 0xf036b2u: /* movei   $f03edc,r1 */
   s.registers[0][1]=0xf03edcu;
   s.pc=0xf036b8u;break;
  case 0xf036b8u: /* cmp     r4,r2 */
   (void)sub(&s,s.registers[0][2],s.registers[0][4]);
   s.pc=0xf036bau;break;
  case 0xf036bau: /* store   r9,(r1) */
   CHECK(wr32(bus,&s,local(s.registers[0][1])?(s.registers[0][1]&~3u):s.registers[0][1],s.registers[0][9]));
   s.pc=0xf036bcu;break;
  case 0xf036bcu: /* jr      z,00F036C6 */
   if(condition(&s,2)){pending=1;target=0xf036c6u;}
   s.pc=0xf036beu;break;
  case 0xf036beu: /* subq    $4,r1 */
   s.registers[0][1]=sub(&s,s.registers[0][1],4u);
   s.pc=0xf036c0u;break;
  case 0xf036c0u: /* cmpq    $0,r6 */
   (void)sub(&s,s.registers[0][6],0x0u);
   s.pc=0xf036c2u;break;
  case 0xf036c2u: /* jr      z,00F036D4 */
   if(condition(&s,2)){pending=1;target=0xf036d4u;}
   s.pc=0xf036c4u;break;
  case 0xf036c4u: /* move    r6,r2 */
   s.registers[0][2]=s.registers[0][6];
   s.pc=0xf036c6u;break;
  case 0xf036c6u: /* moveta  r24,r21 */
   s.registers[1][21]=s.registers[0][24];
   s.pc=0xf036c8u;break;
  case 0xf036c8u: /* store   r25,(r1) */
   CHECK(wr32(bus,&s,local(s.registers[0][1])?(s.registers[0][1]&~3u):s.registers[0][1],s.registers[0][25]));
   s.pc=0xf036cau;break;
  case 0xf036cau: /* moveta  r24,r27 */
   s.registers[1][27]=s.registers[0][24];
   s.pc=0xf036ccu;break;
  case 0xf036ccu: /* moveq   0,r7 */
   s.registers[0][7]=0u;
   s.pc=0xf036ceu;break;
case 0xf036ceu: /* movefa  r3,r8 */
 s.registers[0][8]=s.registers[1][3];
 s.pc=0xf036d0u;break;
  case 0xf036d0u: /* jr      00F036E0 */
   if(condition(&s,0)){pending=1;target=0xf036e0u;}
   s.pc=0xf036d2u;break;
  case 0xf036d2u: /* moveta  r18,r29 */
   s.registers[1][29]=s.registers[0][18];
   s.pc=0xf036d4u;break;
  case 0xf036d4u: /* moveta  r26,r21 */
   s.registers[1][21]=s.registers[0][26];
   s.pc=0xf036d6u;break;
  case 0xf036d6u: /* store   r27,(r1) */
   CHECK(wr32(bus,&s,local(s.registers[0][1])?(s.registers[0][1]&~3u):s.registers[0][1],s.registers[0][27]));
   s.pc=0xf036d8u;break;
  case 0xf036d8u: /* moveta  r26,r27 */
   s.registers[1][27]=s.registers[0][26];
   s.pc=0xf036dau;break;
  case 0xf036dau: /* moveq   0,r7 */
   s.registers[0][7]=0u;
   s.pc=0xf036dcu;break;
case 0xf036dcu: /* movefa  r2,r8 */
 s.registers[0][8]=s.registers[1][2];
 s.pc=0xf036deu;break;
  case 0xf036deu: /* moveta  r20,r29 */
   s.registers[1][29]=s.registers[0][20];
   s.pc=0xf036e0u;break;
  case 0xf036e0u: /* moveta  r7,r18 */
   s.registers[1][18]=s.registers[0][7];
   s.pc=0xf036e2u;break;
  case 0xf036e2u: /* addq    $8,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],8u);
   s.pc=0xf036e4u;break;
  case 0xf036e4u: /* moveta  r8,r19 */
   s.registers[1][19]=s.registers[0][8];
   s.pc=0xf036e6u;break;
  case 0xf036e6u: /* store   r2,(r1) */
   CHECK(wr32(bus,&s,local(s.registers[0][1])?(s.registers[0][1]&~3u):s.registers[0][1],s.registers[0][2]));
   s.pc=0xf036e8u;break;
  case 0xf036e8u: /* shlq    $5,r23 */
   s.c=s.registers[0][23]>>31;s.registers[0][23]=s.registers[0][23]<<5;zn(&s,s.registers[0][23]);
   s.pc=0xf036eau;break;
case 0xf036eau: /* movefa  r1,r0 */
 s.registers[0][0]=s.registers[1][1];
 s.pc=0xf036ecu;break;
  case 0xf036ecu: /* cmp     r23,r0 */
   (void)sub(&s,s.registers[0][0],s.registers[0][23]);
   s.pc=0xf036eeu;break;
  case 0xf036eeu: /* jr      nn,00F036F4 */
   if(condition(&s,20)){pending=1;target=0xf036f4u;}
   s.pc=0xf036f0u;break;
case 0xf036f0u: /* movefa  r0,r1 */
 s.registers[0][1]=s.registers[1][0];
 s.pc=0xf036f2u;break;
  case 0xf036f2u: /* move    r0,r23 */
   s.registers[0][23]=s.registers[0][0];
   s.pc=0xf036f4u;break;
  case 0xf036f4u: /* neg     r23 */
   s.registers[0][23]=sub(&s,0,s.registers[0][23]);
   s.pc=0xf036f6u;break;
  case 0xf036f6u: /* moveta  r4,r16 */
   s.registers[1][16]=s.registers[0][4];
   s.pc=0xf036f8u;break;
  case 0xf036f8u: /* shlq    $10,r23 */
   s.c=s.registers[0][23]>>31;s.registers[0][23]=s.registers[0][23]<<16;zn(&s,s.registers[0][23]);
   s.pc=0xf036fau;break;
  case 0xf036fau: /* movei   $f03ed0,r2 */
   s.registers[0][2]=0xf03ed0u;
   s.pc=0xf03700u;break;
  case 0xf03700u: /* shrq    $8,r23 */
   s.c=s.registers[0][23]&1u;s.registers[0][23]=s.registers[0][23]>>8;zn(&s,s.registers[0][23]);
   s.pc=0xf03702u;break;
  case 0xf03702u: /* cmp     r1,r4 */
   (void)sub(&s,s.registers[0][4],s.registers[0][1]);
   s.pc=0xf03704u;break;
  case 0xf03704u: /* moveta  r23,r28 */
   s.registers[1][28]=s.registers[0][23];
   s.pc=0xf03706u;break;
  case 0xf03706u: /* jr      z,00F03726 */
   if(condition(&s,2)){pending=1;target=0xf03726u;}
   s.pc=0xf03708u;break;
  case 0xf03708u: /* shlq    $3,r4 */
   s.c=s.registers[0][4]>>31;s.registers[0][4]=s.registers[0][4]<<3;zn(&s,s.registers[0][4]);
   s.pc=0xf0370au;break;
  case 0xf0370au: /* load    (r2),r0 */
   CHECK(rd32(bus,&s,s.registers[0][2]&~3u,&v));s.registers[0][0]=v;
   s.pc=0xf0370cu;break;
  case 0xf0370cu: /* add     r0,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],s.registers[0][0]);
   s.pc=0xf0370eu;break;
  case 0xf0370eu: /* addq    $4,r2 */
   s.registers[0][2]=add(&s,s.registers[0][2],4u);
   s.pc=0xf03710u;break;
  case 0xf03710u: /* load    (r4),r0 */
   CHECK(rd32(bus,&s,s.registers[0][4]&~3u,&v));s.registers[0][0]=v;
   s.pc=0xf03712u;break;
  case 0xf03712u: /* load    (r2),r1 */
   CHECK(rd32(bus,&s,s.registers[0][2]&~3u,&v));s.registers[0][1]=v;
   s.pc=0xf03714u;break;
  case 0xf03714u: /* shlq    $2,r5 */
   s.c=s.registers[0][5]>>31;s.registers[0][5]=s.registers[0][5]<<2;zn(&s,s.registers[0][5]);
   s.pc=0xf03716u;break;
  case 0xf03716u: /* moveta  r0,r22 */
   s.registers[1][22]=s.registers[0][0];
   s.pc=0xf03718u;break;
  case 0xf03718u: /* add     r1,r5 */
   s.registers[0][5]=add(&s,s.registers[0][5],s.registers[0][1]);
   s.pc=0xf0371au;break;
  case 0xf0371au: /* addq    $4,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],4u);
   s.pc=0xf0371cu;break;
  case 0xf0371cu: /* load    (r5),r0 */
   CHECK(rd32(bus,&s,s.registers[0][5]&~3u,&v));s.registers[0][0]=v;
   s.pc=0xf0371eu;break;
  case 0xf0371eu: /* load    (r4),r1 */
   CHECK(rd32(bus,&s,s.registers[0][4]&~3u,&v));s.registers[0][1]=v;
   s.pc=0xf03720u;break;
  case 0xf03720u: /* moveta  r0,r17 */
   s.registers[1][17]=s.registers[0][0];
   s.pc=0xf03722u;break;
  case 0xf03722u: /* jr      00F03740 */
   if(condition(&s,0)){pending=1;target=0xf03740u;}
   s.pc=0xf03724u;break;
  case 0xf03724u: /* moveta  r1,r23 */
   s.registers[1][23]=s.registers[0][1];
   s.pc=0xf03726u;break;
  case 0xf03726u: /* move    r6,r0 */
   s.registers[0][0]=s.registers[0][6];
   s.pc=0xf03728u;break;
  case 0xf03728u: /* shrq    $8,r1 */
   s.c=s.registers[0][1]&1u;s.registers[0][1]=s.registers[0][1]>>8;zn(&s,s.registers[0][1]);
   s.pc=0xf0372au;break;
  case 0xf0372au: /* shlq    $8,r23 */
   s.c=s.registers[0][23]>>31;s.registers[0][23]=s.registers[0][23]<<8;zn(&s,s.registers[0][23]);
   s.pc=0xf0372cu;break;
  case 0xf0372cu: /* and     r1,r0 */
   s.registers[0][0]&=s.registers[0][1];
   zn(&s,s.registers[0][0]);
   s.pc=0xf0372eu;break;
  case 0xf0372eu: /* sharq   $18,r23 */
   s.c=s.registers[0][23]&1u;s.registers[0][23]=sar(s.registers[0][23],24);zn(&s,s.registers[0][23]);
   s.pc=0xf03730u;break;
  case 0xf03730u: /* shlq    $8,r1 */
   s.c=s.registers[0][1]>>31;s.registers[0][1]=s.registers[0][1]<<8;zn(&s,s.registers[0][1]);
   s.pc=0xf03732u;break;
  case 0xf03732u: /* add     r23,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][23]);
   s.pc=0xf03734u;break;
  case 0xf03734u: /* and     r1,r6 */
   s.registers[0][6]&=s.registers[0][1];
   zn(&s,s.registers[0][6]);
   s.pc=0xf03736u;break;
case 0xf03736u: /* sat8    r0 */
 s.registers[0][0]=(s.registers[0][0]&0x80000000u)?0u:(s.registers[0][0]>255u?255u:s.registers[0][0]);
 zn(&s,s.registers[0][0]);
 s.pc=0xf03738u;break;
  case 0xf03738u: /* or      r0,r6 */
   s.registers[0][6]|=s.registers[0][0];
   zn(&s,s.registers[0][6]);
   s.pc=0xf0373au;break;
  case 0xf0373au: /* move    r6,r1 */
   s.registers[0][1]=s.registers[0][6];
   s.pc=0xf0373cu;break;
  case 0xf0373cu: /* shlq    $10,r1 */
   s.c=s.registers[0][1]>>31;s.registers[0][1]=s.registers[0][1]<<16;zn(&s,s.registers[0][1]);
   s.pc=0xf0373eu;break;
  case 0xf0373eu: /* or      r1,r6 */
   s.registers[0][6]|=s.registers[0][1];
   zn(&s,s.registers[0][6]);
   s.pc=0xf03740u;break;
  case 0xf03740u: /* moveta  r6,r15 */
   s.registers[1][15]=s.registers[0][6];
   s.pc=0xf03742u;break;
  case 0xf03742u: /* movei   $f03ee0,r4 */
   s.registers[0][4]=0xf03ee0u;
   s.pc=0xf03748u;break;
  case 0xf03748u: /* moveq   1,r0 */
   s.registers[0][0]=1u;
   s.pc=0xf0374au;break;
case 0xf0374au: /* movefa  r0,r1 */
 s.registers[0][1]=s.registers[1][0];
 s.pc=0xf0374cu;break;
  case 0xf0374cu: /* moveta  r0,r20 */
   s.registers[1][20]=s.registers[0][0];
   s.pc=0xf0374eu;break;
case 0xf0374eu: /* movefa  r16,r2 */
 s.registers[0][2]=s.registers[1][16];
 s.pc=0xf03750u;break;
  case 0xf03750u: /* load    (r4),r3 */
   CHECK(rd32(bus,&s,s.registers[0][4]&~3u,&v));s.registers[0][3]=v;
   s.pc=0xf03752u;break;
  case 0xf03752u: /* cmp     r1,r2 */
   (void)sub(&s,s.registers[0][2],s.registers[0][1]);
   s.pc=0xf03754u;break;
  case 0xf03754u: /* jr      z,00F03770 */
   if(condition(&s,2)){pending=1;target=0xf03770u;}
   s.pc=0xf03756u;break;
  case 0xf03756u: /* cmpq    $0,r3 */
   (void)sub(&s,s.registers[0][3],0x0u);
   s.pc=0xf03758u;break;
case 0xf03758u: /* movefa  r22,r24 */
 s.registers[0][24]=s.registers[1][22];
 s.pc=0xf0375au;break;
case 0xf0375au: /* movefa  r23,r25 */
 s.registers[0][25]=s.registers[1][23];
 s.pc=0xf0375cu;break;
  case 0xf0375cu: /* movei   $f03b22,r23 */
   s.registers[0][23]=0xf03b22u;
   s.pc=0xf03762u;break;
  case 0xf03762u: /* jr      nz,00F03780 */
   if(condition(&s,1)){pending=1;target=0xf03780u;}
   s.pc=0xf03764u;break;
  case 0xf03764u: /* moveta  r0,r26 */
   s.registers[1][26]=s.registers[0][0];
   s.pc=0xf03766u;break;
  case 0xf03766u: /* movei   $f0398a,r23 */
   s.registers[0][23]=0xf0398au;
   s.pc=0xf0376cu;break;
  case 0xf0376cu: /* jr      00F03780 */
   if(condition(&s,0)){pending=1;target=0xf03780u;}
   s.pc=0xf0376eu;break;
  case 0xf0376eu: /* nop */
   s.pc=0xf03770u;break;
  case 0xf03770u: /* movei   $f03c3e,r23 */
   s.registers[0][23]=0xf03c3eu;
   s.pc=0xf03776u;break;
  case 0xf03776u: /* jr      nz,00F03780 */
   if(condition(&s,1)){pending=1;target=0xf03780u;}
   s.pc=0xf03778u;break;
  case 0xf03778u: /* moveta  r0,r26 */
   s.registers[1][26]=s.registers[0][0];
   s.pc=0xf0377au;break;
  case 0xf0377au: /* movei   $f03ab2,r23 */
   s.registers[0][23]=0xf03ab2u;
   s.pc=0xf03780u;break;
  case 0xf03780u: /* movei   $13e20,r26 */
   s.registers[0][26]=0x13e20u;
   s.pc=0xf03786u;break;
case 0xf03786u: /* movefa  r28,r27 */
 s.registers[0][27]=s.registers[1][28];
 s.pc=0xf03788u;break;
case 0xf03788u: /* movefa  r29,r21 */
 s.registers[0][21]=s.registers[1][29];
 s.pc=0xf0378au;break;
  case 0xf0378au: /* move    pc,r22 */
   s.registers[0][22]=0xf0378au;
   s.pc=0xf0378cu;break;
  case 0xf0378cu: /* subq    $1,r21 */
   s.registers[0][21]=sub(&s,s.registers[0][21],1u);
   s.pc=0xf0378eu;break;
  case 0xf0378eu: /* addq    $6,r22 */
   s.registers[0][22]=add(&s,s.registers[0][22],6u);
   s.pc=0xf03790u;break;
case 0xf03790u: /* movefa  r20,r0 */
 s.registers[0][0]=s.registers[1][20];
 s.pc=0xf03792u;break;
  case 0xf03792u: /* add     r10,r9 */
   s.registers[0][9]=add(&s,s.registers[0][9],s.registers[0][10]);
   s.pc=0xf03794u;break;
  case 0xf03794u: /* subq    $1,r0 */
   s.registers[0][0]=sub(&s,s.registers[0][0],1u);
   s.pc=0xf03796u;break;
  case 0xf03796u: /* jr      nz,00F0379E */
   if(condition(&s,1)){pending=1;target=0xf0379eu;}
   s.pc=0xf03798u;break;
  case 0xf03798u: /* moveta  r0,r20 */
   s.registers[1][20]=s.registers[0][0];
   s.pc=0xf0379au;break;
case 0xf0379au: /* movefa  r4,r3 */
 s.registers[0][3]=s.registers[1][4];
 s.pc=0xf0379cu;break;
  case 0xf0379cu: /* jump    (r3) */
   if(condition(&s,0)){pending=1;target=s.registers[0][3];}
   s.pc=0xf0379eu;break;
case 0xf0379eu: /* movefa  r24,r1 */
 s.registers[0][1]=s.registers[1][24];
 s.pc=0xf037a0u;break;
case 0xf037a0u: /* movefa  r25,r2 */
 s.registers[0][2]=s.registers[1][25];
 s.pc=0xf037a2u;break;
case 0xf037a2u: /* movefa  r22,r11 */
 s.registers[0][11]=s.registers[1][22];
 s.pc=0xf037a4u;break;
case 0xf037a4u: /* movefa  r23,r12 */
 s.registers[0][12]=s.registers[1][23];
 s.pc=0xf037a6u;break;
  case 0xf037a6u: /* add     r1,r11 */
   s.registers[0][11]=add(&s,s.registers[0][11],s.registers[0][1]);
   s.pc=0xf037a8u;break;
  case 0xf037a8u: /* add     r2,r12 */
   s.registers[0][12]=add(&s,s.registers[0][12],s.registers[0][2]);
   s.pc=0xf037aau;break;
  case 0xf037aau: /* add     r14,r13 */
   s.registers[0][13]=add(&s,s.registers[0][13],s.registers[0][14]);
   s.pc=0xf037acu;break;
  case 0xf037acu: /* moveta  r11,r22 */
   s.registers[1][22]=s.registers[0][11];
   s.pc=0xf037aeu;break;
  case 0xf037aeu: /* moveta  r12,r23 */
   s.registers[1][23]=s.registers[0][12];
   s.pc=0xf037b0u;break;
case 0xf037b0u: /* movefa  r26,r0 */
 s.registers[0][0]=s.registers[1][26];
 s.pc=0xf037b2u;break;
  case 0xf037b2u: /* add     r16,r15 */
   s.registers[0][15]=add(&s,s.registers[0][15],s.registers[0][16]);
   s.pc=0xf037b4u;break;
  case 0xf037b4u: /* subq    $1,r0 */
   s.registers[0][0]=sub(&s,s.registers[0][0],1u);
   s.pc=0xf037b6u;break;
  case 0xf037b6u: /* jr      nz,00F037BE */
   if(condition(&s,1)){pending=1;target=0xf037beu;}
   s.pc=0xf037b8u;break;
  case 0xf037b8u: /* moveta  r0,r26 */
   s.registers[1][26]=s.registers[0][0];
   s.pc=0xf037bau;break;
case 0xf037bau: /* movefa  r5,r3 */
 s.registers[0][3]=s.registers[1][5];
 s.pc=0xf037bcu;break;
  case 0xf037bcu: /* jump    (r3) */
   if(condition(&s,0)){pending=1;target=s.registers[0][3];}
   s.pc=0xf037beu;break;
case 0xf037beu: /* movefa  r30,r1 */
 s.registers[0][1]=s.registers[1][30];
 s.pc=0xf037c0u;break;
case 0xf037c0u: /* movefa  r31,r2 */
 s.registers[0][2]=s.registers[1][31];
 s.pc=0xf037c2u;break;
case 0xf037c2u: /* movefa  r28,r17 */
 s.registers[0][17]=s.registers[1][28];
 s.pc=0xf037c4u;break;
case 0xf037c4u: /* movefa  r29,r18 */
 s.registers[0][18]=s.registers[1][29];
 s.pc=0xf037c6u;break;
  case 0xf037c6u: /* add     r1,r17 */
   s.registers[0][17]=add(&s,s.registers[0][17],s.registers[0][1]);
   s.pc=0xf037c8u;break;
  case 0xf037c8u: /* add     r2,r18 */
   s.registers[0][18]=add(&s,s.registers[0][18],s.registers[0][2]);
   s.pc=0xf037cau;break;
  case 0xf037cau: /* add     r20,r19 */
   s.registers[0][19]=add(&s,s.registers[0][19],s.registers[0][20]);
   s.pc=0xf037ccu;break;
  case 0xf037ccu: /* moveta  r17,r28 */
   s.registers[1][28]=s.registers[0][17];
   s.pc=0xf037ceu;break;
  case 0xf037ceu: /* moveta  r18,r29 */
   s.registers[1][29]=s.registers[0][18];
   s.pc=0xf037d0u;break;
case 0xf037d0u: /* movefa  r18,r4 */
 s.registers[0][4]=s.registers[1][18];
 s.pc=0xf037d2u;break;
  case 0xf037d2u: /* addq    $1,r21 */
   s.registers[0][21]=add(&s,s.registers[0][21],1u);
   s.pc=0xf037d4u;break;
case 0xf037d4u: /* movefa  r19,r5 */
 s.registers[0][5]=s.registers[1][19];
 s.pc=0xf037d6u;break;
  case 0xf037d6u: /* cmp     r4,r21 */
   (void)sub(&s,s.registers[0][21],s.registers[0][4]);
   s.pc=0xf037d8u;break;
  case 0xf037d8u: /* jump    n,(r22) */
   if(condition(&s,24)){pending=1;target=s.registers[0][22];}
   s.pc=0xf037dau;break;
  case 0xf037dau: /* cmp     r5,r21 */
   (void)sub(&s,s.registers[0][21],s.registers[0][5]);
   s.pc=0xf037dcu;break;
  case 0xf037dcu: /* jump    n,(r23) */
   if(condition(&s,24)){pending=1;target=s.registers[0][23];}
   s.pc=0xf037deu;break;
case 0xf037deu: /* movefa  r1,r0 */
 s.registers[0][0]=s.registers[1][1];
 s.pc=0xf037e0u;break;
  case 0xf037e0u: /* movei   $f03ecc,r5 */
   s.registers[0][5]=0xf03eccu;
   s.pc=0xf037e6u;break;
  case 0xf037e6u: /* load    (r5),r6 */
   CHECK(rd32(bus,&s,s.registers[0][5]&~3u,&v));s.registers[0][6]=v;
   s.pc=0xf037e8u;break;
  case 0xf037e8u: /* movei   $f035aa,r4 */
   s.registers[0][4]=0xf035aau;
   s.pc=0xf037eeu;break;
  case 0xf037eeu: /* subq    $1,r6 */
   s.registers[0][6]=sub(&s,s.registers[0][6],1u);
   s.pc=0xf037f0u;break;
  case 0xf037f0u: /* jump    nz,(r4) */
   if(condition(&s,1)){pending=1;target=s.registers[0][4];}
   s.pc=0xf037f2u;break;
  case 0xf037f2u: /* store   r6,(r5) */
   CHECK(wr32(bus,&s,local(s.registers[0][5])?(s.registers[0][5]&~3u):s.registers[0][5],s.registers[0][6]));
   s.pc=0xf037f4u;break;
  case 0xf037f4u: /* movei   $f031be,r6 */
   s.registers[0][6]=0xf031beu;
   s.pc=0xf037fau;break;
  case 0xf037fau: /* movei   $f03204,r5 */
   s.registers[0][5]=0xf03204u;
   s.pc=0xf03800u;break;
  case 0xf03800u: /* movei   $6380,r4 */
   s.registers[0][4]=0x6380u;
   s.pc=0xf03806u;break;
  case 0xf03806u: /* jump    (r6) */
   if(condition(&s,0)){pending=1;target=s.registers[0][6];}
   s.pc=0xf03808u;break;
  case 0xf03808u: /* store   r4,(r5) */
   CHECK(wr32(bus,&s,local(s.registers[0][5])?(s.registers[0][5]&~3u):s.registers[0][5],s.registers[0][4]));
   s.pc=0xf0380au;break;
  case 0xf0380au: /* movei   $f03ed8,r2 */
   s.registers[0][2]=0xf03ed8u;
   s.pc=0xf03810u;break;
case 0xf03810u: /* movefa  r21,r4 */
 s.registers[0][4]=s.registers[1][21];
 s.pc=0xf03812u;break;
  case 0xf03812u: /* load    (r2),r0 */
   CHECK(rd32(bus,&s,s.registers[0][2]&~3u,&v));s.registers[0][0]=v;
   s.pc=0xf03814u;break;
case 0xf03814u: /* movefa  r6,r1 */
 s.registers[0][1]=s.registers[1][6];
 s.pc=0xf03816u;break;
  case 0xf03816u: /* cmp     r4,r0 */
   (void)sub(&s,s.registers[0][0],s.registers[0][4]);
   s.pc=0xf03818u;break;
  case 0xf03818u: /* jump    z,(r1) */
   if(condition(&s,2)){pending=1;target=s.registers[0][1];}
   s.pc=0xf0381au;break;
  case 0xf0381au: /* addq    $4,r2 */
   s.registers[0][2]=add(&s,s.registers[0][2],4u);
   s.pc=0xf0381cu;break;
  case 0xf0381cu: /* move    r4,r5 */
   s.registers[0][5]=s.registers[0][4];
   s.pc=0xf0381eu;break;
  case 0xf0381eu: /* load    (r2),r0 */
   CHECK(rd32(bus,&s,s.registers[0][2]&~3u,&v));s.registers[0][0]=v;
   s.pc=0xf03820u;break;
  case 0xf03820u: /* subq    $8,r5 */
   s.registers[0][5]=sub(&s,s.registers[0][5],8u);
   s.pc=0xf03822u;break;
case 0xf03822u: /* subqt   $8,r0 */
 s.registers[0][0]-=8u;
 s.pc=0xf03824u;break;
  case 0xf03824u: /* jr      nn,00F0382A */
   if(condition(&s,20)){pending=1;target=0xf0382au;}
   s.pc=0xf03826u;break;
  case 0xf03826u: /* addq    $4,r2 */
   s.registers[0][2]=add(&s,s.registers[0][2],4u);
   s.pc=0xf03828u;break;
  case 0xf03828u: /* move    r0,r5 */
   s.registers[0][5]=s.registers[0][0];
   s.pc=0xf0382au;break;
case 0xf0382au: /* movefa  r7,r6 */
 s.registers[0][6]=s.registers[1][7];
 s.pc=0xf0382cu;break;
  case 0xf0382cu: /* load    (r2),r1 */
   CHECK(rd32(bus,&s,s.registers[0][2]&~3u,&v));s.registers[0][1]=v;
   s.pc=0xf0382eu;break;
case 0xf0382eu: /* movefa  r7,r7 */
 s.registers[0][7]=s.registers[1][7];
 s.pc=0xf03830u;break;
  case 0xf03830u: /* add     r4,r6 */
   s.registers[0][6]=add(&s,s.registers[0][6],s.registers[0][4]);
   s.pc=0xf03832u;break;
  case 0xf03832u: /* add     r5,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],s.registers[0][5]);
   s.pc=0xf03834u;break;
  case 0xf03834u: /* load    (r6),r9 */
   CHECK(rd32(bus,&s,s.registers[0][6]&~3u,&v));s.registers[0][9]=v;
   s.pc=0xf03836u;break;
  case 0xf03836u: /* load    (r7),r10 */
   CHECK(rd32(bus,&s,s.registers[0][7]&~3u,&v));s.registers[0][10]=v;
   s.pc=0xf03838u;break;
  case 0xf03838u: /* cmpq    $0,r1 */
   (void)sub(&s,s.registers[0][1],0x0u);
   s.pc=0xf0383au;break;
  case 0xf0383au: /* jr      nz,00F03842 */
   if(condition(&s,1)){pending=1;target=0xf03842u;}
   s.pc=0xf0383cu;break;
  case 0xf0383cu: /* moveta  r5,r21 */
   s.registers[1][21]=s.registers[0][5];
   s.pc=0xf0383eu;break;
case 0xf0383eu: /* rorq    $10,r9 */
 v=s.registers[0][9];s.c=v>>31;
 s.registers[0][9]=(v>>16)|(v<<16);
 zn(&s,s.registers[0][9]);
 s.pc=0xf03840u;break;
case 0xf03840u: /* rorq    $10,r10 */
 v=s.registers[0][10];s.c=v>>31;
 s.registers[0][10]=(v>>16)|(v<<16);
 zn(&s,s.registers[0][10]);
 s.pc=0xf03842u;break;
  case 0xf03842u: /* move    r9,r2 */
   s.registers[0][2]=s.registers[0][9];
   s.pc=0xf03844u;break;
  case 0xf03844u: /* move    r10,r8 */
   s.registers[0][8]=s.registers[0][10];
   s.pc=0xf03846u;break;
  case 0xf03846u: /* shlq    $10,r2 */
   s.c=s.registers[0][2]>>31;s.registers[0][2]=s.registers[0][2]<<16;zn(&s,s.registers[0][2]);
   s.pc=0xf03848u;break;
  case 0xf03848u: /* shlq    $10,r8 */
   s.c=s.registers[0][8]>>31;s.registers[0][8]=s.registers[0][8]<<16;zn(&s,s.registers[0][8]);
   s.pc=0xf0384au;break;
  case 0xf0384au: /* sharq   $10,r2 */
   s.c=s.registers[0][2]&1u;s.registers[0][2]=sar(s.registers[0][2],16);zn(&s,s.registers[0][2]);
   s.pc=0xf0384cu;break;
  case 0xf0384cu: /* sharq   $10,r8 */
   s.c=s.registers[0][8]&1u;s.registers[0][8]=sar(s.registers[0][8],16);zn(&s,s.registers[0][8]);
   s.pc=0xf0384eu;break;
  case 0xf0384eu: /* sharq   $10,r9 */
   s.c=s.registers[0][9]&1u;s.registers[0][9]=sar(s.registers[0][9],16);zn(&s,s.registers[0][9]);
   s.pc=0xf03850u;break;
  case 0xf03850u: /* sharq   $10,r10 */
   s.c=s.registers[0][10]&1u;s.registers[0][10]=sar(s.registers[0][10],16);zn(&s,s.registers[0][10]);
   s.pc=0xf03852u;break;
  case 0xf03852u: /* sub     r2,r8 */
   s.registers[0][8]=sub(&s,s.registers[0][8],s.registers[0][2]);
   s.pc=0xf03854u;break;
  case 0xf03854u: /* jr      nz,00F0385A */
   if(condition(&s,1)){pending=1;target=0xf0385au;}
   s.pc=0xf03856u;break;
  case 0xf03856u: /* moveta  r8,r20 */
   s.registers[1][20]=s.registers[0][8];
   s.pc=0xf03858u;break;
  case 0xf03858u: /* jump    (r3) */
   if(condition(&s,0)){pending=1;target=s.registers[0][3];}
   s.pc=0xf0385au;break;
  case 0xf0385au: /* shlq    $10,r9 */
   s.c=s.registers[0][9]>>31;s.registers[0][9]=s.registers[0][9]<<16;zn(&s,s.registers[0][9]);
   s.pc=0xf0385cu;break;
  case 0xf0385cu: /* shlq    $10,r10 */
   s.c=s.registers[0][10]>>31;s.registers[0][10]=s.registers[0][10]<<16;zn(&s,s.registers[0][10]);
   s.pc=0xf0385eu;break;
  case 0xf0385eu: /* addqt   $4,r6 */
   s.registers[0][6]+=4u;
   s.pc=0xf03860u;break;
  case 0xf03860u: /* sub     r9,r10 */
   s.registers[0][10]=sub(&s,s.registers[0][10],s.registers[0][9]);
   s.pc=0xf03862u;break;
  case 0xf03862u: /* addqt   $4,r7 */
   s.registers[0][7]+=4u;
   s.pc=0xf03864u;break;
  case 0xf03864u: /* abs     r10 */
   s.c=s.registers[0][10]>>31;if(s.registers[0][10]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[0][10]=0u-s.registers[0][10];s.n=0;s.z=s.registers[0][10]==0;}
   s.pc=0xf03866u;break;
  case 0xf03866u: /* div     r8,r10 */
   divide(&s,8,10);
   s.pc=0xf03868u;break;
  case 0xf03868u: /* load    (r6),r13 */
   CHECK(rd32(bus,&s,s.registers[0][6]&~3u,&v));s.registers[0][13]=v;
   s.pc=0xf0386au;break;
  case 0xf0386au: /* load    (r7),r14 */
   CHECK(rd32(bus,&s,s.registers[0][7]&~3u,&v));s.registers[0][14]=v;
   s.pc=0xf0386cu;break;
case 0xf0386cu: /* movefa  r17,r6 */
 s.registers[0][6]=s.registers[1][17];
 s.pc=0xf0386eu;break;
  case 0xf0386eu: /* movei   $f037ac,r3 */
   s.registers[0][3]=0xf037acu;
   s.pc=0xf03874u;break;
case 0xf03874u: /* movefa  r17,r7 */
 s.registers[0][7]=s.registers[1][17];
 s.pc=0xf03876u;break;
case 0xf03876u: /* movefa  r0,r1 */
 s.registers[0][1]=s.registers[1][0];
 s.pc=0xf03878u;break;
  case 0xf03878u: /* jr      nc,00F0387E */
   if(condition(&s,4)){pending=1;target=0xf0387eu;}
   s.pc=0xf0387au;break;
case 0xf0387au: /* movefa  r16,r2 */
 s.registers[0][2]=s.registers[1][16];
 s.pc=0xf0387cu;break;
  case 0xf0387cu: /* neg     r10 */
   s.registers[0][10]=sub(&s,0,s.registers[0][10]);
   s.pc=0xf0387eu;break;
  case 0xf0387eu: /* sharq   $1,r4 */
   s.c=s.registers[0][4]&1u;s.registers[0][4]=sar(s.registers[0][4],1);zn(&s,s.registers[0][4]);
   s.pc=0xf03880u;break;
  case 0xf03880u: /* cmp     r1,r2 */
   (void)sub(&s,s.registers[0][2],s.registers[0][1]);
   s.pc=0xf03882u;break;
  case 0xf03882u: /* jump    z,(r3) */
   if(condition(&s,2)){pending=1;target=s.registers[0][3];}
   s.pc=0xf03884u;break;
  case 0xf03884u: /* sharq   $1,r5 */
   s.c=s.registers[0][5]&1u;s.registers[0][5]=sar(s.registers[0][5],1);zn(&s,s.registers[0][5]);
   s.pc=0xf03886u;break;
  case 0xf03886u: /* shrq    $10,r13 */
   s.c=s.registers[0][13]&1u;s.registers[0][13]=s.registers[0][13]>>16;zn(&s,s.registers[0][13]);
   s.pc=0xf03888u;break;
  case 0xf03888u: /* shrq    $10,r14 */
   s.c=s.registers[0][14]&1u;s.registers[0][14]=s.registers[0][14]>>16;zn(&s,s.registers[0][14]);
   s.pc=0xf0388au;break;
  case 0xf0388au: /* add     r4,r6 */
   s.registers[0][6]=add(&s,s.registers[0][6],s.registers[0][4]);
   s.pc=0xf0388cu;break;
  case 0xf0388cu: /* add     r5,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],s.registers[0][5]);
   s.pc=0xf0388eu;break;
  case 0xf0388eu: /* load    (r6),r11 */
   CHECK(rd32(bus,&s,s.registers[0][6]&~3u,&v));s.registers[0][11]=v;
   s.pc=0xf03890u;break;
  case 0xf03890u: /* load    (r7),r1 */
   CHECK(rd32(bus,&s,s.registers[0][7]&~3u,&v));s.registers[0][1]=v;
   s.pc=0xf03892u;break;
  case 0xf03892u: /* move    r11,r12 */
   s.registers[0][12]=s.registers[0][11];
   s.pc=0xf03894u;break;
  case 0xf03894u: /* move    r1,r2 */
   s.registers[0][2]=s.registers[0][1];
   s.pc=0xf03896u;break;
  case 0xf03896u: /* shrq    $10,r11 */
   s.c=s.registers[0][11]&1u;s.registers[0][11]=s.registers[0][11]>>16;zn(&s,s.registers[0][11]);
   s.pc=0xf03898u;break;
  case 0xf03898u: /* shrq    $10,r1 */
   s.c=s.registers[0][1]&1u;s.registers[0][1]=s.registers[0][1]>>16;zn(&s,s.registers[0][1]);
   s.pc=0xf0389au;break;
  case 0xf0389au: /* mult    r13,r11 */
   s.registers[0][11]=(s.registers[0][11]&0xffffu)*(s.registers[0][13]&0xffffu);
   zn(&s,s.registers[0][11]);
   s.pc=0xf0389cu;break;
  case 0xf0389cu: /* mult    r14,r1 */
   s.registers[0][1]=(s.registers[0][1]&0xffffu)*(s.registers[0][14]&0xffffu);
   zn(&s,s.registers[0][1]);
   s.pc=0xf0389eu;break;
  case 0xf0389eu: /* mult    r13,r12 */
   s.registers[0][12]=(s.registers[0][12]&0xffffu)*(s.registers[0][13]&0xffffu);
   zn(&s,s.registers[0][12]);
   s.pc=0xf038a0u;break;
  case 0xf038a0u: /* mult    r14,r2 */
   s.registers[0][2]=(s.registers[0][2]&0xffffu)*(s.registers[0][14]&0xffffu);
   zn(&s,s.registers[0][2]);
   s.pc=0xf038a2u;break;
  case 0xf038a2u: /* shlq    $10,r13 */
   s.c=s.registers[0][13]>>31;s.registers[0][13]=s.registers[0][13]<<16;zn(&s,s.registers[0][13]);
   s.pc=0xf038a4u;break;
  case 0xf038a4u: /* sub     r11,r1 */
   s.registers[0][1]=sub(&s,s.registers[0][1],s.registers[0][11]);
   s.pc=0xf038a6u;break;
  case 0xf038a6u: /* shlq    $10,r14 */
   s.c=s.registers[0][14]>>31;s.registers[0][14]=s.registers[0][14]<<16;zn(&s,s.registers[0][14]);
   s.pc=0xf038a8u;break;
  case 0xf038a8u: /* abs     r1 */
   s.c=s.registers[0][1]>>31;if(s.registers[0][1]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[0][1]=0u-s.registers[0][1];s.n=0;s.z=s.registers[0][1]==0;}
   s.pc=0xf038aau;break;
  case 0xf038aau: /* div     r8,r1 */
   divide(&s,8,1);
   s.pc=0xf038acu;break;
  case 0xf038acu: /* jr      nc,00F038B2 */
   if(condition(&s,4)){pending=1;target=0xf038b2u;}
   s.pc=0xf038aeu;break;
  case 0xf038aeu: /* sub     r12,r2 */
   s.registers[0][2]=sub(&s,s.registers[0][2],s.registers[0][12]);
   s.pc=0xf038b0u;break;
  case 0xf038b0u: /* neg     r1 */
   s.registers[0][1]=sub(&s,0,s.registers[0][1]);
   s.pc=0xf038b2u;break;
  case 0xf038b2u: /* abs     r2 */
   s.c=s.registers[0][2]>>31;if(s.registers[0][2]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[0][2]=0u-s.registers[0][2];s.n=0;s.z=s.registers[0][2]==0;}
   s.pc=0xf038b4u;break;
  case 0xf038b4u: /* div     r8,r2 */
   divide(&s,8,2);
   s.pc=0xf038b6u;break;
  case 0xf038b6u: /* jr      nc,00F038BC */
   if(condition(&s,4)){pending=1;target=0xf038bcu;}
   s.pc=0xf038b8u;break;
  case 0xf038b8u: /* sub     r13,r14 */
   s.registers[0][14]=sub(&s,s.registers[0][14],s.registers[0][13]);
   s.pc=0xf038bau;break;
  case 0xf038bau: /* neg     r2 */
   s.registers[0][2]=sub(&s,0,s.registers[0][2]);
   s.pc=0xf038bcu;break;
  case 0xf038bcu: /* abs     r14 */
   s.c=s.registers[0][14]>>31;if(s.registers[0][14]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[0][14]=0u-s.registers[0][14];s.n=0;s.z=s.registers[0][14]==0;}
   s.pc=0xf038beu;break;
  case 0xf038beu: /* div     r8,r14 */
   divide(&s,8,14);
   s.pc=0xf038c0u;break;
  case 0xf038c0u: /* jr      nc,00F038C6 */
   if(condition(&s,4)){pending=1;target=0xf038c6u;}
   s.pc=0xf038c2u;break;
  case 0xf038c2u: /* moveta  r1,r24 */
   s.registers[1][24]=s.registers[0][1];
   s.pc=0xf038c4u;break;
  case 0xf038c4u: /* neg     r14 */
   s.registers[0][14]=sub(&s,0,s.registers[0][14]);
   s.pc=0xf038c6u;break;
  case 0xf038c6u: /* jump    (r3) */
   if(condition(&s,0)){pending=1;target=s.registers[0][3];}
   s.pc=0xf038c8u;break;
  case 0xf038c8u: /* moveta  r2,r25 */
   s.registers[1][25]=s.registers[0][2];
   s.pc=0xf038cau;break;
  case 0xf038cau: /* movei   $f03ed8,r2 */
   s.registers[0][2]=0xf03ed8u;
   s.pc=0xf038d0u;break;
case 0xf038d0u: /* movefa  r27,r4 */
 s.registers[0][4]=s.registers[1][27];
 s.pc=0xf038d2u;break;
  case 0xf038d2u: /* load    (r2),r0 */
   CHECK(rd32(bus,&s,s.registers[0][2]&~3u,&v));s.registers[0][0]=v;
   s.pc=0xf038d4u;break;
case 0xf038d4u: /* movefa  r6,r1 */
 s.registers[0][1]=s.registers[1][6];
 s.pc=0xf038d6u;break;
  case 0xf038d6u: /* cmp     r4,r0 */
   (void)sub(&s,s.registers[0][0],s.registers[0][4]);
   s.pc=0xf038d8u;break;
  case 0xf038d8u: /* jump    z,(r1) */
   if(condition(&s,2)){pending=1;target=s.registers[0][1];}
   s.pc=0xf038dau;break;
  case 0xf038dau: /* addq    $4,r2 */
   s.registers[0][2]=add(&s,s.registers[0][2],4u);
   s.pc=0xf038dcu;break;
  case 0xf038dcu: /* move    r4,r5 */
   s.registers[0][5]=s.registers[0][4];
   s.pc=0xf038deu;break;
  case 0xf038deu: /* load    (r2),r0 */
   CHECK(rd32(bus,&s,s.registers[0][2]&~3u,&v));s.registers[0][0]=v;
   s.pc=0xf038e0u;break;
  case 0xf038e0u: /* addq    $8,r5 */
   s.registers[0][5]=add(&s,s.registers[0][5],8u);
   s.pc=0xf038e2u;break;
  case 0xf038e2u: /* cmp     r0,r5 */
   (void)sub(&s,s.registers[0][5],s.registers[0][0]);
   s.pc=0xf038e4u;break;
  case 0xf038e4u: /* jr      n,00F038EA */
   if(condition(&s,24)){pending=1;target=0xf038eau;}
   s.pc=0xf038e6u;break;
  case 0xf038e6u: /* addq    $4,r2 */
   s.registers[0][2]=add(&s,s.registers[0][2],4u);
   s.pc=0xf038e8u;break;
  case 0xf038e8u: /* moveq   0,r5 */
   s.registers[0][5]=0u;
   s.pc=0xf038eau;break;
case 0xf038eau: /* movefa  r7,r6 */
 s.registers[0][6]=s.registers[1][7];
 s.pc=0xf038ecu;break;
  case 0xf038ecu: /* load    (r2),r1 */
   CHECK(rd32(bus,&s,s.registers[0][2]&~3u,&v));s.registers[0][1]=v;
   s.pc=0xf038eeu;break;
case 0xf038eeu: /* movefa  r7,r7 */
 s.registers[0][7]=s.registers[1][7];
 s.pc=0xf038f0u;break;
  case 0xf038f0u: /* add     r4,r6 */
   s.registers[0][6]=add(&s,s.registers[0][6],s.registers[0][4]);
   s.pc=0xf038f2u;break;
  case 0xf038f2u: /* add     r5,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],s.registers[0][5]);
   s.pc=0xf038f4u;break;
  case 0xf038f4u: /* load    (r6),r15 */
   CHECK(rd32(bus,&s,s.registers[0][6]&~3u,&v));s.registers[0][15]=v;
   s.pc=0xf038f6u;break;
  case 0xf038f6u: /* load    (r7),r16 */
   CHECK(rd32(bus,&s,s.registers[0][7]&~3u,&v));s.registers[0][16]=v;
   s.pc=0xf038f8u;break;
  case 0xf038f8u: /* cmpq    $0,r1 */
   (void)sub(&s,s.registers[0][1],0x0u);
   s.pc=0xf038fau;break;
  case 0xf038fau: /* jr      nz,00F03902 */
   if(condition(&s,1)){pending=1;target=0xf03902u;}
   s.pc=0xf038fcu;break;
  case 0xf038fcu: /* moveta  r5,r27 */
   s.registers[1][27]=s.registers[0][5];
   s.pc=0xf038feu;break;
case 0xf038feu: /* rorq    $10,r15 */
 v=s.registers[0][15];s.c=v>>31;
 s.registers[0][15]=(v>>16)|(v<<16);
 zn(&s,s.registers[0][15]);
 s.pc=0xf03900u;break;
case 0xf03900u: /* rorq    $10,r16 */
 v=s.registers[0][16];s.c=v>>31;
 s.registers[0][16]=(v>>16)|(v<<16);
 zn(&s,s.registers[0][16]);
 s.pc=0xf03902u;break;
  case 0xf03902u: /* move    r15,r2 */
   s.registers[0][2]=s.registers[0][15];
   s.pc=0xf03904u;break;
  case 0xf03904u: /* move    r16,r8 */
   s.registers[0][8]=s.registers[0][16];
   s.pc=0xf03906u;break;
  case 0xf03906u: /* shlq    $10,r2 */
   s.c=s.registers[0][2]>>31;s.registers[0][2]=s.registers[0][2]<<16;zn(&s,s.registers[0][2]);
   s.pc=0xf03908u;break;
  case 0xf03908u: /* shlq    $10,r8 */
   s.c=s.registers[0][8]>>31;s.registers[0][8]=s.registers[0][8]<<16;zn(&s,s.registers[0][8]);
   s.pc=0xf0390au;break;
  case 0xf0390au: /* sharq   $10,r2 */
   s.c=s.registers[0][2]&1u;s.registers[0][2]=sar(s.registers[0][2],16);zn(&s,s.registers[0][2]);
   s.pc=0xf0390cu;break;
  case 0xf0390cu: /* sharq   $10,r8 */
   s.c=s.registers[0][8]&1u;s.registers[0][8]=sar(s.registers[0][8],16);zn(&s,s.registers[0][8]);
   s.pc=0xf0390eu;break;
  case 0xf0390eu: /* sharq   $10,r15 */
   s.c=s.registers[0][15]&1u;s.registers[0][15]=sar(s.registers[0][15],16);zn(&s,s.registers[0][15]);
   s.pc=0xf03910u;break;
  case 0xf03910u: /* sharq   $10,r16 */
   s.c=s.registers[0][16]&1u;s.registers[0][16]=sar(s.registers[0][16],16);zn(&s,s.registers[0][16]);
   s.pc=0xf03912u;break;
  case 0xf03912u: /* sub     r2,r8 */
   s.registers[0][8]=sub(&s,s.registers[0][8],s.registers[0][2]);
   s.pc=0xf03914u;break;
  case 0xf03914u: /* jr      nz,00F0391A */
   if(condition(&s,1)){pending=1;target=0xf0391au;}
   s.pc=0xf03916u;break;
  case 0xf03916u: /* moveta  r8,r26 */
   s.registers[1][26]=s.registers[0][8];
   s.pc=0xf03918u;break;
  case 0xf03918u: /* jump    (r3) */
   if(condition(&s,0)){pending=1;target=s.registers[0][3];}
   s.pc=0xf0391au;break;
  case 0xf0391au: /* shlq    $10,r15 */
   s.c=s.registers[0][15]>>31;s.registers[0][15]=s.registers[0][15]<<16;zn(&s,s.registers[0][15]);
   s.pc=0xf0391cu;break;
  case 0xf0391cu: /* shlq    $10,r16 */
   s.c=s.registers[0][16]>>31;s.registers[0][16]=s.registers[0][16]<<16;zn(&s,s.registers[0][16]);
   s.pc=0xf0391eu;break;
  case 0xf0391eu: /* addqt   $4,r6 */
   s.registers[0][6]+=4u;
   s.pc=0xf03920u;break;
  case 0xf03920u: /* sub     r15,r16 */
   s.registers[0][16]=sub(&s,s.registers[0][16],s.registers[0][15]);
   s.pc=0xf03922u;break;
  case 0xf03922u: /* addqt   $4,r7 */
   s.registers[0][7]+=4u;
   s.pc=0xf03924u;break;
  case 0xf03924u: /* abs     r16 */
   s.c=s.registers[0][16]>>31;if(s.registers[0][16]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[0][16]=0u-s.registers[0][16];s.n=0;s.z=s.registers[0][16]==0;}
   s.pc=0xf03926u;break;
  case 0xf03926u: /* div     r8,r16 */
   divide(&s,8,16);
   s.pc=0xf03928u;break;
  case 0xf03928u: /* load    (r6),r19 */
   CHECK(rd32(bus,&s,s.registers[0][6]&~3u,&v));s.registers[0][19]=v;
   s.pc=0xf0392au;break;
  case 0xf0392au: /* load    (r7),r20 */
   CHECK(rd32(bus,&s,s.registers[0][7]&~3u,&v));s.registers[0][20]=v;
   s.pc=0xf0392cu;break;
case 0xf0392cu: /* movefa  r17,r6 */
 s.registers[0][6]=s.registers[1][17];
 s.pc=0xf0392eu;break;
  case 0xf0392eu: /* movei   $f037cc,r3 */
   s.registers[0][3]=0xf037ccu;
   s.pc=0xf03934u;break;
case 0xf03934u: /* movefa  r17,r7 */
 s.registers[0][7]=s.registers[1][17];
 s.pc=0xf03936u;break;
case 0xf03936u: /* movefa  r0,r1 */
 s.registers[0][1]=s.registers[1][0];
 s.pc=0xf03938u;break;
  case 0xf03938u: /* jr      nc,00F0393E */
   if(condition(&s,4)){pending=1;target=0xf0393eu;}
   s.pc=0xf0393au;break;
case 0xf0393au: /* movefa  r16,r2 */
 s.registers[0][2]=s.registers[1][16];
 s.pc=0xf0393cu;break;
  case 0xf0393cu: /* neg     r16 */
   s.registers[0][16]=sub(&s,0,s.registers[0][16]);
   s.pc=0xf0393eu;break;
  case 0xf0393eu: /* sharq   $1,r4 */
   s.c=s.registers[0][4]&1u;s.registers[0][4]=sar(s.registers[0][4],1);zn(&s,s.registers[0][4]);
   s.pc=0xf03940u;break;
  case 0xf03940u: /* cmp     r1,r2 */
   (void)sub(&s,s.registers[0][2],s.registers[0][1]);
   s.pc=0xf03942u;break;
  case 0xf03942u: /* jump    z,(r3) */
   if(condition(&s,2)){pending=1;target=s.registers[0][3];}
   s.pc=0xf03944u;break;
  case 0xf03944u: /* sharq   $1,r5 */
   s.c=s.registers[0][5]&1u;s.registers[0][5]=sar(s.registers[0][5],1);zn(&s,s.registers[0][5]);
   s.pc=0xf03946u;break;
  case 0xf03946u: /* shrq    $10,r19 */
   s.c=s.registers[0][19]&1u;s.registers[0][19]=s.registers[0][19]>>16;zn(&s,s.registers[0][19]);
   s.pc=0xf03948u;break;
  case 0xf03948u: /* shrq    $10,r20 */
   s.c=s.registers[0][20]&1u;s.registers[0][20]=s.registers[0][20]>>16;zn(&s,s.registers[0][20]);
   s.pc=0xf0394au;break;
  case 0xf0394au: /* add     r4,r6 */
   s.registers[0][6]=add(&s,s.registers[0][6],s.registers[0][4]);
   s.pc=0xf0394cu;break;
  case 0xf0394cu: /* add     r5,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],s.registers[0][5]);
   s.pc=0xf0394eu;break;
  case 0xf0394eu: /* load    (r6),r17 */
   CHECK(rd32(bus,&s,s.registers[0][6]&~3u,&v));s.registers[0][17]=v;
   s.pc=0xf03950u;break;
  case 0xf03950u: /* load    (r7),r1 */
   CHECK(rd32(bus,&s,s.registers[0][7]&~3u,&v));s.registers[0][1]=v;
   s.pc=0xf03952u;break;
  case 0xf03952u: /* move    r17,r18 */
   s.registers[0][18]=s.registers[0][17];
   s.pc=0xf03954u;break;
  case 0xf03954u: /* move    r1,r2 */
   s.registers[0][2]=s.registers[0][1];
   s.pc=0xf03956u;break;
  case 0xf03956u: /* shrq    $10,r17 */
   s.c=s.registers[0][17]&1u;s.registers[0][17]=s.registers[0][17]>>16;zn(&s,s.registers[0][17]);
   s.pc=0xf03958u;break;
  case 0xf03958u: /* shrq    $10,r1 */
   s.c=s.registers[0][1]&1u;s.registers[0][1]=s.registers[0][1]>>16;zn(&s,s.registers[0][1]);
   s.pc=0xf0395au;break;
  case 0xf0395au: /* mult    r19,r17 */
   s.registers[0][17]=(s.registers[0][17]&0xffffu)*(s.registers[0][19]&0xffffu);
   zn(&s,s.registers[0][17]);
   s.pc=0xf0395cu;break;
  case 0xf0395cu: /* mult    r20,r1 */
   s.registers[0][1]=(s.registers[0][1]&0xffffu)*(s.registers[0][20]&0xffffu);
   zn(&s,s.registers[0][1]);
   s.pc=0xf0395eu;break;
  case 0xf0395eu: /* mult    r19,r18 */
   s.registers[0][18]=(s.registers[0][18]&0xffffu)*(s.registers[0][19]&0xffffu);
   zn(&s,s.registers[0][18]);
   s.pc=0xf03960u;break;
  case 0xf03960u: /* mult    r20,r2 */
   s.registers[0][2]=(s.registers[0][2]&0xffffu)*(s.registers[0][20]&0xffffu);
   zn(&s,s.registers[0][2]);
   s.pc=0xf03962u;break;
  case 0xf03962u: /* shlq    $10,r19 */
   s.c=s.registers[0][19]>>31;s.registers[0][19]=s.registers[0][19]<<16;zn(&s,s.registers[0][19]);
   s.pc=0xf03964u;break;
  case 0xf03964u: /* sub     r17,r1 */
   s.registers[0][1]=sub(&s,s.registers[0][1],s.registers[0][17]);
   s.pc=0xf03966u;break;
  case 0xf03966u: /* shlq    $10,r20 */
   s.c=s.registers[0][20]>>31;s.registers[0][20]=s.registers[0][20]<<16;zn(&s,s.registers[0][20]);
   s.pc=0xf03968u;break;
  case 0xf03968u: /* abs     r1 */
   s.c=s.registers[0][1]>>31;if(s.registers[0][1]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[0][1]=0u-s.registers[0][1];s.n=0;s.z=s.registers[0][1]==0;}
   s.pc=0xf0396au;break;
  case 0xf0396au: /* div     r8,r1 */
   divide(&s,8,1);
   s.pc=0xf0396cu;break;
  case 0xf0396cu: /* jr      nc,00F03972 */
   if(condition(&s,4)){pending=1;target=0xf03972u;}
   s.pc=0xf0396eu;break;
  case 0xf0396eu: /* sub     r18,r2 */
   s.registers[0][2]=sub(&s,s.registers[0][2],s.registers[0][18]);
   s.pc=0xf03970u;break;
  case 0xf03970u: /* neg     r1 */
   s.registers[0][1]=sub(&s,0,s.registers[0][1]);
   s.pc=0xf03972u;break;
  case 0xf03972u: /* abs     r2 */
   s.c=s.registers[0][2]>>31;if(s.registers[0][2]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[0][2]=0u-s.registers[0][2];s.n=0;s.z=s.registers[0][2]==0;}
   s.pc=0xf03974u;break;
  case 0xf03974u: /* div     r8,r2 */
   divide(&s,8,2);
   s.pc=0xf03976u;break;
  case 0xf03976u: /* jr      nc,00F0397C */
   if(condition(&s,4)){pending=1;target=0xf0397cu;}
   s.pc=0xf03978u;break;
  case 0xf03978u: /* sub     r19,r20 */
   s.registers[0][20]=sub(&s,s.registers[0][20],s.registers[0][19]);
   s.pc=0xf0397au;break;
  case 0xf0397au: /* neg     r2 */
   s.registers[0][2]=sub(&s,0,s.registers[0][2]);
   s.pc=0xf0397cu;break;
  case 0xf0397cu: /* abs     r20 */
   s.c=s.registers[0][20]>>31;if(s.registers[0][20]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[0][20]=0u-s.registers[0][20];s.n=0;s.z=s.registers[0][20]==0;}
   s.pc=0xf0397eu;break;
  case 0xf0397eu: /* div     r8,r20 */
   divide(&s,8,20);
   s.pc=0xf03980u;break;
  case 0xf03980u: /* jr      nc,00F03986 */
   if(condition(&s,4)){pending=1;target=0xf03986u;}
   s.pc=0xf03982u;break;
  case 0xf03982u: /* moveta  r1,r30 */
   s.registers[1][30]=s.registers[0][1];
   s.pc=0xf03984u;break;
  case 0xf03984u: /* neg     r20 */
   s.registers[0][20]=sub(&s,0,s.registers[0][20]);
   s.pc=0xf03986u;break;
  case 0xf03986u: /* jump    (r3) */
   if(condition(&s,0)){pending=1;target=s.registers[0][3];}
   s.pc=0xf03988u;break;
  case 0xf03988u: /* moveta  r2,r31 */
   s.registers[1][31]=s.registers[0][2];
   s.pc=0xf0398au;break;
  case 0xf0398au: /* move    r9,r6 */
   s.registers[0][6]=s.registers[0][9];
   s.pc=0xf0398cu;break;
  case 0xf0398cu: /* move    r15,r7 */
   s.registers[0][7]=s.registers[0][15];
   s.pc=0xf0398eu;break;
  case 0xf0398eu: /* moveq   0,r4 */
   s.registers[0][4]=0u;
   s.pc=0xf03990u;break;
  case 0xf03990u: /* add     r0,r6 */
   s.registers[0][6]=add(&s,s.registers[0][6],s.registers[0][0]);
   s.pc=0xf03992u;break;
case 0xf03992u: /* movefa  r3,r5 */
 s.registers[0][5]=s.registers[1][3];
 s.pc=0xf03994u;break;
  case 0xf03994u: /* sharq   $10,r6 */
   s.c=s.registers[0][6]&1u;s.registers[0][6]=sar(s.registers[0][6],16);zn(&s,s.registers[0][6]);
   s.pc=0xf03996u;break;
  case 0xf03996u: /* add     r0,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],s.registers[0][0]);
   s.pc=0xf03998u;break;
  case 0xf03998u: /* addq    $1,r6 */
   s.registers[0][6]=add(&s,s.registers[0][6],1u);
   s.pc=0xf0399au;break;
  case 0xf0399au: /* sharq   $10,r7 */
   s.c=s.registers[0][7]&1u;s.registers[0][7]=sar(s.registers[0][7],16);zn(&s,s.registers[0][7]);
   s.pc=0xf0399cu;break;
  case 0xf0399cu: /* cmp     r4,r6 */
   (void)sub(&s,s.registers[0][6],s.registers[0][4]);
   s.pc=0xf0399eu;break;
  case 0xf0399eu: /* jump    n,(r22) */
   if(condition(&s,24)){pending=1;target=s.registers[0][22];}
   s.pc=0xf039a0u;break;
  case 0xf039a0u: /* cmp     r7,r5 */
   (void)sub(&s,s.registers[0][5],s.registers[0][7]);
   s.pc=0xf039a2u;break;
  case 0xf039a2u: /* jump    n,(r22) */
   if(condition(&s,24)){pending=1;target=s.registers[0][22];}
   s.pc=0xf039a4u;break;
  case 0xf039a4u: /* move    r6,r8 */
   s.registers[0][8]=s.registers[0][6];
   s.pc=0xf039a6u;break;
  case 0xf039a6u: /* sub     r7,r8 */
   s.registers[0][8]=sub(&s,s.registers[0][8],s.registers[0][7]);
   s.pc=0xf039a8u;break;
  case 0xf039a8u: /* jump    n,(r22) */
   if(condition(&s,24)){pending=1;target=s.registers[0][22];}
   s.pc=0xf039aau;break;
  case 0xf039aau: /* move    r13,r1 */
   s.registers[0][1]=s.registers[0][13];
   s.pc=0xf039acu;break;
  case 0xf039acu: /* move    r19,r2 */
   s.registers[0][2]=s.registers[0][19];
   s.pc=0xf039aeu;break;
  case 0xf039aeu: /* sharq   $11,r1 */
   s.c=s.registers[0][1]&1u;s.registers[0][1]=sar(s.registers[0][1],17);zn(&s,s.registers[0][1]);
   s.pc=0xf039b0u;break;
  case 0xf039b0u: /* sharq   $11,r2 */
   s.c=s.registers[0][2]&1u;s.registers[0][2]=sar(s.registers[0][2],17);zn(&s,s.registers[0][2]);
   s.pc=0xf039b2u;break;
  case 0xf039b2u: /* add     r1,r11 */
   s.registers[0][11]=add(&s,s.registers[0][11],s.registers[0][1]);
   s.pc=0xf039b4u;break;
  case 0xf039b4u: /* add     r2,r17 */
   s.registers[0][17]=add(&s,s.registers[0][17],s.registers[0][2]);
   s.pc=0xf039b6u;break;
  case 0xf039b6u: /* add     r1,r12 */
   s.registers[0][12]=add(&s,s.registers[0][12],s.registers[0][1]);
   s.pc=0xf039b8u;break;
  case 0xf039b8u: /* add     r2,r18 */
   s.registers[0][18]=add(&s,s.registers[0][18],s.registers[0][2]);
   s.pc=0xf039bau;break;
  case 0xf039bau: /* move    r13,r1 */
   s.registers[0][1]=s.registers[0][13];
   s.pc=0xf039bcu;break;
  case 0xf039bcu: /* move    r19,r2 */
   s.registers[0][2]=s.registers[0][19];
   s.pc=0xf039beu;break;
  case 0xf039beu: /* sharq   $10,r1 */
   s.c=s.registers[0][1]&1u;s.registers[0][1]=sar(s.registers[0][1],16);zn(&s,s.registers[0][1]);
   s.pc=0xf039c0u;break;
  case 0xf039c0u: /* sharq   $10,r2 */
   s.c=s.registers[0][2]&1u;s.registers[0][2]=sar(s.registers[0][2],16);zn(&s,s.registers[0][2]);
   s.pc=0xf039c2u;break;
  case 0xf039c2u: /* abs     r11 */
   s.c=s.registers[0][11]>>31;if(s.registers[0][11]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[0][11]=0u-s.registers[0][11];s.n=0;s.z=s.registers[0][11]==0;}
   s.pc=0xf039c4u;break;
  case 0xf039c4u: /* jr      nc,00F039CA */
   if(condition(&s,4)){pending=1;target=0xf039cau;}
   s.pc=0xf039c6u;break;
  case 0xf039c6u: /* div     r1,r11 */
   divide(&s,1,11);
   s.pc=0xf039c8u;break;
  case 0xf039c8u: /* neg     r11 */
   s.registers[0][11]=sub(&s,0,s.registers[0][11]);
   s.pc=0xf039cau;break;
  case 0xf039cau: /* abs     r17 */
   s.c=s.registers[0][17]>>31;if(s.registers[0][17]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[0][17]=0u-s.registers[0][17];s.n=0;s.z=s.registers[0][17]==0;}
   s.pc=0xf039ccu;break;
  case 0xf039ccu: /* jr      nc,00F039D2 */
   if(condition(&s,4)){pending=1;target=0xf039d2u;}
   s.pc=0xf039ceu;break;
  case 0xf039ceu: /* div     r2,r17 */
   divide(&s,2,17);
   s.pc=0xf039d0u;break;
  case 0xf039d0u: /* neg     r17 */
   s.registers[0][17]=sub(&s,0,s.registers[0][17]);
   s.pc=0xf039d2u;break;
  case 0xf039d2u: /* shlq    $10,r11 */
   s.c=s.registers[0][11]>>31;s.registers[0][11]=s.registers[0][11]<<16;zn(&s,s.registers[0][11]);
   s.pc=0xf039d4u;break;
  case 0xf039d4u: /* shlq    $10,r17 */
   s.c=s.registers[0][17]>>31;s.registers[0][17]=s.registers[0][17]<<16;zn(&s,s.registers[0][17]);
   s.pc=0xf039d6u;break;
  case 0xf039d6u: /* abs     r12 */
   s.c=s.registers[0][12]>>31;if(s.registers[0][12]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[0][12]=0u-s.registers[0][12];s.n=0;s.z=s.registers[0][12]==0;}
   s.pc=0xf039d8u;break;
  case 0xf039d8u: /* jr      nc,00F039DE */
   if(condition(&s,4)){pending=1;target=0xf039deu;}
   s.pc=0xf039dau;break;
  case 0xf039dau: /* div     r1,r12 */
   divide(&s,1,12);
   s.pc=0xf039dcu;break;
  case 0xf039dcu: /* neg     r12 */
   s.registers[0][12]=sub(&s,0,s.registers[0][12]);
   s.pc=0xf039deu;break;
  case 0xf039deu: /* abs     r18 */
   s.c=s.registers[0][18]>>31;if(s.registers[0][18]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[0][18]=0u-s.registers[0][18];s.n=0;s.z=s.registers[0][18]==0;}
   s.pc=0xf039e0u;break;
  case 0xf039e0u: /* jr      nc,00F039E6 */
   if(condition(&s,4)){pending=1;target=0xf039e6u;}
   s.pc=0xf039e2u;break;
  case 0xf039e2u: /* div     r2,r18 */
   divide(&s,2,18);
   s.pc=0xf039e4u;break;
  case 0xf039e4u: /* neg     r18 */
   s.registers[0][18]=sub(&s,0,s.registers[0][18]);
   s.pc=0xf039e6u;break;
  case 0xf039e6u: /* shlq    $10,r12 */
   s.c=s.registers[0][12]>>31;s.registers[0][12]=s.registers[0][12]<<16;zn(&s,s.registers[0][12]);
   s.pc=0xf039e8u;break;
  case 0xf039e8u: /* shlq    $10,r18 */
   s.c=s.registers[0][18]>>31;s.registers[0][18]=s.registers[0][18]<<16;zn(&s,s.registers[0][18]);
   s.pc=0xf039eau;break;
  case 0xf039eau: /* sub     r17,r11 */
   s.registers[0][11]=sub(&s,s.registers[0][11],s.registers[0][17]);
   s.pc=0xf039ecu;break;
  case 0xf039ecu: /* abs     r11 */
   s.c=s.registers[0][11]>>31;if(s.registers[0][11]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[0][11]=0u-s.registers[0][11];s.n=0;s.z=s.registers[0][11]==0;}
   s.pc=0xf039eeu;break;
  case 0xf039eeu: /* jr      nc,00F039F4 */
   if(condition(&s,4)){pending=1;target=0xf039f4u;}
   s.pc=0xf039f0u;break;
  case 0xf039f0u: /* div     r8,r11 */
   divide(&s,8,11);
   s.pc=0xf039f2u;break;
  case 0xf039f2u: /* neg     r11 */
   s.registers[0][11]=sub(&s,0,s.registers[0][11]);
   s.pc=0xf039f4u;break;
  case 0xf039f4u: /* sub     r18,r12 */
   s.registers[0][12]=sub(&s,s.registers[0][12],s.registers[0][18]);
   s.pc=0xf039f6u;break;
  case 0xf039f6u: /* abs     r12 */
   s.c=s.registers[0][12]>>31;if(s.registers[0][12]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[0][12]=0u-s.registers[0][12];s.n=0;s.z=s.registers[0][12]==0;}
   s.pc=0xf039f8u;break;
  case 0xf039f8u: /* jr      nc,00F039FE */
   if(condition(&s,4)){pending=1;target=0xf039feu;}
   s.pc=0xf039fau;break;
  case 0xf039fau: /* div     r8,r12 */
   divide(&s,8,12);
   s.pc=0xf039fcu;break;
  case 0xf039fcu: /* neg     r12 */
   s.registers[0][12]=sub(&s,0,s.registers[0][12]);
   s.pc=0xf039feu;break;
  case 0xf039feu: /* cmp     r5,r6 */
   (void)sub(&s,s.registers[0][6],s.registers[0][5]);
   s.pc=0xf03a00u;break;
  case 0xf03a00u: /* jr      n,00F03A06 */
   if(condition(&s,24)){pending=1;target=0xf03a06u;}
   s.pc=0xf03a02u;break;
  case 0xf03a02u: /* move    r4,r2 */
   s.registers[0][2]=s.registers[0][4];
   s.pc=0xf03a04u;break;
  case 0xf03a04u: /* move    r5,r6 */
   s.registers[0][6]=s.registers[0][5];
   s.pc=0xf03a06u;break;
  case 0xf03a06u: /* movei   $f03a34,r0 */
   s.registers[0][0]=0xf03a34u;
   s.pc=0xf03a0cu;break;
  case 0xf03a0cu: /* cmp     r7,r4 */
   (void)sub(&s,s.registers[0][4],s.registers[0][7]);
   s.pc=0xf03a0eu;break;
  case 0xf03a0eu: /* jump    n,(r0) */
   if(condition(&s,24)){pending=1;target=s.registers[0][0];}
   s.pc=0xf03a10u;break;
  case 0xf03a10u: /* sub     r7,r2 */
   s.registers[0][2]=sub(&s,s.registers[0][2],s.registers[0][7]);
   s.pc=0xf03a12u;break;
  case 0xf03a12u: /* move    r11,r0 */
   s.registers[0][0]=s.registers[0][11];
   s.pc=0xf03a14u;break;
  case 0xf03a14u: /* move    r12,r1 */
   s.registers[0][1]=s.registers[0][12];
   s.pc=0xf03a16u;break;
  case 0xf03a16u: /* mult    r2,r0 */
   s.registers[0][0]=(s.registers[0][0]&0xffffu)*(s.registers[0][2]&0xffffu);
   zn(&s,s.registers[0][0]);
   s.pc=0xf03a18u;break;
  case 0xf03a18u: /* mult    r2,r1 */
   s.registers[0][1]=(s.registers[0][1]&0xffffu)*(s.registers[0][2]&0xffffu);
   zn(&s,s.registers[0][1]);
   s.pc=0xf03a1au;break;
  case 0xf03a1au: /* add     r0,r17 */
   s.registers[0][17]=add(&s,s.registers[0][17],s.registers[0][0]);
   s.pc=0xf03a1cu;break;
  case 0xf03a1cu: /* add     r1,r18 */
   s.registers[0][18]=add(&s,s.registers[0][18],s.registers[0][1]);
   s.pc=0xf03a1eu;break;
  case 0xf03a1eu: /* move    r4,r7 */
   s.registers[0][7]=s.registers[0][4];
   s.pc=0xf03a20u;break;
  case 0xf03a20u: /* move    r11,r0 */
   s.registers[0][0]=s.registers[0][11];
   s.pc=0xf03a22u;break;
  case 0xf03a22u: /* move    r12,r1 */
   s.registers[0][1]=s.registers[0][12];
   s.pc=0xf03a24u;break;
  case 0xf03a24u: /* shrq    $10,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=s.registers[0][0]>>16;zn(&s,s.registers[0][0]);
   s.pc=0xf03a26u;break;
  case 0xf03a26u: /* shrq    $10,r1 */
   s.c=s.registers[0][1]&1u;s.registers[0][1]=s.registers[0][1]>>16;zn(&s,s.registers[0][1]);
   s.pc=0xf03a28u;break;
  case 0xf03a28u: /* imult   r2,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][2]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf03a2au;break;
  case 0xf03a2au: /* imult   r2,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][2]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf03a2cu;break;
  case 0xf03a2cu: /* shlq    $10,r0 */
   s.c=s.registers[0][0]>>31;s.registers[0][0]=s.registers[0][0]<<16;zn(&s,s.registers[0][0]);
   s.pc=0xf03a2eu;break;
  case 0xf03a2eu: /* shlq    $10,r1 */
   s.c=s.registers[0][1]>>31;s.registers[0][1]=s.registers[0][1]<<16;zn(&s,s.registers[0][1]);
   s.pc=0xf03a30u;break;
  case 0xf03a30u: /* add     r0,r17 */
   s.registers[0][17]=add(&s,s.registers[0][17],s.registers[0][0]);
   s.pc=0xf03a32u;break;
  case 0xf03a32u: /* add     r1,r18 */
   s.registers[0][18]=add(&s,s.registers[0][18],s.registers[0][1]);
   s.pc=0xf03a34u;break;
  case 0xf03a34u: /* sub     r7,r6 */
   s.registers[0][6]=sub(&s,s.registers[0][6],s.registers[0][7]);
   s.pc=0xf03a36u;break;
  case 0xf03a36u: /* jump    z,(r22) */
   if(condition(&s,2)){pending=1;target=s.registers[0][22];}
   s.pc=0xf03a38u;break;
  case 0xf03a38u: /* move    r18,r0 */
   s.registers[0][0]=s.registers[0][18];
   s.pc=0xf03a3au;break;
  case 0xf03a3au: /* move    r17,r4 */
   s.registers[0][4]=s.registers[0][17];
   s.pc=0xf03a3cu;break;
  case 0xf03a3cu: /* shrq    $10,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=s.registers[0][0]>>16;zn(&s,s.registers[0][0]);
   s.pc=0xf03a3eu;break;
  case 0xf03a3eu: /* shrq    $10,r4 */
   s.c=s.registers[0][4]&1u;s.registers[0][4]=s.registers[0][4]>>16;zn(&s,s.registers[0][4]);
   s.pc=0xf03a40u;break;
  case 0xf03a40u: /* shlq    $10,r0 */
   s.c=s.registers[0][0]>>31;s.registers[0][0]=s.registers[0][0]<<16;zn(&s,s.registers[0][0]);
   s.pc=0xf03a42u;break;
  case 0xf03a42u: /* shlq    $10,r17 */
   s.c=s.registers[0][17]>>31;s.registers[0][17]=s.registers[0][17]<<16;zn(&s,s.registers[0][17]);
   s.pc=0xf03a44u;break;
  case 0xf03a44u: /* or      r0,r4 */
   s.registers[0][4]|=s.registers[0][0];
   zn(&s,s.registers[0][4]);
   s.pc=0xf03a46u;break;
  case 0xf03a46u: /* shlq    $10,r18 */
   s.c=s.registers[0][18]>>31;s.registers[0][18]=s.registers[0][18]<<16;zn(&s,s.registers[0][18]);
   s.pc=0xf03a48u;break;
  case 0xf03a48u: /* shrq    $10,r17 */
   s.c=s.registers[0][17]&1u;s.registers[0][17]=s.registers[0][17]>>16;zn(&s,s.registers[0][17]);
   s.pc=0xf03a4au;break;
  case 0xf03a4au: /* move    r12,r0 */
   s.registers[0][0]=s.registers[0][12];
   s.pc=0xf03a4cu;break;
  case 0xf03a4cu: /* or      r18,r17 */
   s.registers[0][17]|=s.registers[0][18];
   zn(&s,s.registers[0][17]);
   s.pc=0xf03a4eu;break;
  case 0xf03a4eu: /* move    r11,r5 */
   s.registers[0][5]=s.registers[0][11];
   s.pc=0xf03a50u;break;
  case 0xf03a50u: /* shrq    $10,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=s.registers[0][0]>>16;zn(&s,s.registers[0][0]);
   s.pc=0xf03a52u;break;
  case 0xf03a52u: /* shrq    $10,r5 */
   s.c=s.registers[0][5]&1u;s.registers[0][5]=s.registers[0][5]>>16;zn(&s,s.registers[0][5]);
   s.pc=0xf03a54u;break;
  case 0xf03a54u: /* shlq    $10,r0 */
   s.c=s.registers[0][0]>>31;s.registers[0][0]=s.registers[0][0]<<16;zn(&s,s.registers[0][0]);
   s.pc=0xf03a56u;break;
  case 0xf03a56u: /* shlq    $10,r11 */
   s.c=s.registers[0][11]>>31;s.registers[0][11]=s.registers[0][11]<<16;zn(&s,s.registers[0][11]);
   s.pc=0xf03a58u;break;
  case 0xf03a58u: /* or      r0,r5 */
   s.registers[0][5]|=s.registers[0][0];
   zn(&s,s.registers[0][5]);
   s.pc=0xf03a5au;break;
  case 0xf03a5au: /* shlq    $10,r12 */
   s.c=s.registers[0][12]>>31;s.registers[0][12]=s.registers[0][12]<<16;zn(&s,s.registers[0][12]);
   s.pc=0xf03a5cu;break;
  case 0xf03a5cu: /* shrq    $10,r11 */
   s.c=s.registers[0][11]&1u;s.registers[0][11]=s.registers[0][11]>>16;zn(&s,s.registers[0][11]);
   s.pc=0xf03a5eu;break;
  case 0xf03a5eu: /* move    r21,r8 */
   s.registers[0][8]=s.registers[0][21];
   s.pc=0xf03a60u;break;
  case 0xf03a60u: /* or      r12,r11 */
   s.registers[0][11]|=s.registers[0][12];
   zn(&s,s.registers[0][11]);
   s.pc=0xf03a62u;break;
  case 0xf03a62u: /* shlq    $10,r7 */
   s.c=s.registers[0][7]>>31;s.registers[0][7]=s.registers[0][7]<<16;zn(&s,s.registers[0][7]);
   s.pc=0xf03a64u;break;
case 0xf03a64u: /* movefa  r0,r2 */
 s.registers[0][2]=s.registers[1][0];
 s.pc=0xf03a66u;break;
  case 0xf03a66u: /* or      r7,r8 */
   s.registers[0][8]|=s.registers[0][7];
   zn(&s,s.registers[0][8]);
   s.pc=0xf03a68u;break;
  case 0xf03a68u: /* shlq    $10,r6 */
   s.c=s.registers[0][6]>>31;s.registers[0][6]=s.registers[0][6]<<16;zn(&s,s.registers[0][6]);
   s.pc=0xf03a6au;break;
  case 0xf03a6au: /* bset    $10,r2 */
   s.registers[0][2]|=(1u<<16);
   zn(&s,s.registers[0][2]);
   s.pc=0xf03a6cu;break;
case 0xf03a6cu: /* movefa  r8,r1 */
 s.registers[0][1]=s.registers[1][8];
 s.pc=0xf03a6eu;break;
case 0xf03a6eu: /* movefa  r9,r7 */
 s.registers[0][7]=s.registers[1][9];
 s.pc=0xf03a70u;break;
case 0xf03a70u: /* movefa  r10,r3 */
 s.registers[0][3]=s.registers[1][10];
 s.pc=0xf03a72u;break;
  case 0xf03a72u: /* load    (r3),r0 */
   CHECK(rd32(bus,&s,s.registers[0][3]&~3u,&v));s.registers[0][0]=v;
   s.pc=0xf03a74u;break;
  case 0xf03a74u: /* btst    $0,r0 */
   s.z=((~s.registers[0][0])>>0)&1u;
   s.pc=0xf03a76u;break;
  case 0xf03a76u: /* jr      z,00F03A72 */
   if(condition(&s,2)){pending=1;target=0xf03a72u;}
   s.pc=0xf03a78u;break;
  case 0xf03a78u: /* bset    $0,r6 */
   s.registers[0][6]|=(1u<<0);
   zn(&s,s.registers[0][6]);
   s.pc=0xf03a7au;break;
  case 0xf03a7au: /* store   r26,(r7) */
   CHECK(wr32(bus,&s,local(s.registers[0][7])?(s.registers[0][7]&~3u):s.registers[0][7],s.registers[0][26]));
   s.pc=0xf03a7cu;break;
  case 0xf03a7cu: /* store   r24,(r1) */
   CHECK(wr32(bus,&s,local(s.registers[0][1])?(s.registers[0][1]&~3u):s.registers[0][1],s.registers[0][24]));
   s.pc=0xf03a7eu;break;
  case 0xf03a7eu: /* addq    $8,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],8u);
   s.pc=0xf03a80u;break;
  case 0xf03a80u: /* addq    $4,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],4u);
   s.pc=0xf03a82u;break;
  case 0xf03a82u: /* store   r8,(r7) */
   CHECK(wr32(bus,&s,local(s.registers[0][7])?(s.registers[0][7]&~3u):s.registers[0][7],s.registers[0][8]));
   s.pc=0xf03a84u;break;
  case 0xf03a84u: /* store   r25,(r1) */
   CHECK(wr32(bus,&s,local(s.registers[0][1])?(s.registers[0][1]&~3u):s.registers[0][1],s.registers[0][25]));
   s.pc=0xf03a86u;break;
  case 0xf03a86u: /* addq    $4,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],4u);
   s.pc=0xf03a88u;break;
  case 0xf03a88u: /* addq    $8,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],8u);
   s.pc=0xf03a8au;break;
  case 0xf03a8au: /* store   r2,(r7) */
   CHECK(wr32(bus,&s,local(s.registers[0][7])?(s.registers[0][7]&~3u):s.registers[0][7],s.registers[0][2]));
   s.pc=0xf03a8cu;break;
  case 0xf03a8cu: /* store   r4,(r1) */
   CHECK(wr32(bus,&s,local(s.registers[0][1])?(s.registers[0][1]&~3u):s.registers[0][1],s.registers[0][4]));
   s.pc=0xf03a8eu;break;
  case 0xf03a8eu: /* subq    $c,r7 */
   s.registers[0][7]=sub(&s,s.registers[0][7],12u);
   s.pc=0xf03a90u;break;
  case 0xf03a90u: /* addq    $c,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],12u);
   s.pc=0xf03a92u;break;
  case 0xf03a92u: /* addq    $4,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],4u);
   s.pc=0xf03a94u;break;
  case 0xf03a94u: /* store   r17,(r1) */
   CHECK(wr32(bus,&s,local(s.registers[0][1])?(s.registers[0][1]&~3u):s.registers[0][1],s.registers[0][17]));
   s.pc=0xf03a96u;break;
  case 0xf03a96u: /* store   r6,(r3) */
   CHECK(wr32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],s.registers[0][6]));
   s.pc=0xf03a98u;break;
  case 0xf03a98u: /* addq    $4,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],4u);
   s.pc=0xf03a9au;break;
  case 0xf03a9au: /* addq    $20,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],32u);
   s.pc=0xf03a9cu;break;
  case 0xf03a9cu: /* store   r5,(r1) */
   CHECK(wr32(bus,&s,local(s.registers[0][1])?(s.registers[0][1]&~3u):s.registers[0][1],s.registers[0][5]));
   s.pc=0xf03a9eu;break;
  case 0xf03a9eu: /* addq    $14,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],20u);
   s.pc=0xf03aa0u;break;
  case 0xf03aa0u: /* addq    $4,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],4u);
   s.pc=0xf03aa2u;break;
  case 0xf03aa2u: /* store   r27,(r3) */
   CHECK(wr32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],s.registers[0][27]));
   s.pc=0xf03aa4u;break;
  case 0xf03aa4u: /* store   r11,(r1) */
   CHECK(wr32(bus,&s,local(s.registers[0][1])?(s.registers[0][1]&~3u):s.registers[0][1],s.registers[0][11]));
   s.pc=0xf03aa6u;break;
  case 0xf03aa6u: /* subq    $18,r3 */
   s.registers[0][3]=sub(&s,s.registers[0][3],24u);
   s.pc=0xf03aa8u;break;
  case 0xf03aa8u: /* subq    $20,r1 */
   s.registers[0][1]=sub(&s,s.registers[0][1],32u);
   s.pc=0xf03aaau;break;
  case 0xf03aaau: /* subq    $20,r3 */
   s.registers[0][3]=sub(&s,s.registers[0][3],32u);
   s.pc=0xf03aacu;break;
case 0xf03aacu: /* movefa  r12,r0 */
 s.registers[0][0]=s.registers[1][12];
 s.pc=0xf03aaeu;break;
  case 0xf03aaeu: /* jump    (r22) */
   if(condition(&s,0)){pending=1;target=s.registers[0][22];}
   s.pc=0xf03ab0u;break;
  case 0xf03ab0u: /* store   r0,(r3) */
   CHECK(wr32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],s.registers[0][0]));
   s.pc=0xf03ab2u;break;
  case 0xf03ab2u: /* move    r9,r6 */
   s.registers[0][6]=s.registers[0][9];
   s.pc=0xf03ab4u;break;
  case 0xf03ab4u: /* move    r15,r7 */
   s.registers[0][7]=s.registers[0][15];
   s.pc=0xf03ab6u;break;
case 0xf03ab6u: /* movefa  r1,r0 */
 s.registers[0][0]=s.registers[1][1];
 s.pc=0xf03ab8u;break;
  case 0xf03ab8u: /* moveq   0,r4 */
   s.registers[0][4]=0u;
   s.pc=0xf03abau;break;
  case 0xf03abau: /* add     r0,r6 */
   s.registers[0][6]=add(&s,s.registers[0][6],s.registers[0][0]);
   s.pc=0xf03abcu;break;
case 0xf03abcu: /* movefa  r3,r5 */
 s.registers[0][5]=s.registers[1][3];
 s.pc=0xf03abeu;break;
  case 0xf03abeu: /* sharq   $10,r6 */
   s.c=s.registers[0][6]&1u;s.registers[0][6]=sar(s.registers[0][6],16);zn(&s,s.registers[0][6]);
   s.pc=0xf03ac0u;break;
  case 0xf03ac0u: /* add     r0,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],s.registers[0][0]);
   s.pc=0xf03ac2u;break;
  case 0xf03ac2u: /* addq    $1,r6 */
   s.registers[0][6]=add(&s,s.registers[0][6],1u);
   s.pc=0xf03ac4u;break;
  case 0xf03ac4u: /* sharq   $10,r7 */
   s.c=s.registers[0][7]&1u;s.registers[0][7]=sar(s.registers[0][7],16);zn(&s,s.registers[0][7]);
   s.pc=0xf03ac6u;break;
  case 0xf03ac6u: /* cmp     r4,r6 */
   (void)sub(&s,s.registers[0][6],s.registers[0][4]);
   s.pc=0xf03ac8u;break;
  case 0xf03ac8u: /* jump    n,(r22) */
   if(condition(&s,24)){pending=1;target=s.registers[0][22];}
   s.pc=0xf03acau;break;
  case 0xf03acau: /* cmp     r7,r5 */
   (void)sub(&s,s.registers[0][5],s.registers[0][7]);
   s.pc=0xf03accu;break;
  case 0xf03accu: /* jump    n,(r22) */
   if(condition(&s,24)){pending=1;target=s.registers[0][22];}
   s.pc=0xf03aceu;break;
  case 0xf03aceu: /* move    r6,r8 */
   s.registers[0][8]=s.registers[0][6];
   s.pc=0xf03ad0u;break;
  case 0xf03ad0u: /* sub     r7,r8 */
   s.registers[0][8]=sub(&s,s.registers[0][8],s.registers[0][7]);
   s.pc=0xf03ad2u;break;
  case 0xf03ad2u: /* jump    n,(r22) */
   if(condition(&s,24)){pending=1;target=s.registers[0][22];}
   s.pc=0xf03ad4u;break;
  case 0xf03ad4u: /* cmp     r5,r6 */
   (void)sub(&s,s.registers[0][6],s.registers[0][5]);
   s.pc=0xf03ad6u;break;
  case 0xf03ad6u: /* jr      n,00F03ADC */
   if(condition(&s,24)){pending=1;target=0xf03adcu;}
   s.pc=0xf03ad8u;break;
  case 0xf03ad8u: /* cmp     r7,r4 */
   (void)sub(&s,s.registers[0][4],s.registers[0][7]);
   s.pc=0xf03adau;break;
  case 0xf03adau: /* move    r5,r6 */
   s.registers[0][6]=s.registers[0][5];
   s.pc=0xf03adcu;break;
  case 0xf03adcu: /* jr      n,00F03AE2 */
   if(condition(&s,24)){pending=1;target=0xf03ae2u;}
   s.pc=0xf03adeu;break;
  case 0xf03adeu: /* move    r21,r8 */
   s.registers[0][8]=s.registers[0][21];
   s.pc=0xf03ae0u;break;
  case 0xf03ae0u: /* move    r4,r7 */
   s.registers[0][7]=s.registers[0][4];
   s.pc=0xf03ae2u;break;
case 0xf03ae2u: /* movefa  r15,r1 */
 s.registers[0][1]=s.registers[1][15];
 s.pc=0xf03ae4u;break;
  case 0xf03ae4u: /* sub     r7,r6 */
   s.registers[0][6]=sub(&s,s.registers[0][6],s.registers[0][7]);
   s.pc=0xf03ae6u;break;
  case 0xf03ae6u: /* jump    z,(r22) */
   if(condition(&s,2)){pending=1;target=s.registers[0][22];}
   s.pc=0xf03ae8u;break;
case 0xf03ae8u: /* movefa  r0,r2 */
 s.registers[0][2]=s.registers[1][0];
 s.pc=0xf03aeau;break;
  case 0xf03aeau: /* shlq    $10,r7 */
   s.c=s.registers[0][7]>>31;s.registers[0][7]=s.registers[0][7]<<16;zn(&s,s.registers[0][7]);
   s.pc=0xf03aecu;break;
  case 0xf03aecu: /* bset    $10,r2 */
   s.registers[0][2]|=(1u<<16);
   zn(&s,s.registers[0][2]);
   s.pc=0xf03aeeu;break;
  case 0xf03aeeu: /* shlq    $10,r6 */
   s.c=s.registers[0][6]>>31;s.registers[0][6]=s.registers[0][6]<<16;zn(&s,s.registers[0][6]);
   s.pc=0xf03af0u;break;
  case 0xf03af0u: /* or      r7,r8 */
   s.registers[0][8]|=s.registers[0][7];
   zn(&s,s.registers[0][8]);
   s.pc=0xf03af2u;break;
case 0xf03af2u: /* movefa  r9,r7 */
 s.registers[0][7]=s.registers[1][9];
 s.pc=0xf03af4u;break;
case 0xf03af4u: /* movefa  r10,r3 */
 s.registers[0][3]=s.registers[1][10];
 s.pc=0xf03af6u;break;
  case 0xf03af6u: /* load    (r3),r0 */
   CHECK(rd32(bus,&s,s.registers[0][3]&~3u,&v));s.registers[0][0]=v;
   s.pc=0xf03af8u;break;
  case 0xf03af8u: /* btst    $0,r0 */
   s.z=((~s.registers[0][0])>>0)&1u;
   s.pc=0xf03afau;break;
  case 0xf03afau: /* jr      z,00F03AF6 */
   if(condition(&s,2)){pending=1;target=0xf03af6u;}
   s.pc=0xf03afcu;break;
  case 0xf03afcu: /* bset    $0,r6 */
   s.registers[0][6]|=(1u<<0);
   zn(&s,s.registers[0][6]);
   s.pc=0xf03afeu;break;
  case 0xf03afeu: /* addq    $4,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],4u);
   s.pc=0xf03b00u;break;
  case 0xf03b00u: /* store   r26,(r7) */
   CHECK(wr32(bus,&s,local(s.registers[0][7])?(s.registers[0][7]&~3u):s.registers[0][7],s.registers[0][26]));
   s.pc=0xf03b02u;break;
  case 0xf03b02u: /* store   r6,(r3) */
   CHECK(wr32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],s.registers[0][6]));
   s.pc=0xf03b04u;break;
  case 0xf03b04u: /* addq    $8,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],8u);
   s.pc=0xf03b06u;break;
  case 0xf03b06u: /* addq    $14,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],20u);
   s.pc=0xf03b08u;break;
  case 0xf03b08u: /* addq    $18,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],24u);
   s.pc=0xf03b0au;break;
  case 0xf03b0au: /* store   r8,(r7) */
   CHECK(wr32(bus,&s,local(s.registers[0][7])?(s.registers[0][7]&~3u):s.registers[0][7],s.registers[0][8]));
   s.pc=0xf03b0cu;break;
  case 0xf03b0cu: /* store   r1,(r3) */
   CHECK(wr32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],s.registers[0][1]));
   s.pc=0xf03b0eu;break;
  case 0xf03b0eu: /* addq    $4,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],4u);
   s.pc=0xf03b10u;break;
  case 0xf03b10u: /* addq    $4,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],4u);
   s.pc=0xf03b12u;break;
  case 0xf03b12u: /* store   r2,(r7) */
   CHECK(wr32(bus,&s,local(s.registers[0][7])?(s.registers[0][7]&~3u):s.registers[0][7],s.registers[0][2]));
   s.pc=0xf03b14u;break;
  case 0xf03b14u: /* store   r1,(r3) */
   CHECK(wr32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],s.registers[0][1]));
   s.pc=0xf03b16u;break;
  case 0xf03b16u: /* subq    $c,r7 */
   s.registers[0][7]=sub(&s,s.registers[0][7],12u);
   s.pc=0xf03b18u;break;
  case 0xf03b18u: /* subq    $14,r3 */
   s.registers[0][3]=sub(&s,s.registers[0][3],20u);
   s.pc=0xf03b1au;break;
  case 0xf03b1au: /* subq    $20,r3 */
   s.registers[0][3]=sub(&s,s.registers[0][3],32u);
   s.pc=0xf03b1cu;break;
case 0xf03b1cu: /* movefa  r11,r0 */
 s.registers[0][0]=s.registers[1][11];
 s.pc=0xf03b1eu;break;
  case 0xf03b1eu: /* jump    (r22) */
   if(condition(&s,0)){pending=1;target=s.registers[0][22];}
   s.pc=0xf03b20u;break;
  case 0xf03b20u: /* store   r0,(r3) */
   CHECK(wr32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],s.registers[0][0]));
   s.pc=0xf03b22u;break;
  case 0xf03b22u: /* move    r15,r7 */
   s.registers[0][7]=s.registers[0][15];
   s.pc=0xf03b24u;break;
  case 0xf03b24u: /* move    r9,r6 */
   s.registers[0][6]=s.registers[0][9];
   s.pc=0xf03b26u;break;
  case 0xf03b26u: /* moveq   0,r4 */
   s.registers[0][4]=0u;
   s.pc=0xf03b28u;break;
  case 0xf03b28u: /* add     r0,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],s.registers[0][0]);
   s.pc=0xf03b2au;break;
case 0xf03b2au: /* movefa  r2,r5 */
 s.registers[0][5]=s.registers[1][2];
 s.pc=0xf03b2cu;break;
  case 0xf03b2cu: /* add     r0,r6 */
   s.registers[0][6]=add(&s,s.registers[0][6],s.registers[0][0]);
   s.pc=0xf03b2eu;break;
  case 0xf03b2eu: /* sharq   $10,r7 */
   s.c=s.registers[0][7]&1u;s.registers[0][7]=sar(s.registers[0][7],16);zn(&s,s.registers[0][7]);
   s.pc=0xf03b30u;break;
  case 0xf03b30u: /* sharq   $10,r6 */
   s.c=s.registers[0][6]&1u;s.registers[0][6]=sar(s.registers[0][6],16);zn(&s,s.registers[0][6]);
   s.pc=0xf03b32u;break;
  case 0xf03b32u: /* cmp     r4,r7 */
   (void)sub(&s,s.registers[0][7],s.registers[0][4]);
   s.pc=0xf03b34u;break;
  case 0xf03b34u: /* jump    n,(r22) */
   if(condition(&s,24)){pending=1;target=s.registers[0][22];}
   s.pc=0xf03b36u;break;
  case 0xf03b36u: /* cmp     r6,r5 */
   (void)sub(&s,s.registers[0][5],s.registers[0][6]);
   s.pc=0xf03b38u;break;
  case 0xf03b38u: /* jump    n,(r22) */
   if(condition(&s,24)){pending=1;target=s.registers[0][22];}
   s.pc=0xf03b3au;break;
  case 0xf03b3au: /* move    r7,r8 */
   s.registers[0][8]=s.registers[0][7];
   s.pc=0xf03b3cu;break;
  case 0xf03b3cu: /* sub     r6,r8 */
   s.registers[0][8]=sub(&s,s.registers[0][8],s.registers[0][6]);
   s.pc=0xf03b3eu;break;
  case 0xf03b3eu: /* jump    n,(r22) */
   if(condition(&s,24)){pending=1;target=s.registers[0][22];}
   s.pc=0xf03b40u;break;
  case 0xf03b40u: /* move    r13,r1 */
   s.registers[0][1]=s.registers[0][13];
   s.pc=0xf03b42u;break;
  case 0xf03b42u: /* move    r19,r2 */
   s.registers[0][2]=s.registers[0][19];
   s.pc=0xf03b44u;break;
  case 0xf03b44u: /* sharq   $11,r1 */
   s.c=s.registers[0][1]&1u;s.registers[0][1]=sar(s.registers[0][1],17);zn(&s,s.registers[0][1]);
   s.pc=0xf03b46u;break;
  case 0xf03b46u: /* sharq   $11,r2 */
   s.c=s.registers[0][2]&1u;s.registers[0][2]=sar(s.registers[0][2],17);zn(&s,s.registers[0][2]);
   s.pc=0xf03b48u;break;
  case 0xf03b48u: /* add     r1,r11 */
   s.registers[0][11]=add(&s,s.registers[0][11],s.registers[0][1]);
   s.pc=0xf03b4au;break;
  case 0xf03b4au: /* add     r2,r17 */
   s.registers[0][17]=add(&s,s.registers[0][17],s.registers[0][2]);
   s.pc=0xf03b4cu;break;
  case 0xf03b4cu: /* add     r1,r12 */
   s.registers[0][12]=add(&s,s.registers[0][12],s.registers[0][1]);
   s.pc=0xf03b4eu;break;
  case 0xf03b4eu: /* add     r2,r18 */
   s.registers[0][18]=add(&s,s.registers[0][18],s.registers[0][2]);
   s.pc=0xf03b50u;break;
  case 0xf03b50u: /* move    r13,r1 */
   s.registers[0][1]=s.registers[0][13];
   s.pc=0xf03b52u;break;
  case 0xf03b52u: /* move    r19,r2 */
   s.registers[0][2]=s.registers[0][19];
   s.pc=0xf03b54u;break;
  case 0xf03b54u: /* sharq   $10,r1 */
   s.c=s.registers[0][1]&1u;s.registers[0][1]=sar(s.registers[0][1],16);zn(&s,s.registers[0][1]);
   s.pc=0xf03b56u;break;
  case 0xf03b56u: /* sharq   $10,r2 */
   s.c=s.registers[0][2]&1u;s.registers[0][2]=sar(s.registers[0][2],16);zn(&s,s.registers[0][2]);
   s.pc=0xf03b58u;break;
  case 0xf03b58u: /* abs     r11 */
   s.c=s.registers[0][11]>>31;if(s.registers[0][11]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[0][11]=0u-s.registers[0][11];s.n=0;s.z=s.registers[0][11]==0;}
   s.pc=0xf03b5au;break;
  case 0xf03b5au: /* jr      nc,00F03B60 */
   if(condition(&s,4)){pending=1;target=0xf03b60u;}
   s.pc=0xf03b5cu;break;
  case 0xf03b5cu: /* div     r1,r11 */
   divide(&s,1,11);
   s.pc=0xf03b5eu;break;
  case 0xf03b5eu: /* neg     r11 */
   s.registers[0][11]=sub(&s,0,s.registers[0][11]);
   s.pc=0xf03b60u;break;
  case 0xf03b60u: /* abs     r17 */
   s.c=s.registers[0][17]>>31;if(s.registers[0][17]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[0][17]=0u-s.registers[0][17];s.n=0;s.z=s.registers[0][17]==0;}
   s.pc=0xf03b62u;break;
  case 0xf03b62u: /* jr      nc,00F03B68 */
   if(condition(&s,4)){pending=1;target=0xf03b68u;}
   s.pc=0xf03b64u;break;
  case 0xf03b64u: /* div     r2,r17 */
   divide(&s,2,17);
   s.pc=0xf03b66u;break;
  case 0xf03b66u: /* neg     r17 */
   s.registers[0][17]=sub(&s,0,s.registers[0][17]);
   s.pc=0xf03b68u;break;
  case 0xf03b68u: /* shlq    $10,r11 */
   s.c=s.registers[0][11]>>31;s.registers[0][11]=s.registers[0][11]<<16;zn(&s,s.registers[0][11]);
   s.pc=0xf03b6au;break;
  case 0xf03b6au: /* shlq    $10,r17 */
   s.c=s.registers[0][17]>>31;s.registers[0][17]=s.registers[0][17]<<16;zn(&s,s.registers[0][17]);
   s.pc=0xf03b6cu;break;
  case 0xf03b6cu: /* abs     r12 */
   s.c=s.registers[0][12]>>31;if(s.registers[0][12]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[0][12]=0u-s.registers[0][12];s.n=0;s.z=s.registers[0][12]==0;}
   s.pc=0xf03b6eu;break;
  case 0xf03b6eu: /* jr      nc,00F03B74 */
   if(condition(&s,4)){pending=1;target=0xf03b74u;}
   s.pc=0xf03b70u;break;
  case 0xf03b70u: /* div     r1,r12 */
   divide(&s,1,12);
   s.pc=0xf03b72u;break;
  case 0xf03b72u: /* neg     r12 */
   s.registers[0][12]=sub(&s,0,s.registers[0][12]);
   s.pc=0xf03b74u;break;
  case 0xf03b74u: /* abs     r18 */
   s.c=s.registers[0][18]>>31;if(s.registers[0][18]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[0][18]=0u-s.registers[0][18];s.n=0;s.z=s.registers[0][18]==0;}
   s.pc=0xf03b76u;break;
  case 0xf03b76u: /* jr      nc,00F03B7C */
   if(condition(&s,4)){pending=1;target=0xf03b7cu;}
   s.pc=0xf03b78u;break;
  case 0xf03b78u: /* div     r2,r18 */
   divide(&s,2,18);
   s.pc=0xf03b7au;break;
  case 0xf03b7au: /* neg     r18 */
   s.registers[0][18]=sub(&s,0,s.registers[0][18]);
   s.pc=0xf03b7cu;break;
  case 0xf03b7cu: /* shlq    $10,r12 */
   s.c=s.registers[0][12]>>31;s.registers[0][12]=s.registers[0][12]<<16;zn(&s,s.registers[0][12]);
   s.pc=0xf03b7eu;break;
  case 0xf03b7eu: /* shlq    $10,r18 */
   s.c=s.registers[0][18]>>31;s.registers[0][18]=s.registers[0][18]<<16;zn(&s,s.registers[0][18]);
   s.pc=0xf03b80u;break;
  case 0xf03b80u: /* sub     r11,r17 */
   s.registers[0][17]=sub(&s,s.registers[0][17],s.registers[0][11]);
   s.pc=0xf03b82u;break;
  case 0xf03b82u: /* abs     r17 */
   s.c=s.registers[0][17]>>31;if(s.registers[0][17]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[0][17]=0u-s.registers[0][17];s.n=0;s.z=s.registers[0][17]==0;}
   s.pc=0xf03b84u;break;
  case 0xf03b84u: /* jr      nc,00F03B8A */
   if(condition(&s,4)){pending=1;target=0xf03b8au;}
   s.pc=0xf03b86u;break;
  case 0xf03b86u: /* div     r8,r17 */
   divide(&s,8,17);
   s.pc=0xf03b88u;break;
  case 0xf03b88u: /* neg     r17 */
   s.registers[0][17]=sub(&s,0,s.registers[0][17]);
   s.pc=0xf03b8au;break;
  case 0xf03b8au: /* sub     r12,r18 */
   s.registers[0][18]=sub(&s,s.registers[0][18],s.registers[0][12]);
   s.pc=0xf03b8cu;break;
  case 0xf03b8cu: /* abs     r18 */
   s.c=s.registers[0][18]>>31;if(s.registers[0][18]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[0][18]=0u-s.registers[0][18];s.n=0;s.z=s.registers[0][18]==0;}
   s.pc=0xf03b8eu;break;
  case 0xf03b8eu: /* jr      nc,00F03B94 */
   if(condition(&s,4)){pending=1;target=0xf03b94u;}
   s.pc=0xf03b90u;break;
  case 0xf03b90u: /* div     r8,r18 */
   divide(&s,8,18);
   s.pc=0xf03b92u;break;
  case 0xf03b92u: /* neg     r18 */
   s.registers[0][18]=sub(&s,0,s.registers[0][18]);
   s.pc=0xf03b94u;break;
  case 0xf03b94u: /* cmp     r5,r7 */
   (void)sub(&s,s.registers[0][7],s.registers[0][5]);
   s.pc=0xf03b96u;break;
  case 0xf03b96u: /* jr      n,00F03B9C */
   if(condition(&s,24)){pending=1;target=0xf03b9cu;}
   s.pc=0xf03b98u;break;
  case 0xf03b98u: /* move    r4,r2 */
   s.registers[0][2]=s.registers[0][4];
   s.pc=0xf03b9au;break;
  case 0xf03b9au: /* move    r5,r7 */
   s.registers[0][7]=s.registers[0][5];
   s.pc=0xf03b9cu;break;
  case 0xf03b9cu: /* movei   $f03bca,r0 */
   s.registers[0][0]=0xf03bcau;
   s.pc=0xf03ba2u;break;
  case 0xf03ba2u: /* cmp     r6,r4 */
   (void)sub(&s,s.registers[0][4],s.registers[0][6]);
   s.pc=0xf03ba4u;break;
  case 0xf03ba4u: /* jump    n,(r0) */
   if(condition(&s,24)){pending=1;target=s.registers[0][0];}
   s.pc=0xf03ba6u;break;
  case 0xf03ba6u: /* sub     r6,r2 */
   s.registers[0][2]=sub(&s,s.registers[0][2],s.registers[0][6]);
   s.pc=0xf03ba8u;break;
  case 0xf03ba8u: /* move    r17,r0 */
   s.registers[0][0]=s.registers[0][17];
   s.pc=0xf03baau;break;
  case 0xf03baau: /* move    r18,r1 */
   s.registers[0][1]=s.registers[0][18];
   s.pc=0xf03bacu;break;
  case 0xf03bacu: /* mult    r2,r0 */
   s.registers[0][0]=(s.registers[0][0]&0xffffu)*(s.registers[0][2]&0xffffu);
   zn(&s,s.registers[0][0]);
   s.pc=0xf03baeu;break;
  case 0xf03baeu: /* mult    r2,r1 */
   s.registers[0][1]=(s.registers[0][1]&0xffffu)*(s.registers[0][2]&0xffffu);
   zn(&s,s.registers[0][1]);
   s.pc=0xf03bb0u;break;
  case 0xf03bb0u: /* add     r0,r11 */
   s.registers[0][11]=add(&s,s.registers[0][11],s.registers[0][0]);
   s.pc=0xf03bb2u;break;
  case 0xf03bb2u: /* add     r1,r12 */
   s.registers[0][12]=add(&s,s.registers[0][12],s.registers[0][1]);
   s.pc=0xf03bb4u;break;
  case 0xf03bb4u: /* move    r4,r6 */
   s.registers[0][6]=s.registers[0][4];
   s.pc=0xf03bb6u;break;
  case 0xf03bb6u: /* move    r17,r0 */
   s.registers[0][0]=s.registers[0][17];
   s.pc=0xf03bb8u;break;
  case 0xf03bb8u: /* move    r18,r1 */
   s.registers[0][1]=s.registers[0][18];
   s.pc=0xf03bbau;break;
  case 0xf03bbau: /* shrq    $10,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=s.registers[0][0]>>16;zn(&s,s.registers[0][0]);
   s.pc=0xf03bbcu;break;
  case 0xf03bbcu: /* shrq    $10,r1 */
   s.c=s.registers[0][1]&1u;s.registers[0][1]=s.registers[0][1]>>16;zn(&s,s.registers[0][1]);
   s.pc=0xf03bbeu;break;
  case 0xf03bbeu: /* imult   r2,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][2]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf03bc0u;break;
  case 0xf03bc0u: /* imult   r2,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][2]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf03bc2u;break;
  case 0xf03bc2u: /* shlq    $10,r0 */
   s.c=s.registers[0][0]>>31;s.registers[0][0]=s.registers[0][0]<<16;zn(&s,s.registers[0][0]);
   s.pc=0xf03bc4u;break;
  case 0xf03bc4u: /* shlq    $10,r1 */
   s.c=s.registers[0][1]>>31;s.registers[0][1]=s.registers[0][1]<<16;zn(&s,s.registers[0][1]);
   s.pc=0xf03bc6u;break;
  case 0xf03bc6u: /* add     r0,r11 */
   s.registers[0][11]=add(&s,s.registers[0][11],s.registers[0][0]);
   s.pc=0xf03bc8u;break;
  case 0xf03bc8u: /* add     r1,r12 */
   s.registers[0][12]=add(&s,s.registers[0][12],s.registers[0][1]);
   s.pc=0xf03bcau;break;
  case 0xf03bcau: /* sub     r6,r7 */
   s.registers[0][7]=sub(&s,s.registers[0][7],s.registers[0][6]);
   s.pc=0xf03bccu;break;
  case 0xf03bccu: /* jump    z,(r22) */
   if(condition(&s,2)){pending=1;target=s.registers[0][22];}
   s.pc=0xf03bceu;break;
  case 0xf03bceu: /* move    r12,r0 */
   s.registers[0][0]=s.registers[0][12];
   s.pc=0xf03bd0u;break;
  case 0xf03bd0u: /* move    r11,r4 */
   s.registers[0][4]=s.registers[0][11];
   s.pc=0xf03bd2u;break;
  case 0xf03bd2u: /* shrq    $10,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=s.registers[0][0]>>16;zn(&s,s.registers[0][0]);
   s.pc=0xf03bd4u;break;
  case 0xf03bd4u: /* shrq    $10,r4 */
   s.c=s.registers[0][4]&1u;s.registers[0][4]=s.registers[0][4]>>16;zn(&s,s.registers[0][4]);
   s.pc=0xf03bd6u;break;
  case 0xf03bd6u: /* shlq    $10,r0 */
   s.c=s.registers[0][0]>>31;s.registers[0][0]=s.registers[0][0]<<16;zn(&s,s.registers[0][0]);
   s.pc=0xf03bd8u;break;
  case 0xf03bd8u: /* shlq    $10,r11 */
   s.c=s.registers[0][11]>>31;s.registers[0][11]=s.registers[0][11]<<16;zn(&s,s.registers[0][11]);
   s.pc=0xf03bdau;break;
  case 0xf03bdau: /* or      r0,r4 */
   s.registers[0][4]|=s.registers[0][0];
   zn(&s,s.registers[0][4]);
   s.pc=0xf03bdcu;break;
  case 0xf03bdcu: /* shlq    $10,r12 */
   s.c=s.registers[0][12]>>31;s.registers[0][12]=s.registers[0][12]<<16;zn(&s,s.registers[0][12]);
   s.pc=0xf03bdeu;break;
  case 0xf03bdeu: /* shrq    $10,r11 */
   s.c=s.registers[0][11]&1u;s.registers[0][11]=s.registers[0][11]>>16;zn(&s,s.registers[0][11]);
   s.pc=0xf03be0u;break;
  case 0xf03be0u: /* move    r18,r0 */
   s.registers[0][0]=s.registers[0][18];
   s.pc=0xf03be2u;break;
  case 0xf03be2u: /* or      r12,r11 */
   s.registers[0][11]|=s.registers[0][12];
   zn(&s,s.registers[0][11]);
   s.pc=0xf03be4u;break;
  case 0xf03be4u: /* move    r17,r5 */
   s.registers[0][5]=s.registers[0][17];
   s.pc=0xf03be6u;break;
  case 0xf03be6u: /* shrq    $10,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=s.registers[0][0]>>16;zn(&s,s.registers[0][0]);
   s.pc=0xf03be8u;break;
  case 0xf03be8u: /* shrq    $10,r5 */
   s.c=s.registers[0][5]&1u;s.registers[0][5]=s.registers[0][5]>>16;zn(&s,s.registers[0][5]);
   s.pc=0xf03beau;break;
  case 0xf03beau: /* shlq    $10,r0 */
   s.c=s.registers[0][0]>>31;s.registers[0][0]=s.registers[0][0]<<16;zn(&s,s.registers[0][0]);
   s.pc=0xf03becu;break;
  case 0xf03becu: /* shlq    $10,r17 */
   s.c=s.registers[0][17]>>31;s.registers[0][17]=s.registers[0][17]<<16;zn(&s,s.registers[0][17]);
   s.pc=0xf03beeu;break;
  case 0xf03beeu: /* or      r0,r5 */
   s.registers[0][5]|=s.registers[0][0];
   zn(&s,s.registers[0][5]);
   s.pc=0xf03bf0u;break;
  case 0xf03bf0u: /* shlq    $10,r18 */
   s.c=s.registers[0][18]>>31;s.registers[0][18]=s.registers[0][18]<<16;zn(&s,s.registers[0][18]);
   s.pc=0xf03bf2u;break;
  case 0xf03bf2u: /* shrq    $10,r17 */
   s.c=s.registers[0][17]&1u;s.registers[0][17]=s.registers[0][17]>>16;zn(&s,s.registers[0][17]);
   s.pc=0xf03bf4u;break;
  case 0xf03bf4u: /* move    r21,r8 */
   s.registers[0][8]=s.registers[0][21];
   s.pc=0xf03bf6u;break;
  case 0xf03bf6u: /* or      r18,r17 */
   s.registers[0][17]|=s.registers[0][18];
   zn(&s,s.registers[0][17]);
   s.pc=0xf03bf8u;break;
  case 0xf03bf8u: /* shlq    $10,r8 */
   s.c=s.registers[0][8]>>31;s.registers[0][8]=s.registers[0][8]<<16;zn(&s,s.registers[0][8]);
   s.pc=0xf03bfau;break;
  case 0xf03bfau: /* bset    $10,r7 */
   s.registers[0][7]|=(1u<<16);
   zn(&s,s.registers[0][7]);
   s.pc=0xf03bfcu;break;
case 0xf03bfcu: /* movefa  r8,r1 */
 s.registers[0][1]=s.registers[1][8];
 s.pc=0xf03bfeu;break;
case 0xf03bfeu: /* movefa  r9,r2 */
 s.registers[0][2]=s.registers[1][9];
 s.pc=0xf03c00u;break;
case 0xf03c00u: /* movefa  r10,r3 */
 s.registers[0][3]=s.registers[1][10];
 s.pc=0xf03c02u;break;
  case 0xf03c02u: /* load    (r3),r0 */
   CHECK(rd32(bus,&s,s.registers[0][3]&~3u,&v));s.registers[0][0]=v;
   s.pc=0xf03c04u;break;
  case 0xf03c04u: /* btst    $0,r0 */
   s.z=((~s.registers[0][0])>>0)&1u;
   s.pc=0xf03c06u;break;
  case 0xf03c06u: /* jr      z,00F03C02 */
   if(condition(&s,2)){pending=1;target=0xf03c02u;}
   s.pc=0xf03c08u;break;
  case 0xf03c08u: /* or      r6,r8 */
   s.registers[0][8]|=s.registers[0][6];
   zn(&s,s.registers[0][8]);
   s.pc=0xf03c0au;break;
  case 0xf03c0au: /* store   r24,(r1) */
   CHECK(wr32(bus,&s,local(s.registers[0][1])?(s.registers[0][1]&~3u):s.registers[0][1],s.registers[0][24]));
   s.pc=0xf03c0cu;break;
  case 0xf03c0cu: /* store   r26,(r2) */
   CHECK(wr32(bus,&s,local(s.registers[0][2])?(s.registers[0][2]&~3u):s.registers[0][2],s.registers[0][26]));
   s.pc=0xf03c0eu;break;
  case 0xf03c0eu: /* addq    $4,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],4u);
   s.pc=0xf03c10u;break;
  case 0xf03c10u: /* addq    $8,r2 */
   s.registers[0][2]=add(&s,s.registers[0][2],8u);
   s.pc=0xf03c12u;break;
  case 0xf03c12u: /* store   r25,(r1) */
   CHECK(wr32(bus,&s,local(s.registers[0][1])?(s.registers[0][1]&~3u):s.registers[0][1],s.registers[0][25]));
   s.pc=0xf03c14u;break;
  case 0xf03c14u: /* store   r8,(r2) */
   CHECK(wr32(bus,&s,local(s.registers[0][2])?(s.registers[0][2]&~3u):s.registers[0][2],s.registers[0][8]));
   s.pc=0xf03c16u;break;
  case 0xf03c16u: /* addq    $8,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],8u);
   s.pc=0xf03c18u;break;
  case 0xf03c18u: /* subq    $8,r2 */
   s.registers[0][2]=sub(&s,s.registers[0][2],8u);
   s.pc=0xf03c1au;break;
  case 0xf03c1au: /* store   r4,(r1) */
   CHECK(wr32(bus,&s,local(s.registers[0][1])?(s.registers[0][1]&~3u):s.registers[0][1],s.registers[0][4]));
   s.pc=0xf03c1cu;break;
  case 0xf03c1cu: /* addq    $4,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],4u);
   s.pc=0xf03c1eu;break;
  case 0xf03c1eu: /* addq    $c,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],12u);
   s.pc=0xf03c20u;break;
  case 0xf03c20u: /* store   r7,(r3) */
   CHECK(wr32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],s.registers[0][7]));
   s.pc=0xf03c22u;break;
  case 0xf03c22u: /* store   r11,(r1) */
   CHECK(wr32(bus,&s,local(s.registers[0][1])?(s.registers[0][1]&~3u):s.registers[0][1],s.registers[0][11]));
   s.pc=0xf03c24u;break;
  case 0xf03c24u: /* addq    $20,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],32u);
   s.pc=0xf03c26u;break;
  case 0xf03c26u: /* addq    $4,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],4u);
   s.pc=0xf03c28u;break;
  case 0xf03c28u: /* addq    $14,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],20u);
   s.pc=0xf03c2au;break;
  case 0xf03c2au: /* store   r5,(r1) */
   CHECK(wr32(bus,&s,local(s.registers[0][1])?(s.registers[0][1]&~3u):s.registers[0][1],s.registers[0][5]));
   s.pc=0xf03c2cu;break;
  case 0xf03c2cu: /* store   r27,(r3) */
   CHECK(wr32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],s.registers[0][27]));
   s.pc=0xf03c2eu;break;
  case 0xf03c2eu: /* addq    $4,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],4u);
   s.pc=0xf03c30u;break;
  case 0xf03c30u: /* subq    $18,r3 */
   s.registers[0][3]=sub(&s,s.registers[0][3],24u);
   s.pc=0xf03c32u;break;
  case 0xf03c32u: /* store   r17,(r1) */
   CHECK(wr32(bus,&s,local(s.registers[0][1])?(s.registers[0][1]&~3u):s.registers[0][1],s.registers[0][17]));
   s.pc=0xf03c34u;break;
  case 0xf03c34u: /* subq    $20,r3 */
   s.registers[0][3]=sub(&s,s.registers[0][3],32u);
   s.pc=0xf03c36u;break;
  case 0xf03c36u: /* subq    $20,r1 */
   s.registers[0][1]=sub(&s,s.registers[0][1],32u);
   s.pc=0xf03c38u;break;
case 0xf03c38u: /* movefa  r12,r0 */
 s.registers[0][0]=s.registers[1][12];
 s.pc=0xf03c3au;break;
  case 0xf03c3au: /* jump    (r22) */
   if(condition(&s,0)){pending=1;target=s.registers[0][22];}
   s.pc=0xf03c3cu;break;
  case 0xf03c3cu: /* store   r0,(r3) */
   CHECK(wr32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],s.registers[0][0]));
   s.pc=0xf03c3eu;break;
  case 0xf03c3eu: /* move    r15,r7 */
   s.registers[0][7]=s.registers[0][15];
   s.pc=0xf03c40u;break;
  case 0xf03c40u: /* move    r9,r6 */
   s.registers[0][6]=s.registers[0][9];
   s.pc=0xf03c42u;break;
  case 0xf03c42u: /* moveq   0,r4 */
   s.registers[0][4]=0u;
   s.pc=0xf03c44u;break;
  case 0xf03c44u: /* add     r0,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],s.registers[0][0]);
   s.pc=0xf03c46u;break;
case 0xf03c46u: /* movefa  r2,r5 */
 s.registers[0][5]=s.registers[1][2];
 s.pc=0xf03c48u;break;
  case 0xf03c48u: /* add     r0,r6 */
   s.registers[0][6]=add(&s,s.registers[0][6],s.registers[0][0]);
   s.pc=0xf03c4au;break;
  case 0xf03c4au: /* sharq   $10,r7 */
   s.c=s.registers[0][7]&1u;s.registers[0][7]=sar(s.registers[0][7],16);zn(&s,s.registers[0][7]);
   s.pc=0xf03c4cu;break;
  case 0xf03c4cu: /* sharq   $10,r6 */
   s.c=s.registers[0][6]&1u;s.registers[0][6]=sar(s.registers[0][6],16);zn(&s,s.registers[0][6]);
   s.pc=0xf03c4eu;break;
  case 0xf03c4eu: /* cmp     r4,r7 */
   (void)sub(&s,s.registers[0][7],s.registers[0][4]);
   s.pc=0xf03c50u;break;
  case 0xf03c50u: /* jump    n,(r22) */
   if(condition(&s,24)){pending=1;target=s.registers[0][22];}
   s.pc=0xf03c52u;break;
  case 0xf03c52u: /* cmp     r6,r5 */
   (void)sub(&s,s.registers[0][5],s.registers[0][6]);
   s.pc=0xf03c54u;break;
  case 0xf03c54u: /* jump    n,(r22) */
   if(condition(&s,24)){pending=1;target=s.registers[0][22];}
   s.pc=0xf03c56u;break;
  case 0xf03c56u: /* move    r7,r8 */
   s.registers[0][8]=s.registers[0][7];
   s.pc=0xf03c58u;break;
  case 0xf03c58u: /* sub     r6,r8 */
   s.registers[0][8]=sub(&s,s.registers[0][8],s.registers[0][6]);
   s.pc=0xf03c5au;break;
  case 0xf03c5au: /* jump    n,(r22) */
   if(condition(&s,24)){pending=1;target=s.registers[0][22];}
   s.pc=0xf03c5cu;break;
  case 0xf03c5cu: /* cmp     r5,r7 */
   (void)sub(&s,s.registers[0][7],s.registers[0][5]);
   s.pc=0xf03c5eu;break;
  case 0xf03c5eu: /* jr      n,00F03C64 */
   if(condition(&s,24)){pending=1;target=0xf03c64u;}
   s.pc=0xf03c60u;break;
  case 0xf03c60u: /* cmp     r6,r4 */
   (void)sub(&s,s.registers[0][4],s.registers[0][6]);
   s.pc=0xf03c62u;break;
  case 0xf03c62u: /* move    r5,r7 */
   s.registers[0][7]=s.registers[0][5];
   s.pc=0xf03c64u;break;
  case 0xf03c64u: /* jr      n,00F03C6A */
   if(condition(&s,24)){pending=1;target=0xf03c6au;}
   s.pc=0xf03c66u;break;
  case 0xf03c66u: /* move    r21,r8 */
   s.registers[0][8]=s.registers[0][21];
   s.pc=0xf03c68u;break;
  case 0xf03c68u: /* move    r4,r6 */
   s.registers[0][6]=s.registers[0][4];
   s.pc=0xf03c6au;break;
case 0xf03c6au: /* movefa  r15,r4 */
 s.registers[0][4]=s.registers[1][15];
 s.pc=0xf03c6cu;break;
  case 0xf03c6cu: /* sub     r6,r7 */
   s.registers[0][7]=sub(&s,s.registers[0][7],s.registers[0][6]);
   s.pc=0xf03c6eu;break;
  case 0xf03c6eu: /* jump    z,(r22) */
   if(condition(&s,2)){pending=1;target=s.registers[0][22];}
   s.pc=0xf03c70u;break;
  case 0xf03c70u: /* shlq    $10,r8 */
   s.c=s.registers[0][8]>>31;s.registers[0][8]=s.registers[0][8]<<16;zn(&s,s.registers[0][8]);
   s.pc=0xf03c72u;break;
  case 0xf03c72u: /* bset    $10,r7 */
   s.registers[0][7]|=(1u<<16);
   zn(&s,s.registers[0][7]);
   s.pc=0xf03c74u;break;
case 0xf03c74u: /* movefa  r9,r2 */
 s.registers[0][2]=s.registers[1][9];
 s.pc=0xf03c76u;break;
case 0xf03c76u: /* movefa  r10,r3 */
 s.registers[0][3]=s.registers[1][10];
 s.pc=0xf03c78u;break;
  case 0xf03c78u: /* load    (r3),r0 */
   CHECK(rd32(bus,&s,s.registers[0][3]&~3u,&v));s.registers[0][0]=v;
   s.pc=0xf03c7au;break;
  case 0xf03c7au: /* btst    $0,r0 */
   s.z=((~s.registers[0][0])>>0)&1u;
   s.pc=0xf03c7cu;break;
  case 0xf03c7cu: /* jr      z,00F03C78 */
   if(condition(&s,2)){pending=1;target=0xf03c78u;}
   s.pc=0xf03c7eu;break;
  case 0xf03c7eu: /* or      r6,r8 */
   s.registers[0][8]|=s.registers[0][6];
   zn(&s,s.registers[0][8]);
   s.pc=0xf03c80u;break;
  case 0xf03c80u: /* addq    $4,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],4u);
   s.pc=0xf03c82u;break;
  case 0xf03c82u: /* store   r7,(r3) */
   CHECK(wr32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],s.registers[0][7]));
   s.pc=0xf03c84u;break;
  case 0xf03c84u: /* store   r26,(r2) */
   CHECK(wr32(bus,&s,local(s.registers[0][2])?(s.registers[0][2]&~3u):s.registers[0][2],s.registers[0][26]));
   s.pc=0xf03c86u;break;
  case 0xf03c86u: /* addq    $14,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],20u);
   s.pc=0xf03c88u;break;
  case 0xf03c88u: /* addq    $18,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],24u);
   s.pc=0xf03c8au;break;
  case 0xf03c8au: /* addq    $8,r2 */
   s.registers[0][2]=add(&s,s.registers[0][2],8u);
   s.pc=0xf03c8cu;break;
  case 0xf03c8cu: /* store   r4,(r3) */
   CHECK(wr32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],s.registers[0][4]));
   s.pc=0xf03c8eu;break;
  case 0xf03c8eu: /* addq    $4,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],4u);
   s.pc=0xf03c90u;break;
  case 0xf03c90u: /* store   r8,(r2) */
   CHECK(wr32(bus,&s,local(s.registers[0][2])?(s.registers[0][2]&~3u):s.registers[0][2],s.registers[0][8]));
   s.pc=0xf03c92u;break;
  case 0xf03c92u: /* store   r4,(r3) */
   CHECK(wr32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],s.registers[0][4]));
   s.pc=0xf03c94u;break;
  case 0xf03c94u: /* subq    $8,r2 */
   s.registers[0][2]=sub(&s,s.registers[0][2],8u);
   s.pc=0xf03c96u;break;
  case 0xf03c96u: /* subq    $14,r3 */
   s.registers[0][3]=sub(&s,s.registers[0][3],20u);
   s.pc=0xf03c98u;break;
  case 0xf03c98u: /* subq    $20,r3 */
   s.registers[0][3]=sub(&s,s.registers[0][3],32u);
   s.pc=0xf03c9au;break;
case 0xf03c9au: /* movefa  r11,r0 */
 s.registers[0][0]=s.registers[1][11];
 s.pc=0xf03c9cu;break;
  case 0xf03c9cu: /* jump    (r22) */
   if(condition(&s,0)){pending=1;target=s.registers[0][22];}
   s.pc=0xf03c9eu;break;
  case 0xf03c9eu: /* store   r0,(r3) */
   CHECK(wr32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],s.registers[0][0]));
   s.pc=0xf03ca0u;break;
  case 0xf03ca0u: /* movei   $f03210,r0 */
   s.registers[0][0]=0xf03210u;
   s.pc=0xf03ca6u;break;
case 0xf03ca6u: /* movefa  r0,r21 */
 s.registers[0][21]=s.registers[1][0];
 s.pc=0xf03ca8u;break;
  case 0xf03ca8u: /* load    (r0),r1 */
   CHECK(rd32(bus,&s,s.registers[0][0]&~3u,&v));s.registers[0][1]=v;
   s.pc=0xf03caau;break;
case 0xf03caau: /* movefa  r0,r22 */
 s.registers[0][22]=s.registers[1][0];
 s.pc=0xf03cacu;break;
  case 0xf03cacu: /* addq    $16,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],22u);
   s.pc=0xf03caeu;break;
  case 0xf03caeu: /* shlq    $10,r22 */
   s.c=s.registers[0][22]>>31;s.registers[0][22]=s.registers[0][22]<<16;zn(&s,s.registers[0][22]);
   s.pc=0xf03cb0u;break;
  case 0xf03cb0u: /* loadw   (r1),r25 */
   CHECK(loadw(bus,&s,s.registers[0][1],&v));s.registers[0][25]=v;
   s.pc=0xf03cb2u;break;
  case 0xf03cb2u: /* movei   $f037f4,r27 */
   s.registers[0][27]=0xf037f4u;
   s.pc=0xf03cb8u;break;
  case 0xf03cb8u: /* shlq    $10,r25 */
   s.c=s.registers[0][25]>>31;s.registers[0][25]=s.registers[0][25]<<16;zn(&s,s.registers[0][25]);
   s.pc=0xf03cbau;break;
  case 0xf03cbau: /* moveq   31,r2 */
   s.registers[0][2]=31u;
   s.pc=0xf03cbcu;break;
  case 0xf03cbcu: /* sharq   $10,r25 */
   s.c=s.registers[0][25]&1u;s.registers[0][25]=sar(s.registers[0][25],16);zn(&s,s.registers[0][25]);
   s.pc=0xf03cbeu;break;
  case 0xf03cbeu: /* movei   $300,r3 */
   s.registers[0][3]=0x300u;
   s.pc=0xf03cc4u;break;
  case 0xf03cc4u: /* cmp     r2,r25 */
   (void)sub(&s,s.registers[0][25],s.registers[0][2]);
   s.pc=0xf03cc6u;break;
  case 0xf03cc6u: /* jump    n,(r27) */
   if(condition(&s,24)){pending=1;target=s.registers[0][27];}
   s.pc=0xf03cc8u;break;
  case 0xf03cc8u: /* cmp     r25,r3 */
   (void)sub(&s,s.registers[0][3],s.registers[0][25]);
   s.pc=0xf03ccau;break;
  case 0xf03ccau: /* jump    n,(r27) */
   if(condition(&s,24)){pending=1;target=s.registers[0][27];}
   s.pc=0xf03cccu;break;
  case 0xf03cccu: /* subq    $4,r0 */
   s.registers[0][0]=sub(&s,s.registers[0][0],4u);
   s.pc=0xf03cceu;break;
  case 0xf03cceu: /* subq    $4,r1 */
   s.registers[0][1]=sub(&s,s.registers[0][1],4u);
   s.pc=0xf03cd0u;break;
  case 0xf03cd0u: /* load    (r0),r26 */
   CHECK(rd32(bus,&s,s.registers[0][0]&~3u,&v));s.registers[0][26]=v;
   s.pc=0xf03cd2u;break;
  case 0xf03cd2u: /* movei   $ad,r18 */
   s.registers[0][18]=0xadu;
   s.pc=0xf03cd8u;break;
  case 0xf03cd8u: /* load    (r26),r2 */
   CHECK(rd32(bus,&s,s.registers[0][26]&~3u,&v));s.registers[0][2]=v;
   s.pc=0xf03cdau;break;
  case 0xf03cdau: /* move    r18,r3 */
   s.registers[0][3]=s.registers[0][18];
   s.pc=0xf03cdcu;break;
  case 0xf03cdcu: /* addq    $4,r26 */
   s.registers[0][26]=add(&s,s.registers[0][26],4u);
   s.pc=0xf03cdeu;break;
  case 0xf03cdeu: /* shlq    $10,r18 */
   s.c=s.registers[0][18]>>31;s.registers[0][18]=s.registers[0][18]<<16;zn(&s,s.registers[0][18]);
   s.pc=0xf03ce0u;break;
  case 0xf03ce0u: /* loadw   (r26),r4 */
   CHECK(loadw(bus,&s,s.registers[0][26],&v));s.registers[0][4]=v;
   s.pc=0xf03ce2u;break;
  case 0xf03ce2u: /* div     r2,r18 */
   divide(&s,2,18);
   s.pc=0xf03ce4u;break;
  case 0xf03ce4u: /* addq    $2,r26 */
   s.registers[0][26]=add(&s,s.registers[0][26],2u);
   s.pc=0xf03ce6u;break;
  case 0xf03ce6u: /* or      r18,r18 */
   s.registers[0][18]|=s.registers[0][18];
   zn(&s,s.registers[0][18]);
   s.pc=0xf03ce8u;break;
  case 0xf03ce8u: /* loadw   (r26),r5 */
   CHECK(loadw(bus,&s,s.registers[0][26],&v));s.registers[0][5]=v;
   s.pc=0xf03ceau;break;
  case 0xf03ceau: /* shlq    $10,r18 */
   s.c=s.registers[0][18]>>31;s.registers[0][18]=s.registers[0][18]<<16;zn(&s,s.registers[0][18]);
   s.pc=0xf03cecu;break;
  case 0xf03cecu: /* addq    $2,r26 */
   s.registers[0][26]=add(&s,s.registers[0][26],2u);
   s.pc=0xf03ceeu;break;
  case 0xf03ceeu: /* div     r25,r18 */
   divide(&s,25,18);
   s.pc=0xf03cf0u;break;
  case 0xf03cf0u: /* loadw   (r26),r11 */
   CHECK(loadw(bus,&s,s.registers[0][26],&v));s.registers[0][11]=v;
   s.pc=0xf03cf2u;break;
  case 0xf03cf2u: /* or      r18,r18 */
   s.registers[0][18]|=s.registers[0][18];
   zn(&s,s.registers[0][18]);
   s.pc=0xf03cf4u;break;
  case 0xf03cf4u: /* addq    $2,r26 */
   s.registers[0][26]=add(&s,s.registers[0][26],2u);
   s.pc=0xf03cf6u;break;
  case 0xf03cf6u: /* moveq   1,r20 */
   s.registers[0][20]=1u;
   s.pc=0xf03cf8u;break;
  case 0xf03cf8u: /* loadw   (r26),r12 */
   CHECK(loadw(bus,&s,s.registers[0][26],&v));s.registers[0][12]=v;
   s.pc=0xf03cfau;break;
  case 0xf03cfau: /* shlq    $1f,r20 */
   s.c=s.registers[0][20]>>31;s.registers[0][20]=s.registers[0][20]<<31;zn(&s,s.registers[0][20]);
   s.pc=0xf03cfcu;break;
  case 0xf03cfcu: /* addq    $2,r26 */
   s.registers[0][26]=add(&s,s.registers[0][26],2u);
   s.pc=0xf03cfeu;break;
  case 0xf03cfeu: /* div     r18,r20 */
   divide(&s,18,20);
   s.pc=0xf03d00u;break;
  case 0xf03d00u: /* load    (r26),r19 */
   CHECK(rd32(bus,&s,s.registers[0][26]&~3u,&v));s.registers[0][19]=v;
   s.pc=0xf03d02u;break;
  case 0xf03d02u: /* or      r20,r20 */
   s.registers[0][20]|=s.registers[0][20];
   zn(&s,s.registers[0][20]);
   s.pc=0xf03d04u;break;
  case 0xf03d04u: /* addq    $4,r26 */
   s.registers[0][26]=add(&s,s.registers[0][26],4u);
   s.pc=0xf03d06u;break;
  case 0xf03d06u: /* shlq    $1,r20 */
   s.c=s.registers[0][20]>>31;s.registers[0][20]=s.registers[0][20]<<1;zn(&s,s.registers[0][20]);
   s.pc=0xf03d08u;break;
  case 0xf03d08u: /* shlq    $10,r4 */
   s.c=s.registers[0][4]>>31;s.registers[0][4]=s.registers[0][4]<<16;zn(&s,s.registers[0][4]);
   s.pc=0xf03d0au;break;
  case 0xf03d0au: /* shlq    $10,r5 */
   s.c=s.registers[0][5]>>31;s.registers[0][5]=s.registers[0][5]<<16;zn(&s,s.registers[0][5]);
   s.pc=0xf03d0cu;break;
  case 0xf03d0cu: /* moveq   1,r13 */
   s.registers[0][13]=1u;
   s.pc=0xf03d0eu;break;
  case 0xf03d0eu: /* btst    $f,r11 */
   s.z=((~s.registers[0][11])>>15)&1u;
   s.pc=0xf03d10u;break;
  case 0xf03d10u: /* jr      z,00F03D18 */
   if(condition(&s,2)){pending=1;target=0xf03d18u;}
   s.pc=0xf03d12u;break;
  case 0xf03d12u: /* bclr    $f,r11 */
   s.registers[0][11]&=~(1u<<15);
   zn(&s,s.registers[0][11]);
   s.pc=0xf03d14u;break;
  case 0xf03d14u: /* neg     r4 */
   s.registers[0][4]=sub(&s,0,s.registers[0][4]);
   s.pc=0xf03d16u;break;
  case 0xf03d16u: /* neg     r13 */
   s.registers[0][13]=sub(&s,0,s.registers[0][13]);
   s.pc=0xf03d18u;break;
  case 0xf03d18u: /* move    r4,r6 */
   s.registers[0][6]=s.registers[0][4];
   s.pc=0xf03d1au;break;
  case 0xf03d1au: /* move    r5,r7 */
   s.registers[0][7]=s.registers[0][5];
   s.pc=0xf03d1cu;break;
  case 0xf03d1cu: /* abs     r4 */
   s.c=s.registers[0][4]>>31;if(s.registers[0][4]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[0][4]=0u-s.registers[0][4];s.n=0;s.z=s.registers[0][4]==0;}
   s.pc=0xf03d1eu;break;
  case 0xf03d1eu: /* jr      nc,00F03D24 */
   if(condition(&s,4)){pending=1;target=0xf03d24u;}
   s.pc=0xf03d20u;break;
  case 0xf03d20u: /* div     r2,r4 */
   divide(&s,2,4);
   s.pc=0xf03d22u;break;
  case 0xf03d22u: /* neg     r4 */
   s.registers[0][4]=sub(&s,0,s.registers[0][4]);
   s.pc=0xf03d24u;break;
  case 0xf03d24u: /* abs     r5 */
   s.c=s.registers[0][5]>>31;if(s.registers[0][5]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[0][5]=0u-s.registers[0][5];s.n=0;s.z=s.registers[0][5]==0;}
   s.pc=0xf03d26u;break;
  case 0xf03d26u: /* jr      nc,00F03D2C */
   if(condition(&s,4)){pending=1;target=0xf03d2cu;}
   s.pc=0xf03d28u;break;
  case 0xf03d28u: /* div     r2,r5 */
   divide(&s,2,5);
   s.pc=0xf03d2au;break;
  case 0xf03d2au: /* neg     r5 */
   s.registers[0][5]=sub(&s,0,s.registers[0][5]);
   s.pc=0xf03d2cu;break;
  case 0xf03d2cu: /* loadw   (r1),r23 */
   CHECK(loadw(bus,&s,s.registers[0][1],&v));s.registers[0][23]=v;
   s.pc=0xf03d2eu;break;
  case 0xf03d2eu: /* shlq    $10,r23 */
   s.c=s.registers[0][23]>>31;s.registers[0][23]=s.registers[0][23]<<16;zn(&s,s.registers[0][23]);
   s.pc=0xf03d30u;break;
  case 0xf03d30u: /* addq    $2,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],2u);
   s.pc=0xf03d32u;break;
  case 0xf03d32u: /* sharq   $10,r23 */
   s.c=s.registers[0][23]&1u;s.registers[0][23]=sar(s.registers[0][23],16);zn(&s,s.registers[0][23]);
   s.pc=0xf03d34u;break;
  case 0xf03d34u: /* loadw   (r1),r24 */
   CHECK(loadw(bus,&s,s.registers[0][1],&v));s.registers[0][24]=v;
   s.pc=0xf03d36u;break;
  case 0xf03d36u: /* shlq    $10,r24 */
   s.c=s.registers[0][24]>>31;s.registers[0][24]=s.registers[0][24]<<16;zn(&s,s.registers[0][24]);
   s.pc=0xf03d38u;break;
  case 0xf03d38u: /* add     r4,r23 */
   s.registers[0][23]=add(&s,s.registers[0][23],s.registers[0][4]);
   s.pc=0xf03d3au;break;
  case 0xf03d3au: /* sharq   $10,r24 */
   s.c=s.registers[0][24]&1u;s.registers[0][24]=sar(s.registers[0][24],16);zn(&s,s.registers[0][24]);
   s.pc=0xf03d3cu;break;
  case 0xf03d3cu: /* add     r5,r24 */
   s.registers[0][24]=add(&s,s.registers[0][24],s.registers[0][5]);
   s.pc=0xf03d3eu;break;
  case 0xf03d3eu: /* movei   $6f,r8 */
   s.registers[0][8]=0x6fu;
   s.pc=0xf03d44u;break;
  case 0xf03d44u: /* imult   r3,r23 */
   s.registers[0][23]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][23])*(int32_t)sx16(s.registers[0][3]));
   zn(&s,s.registers[0][23]);
   s.pc=0xf03d46u;break;
  case 0xf03d46u: /* movei   $59,r9 */
   s.registers[0][9]=0x59u;
   s.pc=0xf03d4cu;break;
  case 0xf03d4cu: /* imult   r3,r24 */
   s.registers[0][24]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][24])*(int32_t)sx16(s.registers[0][3]));
   zn(&s,s.registers[0][24]);
   s.pc=0xf03d4eu;break;
  case 0xf03d4eu: /* abs     r23 */
   s.c=s.registers[0][23]>>31;if(s.registers[0][23]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[0][23]=0u-s.registers[0][23];s.n=0;s.z=s.registers[0][23]==0;}
   s.pc=0xf03d50u;break;
  case 0xf03d50u: /* jr      nc,00F03D56 */
   if(condition(&s,4)){pending=1;target=0xf03d56u;}
   s.pc=0xf03d52u;break;
  case 0xf03d52u: /* div     r25,r23 */
   divide(&s,25,23);
   s.pc=0xf03d54u;break;
  case 0xf03d54u: /* neg     r23 */
   s.registers[0][23]=sub(&s,0,s.registers[0][23]);
   s.pc=0xf03d56u;break;
  case 0xf03d56u: /* abs     r24 */
   s.c=s.registers[0][24]>>31;if(s.registers[0][24]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[0][24]=0u-s.registers[0][24];s.n=0;s.z=s.registers[0][24]==0;}
   s.pc=0xf03d58u;break;
  case 0xf03d58u: /* jr      nc,00F03D5E */
   if(condition(&s,4)){pending=1;target=0xf03d5eu;}
   s.pc=0xf03d5au;break;
  case 0xf03d5au: /* div     r25,r24 */
   divide(&s,25,24);
   s.pc=0xf03d5cu;break;
  case 0xf03d5cu: /* neg     r24 */
   s.registers[0][24]=sub(&s,0,s.registers[0][24]);
   s.pc=0xf03d5eu;break;
  case 0xf03d5eu: /* add     r8,r23 */
   s.registers[0][23]=add(&s,s.registers[0][23],s.registers[0][8]);
   s.pc=0xf03d60u;break;
  case 0xf03d60u: /* add     r9,r24 */
   s.registers[0][24]=add(&s,s.registers[0][24],s.registers[0][9]);
   s.pc=0xf03d62u;break;
  case 0xf03d62u: /* move    r18,r2 */
   s.registers[0][2]=s.registers[0][18];
   s.pc=0xf03d64u;break;
  case 0xf03d64u: /* move    r18,r16 */
   s.registers[0][16]=s.registers[0][18];
   s.pc=0xf03d66u;break;
  case 0xf03d66u: /* sharq   $10,r16 */
   s.c=s.registers[0][16]&1u;s.registers[0][16]=sar(s.registers[0][16],16);zn(&s,s.registers[0][16]);
   s.pc=0xf03d68u;break;
  case 0xf03d68u: /* mult    r11,r2 */
   s.registers[0][2]=(s.registers[0][2]&0xffffu)*(s.registers[0][11]&0xffffu);
   zn(&s,s.registers[0][2]);
   s.pc=0xf03d6au;break;
  case 0xf03d6au: /* imult   r11,r16 */
   s.registers[0][16]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][16])*(int32_t)sx16(s.registers[0][11]));
   zn(&s,s.registers[0][16]);
   s.pc=0xf03d6cu;break;
  case 0xf03d6cu: /* shrq    $10,r2 */
   s.c=s.registers[0][2]&1u;s.registers[0][2]=s.registers[0][2]>>16;zn(&s,s.registers[0][2]);
   s.pc=0xf03d6eu;break;
  case 0xf03d6eu: /* add     r2,r16 */
   s.registers[0][16]=add(&s,s.registers[0][16],s.registers[0][2]);
   s.pc=0xf03d70u;break;
  case 0xf03d70u: /* jump    z,(r27) */
   if(condition(&s,2)){pending=1;target=s.registers[0][27];}
   s.pc=0xf03d72u;break;
  case 0xf03d72u: /* move    r18,r2 */
   s.registers[0][2]=s.registers[0][18];
   s.pc=0xf03d74u;break;
  case 0xf03d74u: /* move    r18,r17 */
   s.registers[0][17]=s.registers[0][18];
   s.pc=0xf03d76u;break;
  case 0xf03d76u: /* sharq   $10,r17 */
   s.c=s.registers[0][17]&1u;s.registers[0][17]=sar(s.registers[0][17],16);zn(&s,s.registers[0][17]);
   s.pc=0xf03d78u;break;
  case 0xf03d78u: /* mult    r12,r2 */
   s.registers[0][2]=(s.registers[0][2]&0xffffu)*(s.registers[0][12]&0xffffu);
   zn(&s,s.registers[0][2]);
   s.pc=0xf03d7au;break;
  case 0xf03d7au: /* imult   r12,r17 */
   s.registers[0][17]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][17])*(int32_t)sx16(s.registers[0][12]));
   zn(&s,s.registers[0][17]);
   s.pc=0xf03d7cu;break;
  case 0xf03d7cu: /* shrq    $10,r2 */
   s.c=s.registers[0][2]&1u;s.registers[0][2]=s.registers[0][2]>>16;zn(&s,s.registers[0][2]);
   s.pc=0xf03d7eu;break;
  case 0xf03d7eu: /* add     r2,r17 */
   s.registers[0][17]=add(&s,s.registers[0][17],s.registers[0][2]);
   s.pc=0xf03d80u;break;
  case 0xf03d80u: /* jump    z,(r27) */
   if(condition(&s,2)){pending=1;target=s.registers[0][27];}
   s.pc=0xf03d82u;break;
  case 0xf03d82u: /* move    r16,r4 */
   s.registers[0][4]=s.registers[0][16];
   s.pc=0xf03d84u;break;
  case 0xf03d84u: /* move    r17,r5 */
   s.registers[0][5]=s.registers[0][17];
   s.pc=0xf03d86u;break;
  case 0xf03d86u: /* sharq   $1,r4 */
   s.c=s.registers[0][4]&1u;s.registers[0][4]=sar(s.registers[0][4],1);zn(&s,s.registers[0][4]);
   s.pc=0xf03d88u;break;
  case 0xf03d88u: /* sharq   $1,r5 */
   s.c=s.registers[0][5]&1u;s.registers[0][5]=sar(s.registers[0][5],1);zn(&s,s.registers[0][5]);
   s.pc=0xf03d8au;break;
  case 0xf03d8au: /* sub     r4,r23 */
   s.registers[0][23]=sub(&s,s.registers[0][23],s.registers[0][4]);
   s.pc=0xf03d8cu;break;
  case 0xf03d8cu: /* sub     r5,r24 */
   s.registers[0][24]=sub(&s,s.registers[0][24],s.registers[0][5]);
   s.pc=0xf03d8eu;break;
case 0xf03d8eu: /* movefa  r2,r1 */
 s.registers[0][1]=s.registers[1][2];
 s.pc=0xf03d90u;break;
case 0xf03d90u: /* movefa  r3,r3 */
 s.registers[0][3]=s.registers[1][3];
 s.pc=0xf03d92u;break;
  case 0xf03d92u: /* cmp     r1,r23 */
   (void)sub(&s,s.registers[0][23],s.registers[0][1]);
   s.pc=0xf03d94u;break;
  case 0xf03d94u: /* jump    nn,(r27) */
   if(condition(&s,20)){pending=1;target=s.registers[0][27];}
   s.pc=0xf03d96u;break;
  case 0xf03d96u: /* cmp     r3,r24 */
   (void)sub(&s,s.registers[0][24],s.registers[0][3]);
   s.pc=0xf03d98u;break;
  case 0xf03d98u: /* jump    nn,(r27) */
   if(condition(&s,20)){pending=1;target=s.registers[0][27];}
   s.pc=0xf03d9au;break;
  case 0xf03d9au: /* move    r23,r4 */
   s.registers[0][4]=s.registers[0][23];
   s.pc=0xf03d9cu;break;
  case 0xf03d9cu: /* move    r24,r5 */
   s.registers[0][5]=s.registers[0][24];
   s.pc=0xf03d9eu;break;
  case 0xf03d9eu: /* add     r16,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],s.registers[0][16]);
   s.pc=0xf03da0u;break;
  case 0xf03da0u: /* add     r17,r5 */
   s.registers[0][5]=add(&s,s.registers[0][5],s.registers[0][17]);
   s.pc=0xf03da2u;break;
  case 0xf03da2u: /* moveq   0,r0 */
   s.registers[0][0]=0u;
   s.pc=0xf03da4u;break;
  case 0xf03da4u: /* moveq   0,r2 */
   s.registers[0][2]=0u;
   s.pc=0xf03da6u;break;
  case 0xf03da6u: /* cmp     r4,r0 */
   (void)sub(&s,s.registers[0][0],s.registers[0][4]);
   s.pc=0xf03da8u;break;
  case 0xf03da8u: /* jump    nn,(r27) */
   if(condition(&s,20)){pending=1;target=s.registers[0][27];}
   s.pc=0xf03daau;break;
  case 0xf03daau: /* cmp     r5,r2 */
   (void)sub(&s,s.registers[0][2],s.registers[0][5]);
   s.pc=0xf03dacu;break;
  case 0xf03dacu: /* jump    nn,(r27) */
   if(condition(&s,20)){pending=1;target=s.registers[0][27];}
   s.pc=0xf03daeu;break;
  case 0xf03daeu: /* sub     r1,r4 */
   s.registers[0][4]=sub(&s,s.registers[0][4],s.registers[0][1]);
   s.pc=0xf03db0u;break;
  case 0xf03db0u: /* jr      n,00F03DB6 */
   if(condition(&s,24)){pending=1;target=0xf03db6u;}
   s.pc=0xf03db2u;break;
  case 0xf03db2u: /* nop */
   s.pc=0xf03db4u;break;
  case 0xf03db4u: /* sub     r4,r16 */
   s.registers[0][16]=sub(&s,s.registers[0][16],s.registers[0][4]);
   s.pc=0xf03db6u;break;
  case 0xf03db6u: /* sub     r3,r5 */
   s.registers[0][5]=sub(&s,s.registers[0][5],s.registers[0][3]);
   s.pc=0xf03db8u;break;
  case 0xf03db8u: /* jr      n,00F03DBE */
   if(condition(&s,24)){pending=1;target=0xf03dbeu;}
   s.pc=0xf03dbau;break;
  case 0xf03dbau: /* nop */
   s.pc=0xf03dbcu;break;
  case 0xf03dbcu: /* sub     r5,r17 */
   s.registers[0][17]=sub(&s,s.registers[0][17],s.registers[0][5]);
   s.pc=0xf03dbeu;break;
  case 0xf03dbeu: /* move    r0,r4 */
   s.registers[0][4]=s.registers[0][0];
   s.pc=0xf03dc0u;break;
  case 0xf03dc0u: /* move    r2,r5 */
   s.registers[0][5]=s.registers[0][2];
   s.pc=0xf03dc2u;break;
  case 0xf03dc2u: /* sub     r23,r4 */
   s.registers[0][4]=sub(&s,s.registers[0][4],s.registers[0][23]);
   s.pc=0xf03dc4u;break;
  case 0xf03dc4u: /* jr      n,00F03DDA */
   if(condition(&s,24)){pending=1;target=0xf03ddau;}
   s.pc=0xf03dc6u;break;
  case 0xf03dc6u: /* moveq   0,r14 */
   s.registers[0][14]=0u;
   s.pc=0xf03dc8u;break;
  case 0xf03dc8u: /* move    r0,r23 */
   s.registers[0][23]=s.registers[0][0];
   s.pc=0xf03dcau;break;
  case 0xf03dcau: /* sub     r4,r16 */
   s.registers[0][16]=sub(&s,s.registers[0][16],s.registers[0][4]);
   s.pc=0xf03dccu;break;
  case 0xf03dccu: /* move    r20,r14 */
   s.registers[0][14]=s.registers[0][20];
   s.pc=0xf03dceu;break;
  case 0xf03dceu: /* move    r20,r6 */
   s.registers[0][6]=s.registers[0][20];
   s.pc=0xf03dd0u;break;
  case 0xf03dd0u: /* sharq   $10,r14 */
   s.c=s.registers[0][14]&1u;s.registers[0][14]=sar(s.registers[0][14],16);zn(&s,s.registers[0][14]);
   s.pc=0xf03dd2u;break;
  case 0xf03dd2u: /* imult   r4,r14 */
   s.registers[0][14]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][14])*(int32_t)sx16(s.registers[0][4]));
   zn(&s,s.registers[0][14]);
   s.pc=0xf03dd4u;break;
  case 0xf03dd4u: /* mult    r4,r6 */
   s.registers[0][6]=(s.registers[0][6]&0xffffu)*(s.registers[0][4]&0xffffu);
   zn(&s,s.registers[0][6]);
   s.pc=0xf03dd6u;break;
  case 0xf03dd6u: /* shlq    $10,r14 */
   s.c=s.registers[0][14]>>31;s.registers[0][14]=s.registers[0][14]<<16;zn(&s,s.registers[0][14]);
   s.pc=0xf03dd8u;break;
  case 0xf03dd8u: /* add     r6,r14 */
   s.registers[0][14]=add(&s,s.registers[0][14],s.registers[0][6]);
   s.pc=0xf03ddau;break;
  case 0xf03ddau: /* sub     r24,r5 */
   s.registers[0][5]=sub(&s,s.registers[0][5],s.registers[0][24]);
   s.pc=0xf03ddcu;break;
  case 0xf03ddcu: /* jr      n,00F03DF2 */
   if(condition(&s,24)){pending=1;target=0xf03df2u;}
   s.pc=0xf03ddeu;break;
  case 0xf03ddeu: /* moveq   0,r15 */
   s.registers[0][15]=0u;
   s.pc=0xf03de0u;break;
  case 0xf03de0u: /* move    r2,r24 */
   s.registers[0][24]=s.registers[0][2];
   s.pc=0xf03de2u;break;
  case 0xf03de2u: /* sub     r5,r17 */
   s.registers[0][17]=sub(&s,s.registers[0][17],s.registers[0][5]);
   s.pc=0xf03de4u;break;
  case 0xf03de4u: /* move    r20,r15 */
   s.registers[0][15]=s.registers[0][20];
   s.pc=0xf03de6u;break;
  case 0xf03de6u: /* move    r20,r7 */
   s.registers[0][7]=s.registers[0][20];
   s.pc=0xf03de8u;break;
  case 0xf03de8u: /* sharq   $10,r15 */
   s.c=s.registers[0][15]&1u;s.registers[0][15]=sar(s.registers[0][15],16);zn(&s,s.registers[0][15]);
   s.pc=0xf03deau;break;
  case 0xf03deau: /* imult   r5,r15 */
   s.registers[0][15]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][15])*(int32_t)sx16(s.registers[0][5]));
   zn(&s,s.registers[0][15]);
   s.pc=0xf03decu;break;
  case 0xf03decu: /* mult    r5,r7 */
   s.registers[0][7]=(s.registers[0][7]&0xffffu)*(s.registers[0][5]&0xffffu);
   zn(&s,s.registers[0][7]);
   s.pc=0xf03deeu;break;
  case 0xf03deeu: /* shlq    $10,r15 */
   s.c=s.registers[0][15]>>31;s.registers[0][15]=s.registers[0][15]<<16;zn(&s,s.registers[0][15]);
   s.pc=0xf03df0u;break;
  case 0xf03df0u: /* add     r7,r15 */
   s.registers[0][15]=add(&s,s.registers[0][15],s.registers[0][7]);
   s.pc=0xf03df2u;break;
  case 0xf03df2u: /* shlq    $5,r25 */
   s.c=s.registers[0][25]>>31;s.registers[0][25]=s.registers[0][25]<<5;zn(&s,s.registers[0][25]);
   s.pc=0xf03df4u;break;
case 0xf03df4u: /* movefa  r1,r8 */
 s.registers[0][8]=s.registers[1][1];
 s.pc=0xf03df6u;break;
  case 0xf03df6u: /* neg     r25 */
   s.registers[0][25]=sub(&s,0,s.registers[0][25]);
   s.pc=0xf03df8u;break;
  case 0xf03df8u: /* neg     r8 */
   s.registers[0][8]=sub(&s,0,s.registers[0][8]);
   s.pc=0xf03dfau;break;
  case 0xf03dfau: /* cmp     r8,r25 */
   (void)sub(&s,s.registers[0][25],s.registers[0][8]);
   s.pc=0xf03dfcu;break;
  case 0xf03dfcu: /* jr      nn,00F03E02 */
   if(condition(&s,20)){pending=1;target=0xf03e02u;}
   s.pc=0xf03dfeu;break;
  case 0xf03dfeu: /* nop */
   s.pc=0xf03e00u;break;
  case 0xf03e00u: /* move    r8,r25 */
   s.registers[0][25]=s.registers[0][8];
   s.pc=0xf03e02u;break;
  case 0xf03e02u: /* shlq    $10,r25 */
   s.c=s.registers[0][25]>>31;s.registers[0][25]=s.registers[0][25]<<16;zn(&s,s.registers[0][25]);
   s.pc=0xf03e04u;break;
  case 0xf03e04u: /* shrq    $8,r25 */
   s.c=s.registers[0][25]&1u;s.registers[0][25]=s.registers[0][25]>>8;zn(&s,s.registers[0][25]);
   s.pc=0xf03e06u;break;
case 0xf03e06u: /* movefa  r8,r1 */
 s.registers[0][1]=s.registers[1][8];
 s.pc=0xf03e08u;break;
case 0xf03e08u: /* movefa  r9,r2 */
 s.registers[0][2]=s.registers[1][9];
 s.pc=0xf03e0au;break;
case 0xf03e0au: /* movefa  r10,r3 */
 s.registers[0][3]=s.registers[1][10];
 s.pc=0xf03e0cu;break;
  case 0xf03e0cu: /* movei   $f02268,r4 */
   s.registers[0][4]=0xf02268u;
   s.pc=0xf03e12u;break;
  case 0xf03e12u: /* movei   $13e20,r5 */
   s.registers[0][5]=0x13e20u;
   s.pc=0xf03e18u;break;
  case 0xf03e18u: /* movei   $49802f09,r6 */
   s.registers[0][6]=0x49802f09u;
   s.pc=0xf03e1eu;break;
  case 0xf03e1eu: /* cmpq    $0,r13 */
   (void)sub(&s,s.registers[0][13],0x0u);
   s.pc=0xf03e20u;break;
  case 0xf03e20u: /* jr      nn,00F03E2C */
   if(condition(&s,20)){pending=1;target=0xf03e2cu;}
   s.pc=0xf03e22u;break;
  case 0xf03e22u: /* subq    $1,r11 */
   s.registers[0][11]=sub(&s,s.registers[0][11],1u);
   s.pc=0xf03e24u;break;
  case 0xf03e24u: /* shlq    $10,r11 */
   s.c=s.registers[0][11]>>31;s.registers[0][11]=s.registers[0][11]<<16;zn(&s,s.registers[0][11]);
   s.pc=0xf03e26u;break;
  case 0xf03e26u: /* sub     r14,r11 */
   s.registers[0][11]=sub(&s,s.registers[0][11],s.registers[0][14]);
   s.pc=0xf03e28u;break;
  case 0xf03e28u: /* neg     r20 */
   s.registers[0][20]=sub(&s,0,s.registers[0][20]);
   s.pc=0xf03e2au;break;
  case 0xf03e2au: /* move    r11,r14 */
   s.registers[0][14]=s.registers[0][11];
   s.pc=0xf03e2cu;break;
  case 0xf03e2cu: /* move    r15,r7 */
   s.registers[0][7]=s.registers[0][15];
   s.pc=0xf03e2eu;break;
  case 0xf03e2eu: /* move    r14,r0 */
   s.registers[0][0]=s.registers[0][14];
   s.pc=0xf03e30u;break;
  case 0xf03e30u: /* and     r22,r7 */
   s.registers[0][7]&=s.registers[0][22];
   zn(&s,s.registers[0][7]);
   s.pc=0xf03e32u;break;
  case 0xf03e32u: /* and     r21,r14 */
   s.registers[0][14]&=s.registers[0][21];
   zn(&s,s.registers[0][14]);
   s.pc=0xf03e34u;break;
  case 0xf03e34u: /* shrq    $10,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=s.registers[0][0]>>16;zn(&s,s.registers[0][0]);
   s.pc=0xf03e36u;break;
  case 0xf03e36u: /* shlq    $10,r15 */
   s.c=s.registers[0][15]>>31;s.registers[0][15]=s.registers[0][15]<<16;zn(&s,s.registers[0][15]);
   s.pc=0xf03e38u;break;
  case 0xf03e38u: /* or      r0,r7 */
   s.registers[0][7]|=s.registers[0][0];
   zn(&s,s.registers[0][7]);
   s.pc=0xf03e3au;break;
  case 0xf03e3au: /* or      r14,r15 */
   s.registers[0][15]|=s.registers[0][14];
   zn(&s,s.registers[0][15]);
   s.pc=0xf03e3cu;break;
  case 0xf03e3cu: /* move    r20,r8 */
   s.registers[0][8]=s.registers[0][20];
   s.pc=0xf03e3eu;break;
  case 0xf03e3eu: /* move    r20,r9 */
   s.registers[0][9]=s.registers[0][20];
   s.pc=0xf03e40u;break;
  case 0xf03e40u: /* shrq    $10,r8 */
   s.c=s.registers[0][8]&1u;s.registers[0][8]=s.registers[0][8]>>16;zn(&s,s.registers[0][8]);
   s.pc=0xf03e42u;break;
  case 0xf03e42u: /* and     r21,r9 */
   s.registers[0][9]&=s.registers[0][21];
   zn(&s,s.registers[0][9]);
   s.pc=0xf03e44u;break;
  case 0xf03e44u: /* cmpq    $0,r13 */
   (void)sub(&s,s.registers[0][13],0x0u);
   s.pc=0xf03e46u;break;
  case 0xf03e46u: /* jr      nn,00F03E4C */
   if(condition(&s,20)){pending=1;target=0xf03e4cu;}
   s.pc=0xf03e48u;break;
  case 0xf03e48u: /* nop */
   s.pc=0xf03e4au;break;
  case 0xf03e4au: /* neg     r20 */
   s.registers[0][20]=sub(&s,0,s.registers[0][20]);
   s.pc=0xf03e4cu;break;
  case 0xf03e4cu: /* move    r20,r0 */
   s.registers[0][0]=s.registers[0][20];
   s.pc=0xf03e4eu;break;
  case 0xf03e4eu: /* move    r20,r10 */
   s.registers[0][10]=s.registers[0][20];
   s.pc=0xf03e50u;break;
  case 0xf03e50u: /* and     r21,r0 */
   s.registers[0][0]&=s.registers[0][21];
   zn(&s,s.registers[0][0]);
   s.pc=0xf03e52u;break;
  case 0xf03e52u: /* sharq   $10,r10 */
   s.c=s.registers[0][10]&1u;s.registers[0][10]=sar(s.registers[0][10],16);zn(&s,s.registers[0][10]);
   s.pc=0xf03e54u;break;
  case 0xf03e54u: /* mult    r16,r0 */
   s.registers[0][0]=(s.registers[0][0]&0xffffu)*(s.registers[0][16]&0xffffu);
   zn(&s,s.registers[0][0]);
   s.pc=0xf03e56u;break;
  case 0xf03e56u: /* imult   r16,r10 */
   s.registers[0][10]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][10])*(int32_t)sx16(s.registers[0][16]));
   zn(&s,s.registers[0][10]);
   s.pc=0xf03e58u;break;
  case 0xf03e58u: /* shlq    $10,r10 */
   s.c=s.registers[0][10]>>31;s.registers[0][10]=s.registers[0][10]<<16;zn(&s,s.registers[0][10]);
   s.pc=0xf03e5au;break;
  case 0xf03e5au: /* add     r0,r10 */
   s.registers[0][10]=add(&s,s.registers[0][10],s.registers[0][0]);
   s.pc=0xf03e5cu;break;
  case 0xf03e5cu: /* cmpq    $0,r13 */
   (void)sub(&s,s.registers[0][13],0x0u);
   s.pc=0xf03e5eu;break;
  case 0xf03e5eu: /* jr      nn,00F03E64 */
   if(condition(&s,20)){pending=1;target=0xf03e64u;}
   s.pc=0xf03e60u;break;
  case 0xf03e60u: /* neg     r10 */
   s.registers[0][10]=sub(&s,0,s.registers[0][10]);
   s.pc=0xf03e62u;break;
  case 0xf03e62u: /* neg     r10 */
   s.registers[0][10]=sub(&s,0,s.registers[0][10]);
   s.pc=0xf03e64u;break;
  case 0xf03e64u: /* move    r20,r11 */
   s.registers[0][11]=s.registers[0][20];
   s.pc=0xf03e66u;break;
  case 0xf03e66u: /* move    r10,r0 */
   s.registers[0][0]=s.registers[0][10];
   s.pc=0xf03e68u;break;
  case 0xf03e68u: /* shlq    $10,r11 */
   s.c=s.registers[0][11]>>31;s.registers[0][11]=s.registers[0][11]<<16;zn(&s,s.registers[0][11]);
   s.pc=0xf03e6au;break;
  case 0xf03e6au: /* and     r22,r20 */
   s.registers[0][20]&=s.registers[0][22];
   zn(&s,s.registers[0][20]);
   s.pc=0xf03e6cu;break;
  case 0xf03e6cu: /* and     r21,r0 */
   s.registers[0][0]&=s.registers[0][21];
   zn(&s,s.registers[0][0]);
   s.pc=0xf03e6eu;break;
  case 0xf03e6eu: /* shrq    $10,r10 */
   s.c=s.registers[0][10]&1u;s.registers[0][10]=s.registers[0][10]>>16;zn(&s,s.registers[0][10]);
   s.pc=0xf03e70u;break;
  case 0xf03e70u: /* or      r0,r11 */
   s.registers[0][11]|=s.registers[0][0];
   zn(&s,s.registers[0][11]);
   s.pc=0xf03e72u;break;
  case 0xf03e72u: /* or      r20,r10 */
   s.registers[0][10]|=s.registers[0][20];
   zn(&s,s.registers[0][10]);
   s.pc=0xf03e74u;break;
  case 0xf03e74u: /* move    r16,r12 */
   s.registers[0][12]=s.registers[0][16];
   s.pc=0xf03e76u;break;
  case 0xf03e76u: /* neg     r12 */
   s.registers[0][12]=sub(&s,0,s.registers[0][12]);
   s.pc=0xf03e78u;break;
  case 0xf03e78u: /* and     r21,r12 */
   s.registers[0][12]&=s.registers[0][21];
   zn(&s,s.registers[0][12]);
   s.pc=0xf03e7au;break;
  case 0xf03e7au: /* bset    $10,r12 */
   s.registers[0][12]|=(1u<<16);
   zn(&s,s.registers[0][12]);
   s.pc=0xf03e7cu;break;
  case 0xf03e7cu: /* and     r21,r23 */
   s.registers[0][23]&=s.registers[0][21];
   zn(&s,s.registers[0][23]);
   s.pc=0xf03e7eu;break;
  case 0xf03e7eu: /* shlq    $10,r24 */
   s.c=s.registers[0][24]>>31;s.registers[0][24]=s.registers[0][24]<<16;zn(&s,s.registers[0][24]);
   s.pc=0xf03e80u;break;
  case 0xf03e80u: /* or      r23,r24 */
   s.registers[0][24]|=s.registers[0][23];
   zn(&s,s.registers[0][24]);
   s.pc=0xf03e82u;break;
  case 0xf03e82u: /* shlq    $10,r17 */
   s.c=s.registers[0][17]>>31;s.registers[0][17]=s.registers[0][17]<<16;zn(&s,s.registers[0][17]);
   s.pc=0xf03e84u;break;
  case 0xf03e84u: /* or      r17,r16 */
   s.registers[0][16]|=s.registers[0][17];
   zn(&s,s.registers[0][16]);
   s.pc=0xf03e86u;break;
  case 0xf03e86u: /* load    (r3),r0 */
   CHECK(rd32(bus,&s,s.registers[0][3]&~3u,&v));s.registers[0][0]=v;
   s.pc=0xf03e88u;break;
  case 0xf03e88u: /* btst    $0,r0 */
   s.z=((~s.registers[0][0])>>0)&1u;
   s.pc=0xf03e8au;break;
  case 0xf03e8au: /* jr      z,00F03E86 */
   if(condition(&s,2)){pending=1;target=0xf03e86u;}
   s.pc=0xf03e8cu;break;
  case 0xf03e8cu: /* moveq   0,r0 */
   s.registers[0][0]=0u;
   s.pc=0xf03e8eu;break;
  case 0xf03e8eu: /* store   r26,(r1) */
   CHECK(wr32(bus,&s,local(s.registers[0][1])?(s.registers[0][1]&~3u):s.registers[0][1],s.registers[0][26]));
   s.pc=0xf03e90u;break;
  case 0xf03e90u: /* store   r5,(r2) */
   CHECK(wr32(bus,&s,local(s.registers[0][2])?(s.registers[0][2]&~3u):s.registers[0][2],s.registers[0][5]));
   s.pc=0xf03e92u;break;
  case 0xf03e92u: /* addq    $4,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],4u);
   s.pc=0xf03e94u;break;
  case 0xf03e94u: /* addq    $8,r2 */
   s.registers[0][2]=add(&s,s.registers[0][2],8u);
   s.pc=0xf03e96u;break;
  case 0xf03e96u: /* store   r19,(r1) */
   CHECK(wr32(bus,&s,local(s.registers[0][1])?(s.registers[0][1]&~3u):s.registers[0][1],s.registers[0][19]));
   s.pc=0xf03e98u;break;
  case 0xf03e98u: /* store   r24,(r2) */
   CHECK(wr32(bus,&s,local(s.registers[0][2])?(s.registers[0][2]&~3u):s.registers[0][2],s.registers[0][24]));
   s.pc=0xf03e9au;break;
  case 0xf03e9au: /* addq    $8,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],8u);
   s.pc=0xf03e9cu;break;
  case 0xf03e9cu: /* addq    $4,r2 */
   s.registers[0][2]=add(&s,s.registers[0][2],4u);
   s.pc=0xf03e9eu;break;
  case 0xf03e9eu: /* store   r7,(r1) */
   CHECK(wr32(bus,&s,local(s.registers[0][1])?(s.registers[0][1]&~3u):s.registers[0][1],s.registers[0][7]));
   s.pc=0xf03ea0u;break;
  case 0xf03ea0u: /* store   r12,(r2) */
   CHECK(wr32(bus,&s,local(s.registers[0][2])?(s.registers[0][2]&~3u):s.registers[0][2],s.registers[0][12]));
   s.pc=0xf03ea2u;break;
  case 0xf03ea2u: /* addq    $c,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],12u);
   s.pc=0xf03ea4u;break;
  case 0xf03ea4u: /* store   r0,(r4) */
   CHECK(wr32(bus,&s,local(s.registers[0][4])?(s.registers[0][4]&~3u):s.registers[0][4],s.registers[0][0]));
   s.pc=0xf03ea6u;break;
  case 0xf03ea6u: /* store   r15,(r1) */
   CHECK(wr32(bus,&s,local(s.registers[0][1])?(s.registers[0][1]&~3u):s.registers[0][1],s.registers[0][15]));
   s.pc=0xf03ea8u;break;
  case 0xf03ea8u: /* addq    $4,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],4u);
   s.pc=0xf03eaau;break;
  case 0xf03eaau: /* addq    $4,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],4u);
   s.pc=0xf03eacu;break;
  case 0xf03eacu: /* store   r0,(r4) */
   CHECK(wr32(bus,&s,local(s.registers[0][4])?(s.registers[0][4]&~3u):s.registers[0][4],s.registers[0][0]));
   s.pc=0xf03eaeu;break;
  case 0xf03eaeu: /* store   r8,(r1) */
   CHECK(wr32(bus,&s,local(s.registers[0][1])?(s.registers[0][1]&~3u):s.registers[0][1],s.registers[0][8]));
   s.pc=0xf03eb0u;break;
  case 0xf03eb0u: /* addq    $4,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],4u);
   s.pc=0xf03eb2u;break;
  case 0xf03eb2u: /* addq    $4,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],4u);
   s.pc=0xf03eb4u;break;
  case 0xf03eb4u: /* store   r25,(r4) */
   CHECK(wr32(bus,&s,local(s.registers[0][4])?(s.registers[0][4]&~3u):s.registers[0][4],s.registers[0][25]));
   s.pc=0xf03eb6u;break;
  case 0xf03eb6u: /* store   r9,(r1) */
   CHECK(wr32(bus,&s,local(s.registers[0][1])?(s.registers[0][1]&~3u):s.registers[0][1],s.registers[0][9]));
   s.pc=0xf03eb8u;break;
  case 0xf03eb8u: /* addq    $4,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],4u);
   s.pc=0xf03ebau;break;
  case 0xf03ebau: /* subq    $c,r1 */
   s.registers[0][1]=sub(&s,s.registers[0][1],12u);
   s.pc=0xf03ebcu;break;
  case 0xf03ebcu: /* store   r16,(r3) */
   CHECK(wr32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],s.registers[0][16]));
   s.pc=0xf03ebeu;break;
  case 0xf03ebeu: /* store   r11,(r1) */
   CHECK(wr32(bus,&s,local(s.registers[0][1])?(s.registers[0][1]&~3u):s.registers[0][1],s.registers[0][11]));
   s.pc=0xf03ec0u;break;
  case 0xf03ec0u: /* subq    $4,r3 */
   s.registers[0][3]=sub(&s,s.registers[0][3],4u);
   s.pc=0xf03ec2u;break;
  case 0xf03ec2u: /* subq    $4,r1 */
   s.registers[0][1]=sub(&s,s.registers[0][1],4u);
   s.pc=0xf03ec4u;break;
  case 0xf03ec4u: /* store   r10,(r1) */
   CHECK(wr32(bus,&s,local(s.registers[0][1])?(s.registers[0][1]&~3u):s.registers[0][1],s.registers[0][10]));
   s.pc=0xf03ec6u;break;
  case 0xf03ec6u: /* jump    (r27) */
   if(condition(&s,0)){pending=1;target=s.registers[0][27];}
   s.pc=0xf03ec8u;break;
  case 0xf03ec8u: /* store   r6,(r3) */
   CHECK(wr32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],s.registers[0][6]));
   s.pc=0xf03ecau;break;
default:return BIWN_GPU_RESIDENT_BAD_PC;
}if(delayed){if(pending)return BIWN_GPU_RESIDENT_BAD_DELAY;s.pc=resume;}if(s.pc==0xf031beu){*state=s;return BIWN_GPU_RESIDENT_OK;}}return BIWN_GPU_RESIDENT_WORK_LIMIT;}
