/* Generated from the pinned GPU6AE0 overlay by
 * scripts/generate_biwn_gpu_interior6ae0.py. Analyst static recompilation,
 * not recovered original source. Integer primitive behavior is checked
 * against the pinned Virtual Jaguar core; no core runs on the C side. */
#include "biwn_gpu_interior6ae0.h"
#include <string.h>
static uint32_t sx16(uint32_t v){return(v&0x7fffu)-(v&0x8000u);}
static uint32_t sar(uint32_t v,unsigned n){return n>=32?((v&0x80000000u)?0xffffffffu:0):(v>>n)|((v&0x80000000u)?(0xffffffffu<<(32-n)):0);}
static void zn(struct biwn_gpu_interior6ae0_state *s,uint32_t v){s->z=v==0;s->n=v>>31;}
static uint32_t add(struct biwn_gpu_interior6ae0_state *s,uint32_t a,uint32_t b){uint32_t v=a+b;s->c=b>~a;zn(s,v);return v;}
static uint32_t sub(struct biwn_gpu_interior6ae0_state *s,uint32_t a,uint32_t b){uint32_t v=a-b;s->c=b>a;zn(s,v);return v;}
static int condition(struct biwn_gpu_interior6ae0_state *s,unsigned code){unsigned flags=s->z|(s->c<<1)|(s->n<<2);return !((code&1u)&&(flags&1u))&&!((code&2u)&&!(flags&1u))&&!((code&4u)&&(flags&(2u<<(code>>4))))&&!((code&8u)&&!(flags&(2u<<(code>>4))));}
static uint32_t be32(const uint8_t *p){return((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
static void put32(uint8_t *p,uint32_t v){p[0]=(uint8_t)(v>>24);p[1]=(uint8_t)(v>>16);p[2]=(uint8_t)(v>>8);p[3]=(uint8_t)v;}
static int local(uint32_t a){return a>=0xf03000u&&a<=0xf03ffcu;}
static int rd32(struct biwn_gpu_interior6ae0_bus *bus,struct biwn_gpu_interior6ae0_state *s,uint32_t a,uint32_t *v){if(local(a)){*v=be32(s->local_RAM+a-0xf03000u);return 0;}if(a==0xf02104u){*v=s->matrix_control;return 0;}if(a==0xf02108u){*v=s->matrix_pointer;return 0;}return bus->read32(bus->context,a,v)?2:0;}
static int rd16(struct biwn_gpu_interior6ae0_bus *bus,struct biwn_gpu_interior6ae0_state *s,uint32_t a,uint32_t *v){uint16_t h;if(a>=0xf03000u&&a<=0xf03ffeu){unsigned p=a-0xf03000u;*v=((uint32_t)s->local_RAM[p]<<8)|s->local_RAM[p+1];return 0;}if(bus->read16(bus->context,a,&h))return 2;*v=h;return 0;}
static int loadw(struct biwn_gpu_interior6ae0_bus *bus,struct biwn_gpu_interior6ae0_state *s,uint32_t a,uint32_t *v){if(a>=0xf03000u&&a<=0xf03fffu)return rd32(bus,s,a&~3u,v);return rd16(bus,s,a,v);}
static int wr32(struct biwn_gpu_interior6ae0_bus *bus,struct biwn_gpu_interior6ae0_state *s,uint32_t a,uint32_t v){if(local(a)){put32(s->local_RAM+a-0xf03000u,v);return 0;}if(a==0xf02104u){s->matrix_control=v;return 0;}if(a==0xf02108u){s->matrix_pointer=v&~3u;return 0;}return bus->write32(bus->context,a,v)?2:0;}
static void divide(struct biwn_gpu_interior6ae0_state *s,unsigned m,unsigned n){uint32_t q=s->registers[0][n],r=0,d=s->registers[0][m];unsigned i;if(s->division_control&1u){r=q>>16;q<<=16;}for(i=0;i<32;i++){uint32_t sign=r&0x80000000u;r=(r<<1)|(q>>31);r+=sign?d:0u-d;q=(q<<1)|((~r)>>31);}s->registers[0][n]=q;s->remainder=r;}
static int matrix(struct biwn_gpu_interior6ae0_bus *bus,struct biwn_gpu_interior6ae0_state *s,unsigned m,unsigned n){unsigned i,count=s->matrix_control&15u;uint32_t a=s->matrix_pointer,v;int64_t sum=0;for(i=0;i<count;i++){uint32_t packed=s->registers[1][m+(i>>1)];int32_t x=(int32_t)sx16(packed>>(i&1u?16:0));int status=rd16(bus,s,a+2,&v);if(status)return status;sum+=(int64_t)x*(int32_t)sx16(v);a+=(s->matrix_control&16u)?4u*count:4u;}s->registers[0][n]=(uint32_t)sum;zn(s,(uint32_t)sum);return 0;}
static const uint8_t source_image[]={0x8c,0x20,0x8c,0x21,0x20,0x0,0x20,0x1,0x66,0x0,0x62,0x1,0x98,0x2,0x32,0x14,0x0,0xf0,0xa4,0x44,0x8,0x82,0x8,0x84,0xa4,0x50,0xa4,0x85,0x8,0x82,0x8,0x84,0xa4,0x43,0xa4,0x86,0x88,0x67,0x8f,0x14,0x88,0x68,0x8c,0xd5,0x98,0x9,0x32,0x8e,0x0,0xf0,0x98,0xa,0x32,0xa0,0x0,0xf0,0x98,0xb,0x32,0xcc,0x0,0xf0,0x98,0xc,0x32,0xda,0x0,0xf0,0x98,0xd,0x32,0xe2,0x0,0xf0,0xd1,0x60,0x39,0xf3,0x78,0xe8,0xd1,0xa2,0x8,0x87,0xa4,0xf1,0x8,0x87,0xa,0xd1,0xa2,0x32,0x42,0xb2,0x0,0xd2,0x8,0x52,0xa2,0x53,0x35,0x33,0xd4,0x81,0x18,0x52,0x35,0x13,0xd1,0x82,0xe4,0x0,0x8,0x92,0xa2,0x50,0x18,0x92,0x78,0x10,0xd1,0x82,0x88,0x6e,0x79,0xc8,0xd1,0x62,0xe4,0x0,0xa5,0xcf,0x79,0xf0,0xd7,0x41,0x9,0xe,0xd1,0x80,0x8a,0x11,0x42,0x91,0x0,0xb1,0xbd,0x10,0x8,0x88,0xbd,0x11,0x8,0x88,0x35,0xf3,0xd1,0x42,0x2,0xb2,0xd1,0x20,0x8c,0xf,0xbd,0x0,0x8,0x88,0xbd,0xf,0x98,0x7,0x32,0xc,0x0,0xf0,0x98,0x2,0x34,0xd0,0x0,0xf0,0xa4,0xe8,0x8d,0x2a,0x8,0x87,0xa1,0xe,0x62,0xe,0x6e,0xe,0x8,0x48,0xbc,0x4e,0x18,0x2a,0xd7,0x21,0xc,0x82,0xa4,0xe9,0xa1,0xb,0xa1,0x23,0x62,0xb,0x62,0x3,0x6e,0xb,0x6e,0x3,0x8,0x48,0x8,0x49,0xa1,0xc,0xa1,0x24,0x62,0xc,0x62,0x4,0x6e,0xc,0x6e,0x4,0x8,0x48,0x8,0x49,0xa1,0xd,0xa1,0x25,0x62,0xd,0x62,0x5,0x6e,0xd,0x6e,0x5,0x1,0x63,0x1,0x84,0x1,0xa5,0x19,0x82,0x9,0x87,0xa4,0xe6,0x8,0x86,0x98,0x19,0x21,0x4,0x0,0xf0,0x98,0x18,0x0,0x3,0x0,0x0,0xbf,0x38,0x98,0xa,0x4,0x0,0x0,0x0,0x98,0x7,0x0,0xad,0x0,0x0,0x89,0x49,0x98,0x8,0x0,0x6f,0x0,0x0,0x20,0x9,0x98,0xb,0x34,0xe,0x0,0xf0,0x98,0xc,0x21,0x8,0x0,0xf0,0x98,0x17,0x0,0x40,0x0,0x0,0xa4,0xd8,0x98,0x16,0x34,0x6e,0x0,0xf0,0x7c,0x18,0xd2,0xc2,0x8,0x58,0x8c,0xe,0xa3,0xd,0x42,0xee,0x8,0x58,0x10,0x8e,0xa3,0xf,0x42,0xed,0x8,0x58,0x10,0x6d,0xa3,0x10,0x42,0xef,0x8,0x58,0x10,0xaf,0xa3,0x11,0x42,0xf0,0x42,0xf1,0x88,0x12,0x88,0x33,0x88,0x14,0x88,0x35,0xcc,0x16,0x62,0xe,0x8,0xd6,0x8c,0x18,0x8a,0x39,0xd1,0x60,0x9,0x16,0x8a,0x18,0x8a,0x39,0xd1,0x60,0x9,0x16,0x8a,0x18,0x8c,0x19,0xd1,0x60,0x9,0x16,0x8c,0x18,0x8c,0x19,0xd1,0x60,0x9,0x16,0x8c,0x18,0x98,0x19,0x0,0xe0,0x0,0x0,0x7b,0x13,0xd5,0xb8,0x7a,0x59,0xd5,0x78,0x8f,0xf8,0x98,0x19,0x3,0x0,0x0,0x0,0x7b,0x15,0xd4,0xb8,0x7a,0x99,0xd4,0x78,0xe4,0x0,0xd4,0x40,0xe4,0x0,0x8c,0x15,0x98,0x16,0x33,0x7e,0x0,0xf0,0xbc,0xd5,0xd2,0xc0,0x9,0x6,0x1,0xb8,0x1,0xf9,0x24,0x18,0x24,0x19,0x29,0xd8,0x1b,0x2,0xbd,0x82,0x93,0x18,0x93,0x39,0xdb,0x1a,0xb,0x2,0xbd,0x82,0x93,0x18,0x93,0x39,0xdb,0x1b,0x6d,0xda,0x6d,0xdb,0x44,0xfa,0x7c,0x3b,0xd4,0x54,0xe4,0x0,0x8d,0x1b,0x58,0x1a,0xd4,0x44,0x57,0x7a,0x20,0x1a,0x7b,0x49,0xd4,0x58,0x79,0x5a,0x89,0x3a,0xd4,0x58,0xe4,0x0,0x89,0x5a,0x1,0x1a,0x7b,0x52,0xd4,0x58,0x7a,0x7a,0x8b,0x52,0xd4,0x58,0x7b,0x74,0x8b,0x53,0xd4,0x58,0x7a,0xbb,0x8b,0x74,0xd2,0xd8,0xe4,0x0,0xd2,0xc0,0x8b,0x75,0x98,0x2,0x32,0x1c,0x0,0xf0,0xa4,0x46,0x19,0x6,0x98,0x3,0x34,0x8a,0x0,0xf0,0x98,0x4,0x34,0x9a,0x0,0xf0,0x98,0x5,0x34,0xc2,0x0,0xf0,0x9,0x6,0xa4,0xc7,0x78,0x7,0xd0,0xa2,0x8,0x86,0xa4,0xc8,0x18,0x86,0x88,0xc9,0x9,0x9,0xa5,0x2a,0x78,0xa,0xd0,0x62,0x8,0x89,0xa5,0x2b,0x79,0xb,0xd0,0x98,0x18,0x89,0xbc,0xca,0xbd,0x27,0x8,0x86,0x8,0x89,0xbc,0xcb,0xbd,0x28,0x18,0x86,0x18,0x89,0x89,0x47,0xd0,0x80,0x89,0x68,0x98,0xc,0x31,0xbe,0x0,0xf0,0xd1,0x80,0xe4,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0};
enum biwn_gpu_interior6ae0_status biwn_gpu_interior6ae0_prepare(struct biwn_gpu_interior6ae0_state *s,uint32_t scene,uint32_t sector){if(!s||s->z>1||s->c>1||s->n>1)return 1;memcpy(s->local_RAM+0x240,source_image,sizeof(source_image));put32(s->local_RAM+0x204,27360u);put32(s->local_RAM+0x20c,293768u);put32(s->local_RAM+0x210,0x49b8c);put32(s->local_RAM+0x214,scene);put32(s->local_RAM+0x218,sector);put32(s->local_RAM+0x21c,1103496u);s->pc=0xf03240;s->instructions=0;return 0;}
#define CHECK(e) do{int status=(e);if(status)return(enum biwn_gpu_interior6ae0_status)status;}while(0)
enum biwn_gpu_interior6ae0_status biwn_gpu_interior6ae0_run(struct biwn_gpu_interior6ae0_bus *bus,struct biwn_gpu_interior6ae0_state *state,uint32_t budget){struct biwn_gpu_interior6ae0_state s;uint32_t v,target=0;unsigned pending=0;if(!bus||!state||!budget||!bus->read16||!bus->read32||!bus->write16||!bus->write32||state->z>1||state->c>1||state->n>1)return 1;s=*state;while(budget--){unsigned delayed=pending;uint32_t resume=target;pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){
  case 0xf03240u: /* moveq   1,r0 */
   s.registers[0][0]=1u;
   s.pc=0xf03242u;break;
  case 0xf03242u: /* moveq   1,r1 */
   s.registers[0][1]=1u;
   s.pc=0xf03244u;break;
  case 0xf03244u: /* neg     r0 */
   s.registers[0][0]=sub(&s,0,s.registers[0][0]);
   s.pc=0xf03246u;break;
  case 0xf03246u: /* neg     r1 */
   s.registers[0][1]=sub(&s,0,s.registers[0][1]);
   s.pc=0xf03248u;break;
  case 0xf03248u: /* shrq    $10,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=s.registers[0][0]>>16;zn(&s,s.registers[0][0]);
   s.pc=0xf0324au;break;
  case 0xf0324au: /* shlq    $10,r1 */
   s.c=s.registers[0][1]>>31;s.registers[0][1]=s.registers[0][1]<<16;zn(&s,s.registers[0][1]);
   s.pc=0xf0324cu;break;
  case 0xf0324cu: /* movei   $f03214,r2 */
   s.registers[0][2]=0xf03214u;
   s.pc=0xf03252u;break;
  case 0xf03252u: /* load    (r2),r4 */
   CHECK(rd32(bus,&s,s.registers[0][2]&~3u,&v));s.registers[0][4]=v;
   s.pc=0xf03254u;break;
  case 0xf03254u: /* addq    $4,r2 */
   s.registers[0][2]=add(&s,s.registers[0][2],4u);
   s.pc=0xf03256u;break;
  case 0xf03256u: /* addq    $4,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],4u);
   s.pc=0xf03258u;break;
  case 0xf03258u: /* load    (r2),r16 */
   CHECK(rd32(bus,&s,s.registers[0][2]&~3u,&v));s.registers[0][16]=v;
   s.pc=0xf0325au;break;
  case 0xf0325au: /* load    (r4),r5 */
   CHECK(rd32(bus,&s,s.registers[0][4]&~3u,&v));s.registers[0][5]=v;
   s.pc=0xf0325cu;break;
  case 0xf0325cu: /* addq    $4,r2 */
   s.registers[0][2]=add(&s,s.registers[0][2],4u);
   s.pc=0xf0325eu;break;
  case 0xf0325eu: /* addq    $4,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],4u);
   s.pc=0xf03260u;break;
  case 0xf03260u: /* load    (r2),r3 */
   CHECK(rd32(bus,&s,s.registers[0][2]&~3u,&v));s.registers[0][3]=v;
   s.pc=0xf03262u;break;
  case 0xf03262u: /* load    (r4),r6 */
   CHECK(rd32(bus,&s,s.registers[0][4]&~3u,&v));s.registers[0][6]=v;
   s.pc=0xf03264u;break;
  case 0xf03264u: /* move    r3,r7 */
   s.registers[0][7]=s.registers[0][3];
   s.pc=0xf03266u;break;
  case 0xf03266u: /* moveq   24,r20 */
   s.registers[0][20]=24u;
   s.pc=0xf03268u;break;
  case 0xf03268u: /* move    r3,r8 */
   s.registers[0][8]=s.registers[0][3];
   s.pc=0xf0326au;break;
  case 0xf0326au: /* moveq   6,r21 */
   s.registers[0][21]=6u;
   s.pc=0xf0326cu;break;
  case 0xf0326cu: /* movei   $f0328e,r9 */
   s.registers[0][9]=0xf0328eu;
   s.pc=0xf03272u;break;
  case 0xf03272u: /* movei   $f032a0,r10 */
   s.registers[0][10]=0xf032a0u;
   s.pc=0xf03278u;break;
  case 0xf03278u: /* movei   $f032cc,r11 */
   s.registers[0][11]=0xf032ccu;
   s.pc=0xf0327eu;break;
  case 0xf0327eu: /* movei   $f032da,r12 */
   s.registers[0][12]=0xf032dau;
   s.pc=0xf03284u;break;
  case 0xf03284u: /* movei   $f032e2,r13 */
   s.registers[0][13]=0xf032e2u;
   s.pc=0xf0328au;break;
  case 0xf0328au: /* jump    (r11) */
   if(condition(&s,0)){pending=1;target=s.registers[0][11];}
   s.pc=0xf0328cu;break;
  case 0xf0328cu: /* bset    $f,r19 */
   s.registers[0][19]|=(1u<<15);
   zn(&s,s.registers[0][19]);
   s.pc=0xf0328eu;break;
  case 0xf0328eu: /* cmp     r7,r8 */
   (void)sub(&s,s.registers[0][8],s.registers[0][7]);
   s.pc=0xf03290u;break;
  case 0xf03290u: /* jump    z,(r13) */
   if(condition(&s,2)){pending=1;target=s.registers[0][13];}
   s.pc=0xf03292u;break;
  case 0xf03292u: /* addq    $4,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],4u);
   s.pc=0xf03294u;break;
  case 0xf03294u: /* load    (r7),r17 */
   CHECK(rd32(bus,&s,s.registers[0][7]&~3u,&v));s.registers[0][17]=v;
   s.pc=0xf03296u;break;
  case 0xf03296u: /* addq    $4,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],4u);
   s.pc=0xf03298u;break;
  case 0xf03298u: /* addq    $16,r17 */
   s.registers[0][17]=add(&s,s.registers[0][17],22u);
   s.pc=0xf0329au;break;
  case 0xf0329au: /* loadw   (r17),r18 */
   CHECK(loadw(bus,&s,s.registers[0][17],&v));s.registers[0][18]=v;
   s.pc=0xf0329cu;break;
  case 0xf0329cu: /* mult    r21,r18 */
   s.registers[0][18]=(s.registers[0][18]&0xffffu)*(s.registers[0][21]&0xffffu);
   zn(&s,s.registers[0][18]);
   s.pc=0xf0329eu;break;
  case 0xf0329eu: /* add     r6,r18 */
   s.registers[0][18]=add(&s,s.registers[0][18],s.registers[0][6]);
   s.pc=0xf032a0u;break;
  case 0xf032a0u: /* addq    $2,r18 */
   s.registers[0][18]=add(&s,s.registers[0][18],2u);
   s.pc=0xf032a2u;break;
  case 0xf032a2u: /* loadw   (r18),r19 */
   CHECK(loadw(bus,&s,s.registers[0][18],&v));s.registers[0][19]=v;
   s.pc=0xf032a4u;break;
  case 0xf032a4u: /* btst    $9,r19 */
   s.z=((~s.registers[0][19])>>9)&1u;
   s.pc=0xf032a6u;break;
  case 0xf032a6u: /* jr      nz,00F032B0 */
   if(condition(&s,1)){pending=1;target=0xf032b0u;}
   s.pc=0xf032a8u;break;
  case 0xf032a8u: /* subq    $2,r18 */
   s.registers[0][18]=sub(&s,s.registers[0][18],2u);
   s.pc=0xf032aau;break;
  case 0xf032aau: /* btst    $8,r19 */
   s.z=((~s.registers[0][19])>>8)&1u;
   s.pc=0xf032acu;break;
  case 0xf032acu: /* jump    z,(r12) */
   if(condition(&s,2)){pending=1;target=s.registers[0][12];}
   s.pc=0xf032aeu;break;
  case 0xf032aeu: /* nop */
   s.pc=0xf032b0u;break;
  case 0xf032b0u: /* addq    $4,r18 */
   s.registers[0][18]=add(&s,s.registers[0][18],4u);
   s.pc=0xf032b2u;break;
  case 0xf032b2u: /* loadw   (r18),r16 */
   CHECK(loadw(bus,&s,s.registers[0][18],&v));s.registers[0][16]=v;
   s.pc=0xf032b4u;break;
  case 0xf032b4u: /* subq    $4,r18 */
   s.registers[0][18]=sub(&s,s.registers[0][18],4u);
   s.pc=0xf032b6u;break;
  case 0xf032b6u: /* cmp     r0,r16 */
   (void)sub(&s,s.registers[0][16],s.registers[0][0]);
   s.pc=0xf032b8u;break;
  case 0xf032b8u: /* jump    z,(r12) */
   if(condition(&s,2)){pending=1;target=s.registers[0][12];}
   s.pc=0xf032bau;break;
  case 0xf032bau: /* move    r3,r14 */
   s.registers[0][14]=s.registers[0][3];
   s.pc=0xf032bcu;break;
  case 0xf032bcu: /* cmp     r14,r8 */
   (void)sub(&s,s.registers[0][8],s.registers[0][14]);
   s.pc=0xf032beu;break;
  case 0xf032beu: /* jump    z,(r11) */
   if(condition(&s,2)){pending=1;target=s.registers[0][11];}
   s.pc=0xf032c0u;break;
  case 0xf032c0u: /* nop */
   s.pc=0xf032c2u;break;
  case 0xf032c2u: /* load    (r14),r15 */
   CHECK(rd32(bus,&s,s.registers[0][14]&~3u,&v));s.registers[0][15]=v;
   s.pc=0xf032c4u;break;
  case 0xf032c4u: /* cmp     r15,r16 */
   (void)sub(&s,s.registers[0][16],s.registers[0][15]);
   s.pc=0xf032c6u;break;
  case 0xf032c6u: /* jr      nz,00F032BC */
   if(condition(&s,1)){pending=1;target=0xf032bcu;}
   s.pc=0xf032c8u;break;
  case 0xf032c8u: /* addq    $8,r14 */
   s.registers[0][14]=add(&s,s.registers[0][14],8u);
   s.pc=0xf032cau;break;
  case 0xf032cau: /* jump    (r12) */
   if(condition(&s,0)){pending=1;target=s.registers[0][12];}
   s.pc=0xf032ccu;break;
  case 0xf032ccu: /* move    r16,r17 */
   s.registers[0][17]=s.registers[0][16];
   s.pc=0xf032ceu;break;
  case 0xf032ceu: /* mult    r20,r17 */
   s.registers[0][17]=(s.registers[0][17]&0xffffu)*(s.registers[0][20]&0xffffu);
   zn(&s,s.registers[0][17]);
   s.pc=0xf032d0u;break;
  case 0xf032d0u: /* add     r5,r17 */
   s.registers[0][17]=add(&s,s.registers[0][17],s.registers[0][5]);
   s.pc=0xf032d2u;break;
  case 0xf032d2u: /* store   r16,(r8) */
   CHECK(wr32(bus,&s,local(s.registers[0][8])?(s.registers[0][8]&~3u):s.registers[0][8],s.registers[0][16]));
   s.pc=0xf032d4u;break;
  case 0xf032d4u: /* addq    $4,r8 */
   s.registers[0][8]=add(&s,s.registers[0][8],4u);
   s.pc=0xf032d6u;break;
  case 0xf032d6u: /* store   r17,(r8) */
   CHECK(wr32(bus,&s,local(s.registers[0][8])?(s.registers[0][8]&~3u):s.registers[0][8],s.registers[0][17]));
   s.pc=0xf032d8u;break;
  case 0xf032d8u: /* addq    $4,r8 */
   s.registers[0][8]=add(&s,s.registers[0][8],4u);
   s.pc=0xf032dau;break;
  case 0xf032dau: /* btst    $f,r19 */
   s.z=((~s.registers[0][19])>>15)&1u;
   s.pc=0xf032dcu;break;
  case 0xf032dcu: /* jump    z,(r10) */
   if(condition(&s,2)){pending=1;target=s.registers[0][10];}
   s.pc=0xf032deu;break;
  case 0xf032deu: /* add     r21,r18 */
   s.registers[0][18]=add(&s,s.registers[0][18],s.registers[0][21]);
   s.pc=0xf032e0u;break;
  case 0xf032e0u: /* jump    (r9) */
   if(condition(&s,0)){pending=1;target=s.registers[0][9];}
   s.pc=0xf032e2u;break;
  case 0xf032e2u: /* moveq   0,r15 */
   s.registers[0][15]=0u;
   s.pc=0xf032e4u;break;
  case 0xf032e4u: /* store   r0,(r8) */
   CHECK(wr32(bus,&s,local(s.registers[0][8])?(s.registers[0][8]&~3u):s.registers[0][8],s.registers[0][0]));
   s.pc=0xf032e6u;break;
  case 0xf032e6u: /* addq    $4,r8 */
   s.registers[0][8]=add(&s,s.registers[0][8],4u);
   s.pc=0xf032e8u;break;
  case 0xf032e8u: /* store   r15,(r8) */
   CHECK(wr32(bus,&s,local(s.registers[0][8])?(s.registers[0][8]&~3u):s.registers[0][8],s.registers[0][15]));
   s.pc=0xf032eau;break;
  case 0xf032eau: /* movei   $f0320c,r7 */
   s.registers[0][7]=0xf0320cu;
   s.pc=0xf032f0u;break;
  case 0xf032f0u: /* movei   $f034d0,r2 */
   s.registers[0][2]=0xf034d0u;
   s.pc=0xf032f6u;break;
  case 0xf032f6u: /* load    (r7),r8 */
   CHECK(rd32(bus,&s,s.registers[0][7]&~3u,&v));s.registers[0][8]=v;
   s.pc=0xf032f8u;break;
  case 0xf032f8u: /* moveq   9,r10 */
   s.registers[0][10]=9u;
   s.pc=0xf032fau;break;
  case 0xf032fau: /* addq    $4,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],4u);
   s.pc=0xf032fcu;break;
  case 0xf032fcu: /* loadw   (r8),r14 */
   CHECK(loadw(bus,&s,s.registers[0][8],&v));s.registers[0][14]=v;
   s.pc=0xf032feu;break;
  case 0xf032feu: /* shlq    $10,r14 */
   s.c=s.registers[0][14]>>31;s.registers[0][14]=s.registers[0][14]<<16;zn(&s,s.registers[0][14]);
   s.pc=0xf03300u;break;
  case 0xf03300u: /* sharq   $10,r14 */
   s.c=s.registers[0][14]&1u;s.registers[0][14]=sar(s.registers[0][14],16);zn(&s,s.registers[0][14]);
   s.pc=0xf03302u;break;
  case 0xf03302u: /* addq    $2,r8 */
   s.registers[0][8]=add(&s,s.registers[0][8],2u);
   s.pc=0xf03304u;break;
  case 0xf03304u: /* store   r14,(r2) */
   CHECK(wr32(bus,&s,local(s.registers[0][2])?(s.registers[0][2]&~3u):s.registers[0][2],s.registers[0][14]));
   s.pc=0xf03306u;break;
  case 0xf03306u: /* subq    $1,r10 */
   s.registers[0][10]=sub(&s,s.registers[0][10],1u);
   s.pc=0xf03308u;break;
  case 0xf03308u: /* jr      nz,00F032FC */
   if(condition(&s,1)){pending=1;target=0xf032fcu;}
   s.pc=0xf0330au;break;
  case 0xf0330au: /* addqt   $4,r2 */
   s.registers[0][2]+=4u;
   s.pc=0xf0330cu;break;
  case 0xf0330cu: /* load    (r7),r9 */
   CHECK(rd32(bus,&s,s.registers[0][7]&~3u,&v));s.registers[0][9]=v;
   s.pc=0xf0330eu;break;
  case 0xf0330eu: /* loadw   (r8),r11 */
   CHECK(loadw(bus,&s,s.registers[0][8],&v));s.registers[0][11]=v;
   s.pc=0xf03310u;break;
  case 0xf03310u: /* loadw   (r9),r3 */
   CHECK(loadw(bus,&s,s.registers[0][9],&v));s.registers[0][3]=v;
   s.pc=0xf03312u;break;
  case 0xf03312u: /* shlq    $10,r11 */
   s.c=s.registers[0][11]>>31;s.registers[0][11]=s.registers[0][11]<<16;zn(&s,s.registers[0][11]);
   s.pc=0xf03314u;break;
  case 0xf03314u: /* shlq    $10,r3 */
   s.c=s.registers[0][3]>>31;s.registers[0][3]=s.registers[0][3]<<16;zn(&s,s.registers[0][3]);
   s.pc=0xf03316u;break;
  case 0xf03316u: /* sharq   $10,r11 */
   s.c=s.registers[0][11]&1u;s.registers[0][11]=sar(s.registers[0][11],16);zn(&s,s.registers[0][11]);
   s.pc=0xf03318u;break;
  case 0xf03318u: /* sharq   $10,r3 */
   s.c=s.registers[0][3]&1u;s.registers[0][3]=sar(s.registers[0][3],16);zn(&s,s.registers[0][3]);
   s.pc=0xf0331au;break;
  case 0xf0331au: /* addq    $2,r8 */
   s.registers[0][8]=add(&s,s.registers[0][8],2u);
   s.pc=0xf0331cu;break;
  case 0xf0331cu: /* addq    $2,r9 */
   s.registers[0][9]=add(&s,s.registers[0][9],2u);
   s.pc=0xf0331eu;break;
  case 0xf0331eu: /* loadw   (r8),r12 */
   CHECK(loadw(bus,&s,s.registers[0][8],&v));s.registers[0][12]=v;
   s.pc=0xf03320u;break;
  case 0xf03320u: /* loadw   (r9),r4 */
   CHECK(loadw(bus,&s,s.registers[0][9],&v));s.registers[0][4]=v;
   s.pc=0xf03322u;break;
  case 0xf03322u: /* shlq    $10,r12 */
   s.c=s.registers[0][12]>>31;s.registers[0][12]=s.registers[0][12]<<16;zn(&s,s.registers[0][12]);
   s.pc=0xf03324u;break;
  case 0xf03324u: /* shlq    $10,r4 */
   s.c=s.registers[0][4]>>31;s.registers[0][4]=s.registers[0][4]<<16;zn(&s,s.registers[0][4]);
   s.pc=0xf03326u;break;
  case 0xf03326u: /* sharq   $10,r12 */
   s.c=s.registers[0][12]&1u;s.registers[0][12]=sar(s.registers[0][12],16);zn(&s,s.registers[0][12]);
   s.pc=0xf03328u;break;
  case 0xf03328u: /* sharq   $10,r4 */
   s.c=s.registers[0][4]&1u;s.registers[0][4]=sar(s.registers[0][4],16);zn(&s,s.registers[0][4]);
   s.pc=0xf0332au;break;
  case 0xf0332au: /* addq    $2,r8 */
   s.registers[0][8]=add(&s,s.registers[0][8],2u);
   s.pc=0xf0332cu;break;
  case 0xf0332cu: /* addq    $2,r9 */
   s.registers[0][9]=add(&s,s.registers[0][9],2u);
   s.pc=0xf0332eu;break;
  case 0xf0332eu: /* loadw   (r8),r13 */
   CHECK(loadw(bus,&s,s.registers[0][8],&v));s.registers[0][13]=v;
   s.pc=0xf03330u;break;
  case 0xf03330u: /* loadw   (r9),r5 */
   CHECK(loadw(bus,&s,s.registers[0][9],&v));s.registers[0][5]=v;
   s.pc=0xf03332u;break;
  case 0xf03332u: /* shlq    $10,r13 */
   s.c=s.registers[0][13]>>31;s.registers[0][13]=s.registers[0][13]<<16;zn(&s,s.registers[0][13]);
   s.pc=0xf03334u;break;
  case 0xf03334u: /* shlq    $10,r5 */
   s.c=s.registers[0][5]>>31;s.registers[0][5]=s.registers[0][5]<<16;zn(&s,s.registers[0][5]);
   s.pc=0xf03336u;break;
  case 0xf03336u: /* sharq   $10,r13 */
   s.c=s.registers[0][13]&1u;s.registers[0][13]=sar(s.registers[0][13],16);zn(&s,s.registers[0][13]);
   s.pc=0xf03338u;break;
  case 0xf03338u: /* sharq   $10,r5 */
   s.c=s.registers[0][5]&1u;s.registers[0][5]=sar(s.registers[0][5],16);zn(&s,s.registers[0][5]);
   s.pc=0xf0333au;break;
  case 0xf0333au: /* add     r11,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],s.registers[0][11]);
   s.pc=0xf0333cu;break;
  case 0xf0333cu: /* add     r12,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],s.registers[0][12]);
   s.pc=0xf0333eu;break;
  case 0xf0333eu: /* add     r13,r5 */
   s.registers[0][5]=add(&s,s.registers[0][5],s.registers[0][13]);
   s.pc=0xf03340u;break;
  case 0xf03340u: /* subq    $c,r2 */
   s.registers[0][2]=sub(&s,s.registers[0][2],12u);
   s.pc=0xf03342u;break;
  case 0xf03342u: /* addq    $c,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],12u);
   s.pc=0xf03344u;break;
  case 0xf03344u: /* load    (r7),r6 */
   CHECK(rd32(bus,&s,s.registers[0][7]&~3u,&v));s.registers[0][6]=v;
   s.pc=0xf03346u;break;
  case 0xf03346u: /* addq    $4,r6 */
   s.registers[0][6]=add(&s,s.registers[0][6],4u);
   s.pc=0xf03348u;break;
  case 0xf03348u: /* movei   $f02104,r25 */
   s.registers[0][25]=0xf02104u;
   s.pc=0xf0334eu;break;
  case 0xf0334eu: /* movei   $3,r24 */
   s.registers[0][24]=0x3u;
   s.pc=0xf03354u;break;
  case 0xf03354u: /* store   r24,(r25) */
   CHECK(wr32(bus,&s,local(s.registers[0][25])?(s.registers[0][25]&~3u):s.registers[0][25],s.registers[0][24]));
   s.pc=0xf03356u;break;
  case 0xf03356u: /* movei   $400,r10 */
   s.registers[0][10]=0x400u;
   s.pc=0xf0335cu;break;
  case 0xf0335cu: /* movei   $ad,r7 */
   s.registers[0][7]=0xadu;
   s.pc=0xf03362u;break;
  case 0xf03362u: /* move    r10,r9 */
   s.registers[0][9]=s.registers[0][10];
   s.pc=0xf03364u;break;
  case 0xf03364u: /* movei   $6f,r8 */
   s.registers[0][8]=0x6fu;
   s.pc=0xf0336au;break;
  case 0xf0336au: /* neg     r9 */
   s.registers[0][9]=sub(&s,0,s.registers[0][9]);
   s.pc=0xf0336cu;break;
  case 0xf0336cu: /* movei   $f0340e,r11 */
   s.registers[0][11]=0xf0340eu;
   s.pc=0xf03372u;break;
  case 0xf03372u: /* movei   $f02108,r12 */
   s.registers[0][12]=0xf02108u;
   s.pc=0xf03378u;break;
  case 0xf03378u: /* movei   $40,r23 */
   s.registers[0][23]=0x40u;
   s.pc=0xf0337eu;break;
  case 0xf0337eu: /* load    (r6),r24 */
   CHECK(rd32(bus,&s,s.registers[0][6]&~3u,&v));s.registers[0][24]=v;
   s.pc=0xf03380u;break;
  case 0xf03380u: /* movei   $f0346e,r22 */
   s.registers[0][22]=0xf0346eu;
   s.pc=0xf03386u;break;
  case 0xf03386u: /* cmpq    $0,r24 */
   (void)sub(&s,s.registers[0][24],0x0u);
   s.pc=0xf03388u;break;
  case 0xf03388u: /* jump    z,(r22) */
   if(condition(&s,2)){pending=1;target=s.registers[0][22];}
   s.pc=0xf0338au;break;
  case 0xf0338au: /* addq    $2,r24 */
   s.registers[0][24]=add(&s,s.registers[0][24],2u);
   s.pc=0xf0338cu;break;
  case 0xf0338cu: /* moveq   0,r14 */
   s.registers[0][14]=0u;
   s.pc=0xf0338eu;break;
  case 0xf0338eu: /* loadw   (r24),r13 */
   CHECK(loadw(bus,&s,s.registers[0][24],&v));s.registers[0][13]=v;
   s.pc=0xf03390u;break;
  case 0xf03390u: /* mult    r23,r14 */
   s.registers[0][14]=(s.registers[0][14]&0xffffu)*(s.registers[0][23]&0xffffu);
   zn(&s,s.registers[0][14]);
   s.pc=0xf03392u;break;
  case 0xf03392u: /* addq    $2,r24 */
   s.registers[0][24]=add(&s,s.registers[0][24],2u);
   s.pc=0xf03394u;break;
  case 0xf03394u: /* sub     r4,r14 */
   s.registers[0][14]=sub(&s,s.registers[0][14],s.registers[0][4]);
   s.pc=0xf03396u;break;
  case 0xf03396u: /* loadw   (r24),r15 */
   CHECK(loadw(bus,&s,s.registers[0][24],&v));s.registers[0][15]=v;
   s.pc=0xf03398u;break;
  case 0xf03398u: /* mult    r23,r13 */
   s.registers[0][13]=(s.registers[0][13]&0xffffu)*(s.registers[0][23]&0xffffu);
   zn(&s,s.registers[0][13]);
   s.pc=0xf0339au;break;
  case 0xf0339au: /* addq    $2,r24 */
   s.registers[0][24]=add(&s,s.registers[0][24],2u);
   s.pc=0xf0339cu;break;
  case 0xf0339cu: /* sub     r3,r13 */
   s.registers[0][13]=sub(&s,s.registers[0][13],s.registers[0][3]);
   s.pc=0xf0339eu;break;
  case 0xf0339eu: /* loadw   (r24),r16 */
   CHECK(loadw(bus,&s,s.registers[0][24],&v));s.registers[0][16]=v;
   s.pc=0xf033a0u;break;
  case 0xf033a0u: /* mult    r23,r15 */
   s.registers[0][15]=(s.registers[0][15]&0xffffu)*(s.registers[0][23]&0xffffu);
   zn(&s,s.registers[0][15]);
   s.pc=0xf033a2u;break;
  case 0xf033a2u: /* addq    $2,r24 */
   s.registers[0][24]=add(&s,s.registers[0][24],2u);
   s.pc=0xf033a4u;break;
  case 0xf033a4u: /* sub     r5,r15 */
   s.registers[0][15]=sub(&s,s.registers[0][15],s.registers[0][5]);
   s.pc=0xf033a6u;break;
  case 0xf033a6u: /* loadw   (r24),r17 */
   CHECK(loadw(bus,&s,s.registers[0][24],&v));s.registers[0][17]=v;
   s.pc=0xf033a8u;break;
  case 0xf033a8u: /* mult    r23,r16 */
   s.registers[0][16]=(s.registers[0][16]&0xffffu)*(s.registers[0][23]&0xffffu);
   zn(&s,s.registers[0][16]);
   s.pc=0xf033aau;break;
  case 0xf033aau: /* mult    r23,r17 */
   s.registers[0][17]=(s.registers[0][17]&0xffffu)*(s.registers[0][23]&0xffffu);
   zn(&s,s.registers[0][17]);
   s.pc=0xf033acu;break;
  case 0xf033acu: /* move    r0,r18 */
   s.registers[0][18]=s.registers[0][0];
   s.pc=0xf033aeu;break;
  case 0xf033aeu: /* move    r1,r19 */
   s.registers[0][19]=s.registers[0][1];
   s.pc=0xf033b0u;break;
  case 0xf033b0u: /* move    r0,r20 */
   s.registers[0][20]=s.registers[0][0];
   s.pc=0xf033b2u;break;
  case 0xf033b2u: /* move    r1,r21 */
   s.registers[0][21]=s.registers[0][1];
   s.pc=0xf033b4u;break;
  case 0xf033b4u: /* move    pc,r22 */
   s.registers[0][22]=0xf033b4u;
   s.pc=0xf033b6u;break;
  case 0xf033b6u: /* shlq    $10,r14 */
   s.c=s.registers[0][14]>>31;s.registers[0][14]=s.registers[0][14]<<16;zn(&s,s.registers[0][14]);
   s.pc=0xf033b8u;break;
  case 0xf033b8u: /* addq    $6,r22 */
   s.registers[0][22]=add(&s,s.registers[0][22],6u);
   s.pc=0xf033bau;break;
  case 0xf033bau: /* moveq   0,r24 */
   s.registers[0][24]=0u;
   s.pc=0xf033bcu;break;
  case 0xf033bcu: /* move    r17,r25 */
   s.registers[0][25]=s.registers[0][17];
   s.pc=0xf033beu;break;
  case 0xf033beu: /* jump    (r11) */
   if(condition(&s,0)){pending=1;target=s.registers[0][11];}
   s.pc=0xf033c0u;break;
  case 0xf033c0u: /* addq    $8,r22 */
   s.registers[0][22]=add(&s,s.registers[0][22],8u);
   s.pc=0xf033c2u;break;
  case 0xf033c2u: /* move    r16,r24 */
   s.registers[0][24]=s.registers[0][16];
   s.pc=0xf033c4u;break;
  case 0xf033c4u: /* move    r17,r25 */
   s.registers[0][25]=s.registers[0][17];
   s.pc=0xf033c6u;break;
  case 0xf033c6u: /* jump    (r11) */
   if(condition(&s,0)){pending=1;target=s.registers[0][11];}
   s.pc=0xf033c8u;break;
  case 0xf033c8u: /* addq    $8,r22 */
   s.registers[0][22]=add(&s,s.registers[0][22],8u);
   s.pc=0xf033cau;break;
  case 0xf033cau: /* move    r16,r24 */
   s.registers[0][24]=s.registers[0][16];
   s.pc=0xf033ccu;break;
  case 0xf033ccu: /* moveq   0,r25 */
   s.registers[0][25]=0u;
   s.pc=0xf033ceu;break;
  case 0xf033ceu: /* jump    (r11) */
   if(condition(&s,0)){pending=1;target=s.registers[0][11];}
   s.pc=0xf033d0u;break;
  case 0xf033d0u: /* addq    $8,r22 */
   s.registers[0][22]=add(&s,s.registers[0][22],8u);
   s.pc=0xf033d2u;break;
  case 0xf033d2u: /* moveq   0,r24 */
   s.registers[0][24]=0u;
   s.pc=0xf033d4u;break;
  case 0xf033d4u: /* moveq   0,r25 */
   s.registers[0][25]=0u;
   s.pc=0xf033d6u;break;
  case 0xf033d6u: /* jump    (r11) */
   if(condition(&s,0)){pending=1;target=s.registers[0][11];}
   s.pc=0xf033d8u;break;
  case 0xf033d8u: /* addq    $8,r22 */
   s.registers[0][22]=add(&s,s.registers[0][22],8u);
   s.pc=0xf033dau;break;
  case 0xf033dau: /* moveq   0,r24 */
   s.registers[0][24]=0u;
   s.pc=0xf033dcu;break;
  case 0xf033dcu: /* movei   $e0,r25 */
   s.registers[0][25]=0xe0u;
   s.pc=0xf033e2u;break;
  case 0xf033e2u: /* cmp     r24,r19 */
   (void)sub(&s,s.registers[0][19],s.registers[0][24]);
   s.pc=0xf033e4u;break;
  case 0xf033e4u: /* jr      n,00F03400 */
   if(condition(&s,24)){pending=1;target=0xf03400u;}
   s.pc=0xf033e6u;break;
  case 0xf033e6u: /* cmp     r18,r25 */
   (void)sub(&s,s.registers[0][25],s.registers[0][18]);
   s.pc=0xf033e8u;break;
  case 0xf033e8u: /* jr      n,00F03400 */
   if(condition(&s,24)){pending=1;target=0xf03400u;}
   s.pc=0xf033eau;break;
  case 0xf033eau: /* moveq   31,r24 */
   s.registers[0][24]=31u;
   s.pc=0xf033ecu;break;
  case 0xf033ecu: /* movei   $300,r25 */
   s.registers[0][25]=0x300u;
   s.pc=0xf033f2u;break;
  case 0xf033f2u: /* cmp     r24,r21 */
   (void)sub(&s,s.registers[0][21],s.registers[0][24]);
   s.pc=0xf033f4u;break;
  case 0xf033f4u: /* jr      n,00F03400 */
   if(condition(&s,24)){pending=1;target=0xf03400u;}
   s.pc=0xf033f6u;break;
  case 0xf033f6u: /* cmp     r20,r25 */
   (void)sub(&s,s.registers[0][25],s.registers[0][20]);
   s.pc=0xf033f8u;break;
  case 0xf033f8u: /* jr      n,00F03400 */
   if(condition(&s,24)){pending=1;target=0xf03400u;}
   s.pc=0xf033fau;break;
  case 0xf033fau: /* nop */
   s.pc=0xf033fcu;break;
  case 0xf033fcu: /* jr      00F03402 */
   if(condition(&s,0)){pending=1;target=0xf03402u;}
   s.pc=0xf033feu;break;
  case 0xf033feu: /* nop */
   s.pc=0xf03400u;break;
  case 0xf03400u: /* moveq   0,r21 */
   s.registers[0][21]=0u;
   s.pc=0xf03402u;break;
  case 0xf03402u: /* movei   $f0337e,r22 */
   s.registers[0][22]=0xf0337eu;
   s.pc=0xf03408u;break;
  case 0xf03408u: /* store   r21,(r6) */
   CHECK(wr32(bus,&s,local(s.registers[0][6])?(s.registers[0][6]&~3u):s.registers[0][6],s.registers[0][21]));
   s.pc=0xf0340au;break;
  case 0xf0340au: /* jump    (r22) */
   if(condition(&s,0)){pending=1;target=s.registers[0][22];}
   s.pc=0xf0340cu;break;
  case 0xf0340cu: /* addq    $8,r6 */
   s.registers[0][6]=add(&s,s.registers[0][6],8u);
   s.pc=0xf0340eu;break;
  case 0xf0340eu: /* add     r13,r24 */
   s.registers[0][24]=add(&s,s.registers[0][24],s.registers[0][13]);
   s.pc=0xf03410u;break;
  case 0xf03410u: /* add     r15,r25 */
   s.registers[0][25]=add(&s,s.registers[0][25],s.registers[0][15]);
   s.pc=0xf03412u;break;
  case 0xf03412u: /* and     r0,r24 */
   s.registers[0][24]&=s.registers[0][0];
   zn(&s,s.registers[0][24]);
   s.pc=0xf03414u;break;
  case 0xf03414u: /* and     r0,r25 */
   s.registers[0][25]&=s.registers[0][0];
   zn(&s,s.registers[0][25]);
   s.pc=0xf03416u;break;
  case 0xf03416u: /* or      r14,r24 */
   s.registers[0][24]|=s.registers[0][14];
   zn(&s,s.registers[0][24]);
   s.pc=0xf03418u;break;
  case 0xf03418u: /* subq    $18,r2 */
   s.registers[0][2]=sub(&s,s.registers[0][2],24u);
   s.pc=0xf0341au;break;
  case 0xf0341au: /* store   r2,(r12) */
   CHECK(wr32(bus,&s,local(s.registers[0][12])?(s.registers[0][12]&~3u):s.registers[0][12],s.registers[0][2]));
   s.pc=0xf0341cu;break;
  case 0xf0341cu: /* moveta  r24,r24 */
   s.registers[1][24]=s.registers[0][24];
   s.pc=0xf0341eu;break;
  case 0xf0341eu: /* moveta  r25,r25 */
   s.registers[1][25]=s.registers[0][25];
   s.pc=0xf03420u;break;
  case 0xf03420u: /* mmult   r24,r26 */
   CHECK(matrix(bus,&s,24,26));
   s.pc=0xf03422u;break;
  case 0xf03422u: /* addq    $18,r2 */
   s.registers[0][2]=add(&s,s.registers[0][2],24u);
   s.pc=0xf03424u;break;
  case 0xf03424u: /* store   r2,(r12) */
   CHECK(wr32(bus,&s,local(s.registers[0][12])?(s.registers[0][12]&~3u):s.registers[0][12],s.registers[0][2]));
   s.pc=0xf03426u;break;
  case 0xf03426u: /* moveta  r24,r24 */
   s.registers[1][24]=s.registers[0][24];
   s.pc=0xf03428u;break;
  case 0xf03428u: /* moveta  r25,r25 */
   s.registers[1][25]=s.registers[0][25];
   s.pc=0xf0342au;break;
  case 0xf0342au: /* mmult   r24,r27 */
   CHECK(matrix(bus,&s,24,27));
   s.pc=0xf0342cu;break;
  case 0xf0342cu: /* sharq   $e,r26 */
   s.c=s.registers[0][26]&1u;s.registers[0][26]=sar(s.registers[0][26],14);zn(&s,s.registers[0][26]);
   s.pc=0xf0342eu;break;
  case 0xf0342eu: /* sharq   $e,r27 */
   s.c=s.registers[0][27]&1u;s.registers[0][27]=sar(s.registers[0][27],14);zn(&s,s.registers[0][27]);
   s.pc=0xf03430u;break;
  case 0xf03430u: /* imult   r7,r26 */
   s.registers[0][26]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][26])*(int32_t)sx16(s.registers[0][7]));
   zn(&s,s.registers[0][26]);
   s.pc=0xf03432u;break;
  case 0xf03432u: /* cmpq    $1,r27 */
   (void)sub(&s,s.registers[0][27],0x1u);
   s.pc=0xf03434u;break;
  case 0xf03434u: /* jr      nn,00F0343A */
   if(condition(&s,20)){pending=1;target=0xf0343au;}
   s.pc=0xf03436u;break;
  case 0xf03436u: /* nop */
   s.pc=0xf03438u;break;
  case 0xf03438u: /* moveq   8,r27 */
   s.registers[0][27]=8u;
   s.pc=0xf0343au;break;
  case 0xf0343au: /* abs     r26 */
   s.c=s.registers[0][26]>>31;if(s.registers[0][26]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[0][26]=0u-s.registers[0][26];s.n=0;s.z=s.registers[0][26]==0;}
   s.pc=0xf0343cu;break;
  case 0xf0343cu: /* jr      nc,00F03442 */
   if(condition(&s,4)){pending=1;target=0xf03442u;}
   s.pc=0xf0343eu;break;
  case 0xf0343eu: /* div     r27,r26 */
   divide(&s,27,26);
   s.pc=0xf03440u;break;
  case 0xf03440u: /* neg     r26 */
   s.registers[0][26]=sub(&s,0,s.registers[0][26]);
   s.pc=0xf03442u;break;
  case 0xf03442u: /* cmp     r26,r9 */
   (void)sub(&s,s.registers[0][9],s.registers[0][26]);
   s.pc=0xf03444u;break;
  case 0xf03444u: /* jr      n,00F0344A */
   if(condition(&s,24)){pending=1;target=0xf0344au;}
   s.pc=0xf03446u;break;
  case 0xf03446u: /* cmp     r10,r26 */
   (void)sub(&s,s.registers[0][26],s.registers[0][10]);
   s.pc=0xf03448u;break;
  case 0xf03448u: /* move    r9,r26 */
   s.registers[0][26]=s.registers[0][9];
   s.pc=0xf0344au;break;
  case 0xf0344au: /* jr      n,00F03450 */
   if(condition(&s,24)){pending=1;target=0xf03450u;}
   s.pc=0xf0344cu;break;
  case 0xf0344cu: /* nop */
   s.pc=0xf0344eu;break;
  case 0xf0344eu: /* move    r10,r26 */
   s.registers[0][26]=s.registers[0][10];
   s.pc=0xf03450u;break;
  case 0xf03450u: /* add     r8,r26 */
   s.registers[0][26]=add(&s,s.registers[0][26],s.registers[0][8]);
   s.pc=0xf03452u;break;
  case 0xf03452u: /* cmp     r26,r18 */
   (void)sub(&s,s.registers[0][18],s.registers[0][26]);
   s.pc=0xf03454u;break;
  case 0xf03454u: /* jr      n,00F0345A */
   if(condition(&s,24)){pending=1;target=0xf0345au;}
   s.pc=0xf03456u;break;
  case 0xf03456u: /* cmp     r19,r26 */
   (void)sub(&s,s.registers[0][26],s.registers[0][19]);
   s.pc=0xf03458u;break;
  case 0xf03458u: /* move    r26,r18 */
   s.registers[0][18]=s.registers[0][26];
   s.pc=0xf0345au;break;
  case 0xf0345au: /* jr      n,00F03460 */
   if(condition(&s,24)){pending=1;target=0xf03460u;}
   s.pc=0xf0345cu;break;
  case 0xf0345cu: /* cmp     r27,r20 */
   (void)sub(&s,s.registers[0][20],s.registers[0][27]);
   s.pc=0xf0345eu;break;
  case 0xf0345eu: /* move    r26,r19 */
   s.registers[0][19]=s.registers[0][26];
   s.pc=0xf03460u;break;
  case 0xf03460u: /* jr      n,00F03466 */
   if(condition(&s,24)){pending=1;target=0xf03466u;}
   s.pc=0xf03462u;break;
  case 0xf03462u: /* cmp     r21,r27 */
   (void)sub(&s,s.registers[0][27],s.registers[0][21]);
   s.pc=0xf03464u;break;
  case 0xf03464u: /* move    r27,r20 */
   s.registers[0][20]=s.registers[0][27];
   s.pc=0xf03466u;break;
  case 0xf03466u: /* jump    n,(r22) */
   if(condition(&s,24)){pending=1;target=s.registers[0][22];}
   s.pc=0xf03468u;break;
  case 0xf03468u: /* nop */
   s.pc=0xf0346au;break;
  case 0xf0346au: /* jump    (r22) */
   if(condition(&s,0)){pending=1;target=s.registers[0][22];}
   s.pc=0xf0346cu;break;
  case 0xf0346cu: /* move    r27,r21 */
   s.registers[0][21]=s.registers[0][27];
   s.pc=0xf0346eu;break;
  case 0xf0346eu: /* movei   $f0321c,r2 */
   s.registers[0][2]=0xf0321cu;
   s.pc=0xf03474u;break;
  case 0xf03474u: /* load    (r2),r6 */
   CHECK(rd32(bus,&s,s.registers[0][2]&~3u,&v));s.registers[0][6]=v;
   s.pc=0xf03476u;break;
  case 0xf03476u: /* subq    $8,r6 */
   s.registers[0][6]=sub(&s,s.registers[0][6],8u);
   s.pc=0xf03478u;break;
  case 0xf03478u: /* movei   $f0348a,r3 */
   s.registers[0][3]=0xf0348au;
   s.pc=0xf0347eu;break;
  case 0xf0347eu: /* movei   $f0349a,r4 */
   s.registers[0][4]=0xf0349au;
   s.pc=0xf03484u;break;
  case 0xf03484u: /* movei   $f034c2,r5 */
   s.registers[0][5]=0xf034c2u;
   s.pc=0xf0348au;break;
  case 0xf0348au: /* addq    $8,r6 */
   s.registers[0][6]=add(&s,s.registers[0][6],8u);
   s.pc=0xf0348cu;break;
  case 0xf0348cu: /* load    (r6),r7 */
   CHECK(rd32(bus,&s,s.registers[0][6]&~3u,&v));s.registers[0][7]=v;
   s.pc=0xf0348eu;break;
  case 0xf0348eu: /* cmp     r0,r7 */
   (void)sub(&s,s.registers[0][7],s.registers[0][0]);
   s.pc=0xf03490u;break;
  case 0xf03490u: /* jump    z,(r5) */
   if(condition(&s,2)){pending=1;target=s.registers[0][5];}
   s.pc=0xf03492u;break;
  case 0xf03492u: /* addq    $4,r6 */
   s.registers[0][6]=add(&s,s.registers[0][6],4u);
   s.pc=0xf03494u;break;
  case 0xf03494u: /* load    (r6),r8 */
   CHECK(rd32(bus,&s,s.registers[0][6]&~3u,&v));s.registers[0][8]=v;
   s.pc=0xf03496u;break;
  case 0xf03496u: /* subq    $4,r6 */
   s.registers[0][6]=sub(&s,s.registers[0][6],4u);
   s.pc=0xf03498u;break;
  case 0xf03498u: /* move    r6,r9 */
   s.registers[0][9]=s.registers[0][6];
   s.pc=0xf0349au;break;
  case 0xf0349au: /* addq    $8,r9 */
   s.registers[0][9]=add(&s,s.registers[0][9],8u);
   s.pc=0xf0349cu;break;
  case 0xf0349cu: /* load    (r9),r10 */
   CHECK(rd32(bus,&s,s.registers[0][9]&~3u,&v));s.registers[0][10]=v;
   s.pc=0xf0349eu;break;
  case 0xf0349eu: /* cmp     r0,r10 */
   (void)sub(&s,s.registers[0][10],s.registers[0][0]);
   s.pc=0xf034a0u;break;
  case 0xf034a0u: /* jump    z,(r3) */
   if(condition(&s,2)){pending=1;target=s.registers[0][3];}
   s.pc=0xf034a2u;break;
  case 0xf034a2u: /* addq    $4,r9 */
   s.registers[0][9]=add(&s,s.registers[0][9],4u);
   s.pc=0xf034a4u;break;
  case 0xf034a4u: /* load    (r9),r11 */
   CHECK(rd32(bus,&s,s.registers[0][9]&~3u,&v));s.registers[0][11]=v;
   s.pc=0xf034a6u;break;
  case 0xf034a6u: /* cmp     r8,r11 */
   (void)sub(&s,s.registers[0][11],s.registers[0][8]);
   s.pc=0xf034a8u;break;
  case 0xf034a8u: /* jump    n,(r4) */
   if(condition(&s,24)){pending=1;target=s.registers[0][4];}
   s.pc=0xf034aau;break;
  case 0xf034aau: /* subq    $4,r9 */
   s.registers[0][9]=sub(&s,s.registers[0][9],4u);
   s.pc=0xf034acu;break;
  case 0xf034acu: /* store   r10,(r6) */
   CHECK(wr32(bus,&s,local(s.registers[0][6])?(s.registers[0][6]&~3u):s.registers[0][6],s.registers[0][10]));
   s.pc=0xf034aeu;break;
  case 0xf034aeu: /* store   r7,(r9) */
   CHECK(wr32(bus,&s,local(s.registers[0][9])?(s.registers[0][9]&~3u):s.registers[0][9],s.registers[0][7]));
   s.pc=0xf034b0u;break;
  case 0xf034b0u: /* addq    $4,r6 */
   s.registers[0][6]=add(&s,s.registers[0][6],4u);
   s.pc=0xf034b2u;break;
  case 0xf034b2u: /* addq    $4,r9 */
   s.registers[0][9]=add(&s,s.registers[0][9],4u);
   s.pc=0xf034b4u;break;
  case 0xf034b4u: /* store   r11,(r6) */
   CHECK(wr32(bus,&s,local(s.registers[0][6])?(s.registers[0][6]&~3u):s.registers[0][6],s.registers[0][11]));
   s.pc=0xf034b6u;break;
  case 0xf034b6u: /* store   r8,(r9) */
   CHECK(wr32(bus,&s,local(s.registers[0][9])?(s.registers[0][9]&~3u):s.registers[0][9],s.registers[0][8]));
   s.pc=0xf034b8u;break;
  case 0xf034b8u: /* subq    $4,r6 */
   s.registers[0][6]=sub(&s,s.registers[0][6],4u);
   s.pc=0xf034bau;break;
  case 0xf034bau: /* subq    $4,r9 */
   s.registers[0][9]=sub(&s,s.registers[0][9],4u);
   s.pc=0xf034bcu;break;
  case 0xf034bcu: /* move    r10,r7 */
   s.registers[0][7]=s.registers[0][10];
   s.pc=0xf034beu;break;
  case 0xf034beu: /* jump    (r4) */
   if(condition(&s,0)){pending=1;target=s.registers[0][4];}
   s.pc=0xf034c0u;break;
  case 0xf034c0u: /* move    r11,r8 */
   s.registers[0][8]=s.registers[0][11];
   s.pc=0xf034c2u;break;
  case 0xf034c2u: /* movei   $f031be,r12 */
   s.registers[0][12]=0xf031beu;
   s.pc=0xf034c8u;break;
  case 0xf034c8u: /* jump    (r12) */
   if(condition(&s,0)){pending=1;target=s.registers[0][12];}
   s.pc=0xf034cau;break;
  case 0xf034cau: /* nop */
   s.pc=0xf034ccu;break;
default:return BIWN_GPU_INTERIOR6AE0_BAD_PC;
 }if(delayed){if(pending)return BIWN_GPU_INTERIOR6AE0_BAD_DELAY;s.pc=resume;}if(s.pc==0xf031beu){*state=s;return BIWN_GPU_INTERIOR6AE0_OK;}}return BIWN_GPU_INTERIOR6AE0_WORK_LIMIT;}
