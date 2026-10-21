/* Generated from the pinned GPU4720 command payload by
 * scripts/generate_biwn_gpu_command4720.py. Analyst static recompilation,
 * not recovered original source. Integer primitive behavior is checked
 * against the pinned Virtual Jaguar core; no core runs on the C side. */
#include "biwn_gpu_command4720.h"
#include <string.h>
static uint32_t sx16(uint32_t v){return(v&0x7fffu)-(v&0x8000u);}
static uint32_t sar(uint32_t v,unsigned n){return n>=32?((v&0x80000000u)?0xffffffffu:0):(v>>n)|((v&0x80000000u)?(0xffffffffu<<(32-n)):0);}
static void zn(struct biwn_gpu_command4720_state *s,uint32_t v){s->z=v==0;s->n=v>>31;}
static uint32_t add(struct biwn_gpu_command4720_state *s,uint32_t a,uint32_t b){uint32_t v=a+b;s->c=b>~a;zn(s,v);return v;}
static uint32_t sub(struct biwn_gpu_command4720_state *s,uint32_t a,uint32_t b){uint32_t v=a-b;s->c=b>a;zn(s,v);return v;}
static int condition(struct biwn_gpu_command4720_state *s,unsigned code){unsigned flags=s->z|(s->c<<1)|(s->n<<2);return !((code&1u)&&(flags&1u))&&!((code&2u)&&!(flags&1u))&&!((code&4u)&&(flags&(2u<<(code>>4))))&&!((code&8u)&&!(flags&(2u<<(code>>4))));}
static uint32_t be32(const uint8_t *p){return((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
static void put32(uint8_t *p,uint32_t v){p[0]=(uint8_t)(v>>24);p[1]=(uint8_t)(v>>16);p[2]=(uint8_t)(v>>8);p[3]=(uint8_t)v;}
static int local(uint32_t a){return a>=0xf03000u&&a<=0xf03ffcu;}
static int rd32(struct biwn_gpu_command4720_bus *bus,struct biwn_gpu_command4720_state *s,uint32_t a,uint32_t *v){if(local(a)){*v=be32(s->local_RAM+a-0xf03000u);return 0;}if(a==0xf02104u){*v=s->matrix_control;return 0;}if(a==0xf02108u){*v=s->matrix_pointer;return 0;}return bus->read32(bus->context,a,v)?2:0;}
static int rd16(struct biwn_gpu_command4720_bus *bus,struct biwn_gpu_command4720_state *s,uint32_t a,uint32_t *v){uint16_t h;if(a>=0xf03000u&&a<=0xf03ffeu){unsigned p=a-0xf03000u;*v=((uint32_t)s->local_RAM[p]<<8)|s->local_RAM[p+1];return 0;}if(bus->read16(bus->context,a,&h))return 2;*v=h;return 0;}
static int loadw(struct biwn_gpu_command4720_bus *bus,struct biwn_gpu_command4720_state *s,uint32_t a,uint32_t *v){if(a>=0xf03000u&&a<=0xf03fffu)return rd32(bus,s,a&~3u,v);return rd16(bus,s,a,v);}
static int wr32(struct biwn_gpu_command4720_bus *bus,struct biwn_gpu_command4720_state *s,uint32_t a,uint32_t v){if(local(a)){put32(s->local_RAM+a-0xf03000u,v);return 0;}if(a==0xf02104u){s->matrix_control=v;return 0;}if(a==0xf02108u){s->matrix_pointer=v&~3u;return 0;}return bus->write32(bus->context,a,v)?2:0;}
static int wr16(struct biwn_gpu_command4720_bus *bus,struct biwn_gpu_command4720_state *s,uint32_t a,uint32_t v){if(a>=0xf03000u&&a<=0xf03fffu)return wr32(bus,s,a&~1u,v&0xffffu);return bus->write16(bus->context,a,(uint16_t)v)?2:0;}
#define CHECK(e) do{int status=(e);if(status)return(enum biwn_gpu_command4720_status)status;}while(0)
enum biwn_gpu_command4720_status biwn_gpu_command4720_run(struct biwn_gpu_command4720_bus *bus,struct biwn_gpu_command4720_state *state,uint32_t budget){struct biwn_gpu_command4720_state s;uint32_t v,target=0;unsigned pending=0;if(!bus||!state||!budget||!bus->read16||!bus->read32||!bus->write16||!bus->write32||state->active_bank||state->z>1||state->c>1||state->n>1)return 1;s=*state;while(budget--){unsigned delayed=pending;uint32_t resume=target;pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){
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
  case 0xf03252u: /* moveq   1,r8 */
   s.registers[0][8]=1u;
   s.pc=0xf03254u;break;
case 0xf03254u: /* load    (r3),r0 */
 CHECK(rd32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],&v));s.registers[0][0]=v;
 s.pc=0xf03256u;break;
  case 0xf03256u: /* movei   $f034ce,r26 */
   s.registers[0][26]=0xf034ceu;
   s.pc=0xf0325cu;break;
  case 0xf0325cu: /* addq    $4,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],4u);
   s.pc=0xf0325eu;break;
  case 0xf0325eu: /* shlq    $d,r8 */
   s.c=s.registers[0][8]>>31;s.registers[0][8]=s.registers[0][8]<<13;zn(&s,s.registers[0][8]);
   s.pc=0xf03260u;break;
case 0xf03260u: /* load    (r3),r4 */
 CHECK(rd32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],&v));s.registers[0][4]=v;
 s.pc=0xf03262u;break;
  case 0xf03262u: /* movei   $f034cc,r25 */
   s.registers[0][25]=0xf034ccu;
   s.pc=0xf03268u;break;
  case 0xf03268u: /* addq    $4,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],4u);
   s.pc=0xf0326au;break;
  case 0xf0326au: /* moveq   4,r23 */
   s.registers[0][23]=4u;
   s.pc=0xf0326cu;break;
case 0xf0326cu: /* load    (r3),r5 */
 CHECK(rd32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],&v));s.registers[0][5]=v;
 s.pc=0xf0326eu;break;
  case 0xf0326eu: /* movei   $f03504,r24 */
   s.registers[0][24]=0xf03504u;
   s.pc=0xf03274u;break;
  case 0xf03274u: /* addq    $4,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],4u);
   s.pc=0xf03276u;break;
case 0xf03276u: /* load    (r3),r6 */
 CHECK(rd32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],&v));s.registers[0][6]=v;
 s.pc=0xf03278u;break;
  case 0xf03278u: /* shlq    $4,r23 */
   s.c=s.registers[0][23]>>31;s.registers[0][23]=s.registers[0][23]<<4;zn(&s,s.registers[0][23]);
   s.pc=0xf0327au;break;
  case 0xf0327au: /* addq    $4,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],4u);
   s.pc=0xf0327cu;break;
case 0xf0327cu: /* load    (r3),r7 */
 CHECK(rd32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],&v));s.registers[0][7]=v;
 s.pc=0xf0327eu;break;
  case 0xf0327eu: /* loadw   (r0),r9 */
   CHECK(loadw(bus,&s,s.registers[0][0],&v));s.registers[0][9]=v;
   s.pc=0xf03280u;break;
  case 0xf03280u: /* shlq    $10,r7 */
   s.c=s.registers[0][7]>>31;s.registers[0][7]=s.registers[0][7]<<16;zn(&s,s.registers[0][7]);
   s.pc=0xf03282u;break;
  case 0xf03282u: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf03284u;break;
  case 0xf03284u: /* sharq   $10,r7 */
   s.c=s.registers[0][7]&1u;s.registers[0][7]=sar(s.registers[0][7],16);zn(&s,s.registers[0][7]);
   s.pc=0xf03286u;break;
  case 0xf03286u: /* loadw   (r0),r10 */
   CHECK(loadw(bus,&s,s.registers[0][0],&v));s.registers[0][10]=v;
   s.pc=0xf03288u;break;
  case 0xf03288u: /* shlq    $10,r9 */
   s.c=s.registers[0][9]>>31;s.registers[0][9]=s.registers[0][9]<<16;zn(&s,s.registers[0][9]);
   s.pc=0xf0328au;break;
  case 0xf0328au: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf0328cu;break;
  case 0xf0328cu: /* shlq    $10,r10 */
   s.c=s.registers[0][10]>>31;s.registers[0][10]=s.registers[0][10]<<16;zn(&s,s.registers[0][10]);
   s.pc=0xf0328eu;break;
  case 0xf0328eu: /* loadw   (r0),r11 */
   CHECK(loadw(bus,&s,s.registers[0][0],&v));s.registers[0][11]=v;
   s.pc=0xf03290u;break;
  case 0xf03290u: /* sharq   $10,r9 */
   s.c=s.registers[0][9]&1u;s.registers[0][9]=sar(s.registers[0][9],16);zn(&s,s.registers[0][9]);
   s.pc=0xf03292u;break;
  case 0xf03292u: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf03294u;break;
  case 0xf03294u: /* shlq    $10,r11 */
   s.c=s.registers[0][11]>>31;s.registers[0][11]=s.registers[0][11]<<16;zn(&s,s.registers[0][11]);
   s.pc=0xf03296u;break;
  case 0xf03296u: /* loadw   (r0),r12 */
   CHECK(loadw(bus,&s,s.registers[0][0],&v));s.registers[0][12]=v;
   s.pc=0xf03298u;break;
  case 0xf03298u: /* sharq   $10,r10 */
   s.c=s.registers[0][10]&1u;s.registers[0][10]=sar(s.registers[0][10],16);zn(&s,s.registers[0][10]);
   s.pc=0xf0329au;break;
  case 0xf0329au: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf0329cu;break;
  case 0xf0329cu: /* sharq   $10,r11 */
   s.c=s.registers[0][11]&1u;s.registers[0][11]=sar(s.registers[0][11],16);zn(&s,s.registers[0][11]);
   s.pc=0xf0329eu;break;
  case 0xf0329eu: /* loadw   (r0),r13 */
   CHECK(loadw(bus,&s,s.registers[0][0],&v));s.registers[0][13]=v;
   s.pc=0xf032a0u;break;
  case 0xf032a0u: /* shlq    $10,r12 */
   s.c=s.registers[0][12]>>31;s.registers[0][12]=s.registers[0][12]<<16;zn(&s,s.registers[0][12]);
   s.pc=0xf032a2u;break;
  case 0xf032a2u: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf032a4u;break;
  case 0xf032a4u: /* shlq    $10,r13 */
   s.c=s.registers[0][13]>>31;s.registers[0][13]=s.registers[0][13]<<16;zn(&s,s.registers[0][13]);
   s.pc=0xf032a6u;break;
  case 0xf032a6u: /* loadw   (r0),r14 */
   CHECK(loadw(bus,&s,s.registers[0][0],&v));s.registers[0][14]=v;
   s.pc=0xf032a8u;break;
  case 0xf032a8u: /* sharq   $10,r12 */
   s.c=s.registers[0][12]&1u;s.registers[0][12]=sar(s.registers[0][12],16);zn(&s,s.registers[0][12]);
   s.pc=0xf032aau;break;
  case 0xf032aau: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf032acu;break;
  case 0xf032acu: /* shlq    $10,r14 */
   s.c=s.registers[0][14]>>31;s.registers[0][14]=s.registers[0][14]<<16;zn(&s,s.registers[0][14]);
   s.pc=0xf032aeu;break;
  case 0xf032aeu: /* loadw   (r0),r15 */
   CHECK(loadw(bus,&s,s.registers[0][0],&v));s.registers[0][15]=v;
   s.pc=0xf032b0u;break;
  case 0xf032b0u: /* sharq   $10,r13 */
   s.c=s.registers[0][13]&1u;s.registers[0][13]=sar(s.registers[0][13],16);zn(&s,s.registers[0][13]);
   s.pc=0xf032b2u;break;
  case 0xf032b2u: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf032b4u;break;
  case 0xf032b4u: /* sharq   $10,r14 */
   s.c=s.registers[0][14]&1u;s.registers[0][14]=sar(s.registers[0][14],16);zn(&s,s.registers[0][14]);
   s.pc=0xf032b6u;break;
  case 0xf032b6u: /* loadw   (r0),r16 */
   CHECK(loadw(bus,&s,s.registers[0][0],&v));s.registers[0][16]=v;
   s.pc=0xf032b8u;break;
  case 0xf032b8u: /* shlq    $10,r15 */
   s.c=s.registers[0][15]>>31;s.registers[0][15]=s.registers[0][15]<<16;zn(&s,s.registers[0][15]);
   s.pc=0xf032bau;break;
  case 0xf032bau: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf032bcu;break;
  case 0xf032bcu: /* shlq    $10,r16 */
   s.c=s.registers[0][16]>>31;s.registers[0][16]=s.registers[0][16]<<16;zn(&s,s.registers[0][16]);
   s.pc=0xf032beu;break;
  case 0xf032beu: /* loadw   (r0),r17 */
   CHECK(loadw(bus,&s,s.registers[0][0],&v));s.registers[0][17]=v;
   s.pc=0xf032c0u;break;
  case 0xf032c0u: /* sharq   $10,r15 */
   s.c=s.registers[0][15]&1u;s.registers[0][15]=sar(s.registers[0][15],16);zn(&s,s.registers[0][15]);
   s.pc=0xf032c2u;break;
  case 0xf032c2u: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf032c4u;break;
  case 0xf032c4u: /* shlq    $10,r17 */
   s.c=s.registers[0][17]>>31;s.registers[0][17]=s.registers[0][17]<<16;zn(&s,s.registers[0][17]);
   s.pc=0xf032c6u;break;
  case 0xf032c6u: /* loadw   (r0),r18 */
   CHECK(loadw(bus,&s,s.registers[0][0],&v));s.registers[0][18]=v;
   s.pc=0xf032c8u;break;
  case 0xf032c8u: /* sharq   $10,r16 */
   s.c=s.registers[0][16]&1u;s.registers[0][16]=sar(s.registers[0][16],16);zn(&s,s.registers[0][16]);
   s.pc=0xf032cau;break;
  case 0xf032cau: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf032ccu;break;
  case 0xf032ccu: /* sharq   $10,r17 */
   s.c=s.registers[0][17]&1u;s.registers[0][17]=sar(s.registers[0][17],16);zn(&s,s.registers[0][17]);
   s.pc=0xf032ceu;break;
  case 0xf032ceu: /* loadw   (r0),r19 */
   CHECK(loadw(bus,&s,s.registers[0][0],&v));s.registers[0][19]=v;
   s.pc=0xf032d0u;break;
  case 0xf032d0u: /* shlq    $10,r18 */
   s.c=s.registers[0][18]>>31;s.registers[0][18]=s.registers[0][18]<<16;zn(&s,s.registers[0][18]);
   s.pc=0xf032d2u;break;
  case 0xf032d2u: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf032d4u;break;
  case 0xf032d4u: /* shlq    $10,r19 */
   s.c=s.registers[0][19]>>31;s.registers[0][19]=s.registers[0][19]<<16;zn(&s,s.registers[0][19]);
   s.pc=0xf032d6u;break;
  case 0xf032d6u: /* loadw   (r0),r20 */
   CHECK(loadw(bus,&s,s.registers[0][0],&v));s.registers[0][20]=v;
   s.pc=0xf032d8u;break;
  case 0xf032d8u: /* sharq   $10,r18 */
   s.c=s.registers[0][18]&1u;s.registers[0][18]=sar(s.registers[0][18],16);zn(&s,s.registers[0][18]);
   s.pc=0xf032dau;break;
  case 0xf032dau: /* shlq    $10,r20 */
   s.c=s.registers[0][20]>>31;s.registers[0][20]=s.registers[0][20]<<16;zn(&s,s.registers[0][20]);
   s.pc=0xf032dcu;break;
  case 0xf032dcu: /* sharq   $10,r19 */
   s.c=s.registers[0][19]&1u;s.registers[0][19]=sar(s.registers[0][19],16);zn(&s,s.registers[0][19]);
   s.pc=0xf032deu;break;
  case 0xf032deu: /* sharq   $10,r20 */
   s.c=s.registers[0][20]&1u;s.registers[0][20]=sar(s.registers[0][20],16);zn(&s,s.registers[0][20]);
   s.pc=0xf032e0u;break;
  case 0xf032e0u: /* movei   $f0335c,r2 */
   s.registers[0][2]=0xf0335cu;
   s.pc=0xf032e6u;break;
  case 0xf032e6u: /* cmpq    $0,r5 */
   (void)sub(&s,s.registers[0][5],0x0u);
   s.pc=0xf032e8u;break;
  case 0xf032e8u: /* jump    z,(r2) */
   if(condition(&s,2)){pending=1;target=s.registers[0][2];}
   s.pc=0xf032eau;break;
  case 0xf032eau: /* move    r5,r0 */
   s.registers[0][0]=s.registers[0][5];
   s.pc=0xf032ecu;break;
  case 0xf032ecu: /* move    pc,r27 */
   s.registers[0][27]=0xf032ecu;
   s.pc=0xf032eeu;break;
  case 0xf032eeu: /* jump    (r26) */
   if(condition(&s,0)){pending=1;target=s.registers[0][26];}
   s.pc=0xf032f0u;break;
  case 0xf032f0u: /* addq    $6,r27 */
   s.registers[0][27]=add(&s,s.registers[0][27],6u);
   s.pc=0xf032f2u;break;
  case 0xf032f2u: /* move    r0,r21 */
   s.registers[0][21]=s.registers[0][0];
   s.pc=0xf032f4u;break;
  case 0xf032f4u: /* move    r5,r0 */
   s.registers[0][0]=s.registers[0][5];
   s.pc=0xf032f6u;break;
  case 0xf032f6u: /* move    pc,r27 */
   s.registers[0][27]=0xf032f6u;
   s.pc=0xf032f8u;break;
  case 0xf032f8u: /* jump    (r25) */
   if(condition(&s,0)){pending=1;target=s.registers[0][25];}
   s.pc=0xf032fau;break;
  case 0xf032fau: /* addq    $6,r27 */
   s.registers[0][27]=add(&s,s.registers[0][27],6u);
   s.pc=0xf032fcu;break;
  case 0xf032fcu: /* move    r0,r22 */
   s.registers[0][22]=s.registers[0][0];
   s.pc=0xf032feu;break;
  case 0xf032feu: /* move    r21,r1 */
   s.registers[0][1]=s.registers[0][21];
   s.pc=0xf03300u;break;
  case 0xf03300u: /* imult   r15,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][15]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf03302u;break;
  case 0xf03302u: /* imult   r9,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][9]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf03304u;break;
  case 0xf03304u: /* sub     r1,r0 */
   s.registers[0][0]=sub(&s,s.registers[0][0],s.registers[0][1]);
   s.pc=0xf03306u;break;
  case 0xf03306u: /* move    r21,r1 */
   s.registers[0][1]=s.registers[0][21];
   s.pc=0xf03308u;break;
  case 0xf03308u: /* add     r8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][8]);
   s.pc=0xf0330au;break;
  case 0xf0330au: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf0330cu;break;
  case 0xf0330cu: /* imult   r15,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][15]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf0330eu;break;
  case 0xf0330eu: /* move    r0,r15 */
   s.registers[0][15]=s.registers[0][0];
   s.pc=0xf03310u;break;
  case 0xf03310u: /* move    r22,r0 */
   s.registers[0][0]=s.registers[0][22];
   s.pc=0xf03312u;break;
  case 0xf03312u: /* imult   r9,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][9]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf03314u;break;
  case 0xf03314u: /* add     r1,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][1]);
   s.pc=0xf03316u;break;
  case 0xf03316u: /* add     r8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][8]);
   s.pc=0xf03318u;break;
  case 0xf03318u: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf0331au;break;
  case 0xf0331au: /* move    r0,r9 */
   s.registers[0][9]=s.registers[0][0];
   s.pc=0xf0331cu;break;
  case 0xf0331cu: /* move    r22,r0 */
   s.registers[0][0]=s.registers[0][22];
   s.pc=0xf0331eu;break;
  case 0xf0331eu: /* move    r21,r1 */
   s.registers[0][1]=s.registers[0][21];
   s.pc=0xf03320u;break;
  case 0xf03320u: /* imult   r16,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][16]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf03322u;break;
  case 0xf03322u: /* imult   r10,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][10]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf03324u;break;
  case 0xf03324u: /* sub     r1,r0 */
   s.registers[0][0]=sub(&s,s.registers[0][0],s.registers[0][1]);
   s.pc=0xf03326u;break;
  case 0xf03326u: /* move    r21,r1 */
   s.registers[0][1]=s.registers[0][21];
   s.pc=0xf03328u;break;
  case 0xf03328u: /* add     r8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][8]);
   s.pc=0xf0332au;break;
  case 0xf0332au: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf0332cu;break;
  case 0xf0332cu: /* imult   r16,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][16]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf0332eu;break;
  case 0xf0332eu: /* move    r0,r16 */
   s.registers[0][16]=s.registers[0][0];
   s.pc=0xf03330u;break;
  case 0xf03330u: /* move    r22,r0 */
   s.registers[0][0]=s.registers[0][22];
   s.pc=0xf03332u;break;
  case 0xf03332u: /* imult   r10,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][10]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf03334u;break;
  case 0xf03334u: /* add     r1,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][1]);
   s.pc=0xf03336u;break;
  case 0xf03336u: /* add     r8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][8]);
   s.pc=0xf03338u;break;
  case 0xf03338u: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf0333au;break;
  case 0xf0333au: /* move    r0,r10 */
   s.registers[0][10]=s.registers[0][0];
   s.pc=0xf0333cu;break;
  case 0xf0333cu: /* move    r22,r0 */
   s.registers[0][0]=s.registers[0][22];
   s.pc=0xf0333eu;break;
  case 0xf0333eu: /* move    r21,r1 */
   s.registers[0][1]=s.registers[0][21];
   s.pc=0xf03340u;break;
  case 0xf03340u: /* imult   r17,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][17]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf03342u;break;
  case 0xf03342u: /* imult   r11,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][11]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf03344u;break;
  case 0xf03344u: /* sub     r1,r0 */
   s.registers[0][0]=sub(&s,s.registers[0][0],s.registers[0][1]);
   s.pc=0xf03346u;break;
  case 0xf03346u: /* move    r21,r1 */
   s.registers[0][1]=s.registers[0][21];
   s.pc=0xf03348u;break;
  case 0xf03348u: /* add     r8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][8]);
   s.pc=0xf0334au;break;
  case 0xf0334au: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf0334cu;break;
  case 0xf0334cu: /* imult   r17,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][17]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf0334eu;break;
  case 0xf0334eu: /* move    r0,r17 */
   s.registers[0][17]=s.registers[0][0];
   s.pc=0xf03350u;break;
  case 0xf03350u: /* move    r22,r0 */
   s.registers[0][0]=s.registers[0][22];
   s.pc=0xf03352u;break;
  case 0xf03352u: /* imult   r11,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][11]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf03354u;break;
  case 0xf03354u: /* add     r1,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][1]);
   s.pc=0xf03356u;break;
  case 0xf03356u: /* add     r8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][8]);
   s.pc=0xf03358u;break;
  case 0xf03358u: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf0335au;break;
  case 0xf0335au: /* move    r0,r11 */
   s.registers[0][11]=s.registers[0][0];
   s.pc=0xf0335cu;break;
  case 0xf0335cu: /* movei   $f033d8,r2 */
   s.registers[0][2]=0xf033d8u;
   s.pc=0xf03362u;break;
  case 0xf03362u: /* cmpq    $0,r4 */
   (void)sub(&s,s.registers[0][4],0x0u);
   s.pc=0xf03364u;break;
  case 0xf03364u: /* jump    z,(r2) */
   if(condition(&s,2)){pending=1;target=s.registers[0][2];}
   s.pc=0xf03366u;break;
  case 0xf03366u: /* move    r4,r0 */
   s.registers[0][0]=s.registers[0][4];
   s.pc=0xf03368u;break;
  case 0xf03368u: /* move    pc,r27 */
   s.registers[0][27]=0xf03368u;
   s.pc=0xf0336au;break;
  case 0xf0336au: /* jump    (r26) */
   if(condition(&s,0)){pending=1;target=s.registers[0][26];}
   s.pc=0xf0336cu;break;
  case 0xf0336cu: /* addq    $6,r27 */
   s.registers[0][27]=add(&s,s.registers[0][27],6u);
   s.pc=0xf0336eu;break;
  case 0xf0336eu: /* move    r0,r21 */
   s.registers[0][21]=s.registers[0][0];
   s.pc=0xf03370u;break;
  case 0xf03370u: /* move    r4,r0 */
   s.registers[0][0]=s.registers[0][4];
   s.pc=0xf03372u;break;
  case 0xf03372u: /* move    pc,r27 */
   s.registers[0][27]=0xf03372u;
   s.pc=0xf03374u;break;
  case 0xf03374u: /* jump    (r25) */
   if(condition(&s,0)){pending=1;target=s.registers[0][25];}
   s.pc=0xf03376u;break;
  case 0xf03376u: /* addq    $6,r27 */
   s.registers[0][27]=add(&s,s.registers[0][27],6u);
   s.pc=0xf03378u;break;
  case 0xf03378u: /* move    r0,r22 */
   s.registers[0][22]=s.registers[0][0];
   s.pc=0xf0337au;break;
  case 0xf0337au: /* move    r21,r1 */
   s.registers[0][1]=s.registers[0][21];
   s.pc=0xf0337cu;break;
  case 0xf0337cu: /* imult   r12,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][12]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf0337eu;break;
  case 0xf0337eu: /* imult   r15,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][15]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf03380u;break;
  case 0xf03380u: /* sub     r1,r0 */
   s.registers[0][0]=sub(&s,s.registers[0][0],s.registers[0][1]);
   s.pc=0xf03382u;break;
  case 0xf03382u: /* move    r21,r1 */
   s.registers[0][1]=s.registers[0][21];
   s.pc=0xf03384u;break;
  case 0xf03384u: /* add     r8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][8]);
   s.pc=0xf03386u;break;
  case 0xf03386u: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf03388u;break;
  case 0xf03388u: /* imult   r12,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][12]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf0338au;break;
  case 0xf0338au: /* move    r0,r12 */
   s.registers[0][12]=s.registers[0][0];
   s.pc=0xf0338cu;break;
  case 0xf0338cu: /* move    r22,r0 */
   s.registers[0][0]=s.registers[0][22];
   s.pc=0xf0338eu;break;
  case 0xf0338eu: /* imult   r15,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][15]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf03390u;break;
  case 0xf03390u: /* add     r1,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][1]);
   s.pc=0xf03392u;break;
  case 0xf03392u: /* add     r8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][8]);
   s.pc=0xf03394u;break;
  case 0xf03394u: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf03396u;break;
  case 0xf03396u: /* move    r0,r15 */
   s.registers[0][15]=s.registers[0][0];
   s.pc=0xf03398u;break;
  case 0xf03398u: /* move    r22,r0 */
   s.registers[0][0]=s.registers[0][22];
   s.pc=0xf0339au;break;
  case 0xf0339au: /* move    r21,r1 */
   s.registers[0][1]=s.registers[0][21];
   s.pc=0xf0339cu;break;
  case 0xf0339cu: /* imult   r13,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][13]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf0339eu;break;
  case 0xf0339eu: /* imult   r16,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][16]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf033a0u;break;
  case 0xf033a0u: /* sub     r1,r0 */
   s.registers[0][0]=sub(&s,s.registers[0][0],s.registers[0][1]);
   s.pc=0xf033a2u;break;
  case 0xf033a2u: /* move    r21,r1 */
   s.registers[0][1]=s.registers[0][21];
   s.pc=0xf033a4u;break;
  case 0xf033a4u: /* add     r8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][8]);
   s.pc=0xf033a6u;break;
  case 0xf033a6u: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf033a8u;break;
  case 0xf033a8u: /* imult   r13,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][13]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf033aau;break;
  case 0xf033aau: /* move    r0,r13 */
   s.registers[0][13]=s.registers[0][0];
   s.pc=0xf033acu;break;
  case 0xf033acu: /* move    r22,r0 */
   s.registers[0][0]=s.registers[0][22];
   s.pc=0xf033aeu;break;
  case 0xf033aeu: /* imult   r16,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][16]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf033b0u;break;
  case 0xf033b0u: /* add     r1,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][1]);
   s.pc=0xf033b2u;break;
  case 0xf033b2u: /* add     r8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][8]);
   s.pc=0xf033b4u;break;
  case 0xf033b4u: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf033b6u;break;
  case 0xf033b6u: /* move    r0,r16 */
   s.registers[0][16]=s.registers[0][0];
   s.pc=0xf033b8u;break;
  case 0xf033b8u: /* move    r22,r0 */
   s.registers[0][0]=s.registers[0][22];
   s.pc=0xf033bau;break;
  case 0xf033bau: /* move    r21,r1 */
   s.registers[0][1]=s.registers[0][21];
   s.pc=0xf033bcu;break;
  case 0xf033bcu: /* imult   r14,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][14]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf033beu;break;
  case 0xf033beu: /* imult   r17,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][17]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf033c0u;break;
  case 0xf033c0u: /* sub     r1,r0 */
   s.registers[0][0]=sub(&s,s.registers[0][0],s.registers[0][1]);
   s.pc=0xf033c2u;break;
  case 0xf033c2u: /* move    r21,r1 */
   s.registers[0][1]=s.registers[0][21];
   s.pc=0xf033c4u;break;
  case 0xf033c4u: /* add     r8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][8]);
   s.pc=0xf033c6u;break;
  case 0xf033c6u: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf033c8u;break;
  case 0xf033c8u: /* imult   r14,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][14]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf033cau;break;
  case 0xf033cau: /* move    r0,r14 */
   s.registers[0][14]=s.registers[0][0];
   s.pc=0xf033ccu;break;
  case 0xf033ccu: /* move    r22,r0 */
   s.registers[0][0]=s.registers[0][22];
   s.pc=0xf033ceu;break;
  case 0xf033ceu: /* imult   r17,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][17]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf033d0u;break;
  case 0xf033d0u: /* add     r1,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][1]);
   s.pc=0xf033d2u;break;
  case 0xf033d2u: /* add     r8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][8]);
   s.pc=0xf033d4u;break;
  case 0xf033d4u: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf033d6u;break;
  case 0xf033d6u: /* move    r0,r17 */
   s.registers[0][17]=s.registers[0][0];
   s.pc=0xf033d8u;break;
  case 0xf033d8u: /* movei   $f03454,r2 */
   s.registers[0][2]=0xf03454u;
   s.pc=0xf033deu;break;
  case 0xf033deu: /* cmpq    $0,r6 */
   (void)sub(&s,s.registers[0][6],0x0u);
   s.pc=0xf033e0u;break;
  case 0xf033e0u: /* jump    z,(r2) */
   if(condition(&s,2)){pending=1;target=s.registers[0][2];}
   s.pc=0xf033e2u;break;
  case 0xf033e2u: /* move    r6,r0 */
   s.registers[0][0]=s.registers[0][6];
   s.pc=0xf033e4u;break;
  case 0xf033e4u: /* move    pc,r27 */
   s.registers[0][27]=0xf033e4u;
   s.pc=0xf033e6u;break;
  case 0xf033e6u: /* jump    (r26) */
   if(condition(&s,0)){pending=1;target=s.registers[0][26];}
   s.pc=0xf033e8u;break;
  case 0xf033e8u: /* addq    $6,r27 */
   s.registers[0][27]=add(&s,s.registers[0][27],6u);
   s.pc=0xf033eau;break;
  case 0xf033eau: /* move    r0,r21 */
   s.registers[0][21]=s.registers[0][0];
   s.pc=0xf033ecu;break;
  case 0xf033ecu: /* move    r6,r0 */
   s.registers[0][0]=s.registers[0][6];
   s.pc=0xf033eeu;break;
  case 0xf033eeu: /* move    pc,r27 */
   s.registers[0][27]=0xf033eeu;
   s.pc=0xf033f0u;break;
  case 0xf033f0u: /* jump    (r25) */
   if(condition(&s,0)){pending=1;target=s.registers[0][25];}
   s.pc=0xf033f2u;break;
  case 0xf033f2u: /* addq    $6,r27 */
   s.registers[0][27]=add(&s,s.registers[0][27],6u);
   s.pc=0xf033f4u;break;
  case 0xf033f4u: /* move    r0,r22 */
   s.registers[0][22]=s.registers[0][0];
   s.pc=0xf033f6u;break;
  case 0xf033f6u: /* move    r21,r1 */
   s.registers[0][1]=s.registers[0][21];
   s.pc=0xf033f8u;break;
  case 0xf033f8u: /* imult   r9,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][9]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf033fau;break;
  case 0xf033fau: /* imult   r12,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][12]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf033fcu;break;
  case 0xf033fcu: /* sub     r1,r0 */
   s.registers[0][0]=sub(&s,s.registers[0][0],s.registers[0][1]);
   s.pc=0xf033feu;break;
  case 0xf033feu: /* move    r21,r1 */
   s.registers[0][1]=s.registers[0][21];
   s.pc=0xf03400u;break;
  case 0xf03400u: /* add     r8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][8]);
   s.pc=0xf03402u;break;
  case 0xf03402u: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf03404u;break;
  case 0xf03404u: /* imult   r9,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][9]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf03406u;break;
  case 0xf03406u: /* move    r0,r9 */
   s.registers[0][9]=s.registers[0][0];
   s.pc=0xf03408u;break;
  case 0xf03408u: /* move    r22,r0 */
   s.registers[0][0]=s.registers[0][22];
   s.pc=0xf0340au;break;
  case 0xf0340au: /* imult   r12,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][12]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf0340cu;break;
  case 0xf0340cu: /* add     r1,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][1]);
   s.pc=0xf0340eu;break;
  case 0xf0340eu: /* add     r8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][8]);
   s.pc=0xf03410u;break;
  case 0xf03410u: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf03412u;break;
  case 0xf03412u: /* move    r0,r12 */
   s.registers[0][12]=s.registers[0][0];
   s.pc=0xf03414u;break;
  case 0xf03414u: /* move    r22,r0 */
   s.registers[0][0]=s.registers[0][22];
   s.pc=0xf03416u;break;
  case 0xf03416u: /* move    r21,r1 */
   s.registers[0][1]=s.registers[0][21];
   s.pc=0xf03418u;break;
  case 0xf03418u: /* imult   r10,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][10]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf0341au;break;
  case 0xf0341au: /* imult   r13,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][13]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf0341cu;break;
  case 0xf0341cu: /* sub     r1,r0 */
   s.registers[0][0]=sub(&s,s.registers[0][0],s.registers[0][1]);
   s.pc=0xf0341eu;break;
  case 0xf0341eu: /* move    r21,r1 */
   s.registers[0][1]=s.registers[0][21];
   s.pc=0xf03420u;break;
  case 0xf03420u: /* add     r8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][8]);
   s.pc=0xf03422u;break;
  case 0xf03422u: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf03424u;break;
  case 0xf03424u: /* imult   r10,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][10]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf03426u;break;
  case 0xf03426u: /* move    r0,r10 */
   s.registers[0][10]=s.registers[0][0];
   s.pc=0xf03428u;break;
  case 0xf03428u: /* move    r22,r0 */
   s.registers[0][0]=s.registers[0][22];
   s.pc=0xf0342au;break;
  case 0xf0342au: /* imult   r13,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][13]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf0342cu;break;
  case 0xf0342cu: /* add     r1,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][1]);
   s.pc=0xf0342eu;break;
  case 0xf0342eu: /* add     r8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][8]);
   s.pc=0xf03430u;break;
  case 0xf03430u: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf03432u;break;
  case 0xf03432u: /* move    r0,r13 */
   s.registers[0][13]=s.registers[0][0];
   s.pc=0xf03434u;break;
  case 0xf03434u: /* move    r22,r0 */
   s.registers[0][0]=s.registers[0][22];
   s.pc=0xf03436u;break;
  case 0xf03436u: /* move    r21,r1 */
   s.registers[0][1]=s.registers[0][21];
   s.pc=0xf03438u;break;
  case 0xf03438u: /* imult   r11,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][11]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf0343au;break;
  case 0xf0343au: /* imult   r14,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][14]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf0343cu;break;
  case 0xf0343cu: /* sub     r1,r0 */
   s.registers[0][0]=sub(&s,s.registers[0][0],s.registers[0][1]);
   s.pc=0xf0343eu;break;
  case 0xf0343eu: /* move    r21,r1 */
   s.registers[0][1]=s.registers[0][21];
   s.pc=0xf03440u;break;
  case 0xf03440u: /* add     r8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][8]);
   s.pc=0xf03442u;break;
  case 0xf03442u: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf03444u;break;
  case 0xf03444u: /* imult   r11,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][11]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf03446u;break;
  case 0xf03446u: /* move    r0,r11 */
   s.registers[0][11]=s.registers[0][0];
   s.pc=0xf03448u;break;
  case 0xf03448u: /* move    r22,r0 */
   s.registers[0][0]=s.registers[0][22];
   s.pc=0xf0344au;break;
  case 0xf0344au: /* imult   r14,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][14]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf0344cu;break;
  case 0xf0344cu: /* add     r1,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][1]);
   s.pc=0xf0344eu;break;
  case 0xf0344eu: /* add     r8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][8]);
   s.pc=0xf03450u;break;
  case 0xf03450u: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf03452u;break;
  case 0xf03452u: /* move    r0,r14 */
   s.registers[0][14]=s.registers[0][0];
   s.pc=0xf03454u;break;
  case 0xf03454u: /* movei   $f0347c,r2 */
   s.registers[0][2]=0xf0347cu;
   s.pc=0xf0345au;break;
  case 0xf0345au: /* cmpq    $0,r7 */
   (void)sub(&s,s.registers[0][7],0x0u);
   s.pc=0xf0345cu;break;
  case 0xf0345cu: /* jump    z,(r2) */
   if(condition(&s,2)){pending=1;target=s.registers[0][2];}
   s.pc=0xf0345eu;break;
  case 0xf0345eu: /* move    r7,r0 */
   s.registers[0][0]=s.registers[0][7];
   s.pc=0xf03460u;break;
  case 0xf03460u: /* move    r7,r1 */
   s.registers[0][1]=s.registers[0][7];
   s.pc=0xf03462u;break;
  case 0xf03462u: /* move    r7,r3 */
   s.registers[0][3]=s.registers[0][7];
   s.pc=0xf03464u;break;
  case 0xf03464u: /* imult   r15,r0 */
   s.registers[0][0]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][0])*(int32_t)sx16(s.registers[0][15]));
   zn(&s,s.registers[0][0]);
   s.pc=0xf03466u;break;
  case 0xf03466u: /* imult   r16,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][16]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf03468u;break;
  case 0xf03468u: /* imult   r17,r3 */
   s.registers[0][3]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][3])*(int32_t)sx16(s.registers[0][17]));
   zn(&s,s.registers[0][3]);
   s.pc=0xf0346au;break;
  case 0xf0346au: /* moveta  r0,r0 */
   s.registers[1][0]=s.registers[0][0];
   s.pc=0xf0346cu;break;
  case 0xf0346cu: /* moveta  r1,r1 */
   s.registers[1][1]=s.registers[0][1];
   s.pc=0xf0346eu;break;
  case 0xf0346eu: /* moveta  r3,r3 */
   s.registers[1][3]=s.registers[0][3];
   s.pc=0xf03470u;break;
  case 0xf03470u: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf03472u;break;
  case 0xf03472u: /* sharq   $e,r1 */
   s.c=s.registers[0][1]&1u;s.registers[0][1]=sar(s.registers[0][1],14);zn(&s,s.registers[0][1]);
   s.pc=0xf03474u;break;
  case 0xf03474u: /* sharq   $e,r3 */
   s.c=s.registers[0][3]&1u;s.registers[0][3]=sar(s.registers[0][3],14);zn(&s,s.registers[0][3]);
   s.pc=0xf03476u;break;
  case 0xf03476u: /* add     r0,r18 */
   s.registers[0][18]=add(&s,s.registers[0][18],s.registers[0][0]);
   s.pc=0xf03478u;break;
  case 0xf03478u: /* add     r1,r19 */
   s.registers[0][19]=add(&s,s.registers[0][19],s.registers[0][1]);
   s.pc=0xf0347au;break;
  case 0xf0347au: /* add     r3,r20 */
   s.registers[0][20]=add(&s,s.registers[0][20],s.registers[0][3]);
   s.pc=0xf0347cu;break;
  case 0xf0347cu: /* movei   $f0320c,r3 */
   s.registers[0][3]=0xf0320cu;
   s.pc=0xf03482u;break;
case 0xf03482u: /* load    (r3),r0 */
 CHECK(rd32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],&v));s.registers[0][0]=v;
 s.pc=0xf03484u;break;
  case 0xf03484u: /* storew  r9,(r0) */
   CHECK(wr16(bus,&s,s.registers[0][0],s.registers[0][9]));
   s.pc=0xf03486u;break;
  case 0xf03486u: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf03488u;break;
  case 0xf03488u: /* storew  r10,(r0) */
   CHECK(wr16(bus,&s,s.registers[0][0],s.registers[0][10]));
   s.pc=0xf0348au;break;
  case 0xf0348au: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf0348cu;break;
  case 0xf0348cu: /* storew  r11,(r0) */
   CHECK(wr16(bus,&s,s.registers[0][0],s.registers[0][11]));
   s.pc=0xf0348eu;break;
  case 0xf0348eu: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf03490u;break;
  case 0xf03490u: /* storew  r12,(r0) */
   CHECK(wr16(bus,&s,s.registers[0][0],s.registers[0][12]));
   s.pc=0xf03492u;break;
  case 0xf03492u: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf03494u;break;
  case 0xf03494u: /* storew  r13,(r0) */
   CHECK(wr16(bus,&s,s.registers[0][0],s.registers[0][13]));
   s.pc=0xf03496u;break;
  case 0xf03496u: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf03498u;break;
  case 0xf03498u: /* storew  r14,(r0) */
   CHECK(wr16(bus,&s,s.registers[0][0],s.registers[0][14]));
   s.pc=0xf0349au;break;
  case 0xf0349au: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf0349cu;break;
  case 0xf0349cu: /* storew  r15,(r0) */
   CHECK(wr16(bus,&s,s.registers[0][0],s.registers[0][15]));
   s.pc=0xf0349eu;break;
  case 0xf0349eu: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf034a0u;break;
  case 0xf034a0u: /* storew  r16,(r0) */
   CHECK(wr16(bus,&s,s.registers[0][0],s.registers[0][16]));
   s.pc=0xf034a2u;break;
  case 0xf034a2u: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf034a4u;break;
  case 0xf034a4u: /* storew  r17,(r0) */
   CHECK(wr16(bus,&s,s.registers[0][0],s.registers[0][17]));
   s.pc=0xf034a6u;break;
  case 0xf034a6u: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf034a8u;break;
  case 0xf034a8u: /* storew  r18,(r0) */
   CHECK(wr16(bus,&s,s.registers[0][0],s.registers[0][18]));
   s.pc=0xf034aau;break;
  case 0xf034aau: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf034acu;break;
  case 0xf034acu: /* storew  r19,(r0) */
   CHECK(wr16(bus,&s,s.registers[0][0],s.registers[0][19]));
   s.pc=0xf034aeu;break;
  case 0xf034aeu: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf034b0u;break;
  case 0xf034b0u: /* storew  r20,(r0) */
   CHECK(wr16(bus,&s,s.registers[0][0],s.registers[0][20]));
   s.pc=0xf034b2u;break;
  case 0xf034b2u: /* addq    $4,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],4u);
   s.pc=0xf034b4u;break;
case 0xf034b4u: /* movefa  r0,r1 */
 s.registers[0][1]=s.registers[1][0];
 s.pc=0xf034b6u;break;
  case 0xf034b6u: /* storew  r1,(r0) */
   CHECK(wr16(bus,&s,s.registers[0][0],s.registers[0][1]));
   s.pc=0xf034b8u;break;
  case 0xf034b8u: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf034bau;break;
case 0xf034bau: /* movefa  r1,r1 */
 s.registers[0][1]=s.registers[1][1];
 s.pc=0xf034bcu;break;
  case 0xf034bcu: /* storew  r1,(r0) */
   CHECK(wr16(bus,&s,s.registers[0][0],s.registers[0][1]));
   s.pc=0xf034beu;break;
  case 0xf034beu: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf034c0u;break;
case 0xf034c0u: /* movefa  r3,r1 */
 s.registers[0][1]=s.registers[1][3];
 s.pc=0xf034c2u;break;
  case 0xf034c2u: /* storew  r1,(r0) */
   CHECK(wr16(bus,&s,s.registers[0][0],s.registers[0][1]));
   s.pc=0xf034c4u;break;
  case 0xf034c4u: /* movei   $f031be,r2 */
   s.registers[0][2]=0xf031beu;
   s.pc=0xf034cau;break;
  case 0xf034cau: /* jump    (r2) */
   if(condition(&s,0)){pending=1;target=s.registers[0][2];}
   s.pc=0xf034ccu;break;
  case 0xf034ccu: /* add     r23,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][23]);
   s.pc=0xf034ceu;break;
  case 0xf034ceu: /* shlq    $18,r0 */
   s.c=s.registers[0][0]>>31;s.registers[0][0]=s.registers[0][0]<<24;zn(&s,s.registers[0][0]);
   s.pc=0xf034d0u;break;
  case 0xf034d0u: /* move    r24,r3 */
   s.registers[0][3]=s.registers[0][24];
   s.pc=0xf034d2u;break;
  case 0xf034d2u: /* jr      n,00F034EA */
   if(condition(&s,24)){pending=1;target=0xf034eau;}
   s.pc=0xf034d4u;break;
  case 0xf034d4u: /* shrq    $18,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=s.registers[0][0]>>24;zn(&s,s.registers[0][0]);
   s.pc=0xf034d6u;break;
  case 0xf034d6u: /* cmp     r0,r23 */
   (void)sub(&s,s.registers[0][23],s.registers[0][0]);
   s.pc=0xf034d8u;break;
  case 0xf034d8u: /* jr      nn,00F034E2 */
   if(condition(&s,20)){pending=1;target=0xf034e2u;}
   s.pc=0xf034dau;break;
  case 0xf034dau: /* move    r23,r1 */
   s.registers[0][1]=s.registers[0][23];
   s.pc=0xf034dcu;break;
  case 0xf034dcu: /* shlq    $1,r1 */
   s.c=s.registers[0][1]>>31;s.registers[0][1]=s.registers[0][1]<<1;zn(&s,s.registers[0][1]);
   s.pc=0xf034deu;break;
  case 0xf034deu: /* sub     r0,r1 */
   s.registers[0][1]=sub(&s,s.registers[0][1],s.registers[0][0]);
   s.pc=0xf034e0u;break;
  case 0xf034e0u: /* move    r1,r0 */
   s.registers[0][0]=s.registers[0][1];
   s.pc=0xf034e2u;break;
  case 0xf034e2u: /* shlq    $2,r0 */
   s.c=s.registers[0][0]>>31;s.registers[0][0]=s.registers[0][0]<<2;zn(&s,s.registers[0][0]);
   s.pc=0xf034e4u;break;
  case 0xf034e4u: /* add     r0,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],s.registers[0][0]);
   s.pc=0xf034e6u;break;
  case 0xf034e6u: /* jump    (r27) */
   if(condition(&s,0)){pending=1;target=s.registers[0][27];}
   s.pc=0xf034e8u;break;
case 0xf034e8u: /* load    (r3),r0 */
 CHECK(rd32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],&v));s.registers[0][0]=v;
 s.pc=0xf034eau;break;
  case 0xf034eau: /* bclr    $7,r0 */
   s.registers[0][0]&=~(1u<<7);
   zn(&s,s.registers[0][0]);
   s.pc=0xf034ecu;break;
  case 0xf034ecu: /* cmp     r0,r23 */
   (void)sub(&s,s.registers[0][23],s.registers[0][0]);
   s.pc=0xf034eeu;break;
  case 0xf034eeu: /* jr      nn,00F034F8 */
   if(condition(&s,20)){pending=1;target=0xf034f8u;}
   s.pc=0xf034f0u;break;
  case 0xf034f0u: /* move    r23,r1 */
   s.registers[0][1]=s.registers[0][23];
   s.pc=0xf034f2u;break;
  case 0xf034f2u: /* shlq    $1,r1 */
   s.c=s.registers[0][1]>>31;s.registers[0][1]=s.registers[0][1]<<1;zn(&s,s.registers[0][1]);
   s.pc=0xf034f4u;break;
  case 0xf034f4u: /* sub     r0,r1 */
   s.registers[0][1]=sub(&s,s.registers[0][1],s.registers[0][0]);
   s.pc=0xf034f6u;break;
  case 0xf034f6u: /* move    r1,r0 */
   s.registers[0][0]=s.registers[0][1];
   s.pc=0xf034f8u;break;
  case 0xf034f8u: /* shlq    $2,r0 */
   s.c=s.registers[0][0]>>31;s.registers[0][0]=s.registers[0][0]<<2;zn(&s,s.registers[0][0]);
   s.pc=0xf034fau;break;
  case 0xf034fau: /* add     r0,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],s.registers[0][0]);
   s.pc=0xf034fcu;break;
case 0xf034fcu: /* load    (r3),r0 */
 CHECK(rd32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],&v));s.registers[0][0]=v;
 s.pc=0xf034feu;break;
  case 0xf034feu: /* jump    (r27) */
   if(condition(&s,0)){pending=1;target=s.registers[0][27];}
   s.pc=0xf03500u;break;
  case 0xf03500u: /* neg     r0 */
   s.registers[0][0]=sub(&s,0,s.registers[0][0]);
   s.pc=0xf03502u;break;
default:return BIWN_GPU_COMMAND4720_BAD_PC;
}if(delayed){if(pending)return BIWN_GPU_COMMAND4720_BAD_DELAY;s.pc=resume;}if(s.pc==0xf031beu){*state=s;return 0;}}return BIWN_GPU_COMMAND4720_WORK_LIMIT;}
