/* Generated from the pinned GPU52E0 overlay by
 * scripts/generate_biwn_gpu_projection.py. Analyst static recompilation,
 * not recovered original source. Integer primitive behavior is checked
 * against the pinned Virtual Jaguar core; no core runs on the C side. */
#include "biwn_gpu_projection.h"
#include <string.h>
static uint32_t sx16(uint32_t v){return(v&0x7fffu)-(v&0x8000u);}
static uint32_t sar(uint32_t v,unsigned n){return n>=32?((v&0x80000000u)?0xffffffffu:0):(v>>n)|((v&0x80000000u)?(0xffffffffu<<(32-n)):0);}
static void zn(struct biwn_gpu_projection_state *s,uint32_t v){s->z=v==0;s->n=v>>31;}
static uint32_t add(struct biwn_gpu_projection_state *s,uint32_t a,uint32_t b){uint32_t v=a+b;s->c=b>~a;zn(s,v);return v;}
static uint32_t sub(struct biwn_gpu_projection_state *s,uint32_t a,uint32_t b){uint32_t v=a-b;s->c=b>a;zn(s,v);return v;}
static int condition(struct biwn_gpu_projection_state *s,unsigned code){unsigned flags=s->z|(s->c<<1)|(s->n<<2);return !((code&1u)&&(flags&1u))&&!((code&2u)&&!(flags&1u))&&!((code&4u)&&(flags&(2u<<(code>>4))))&&!((code&8u)&&!(flags&(2u<<(code>>4))));}
static uint32_t be32(const uint8_t *p){return((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
static void put32(uint8_t *p,uint32_t v){p[0]=(uint8_t)(v>>24);p[1]=(uint8_t)(v>>16);p[2]=(uint8_t)(v>>8);p[3]=(uint8_t)v;}
static int local(uint32_t a){return a>=0xf03000u&&a<=0xf03ffcu;}
static int rd32(struct biwn_gpu_projection_bus *bus,struct biwn_gpu_projection_state *s,uint32_t a,uint32_t *v){if(local(a)){*v=be32(s->local_RAM+a-0xf03000u);return 0;}if(a==0xf02104u){*v=s->matrix_control;return 0;}if(a==0xf02108u){*v=s->matrix_pointer;return 0;}return bus->read32(bus->context,a,v)?2:0;}
static int rd16(struct biwn_gpu_projection_bus *bus,struct biwn_gpu_projection_state *s,uint32_t a,uint32_t *v){uint16_t h;if(a>=0xf03000u&&a<=0xf03ffeu){unsigned p=a-0xf03000u;*v=((uint32_t)s->local_RAM[p]<<8)|s->local_RAM[p+1];return 0;}if(bus->read16(bus->context,a,&h))return 2;*v=h;return 0;}
static int loadw(struct biwn_gpu_projection_bus *bus,struct biwn_gpu_projection_state *s,uint32_t a,uint32_t *v){if(a>=0xf03000u&&a<=0xf03fffu)return rd32(bus,s,a&~3u,v);return rd16(bus,s,a,v);}
static int wr32(struct biwn_gpu_projection_bus *bus,struct biwn_gpu_projection_state *s,uint32_t a,uint32_t v){if(local(a)){put32(s->local_RAM+a-0xf03000u,v);return 0;}if(a==0xf02104u){s->matrix_control=v;return 0;}if(a==0xf02108u){s->matrix_pointer=v&~3u;return 0;}return bus->write32(bus->context,a,v)?2:0;}
static int wr16(struct biwn_gpu_projection_bus *bus,struct biwn_gpu_projection_state *s,uint32_t a,uint32_t v){if(a>=0xf03000u&&a<=0xf03fffu)return wr32(bus,s,a&~1u,v&0xffffu);return bus->write16(bus->context,a,(uint16_t)v)?2:0;}
static void divide(struct biwn_gpu_projection_state *s,unsigned m,unsigned n){uint32_t q=s->registers[0][n],r=0,d=s->registers[0][m];unsigned i;if(s->division_control&1u){r=q>>16;q<<=16;}for(i=0;i<32;i++){uint32_t sign=r&0x80000000u;r=(r<<1)|(q>>31);r+=sign?d:0u-d;q=(q<<1)|((~r)>>31);}s->registers[0][n]=q;s->remainder=r;}
static int matrix(struct biwn_gpu_projection_bus *bus,struct biwn_gpu_projection_state *s,unsigned m,unsigned n){unsigned i,count=s->matrix_control&15u;uint32_t a=s->matrix_pointer,v;int64_t sum=0;for(i=0;i<count;i++){uint32_t packed=s->registers[1][m+(i>>1)];int32_t x=(int32_t)sx16(packed>>(i&1u?16:0));int status=rd16(bus,s,a+2,&v);if(status)return status;sum+=(int64_t)x*(int32_t)sx16(v);a+=(s->matrix_control&16u)?4u*count:4u;}s->registers[0][n]=(uint32_t)sum;zn(s,(uint32_t)sum);return 0;}
static const uint8_t source_image[1200]={
0x8c,0x20,0x8c,0x21,0x20,0x0,0x20,0x1,0x66,0x0,0x62,0x1,0x90,0x0,0x90,0x21,0x98,0x13,0x32,0xc,0x0,0xf0,0x98,0x3,
0x36,0x30,0x0,0xf0,0x98,0x4,0x36,0x60,0x0,0xf0,0x98,0x5,0x36,0x90,0x0,0xf0,0x98,0x6,0x36,0xc0,0x0,0xf0,0x90,0x69,
0x90,0x8a,0x90,0xab,0x90,0xcc,0xa6,0x62,0x8,0x93,0xa6,0x68,0x8,0x93,0xa6,0x69,0x8,0x93,0xa6,0x6a,0x8,0x93,0xa6,0x6b,
0x90,0x42,0x91,0x3,0x91,0x24,0x91,0x45,0x91,0x66,0x8d,0x87,0xa0,0x4c,0x62,0xc,0x8,0x42,0x6e,0xc,0x18,0x27,0xbc,0x6c,
0xd7,0x21,0xc,0x83,0x94,0x6c,0x8e,0x4d,0x91,0x8d,0x63,0xed,0x1,0xac,0x91,0x8e,0x98,0x12,0x33,0xca,0x0,0xf0,0x98,0x11,
0x34,0x14,0x0,0xf0,0x98,0x10,0x34,0x2e,0x0,0xf0,0x98,0xf,0x35,0x80,0x0,0xf0,0x98,0xe,0x35,0x84,0x0,0xf0,0x98,0xd,
0x33,0x42,0x0,0xf0,0x94,0xcc,0x92,0x50,0x92,0x31,0x92,0x12,0x91,0xf3,0x91,0xd4,0x91,0xb5,0x91,0x8f,0x98,0xe,0x0,0xe0,
0x0,0x0,0x98,0xd,0x0,0xb4,0x0,0x0,0x98,0xc,0x3,0x0,0x0,0x0,0x91,0xd6,0x91,0xb7,0x91,0x98,0x98,0x12,0x0,0xad,
0x0,0x0,0x98,0x11,0x0,0xad,0x0,0x0,0x98,0x10,0x0,0x6f,0x0,0x0,0x98,0xf,0x0,0x59,0x0,0x0,0x92,0x59,0x92,0x3a,
0x92,0x1b,0x91,0xfc,0x98,0xe,0xfc,0x0,0xff,0xff,0x98,0xd,0x4,0x0,0x0,0x0,0x91,0xdd,0x91,0xbe,0x98,0x1,0x21,0x4,
0x0,0xf0,0x98,0x0,0x0,0x3,0x0,0x0,0x98,0x6,0x21,0x8,0x0,0xf0,0xbc,0x20,0x94,0x89,0x95,0xac,0x95,0x4b,0x8d,0x2a,
0xa1,0x80,0x62,0x0,0x8,0x4c,0x6e,0x0,0x18,0x2a,0xbd,0x60,0xd7,0x21,0xc,0x8b,0x8d,0x20,0x95,0x2d,0x63,0xc0,0x8c,0x6a,
0x0,0xd,0xa1,0x81,0xa5,0xa0,0x62,0x1,0x8,0x4c,0x6e,0x1,0x8,0x8d,0x10,0x1,0x18,0x2a,0xbd,0x61,0xd6,0xc1,0xc,0x8b,
0x96,0x2,0x94,0xf,0x95,0x6e,0x95,0x2d,0x95,0x4c,0xcc,0x10,0xd0,0x40,0x8,0xd0,0x95,0x4c,0xcc,0x10,0xd0,0x40,0x8,0xd0,
0x95,0x4c,0xcc,0x10,0xd0,0x40,0x8,0xd0,0x8d,0x20,0x95,0x4d,0x63,0xc0,0x95,0x2c,0x0,0xd,0xcc,0x10,0xd0,0x40,0x8,0xd0,
0x95,0xac,0x95,0x6e,0x8d,0x8a,0xa5,0xc0,0x18,0x2a,0xc,0x8e,0xb9,0x80,0xd7,0x61,0xc,0x4c,0xc,0x4c,0xb9,0x83,0xc,0x4c,
0xb9,0x84,0x96,0x20,0xc,0x4c,0xd0,0x0,0xb9,0x85,0xa5,0xa7,0x8,0x8d,0x25,0xe7,0xa5,0xa0,0x8,0x8d,0x62,0x0,0xa5,0xa8,
0x28,0x7,0x8,0x8d,0x25,0xe8,0xbc,0xcc,0x90,0xe7,0x91,0x8,0xd8,0xe0,0x9,0x8c,0x88,0x3,0x6d,0xc0,0xbd,0xc0,0xbc,0xcc,
0x8,0x8e,0x90,0xe7,0x91,0x8,0xd8,0xe0,0x9,0x8c,0x88,0x4,0x6d,0xc0,0xbd,0xc0,0xbc,0xcc,0x8,0x8e,0x90,0xe7,0x91,0x8,
0xd8,0xe0,0x88,0x5,0x6d,0xc0,0xbd,0xc0,0xd2,0x0,0x8,0x8e,0x96,0x42,0x95,0xca,0x95,0x8b,0x94,0x13,0x94,0x34,0x8a,0x75,
0x8a,0x96,0x8a,0x77,0x8a,0x98,0x8c,0x39,0x8c,0x8c,0x20,0x19,0x8f,0xdb,0xa1,0x47,0x8,0x4a,0xa1,0x40,0x8,0x4a,0xa1,0x48,
0x62,0x0,0x8,0x4a,0x95,0x6d,0x28,0x7,0xbc,0xcd,0x90,0xe7,0x91,0x8,0xd8,0xee,0x9,0x8d,0x0,0x6e,0xbc,0xcd,0x6d,0xce,
0x90,0xe7,0x91,0x8,0xd8,0xef,0x9,0x8d,0x0,0x8f,0xbc,0xcd,0x6d,0xcf,0x90,0xe7,0x91,0x8,0xd8,0xf0,0x0,0xb0,0x6d,0xd0,
0x49,0xce,0x51,0xef,0x52,0x10,0x4c,0x1a,0x97,0x20,0x97,0x41,0x44,0xe,0x44,0x2f,0x7b,0x70,0xd4,0x54,0xe4,0x0,0x8b,0x70,
0x58,0xe,0xd4,0x44,0x56,0xe,0x20,0xe,0x58,0xf,0xd4,0x44,0x56,0xf,0x20,0xf,0x97,0xa0,0x97,0xc1,0x79,0xc0,0xd4,0x58,
0x79,0xe0,0x88,0xe,0xd4,0x58,0x78,0x2e,0x88,0xf,0xd4,0x58,0x78,0x2f,0x88,0x2e,0xd4,0x58,0xe4,0x0,0x88,0x2f,0x97,0x60,
0x97,0x81,0x0,0xe,0x0,0x2f,0xbd,0x6e,0x8,0x8b,0xbd,0x6f,0x8,0x8b,0xbd,0x70,0x19,0xb,0x7a,0x8f,0xd4,0x58,0x79,0xf3,
0x89,0xf4,0xd4,0x41,0xe4,0x0,0x79,0xd2,0xd4,0x98,0x79,0xd5,0x89,0xf3,0x89,0xd2,0x89,0x71,0xd4,0x58,0x7a,0xce,0x89,0xd5,
0xd4,0x58,0x7a,0x17,0x89,0xd6,0xd4,0x58,0x7b,0x10,0x8a,0x17,0xd4,0xf8,0xe4,0x0,0x8a,0x18,0xd4,0x61,0x7b,0x3a,0xd4,0x58,
0xe4,0x0,0x8b,0x59,0x18,0x2c,0xd0,0x41,0x9,0x8b,0x96,0x82,0x7a,0x93,0xd0,0x54,0x8f,0xe0,0x97,0x1,0x78,0x18,0xd0,0x58,
0x7a,0xe1,0xd0,0x58,0x8c,0x0,0x96,0xc1,0x78,0x16,0xd0,0x58,0x7a,0xa1,0xd0,0x58,0x8c,0x0,0x96,0xe1,0x78,0x14,0xd0,0x58,
0x7a,0x61,0xd0,0x58,0x8f,0xe0,0x96,0x62,0x78,0x17,0xd0,0x58,0x8e,0x0,0x95,0xa1,0x63,0xe0,0x0,0x1,0xa0,0x20,0x7c,0xe0,
0xd0,0x42,0x7d,0x0,0xd0,0x42,0x8a,0x3a,0x95,0x8a,0x8a,0x3b,0x19,0x9a,0x9,0x9b,0x19,0x8b,0x79,0x5a,0xd4,0x54,0xe4,0x0,
0x89,0x7a,0x7b,0x6b,0xd4,0x54,0xe4,0x0,0x89,0x5b,0xa7,0x4e,0xa7,0x60,0x8,0x9a,0x8,0x9b,0xa7,0x4f,0xa7,0x61,0x12,0x40,
0x12,0x61,0x11,0xd2,0x11,0xf3,0x44,0x13,0x44,0x32,0x7a,0x72,0xd4,0x78,0xe4,0x0,0xd4,0x40,0xe4,0x0,0x8c,0x19,0x95,0xa1,
0x95,0xe0,0xb,0x1,0x9,0x0,0xa0,0x30,0xbc,0x19,0x1b,0x1,0x90,0xf,0x63,0xb0,0x8,0x80,0x94,0xae,0xbc,0x10,0x1,0xc1,
0x95,0xcf,0x90,0x2d,0x1,0xcf,0x96,0xa0,0x18,0x29,0xd0,0x1,0x91,0xee,0x94,0xc6,0x8c,0x0,0x94,0x63,0xbc,0xc0,0x94,0xa4,
0x8,0x86,0x94,0x85,0xbc,0xc0,0x98,0x8,0x35,0xce,0x0,0xf0,0x18,0x86,0x8d,0x7,0x98,0x9,0x36,0x6,0x0,0xf0,0x7c,0x7,
0xd4,0x41,0x88,0xea,0xd1,0x20,0x88,0xeb,0x0,0xca,0xa5,0x4c,0x8f,0xe0,0x8,0x8a,0x78,0xc,0xd1,0x18,0xa5,0x47,0x88,0xcd,
0x8,0x8d,0xa5,0xaf,0x7c,0xf,0xd5,0x2,0x89,0xee,0x0,0xce,0xa5,0xd0,0x79,0x90,0xd4,0x78,0xe4,0x0,0xd6,0xa0,0x89,0xcd,
0xbd,0xab,0xd1,0x0,0xbd,0x4f,0x8,0x86,0xa4,0xc0,0x64,0x60,0x18,0x86,0xbc,0xc0,0x9,0x86,0xb,0x3,0xa4,0xc0,0x64,0x60,
0x9,0x6,0x18,0x25,0xb8,0x60,0xd7,0x41,0x0,0x83,0x98,0x2,0x31,0xbe,0x0,0xf0,0xd0,0x40,0xe4,0x0,0x0,0x0,0x0,0x0,
0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0
};
enum biwn_gpu_projection_status biwn_gpu_projection_prepare(struct biwn_gpu_projection_state *s,uint32_t count){if(!s||!count||s->z>1||s->c>1||s->n>1)return 1;memcpy(s->local_RAM+0x240,source_image,1200);put32(s->local_RAM+0x204,0x52e0);put32(s->local_RAM+0x20c,0x47b88);put32(s->local_RAM+0x210,0x47bc8);put32(s->local_RAM+0x214,count);put32(s->local_RAM+0x218,64);put32(s->local_RAM+0x21c,0x10a684);s->pc=0xf03240;s->instructions=0;return 0;}
#define CHECK(e) do{int status=(e);if(status)return(enum biwn_gpu_projection_status)status;}while(0)
enum biwn_gpu_projection_status biwn_gpu_projection_run(struct biwn_gpu_projection_bus *bus,struct biwn_gpu_projection_state *state,uint32_t budget){struct biwn_gpu_projection_state s;uint32_t v,target=0;unsigned pending=0;if(!bus||!state||!budget||!bus->read16||!bus->read32||!bus->write16||!bus->write32||state->z>1||state->c>1||state->n>1)return 1;s=*state;while(budget--){unsigned delayed=pending;uint32_t resume=target;pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){
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
  case 0xf0324cu: /* moveta  r0,r0 */
   s.registers[1][0]=s.registers[0][0];
   s.pc=0xf0324eu;break;
  case 0xf0324eu: /* moveta  r1,r1 */
   s.registers[1][1]=s.registers[0][1];
   s.pc=0xf03250u;break;
  case 0xf03250u: /* movei   $f0320c,r19 */
   s.registers[0][19]=0xf0320cu;
   s.pc=0xf03256u;break;
  case 0xf03256u: /* movei   $f03630,r3 */
   s.registers[0][3]=0xf03630u;
   s.pc=0xf0325cu;break;
  case 0xf0325cu: /* movei   $f03660,r4 */
   s.registers[0][4]=0xf03660u;
   s.pc=0xf03262u;break;
  case 0xf03262u: /* movei   $f03690,r5 */
   s.registers[0][5]=0xf03690u;
   s.pc=0xf03268u;break;
  case 0xf03268u: /* movei   $f036c0,r6 */
   s.registers[0][6]=0xf036c0u;
   s.pc=0xf0326eu;break;
  case 0xf0326eu: /* moveta  r3,r9 */
   s.registers[1][9]=s.registers[0][3];
   s.pc=0xf03270u;break;
  case 0xf03270u: /* moveta  r4,r10 */
   s.registers[1][10]=s.registers[0][4];
   s.pc=0xf03272u;break;
  case 0xf03272u: /* moveta  r5,r11 */
   s.registers[1][11]=s.registers[0][5];
   s.pc=0xf03274u;break;
  case 0xf03274u: /* moveta  r6,r12 */
   s.registers[1][12]=s.registers[0][6];
   s.pc=0xf03276u;break;
  case 0xf03276u: /* load    (r19),r2 */
   CHECK(rd32(bus,&s,s.registers[0][19]&~3u,&v));s.registers[0][2]=v;
   s.pc=0xf03278u;break;
  case 0xf03278u: /* addq    $4,r19 */
   s.registers[0][19]=add(&s,s.registers[0][19],4u);
   s.pc=0xf0327au;break;
  case 0xf0327au: /* load    (r19),r8 */
   CHECK(rd32(bus,&s,s.registers[0][19]&~3u,&v));s.registers[0][8]=v;
   s.pc=0xf0327cu;break;
  case 0xf0327cu: /* addq    $4,r19 */
   s.registers[0][19]=add(&s,s.registers[0][19],4u);
   s.pc=0xf0327eu;break;
  case 0xf0327eu: /* load    (r19),r9 */
   CHECK(rd32(bus,&s,s.registers[0][19]&~3u,&v));s.registers[0][9]=v;
   s.pc=0xf03280u;break;
  case 0xf03280u: /* addq    $4,r19 */
   s.registers[0][19]=add(&s,s.registers[0][19],4u);
   s.pc=0xf03282u;break;
  case 0xf03282u: /* load    (r19),r10 */
   CHECK(rd32(bus,&s,s.registers[0][19]&~3u,&v));s.registers[0][10]=v;
   s.pc=0xf03284u;break;
  case 0xf03284u: /* addq    $4,r19 */
   s.registers[0][19]=add(&s,s.registers[0][19],4u);
   s.pc=0xf03286u;break;
  case 0xf03286u: /* load    (r19),r11 */
   CHECK(rd32(bus,&s,s.registers[0][19]&~3u,&v));s.registers[0][11]=v;
   s.pc=0xf03288u;break;
  case 0xf03288u: /* moveta  r2,r2 */
   s.registers[1][2]=s.registers[0][2];
   s.pc=0xf0328au;break;
  case 0xf0328au: /* moveta  r8,r3 */
   s.registers[1][3]=s.registers[0][8];
   s.pc=0xf0328cu;break;
  case 0xf0328cu: /* moveta  r9,r4 */
   s.registers[1][4]=s.registers[0][9];
   s.pc=0xf0328eu;break;
  case 0xf0328eu: /* moveta  r10,r5 */
   s.registers[1][5]=s.registers[0][10];
   s.pc=0xf03290u;break;
  case 0xf03290u: /* moveta  r11,r6 */
   s.registers[1][6]=s.registers[0][11];
   s.pc=0xf03292u;break;
  case 0xf03292u: /* moveq   12,r7 */
   s.registers[0][7]=12u;
   s.pc=0xf03294u;break;
  case 0xf03294u: /* loadw   (r2),r12 */
   CHECK(loadw(bus,&s,s.registers[0][2],&v));s.registers[0][12]=v;
   s.pc=0xf03296u;break;
  case 0xf03296u: /* shlq    $10,r12 */
   s.c=s.registers[0][12]>>31;s.registers[0][12]=s.registers[0][12]<<16;zn(&s,s.registers[0][12]);
   s.pc=0xf03298u;break;
  case 0xf03298u: /* addq    $2,r2 */
   s.registers[0][2]=add(&s,s.registers[0][2],2u);
   s.pc=0xf0329au;break;
  case 0xf0329au: /* sharq   $10,r12 */
   s.c=s.registers[0][12]&1u;s.registers[0][12]=sar(s.registers[0][12],16);zn(&s,s.registers[0][12]);
   s.pc=0xf0329cu;break;
  case 0xf0329cu: /* subq    $1,r7 */
   s.registers[0][7]=sub(&s,s.registers[0][7],1u);
   s.pc=0xf0329eu;break;
  case 0xf0329eu: /* store   r12,(r3) */
   CHECK(wr32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],s.registers[0][12]));
   s.pc=0xf032a0u;break;
  case 0xf032a0u: /* jr      nz,00F03294 */
   if(condition(&s,1)){pending=1;target=0xf03294u;}
   s.pc=0xf032a2u;break;
  case 0xf032a2u: /* addqt   $4,r3 */
   s.registers[0][3]+=4u;
   s.pc=0xf032a4u;break;
  case 0xf032a4u: /* movefa  r3,r12 */
   s.registers[0][12]=s.registers[1][3];
   s.pc=0xf032a6u;break;
  case 0xf032a6u: /* moveq   18,r13 */
   s.registers[0][13]=18u;
   s.pc=0xf032a8u;break;
  case 0xf032a8u: /* moveta  r12,r13 */
   s.registers[1][13]=s.registers[0][12];
   s.pc=0xf032aau;break;
  case 0xf032aau: /* shlq    $1,r13 */
   s.c=s.registers[0][13]>>31;s.registers[0][13]=s.registers[0][13]<<1;zn(&s,s.registers[0][13]);
   s.pc=0xf032acu;break;
  case 0xf032acu: /* add     r13,r12 */
   s.registers[0][12]=add(&s,s.registers[0][12],s.registers[0][13]);
   s.pc=0xf032aeu;break;
  case 0xf032aeu: /* moveta  r12,r14 */
   s.registers[1][14]=s.registers[0][12];
   s.pc=0xf032b0u;break;
  case 0xf032b0u: /* movei   $f033ca,r18 */
   s.registers[0][18]=0xf033cau;
   s.pc=0xf032b6u;break;
  case 0xf032b6u: /* movei   $f03414,r17 */
   s.registers[0][17]=0xf03414u;
   s.pc=0xf032bcu;break;
  case 0xf032bcu: /* movei   $f0342e,r16 */
   s.registers[0][16]=0xf0342eu;
   s.pc=0xf032c2u;break;
  case 0xf032c2u: /* movei   $f03580,r15 */
   s.registers[0][15]=0xf03580u;
   s.pc=0xf032c8u;break;
  case 0xf032c8u: /* movei   $f03584,r14 */
   s.registers[0][14]=0xf03584u;
   s.pc=0xf032ceu;break;
  case 0xf032ceu: /* movei   $f03342,r13 */
   s.registers[0][13]=0xf03342u;
   s.pc=0xf032d4u;break;
  case 0xf032d4u: /* movefa  r6,r12 */
   s.registers[0][12]=s.registers[1][6];
   s.pc=0xf032d6u;break;
  case 0xf032d6u: /* moveta  r18,r16 */
   s.registers[1][16]=s.registers[0][18];
   s.pc=0xf032d8u;break;
  case 0xf032d8u: /* moveta  r17,r17 */
   s.registers[1][17]=s.registers[0][17];
   s.pc=0xf032dau;break;
  case 0xf032dau: /* moveta  r16,r18 */
   s.registers[1][18]=s.registers[0][16];
   s.pc=0xf032dcu;break;
  case 0xf032dcu: /* moveta  r15,r19 */
   s.registers[1][19]=s.registers[0][15];
   s.pc=0xf032deu;break;
  case 0xf032deu: /* moveta  r14,r20 */
   s.registers[1][20]=s.registers[0][14];
   s.pc=0xf032e0u;break;
  case 0xf032e0u: /* moveta  r13,r21 */
   s.registers[1][21]=s.registers[0][13];
   s.pc=0xf032e2u;break;
  case 0xf032e2u: /* moveta  r12,r15 */
   s.registers[1][15]=s.registers[0][12];
   s.pc=0xf032e4u;break;
  case 0xf032e4u: /* movei   $e0,r14 */
   s.registers[0][14]=0xe0u;
   s.pc=0xf032eau;break;
  case 0xf032eau: /* movei   $b4,r13 */
   s.registers[0][13]=0xb4u;
   s.pc=0xf032f0u;break;
  case 0xf032f0u: /* movei   $300,r12 */
   s.registers[0][12]=0x300u;
   s.pc=0xf032f6u;break;
  case 0xf032f6u: /* moveta  r14,r22 */
   s.registers[1][22]=s.registers[0][14];
   s.pc=0xf032f8u;break;
  case 0xf032f8u: /* moveta  r13,r23 */
   s.registers[1][23]=s.registers[0][13];
   s.pc=0xf032fau;break;
  case 0xf032fau: /* moveta  r12,r24 */
   s.registers[1][24]=s.registers[0][12];
   s.pc=0xf032fcu;break;
  case 0xf032fcu: /* movei   $ad,r18 */
   s.registers[0][18]=0xadu;
   s.pc=0xf03302u;break;
  case 0xf03302u: /* movei   $ad,r17 */
   s.registers[0][17]=0xadu;
   s.pc=0xf03308u;break;
  case 0xf03308u: /* movei   $6f,r16 */
   s.registers[0][16]=0x6fu;
   s.pc=0xf0330eu;break;
  case 0xf0330eu: /* movei   $59,r15 */
   s.registers[0][15]=0x59u;
   s.pc=0xf03314u;break;
  case 0xf03314u: /* moveta  r18,r25 */
   s.registers[1][25]=s.registers[0][18];
   s.pc=0xf03316u;break;
  case 0xf03316u: /* moveta  r17,r26 */
   s.registers[1][26]=s.registers[0][17];
   s.pc=0xf03318u;break;
  case 0xf03318u: /* moveta  r16,r27 */
   s.registers[1][27]=s.registers[0][16];
   s.pc=0xf0331au;break;
  case 0xf0331au: /* moveta  r15,r28 */
   s.registers[1][28]=s.registers[0][15];
   s.pc=0xf0331cu;break;
  case 0xf0331cu: /* movei   $fffffc00,r14 */
   s.registers[0][14]=0xfffffc00u;
   s.pc=0xf03322u;break;
  case 0xf03322u: /* movei   $400,r13 */
   s.registers[0][13]=0x400u;
   s.pc=0xf03328u;break;
  case 0xf03328u: /* moveta  r14,r29 */
   s.registers[1][29]=s.registers[0][14];
   s.pc=0xf0332au;break;
  case 0xf0332au: /* moveta  r13,r30 */
   s.registers[1][30]=s.registers[0][13];
   s.pc=0xf0332cu;break;
  case 0xf0332cu: /* movei   $f02104,r1 */
   s.registers[0][1]=0xf02104u;
   s.pc=0xf03332u;break;
  case 0xf03332u: /* movei   $3,r0 */
   s.registers[0][0]=0x3u;
   s.pc=0xf03338u;break;
  case 0xf03338u: /* movei   $f02108,r6 */
   s.registers[0][6]=0xf02108u;
   s.pc=0xf0333eu;break;
  case 0xf0333eu: /* store   r0,(r1) */
   CHECK(wr32(bus,&s,local(s.registers[0][1])?(s.registers[0][1]&~3u):s.registers[0][1],s.registers[0][0]));
   s.pc=0xf03340u;break;
  case 0xf03340u: /* movefa  r4,r9 */
   s.registers[0][9]=s.registers[1][4];
   s.pc=0xf03342u;break;
  case 0xf03342u: /* movefa  r13,r12 */
   s.registers[0][12]=s.registers[1][13];
   s.pc=0xf03344u;break;
  case 0xf03344u: /* movefa  r10,r11 */
   s.registers[0][11]=s.registers[1][10];
   s.pc=0xf03346u;break;
  case 0xf03346u: /* moveq   9,r10 */
   s.registers[0][10]=9u;
   s.pc=0xf03348u;break;
  case 0xf03348u: /* loadw   (r12),r0 */
   CHECK(loadw(bus,&s,s.registers[0][12],&v));s.registers[0][0]=v;
   s.pc=0xf0334au;break;
  case 0xf0334au: /* shlq    $10,r0 */
   s.c=s.registers[0][0]>>31;s.registers[0][0]=s.registers[0][0]<<16;zn(&s,s.registers[0][0]);
   s.pc=0xf0334cu;break;
  case 0xf0334cu: /* addq    $2,r12 */
   s.registers[0][12]=add(&s,s.registers[0][12],2u);
   s.pc=0xf0334eu;break;
  case 0xf0334eu: /* sharq   $10,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],16);zn(&s,s.registers[0][0]);
   s.pc=0xf03350u;break;
  case 0xf03350u: /* subq    $1,r10 */
   s.registers[0][10]=sub(&s,s.registers[0][10],1u);
   s.pc=0xf03352u;break;
  case 0xf03352u: /* store   r0,(r11) */
   CHECK(wr32(bus,&s,local(s.registers[0][11])?(s.registers[0][11]&~3u):s.registers[0][11],s.registers[0][0]));
   s.pc=0xf03354u;break;
  case 0xf03354u: /* jr      nz,00F03348 */
   if(condition(&s,1)){pending=1;target=0xf03348u;}
   s.pc=0xf03356u;break;
  case 0xf03356u: /* addqt   $4,r11 */
   s.registers[0][11]+=4u;
   s.pc=0xf03358u;break;
  case 0xf03358u: /* moveq   9,r0 */
   s.registers[0][0]=9u;
   s.pc=0xf0335au;break;
  case 0xf0335au: /* movefa  r9,r13 */
   s.registers[0][13]=s.registers[1][9];
   s.pc=0xf0335cu;break;
  case 0xf0335cu: /* shlq    $2,r0 */
   s.c=s.registers[0][0]>>31;s.registers[0][0]=s.registers[0][0]<<2;zn(&s,s.registers[0][0]);
   s.pc=0xf0335eu;break;
  case 0xf0335eu: /* moveq   3,r10 */
   s.registers[0][10]=3u;
   s.pc=0xf03360u;break;
  case 0xf03360u: /* add     r0,r13 */
   s.registers[0][13]=add(&s,s.registers[0][13],s.registers[0][0]);
   s.pc=0xf03362u;break;
  case 0xf03362u: /* loadw   (r12),r1 */
   CHECK(loadw(bus,&s,s.registers[0][12],&v));s.registers[0][1]=v;
   s.pc=0xf03364u;break;
  case 0xf03364u: /* load    (r13),r0 */
   CHECK(rd32(bus,&s,s.registers[0][13]&~3u,&v));s.registers[0][0]=v;
   s.pc=0xf03366u;break;
  case 0xf03366u: /* shlq    $10,r1 */
   s.c=s.registers[0][1]>>31;s.registers[0][1]=s.registers[0][1]<<16;zn(&s,s.registers[0][1]);
   s.pc=0xf03368u;break;
  case 0xf03368u: /* addq    $2,r12 */
   s.registers[0][12]=add(&s,s.registers[0][12],2u);
   s.pc=0xf0336au;break;
  case 0xf0336au: /* sharq   $10,r1 */
   s.c=s.registers[0][1]&1u;s.registers[0][1]=sar(s.registers[0][1],16);zn(&s,s.registers[0][1]);
   s.pc=0xf0336cu;break;
  case 0xf0336cu: /* addq    $4,r13 */
   s.registers[0][13]=add(&s,s.registers[0][13],4u);
   s.pc=0xf0336eu;break;
  case 0xf0336eu: /* sub     r0,r1 */
   s.registers[0][1]=sub(&s,s.registers[0][1],s.registers[0][0]);
   s.pc=0xf03370u;break;
  case 0xf03370u: /* subq    $1,r10 */
   s.registers[0][10]=sub(&s,s.registers[0][10],1u);
   s.pc=0xf03372u;break;
  case 0xf03372u: /* store   r1,(r11) */
   CHECK(wr32(bus,&s,local(s.registers[0][11])?(s.registers[0][11]&~3u):s.registers[0][11],s.registers[0][1]));
   s.pc=0xf03374u;break;
  case 0xf03374u: /* jr      nz,00F03362 */
   if(condition(&s,1)){pending=1;target=0xf03362u;}
   s.pc=0xf03376u;break;
  case 0xf03376u: /* addqt   $4,r11 */
   s.registers[0][11]+=4u;
   s.pc=0xf03378u;break;
  case 0xf03378u: /* movefa  r16,r2 */
   s.registers[0][2]=s.registers[1][16];
   s.pc=0xf0337au;break;
  case 0xf0337au: /* movefa  r0,r15 */
   s.registers[0][15]=s.registers[1][0];
   s.pc=0xf0337cu;break;
  case 0xf0337cu: /* movefa  r11,r14 */
   s.registers[0][14]=s.registers[1][11];
   s.pc=0xf0337eu;break;
  case 0xf0337eu: /* movefa  r9,r13 */
   s.registers[0][13]=s.registers[1][9];
   s.pc=0xf03380u;break;
  case 0xf03380u: /* movefa  r10,r12 */
   s.registers[0][12]=s.registers[1][10];
   s.pc=0xf03382u;break;
  case 0xf03382u: /* move    pc,r16 */
   s.registers[0][16]=0xf03382u;
   s.pc=0xf03384u;break;
  case 0xf03384u: /* jump    (r2) */
   if(condition(&s,0)){pending=1;target=s.registers[0][2];}
   s.pc=0xf03386u;break;
  case 0xf03386u: /* addq    $6,r16 */
   s.registers[0][16]=add(&s,s.registers[0][16],6u);
   s.pc=0xf03388u;break;
  case 0xf03388u: /* movefa  r10,r12 */
   s.registers[0][12]=s.registers[1][10];
   s.pc=0xf0338au;break;
  case 0xf0338au: /* move    pc,r16 */
   s.registers[0][16]=0xf0338au;
   s.pc=0xf0338cu;break;
  case 0xf0338cu: /* jump    (r2) */
   if(condition(&s,0)){pending=1;target=s.registers[0][2];}
   s.pc=0xf0338eu;break;
  case 0xf0338eu: /* addq    $6,r16 */
   s.registers[0][16]=add(&s,s.registers[0][16],6u);
   s.pc=0xf03390u;break;
  case 0xf03390u: /* movefa  r10,r12 */
   s.registers[0][12]=s.registers[1][10];
   s.pc=0xf03392u;break;
  case 0xf03392u: /* move    pc,r16 */
   s.registers[0][16]=0xf03392u;
   s.pc=0xf03394u;break;
  case 0xf03394u: /* jump    (r2) */
   if(condition(&s,0)){pending=1;target=s.registers[0][2];}
   s.pc=0xf03396u;break;
  case 0xf03396u: /* addq    $6,r16 */
   s.registers[0][16]=add(&s,s.registers[0][16],6u);
   s.pc=0xf03398u;break;
  case 0xf03398u: /* moveq   9,r0 */
   s.registers[0][0]=9u;
   s.pc=0xf0339au;break;
  case 0xf0339au: /* movefa  r10,r13 */
   s.registers[0][13]=s.registers[1][10];
   s.pc=0xf0339cu;break;
  case 0xf0339cu: /* shlq    $2,r0 */
   s.c=s.registers[0][0]>>31;s.registers[0][0]=s.registers[0][0]<<2;zn(&s,s.registers[0][0]);
   s.pc=0xf0339eu;break;
  case 0xf0339eu: /* movefa  r9,r12 */
   s.registers[0][12]=s.registers[1][9];
   s.pc=0xf033a0u;break;
  case 0xf033a0u: /* add     r0,r13 */
   s.registers[0][13]=add(&s,s.registers[0][13],s.registers[0][0]);
   s.pc=0xf033a2u;break;
  case 0xf033a2u: /* move    pc,r16 */
   s.registers[0][16]=0xf033a2u;
   s.pc=0xf033a4u;break;
  case 0xf033a4u: /* jump    (r2) */
   if(condition(&s,0)){pending=1;target=s.registers[0][2];}
   s.pc=0xf033a6u;break;
  case 0xf033a6u: /* addq    $6,r16 */
   s.registers[0][16]=add(&s,s.registers[0][16],6u);
   s.pc=0xf033a8u;break;
  case 0xf033a8u: /* movefa  r13,r12 */
   s.registers[0][12]=s.registers[1][13];
   s.pc=0xf033aau;break;
  case 0xf033aau: /* movefa  r11,r14 */
   s.registers[0][14]=s.registers[1][11];
   s.pc=0xf033acu;break;
  case 0xf033acu: /* moveq   12,r10 */
   s.registers[0][10]=12u;
   s.pc=0xf033aeu;break;
  case 0xf033aeu: /* load    (r14),r0 */
   CHECK(rd32(bus,&s,s.registers[0][14]&~3u,&v));s.registers[0][0]=v;
   s.pc=0xf033b0u;break;
  case 0xf033b0u: /* subq    $1,r10 */
   s.registers[0][10]=sub(&s,s.registers[0][10],1u);
   s.pc=0xf033b2u;break;
  case 0xf033b2u: /* addqt   $4,r14 */
   s.registers[0][14]+=4u;
   s.pc=0xf033b4u;break;
  case 0xf033b4u: /* storew  r0,(r12) */
   CHECK(wr16(bus,&s,s.registers[0][12],s.registers[0][0]));
   s.pc=0xf033b6u;break;
  case 0xf033b6u: /* jr      nz,00F033AE */
   if(condition(&s,1)){pending=1;target=0xf033aeu;}
   s.pc=0xf033b8u;break;
  case 0xf033b8u: /* addqt   $2,r12 */
   s.registers[0][12]+=2u;
   s.pc=0xf033bau;break;
  case 0xf033bau: /* addqt   $2,r12 */
   s.registers[0][12]+=2u;
   s.pc=0xf033bcu;break;
  case 0xf033bcu: /* storew  r3,(r12) */
   CHECK(wr16(bus,&s,s.registers[0][12],s.registers[0][3]));
   s.pc=0xf033beu;break;
  case 0xf033beu: /* addqt   $2,r12 */
   s.registers[0][12]+=2u;
   s.pc=0xf033c0u;break;
  case 0xf033c0u: /* storew  r4,(r12) */
   CHECK(wr16(bus,&s,s.registers[0][12],s.registers[0][4]));
   s.pc=0xf033c2u;break;
  case 0xf033c2u: /* movefa  r17,r0 */
   s.registers[0][0]=s.registers[1][17];
   s.pc=0xf033c4u;break;
  case 0xf033c4u: /* addqt   $2,r12 */
   s.registers[0][12]+=2u;
   s.pc=0xf033c6u;break;
  case 0xf033c6u: /* jump    (r0) */
   if(condition(&s,0)){pending=1;target=s.registers[0][0];}
   s.pc=0xf033c8u;break;
  case 0xf033c8u: /* storew  r5,(r12) */
   CHECK(wr16(bus,&s,s.registers[0][12],s.registers[0][5]));
   s.pc=0xf033cau;break;
  case 0xf033cau: /* load    (r13),r7 */
   CHECK(rd32(bus,&s,s.registers[0][13]&~3u,&v));s.registers[0][7]=v;
   s.pc=0xf033ccu;break;
  case 0xf033ccu: /* addq    $4,r13 */
   s.registers[0][13]=add(&s,s.registers[0][13],4u);
   s.pc=0xf033ceu;break;
  case 0xf033ceu: /* and     r15,r7 */
   s.registers[0][7]&=s.registers[0][15];
   zn(&s,s.registers[0][7]);
   s.pc=0xf033d0u;break;
  case 0xf033d0u: /* load    (r13),r0 */
   CHECK(rd32(bus,&s,s.registers[0][13]&~3u,&v));s.registers[0][0]=v;
   s.pc=0xf033d2u;break;
  case 0xf033d2u: /* addq    $4,r13 */
   s.registers[0][13]=add(&s,s.registers[0][13],4u);
   s.pc=0xf033d4u;break;
  case 0xf033d4u: /* shlq    $10,r0 */
   s.c=s.registers[0][0]>>31;s.registers[0][0]=s.registers[0][0]<<16;zn(&s,s.registers[0][0]);
   s.pc=0xf033d6u;break;
  case 0xf033d6u: /* load    (r13),r8 */
   CHECK(rd32(bus,&s,s.registers[0][13]&~3u,&v));s.registers[0][8]=v;
   s.pc=0xf033d8u;break;
  case 0xf033d8u: /* or      r0,r7 */
   s.registers[0][7]|=s.registers[0][0];
   zn(&s,s.registers[0][7]);
   s.pc=0xf033dau;break;
  case 0xf033dau: /* addq    $4,r13 */
   s.registers[0][13]=add(&s,s.registers[0][13],4u);
   s.pc=0xf033dcu;break;
  case 0xf033dcu: /* and     r15,r8 */
   s.registers[0][8]&=s.registers[0][15];
   zn(&s,s.registers[0][8]);
   s.pc=0xf033deu;break;
  case 0xf033deu: /* store   r12,(r6) */
   CHECK(wr32(bus,&s,local(s.registers[0][6])?(s.registers[0][6]&~3u):s.registers[0][6],s.registers[0][12]));
   s.pc=0xf033e0u;break;
  case 0xf033e0u: /* moveta  r7,r7 */
   s.registers[1][7]=s.registers[0][7];
   s.pc=0xf033e2u;break;
  case 0xf033e2u: /* moveta  r8,r8 */
   s.registers[1][8]=s.registers[0][8];
   s.pc=0xf033e4u;break;
  case 0xf033e4u: /* mmult   r7,r0 */
   CHECK(matrix(bus,&s,7,0));
   s.pc=0xf033e6u;break;
  case 0xf033e6u: /* addq    $c,r12 */
   s.registers[0][12]=add(&s,s.registers[0][12],12u);
   s.pc=0xf033e8u;break;
  case 0xf033e8u: /* move    r0,r3 */
   s.registers[0][3]=s.registers[0][0];
   s.pc=0xf033eau;break;
  case 0xf033eau: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf033ecu;break;
  case 0xf033ecu: /* store   r0,(r14) */
   CHECK(wr32(bus,&s,local(s.registers[0][14])?(s.registers[0][14]&~3u):s.registers[0][14],s.registers[0][0]));
   s.pc=0xf033eeu;break;
  case 0xf033eeu: /* store   r12,(r6) */
   CHECK(wr32(bus,&s,local(s.registers[0][6])?(s.registers[0][6]&~3u):s.registers[0][6],s.registers[0][12]));
   s.pc=0xf033f0u;break;
  case 0xf033f0u: /* addq    $4,r14 */
   s.registers[0][14]=add(&s,s.registers[0][14],4u);
   s.pc=0xf033f2u;break;
  case 0xf033f2u: /* moveta  r7,r7 */
   s.registers[1][7]=s.registers[0][7];
   s.pc=0xf033f4u;break;
  case 0xf033f4u: /* moveta  r8,r8 */
   s.registers[1][8]=s.registers[0][8];
   s.pc=0xf033f6u;break;
  case 0xf033f6u: /* mmult   r7,r0 */
   CHECK(matrix(bus,&s,7,0));
   s.pc=0xf033f8u;break;
  case 0xf033f8u: /* addq    $c,r12 */
   s.registers[0][12]=add(&s,s.registers[0][12],12u);
   s.pc=0xf033fau;break;
  case 0xf033fau: /* move    r0,r4 */
   s.registers[0][4]=s.registers[0][0];
   s.pc=0xf033fcu;break;
  case 0xf033fcu: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf033feu;break;
  case 0xf033feu: /* store   r0,(r14) */
   CHECK(wr32(bus,&s,local(s.registers[0][14])?(s.registers[0][14]&~3u):s.registers[0][14],s.registers[0][0]));
   s.pc=0xf03400u;break;
  case 0xf03400u: /* store   r12,(r6) */
   CHECK(wr32(bus,&s,local(s.registers[0][6])?(s.registers[0][6]&~3u):s.registers[0][6],s.registers[0][12]));
   s.pc=0xf03402u;break;
  case 0xf03402u: /* addq    $4,r14 */
   s.registers[0][14]=add(&s,s.registers[0][14],4u);
   s.pc=0xf03404u;break;
  case 0xf03404u: /* moveta  r7,r7 */
   s.registers[1][7]=s.registers[0][7];
   s.pc=0xf03406u;break;
  case 0xf03406u: /* moveta  r8,r8 */
   s.registers[1][8]=s.registers[0][8];
   s.pc=0xf03408u;break;
  case 0xf03408u: /* mmult   r7,r0 */
   CHECK(matrix(bus,&s,7,0));
   s.pc=0xf0340au;break;
  case 0xf0340au: /* move    r0,r5 */
   s.registers[0][5]=s.registers[0][0];
   s.pc=0xf0340cu;break;
  case 0xf0340cu: /* sharq   $e,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=sar(s.registers[0][0],14);zn(&s,s.registers[0][0]);
   s.pc=0xf0340eu;break;
  case 0xf0340eu: /* store   r0,(r14) */
   CHECK(wr32(bus,&s,local(s.registers[0][14])?(s.registers[0][14]&~3u):s.registers[0][14],s.registers[0][0]));
   s.pc=0xf03410u;break;
  case 0xf03410u: /* jump    (r16) */
   if(condition(&s,0)){pending=1;target=s.registers[0][16];}
   s.pc=0xf03412u;break;
  case 0xf03412u: /* addq    $4,r14 */
   s.registers[0][14]=add(&s,s.registers[0][14],4u);
   s.pc=0xf03414u;break;
  case 0xf03414u: /* movefa  r18,r2 */
   s.registers[0][2]=s.registers[1][18];
   s.pc=0xf03416u;break;
  case 0xf03416u: /* movefa  r14,r10 */
   s.registers[0][10]=s.registers[1][14];
   s.pc=0xf03418u;break;
  case 0xf03418u: /* movefa  r12,r11 */
   s.registers[0][11]=s.registers[1][12];
   s.pc=0xf0341au;break;
  case 0xf0341au: /* movefa  r0,r19 */
   s.registers[0][19]=s.registers[1][0];
   s.pc=0xf0341cu;break;
  case 0xf0341cu: /* movefa  r1,r20 */
   s.registers[0][20]=s.registers[1][1];
   s.pc=0xf0341eu;break;
  case 0xf0341eu: /* move    r19,r21 */
   s.registers[0][21]=s.registers[0][19];
   s.pc=0xf03420u;break;
  case 0xf03420u: /* move    r20,r22 */
   s.registers[0][22]=s.registers[0][20];
   s.pc=0xf03422u;break;
  case 0xf03422u: /* move    r19,r23 */
   s.registers[0][23]=s.registers[0][19];
   s.pc=0xf03424u;break;
  case 0xf03424u: /* move    r20,r24 */
   s.registers[0][24]=s.registers[0][20];
   s.pc=0xf03426u;break;
  case 0xf03426u: /* moveq   1,r25 */
   s.registers[0][25]=1u;
   s.pc=0xf03428u;break;
  case 0xf03428u: /* moveq   4,r12 */
   s.registers[0][12]=4u;
   s.pc=0xf0342au;break;
  case 0xf0342au: /* neg     r25 */
   s.registers[0][25]=sub(&s,0,s.registers[0][25]);
   s.pc=0xf0342cu;break;
  case 0xf0342cu: /* moveq   30,r27 */
   s.registers[0][27]=30u;
   s.pc=0xf0342eu;break;
  case 0xf0342eu: /* loadw   (r10),r7 */
   CHECK(loadw(bus,&s,s.registers[0][10],&v));s.registers[0][7]=v;
   s.pc=0xf03430u;break;
  case 0xf03430u: /* addq    $2,r10 */
   s.registers[0][10]=add(&s,s.registers[0][10],2u);
   s.pc=0xf03432u;break;
  case 0xf03432u: /* loadw   (r10),r0 */
   CHECK(loadw(bus,&s,s.registers[0][10],&v));s.registers[0][0]=v;
   s.pc=0xf03434u;break;
  case 0xf03434u: /* addq    $2,r10 */
   s.registers[0][10]=add(&s,s.registers[0][10],2u);
   s.pc=0xf03436u;break;
  case 0xf03436u: /* loadw   (r10),r8 */
   CHECK(loadw(bus,&s,s.registers[0][10],&v));s.registers[0][8]=v;
   s.pc=0xf03438u;break;
  case 0xf03438u: /* shlq    $10,r0 */
   s.c=s.registers[0][0]>>31;s.registers[0][0]=s.registers[0][0]<<16;zn(&s,s.registers[0][0]);
   s.pc=0xf0343au;break;
  case 0xf0343au: /* addq    $2,r10 */
   s.registers[0][10]=add(&s,s.registers[0][10],2u);
   s.pc=0xf0343cu;break;
  case 0xf0343cu: /* movefa  r11,r13 */
   s.registers[0][13]=s.registers[1][11];
   s.pc=0xf0343eu;break;
  case 0xf0343eu: /* or      r0,r7 */
   s.registers[0][7]|=s.registers[0][0];
   zn(&s,s.registers[0][7]);
   s.pc=0xf03440u;break;
  case 0xf03440u: /* store   r13,(r6) */
   CHECK(wr32(bus,&s,local(s.registers[0][6])?(s.registers[0][6]&~3u):s.registers[0][6],s.registers[0][13]));
   s.pc=0xf03442u;break;
  case 0xf03442u: /* moveta  r7,r7 */
   s.registers[1][7]=s.registers[0][7];
   s.pc=0xf03444u;break;
  case 0xf03444u: /* moveta  r8,r8 */
   s.registers[1][8]=s.registers[0][8];
   s.pc=0xf03446u;break;
  case 0xf03446u: /* mmult   r7,r14 */
   CHECK(matrix(bus,&s,7,14));
   s.pc=0xf03448u;break;
  case 0xf03448u: /* addq    $c,r13 */
   s.registers[0][13]=add(&s,s.registers[0][13],12u);
   s.pc=0xf0344au;break;
  case 0xf0344au: /* add     r3,r14 */
   s.registers[0][14]=add(&s,s.registers[0][14],s.registers[0][3]);
   s.pc=0xf0344cu;break;
  case 0xf0344cu: /* store   r13,(r6) */
   CHECK(wr32(bus,&s,local(s.registers[0][6])?(s.registers[0][6]&~3u):s.registers[0][6],s.registers[0][13]));
   s.pc=0xf0344eu;break;
  case 0xf0344eu: /* sharq   $e,r14 */
   s.c=s.registers[0][14]&1u;s.registers[0][14]=sar(s.registers[0][14],14);zn(&s,s.registers[0][14]);
   s.pc=0xf03450u;break;
  case 0xf03450u: /* moveta  r7,r7 */
   s.registers[1][7]=s.registers[0][7];
   s.pc=0xf03452u;break;
  case 0xf03452u: /* moveta  r8,r8 */
   s.registers[1][8]=s.registers[0][8];
   s.pc=0xf03454u;break;
  case 0xf03454u: /* mmult   r7,r15 */
   CHECK(matrix(bus,&s,7,15));
   s.pc=0xf03456u;break;
  case 0xf03456u: /* addq    $c,r13 */
   s.registers[0][13]=add(&s,s.registers[0][13],12u);
   s.pc=0xf03458u;break;
  case 0xf03458u: /* add     r4,r15 */
   s.registers[0][15]=add(&s,s.registers[0][15],s.registers[0][4]);
   s.pc=0xf0345au;break;
  case 0xf0345au: /* store   r13,(r6) */
   CHECK(wr32(bus,&s,local(s.registers[0][6])?(s.registers[0][6]&~3u):s.registers[0][6],s.registers[0][13]));
   s.pc=0xf0345cu;break;
  case 0xf0345cu: /* sharq   $e,r15 */
   s.c=s.registers[0][15]&1u;s.registers[0][15]=sar(s.registers[0][15],14);zn(&s,s.registers[0][15]);
   s.pc=0xf0345eu;break;
  case 0xf0345eu: /* moveta  r7,r7 */
   s.registers[1][7]=s.registers[0][7];
   s.pc=0xf03460u;break;
  case 0xf03460u: /* moveta  r8,r8 */
   s.registers[1][8]=s.registers[0][8];
   s.pc=0xf03462u;break;
  case 0xf03462u: /* mmult   r7,r16 */
   CHECK(matrix(bus,&s,7,16));
   s.pc=0xf03464u;break;
  case 0xf03464u: /* add     r5,r16 */
   s.registers[0][16]=add(&s,s.registers[0][16],s.registers[0][5]);
   s.pc=0xf03466u;break;
  case 0xf03466u: /* sharq   $e,r16 */
   s.c=s.registers[0][16]&1u;s.registers[0][16]=sar(s.registers[0][16],14);zn(&s,s.registers[0][16]);
   s.pc=0xf03468u;break;
  case 0xf03468u: /* imultn  r14,r14 */
   s.accumulator=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][14])*(int32_t)sx16(s.registers[0][14]));
   zn(&s,s.accumulator);
   s.pc=0xf0346au;break;
  case 0xf0346au: /* imacn   r15,r15 */
   s.accumulator+=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][15])*(int32_t)sx16(s.registers[0][15]));
   s.pc=0xf0346cu;break;
  case 0xf0346cu: /* imacn   r16,r16 */
   s.accumulator+=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][16])*(int32_t)sx16(s.registers[0][16]));
   s.pc=0xf0346eu;break;
  case 0xf0346eu: /* resmac  r26 */
   s.registers[0][26]=s.accumulator;
   s.pc=0xf03470u;break;
  case 0xf03470u: /* movefa  r25,r0 */
   s.registers[0][0]=s.registers[1][25];
   s.pc=0xf03472u;break;
  case 0xf03472u: /* movefa  r26,r1 */
   s.registers[0][1]=s.registers[1][26];
   s.pc=0xf03474u;break;
  case 0xf03474u: /* imult   r0,r14 */
   s.registers[0][14]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][14])*(int32_t)sx16(s.registers[0][0]));
   zn(&s,s.registers[0][14]);
   s.pc=0xf03476u;break;
  case 0xf03476u: /* imult   r1,r15 */
   s.registers[0][15]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][15])*(int32_t)sx16(s.registers[0][1]));
   zn(&s,s.registers[0][15]);
   s.pc=0xf03478u;break;
  case 0xf03478u: /* cmp     r27,r16 */
   (void)sub(&s,s.registers[0][16],s.registers[0][27]);
   s.pc=0xf0347au;break;
  case 0xf0347au: /* jr      nn,00F03480 */
   if(condition(&s,20)){pending=1;target=0xf03480u;}
   s.pc=0xf0347cu;break;
  case 0xf0347cu: /* nop */
   s.pc=0xf0347eu;break;
  case 0xf0347eu: /* move    r27,r16 */
   s.registers[0][16]=s.registers[0][27];
   s.pc=0xf03480u;break;
  case 0xf03480u: /* abs     r14 */
   s.c=s.registers[0][14]>>31;if(s.registers[0][14]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[0][14]=0u-s.registers[0][14];s.n=0;s.z=s.registers[0][14]==0;}
   s.pc=0xf03482u;break;
  case 0xf03482u: /* jr      nc,00F03488 */
   if(condition(&s,4)){pending=1;target=0xf03488u;}
   s.pc=0xf03484u;break;
  case 0xf03484u: /* div     r16,r14 */
   divide(&s,16,14);
   s.pc=0xf03486u;break;
  case 0xf03486u: /* neg     r14 */
   s.registers[0][14]=sub(&s,0,s.registers[0][14]);
   s.pc=0xf03488u;break;
  case 0xf03488u: /* abs     r15 */
   s.c=s.registers[0][15]>>31;if(s.registers[0][15]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[0][15]=0u-s.registers[0][15];s.n=0;s.z=s.registers[0][15]==0;}
   s.pc=0xf0348au;break;
  case 0xf0348au: /* jr      nc,00F03490 */
   if(condition(&s,4)){pending=1;target=0xf03490u;}
   s.pc=0xf0348cu;break;
  case 0xf0348cu: /* div     r16,r15 */
   divide(&s,16,15);
   s.pc=0xf0348eu;break;
  case 0xf0348eu: /* neg     r15 */
   s.registers[0][15]=sub(&s,0,s.registers[0][15]);
   s.pc=0xf03490u;break;
  case 0xf03490u: /* movefa  r29,r0 */
   s.registers[0][0]=s.registers[1][29];
   s.pc=0xf03492u;break;
  case 0xf03492u: /* movefa  r30,r1 */
   s.registers[0][1]=s.registers[1][30];
   s.pc=0xf03494u;break;
  case 0xf03494u: /* cmp     r14,r0 */
   (void)sub(&s,s.registers[0][0],s.registers[0][14]);
   s.pc=0xf03496u;break;
  case 0xf03496u: /* jr      n,00F0349C */
   if(condition(&s,24)){pending=1;target=0xf0349cu;}
   s.pc=0xf03498u;break;
  case 0xf03498u: /* cmp     r15,r0 */
   (void)sub(&s,s.registers[0][0],s.registers[0][15]);
   s.pc=0xf0349au;break;
  case 0xf0349au: /* move    r0,r14 */
   s.registers[0][14]=s.registers[0][0];
   s.pc=0xf0349cu;break;
  case 0xf0349cu: /* jr      n,00F034A2 */
   if(condition(&s,24)){pending=1;target=0xf034a2u;}
   s.pc=0xf0349eu;break;
  case 0xf0349eu: /* cmp     r1,r14 */
   (void)sub(&s,s.registers[0][14],s.registers[0][1]);
   s.pc=0xf034a0u;break;
  case 0xf034a0u: /* move    r0,r15 */
   s.registers[0][15]=s.registers[0][0];
   s.pc=0xf034a2u;break;
  case 0xf034a2u: /* jr      n,00F034A8 */
   if(condition(&s,24)){pending=1;target=0xf034a8u;}
   s.pc=0xf034a4u;break;
  case 0xf034a4u: /* cmp     r1,r15 */
   (void)sub(&s,s.registers[0][15],s.registers[0][1]);
   s.pc=0xf034a6u;break;
  case 0xf034a6u: /* move    r1,r14 */
   s.registers[0][14]=s.registers[0][1];
   s.pc=0xf034a8u;break;
  case 0xf034a8u: /* jr      n,00F034AE */
   if(condition(&s,24)){pending=1;target=0xf034aeu;}
   s.pc=0xf034aau;break;
  case 0xf034aau: /* nop */
   s.pc=0xf034acu;break;
  case 0xf034acu: /* move    r1,r15 */
   s.registers[0][15]=s.registers[0][1];
   s.pc=0xf034aeu;break;
  case 0xf034aeu: /* movefa  r27,r0 */
   s.registers[0][0]=s.registers[1][27];
   s.pc=0xf034b0u;break;
  case 0xf034b0u: /* movefa  r28,r1 */
   s.registers[0][1]=s.registers[1][28];
   s.pc=0xf034b2u;break;
  case 0xf034b2u: /* add     r0,r14 */
   s.registers[0][14]=add(&s,s.registers[0][14],s.registers[0][0]);
   s.pc=0xf034b4u;break;
  case 0xf034b4u: /* add     r1,r15 */
   s.registers[0][15]=add(&s,s.registers[0][15],s.registers[0][1]);
   s.pc=0xf034b6u;break;
  case 0xf034b6u: /* store   r14,(r11) */
   CHECK(wr32(bus,&s,local(s.registers[0][11])?(s.registers[0][11]&~3u):s.registers[0][11],s.registers[0][14]));
   s.pc=0xf034b8u;break;
  case 0xf034b8u: /* addq    $4,r11 */
   s.registers[0][11]=add(&s,s.registers[0][11],4u);
   s.pc=0xf034bau;break;
  case 0xf034bau: /* store   r15,(r11) */
   CHECK(wr32(bus,&s,local(s.registers[0][11])?(s.registers[0][11]&~3u):s.registers[0][11],s.registers[0][15]));
   s.pc=0xf034bcu;break;
  case 0xf034bcu: /* addq    $4,r11 */
   s.registers[0][11]=add(&s,s.registers[0][11],4u);
   s.pc=0xf034beu;break;
  case 0xf034beu: /* store   r16,(r11) */
   CHECK(wr32(bus,&s,local(s.registers[0][11])?(s.registers[0][11]&~3u):s.registers[0][11],s.registers[0][16]));
   s.pc=0xf034c0u;break;
  case 0xf034c0u: /* subq    $8,r11 */
   s.registers[0][11]=sub(&s,s.registers[0][11],8u);
   s.pc=0xf034c2u;break;
  case 0xf034c2u: /* cmp     r20,r15 */
   (void)sub(&s,s.registers[0][15],s.registers[0][20]);
   s.pc=0xf034c4u;break;
  case 0xf034c4u: /* jr      n,00F034CA */
   if(condition(&s,24)){pending=1;target=0xf034cau;}
   s.pc=0xf034c6u;break;
  case 0xf034c6u: /* cmp     r15,r19 */
   (void)sub(&s,s.registers[0][19],s.registers[0][15]);
   s.pc=0xf034c8u;break;
  case 0xf034c8u: /* move    r15,r20 */
   s.registers[0][20]=s.registers[0][15];
   s.pc=0xf034cau;break;
  case 0xf034cau: /* jr      nz,00F034D0 */
   if(condition(&s,1)){pending=1;target=0xf034d0u;}
   s.pc=0xf034ccu;break;
  case 0xf034ccu: /* nop */
   s.pc=0xf034ceu;break;
  case 0xf034ceu: /* cmp     r14,r18 */
   (void)sub(&s,s.registers[0][18],s.registers[0][14]);
   s.pc=0xf034d0u;break;
  case 0xf034d0u: /* jr      n,00F034DA */
   if(condition(&s,24)){pending=1;target=0xf034dau;}
   s.pc=0xf034d2u;break;
  case 0xf034d2u: /* cmp     r14,r21 */
   (void)sub(&s,s.registers[0][21],s.registers[0][14]);
   s.pc=0xf034d4u;break;
  case 0xf034d4u: /* move    r15,r19 */
   s.registers[0][19]=s.registers[0][15];
   s.pc=0xf034d6u;break;
  case 0xf034d6u: /* move    r14,r18 */
   s.registers[0][18]=s.registers[0][14];
   s.pc=0xf034d8u;break;
  case 0xf034d8u: /* move    r11,r17 */
   s.registers[0][17]=s.registers[0][11];
   s.pc=0xf034dau;break;
  case 0xf034dau: /* jr      n,00F034E0 */
   if(condition(&s,24)){pending=1;target=0xf034e0u;}
   s.pc=0xf034dcu;break;
  case 0xf034dcu: /* cmp     r22,r14 */
   (void)sub(&s,s.registers[0][14],s.registers[0][22]);
   s.pc=0xf034deu;break;
  case 0xf034deu: /* move    r14,r21 */
   s.registers[0][21]=s.registers[0][14];
   s.pc=0xf034e0u;break;
  case 0xf034e0u: /* jr      n,00F034E6 */
   if(condition(&s,24)){pending=1;target=0xf034e6u;}
   s.pc=0xf034e2u;break;
  case 0xf034e2u: /* cmp     r16,r23 */
   (void)sub(&s,s.registers[0][23],s.registers[0][16]);
   s.pc=0xf034e4u;break;
  case 0xf034e4u: /* move    r14,r22 */
   s.registers[0][22]=s.registers[0][14];
   s.pc=0xf034e6u;break;
  case 0xf034e6u: /* jr      n,00F034EC */
   if(condition(&s,24)){pending=1;target=0xf034ecu;}
   s.pc=0xf034e8u;break;
  case 0xf034e8u: /* cmp     r24,r16 */
   (void)sub(&s,s.registers[0][16],s.registers[0][24]);
   s.pc=0xf034eau;break;
  case 0xf034eau: /* move    r16,r23 */
   s.registers[0][23]=s.registers[0][16];
   s.pc=0xf034ecu;break;
  case 0xf034ecu: /* jr      n,00F034FC */
   if(condition(&s,24)){pending=1;target=0xf034fcu;}
   s.pc=0xf034eeu;break;
  case 0xf034eeu: /* nop */
   s.pc=0xf034f0u;break;
  case 0xf034f0u: /* move    r16,r24 */
   s.registers[0][24]=s.registers[0][16];
   s.pc=0xf034f2u;break;
  case 0xf034f2u: /* jr      nz,00F034FA */
   if(condition(&s,1)){pending=1;target=0xf034fau;}
   s.pc=0xf034f4u;break;
  case 0xf034f4u: /* cmp     r25,r26 */
   (void)sub(&s,s.registers[0][26],s.registers[0][25]);
   s.pc=0xf034f6u;break;
  case 0xf034f6u: /* jr      n,00F034FC */
   if(condition(&s,24)){pending=1;target=0xf034fcu;}
   s.pc=0xf034f8u;break;
  case 0xf034f8u: /* nop */
   s.pc=0xf034fau;break;
  case 0xf034fau: /* move    r26,r25 */
   s.registers[0][25]=s.registers[0][26];
   s.pc=0xf034fcu;break;
  case 0xf034fcu: /* subq    $1,r12 */
   s.registers[0][12]=sub(&s,s.registers[0][12],1u);
   s.pc=0xf034feu;break;
  case 0xf034feu: /* jump    nz,(r2) */
   if(condition(&s,1)){pending=1;target=s.registers[0][2];}
   s.pc=0xf03500u;break;
  case 0xf03500u: /* addq    $c,r11 */
   s.registers[0][11]=add(&s,s.registers[0][11],12u);
   s.pc=0xf03502u;break;
  case 0xf03502u: /* movefa  r20,r2 */
   s.registers[0][2]=s.registers[1][20];
   s.pc=0xf03504u;break;
  case 0xf03504u: /* cmp     r20,r19 */
   (void)sub(&s,s.registers[0][19],s.registers[0][20]);
   s.pc=0xf03506u;break;
  case 0xf03506u: /* jump    nn,(r2) */
   if(condition(&s,20)){pending=1;target=s.registers[0][2];}
   s.pc=0xf03508u;break;
  case 0xf03508u: /* moveq   31,r0 */
   s.registers[0][0]=31u;
   s.pc=0xf0350au;break;
  case 0xf0350au: /* movefa  r24,r1 */
   s.registers[0][1]=s.registers[1][24];
   s.pc=0xf0350cu;break;
  case 0xf0350cu: /* cmp     r0,r24 */
   (void)sub(&s,s.registers[0][24],s.registers[0][0]);
   s.pc=0xf0350eu;break;
  case 0xf0350eu: /* jump    n,(r2) */
   if(condition(&s,24)){pending=1;target=s.registers[0][2];}
   s.pc=0xf03510u;break;
  case 0xf03510u: /* cmp     r23,r1 */
   (void)sub(&s,s.registers[0][1],s.registers[0][23]);
   s.pc=0xf03512u;break;
  case 0xf03512u: /* jump    n,(r2) */
   if(condition(&s,24)){pending=1;target=s.registers[0][2];}
   s.pc=0xf03514u;break;
  case 0xf03514u: /* moveq   0,r0 */
   s.registers[0][0]=0u;
   s.pc=0xf03516u;break;
  case 0xf03516u: /* movefa  r22,r1 */
   s.registers[0][1]=s.registers[1][22];
   s.pc=0xf03518u;break;
  case 0xf03518u: /* cmp     r0,r22 */
   (void)sub(&s,s.registers[0][22],s.registers[0][0]);
   s.pc=0xf0351au;break;
  case 0xf0351au: /* jump    n,(r2) */
   if(condition(&s,24)){pending=1;target=s.registers[0][2];}
   s.pc=0xf0351cu;break;
  case 0xf0351cu: /* cmp     r21,r1 */
   (void)sub(&s,s.registers[0][1],s.registers[0][21]);
   s.pc=0xf0351eu;break;
  case 0xf0351eu: /* jump    n,(r2) */
   if(condition(&s,24)){pending=1;target=s.registers[0][2];}
   s.pc=0xf03520u;break;
  case 0xf03520u: /* moveq   0,r0 */
   s.registers[0][0]=0u;
   s.pc=0xf03522u;break;
  case 0xf03522u: /* movefa  r23,r1 */
   s.registers[0][1]=s.registers[1][23];
   s.pc=0xf03524u;break;
  case 0xf03524u: /* cmp     r0,r20 */
   (void)sub(&s,s.registers[0][20],s.registers[0][0]);
   s.pc=0xf03526u;break;
  case 0xf03526u: /* jump    n,(r2) */
   if(condition(&s,24)){pending=1;target=s.registers[0][2];}
   s.pc=0xf03528u;break;
  case 0xf03528u: /* cmp     r19,r1 */
   (void)sub(&s,s.registers[0][1],s.registers[0][19]);
   s.pc=0xf0352au;break;
  case 0xf0352au: /* jump    n,(r2) */
   if(condition(&s,24)){pending=1;target=s.registers[0][2];}
   s.pc=0xf0352cu;break;
  case 0xf0352cu: /* moveq   31,r0 */
   s.registers[0][0]=31u;
   s.pc=0xf0352eu;break;
  case 0xf0352eu: /* movefa  r19,r2 */
   s.registers[0][2]=s.registers[1][19];
   s.pc=0xf03530u;break;
  case 0xf03530u: /* cmp     r0,r23 */
   (void)sub(&s,s.registers[0][23],s.registers[0][0]);
   s.pc=0xf03532u;break;
  case 0xf03532u: /* jump    n,(r2) */
   if(condition(&s,24)){pending=1;target=s.registers[0][2];}
   s.pc=0xf03534u;break;
  case 0xf03534u: /* moveq   16,r0 */
   s.registers[0][0]=16u;
   s.pc=0xf03536u;break;
  case 0xf03536u: /* movefa  r13,r1 */
   s.registers[0][1]=s.registers[1][13];
   s.pc=0xf03538u;break;
  case 0xf03538u: /* shlq    $1,r0 */
   s.c=s.registers[0][0]>>31;s.registers[0][0]=s.registers[0][0]<<1;zn(&s,s.registers[0][0]);
   s.pc=0xf0353au;break;
  case 0xf0353au: /* add     r0,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],s.registers[0][0]);
   s.pc=0xf0353cu;break;
  case 0xf0353cu: /* loadw   (r1),r0 */
   CHECK(loadw(bus,&s,s.registers[0][1],&v));s.registers[0][0]=v;
   s.pc=0xf0353eu;break;
  case 0xf0353eu: /* cmpq    $7,r0 */
   (void)sub(&s,s.registers[0][0],0x7u);
   s.pc=0xf03540u;break;
  case 0xf03540u: /* jump    z,(r2) */
   if(condition(&s,2)){pending=1;target=s.registers[0][2];}
   s.pc=0xf03542u;break;
  case 0xf03542u: /* cmpq    $8,r0 */
   (void)sub(&s,s.registers[0][0],0x8u);
   s.pc=0xf03544u;break;
  case 0xf03544u: /* jump    z,(r2) */
   if(condition(&s,2)){pending=1;target=s.registers[0][2];}
   s.pc=0xf03546u;break;
  case 0xf03546u: /* move    r17,r26 */
   s.registers[0][26]=s.registers[0][17];
   s.pc=0xf03548u;break;
  case 0xf03548u: /* movefa  r12,r10 */
   s.registers[0][10]=s.registers[1][12];
   s.pc=0xf0354au;break;
  case 0xf0354au: /* move    r17,r27 */
   s.registers[0][27]=s.registers[0][17];
   s.pc=0xf0354cu;break;
  case 0xf0354cu: /* subq    $c,r26 */
   s.registers[0][26]=sub(&s,s.registers[0][26],12u);
   s.pc=0xf0354eu;break;
  case 0xf0354eu: /* addq    $c,r27 */
   s.registers[0][27]=add(&s,s.registers[0][27],12u);
   s.pc=0xf03550u;break;
  case 0xf03550u: /* subq    $c,r11 */
   s.registers[0][11]=sub(&s,s.registers[0][11],12u);
   s.pc=0xf03552u;break;
  case 0xf03552u: /* cmp     r10,r26 */
   (void)sub(&s,s.registers[0][26],s.registers[0][10]);
   s.pc=0xf03554u;break;
  case 0xf03554u: /* jr      nn,00F0355A */
   if(condition(&s,20)){pending=1;target=0xf0355au;}
   s.pc=0xf03556u;break;
  case 0xf03556u: /* nop */
   s.pc=0xf03558u;break;
  case 0xf03558u: /* move    r11,r26 */
   s.registers[0][26]=s.registers[0][11];
   s.pc=0xf0355au;break;
  case 0xf0355au: /* cmp     r27,r11 */
   (void)sub(&s,s.registers[0][11],s.registers[0][27]);
   s.pc=0xf0355cu;break;
  case 0xf0355cu: /* jr      nn,00F03562 */
   if(condition(&s,20)){pending=1;target=0xf03562u;}
   s.pc=0xf0355eu;break;
  case 0xf0355eu: /* nop */
   s.pc=0xf03560u;break;
  case 0xf03560u: /* move    r10,r27 */
   s.registers[0][27]=s.registers[0][10];
   s.pc=0xf03562u;break;
  case 0xf03562u: /* load    (r26),r14 */
   CHECK(rd32(bus,&s,s.registers[0][26]&~3u,&v));s.registers[0][14]=v;
   s.pc=0xf03564u;break;
  case 0xf03564u: /* load    (r27),r0 */
   CHECK(rd32(bus,&s,s.registers[0][27]&~3u,&v));s.registers[0][0]=v;
   s.pc=0xf03566u;break;
  case 0xf03566u: /* addq    $4,r26 */
   s.registers[0][26]=add(&s,s.registers[0][26],4u);
   s.pc=0xf03568u;break;
  case 0xf03568u: /* addq    $4,r27 */
   s.registers[0][27]=add(&s,s.registers[0][27],4u);
   s.pc=0xf0356au;break;
  case 0xf0356au: /* load    (r26),r15 */
   CHECK(rd32(bus,&s,s.registers[0][26]&~3u,&v));s.registers[0][15]=v;
   s.pc=0xf0356cu;break;
  case 0xf0356cu: /* load    (r27),r1 */
   CHECK(rd32(bus,&s,s.registers[0][27]&~3u,&v));s.registers[0][1]=v;
   s.pc=0xf0356eu;break;
  case 0xf0356eu: /* sub     r18,r0 */
   s.registers[0][0]=sub(&s,s.registers[0][0],s.registers[0][18]);
   s.pc=0xf03570u;break;
  case 0xf03570u: /* sub     r19,r1 */
   s.registers[0][1]=sub(&s,s.registers[0][1],s.registers[0][19]);
   s.pc=0xf03572u;break;
  case 0xf03572u: /* sub     r14,r18 */
   s.registers[0][18]=sub(&s,s.registers[0][18],s.registers[0][14]);
   s.pc=0xf03574u;break;
  case 0xf03574u: /* sub     r15,r19 */
   s.registers[0][19]=sub(&s,s.registers[0][19],s.registers[0][15]);
   s.pc=0xf03576u;break;
  case 0xf03576u: /* imult   r0,r19 */
   s.registers[0][19]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][19])*(int32_t)sx16(s.registers[0][0]));
   zn(&s,s.registers[0][19]);
   s.pc=0xf03578u;break;
  case 0xf03578u: /* imult   r1,r18 */
   s.registers[0][18]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][18])*(int32_t)sx16(s.registers[0][1]));
   zn(&s,s.registers[0][18]);
   s.pc=0xf0357au;break;
  case 0xf0357au: /* cmp     r19,r18 */
   (void)sub(&s,s.registers[0][18],s.registers[0][19]);
   s.pc=0xf0357cu;break;
  case 0xf0357cu: /* jr      n,00F03584 */
   if(condition(&s,24)){pending=1;target=0xf03584u;}
   s.pc=0xf0357eu;break;
  case 0xf0357eu: /* nop */
   s.pc=0xf03580u;break;
  case 0xf03580u: /* jr      00F03586 */
   if(condition(&s,0)){pending=1;target=0xf03586u;}
   s.pc=0xf03582u;break;
  case 0xf03582u: /* nop */
   s.pc=0xf03584u;break;
  case 0xf03584u: /* moveq   0,r25 */
   s.registers[0][25]=0u;
   s.pc=0xf03586u;break;
  case 0xf03586u: /* movefa  r13,r1 */
   s.registers[0][1]=s.registers[1][13];
   s.pc=0xf03588u;break;
  case 0xf03588u: /* movefa  r15,r0 */
   s.registers[0][0]=s.registers[1][15];
   s.pc=0xf0358au;break;
  case 0xf0358au: /* addq    $18,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],24u);
   s.pc=0xf0358cu;break;
  case 0xf0358cu: /* addq    $8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],8u);
   s.pc=0xf0358eu;break;
  case 0xf0358eu: /* loadw   (r1),r16 */
   CHECK(loadw(bus,&s,s.registers[0][1],&v));s.registers[0][16]=v;
   s.pc=0xf03590u;break;
  case 0xf03590u: /* store   r25,(r0) */
   CHECK(wr32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],s.registers[0][25]));
   s.pc=0xf03592u;break;
  case 0xf03592u: /* subq    $18,r1 */
   s.registers[0][1]=sub(&s,s.registers[0][1],24u);
   s.pc=0xf03594u;break;
  case 0xf03594u: /* moveta  r0,r15 */
   s.registers[1][15]=s.registers[0][0];
   s.pc=0xf03596u;break;
  case 0xf03596u: /* shlq    $3,r16 */
   s.c=s.registers[0][16]>>31;s.registers[0][16]=s.registers[0][16]<<3;zn(&s,s.registers[0][16]);
   s.pc=0xf03598u;break;
  case 0xf03598u: /* addq    $4,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],4u);
   s.pc=0xf0359au;break;
  case 0xf0359au: /* movefa  r5,r14 */
   s.registers[0][14]=s.registers[1][5];
   s.pc=0xf0359cu;break;
  case 0xf0359cu: /* store   r16,(r0) */
   CHECK(wr32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],s.registers[0][16]));
   s.pc=0xf0359eu;break;
  case 0xf0359eu: /* add     r14,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],s.registers[0][14]);
   s.pc=0xf035a0u;break;
  case 0xf035a0u: /* movefa  r14,r15 */
   s.registers[0][15]=s.registers[1][14];
   s.pc=0xf035a2u;break;
  case 0xf035a2u: /* moveta  r1,r13 */
   s.registers[1][13]=s.registers[0][1];
   s.pc=0xf035a4u;break;
  case 0xf035a4u: /* add     r14,r15 */
   s.registers[0][15]=add(&s,s.registers[0][15],s.registers[0][14]);
   s.pc=0xf035a6u;break;
  case 0xf035a6u: /* movefa  r21,r0 */
   s.registers[0][0]=s.registers[1][21];
   s.pc=0xf035a8u;break;
  case 0xf035a8u: /* subq    $1,r9 */
   s.registers[0][9]=sub(&s,s.registers[0][9],1u);
   s.pc=0xf035aau;break;
  case 0xf035aau: /* jump    nz,(r0) */
   if(condition(&s,1)){pending=1;target=s.registers[0][0];}
   s.pc=0xf035acu;break;
  case 0xf035acu: /* moveta  r15,r14 */
   s.registers[1][14]=s.registers[0][15];
   s.pc=0xf035aeu;break;
  case 0xf035aeu: /* movefa  r6,r6 */
   s.registers[0][6]=s.registers[1][6];
   s.pc=0xf035b0u;break;
  case 0xf035b0u: /* moveq   0,r0 */
   s.registers[0][0]=0u;
   s.pc=0xf035b2u;break;
  case 0xf035b2u: /* movefa  r3,r3 */
   s.registers[0][3]=s.registers[1][3];
   s.pc=0xf035b4u;break;
  case 0xf035b4u: /* store   r0,(r6) */
   CHECK(wr32(bus,&s,local(s.registers[0][6])?(s.registers[0][6]&~3u):s.registers[0][6],s.registers[0][0]));
   s.pc=0xf035b6u;break;
  case 0xf035b6u: /* movefa  r5,r4 */
   s.registers[0][4]=s.registers[1][5];
   s.pc=0xf035b8u;break;
  case 0xf035b8u: /* addq    $4,r6 */
   s.registers[0][6]=add(&s,s.registers[0][6],4u);
   s.pc=0xf035bau;break;
  case 0xf035bau: /* movefa  r4,r5 */
   s.registers[0][5]=s.registers[1][4];
   s.pc=0xf035bcu;break;
  case 0xf035bcu: /* store   r0,(r6) */
   CHECK(wr32(bus,&s,local(s.registers[0][6])?(s.registers[0][6]&~3u):s.registers[0][6],s.registers[0][0]));
   s.pc=0xf035beu;break;
  case 0xf035beu: /* movei   $f035ce,r8 */
   s.registers[0][8]=0xf035ceu;
   s.pc=0xf035c4u;break;
  case 0xf035c4u: /* subq    $4,r6 */
   s.registers[0][6]=sub(&s,s.registers[0][6],4u);
   s.pc=0xf035c6u;break;
  case 0xf035c6u: /* moveq   8,r7 */
   s.registers[0][7]=8u;
   s.pc=0xf035c8u;break;
  case 0xf035c8u: /* movei   $f03606,r9 */
   s.registers[0][9]=0xf03606u;
   s.pc=0xf035ceu;break;
  case 0xf035ceu: /* cmpq    $0,r7 */
   (void)sub(&s,s.registers[0][7],0x0u);
   s.pc=0xf035d0u;break;
  case 0xf035d0u: /* jr      nz,00F035D6 */
   if(condition(&s,1)){pending=1;target=0xf035d6u;}
   s.pc=0xf035d2u;break;
  case 0xf035d2u: /* move    r7,r10 */
   s.registers[0][10]=s.registers[0][7];
   s.pc=0xf035d4u;break;
  case 0xf035d4u: /* jump    (r9) */
   if(condition(&s,0)){pending=1;target=s.registers[0][9];}
   s.pc=0xf035d6u;break;
  case 0xf035d6u: /* move    r7,r11 */
   s.registers[0][11]=s.registers[0][7];
   s.pc=0xf035d8u;break;
  case 0xf035d8u: /* add     r6,r10 */
   s.registers[0][10]=add(&s,s.registers[0][10],s.registers[0][6]);
   s.pc=0xf035dau;break;
  case 0xf035dau: /* load    (r10),r12 */
   CHECK(rd32(bus,&s,s.registers[0][10]&~3u,&v));s.registers[0][12]=v;
   s.pc=0xf035dcu;break;
  case 0xf035dcu: /* moveq   31,r0 */
   s.registers[0][0]=31u;
   s.pc=0xf035deu;break;
  case 0xf035deu: /* addq    $4,r10 */
   s.registers[0][10]=add(&s,s.registers[0][10],4u);
   s.pc=0xf035e0u;break;
  case 0xf035e0u: /* cmp     r0,r12 */
   (void)sub(&s,s.registers[0][12],s.registers[0][0]);
   s.pc=0xf035e2u;break;
  case 0xf035e2u: /* jump    n,(r8) */
   if(condition(&s,24)){pending=1;target=s.registers[0][8];}
   s.pc=0xf035e4u;break;
  case 0xf035e4u: /* load    (r10),r7 */
   CHECK(rd32(bus,&s,s.registers[0][10]&~3u,&v));s.registers[0][7]=v;
   s.pc=0xf035e6u;break;
  case 0xf035e6u: /* move    r6,r13 */
   s.registers[0][13]=s.registers[0][6];
   s.pc=0xf035e8u;break;
  case 0xf035e8u: /* addq    $4,r13 */
   s.registers[0][13]=add(&s,s.registers[0][13],4u);
   s.pc=0xf035eau;break;
  case 0xf035eau: /* load    (r13),r15 */
   CHECK(rd32(bus,&s,s.registers[0][13]&~3u,&v));s.registers[0][15]=v;
   s.pc=0xf035ecu;break;
  case 0xf035ecu: /* cmpq    $0,r15 */
   (void)sub(&s,s.registers[0][15],0x0u);
   s.pc=0xf035eeu;break;
  case 0xf035eeu: /* jr      z,00F03600 */
   if(condition(&s,2)){pending=1;target=0xf03600u;}
   s.pc=0xf035f0u;break;
  case 0xf035f0u: /* move    r15,r14 */
   s.registers[0][14]=s.registers[0][15];
   s.pc=0xf035f2u;break;
  case 0xf035f2u: /* add     r6,r14 */
   s.registers[0][14]=add(&s,s.registers[0][14],s.registers[0][6]);
   s.pc=0xf035f4u;break;
  case 0xf035f4u: /* load    (r14),r16 */
   CHECK(rd32(bus,&s,s.registers[0][14]&~3u,&v));s.registers[0][16]=v;
   s.pc=0xf035f6u;break;
  case 0xf035f6u: /* cmp     r12,r16 */
   (void)sub(&s,s.registers[0][16],s.registers[0][12]);
   s.pc=0xf035f8u;break;
  case 0xf035f8u: /* jr      n,00F03600 */
   if(condition(&s,24)){pending=1;target=0xf03600u;}
   s.pc=0xf035fau;break;
  case 0xf035fau: /* nop */
   s.pc=0xf035fcu;break;
  case 0xf035fcu: /* jr      00F035E8 */
   if(condition(&s,0)){pending=1;target=0xf035e8u;}
   s.pc=0xf035feu;break;
  case 0xf035feu: /* move    r14,r13 */
   s.registers[0][13]=s.registers[0][14];
   s.pc=0xf03600u;break;
  case 0xf03600u: /* store   r11,(r13) */
   CHECK(wr32(bus,&s,local(s.registers[0][13])?(s.registers[0][13]&~3u):s.registers[0][13],s.registers[0][11]));
   s.pc=0xf03602u;break;
  case 0xf03602u: /* jump    (r8) */
   if(condition(&s,0)){pending=1;target=s.registers[0][8];}
   s.pc=0xf03604u;break;
  case 0xf03604u: /* store   r15,(r10) */
   CHECK(wr32(bus,&s,local(s.registers[0][10])?(s.registers[0][10]&~3u):s.registers[0][10],s.registers[0][15]));
   s.pc=0xf03606u;break;
  case 0xf03606u: /* addq    $4,r6 */
   s.registers[0][6]=add(&s,s.registers[0][6],4u);
   s.pc=0xf03608u;break;
  case 0xf03608u: /* load    (r6),r0 */
   CHECK(rd32(bus,&s,s.registers[0][6]&~3u,&v));s.registers[0][0]=v;
   s.pc=0xf0360au;break;
  case 0xf0360au: /* shrq    $3,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=s.registers[0][0]>>3;zn(&s,s.registers[0][0]);
   s.pc=0xf0360cu;break;
  case 0xf0360cu: /* subq    $4,r6 */
   s.registers[0][6]=sub(&s,s.registers[0][6],4u);
   s.pc=0xf0360eu;break;
  case 0xf0360eu: /* store   r0,(r6) */
   CHECK(wr32(bus,&s,local(s.registers[0][6])?(s.registers[0][6]&~3u):s.registers[0][6],s.registers[0][0]));
   s.pc=0xf03610u;break;
  case 0xf03610u: /* addq    $c,r6 */
   s.registers[0][6]=add(&s,s.registers[0][6],12u);
   s.pc=0xf03612u;break;
  case 0xf03612u: /* addq    $18,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],24u);
   s.pc=0xf03614u;break;
  case 0xf03614u: /* load    (r6),r0 */
   CHECK(rd32(bus,&s,s.registers[0][6]&~3u,&v));s.registers[0][0]=v;
   s.pc=0xf03616u;break;
  case 0xf03616u: /* shrq    $3,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=s.registers[0][0]>>3;zn(&s,s.registers[0][0]);
   s.pc=0xf03618u;break;
  case 0xf03618u: /* addq    $8,r6 */
   s.registers[0][6]=add(&s,s.registers[0][6],8u);
   s.pc=0xf0361au;break;
  case 0xf0361au: /* subq    $1,r5 */
   s.registers[0][5]=sub(&s,s.registers[0][5],1u);
   s.pc=0xf0361cu;break;
  case 0xf0361cu: /* storew  r0,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][0]));
   s.pc=0xf0361eu;break;
  case 0xf0361eu: /* jr      nz,00F03614 */
   if(condition(&s,1)){pending=1;target=0xf03614u;}
   s.pc=0xf03620u;break;
  case 0xf03620u: /* add     r4,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],s.registers[0][4]);
   s.pc=0xf03622u;break;
  case 0xf03622u: /* movei   $f031be,r2 */
   s.registers[0][2]=0xf031beu;
   s.pc=0xf03628u;break;
  case 0xf03628u: /* jump    (r2) */
   if(condition(&s,0)){pending=1;target=s.registers[0][2];}
   s.pc=0xf0362au;break;
  case 0xf0362au: /* nop */
   s.pc=0xf0362cu;break;
  default:return BIWN_GPU_PROJECTION_BAD_PC;
 }if(delayed){if(pending)return BIWN_GPU_PROJECTION_BAD_DELAY;s.pc=resume;}if(s.pc==0xf031beu){*state=s;return BIWN_GPU_PROJECTION_OK;}}return BIWN_GPU_PROJECTION_WORK_LIMIT;}
