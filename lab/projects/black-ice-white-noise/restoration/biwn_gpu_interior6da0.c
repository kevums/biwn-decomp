/* Generated from the pinned GPU6DA0 overlay by
 * scripts/generate_biwn_gpu_interior6da0.py. Analyst static recompilation,
 * not recovered original source. Integer primitive behavior is checked
 * against the pinned Virtual Jaguar core; no core runs on the C side. */
#include "biwn_gpu_interior6da0.h"
#include <string.h>
static uint32_t sar(uint32_t v,unsigned n){return n>=32?((v&0x80000000u)?0xffffffffu:0):(v>>n)|((v&0x80000000u)?(0xffffffffu<<(32-n)):0);}
static void zn(struct biwn_gpu_interior6da0_state *s,uint32_t v){s->z=v==0;s->n=v>>31;}
static uint32_t add(struct biwn_gpu_interior6da0_state *s,uint32_t a,uint32_t b){uint32_t v=a+b;s->c=b>~a;zn(s,v);return v;}
static uint32_t sub(struct biwn_gpu_interior6da0_state *s,uint32_t a,uint32_t b){uint32_t v=a-b;s->c=b>a;zn(s,v);return v;}
static int condition(struct biwn_gpu_interior6da0_state *s,unsigned code){unsigned flags=s->z|(s->c<<1)|(s->n<<2);return !((code&1u)&&(flags&1u))&&!((code&2u)&&!(flags&1u))&&!((code&4u)&&(flags&(2u<<(code>>4))))&&!((code&8u)&&!(flags&(2u<<(code>>4))));}
static uint32_t be32(const uint8_t *p){return((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
static void put32(uint8_t *p,uint32_t v){p[0]=(uint8_t)(v>>24);p[1]=(uint8_t)(v>>16);p[2]=(uint8_t)(v>>8);p[3]=(uint8_t)v;}
static int local(uint32_t a){return a>=0xf03000u&&a<=0xf03ffcu;}
static int rd32(struct biwn_gpu_interior6da0_bus *bus,struct biwn_gpu_interior6da0_state *s,uint32_t a,uint32_t *v){if(local(a)){*v=be32(s->local_RAM+a-0xf03000u);return 0;}if(a==0xf02104u){*v=s->matrix_control;return 0;}if(a==0xf02108u){*v=s->matrix_pointer;return 0;}return bus->read32(bus->context,a,v)?2:0;}
static int rd16(struct biwn_gpu_interior6da0_bus *bus,struct biwn_gpu_interior6da0_state *s,uint32_t a,uint32_t *v){uint16_t h;if(a>=0xf03000u&&a<=0xf03ffeu){unsigned p=a-0xf03000u;*v=((uint32_t)s->local_RAM[p]<<8)|s->local_RAM[p+1];return 0;}if(bus->read16(bus->context,a,&h))return 2;*v=h;return 0;}
static int loadw(struct biwn_gpu_interior6da0_bus *bus,struct biwn_gpu_interior6da0_state *s,uint32_t a,uint32_t *v){if(a>=0xf03000u&&a<=0xf03fffu)return rd32(bus,s,a&~3u,v);return rd16(bus,s,a,v);}
static int wr32(struct biwn_gpu_interior6da0_bus *bus,struct biwn_gpu_interior6da0_state *s,uint32_t a,uint32_t v){if(local(a)){put32(s->local_RAM+a-0xf03000u,v);return 0;}if(a==0xf02104u){s->matrix_control=v;return 0;}if(a==0xf02108u){s->matrix_pointer=v&~3u;return 0;}return bus->write32(bus->context,a,v)?2:0;}
static int wr16(struct biwn_gpu_interior6da0_bus *bus,struct biwn_gpu_interior6da0_state *s,uint32_t a,uint32_t v){if(a>=0xf03000u&&a<=0xf03fffu)return wr32(bus,s,a&~1u,v&0xffffu);return bus->write16(bus->context,a,(uint16_t)v)?2:0;}
static const uint8_t source_image[]={0x98,0x0,0x32,0xc,0x0,0xf0,0xa4,0x7,0x8,0x80,0xa4,0x1,0x8,0x80,0xa4,0x8,0x8,0x80,0xa4,0x9,0x8,0x80,0xa0,0x24,0x8,0x41,0xa0,0x25,0x8,0x41,0xa0,0x26,0x62,0x4,0x62,0x5,0x62,0x6,0x6e,0x4,0x6e,0x5,0x6e,0x6,0x8,0x88,0x98,0x3,0x0,0x18,0x0,0x0,0xa5,0xa,0x41,0x23,0x18,0x88,0x0,0x6a,0x98,0x2,0x0,0x40,0x0,0x0,0x8,0x4a,0x8c,0xc,0xa1,0x4b,0x40,0x4c,0x8,0x4a,0x10,0xac,0xa1,0x4d,0x40,0x4b,0x8,0x4a,0x10,0x8b,0xa1,0x4e,0x40,0x4d,0x8,0x4a,0x10,0xcd,0xa1,0x4f,0x40,0x4e,0x19,0xa,0x40,0x4f,0x8c,0x31,0x8c,0x12,0x60,0x51,0x88,0xf3,0x8,0x93,0xbc,0xf1,0xbe,0x72,0x9,0x7,0x9,0x13,0xbc,0xf1,0xbe,0x72,0x66,0x11,0x9,0x7,0x8,0xd3,0xb8,0xf1,0xba,0x6b,0x8,0x87,0x8,0x93,0xb8,0xec,0xba,0x6d,0x8,0x87,0x8,0xd3,0x8d,0x31,0xbc,0xf2,0x62,0x11,0xbe,0x72,0x29,0x31,0x9,0x7,0xbc,0xf1,0x8,0x87,0x8c,0xd1,0xbc,0xf2,0x18,0x31,0xd7,0xa1,0x8,0x87,0xbc,0xe8,0x1a,0x87,0xb8,0xef,0x8,0x47,0xb8,0xee,0x8,0x87,0xb8,0xef,0x8,0x47,0xb8,0xee,0x8c,0x31,0x98,0x10,0x31,0xbe,0x0,0xf0,0xa4,0x13,0xd2,0x0,0xbe,0x71,0x0,0x0,0x0,0x0};
enum biwn_gpu_interior6da0_status biwn_gpu_interior6da0_prepare(struct biwn_gpu_interior6da0_state *s,uint32_t scene,uint32_t sector){if(!s||s->z>1||s->c>1||s->n>1)return 1;memcpy(s->local_RAM+0x240,source_image,sizeof(source_image));put32(s->local_RAM+0x204,28064u);put32(s->local_RAM+0x20c,293832u);put32(s->local_RAM+0x210,0x49b8c);put32(s->local_RAM+0x214,scene);put32(s->local_RAM+0x218,sector);put32(s->local_RAM+0x21c,301960u);s->pc=0xf03240;s->instructions=0;return 0;}
#define CHECK(e) do{int status=(e);if(status)return(enum biwn_gpu_interior6da0_status)status;}while(0)
enum biwn_gpu_interior6da0_status biwn_gpu_interior6da0_run(struct biwn_gpu_interior6da0_bus *bus,struct biwn_gpu_interior6da0_state *state,uint32_t budget){struct biwn_gpu_interior6da0_state s;uint32_t v,target=0;unsigned pending=0;if(!bus||!state||!budget||!bus->read16||!bus->read32||!bus->write16||!bus->write32||state->z>1||state->c>1||state->n>1)return 1;s=*state;while(budget--){unsigned delayed=pending;uint32_t resume=target;pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){
  case 0xf03240u: /* movei   $f0320c,r0 */
   s.registers[0][0]=0xf0320cu;
   s.pc=0xf03246u;break;
  case 0xf03246u: /* load    (r0),r7 */
   CHECK(rd32(bus,&s,s.registers[0][0]&~3u,&v));s.registers[0][7]=v;
   s.pc=0xf03248u;break;
  case 0xf03248u: /* addq    $4,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],4u);
   s.pc=0xf0324au;break;
  case 0xf0324au: /* load    (r0),r1 */
   CHECK(rd32(bus,&s,s.registers[0][0]&~3u,&v));s.registers[0][1]=v;
   s.pc=0xf0324cu;break;
  case 0xf0324cu: /* addq    $4,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],4u);
   s.pc=0xf0324eu;break;
  case 0xf0324eu: /* load    (r0),r8 */
   CHECK(rd32(bus,&s,s.registers[0][0]&~3u,&v));s.registers[0][8]=v;
   s.pc=0xf03250u;break;
  case 0xf03250u: /* addq    $4,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],4u);
   s.pc=0xf03252u;break;
  case 0xf03252u: /* load    (r0),r9 */
   CHECK(rd32(bus,&s,s.registers[0][0]&~3u,&v));s.registers[0][9]=v;
   s.pc=0xf03254u;break;
  case 0xf03254u: /* addq    $4,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],4u);
   s.pc=0xf03256u;break;
  case 0xf03256u: /* loadw   (r1),r4 */
   CHECK(loadw(bus,&s,s.registers[0][1],&v));s.registers[0][4]=v;
   s.pc=0xf03258u;break;
  case 0xf03258u: /* addq    $2,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],2u);
   s.pc=0xf0325au;break;
  case 0xf0325au: /* loadw   (r1),r5 */
   CHECK(loadw(bus,&s,s.registers[0][1],&v));s.registers[0][5]=v;
   s.pc=0xf0325cu;break;
  case 0xf0325cu: /* addq    $2,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],2u);
   s.pc=0xf0325eu;break;
  case 0xf0325eu: /* loadw   (r1),r6 */
   CHECK(loadw(bus,&s,s.registers[0][1],&v));s.registers[0][6]=v;
   s.pc=0xf03260u;break;
  case 0xf03260u: /* shlq    $10,r4 */
   s.c=s.registers[0][4]>>31;s.registers[0][4]=s.registers[0][4]<<16;zn(&s,s.registers[0][4]);
   s.pc=0xf03262u;break;
  case 0xf03262u: /* shlq    $10,r5 */
   s.c=s.registers[0][5]>>31;s.registers[0][5]=s.registers[0][5]<<16;zn(&s,s.registers[0][5]);
   s.pc=0xf03264u;break;
  case 0xf03264u: /* shlq    $10,r6 */
   s.c=s.registers[0][6]>>31;s.registers[0][6]=s.registers[0][6]<<16;zn(&s,s.registers[0][6]);
   s.pc=0xf03266u;break;
  case 0xf03266u: /* sharq   $10,r4 */
   s.c=s.registers[0][4]&1u;s.registers[0][4]=sar(s.registers[0][4],16);zn(&s,s.registers[0][4]);
   s.pc=0xf03268u;break;
  case 0xf03268u: /* sharq   $10,r5 */
   s.c=s.registers[0][5]&1u;s.registers[0][5]=sar(s.registers[0][5],16);zn(&s,s.registers[0][5]);
   s.pc=0xf0326au;break;
  case 0xf0326au: /* sharq   $10,r6 */
   s.c=s.registers[0][6]&1u;s.registers[0][6]=sar(s.registers[0][6],16);zn(&s,s.registers[0][6]);
   s.pc=0xf0326cu;break;
  case 0xf0326cu: /* addq    $4,r8 */
   s.registers[0][8]=add(&s,s.registers[0][8],4u);
   s.pc=0xf0326eu;break;
  case 0xf0326eu: /* movei   $18,r3 */
   s.registers[0][3]=0x18u;
   s.pc=0xf03274u;break;
  case 0xf03274u: /* load    (r8),r10 */
   CHECK(rd32(bus,&s,s.registers[0][8]&~3u,&v));s.registers[0][10]=v;
   s.pc=0xf03276u;break;
  case 0xf03276u: /* mult    r9,r3 */
   s.registers[0][3]=(s.registers[0][3]&0xffffu)*(s.registers[0][9]&0xffffu);
   zn(&s,s.registers[0][3]);
   s.pc=0xf03278u;break;
  case 0xf03278u: /* subq    $4,r8 */
   s.registers[0][8]=sub(&s,s.registers[0][8],4u);
   s.pc=0xf0327au;break;
  case 0xf0327au: /* add     r3,r10 */
   s.registers[0][10]=add(&s,s.registers[0][10],s.registers[0][3]);
   s.pc=0xf0327cu;break;
  case 0xf0327cu: /* movei   $40,r2 */
   s.registers[0][2]=0x40u;
   s.pc=0xf03282u;break;
  case 0xf03282u: /* addq    $2,r10 */
   s.registers[0][10]=add(&s,s.registers[0][10],2u);
   s.pc=0xf03284u;break;
  case 0xf03284u: /* moveq   0,r12 */
   s.registers[0][12]=0u;
   s.pc=0xf03286u;break;
  case 0xf03286u: /* loadw   (r10),r11 */
   CHECK(loadw(bus,&s,s.registers[0][10],&v));s.registers[0][11]=v;
   s.pc=0xf03288u;break;
  case 0xf03288u: /* mult    r2,r12 */
   s.registers[0][12]=(s.registers[0][12]&0xffffu)*(s.registers[0][2]&0xffffu);
   zn(&s,s.registers[0][12]);
   s.pc=0xf0328au;break;
  case 0xf0328au: /* addq    $2,r10 */
   s.registers[0][10]=add(&s,s.registers[0][10],2u);
   s.pc=0xf0328cu;break;
  case 0xf0328cu: /* sub     r5,r12 */
   s.registers[0][12]=sub(&s,s.registers[0][12],s.registers[0][5]);
   s.pc=0xf0328eu;break;
  case 0xf0328eu: /* loadw   (r10),r13 */
   CHECK(loadw(bus,&s,s.registers[0][10],&v));s.registers[0][13]=v;
   s.pc=0xf03290u;break;
  case 0xf03290u: /* mult    r2,r11 */
   s.registers[0][11]=(s.registers[0][11]&0xffffu)*(s.registers[0][2]&0xffffu);
   zn(&s,s.registers[0][11]);
   s.pc=0xf03292u;break;
  case 0xf03292u: /* addq    $2,r10 */
   s.registers[0][10]=add(&s,s.registers[0][10],2u);
   s.pc=0xf03294u;break;
  case 0xf03294u: /* sub     r4,r11 */
   s.registers[0][11]=sub(&s,s.registers[0][11],s.registers[0][4]);
   s.pc=0xf03296u;break;
  case 0xf03296u: /* loadw   (r10),r14 */
   CHECK(loadw(bus,&s,s.registers[0][10],&v));s.registers[0][14]=v;
   s.pc=0xf03298u;break;
  case 0xf03298u: /* mult    r2,r13 */
   s.registers[0][13]=(s.registers[0][13]&0xffffu)*(s.registers[0][2]&0xffffu);
   zn(&s,s.registers[0][13]);
   s.pc=0xf0329au;break;
  case 0xf0329au: /* addq    $2,r10 */
   s.registers[0][10]=add(&s,s.registers[0][10],2u);
   s.pc=0xf0329cu;break;
  case 0xf0329cu: /* sub     r6,r13 */
   s.registers[0][13]=sub(&s,s.registers[0][13],s.registers[0][6]);
   s.pc=0xf0329eu;break;
  case 0xf0329eu: /* loadw   (r10),r15 */
   CHECK(loadw(bus,&s,s.registers[0][10],&v));s.registers[0][15]=v;
   s.pc=0xf032a0u;break;
  case 0xf032a0u: /* mult    r2,r14 */
   s.registers[0][14]=(s.registers[0][14]&0xffffu)*(s.registers[0][2]&0xffffu);
   zn(&s,s.registers[0][14]);
   s.pc=0xf032a2u;break;
  case 0xf032a2u: /* subq    $8,r10 */
   s.registers[0][10]=sub(&s,s.registers[0][10],8u);
   s.pc=0xf032a4u;break;
  case 0xf032a4u: /* mult    r2,r15 */
   s.registers[0][15]=(s.registers[0][15]&0xffffu)*(s.registers[0][2]&0xffffu);
   zn(&s,s.registers[0][15]);
   s.pc=0xf032a6u;break;
  case 0xf032a6u: /* moveq   1,r17 */
   s.registers[0][17]=1u;
   s.pc=0xf032a8u;break;
  case 0xf032a8u: /* moveq   0,r18 */
   s.registers[0][18]=0u;
   s.pc=0xf032aau;break;
  case 0xf032aau: /* shlq    $1e,r17 */
   s.c=s.registers[0][17]>>31;s.registers[0][17]=s.registers[0][17]<<30;zn(&s,s.registers[0][17]);
   s.pc=0xf032acu;break;
  case 0xf032acu: /* move    r7,r19 */
   s.registers[0][19]=s.registers[0][7];
   s.pc=0xf032aeu;break;
  case 0xf032aeu: /* addq    $4,r19 */
   s.registers[0][19]=add(&s,s.registers[0][19],4u);
   s.pc=0xf032b0u;break;
  case 0xf032b0u: /* store   r17,(r7) */
   CHECK(wr32(bus,&s,local(s.registers[0][7])?(s.registers[0][7]&~3u):s.registers[0][7],s.registers[0][17]));
   s.pc=0xf032b2u;break;
  case 0xf032b2u: /* store   r18,(r19) */
   CHECK(wr32(bus,&s,local(s.registers[0][19])?(s.registers[0][19]&~3u):s.registers[0][19],s.registers[0][18]));
   s.pc=0xf032b4u;break;
  case 0xf032b4u: /* addq    $8,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],8u);
   s.pc=0xf032b6u;break;
  case 0xf032b6u: /* addq    $8,r19 */
   s.registers[0][19]=add(&s,s.registers[0][19],8u);
   s.pc=0xf032b8u;break;
  case 0xf032b8u: /* store   r17,(r7) */
   CHECK(wr32(bus,&s,local(s.registers[0][7])?(s.registers[0][7]&~3u):s.registers[0][7],s.registers[0][17]));
   s.pc=0xf032bau;break;
  case 0xf032bau: /* store   r18,(r19) */
   CHECK(wr32(bus,&s,local(s.registers[0][19])?(s.registers[0][19]&~3u):s.registers[0][19],s.registers[0][18]));
   s.pc=0xf032bcu;break;
  case 0xf032bcu: /* shrq    $10,r17 */
   s.c=s.registers[0][17]&1u;s.registers[0][17]=s.registers[0][17]>>16;zn(&s,s.registers[0][17]);
   s.pc=0xf032beu;break;
  case 0xf032beu: /* addq    $8,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],8u);
   s.pc=0xf032c0u;break;
  case 0xf032c0u: /* addq    $6,r19 */
   s.registers[0][19]=add(&s,s.registers[0][19],6u);
   s.pc=0xf032c2u;break;
  case 0xf032c2u: /* storew  r17,(r7) */
   CHECK(wr16(bus,&s,s.registers[0][7],s.registers[0][17]));
   s.pc=0xf032c4u;break;
  case 0xf032c4u: /* storew  r11,(r19) */
   CHECK(wr16(bus,&s,s.registers[0][19],s.registers[0][11]));
   s.pc=0xf032c6u;break;
  case 0xf032c6u: /* addq    $4,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],4u);
   s.pc=0xf032c8u;break;
  case 0xf032c8u: /* addq    $4,r19 */
   s.registers[0][19]=add(&s,s.registers[0][19],4u);
   s.pc=0xf032cau;break;
  case 0xf032cau: /* storew  r12,(r7) */
   CHECK(wr16(bus,&s,s.registers[0][7],s.registers[0][12]));
   s.pc=0xf032ccu;break;
  case 0xf032ccu: /* storew  r13,(r19) */
   CHECK(wr16(bus,&s,s.registers[0][19],s.registers[0][13]));
   s.pc=0xf032ceu;break;
  case 0xf032ceu: /* addq    $4,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],4u);
   s.pc=0xf032d0u;break;
  case 0xf032d0u: /* addq    $6,r19 */
   s.registers[0][19]=add(&s,s.registers[0][19],6u);
   s.pc=0xf032d2u;break;
  case 0xf032d2u: /* moveq   9,r17 */
   s.registers[0][17]=9u;
   s.pc=0xf032d4u;break;
  case 0xf032d4u: /* store   r18,(r7) */
   CHECK(wr32(bus,&s,local(s.registers[0][7])?(s.registers[0][7]&~3u):s.registers[0][7],s.registers[0][18]));
   s.pc=0xf032d6u;break;
  case 0xf032d6u: /* shlq    $10,r17 */
   s.c=s.registers[0][17]>>31;s.registers[0][17]=s.registers[0][17]<<16;zn(&s,s.registers[0][17]);
   s.pc=0xf032d8u;break;
  case 0xf032d8u: /* store   r18,(r19) */
   CHECK(wr32(bus,&s,local(s.registers[0][19])?(s.registers[0][19]&~3u):s.registers[0][19],s.registers[0][18]));
   s.pc=0xf032dau;break;
  case 0xf032dau: /* or      r9,r17 */
   s.registers[0][17]|=s.registers[0][9];
   zn(&s,s.registers[0][17]);
   s.pc=0xf032dcu;break;
  case 0xf032dcu: /* addq    $8,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],8u);
   s.pc=0xf032deu;break;
  case 0xf032deu: /* store   r17,(r7) */
   CHECK(wr32(bus,&s,local(s.registers[0][7])?(s.registers[0][7]&~3u):s.registers[0][7],s.registers[0][17]));
   s.pc=0xf032e0u;break;
  case 0xf032e0u: /* addq    $4,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],4u);
   s.pc=0xf032e2u;break;
  case 0xf032e2u: /* moveq   6,r17 */
   s.registers[0][17]=6u;
   s.pc=0xf032e4u;break;
  case 0xf032e4u: /* store   r18,(r7) */
   CHECK(wr32(bus,&s,local(s.registers[0][7])?(s.registers[0][7]&~3u):s.registers[0][7],s.registers[0][18]));
   s.pc=0xf032e6u;break;
  case 0xf032e6u: /* subq    $1,r17 */
   s.registers[0][17]=sub(&s,s.registers[0][17],1u);
   s.pc=0xf032e8u;break;
  case 0xf032e8u: /* jr      nz,00F032E4 */
   if(condition(&s,1)){pending=1;target=0xf032e4u;}
   s.pc=0xf032eau;break;
  case 0xf032eau: /* addq    $4,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],4u);
   s.pc=0xf032ecu;break;
  case 0xf032ecu: /* store   r8,(r7) */
   CHECK(wr32(bus,&s,local(s.registers[0][7])?(s.registers[0][7]&~3u):s.registers[0][7],s.registers[0][8]));
   s.pc=0xf032eeu;break;
  case 0xf032eeu: /* subq    $14,r7 */
   s.registers[0][7]=sub(&s,s.registers[0][7],20u);
   s.pc=0xf032f0u;break;
  case 0xf032f0u: /* storew  r15,(r7) */
   CHECK(wr16(bus,&s,s.registers[0][7],s.registers[0][15]));
   s.pc=0xf032f2u;break;
  case 0xf032f2u: /* addq    $2,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],2u);
   s.pc=0xf032f4u;break;
  case 0xf032f4u: /* storew  r14,(r7) */
   CHECK(wr16(bus,&s,s.registers[0][7],s.registers[0][14]));
   s.pc=0xf032f6u;break;
  case 0xf032f6u: /* addq    $4,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],4u);
   s.pc=0xf032f8u;break;
  case 0xf032f8u: /* storew  r15,(r7) */
   CHECK(wr16(bus,&s,s.registers[0][7],s.registers[0][15]));
   s.pc=0xf032fau;break;
  case 0xf032fau: /* addq    $2,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],2u);
   s.pc=0xf032fcu;break;
  case 0xf032fcu: /* storew  r14,(r7) */
   CHECK(wr16(bus,&s,s.registers[0][7],s.registers[0][14]));
   s.pc=0xf032feu;break;
  case 0xf032feu: /* moveq   1,r17 */
   s.registers[0][17]=1u;
   s.pc=0xf03300u;break;
  case 0xf03300u: /* movei   $f031be,r16 */
   s.registers[0][16]=0xf031beu;
   s.pc=0xf03306u;break;
  case 0xf03306u: /* load    (r0),r19 */
   CHECK(rd32(bus,&s,s.registers[0][0]&~3u,&v));s.registers[0][19]=v;
   s.pc=0xf03308u;break;
  case 0xf03308u: /* jump    (r16) */
   if(condition(&s,0)){pending=1;target=s.registers[0][16];}
   s.pc=0xf0330au;break;
  case 0xf0330au: /* store   r17,(r19) */
   CHECK(wr32(bus,&s,local(s.registers[0][19])?(s.registers[0][19]&~3u):s.registers[0][19],s.registers[0][17]));
   s.pc=0xf0330cu;break;
default:return BIWN_GPU_INTERIOR6DA0_BAD_PC;
 }if(delayed){if(pending)return BIWN_GPU_INTERIOR6DA0_BAD_DELAY;s.pc=resume;}if(s.pc==0xf031beu){*state=s;return BIWN_GPU_INTERIOR6DA0_OK;}}return BIWN_GPU_INTERIOR6DA0_WORK_LIMIT;}
