/* Generated from the pinned GPU4D80 overlay by
 * scripts/generate_biwn_gpu_geometry.py. Analyst static recompilation,
 * not recovered original source. Integer primitive behavior is checked
 * against the pinned Virtual Jaguar core; no core runs on the C side. */
#include "biwn_gpu_geometry.h"
#include <string.h>
static uint32_t sx16(uint32_t v){return(v&0x7fffu)-(v&0x8000u);}
static uint32_t sar(uint32_t v,unsigned n){return n>=32?((v&0x80000000u)?0xffffffffu:0):(v>>n)|((v&0x80000000u)?(0xffffffffu<<(32-n)):0);}
static void zn(struct biwn_gpu_geometry_state *s,uint32_t v){s->z=v==0;s->n=v>>31;}
static uint32_t add(struct biwn_gpu_geometry_state *s,uint32_t a,uint32_t b){uint32_t v=a+b;s->c=b>~a;zn(s,v);return v;}
static uint32_t sub(struct biwn_gpu_geometry_state *s,uint32_t a,uint32_t b){uint32_t v=a-b;s->c=b>a;zn(s,v);return v;}
static int condition(struct biwn_gpu_geometry_state *s,unsigned code){unsigned flags=s->z|(s->c<<1)|(s->n<<2);return !((code&1u)&&(flags&1u))&&!((code&2u)&&!(flags&1u))&&!((code&4u)&&(flags&(2u<<(code>>4))))&&!((code&8u)&&!(flags&(2u<<(code>>4))));}
static uint32_t be32(const uint8_t *p){return((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
static void put32(uint8_t *p,uint32_t v){p[0]=(uint8_t)(v>>24);p[1]=(uint8_t)(v>>16);p[2]=(uint8_t)(v>>8);p[3]=(uint8_t)v;}
static int local(uint32_t a){return a>=0xf03000u&&a<=0xf03ffcu;}
static int rd32(struct biwn_gpu_geometry_bus *bus,struct biwn_gpu_geometry_state *s,uint32_t a,uint32_t *v){if(local(a)){*v=be32(s->local_RAM+a-0xf03000u);return 0;}if(a==0xf02104u){*v=s->matrix_control;return 0;}if(a==0xf02108u){*v=s->matrix_pointer;return 0;}return bus->read32(bus->context,a,v)?2:0;}
static int rd16(struct biwn_gpu_geometry_bus *bus,struct biwn_gpu_geometry_state *s,uint32_t a,uint32_t *v){uint16_t h;if(a>=0xf03000u&&a<=0xf03ffeu){unsigned p=a-0xf03000u;*v=((uint32_t)s->local_RAM[p]<<8)|s->local_RAM[p+1];return 0;}if(bus->read16(bus->context,a,&h))return 2;*v=h;return 0;}
static int loadw(struct biwn_gpu_geometry_bus *bus,struct biwn_gpu_geometry_state *s,uint32_t a,uint32_t *v){if(a>=0xf03000u&&a<=0xf03fffu)return rd32(bus,s,a&~3u,v);return rd16(bus,s,a,v);}
static int wr32(struct biwn_gpu_geometry_bus *bus,struct biwn_gpu_geometry_state *s,uint32_t a,uint32_t v){if(local(a)){put32(s->local_RAM+a-0xf03000u,v);return 0;}if(a==0xf02104u){s->matrix_control=v;return 0;}if(a==0xf02108u){s->matrix_pointer=v&~3u;return 0;}return bus->write32(bus->context,a,v)?2:0;}
static int wr16(struct biwn_gpu_geometry_bus *bus,struct biwn_gpu_geometry_state *s,uint32_t a,uint32_t v){if(a>=0xf03000u&&a<=0xf03fffu)return wr32(bus,s,a&~1u,v&0xffffu);return bus->write16(bus->context,a,(uint16_t)v)?2:0;}
static void divide(struct biwn_gpu_geometry_state *s,unsigned m,unsigned n){uint32_t q=s->registers[0][n],r=0,d=s->registers[0][m];unsigned i;if(s->division_control&1u){r=q>>16;q<<=16;}for(i=0;i<32;i++){uint32_t sign=r&0x80000000u;r=(r<<1)|(q>>31);r+=sign?d:0u-d;q=(q<<1)|((~r)>>31);}s->registers[0][n]=q;s->remainder=r;}
static int matrix(struct biwn_gpu_geometry_bus *bus,struct biwn_gpu_geometry_state *s,unsigned m,unsigned n){unsigned i,count=s->matrix_control&15u;uint32_t a=s->matrix_pointer,v;int64_t sum=0;for(i=0;i<count;i++){uint32_t packed=s->registers[1][m+(i>>1)];int32_t x=(int32_t)sx16(packed>>(i&1u?16:0));int status=rd16(bus,s,a+2,&v);if(status)return status;sum+=(int64_t)x*(int32_t)sx16(v);a+=(s->matrix_control&16u)?4u*count:4u;}s->registers[0][n]=(uint32_t)sum;zn(s,(uint32_t)sum);return 0;}
static const uint8_t source_image[1360]={
0x98,0x0,0x32,0xc,0x0,0xf0,0x8c,0x23,0x98,0xb,0x36,0x48,0x0,0xf0,0x20,0x3,0x98,0x1,0x36,0x6c,0x0,0xf0,0x66,0x3,
0x98,0x7,0x4,0x0,0x0,0x0,0x98,0x4,0x0,0xad,0x0,0x0,0x88,0xe6,0x98,0x5,0x0,0x6f,0x0,0x0,0x20,0x6,0xa4,0x8,
0x8d,0x2a,0x8,0x80,0xa1,0x2,0x62,0x2,0x6e,0x2,0x8,0x48,0xbd,0x62,0x18,0x2a,0xd7,0x21,0xc,0x8b,0xa4,0x9,0xa1,0x13,
0xa1,0x30,0x8,0x48,0x8,0x49,0xa1,0x14,0xa1,0x31,0x8,0x48,0x8,0x49,0xa1,0x15,0xa1,0x32,0x62,0x13,0x62,0x10,0x6e,0x13,
0x6e,0x10,0x2,0x70,0x62,0x14,0x62,0x11,0x6e,0x14,0x6e,0x11,0x2,0x91,0x62,0x15,0x62,0x12,0x6e,0x15,0x6e,0x12,0x2,0xb2,
0x8,0x80,0x19,0x8b,0x98,0x19,0x21,0x4,0x0,0xf0,0x98,0x2,0x0,0x3,0x0,0x0,0x98,0xf,0x21,0x8,0x0,0xf0,0xbf,0x22,
0x98,0x18,0x32,0xfa,0x0,0xf0,0x8c,0x14,0x98,0x19,0x33,0x32,0x0,0xf0,0x12,0x34,0x88,0x2c,0x62,0x14,0x8c,0x17,0x98,0x1a,
0x4,0x0,0x0,0x0,0x7c,0xd7,0xd3,0x22,0x8a,0xf5,0x8c,0x16,0x43,0x55,0x8,0x37,0x12,0x55,0x7c,0xd6,0xd6,0xe2,0x8a,0xd3,
0x43,0x53,0x8,0x36,0x12,0x13,0x8a,0x6d,0x8a,0xae,0x24,0x6d,0x24,0x6e,0x2a,0x8d,0x1b,0xb,0xbd,0xeb,0x91,0xad,0x91,0xce,
0xd9,0xa2,0x6d,0xc2,0xbd,0x82,0x8,0x8c,0xb,0xb,0xbd,0xeb,0x91,0xad,0x91,0xce,0xd9,0xa2,0x6d,0xc2,0xbd,0x82,0xd3,0x0,
0x8,0x8c,0xa4,0x8,0x98,0x9,0x36,0x38,0x0,0xf0,0x8c,0x75,0x8c,0xc,0x63,0x95,0x8c,0xd,0x8f,0xd6,0x8c,0x17,0x98,0x18,
0x0,0xe0,0x0,0x0,0x8f,0xf9,0x98,0x1a,0x3,0x0,0x0,0x0,0xcc,0xa,0x89,0x4b,0x9,0xa,0xa,0x8b,0x88,0x72,0x8c,0x8e,
0x88,0x71,0x62,0x12,0x8a,0x33,0x8a,0x54,0x89,0x8f,0x89,0xb0,0x63,0xaf,0x46,0xb0,0xa5,0x22,0x1,0xf0,0x0,0x22,0x2,0x2,
0xa4,0x4f,0x8,0x82,0xa4,0x50,0x44,0x8f,0x7a,0xd0,0xd4,0x54,0x58,0xf,0x8a,0xd0,0xd4,0x44,0x56,0xf,0x20,0xf,0x79,0xe6,
0xd4,0x58,0x78,0xef,0x88,0xcf,0xd4,0x58,0xe4,0x0,0x88,0xef,0x0,0xaf,0x79,0xf1,0xd4,0x58,0x7a,0x4f,0x89,0xf1,0xd4,0x58,
0x7a,0x13,0x89,0xf2,0xd4,0x58,0x7a,0x90,0x8a,0x13,0xd4,0x58,0x18,0x2e,0x8a,0x14,0xd1,0x61,0x8,0x89,0xa5,0xf,0x1a,0x9,
0x7a,0xf2,0xd5,0x38,0x7a,0x38,0xd4,0xf8,0x7b,0x34,0xd4,0xb8,0x7a,0x7a,0xd4,0x78,0x29,0xef,0xd4,0x40,0x3f,0xef,0x3b,0xef,
0x8,0x2c,0x7c,0xac,0xd4,0x61,0xbd,0xf,0x8,0x2d,0x8c,0xc,0x7c,0xad,0xd1,0x41,0x8,0x88,0x98,0x0,0x32,0x10,0x0,0xf0,
0xa4,0x3,0x8c,0x5,0x18,0x80,0xa0,0x68,0xa4,0x4,0x8,0x43,0x9,0x0,0xa0,0x69,0xa4,0x6,0x8,0x43,0x8,0x80,0xa0,0x6a,
0x62,0x8,0x62,0x9,0x62,0xa,0x6e,0x8,0x6e,0x9,0x6e,0xa,0x8c,0xc,0x8c,0xb,0xa4,0xc7,0x98,0x3,0x35,0x6a,0x0,0xf0,
0x37,0xe7,0xd0,0x61,0x8,0x86,0x9,0x7,0xa4,0xed,0x8,0x87,0xa4,0xee,0x8,0x87,0xa4,0xef,0x1a,0x7,0x8c,0x10,0xa0,0xf1,
0x98,0x3,0x35,0x6a,0x0,0xf0,0x7a,0x11,0xd0,0x62,0xe4,0x0,0x9,0x4d,0x98,0x1,0x0,0x40,0x0,0x0,0xa1,0xb2,0x8,0x4d,
0x44,0x32,0xa1,0xb3,0x8,0x4d,0x44,0x33,0xa1,0xb4,0x8,0x4d,0x44,0x34,0xa1,0xb5,0x8,0x4d,0x44,0x35,0xa1,0xb6,0x1a,0x4d,
0x44,0x36,0x98,0x3,0x4,0x0,0x0,0x0,0x89,0x61,0x89,0x82,0x44,0x61,0x44,0x62,0x0,0x32,0x0,0x54,0x11,0x12,0x11,0x33,
0x11,0x54,0x8c,0x17,0x8c,0x38,0x98,0x3,0x35,0x92,0x0,0xf0,0xcc,0x19,0xd0,0x60,0x8,0xd9,0x88,0x83,0x8,0x84,0x8,0xc3,
0xb8,0x96,0xb8,0x75,0x8,0xc4,0x8,0xc3,0xb8,0x96,0xb8,0x75,0x19,0xc4,0x18,0x4,0x2,0xd4,0x8c,0x57,0x8c,0x58,0x98,0x1a,
0x34,0xd6,0x0,0xf0,0x98,0x3,0x35,0x92,0x0,0xf0,0xcc,0x19,0xd0,0x60,0x8,0xd9,0x88,0x83,0x8,0x44,0x8,0xc3,0xb8,0x97,
0xb8,0x75,0x8,0xc4,0x8,0xc3,0xb8,0x97,0xb8,0x75,0x19,0x84,0x18,0x4,0x12,0xd4,0x8c,0x97,0x8c,0x98,0x98,0x1a,0x35,0x2,
0x0,0xf0,0x98,0x3,0x35,0x92,0x0,0xf0,0xcc,0x19,0xd0,0x60,0x8,0xd9,0x88,0x83,0x8,0x43,0xb8,0x95,0xb8,0x77,0x9,0x4,
0xa,0x3,0xb8,0x97,0xb8,0x75,0x19,0x84,0x18,0x4,0x2,0xb2,0x8c,0xd7,0x8c,0x78,0x98,0x1a,0x35,0x30,0x0,0xf0,0x98,0x3,
0x35,0x92,0x0,0xf0,0xcc,0x19,0xd0,0x60,0x8,0xd9,0x88,0x83,0x8,0x44,0x8,0x83,0xb8,0x97,0xb8,0x76,0x8,0xc4,0xa,0x43,
0xb8,0x97,0xb8,0x76,0x19,0x84,0x18,0x4,0x12,0xb2,0x8d,0x17,0x8c,0xb8,0x98,0x1a,0x35,0x5e,0x0,0xf0,0x98,0x3,0x35,0x92,
0x0,0xf0,0xcc,0x19,0xd0,0x60,0x8,0xd9,0x88,0x83,0x8,0x44,0x9,0x43,0xb8,0x97,0xb8,0x76,0x8,0xc4,0x8,0xc3,0xb8,0x97,
0xb8,0x76,0x19,0x84,0x18,0x4,0x98,0x3,0x34,0x38,0x0,0xf0,0x8,0x30,0xd0,0x60,0xa,0x8d,0x98,0x3,0x34,0x18,0x0,0xf0,
0x7c,0x8b,0xd0,0x61,0x8,0x2b,0x7c,0x8c,0x8c,0xb,0xd0,0x61,0x8,0x2c,0xb,0x4,0x8c,0x1,0xa4,0x3,0x98,0x2,0x31,0xbe,
0x0,0xf0,0xb8,0x81,0xbc,0x65,0xd0,0x40,0xe4,0x0,0x98,0x3,0x35,0xde,0x0,0xf0,0x7c,0x17,0xd0,0x62,0xe4,0x0,0x2,0xed,
0x98,0x1,0xf0,0x0,0x0,0x0,0xa1,0xbb,0x98,0x2,0x10,0x0,0x0,0x0,0x27,0x61,0x12,0xed,0x78,0x41,0xd3,0x41,0xe4,0x0,
0x98,0x2,0xf,0xff,0x0,0x0,0x8f,0x81,0x24,0x5b,0x89,0xc3,0x40,0x3b,0x9,0x3,0x3,0x63,0xa0,0x77,0x2a,0xf7,0x7c,0xd7,
0xd4,0x58,0xe4,0x0,0x8c,0xb7,0x20,0x17,0x7c,0x17,0xd3,0x42,0x63,0x57,0x8,0x25,0xb,0x4,0x8c,0x21,0xb8,0x85,0x8c,0x2,
0x8,0x4,0x60,0x41,0x9,0x4,0x88,0x83,0x8,0x83,0xbc,0x81,0xbc,0x62,0x9,0x4,0x9,0x3,0xbc,0x81,0xbc,0x62,0x9,0x4,
0x66,0x1,0x8,0xc3,0xb8,0x81,0xb8,0x72,0x8,0x84,0x8,0x83,0xb8,0x93,0xb8,0x74,0x8,0x84,0x8,0xc3,0x8b,0x1,0xbc,0x82,
0x62,0x1,0xbc,0x62,0x2a,0x1,0x9,0x4,0xbc,0x81,0x8,0x84,0x8c,0xc1,0xbc,0x82,0x18,0x21,0xd7,0xa1,0x8,0x84,0xbc,0x87,
0xd3,0x20,0x1b,0x4,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x30,0x0,0x0,0x0,0x38,0x0,0x0,0x0,0x8,0x0,0x0,0x0,0x0,
0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0
};
enum biwn_gpu_geometry_status biwn_gpu_geometry_init(struct biwn_gpu_geometry_state *s,uint32_t seed,const uint8_t *initial_RAM){unsigned i;if(!s)return 1;memset(s,0,sizeof(*s));if(initial_RAM)memcpy(s->local_RAM,initial_RAM,4096);else memset(s->local_RAM,0xff,4096);memcpy(s->local_RAM+0x240,source_image,1360);for(i=0;i<32;i++){seed=1664525u*seed+1013904223u;s->registers[0][i]=seed;s->registers[1][i]=~seed;}put32(s->local_RAM+0x20c,0x47b88);put32(s->local_RAM+0x210,0x49b8c);put32(s->local_RAM+0x214,0x49bb4);put32(s->local_RAM+0x218,0x49b88);s->division_control=0xa5a50001u;s->pc=0xf03240;return 0;}
#define CHECK(e) do{int status=(e);if(status)return(enum biwn_gpu_geometry_status)status;}while(0)
enum biwn_gpu_geometry_status biwn_gpu_geometry_run(struct biwn_gpu_geometry_bus *bus,struct biwn_gpu_geometry_state *state,uint32_t budget){struct biwn_gpu_geometry_state s;uint32_t v,target=0;unsigned pending=0;if(!bus||!state||!budget||!bus->read16||!bus->read32||!bus->write16||!bus->write32||state->z>1||state->c>1||state->n>1)return 1;s=*state;while(budget--){unsigned delayed=pending;uint32_t resume=target;pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){
  case 0xf03240u: /* movei   $f0320c,r0 */
   s.registers[0][0]=0xf0320cu;
   s.pc=0xf03246u;break;
  case 0xf03246u: /* moveq   1,r3 */
   s.registers[0][3]=1u;
   s.pc=0xf03248u;break;
  case 0xf03248u: /* movei   $f03648,r11 */
   s.registers[0][11]=0xf03648u;
   s.pc=0xf0324eu;break;
  case 0xf0324eu: /* neg     r3 */
   s.registers[0][3]=sub(&s,0,s.registers[0][3]);
   s.pc=0xf03250u;break;
  case 0xf03250u: /* movei   $f0366c,r1 */
   s.registers[0][1]=0xf0366cu;
   s.pc=0xf03256u;break;
  case 0xf03256u: /* shrq    $10,r3 */
   s.c=s.registers[0][3]&1u;s.registers[0][3]=s.registers[0][3]>>16;zn(&s,s.registers[0][3]);
   s.pc=0xf03258u;break;
  case 0xf03258u: /* movei   $400,r7 */
   s.registers[0][7]=0x400u;
   s.pc=0xf0325eu;break;
  case 0xf0325eu: /* movei   $ad,r4 */
   s.registers[0][4]=0xadu;
   s.pc=0xf03264u;break;
  case 0xf03264u: /* move    r7,r6 */
   s.registers[0][6]=s.registers[0][7];
   s.pc=0xf03266u;break;
  case 0xf03266u: /* movei   $6f,r5 */
   s.registers[0][5]=0x6fu;
   s.pc=0xf0326cu;break;
  case 0xf0326cu: /* neg     r6 */
   s.registers[0][6]=sub(&s,0,s.registers[0][6]);
   s.pc=0xf0326eu;break;
  case 0xf0326eu: /* load    (r0),r8 */
   CHECK(rd32(bus,&s,s.registers[0][0]&~3u,&v));s.registers[0][8]=v;
   s.pc=0xf03270u;break;
  case 0xf03270u: /* moveq   9,r10 */
   s.registers[0][10]=9u;
   s.pc=0xf03272u;break;
  case 0xf03272u: /* addq    $4,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],4u);
   s.pc=0xf03274u;break;
  case 0xf03274u: /* loadw   (r8),r2 */
   CHECK(loadw(bus,&s,s.registers[0][8],&v));s.registers[0][2]=v;
   s.pc=0xf03276u;break;
  case 0xf03276u: /* shlq    $10,r2 */
   s.c=s.registers[0][2]>>31;s.registers[0][2]=s.registers[0][2]<<16;zn(&s,s.registers[0][2]);
   s.pc=0xf03278u;break;
  case 0xf03278u: /* sharq   $10,r2 */
   s.c=s.registers[0][2]&1u;s.registers[0][2]=sar(s.registers[0][2],16);zn(&s,s.registers[0][2]);
   s.pc=0xf0327au;break;
  case 0xf0327au: /* addq    $2,r8 */
   s.registers[0][8]=add(&s,s.registers[0][8],2u);
   s.pc=0xf0327cu;break;
  case 0xf0327cu: /* store   r2,(r11) */
   CHECK(wr32(bus,&s,local(s.registers[0][11])?(s.registers[0][11]&~3u):s.registers[0][11],s.registers[0][2]));
   s.pc=0xf0327eu;break;
  case 0xf0327eu: /* subq    $1,r10 */
   s.registers[0][10]=sub(&s,s.registers[0][10],1u);
   s.pc=0xf03280u;break;
  case 0xf03280u: /* jr      nz,00F03274 */
   if(condition(&s,1)){pending=1;target=0xf03274u;}
   s.pc=0xf03282u;break;
  case 0xf03282u: /* addqt   $4,r11 */
   s.registers[0][11]+=4u;
   s.pc=0xf03284u;break;
  case 0xf03284u: /* load    (r0),r9 */
   CHECK(rd32(bus,&s,s.registers[0][0]&~3u,&v));s.registers[0][9]=v;
   s.pc=0xf03286u;break;
  case 0xf03286u: /* loadw   (r8),r19 */
   CHECK(loadw(bus,&s,s.registers[0][8],&v));s.registers[0][19]=v;
   s.pc=0xf03288u;break;
  case 0xf03288u: /* loadw   (r9),r16 */
   CHECK(loadw(bus,&s,s.registers[0][9],&v));s.registers[0][16]=v;
   s.pc=0xf0328au;break;
  case 0xf0328au: /* addq    $2,r8 */
   s.registers[0][8]=add(&s,s.registers[0][8],2u);
   s.pc=0xf0328cu;break;
  case 0xf0328cu: /* addq    $2,r9 */
   s.registers[0][9]=add(&s,s.registers[0][9],2u);
   s.pc=0xf0328eu;break;
  case 0xf0328eu: /* loadw   (r8),r20 */
   CHECK(loadw(bus,&s,s.registers[0][8],&v));s.registers[0][20]=v;
   s.pc=0xf03290u;break;
  case 0xf03290u: /* loadw   (r9),r17 */
   CHECK(loadw(bus,&s,s.registers[0][9],&v));s.registers[0][17]=v;
   s.pc=0xf03292u;break;
  case 0xf03292u: /* addq    $2,r8 */
   s.registers[0][8]=add(&s,s.registers[0][8],2u);
   s.pc=0xf03294u;break;
  case 0xf03294u: /* addq    $2,r9 */
   s.registers[0][9]=add(&s,s.registers[0][9],2u);
   s.pc=0xf03296u;break;
  case 0xf03296u: /* loadw   (r8),r21 */
   CHECK(loadw(bus,&s,s.registers[0][8],&v));s.registers[0][21]=v;
   s.pc=0xf03298u;break;
  case 0xf03298u: /* loadw   (r9),r18 */
   CHECK(loadw(bus,&s,s.registers[0][9],&v));s.registers[0][18]=v;
   s.pc=0xf0329au;break;
  case 0xf0329au: /* shlq    $10,r19 */
   s.c=s.registers[0][19]>>31;s.registers[0][19]=s.registers[0][19]<<16;zn(&s,s.registers[0][19]);
   s.pc=0xf0329cu;break;
  case 0xf0329cu: /* shlq    $10,r16 */
   s.c=s.registers[0][16]>>31;s.registers[0][16]=s.registers[0][16]<<16;zn(&s,s.registers[0][16]);
   s.pc=0xf0329eu;break;
  case 0xf0329eu: /* sharq   $10,r19 */
   s.c=s.registers[0][19]&1u;s.registers[0][19]=sar(s.registers[0][19],16);zn(&s,s.registers[0][19]);
   s.pc=0xf032a0u;break;
  case 0xf032a0u: /* sharq   $10,r16 */
   s.c=s.registers[0][16]&1u;s.registers[0][16]=sar(s.registers[0][16],16);zn(&s,s.registers[0][16]);
   s.pc=0xf032a2u;break;
  case 0xf032a2u: /* add     r19,r16 */
   s.registers[0][16]=add(&s,s.registers[0][16],s.registers[0][19]);
   s.pc=0xf032a4u;break;
  case 0xf032a4u: /* shlq    $10,r20 */
   s.c=s.registers[0][20]>>31;s.registers[0][20]=s.registers[0][20]<<16;zn(&s,s.registers[0][20]);
   s.pc=0xf032a6u;break;
  case 0xf032a6u: /* shlq    $10,r17 */
   s.c=s.registers[0][17]>>31;s.registers[0][17]=s.registers[0][17]<<16;zn(&s,s.registers[0][17]);
   s.pc=0xf032a8u;break;
  case 0xf032a8u: /* sharq   $10,r20 */
   s.c=s.registers[0][20]&1u;s.registers[0][20]=sar(s.registers[0][20],16);zn(&s,s.registers[0][20]);
   s.pc=0xf032aau;break;
  case 0xf032aau: /* sharq   $10,r17 */
   s.c=s.registers[0][17]&1u;s.registers[0][17]=sar(s.registers[0][17],16);zn(&s,s.registers[0][17]);
   s.pc=0xf032acu;break;
  case 0xf032acu: /* add     r20,r17 */
   s.registers[0][17]=add(&s,s.registers[0][17],s.registers[0][20]);
   s.pc=0xf032aeu;break;
  case 0xf032aeu: /* shlq    $10,r21 */
   s.c=s.registers[0][21]>>31;s.registers[0][21]=s.registers[0][21]<<16;zn(&s,s.registers[0][21]);
   s.pc=0xf032b0u;break;
  case 0xf032b0u: /* shlq    $10,r18 */
   s.c=s.registers[0][18]>>31;s.registers[0][18]=s.registers[0][18]<<16;zn(&s,s.registers[0][18]);
   s.pc=0xf032b2u;break;
  case 0xf032b2u: /* sharq   $10,r21 */
   s.c=s.registers[0][21]&1u;s.registers[0][21]=sar(s.registers[0][21],16);zn(&s,s.registers[0][21]);
   s.pc=0xf032b4u;break;
  case 0xf032b4u: /* sharq   $10,r18 */
   s.c=s.registers[0][18]&1u;s.registers[0][18]=sar(s.registers[0][18],16);zn(&s,s.registers[0][18]);
   s.pc=0xf032b6u;break;
  case 0xf032b6u: /* add     r21,r18 */
   s.registers[0][18]=add(&s,s.registers[0][18],s.registers[0][21]);
   s.pc=0xf032b8u;break;
  case 0xf032b8u: /* addq    $4,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],4u);
   s.pc=0xf032bau;break;
  case 0xf032bau: /* subq    $c,r11 */
   s.registers[0][11]=sub(&s,s.registers[0][11],12u);
   s.pc=0xf032bcu;break;
  case 0xf032bcu: /* movei   $f02104,r25 */
   s.registers[0][25]=0xf02104u;
   s.pc=0xf032c2u;break;
  case 0xf032c2u: /* movei   $3,r2 */
   s.registers[0][2]=0x3u;
   s.pc=0xf032c8u;break;
  case 0xf032c8u: /* movei   $f02108,r15 */
   s.registers[0][15]=0xf02108u;
   s.pc=0xf032ceu;break;
  case 0xf032ceu: /* store   r2,(r25) */
   CHECK(wr32(bus,&s,local(s.registers[0][25])?(s.registers[0][25]&~3u):s.registers[0][25],s.registers[0][2]));
   s.pc=0xf032d0u;break;
  case 0xf032d0u: /* movei   $f032fa,r24 */
   s.registers[0][24]=0xf032fau;
   s.pc=0xf032d6u;break;
  case 0xf032d6u: /* moveq   0,r20 */
   s.registers[0][20]=0u;
   s.pc=0xf032d8u;break;
  case 0xf032d8u: /* movei   $f03332,r25 */
   s.registers[0][25]=0xf03332u;
   s.pc=0xf032deu;break;
  case 0xf032deu: /* sub     r17,r20 */
   s.registers[0][20]=sub(&s,s.registers[0][20],s.registers[0][17]);
   s.pc=0xf032e0u;break;
  case 0xf032e0u: /* move    r1,r12 */
   s.registers[0][12]=s.registers[0][1];
   s.pc=0xf032e2u;break;
  case 0xf032e2u: /* shlq    $10,r20 */
   s.c=s.registers[0][20]>>31;s.registers[0][20]=s.registers[0][20]<<16;zn(&s,s.registers[0][20]);
   s.pc=0xf032e4u;break;
  case 0xf032e4u: /* moveq   0,r23 */
   s.registers[0][23]=0u;
   s.pc=0xf032e6u;break;
  case 0xf032e6u: /* movei   $400,r26 */
   s.registers[0][26]=0x400u;
   s.pc=0xf032ecu;break;
  case 0xf032ecu: /* cmpq    $6,r23 */
   (void)sub(&s,s.registers[0][23],0x6u);
   s.pc=0xf032eeu;break;
  case 0xf032eeu: /* jump    z,(r25) */
   if(condition(&s,2)){pending=1;target=s.registers[0][25];}
   s.pc=0xf032f0u;break;
  case 0xf032f0u: /* move    r23,r21 */
   s.registers[0][21]=s.registers[0][23];
   s.pc=0xf032f2u;break;
  case 0xf032f2u: /* moveq   0,r22 */
   s.registers[0][22]=0u;
   s.pc=0xf032f4u;break;
  case 0xf032f4u: /* mult    r26,r21 */
   s.registers[0][21]=(s.registers[0][21]&0xffffu)*(s.registers[0][26]&0xffffu);
   zn(&s,s.registers[0][21]);
   s.pc=0xf032f6u;break;
  case 0xf032f6u: /* addq    $1,r23 */
   s.registers[0][23]=add(&s,s.registers[0][23],1u);
   s.pc=0xf032f8u;break;
  case 0xf032f8u: /* sub     r18,r21 */
   s.registers[0][21]=sub(&s,s.registers[0][21],s.registers[0][18]);
   s.pc=0xf032fau;break;
  case 0xf032fau: /* cmpq    $6,r22 */
   (void)sub(&s,s.registers[0][22],0x6u);
   s.pc=0xf032fcu;break;
  case 0xf032fcu: /* jr      z,00F032EC */
   if(condition(&s,2)){pending=1;target=0xf032ecu;}
   s.pc=0xf032feu;break;
  case 0xf032feu: /* move    r22,r19 */
   s.registers[0][19]=s.registers[0][22];
   s.pc=0xf03300u;break;
  case 0xf03300u: /* mult    r26,r19 */
   s.registers[0][19]=(s.registers[0][19]&0xffffu)*(s.registers[0][26]&0xffffu);
   zn(&s,s.registers[0][19]);
   s.pc=0xf03302u;break;
  case 0xf03302u: /* addq    $1,r22 */
   s.registers[0][22]=add(&s,s.registers[0][22],1u);
   s.pc=0xf03304u;break;
  case 0xf03304u: /* sub     r16,r19 */
   s.registers[0][19]=sub(&s,s.registers[0][19],s.registers[0][16]);
   s.pc=0xf03306u;break;
  case 0xf03306u: /* move    r19,r13 */
   s.registers[0][13]=s.registers[0][19];
   s.pc=0xf03308u;break;
  case 0xf03308u: /* move    r21,r14 */
   s.registers[0][14]=s.registers[0][21];
   s.pc=0xf0330au;break;
  case 0xf0330au: /* and     r3,r13 */
   s.registers[0][13]&=s.registers[0][3];
   zn(&s,s.registers[0][13]);
   s.pc=0xf0330cu;break;
  case 0xf0330cu: /* and     r3,r14 */
   s.registers[0][14]&=s.registers[0][3];
   zn(&s,s.registers[0][14]);
   s.pc=0xf0330eu;break;
  case 0xf0330eu: /* or      r20,r13 */
   s.registers[0][13]|=s.registers[0][20];
   zn(&s,s.registers[0][13]);
   s.pc=0xf03310u;break;
  case 0xf03310u: /* subq    $18,r11 */
   s.registers[0][11]=sub(&s,s.registers[0][11],24u);
   s.pc=0xf03312u;break;
  case 0xf03312u: /* store   r11,(r15) */
   CHECK(wr32(bus,&s,local(s.registers[0][15])?(s.registers[0][15]&~3u):s.registers[0][15],s.registers[0][11]));
   s.pc=0xf03314u;break;
  case 0xf03314u: /* moveta  r13,r13 */
   s.registers[1][13]=s.registers[0][13];
   s.pc=0xf03316u;break;
  case 0xf03316u: /* moveta  r14,r14 */
   s.registers[1][14]=s.registers[0][14];
   s.pc=0xf03318u;break;
  case 0xf03318u: /* mmult   r13,r2 */
   CHECK(matrix(bus,&s,13,2));
   s.pc=0xf0331au;break;
  case 0xf0331au: /* sharq   $e,r2 */
   s.c=s.registers[0][2]&1u;s.registers[0][2]=sar(s.registers[0][2],14);zn(&s,s.registers[0][2]);
   s.pc=0xf0331cu;break;
  case 0xf0331cu: /* store   r2,(r12) */
   CHECK(wr32(bus,&s,local(s.registers[0][12])?(s.registers[0][12]&~3u):s.registers[0][12],s.registers[0][2]));
   s.pc=0xf0331eu;break;
  case 0xf0331eu: /* addq    $4,r12 */
   s.registers[0][12]=add(&s,s.registers[0][12],4u);
   s.pc=0xf03320u;break;
  case 0xf03320u: /* addq    $18,r11 */
   s.registers[0][11]=add(&s,s.registers[0][11],24u);
   s.pc=0xf03322u;break;
  case 0xf03322u: /* store   r11,(r15) */
   CHECK(wr32(bus,&s,local(s.registers[0][15])?(s.registers[0][15]&~3u):s.registers[0][15],s.registers[0][11]));
   s.pc=0xf03324u;break;
  case 0xf03324u: /* moveta  r13,r13 */
   s.registers[1][13]=s.registers[0][13];
   s.pc=0xf03326u;break;
  case 0xf03326u: /* moveta  r14,r14 */
   s.registers[1][14]=s.registers[0][14];
   s.pc=0xf03328u;break;
  case 0xf03328u: /* mmult   r13,r2 */
   CHECK(matrix(bus,&s,13,2));
   s.pc=0xf0332au;break;
  case 0xf0332au: /* sharq   $e,r2 */
   s.c=s.registers[0][2]&1u;s.registers[0][2]=sar(s.registers[0][2],14);zn(&s,s.registers[0][2]);
   s.pc=0xf0332cu;break;
  case 0xf0332cu: /* store   r2,(r12) */
   CHECK(wr32(bus,&s,local(s.registers[0][12])?(s.registers[0][12]&~3u):s.registers[0][12],s.registers[0][2]));
   s.pc=0xf0332eu;break;
  case 0xf0332eu: /* jump    (r24) */
   if(condition(&s,0)){pending=1;target=s.registers[0][24];}
   s.pc=0xf03330u;break;
  case 0xf03330u: /* addq    $4,r12 */
   s.registers[0][12]=add(&s,s.registers[0][12],4u);
   s.pc=0xf03332u;break;
  case 0xf03332u: /* load    (r0),r8 */
   CHECK(rd32(bus,&s,s.registers[0][0]&~3u,&v));s.registers[0][8]=v;
   s.pc=0xf03334u;break;
  case 0xf03334u: /* movei   $f03638,r9 */
   s.registers[0][9]=0xf03638u;
   s.pc=0xf0333au;break;
  case 0xf0333au: /* moveq   3,r21 */
   s.registers[0][21]=3u;
   s.pc=0xf0333cu;break;
  case 0xf0333cu: /* moveq   0,r12 */
   s.registers[0][12]=0u;
   s.pc=0xf0333eu;break;
  case 0xf0333eu: /* shlq    $4,r21 */
   s.c=s.registers[0][21]>>31;s.registers[0][21]=s.registers[0][21]<<4;zn(&s,s.registers[0][21]);
   s.pc=0xf03340u;break;
  case 0xf03340u: /* moveq   0,r13 */
   s.registers[0][13]=0u;
   s.pc=0xf03342u;break;
  case 0xf03342u: /* moveq   30,r22 */
   s.registers[0][22]=30u;
   s.pc=0xf03344u;break;
  case 0xf03344u: /* moveq   0,r23 */
   s.registers[0][23]=0u;
   s.pc=0xf03346u;break;
  case 0xf03346u: /* movei   $e0,r24 */
   s.registers[0][24]=0xe0u;
   s.pc=0xf0334cu;break;
  case 0xf0334cu: /* moveq   31,r25 */
   s.registers[0][25]=31u;
   s.pc=0xf0334eu;break;
  case 0xf0334eu: /* movei   $300,r26 */
   s.registers[0][26]=0x300u;
   s.pc=0xf03354u;break;
  case 0xf03354u: /* move    pc,r10 */
   s.registers[0][10]=0xf03354u;
   s.pc=0xf03356u;break;
  case 0xf03356u: /* move    r10,r11 */
   s.registers[0][11]=s.registers[0][10];
   s.pc=0xf03358u;break;
  case 0xf03358u: /* addq    $8,r10 */
   s.registers[0][10]=add(&s,s.registers[0][10],8u);
   s.pc=0xf0335au;break;
  case 0xf0335au: /* addq    $14,r11 */
   s.registers[0][11]=add(&s,s.registers[0][11],20u);
   s.pc=0xf0335cu;break;
  case 0xf0335cu: /* move    r3,r18 */
   s.registers[0][18]=s.registers[0][3];
   s.pc=0xf0335eu;break;
  case 0xf0335eu: /* moveq   4,r14 */
   s.registers[0][14]=4u;
   s.pc=0xf03360u;break;
  case 0xf03360u: /* move    r3,r17 */
   s.registers[0][17]=s.registers[0][3];
   s.pc=0xf03362u;break;
  case 0xf03362u: /* shlq    $10,r18 */
   s.c=s.registers[0][18]>>31;s.registers[0][18]=s.registers[0][18]<<16;zn(&s,s.registers[0][18]);
   s.pc=0xf03364u;break;
  case 0xf03364u: /* move    r17,r19 */
   s.registers[0][19]=s.registers[0][17];
   s.pc=0xf03366u;break;
  case 0xf03366u: /* move    r18,r20 */
   s.registers[0][20]=s.registers[0][18];
   s.pc=0xf03368u;break;
  case 0xf03368u: /* move    r12,r15 */
   s.registers[0][15]=s.registers[0][12];
   s.pc=0xf0336au;break;
  case 0xf0336au: /* move    r13,r16 */
   s.registers[0][16]=s.registers[0][13];
   s.pc=0xf0336cu;break;
  case 0xf0336cu: /* shlq    $3,r15 */
   s.c=s.registers[0][15]>>31;s.registers[0][15]=s.registers[0][15]<<3;zn(&s,s.registers[0][15]);
   s.pc=0xf0336eu;break;
  case 0xf0336eu: /* imult   r21,r16 */
   s.registers[0][16]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][16])*(int32_t)sx16(s.registers[0][21]));
   zn(&s,s.registers[0][16]);
   s.pc=0xf03370u;break;
  case 0xf03370u: /* load    (r9),r2 */
   CHECK(rd32(bus,&s,s.registers[0][9]&~3u,&v));s.registers[0][2]=v;
   s.pc=0xf03372u;break;
  case 0xf03372u: /* add     r15,r16 */
   s.registers[0][16]=add(&s,s.registers[0][16],s.registers[0][15]);
   s.pc=0xf03374u;break;
  case 0xf03374u: /* add     r1,r2 */
   s.registers[0][2]=add(&s,s.registers[0][2],s.registers[0][1]);
   s.pc=0xf03376u;break;
  case 0xf03376u: /* add     r16,r2 */
   s.registers[0][2]=add(&s,s.registers[0][2],s.registers[0][16]);
   s.pc=0xf03378u;break;
  case 0xf03378u: /* load    (r2),r15 */
   CHECK(rd32(bus,&s,s.registers[0][2]&~3u,&v));s.registers[0][15]=v;
   s.pc=0xf0337au;break;
  case 0xf0337au: /* addq    $4,r2 */
   s.registers[0][2]=add(&s,s.registers[0][2],4u);
   s.pc=0xf0337cu;break;
  case 0xf0337cu: /* load    (r2),r16 */
   CHECK(rd32(bus,&s,s.registers[0][2]&~3u,&v));s.registers[0][16]=v;
   s.pc=0xf0337eu;break;
  case 0xf0337eu: /* imult   r4,r15 */
   s.registers[0][15]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][15])*(int32_t)sx16(s.registers[0][4]));
   zn(&s,s.registers[0][15]);
   s.pc=0xf03380u;break;
  case 0xf03380u: /* cmp     r22,r16 */
   (void)sub(&s,s.registers[0][16],s.registers[0][22]);
   s.pc=0xf03382u;break;
  case 0xf03382u: /* jr      nn,00F03388 */
   if(condition(&s,20)){pending=1;target=0xf03388u;}
   s.pc=0xf03384u;break;
  case 0xf03384u: /* abs     r15 */
   s.c=s.registers[0][15]>>31;if(s.registers[0][15]==0x80000000u){s.n=1;s.z=0;}else{if(s.c)s.registers[0][15]=0u-s.registers[0][15];s.n=0;s.z=s.registers[0][15]==0;}
   s.pc=0xf03386u;break;
  case 0xf03386u: /* move    r22,r16 */
   s.registers[0][16]=s.registers[0][22];
   s.pc=0xf03388u;break;
  case 0xf03388u: /* jr      nc,00F0338E */
   if(condition(&s,4)){pending=1;target=0xf0338eu;}
   s.pc=0xf0338au;break;
  case 0xf0338au: /* div     r16,r15 */
   divide(&s,16,15);
   s.pc=0xf0338cu;break;
  case 0xf0338cu: /* neg     r15 */
   s.registers[0][15]=sub(&s,0,s.registers[0][15]);
   s.pc=0xf0338eu;break;
  case 0xf0338eu: /* cmp     r15,r6 */
   (void)sub(&s,s.registers[0][6],s.registers[0][15]);
   s.pc=0xf03390u;break;
  case 0xf03390u: /* jr      n,00F03396 */
   if(condition(&s,24)){pending=1;target=0xf03396u;}
   s.pc=0xf03392u;break;
  case 0xf03392u: /* cmp     r7,r15 */
   (void)sub(&s,s.registers[0][15],s.registers[0][7]);
   s.pc=0xf03394u;break;
  case 0xf03394u: /* move    r6,r15 */
   s.registers[0][15]=s.registers[0][6];
   s.pc=0xf03396u;break;
  case 0xf03396u: /* jr      n,00F0339C */
   if(condition(&s,24)){pending=1;target=0xf0339cu;}
   s.pc=0xf03398u;break;
  case 0xf03398u: /* nop */
   s.pc=0xf0339au;break;
  case 0xf0339au: /* move    r7,r15 */
   s.registers[0][15]=s.registers[0][7];
   s.pc=0xf0339cu;break;
  case 0xf0339cu: /* add     r5,r15 */
   s.registers[0][15]=add(&s,s.registers[0][15],s.registers[0][5]);
   s.pc=0xf0339eu;break;
  case 0xf0339eu: /* cmp     r15,r17 */
   (void)sub(&s,s.registers[0][17],s.registers[0][15]);
   s.pc=0xf033a0u;break;
  case 0xf033a0u: /* jr      n,00F033A6 */
   if(condition(&s,24)){pending=1;target=0xf033a6u;}
   s.pc=0xf033a2u;break;
  case 0xf033a2u: /* cmp     r18,r15 */
   (void)sub(&s,s.registers[0][15],s.registers[0][18]);
   s.pc=0xf033a4u;break;
  case 0xf033a4u: /* move    r15,r17 */
   s.registers[0][17]=s.registers[0][15];
   s.pc=0xf033a6u;break;
  case 0xf033a6u: /* jr      n,00F033AC */
   if(condition(&s,24)){pending=1;target=0xf033acu;}
   s.pc=0xf033a8u;break;
  case 0xf033a8u: /* cmp     r16,r19 */
   (void)sub(&s,s.registers[0][19],s.registers[0][16]);
   s.pc=0xf033aau;break;
  case 0xf033aau: /* move    r15,r18 */
   s.registers[0][18]=s.registers[0][15];
   s.pc=0xf033acu;break;
  case 0xf033acu: /* jr      n,00F033B2 */
   if(condition(&s,24)){pending=1;target=0xf033b2u;}
   s.pc=0xf033aeu;break;
  case 0xf033aeu: /* cmp     r20,r16 */
   (void)sub(&s,s.registers[0][16],s.registers[0][20]);
   s.pc=0xf033b0u;break;
  case 0xf033b0u: /* move    r16,r19 */
   s.registers[0][19]=s.registers[0][16];
   s.pc=0xf033b2u;break;
  case 0xf033b2u: /* jr      n,00F033B8 */
   if(condition(&s,24)){pending=1;target=0xf033b8u;}
   s.pc=0xf033b4u;break;
  case 0xf033b4u: /* subq    $1,r14 */
   s.registers[0][14]=sub(&s,s.registers[0][14],1u);
   s.pc=0xf033b6u;break;
  case 0xf033b6u: /* move    r16,r20 */
   s.registers[0][20]=s.registers[0][16];
   s.pc=0xf033b8u;break;
  case 0xf033b8u: /* jump    nz,(r11) */
   if(condition(&s,1)){pending=1;target=s.registers[0][11];}
   s.pc=0xf033bau;break;
  case 0xf033bau: /* addq    $4,r9 */
   s.registers[0][9]=add(&s,s.registers[0][9],4u);
   s.pc=0xf033bcu;break;
  case 0xf033bcu: /* load    (r8),r15 */
   CHECK(rd32(bus,&s,s.registers[0][8]&~3u,&v));s.registers[0][15]=v;
   s.pc=0xf033beu;break;
  case 0xf033beu: /* subq    $10,r9 */
   s.registers[0][9]=sub(&s,s.registers[0][9],16u);
   s.pc=0xf033c0u;break;
  case 0xf033c0u: /* cmp     r23,r18 */
   (void)sub(&s,s.registers[0][18],s.registers[0][23]);
   s.pc=0xf033c2u;break;
  case 0xf033c2u: /* jr      n,00F033D6 */
   if(condition(&s,24)){pending=1;target=0xf033d6u;}
   s.pc=0xf033c4u;break;
  case 0xf033c4u: /* cmp     r17,r24 */
   (void)sub(&s,s.registers[0][24],s.registers[0][17]);
   s.pc=0xf033c6u;break;
  case 0xf033c6u: /* jr      n,00F033D6 */
   if(condition(&s,24)){pending=1;target=0xf033d6u;}
   s.pc=0xf033c8u;break;
  case 0xf033c8u: /* cmp     r25,r20 */
   (void)sub(&s,s.registers[0][20],s.registers[0][25]);
   s.pc=0xf033cau;break;
  case 0xf033cau: /* jr      n,00F033D6 */
   if(condition(&s,24)){pending=1;target=0xf033d6u;}
   s.pc=0xf033ccu;break;
  case 0xf033ccu: /* cmp     r19,r26 */
   (void)sub(&s,s.registers[0][26],s.registers[0][19]);
   s.pc=0xf033ceu;break;
  case 0xf033ceu: /* jr      n,00F033D6 */
   if(condition(&s,24)){pending=1;target=0xf033d6u;}
   s.pc=0xf033d0u;break;
  case 0xf033d0u: /* or      r15,r15 */
   s.registers[0][15]|=s.registers[0][15];
   zn(&s,s.registers[0][15]);
   s.pc=0xf033d2u;break;
  case 0xf033d2u: /* jr      00F033D8 */
   if(condition(&s,0)){pending=1;target=0xf033d8u;}
   s.pc=0xf033d4u;break;
  case 0xf033d4u: /* bclr    $1f,r15 */
   s.registers[0][15]&=~(1u<<31);
   zn(&s,s.registers[0][15]);
   s.pc=0xf033d6u;break;
  case 0xf033d6u: /* bset    $1f,r15 */
   s.registers[0][15]|=(1u<<31);
   zn(&s,s.registers[0][15]);
   s.pc=0xf033d8u;break;
  case 0xf033d8u: /* addq    $1,r12 */
   s.registers[0][12]=add(&s,s.registers[0][12],1u);
   s.pc=0xf033dau;break;
  case 0xf033dau: /* cmpq    $5,r12 */
   (void)sub(&s,s.registers[0][12],0x5u);
   s.pc=0xf033dcu;break;
  case 0xf033dcu: /* jr      nz,00F033E4 */
   if(condition(&s,1)){pending=1;target=0xf033e4u;}
   s.pc=0xf033deu;break;
  case 0xf033deu: /* store   r15,(r8) */
   CHECK(wr32(bus,&s,local(s.registers[0][8])?(s.registers[0][8]&~3u):s.registers[0][8],s.registers[0][15]));
   s.pc=0xf033e0u;break;
  case 0xf033e0u: /* addq    $1,r13 */
   s.registers[0][13]=add(&s,s.registers[0][13],1u);
   s.pc=0xf033e2u;break;
  case 0xf033e2u: /* moveq   0,r12 */
   s.registers[0][12]=0u;
   s.pc=0xf033e4u;break;
  case 0xf033e4u: /* cmpq    $5,r13 */
   (void)sub(&s,s.registers[0][13],0x5u);
   s.pc=0xf033e6u;break;
  case 0xf033e6u: /* jump    nz,(r10) */
   if(condition(&s,1)){pending=1;target=s.registers[0][10];}
   s.pc=0xf033e8u;break;
  case 0xf033e8u: /* addq    $4,r8 */
   s.registers[0][8]=add(&s,s.registers[0][8],4u);
   s.pc=0xf033eau;break;
  case 0xf033eau: /* movei   $f03210,r0 */
   s.registers[0][0]=0xf03210u;
   s.pc=0xf033f0u;break;
  case 0xf033f0u: /* load    (r0),r3 */
   CHECK(rd32(bus,&s,s.registers[0][0]&~3u,&v));s.registers[0][3]=v;
   s.pc=0xf033f2u;break;
  case 0xf033f2u: /* moveq   0,r5 */
   s.registers[0][5]=0u;
   s.pc=0xf033f4u;break;
  case 0xf033f4u: /* subq    $4,r0 */
   s.registers[0][0]=sub(&s,s.registers[0][0],4u);
   s.pc=0xf033f6u;break;
  case 0xf033f6u: /* loadw   (r3),r8 */
   CHECK(loadw(bus,&s,s.registers[0][3],&v));s.registers[0][8]=v;
   s.pc=0xf033f8u;break;
  case 0xf033f8u: /* load    (r0),r4 */
   CHECK(rd32(bus,&s,s.registers[0][0]&~3u,&v));s.registers[0][4]=v;
   s.pc=0xf033fau;break;
  case 0xf033fau: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf033fcu;break;
  case 0xf033fcu: /* addq    $8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],8u);
   s.pc=0xf033feu;break;
  case 0xf033feu: /* loadw   (r3),r9 */
   CHECK(loadw(bus,&s,s.registers[0][3],&v));s.registers[0][9]=v;
   s.pc=0xf03400u;break;
  case 0xf03400u: /* load    (r0),r6 */
   CHECK(rd32(bus,&s,s.registers[0][0]&~3u,&v));s.registers[0][6]=v;
   s.pc=0xf03402u;break;
  case 0xf03402u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf03404u;break;
  case 0xf03404u: /* addq    $4,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],4u);
   s.pc=0xf03406u;break;
  case 0xf03406u: /* loadw   (r3),r10 */
   CHECK(loadw(bus,&s,s.registers[0][3],&v));s.registers[0][10]=v;
   s.pc=0xf03408u;break;
  case 0xf03408u: /* shlq    $10,r8 */
   s.c=s.registers[0][8]>>31;s.registers[0][8]=s.registers[0][8]<<16;zn(&s,s.registers[0][8]);
   s.pc=0xf0340au;break;
  case 0xf0340au: /* shlq    $10,r9 */
   s.c=s.registers[0][9]>>31;s.registers[0][9]=s.registers[0][9]<<16;zn(&s,s.registers[0][9]);
   s.pc=0xf0340cu;break;
  case 0xf0340cu: /* shlq    $10,r10 */
   s.c=s.registers[0][10]>>31;s.registers[0][10]=s.registers[0][10]<<16;zn(&s,s.registers[0][10]);
   s.pc=0xf0340eu;break;
  case 0xf0340eu: /* sharq   $10,r8 */
   s.c=s.registers[0][8]&1u;s.registers[0][8]=sar(s.registers[0][8],16);zn(&s,s.registers[0][8]);
   s.pc=0xf03410u;break;
  case 0xf03410u: /* sharq   $10,r9 */
   s.c=s.registers[0][9]&1u;s.registers[0][9]=sar(s.registers[0][9],16);zn(&s,s.registers[0][9]);
   s.pc=0xf03412u;break;
  case 0xf03412u: /* sharq   $10,r10 */
   s.c=s.registers[0][10]&1u;s.registers[0][10]=sar(s.registers[0][10],16);zn(&s,s.registers[0][10]);
   s.pc=0xf03414u;break;
  case 0xf03414u: /* moveq   0,r12 */
   s.registers[0][12]=0u;
   s.pc=0xf03416u;break;
  case 0xf03416u: /* moveq   0,r11 */
   s.registers[0][11]=0u;
   s.pc=0xf03418u;break;
  case 0xf03418u: /* load    (r6),r7 */
   CHECK(rd32(bus,&s,s.registers[0][6]&~3u,&v));s.registers[0][7]=v;
   s.pc=0xf0341au;break;
  case 0xf0341au: /* movei   $f0356a,r3 */
   s.registers[0][3]=0xf0356au;
   s.pc=0xf03420u;break;
  case 0xf03420u: /* btst    $1f,r7 */
   s.z=((~s.registers[0][7])>>31)&1u;
   s.pc=0xf03422u;break;
  case 0xf03422u: /* jump    nz,(r3) */
   if(condition(&s,1)){pending=1;target=s.registers[0][3];}
   s.pc=0xf03424u;break;
  case 0xf03424u: /* addq    $4,r6 */
   s.registers[0][6]=add(&s,s.registers[0][6],4u);
   s.pc=0xf03426u;break;
  case 0xf03426u: /* addq    $8,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],8u);
   s.pc=0xf03428u;break;
  case 0xf03428u: /* load    (r7),r13 */
   CHECK(rd32(bus,&s,s.registers[0][7]&~3u,&v));s.registers[0][13]=v;
   s.pc=0xf0342au;break;
  case 0xf0342au: /* addq    $4,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],4u);
   s.pc=0xf0342cu;break;
  case 0xf0342cu: /* load    (r7),r14 */
   CHECK(rd32(bus,&s,s.registers[0][7]&~3u,&v));s.registers[0][14]=v;
   s.pc=0xf0342eu;break;
  case 0xf0342eu: /* addq    $4,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],4u);
   s.pc=0xf03430u;break;
  case 0xf03430u: /* load    (r7),r15 */
   CHECK(rd32(bus,&s,s.registers[0][7]&~3u,&v));s.registers[0][15]=v;
   s.pc=0xf03432u;break;
  case 0xf03432u: /* subq    $10,r7 */
   s.registers[0][7]=sub(&s,s.registers[0][7],16u);
   s.pc=0xf03434u;break;
  case 0xf03434u: /* moveq   0,r16 */
   s.registers[0][16]=0u;
   s.pc=0xf03436u;break;
  case 0xf03436u: /* loadw   (r7),r17 */
   CHECK(loadw(bus,&s,s.registers[0][7],&v));s.registers[0][17]=v;
   s.pc=0xf03438u;break;
  case 0xf03438u: /* movei   $f0356a,r3 */
   s.registers[0][3]=0xf0356au;
   s.pc=0xf0343eu;break;
  case 0xf0343eu: /* cmp     r16,r17 */
   (void)sub(&s,s.registers[0][17],s.registers[0][16]);
   s.pc=0xf03440u;break;
  case 0xf03440u: /* jump    z,(r3) */
   if(condition(&s,2)){pending=1;target=s.registers[0][3];}
   s.pc=0xf03442u;break;
  case 0xf03442u: /* nop */
   s.pc=0xf03444u;break;
  case 0xf03444u: /* addq    $a,r13 */
   s.registers[0][13]=add(&s,s.registers[0][13],10u);
   s.pc=0xf03446u;break;
  case 0xf03446u: /* movei   $40,r1 */
   s.registers[0][1]=0x40u;
   s.pc=0xf0344cu;break;
  case 0xf0344cu: /* loadw   (r13),r18 */
   CHECK(loadw(bus,&s,s.registers[0][13],&v));s.registers[0][18]=v;
   s.pc=0xf0344eu;break;
  case 0xf0344eu: /* addq    $2,r13 */
   s.registers[0][13]=add(&s,s.registers[0][13],2u);
   s.pc=0xf03450u;break;
  case 0xf03450u: /* imult   r1,r18 */
   s.registers[0][18]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][18])*(int32_t)sx16(s.registers[0][1]));
   zn(&s,s.registers[0][18]);
   s.pc=0xf03452u;break;
  case 0xf03452u: /* loadw   (r13),r19 */
   CHECK(loadw(bus,&s,s.registers[0][13],&v));s.registers[0][19]=v;
   s.pc=0xf03454u;break;
  case 0xf03454u: /* addq    $2,r13 */
   s.registers[0][13]=add(&s,s.registers[0][13],2u);
   s.pc=0xf03456u;break;
  case 0xf03456u: /* imult   r1,r19 */
   s.registers[0][19]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][19])*(int32_t)sx16(s.registers[0][1]));
   zn(&s,s.registers[0][19]);
   s.pc=0xf03458u;break;
  case 0xf03458u: /* loadw   (r13),r20 */
   CHECK(loadw(bus,&s,s.registers[0][13],&v));s.registers[0][20]=v;
   s.pc=0xf0345au;break;
  case 0xf0345au: /* addq    $2,r13 */
   s.registers[0][13]=add(&s,s.registers[0][13],2u);
   s.pc=0xf0345cu;break;
  case 0xf0345cu: /* imult   r1,r20 */
   s.registers[0][20]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][20])*(int32_t)sx16(s.registers[0][1]));
   zn(&s,s.registers[0][20]);
   s.pc=0xf0345eu;break;
  case 0xf0345eu: /* loadw   (r13),r21 */
   CHECK(loadw(bus,&s,s.registers[0][13],&v));s.registers[0][21]=v;
   s.pc=0xf03460u;break;
  case 0xf03460u: /* addq    $2,r13 */
   s.registers[0][13]=add(&s,s.registers[0][13],2u);
   s.pc=0xf03462u;break;
  case 0xf03462u: /* imult   r1,r21 */
   s.registers[0][21]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][21])*(int32_t)sx16(s.registers[0][1]));
   zn(&s,s.registers[0][21]);
   s.pc=0xf03464u;break;
  case 0xf03464u: /* loadw   (r13),r22 */
   CHECK(loadw(bus,&s,s.registers[0][13],&v));s.registers[0][22]=v;
   s.pc=0xf03466u;break;
  case 0xf03466u: /* subq    $12,r13 */
   s.registers[0][13]=sub(&s,s.registers[0][13],18u);
   s.pc=0xf03468u;break;
  case 0xf03468u: /* imult   r1,r22 */
   s.registers[0][22]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][22])*(int32_t)sx16(s.registers[0][1]));
   zn(&s,s.registers[0][22]);
   s.pc=0xf0346au;break;
  case 0xf0346au: /* movei   $400,r3 */
   s.registers[0][3]=0x400u;
   s.pc=0xf03470u;break;
  case 0xf03470u: /* move    r11,r1 */
   s.registers[0][1]=s.registers[0][11];
   s.pc=0xf03472u;break;
  case 0xf03472u: /* move    r12,r2 */
   s.registers[0][2]=s.registers[0][12];
   s.pc=0xf03474u;break;
  case 0xf03474u: /* imult   r3,r1 */
   s.registers[0][1]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][1])*(int32_t)sx16(s.registers[0][3]));
   zn(&s,s.registers[0][1]);
   s.pc=0xf03476u;break;
  case 0xf03476u: /* imult   r3,r2 */
   s.registers[0][2]=(uint32_t)((int64_t)(int32_t)sx16(s.registers[0][2])*(int32_t)sx16(s.registers[0][3]));
   zn(&s,s.registers[0][2]);
   s.pc=0xf03478u;break;
  case 0xf03478u: /* add     r1,r18 */
   s.registers[0][18]=add(&s,s.registers[0][18],s.registers[0][1]);
   s.pc=0xf0347au;break;
  case 0xf0347au: /* add     r2,r20 */
   s.registers[0][20]=add(&s,s.registers[0][20],s.registers[0][2]);
   s.pc=0xf0347cu;break;
  case 0xf0347cu: /* sub     r8,r18 */
   s.registers[0][18]=sub(&s,s.registers[0][18],s.registers[0][8]);
   s.pc=0xf0347eu;break;
  case 0xf0347eu: /* sub     r9,r19 */
   s.registers[0][19]=sub(&s,s.registers[0][19],s.registers[0][9]);
   s.pc=0xf03480u;break;
  case 0xf03480u: /* sub     r10,r20 */
   s.registers[0][20]=sub(&s,s.registers[0][20],s.registers[0][10]);
   s.pc=0xf03482u;break;
  case 0xf03482u: /* moveq   0,r23 */
   s.registers[0][23]=0u;
   s.pc=0xf03484u;break;
  case 0xf03484u: /* moveq   1,r24 */
   s.registers[0][24]=1u;
   s.pc=0xf03486u;break;
  case 0xf03486u: /* movei   $f03592,r3 */
   s.registers[0][3]=0xf03592u;
   s.pc=0xf0348cu;break;
  case 0xf0348cu: /* move    pc,r25 */
   s.registers[0][25]=0xf0348cu;
   s.pc=0xf0348eu;break;
  case 0xf0348eu: /* jump    (r3) */
   if(condition(&s,0)){pending=1;target=s.registers[0][3];}
   s.pc=0xf03490u;break;
  case 0xf03490u: /* addq    $6,r25 */
   s.registers[0][25]=add(&s,s.registers[0][25],6u);
   s.pc=0xf03492u;break;
  case 0xf03492u: /* move    r4,r3 */
   s.registers[0][3]=s.registers[0][4];
   s.pc=0xf03494u;break;
  case 0xf03494u: /* addq    $4,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],4u);
   s.pc=0xf03496u;break;
  case 0xf03496u: /* addq    $6,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],6u);
   s.pc=0xf03498u;break;
  case 0xf03498u: /* storew  r22,(r4) */
   CHECK(wr16(bus,&s,s.registers[0][4],s.registers[0][22]));
   s.pc=0xf0349au;break;
  case 0xf0349au: /* storew  r21,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][21]));
   s.pc=0xf0349cu;break;
  case 0xf0349cu: /* addq    $6,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],6u);
   s.pc=0xf0349eu;break;
  case 0xf0349eu: /* addq    $6,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],6u);
   s.pc=0xf034a0u;break;
  case 0xf034a0u: /* storew  r22,(r4) */
   CHECK(wr16(bus,&s,s.registers[0][4],s.registers[0][22]));
   s.pc=0xf034a2u;break;
  case 0xf034a2u: /* storew  r21,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][21]));
   s.pc=0xf034a4u;break;
  case 0xf034a4u: /* subq    $e,r4 */
   s.registers[0][4]=sub(&s,s.registers[0][4],14u);
   s.pc=0xf034a6u;break;
  case 0xf034a6u: /* subq    $20,r4 */
   s.registers[0][4]=sub(&s,s.registers[0][4],32u);
   s.pc=0xf034a8u;break;
  case 0xf034a8u: /* add     r22,r20 */
   s.registers[0][20]=add(&s,s.registers[0][20],s.registers[0][22]);
   s.pc=0xf034aau;break;
  case 0xf034aau: /* moveq   2,r23 */
   s.registers[0][23]=2u;
   s.pc=0xf034acu;break;
  case 0xf034acu: /* moveq   2,r24 */
   s.registers[0][24]=2u;
   s.pc=0xf034aeu;break;
  case 0xf034aeu: /* movei   $f034d6,r26 */
   s.registers[0][26]=0xf034d6u;
   s.pc=0xf034b4u;break;
  case 0xf034b4u: /* movei   $f03592,r3 */
   s.registers[0][3]=0xf03592u;
   s.pc=0xf034bau;break;
  case 0xf034bau: /* move    pc,r25 */
   s.registers[0][25]=0xf034bau;
   s.pc=0xf034bcu;break;
  case 0xf034bcu: /* jump    (r3) */
   if(condition(&s,0)){pending=1;target=s.registers[0][3];}
   s.pc=0xf034beu;break;
  case 0xf034beu: /* addq    $6,r25 */
   s.registers[0][25]=add(&s,s.registers[0][25],6u);
   s.pc=0xf034c0u;break;
  case 0xf034c0u: /* move    r4,r3 */
   s.registers[0][3]=s.registers[0][4];
   s.pc=0xf034c2u;break;
  case 0xf034c2u: /* addq    $2,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],2u);
   s.pc=0xf034c4u;break;
  case 0xf034c4u: /* addq    $6,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],6u);
   s.pc=0xf034c6u;break;
  case 0xf034c6u: /* storew  r23,(r4) */
   CHECK(wr16(bus,&s,s.registers[0][4],s.registers[0][23]));
   s.pc=0xf034c8u;break;
  case 0xf034c8u: /* storew  r21,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][21]));
   s.pc=0xf034cau;break;
  case 0xf034cau: /* addq    $6,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],6u);
   s.pc=0xf034ccu;break;
  case 0xf034ccu: /* addq    $6,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],6u);
   s.pc=0xf034ceu;break;
  case 0xf034ceu: /* storew  r23,(r4) */
   CHECK(wr16(bus,&s,s.registers[0][4],s.registers[0][23]));
   s.pc=0xf034d0u;break;
  case 0xf034d0u: /* storew  r21,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][21]));
   s.pc=0xf034d2u;break;
  case 0xf034d2u: /* subq    $c,r4 */
   s.registers[0][4]=sub(&s,s.registers[0][4],12u);
   s.pc=0xf034d4u;break;
  case 0xf034d4u: /* subq    $20,r4 */
   s.registers[0][4]=sub(&s,s.registers[0][4],32u);
   s.pc=0xf034d6u;break;
  case 0xf034d6u: /* sub     r22,r20 */
   s.registers[0][20]=sub(&s,s.registers[0][20],s.registers[0][22]);
   s.pc=0xf034d8u;break;
  case 0xf034d8u: /* moveq   4,r23 */
   s.registers[0][23]=4u;
   s.pc=0xf034dau;break;
  case 0xf034dau: /* moveq   4,r24 */
   s.registers[0][24]=4u;
   s.pc=0xf034dcu;break;
  case 0xf034dcu: /* movei   $f03502,r26 */
   s.registers[0][26]=0xf03502u;
   s.pc=0xf034e2u;break;
  case 0xf034e2u: /* movei   $f03592,r3 */
   s.registers[0][3]=0xf03592u;
   s.pc=0xf034e8u;break;
  case 0xf034e8u: /* move    pc,r25 */
   s.registers[0][25]=0xf034e8u;
   s.pc=0xf034eau;break;
  case 0xf034eau: /* jump    (r3) */
   if(condition(&s,0)){pending=1;target=s.registers[0][3];}
   s.pc=0xf034ecu;break;
  case 0xf034ecu: /* addq    $6,r25 */
   s.registers[0][25]=add(&s,s.registers[0][25],6u);
   s.pc=0xf034eeu;break;
  case 0xf034eeu: /* move    r4,r3 */
   s.registers[0][3]=s.registers[0][4];
   s.pc=0xf034f0u;break;
  case 0xf034f0u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf034f2u;break;
  case 0xf034f2u: /* storew  r21,(r4) */
   CHECK(wr16(bus,&s,s.registers[0][4],s.registers[0][21]));
   s.pc=0xf034f4u;break;
  case 0xf034f4u: /* storew  r23,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][23]));
   s.pc=0xf034f6u;break;
  case 0xf034f6u: /* addq    $8,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],8u);
   s.pc=0xf034f8u;break;
  case 0xf034f8u: /* addq    $10,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],16u);
   s.pc=0xf034fau;break;
  case 0xf034fau: /* storew  r23,(r4) */
   CHECK(wr16(bus,&s,s.registers[0][4],s.registers[0][23]));
   s.pc=0xf034fcu;break;
  case 0xf034fcu: /* storew  r21,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][21]));
   s.pc=0xf034feu;break;
  case 0xf034feu: /* subq    $c,r4 */
   s.registers[0][4]=sub(&s,s.registers[0][4],12u);
   s.pc=0xf03500u;break;
  case 0xf03500u: /* subq    $20,r4 */
   s.registers[0][4]=sub(&s,s.registers[0][4],32u);
   s.pc=0xf03502u;break;
  case 0xf03502u: /* add     r21,r18 */
   s.registers[0][18]=add(&s,s.registers[0][18],s.registers[0][21]);
   s.pc=0xf03504u;break;
  case 0xf03504u: /* moveq   6,r23 */
   s.registers[0][23]=6u;
   s.pc=0xf03506u;break;
  case 0xf03506u: /* moveq   3,r24 */
   s.registers[0][24]=3u;
   s.pc=0xf03508u;break;
  case 0xf03508u: /* movei   $f03530,r26 */
   s.registers[0][26]=0xf03530u;
   s.pc=0xf0350eu;break;
  case 0xf0350eu: /* movei   $f03592,r3 */
   s.registers[0][3]=0xf03592u;
   s.pc=0xf03514u;break;
  case 0xf03514u: /* move    pc,r25 */
   s.registers[0][25]=0xf03514u;
   s.pc=0xf03516u;break;
  case 0xf03516u: /* jump    (r3) */
   if(condition(&s,0)){pending=1;target=s.registers[0][3];}
   s.pc=0xf03518u;break;
  case 0xf03518u: /* addq    $6,r25 */
   s.registers[0][25]=add(&s,s.registers[0][25],6u);
   s.pc=0xf0351au;break;
  case 0xf0351au: /* move    r4,r3 */
   s.registers[0][3]=s.registers[0][4];
   s.pc=0xf0351cu;break;
  case 0xf0351cu: /* addq    $2,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],2u);
   s.pc=0xf0351eu;break;
  case 0xf0351eu: /* addq    $4,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],4u);
   s.pc=0xf03520u;break;
  case 0xf03520u: /* storew  r23,(r4) */
   CHECK(wr16(bus,&s,s.registers[0][4],s.registers[0][23]));
   s.pc=0xf03522u;break;
  case 0xf03522u: /* storew  r22,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][22]));
   s.pc=0xf03524u;break;
  case 0xf03524u: /* addq    $6,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],6u);
   s.pc=0xf03526u;break;
  case 0xf03526u: /* addq    $12,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],18u);
   s.pc=0xf03528u;break;
  case 0xf03528u: /* storew  r23,(r4) */
   CHECK(wr16(bus,&s,s.registers[0][4],s.registers[0][23]));
   s.pc=0xf0352au;break;
  case 0xf0352au: /* storew  r22,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][22]));
   s.pc=0xf0352cu;break;
  case 0xf0352cu: /* subq    $c,r4 */
   s.registers[0][4]=sub(&s,s.registers[0][4],12u);
   s.pc=0xf0352eu;break;
  case 0xf0352eu: /* subq    $20,r4 */
   s.registers[0][4]=sub(&s,s.registers[0][4],32u);
   s.pc=0xf03530u;break;
  case 0xf03530u: /* sub     r21,r18 */
   s.registers[0][18]=sub(&s,s.registers[0][18],s.registers[0][21]);
   s.pc=0xf03532u;break;
  case 0xf03532u: /* moveq   8,r23 */
   s.registers[0][23]=8u;
   s.pc=0xf03534u;break;
  case 0xf03534u: /* moveq   5,r24 */
   s.registers[0][24]=5u;
   s.pc=0xf03536u;break;
  case 0xf03536u: /* movei   $f0355e,r26 */
   s.registers[0][26]=0xf0355eu;
   s.pc=0xf0353cu;break;
  case 0xf0353cu: /* movei   $f03592,r3 */
   s.registers[0][3]=0xf03592u;
   s.pc=0xf03542u;break;
  case 0xf03542u: /* move    pc,r25 */
   s.registers[0][25]=0xf03542u;
   s.pc=0xf03544u;break;
  case 0xf03544u: /* jump    (r3) */
   if(condition(&s,0)){pending=1;target=s.registers[0][3];}
   s.pc=0xf03546u;break;
  case 0xf03546u: /* addq    $6,r25 */
   s.registers[0][25]=add(&s,s.registers[0][25],6u);
   s.pc=0xf03548u;break;
  case 0xf03548u: /* move    r4,r3 */
   s.registers[0][3]=s.registers[0][4];
   s.pc=0xf0354au;break;
  case 0xf0354au: /* addq    $2,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],2u);
   s.pc=0xf0354cu;break;
  case 0xf0354cu: /* addq    $a,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],10u);
   s.pc=0xf0354eu;break;
  case 0xf0354eu: /* storew  r23,(r4) */
   CHECK(wr16(bus,&s,s.registers[0][4],s.registers[0][23]));
   s.pc=0xf03550u;break;
  case 0xf03550u: /* storew  r22,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][22]));
   s.pc=0xf03552u;break;
  case 0xf03552u: /* addq    $6,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],6u);
   s.pc=0xf03554u;break;
  case 0xf03554u: /* addq    $6,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],6u);
   s.pc=0xf03556u;break;
  case 0xf03556u: /* storew  r23,(r4) */
   CHECK(wr16(bus,&s,s.registers[0][4],s.registers[0][23]));
   s.pc=0xf03558u;break;
  case 0xf03558u: /* storew  r22,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][22]));
   s.pc=0xf0355au;break;
  case 0xf0355au: /* subq    $c,r4 */
   s.registers[0][4]=sub(&s,s.registers[0][4],12u);
   s.pc=0xf0355cu;break;
  case 0xf0355cu: /* subq    $20,r4 */
   s.registers[0][4]=sub(&s,s.registers[0][4],32u);
   s.pc=0xf0355eu;break;
  case 0xf0355eu: /* movei   $f03438,r3 */
   s.registers[0][3]=0xf03438u;
   s.pc=0xf03564u;break;
  case 0xf03564u: /* addq    $1,r16 */
   s.registers[0][16]=add(&s,s.registers[0][16],1u);
   s.pc=0xf03566u;break;
  case 0xf03566u: /* jump    (r3) */
   if(condition(&s,0)){pending=1;target=s.registers[0][3];}
   s.pc=0xf03568u;break;
  case 0xf03568u: /* addq    $14,r13 */
   s.registers[0][13]=add(&s,s.registers[0][13],20u);
   s.pc=0xf0356au;break;
  case 0xf0356au: /* movei   $f03418,r3 */
   s.registers[0][3]=0xf03418u;
   s.pc=0xf03570u;break;
  case 0xf03570u: /* cmpq    $4,r11 */
   (void)sub(&s,s.registers[0][11],0x4u);
   s.pc=0xf03572u;break;
  case 0xf03572u: /* jump    nz,(r3) */
   if(condition(&s,1)){pending=1;target=s.registers[0][3];}
   s.pc=0xf03574u;break;
  case 0xf03574u: /* addq    $1,r11 */
   s.registers[0][11]=add(&s,s.registers[0][11],1u);
   s.pc=0xf03576u;break;
  case 0xf03576u: /* cmpq    $4,r12 */
   (void)sub(&s,s.registers[0][12],0x4u);
   s.pc=0xf03578u;break;
  case 0xf03578u: /* moveq   0,r11 */
   s.registers[0][11]=0u;
   s.pc=0xf0357au;break;
  case 0xf0357au: /* jump    nz,(r3) */
   if(condition(&s,1)){pending=1;target=s.registers[0][3];}
   s.pc=0xf0357cu;break;
  case 0xf0357cu: /* addq    $1,r12 */
   s.registers[0][12]=add(&s,s.registers[0][12],1u);
   s.pc=0xf0357eu;break;
  case 0xf0357eu: /* addq    $18,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],24u);
   s.pc=0xf03580u;break;
  case 0xf03580u: /* moveq   0,r1 */
   s.registers[0][1]=0u;
   s.pc=0xf03582u;break;
  case 0xf03582u: /* load    (r0),r3 */
   CHECK(rd32(bus,&s,s.registers[0][0]&~3u,&v));s.registers[0][3]=v;
   s.pc=0xf03584u;break;
  case 0xf03584u: /* movei   $f031be,r2 */
   s.registers[0][2]=0xf031beu;
   s.pc=0xf0358au;break;
  case 0xf0358au: /* storew  r1,(r4) */
   CHECK(wr16(bus,&s,s.registers[0][4],s.registers[0][1]));
   s.pc=0xf0358cu;break;
  case 0xf0358cu: /* store   r5,(r3) */
   CHECK(wr32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],s.registers[0][5]));
   s.pc=0xf0358eu;break;
  case 0xf0358eu: /* jump    (r2) */
   if(condition(&s,0)){pending=1;target=s.registers[0][2];}
   s.pc=0xf03590u;break;
  case 0xf03590u: /* nop */
   s.pc=0xf03592u;break;
  case 0xf03592u: /* movei   $f035de,r3 */
   s.registers[0][3]=0xf035deu;
   s.pc=0xf03598u;break;
  case 0xf03598u: /* cmpq    $0,r23 */
   (void)sub(&s,s.registers[0][23],0x0u);
   s.pc=0xf0359au;break;
  case 0xf0359au: /* jump    z,(r3) */
   if(condition(&s,2)){pending=1;target=s.registers[0][3];}
   s.pc=0xf0359cu;break;
  case 0xf0359cu: /* nop */
   s.pc=0xf0359eu;break;
  case 0xf0359eu: /* add     r23,r13 */
   s.registers[0][13]=add(&s,s.registers[0][13],s.registers[0][23]);
   s.pc=0xf035a0u;break;
  case 0xf035a0u: /* movei   $f000,r1 */
   s.registers[0][1]=0xf000u;
   s.pc=0xf035a6u;break;
  case 0xf035a6u: /* loadw   (r13),r27 */
   CHECK(loadw(bus,&s,s.registers[0][13],&v));s.registers[0][27]=v;
   s.pc=0xf035a8u;break;
  case 0xf035a8u: /* movei   $1000,r2 */
   s.registers[0][2]=0x1000u;
   s.pc=0xf035aeu;break;
  case 0xf035aeu: /* and     r27,r1 */
   s.registers[0][1]&=s.registers[0][27];
   zn(&s,s.registers[0][1]);
   s.pc=0xf035b0u;break;
  case 0xf035b0u: /* sub     r23,r13 */
   s.registers[0][13]=sub(&s,s.registers[0][13],s.registers[0][23]);
   s.pc=0xf035b2u;break;
  case 0xf035b2u: /* cmp     r2,r1 */
   (void)sub(&s,s.registers[0][1],s.registers[0][2]);
   s.pc=0xf035b4u;break;
  case 0xf035b4u: /* jump    nz,(r26) */
   if(condition(&s,1)){pending=1;target=s.registers[0][26];}
   s.pc=0xf035b6u;break;
  case 0xf035b6u: /* nop */
   s.pc=0xf035b8u;break;
  case 0xf035b8u: /* movei   $fff,r2 */
   s.registers[0][2]=0xfffu;
   s.pc=0xf035beu;break;
  case 0xf035beu: /* moveq   28,r1 */
   s.registers[0][1]=28u;
   s.pc=0xf035c0u;break;
  case 0xf035c0u: /* and     r2,r27 */
   s.registers[0][27]&=s.registers[0][2];
   zn(&s,s.registers[0][27]);
   s.pc=0xf035c2u;break;
  case 0xf035c2u: /* move    r14,r3 */
   s.registers[0][3]=s.registers[0][14];
   s.pc=0xf035c4u;break;
  case 0xf035c4u: /* mult    r1,r27 */
   s.registers[0][27]=(s.registers[0][27]&0xffffu)*(s.registers[0][1]&0xffffu);
   zn(&s,s.registers[0][27]);
   s.pc=0xf035c6u;break;
  case 0xf035c6u: /* addq    $8,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],8u);
   s.pc=0xf035c8u;break;
  case 0xf035c8u: /* add     r27,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],s.registers[0][27]);
   s.pc=0xf035cau;break;
  case 0xf035cau: /* loadw   (r3),r23 */
   CHECK(loadw(bus,&s,s.registers[0][3],&v));s.registers[0][23]=v;
   s.pc=0xf035ccu;break;
  case 0xf035ccu: /* or      r23,r23 */
   s.registers[0][23]|=s.registers[0][23];
   zn(&s,s.registers[0][23]);
   s.pc=0xf035ceu;break;
  case 0xf035ceu: /* cmpq    $6,r23 */
   (void)sub(&s,s.registers[0][23],0x6u);
   s.pc=0xf035d0u;break;
  case 0xf035d0u: /* jr      n,00F035D6 */
   if(condition(&s,24)){pending=1;target=0xf035d6u;}
   s.pc=0xf035d2u;break;
  case 0xf035d2u: /* nop */
   s.pc=0xf035d4u;break;
  case 0xf035d4u: /* moveq   5,r23 */
   s.registers[0][23]=5u;
   s.pc=0xf035d6u;break;
  case 0xf035d6u: /* neg     r23 */
   s.registers[0][23]=sub(&s,0,s.registers[0][23]);
   s.pc=0xf035d8u;break;
  case 0xf035d8u: /* cmpq    $0,r23 */
   (void)sub(&s,s.registers[0][23],0x0u);
   s.pc=0xf035dau;break;
  case 0xf035dau: /* jump    z,(r26) */
   if(condition(&s,2)){pending=1;target=s.registers[0][26];}
   s.pc=0xf035dcu;break;
  case 0xf035dcu: /* shlq    $6,r23 */
   s.c=s.registers[0][23]>>31;s.registers[0][23]=s.registers[0][23]<<6;zn(&s,s.registers[0][23]);
   s.pc=0xf035deu;break;
  case 0xf035deu: /* addq    $1,r5 */
   s.registers[0][5]=add(&s,s.registers[0][5],1u);
   s.pc=0xf035e0u;break;
  case 0xf035e0u: /* addq    $18,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],24u);
   s.pc=0xf035e2u;break;
  case 0xf035e2u: /* moveq   1,r1 */
   s.registers[0][1]=1u;
   s.pc=0xf035e4u;break;
  case 0xf035e4u: /* storew  r5,(r4) */
   CHECK(wr16(bus,&s,s.registers[0][4],s.registers[0][5]));
   s.pc=0xf035e6u;break;
  case 0xf035e6u: /* moveq   0,r2 */
   s.registers[0][2]=0u;
   s.pc=0xf035e8u;break;
  case 0xf035e8u: /* addq    $20,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],32u);
   s.pc=0xf035eau;break;
  case 0xf035eau: /* shlq    $1e,r1 */
   s.c=s.registers[0][1]>>31;s.registers[0][1]=s.registers[0][1]<<30;zn(&s,s.registers[0][1]);
   s.pc=0xf035ecu;break;
  case 0xf035ecu: /* addq    $8,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],8u);
   s.pc=0xf035eeu;break;
  case 0xf035eeu: /* move    r4,r3 */
   s.registers[0][3]=s.registers[0][4];
   s.pc=0xf035f0u;break;
  case 0xf035f0u: /* addq    $4,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],4u);
   s.pc=0xf035f2u;break;
  case 0xf035f2u: /* store   r1,(r4) */
   CHECK(wr32(bus,&s,local(s.registers[0][4])?(s.registers[0][4]&~3u):s.registers[0][4],s.registers[0][1]));
   s.pc=0xf035f4u;break;
  case 0xf035f4u: /* store   r2,(r3) */
   CHECK(wr32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],s.registers[0][2]));
   s.pc=0xf035f6u;break;
  case 0xf035f6u: /* addq    $8,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],8u);
   s.pc=0xf035f8u;break;
  case 0xf035f8u: /* addq    $8,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],8u);
   s.pc=0xf035fau;break;
  case 0xf035fau: /* store   r1,(r4) */
   CHECK(wr32(bus,&s,local(s.registers[0][4])?(s.registers[0][4]&~3u):s.registers[0][4],s.registers[0][1]));
   s.pc=0xf035fcu;break;
  case 0xf035fcu: /* store   r2,(r3) */
   CHECK(wr32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],s.registers[0][2]));
   s.pc=0xf035feu;break;
  case 0xf035feu: /* addq    $8,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],8u);
   s.pc=0xf03600u;break;
  case 0xf03600u: /* shrq    $10,r1 */
   s.c=s.registers[0][1]&1u;s.registers[0][1]=s.registers[0][1]>>16;zn(&s,s.registers[0][1]);
   s.pc=0xf03602u;break;
  case 0xf03602u: /* addq    $6,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],6u);
   s.pc=0xf03604u;break;
  case 0xf03604u: /* storew  r1,(r4) */
   CHECK(wr16(bus,&s,s.registers[0][4],s.registers[0][1]));
   s.pc=0xf03606u;break;
  case 0xf03606u: /* storew  r18,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][18]));
   s.pc=0xf03608u;break;
  case 0xf03608u: /* addq    $4,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],4u);
   s.pc=0xf0360au;break;
  case 0xf0360au: /* addq    $4,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],4u);
   s.pc=0xf0360cu;break;
  case 0xf0360cu: /* storew  r19,(r4) */
   CHECK(wr16(bus,&s,s.registers[0][4],s.registers[0][19]));
   s.pc=0xf0360eu;break;
  case 0xf0360eu: /* storew  r20,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][20]));
   s.pc=0xf03610u;break;
  case 0xf03610u: /* addq    $4,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],4u);
   s.pc=0xf03612u;break;
  case 0xf03612u: /* addq    $6,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],6u);
   s.pc=0xf03614u;break;
  case 0xf03614u: /* move    r24,r1 */
   s.registers[0][1]=s.registers[0][24];
   s.pc=0xf03616u;break;
  case 0xf03616u: /* store   r2,(r4) */
   CHECK(wr32(bus,&s,local(s.registers[0][4])?(s.registers[0][4]&~3u):s.registers[0][4],s.registers[0][2]));
   s.pc=0xf03618u;break;
  case 0xf03618u: /* shlq    $10,r1 */
   s.c=s.registers[0][1]>>31;s.registers[0][1]=s.registers[0][1]<<16;zn(&s,s.registers[0][1]);
   s.pc=0xf0361au;break;
  case 0xf0361au: /* store   r2,(r3) */
   CHECK(wr32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],s.registers[0][2]));
   s.pc=0xf0361cu;break;
  case 0xf0361cu: /* or      r16,r1 */
   s.registers[0][1]|=s.registers[0][16];
   zn(&s,s.registers[0][1]);
   s.pc=0xf0361eu;break;
  case 0xf0361eu: /* addq    $8,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],8u);
   s.pc=0xf03620u;break;
  case 0xf03620u: /* store   r1,(r4) */
   CHECK(wr32(bus,&s,local(s.registers[0][4])?(s.registers[0][4]&~3u):s.registers[0][4],s.registers[0][1]));
   s.pc=0xf03622u;break;
  case 0xf03622u: /* addq    $4,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],4u);
   s.pc=0xf03624u;break;
  case 0xf03624u: /* moveq   6,r1 */
   s.registers[0][1]=6u;
   s.pc=0xf03626u;break;
  case 0xf03626u: /* store   r2,(r4) */
   CHECK(wr32(bus,&s,local(s.registers[0][4])?(s.registers[0][4]&~3u):s.registers[0][4],s.registers[0][2]));
   s.pc=0xf03628u;break;
  case 0xf03628u: /* subq    $1,r1 */
   s.registers[0][1]=sub(&s,s.registers[0][1],1u);
   s.pc=0xf0362au;break;
  case 0xf0362au: /* jr      nz,00F03626 */
   if(condition(&s,1)){pending=1;target=0xf03626u;}
   s.pc=0xf0362cu;break;
  case 0xf0362cu: /* addq    $4,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],4u);
   s.pc=0xf0362eu;break;
  case 0xf0362eu: /* store   r7,(r4) */
   CHECK(wr32(bus,&s,local(s.registers[0][4])?(s.registers[0][4]&~3u):s.registers[0][4],s.registers[0][7]));
   s.pc=0xf03630u;break;
  case 0xf03630u: /* jump    (r25) */
   if(condition(&s,0)){pending=1;target=s.registers[0][25];}
   s.pc=0xf03632u;break;
  case 0xf03632u: /* subq    $18,r4 */
   s.registers[0][4]=sub(&s,s.registers[0][4],24u);
   s.pc=0xf03634u;break;
  default:return BIWN_GPU_GEOMETRY_BAD_PC;
 }if(delayed){if(pending)return BIWN_GPU_GEOMETRY_BAD_DELAY;s.pc=resume;}if(s.pc==0xf031beu){*state=s;return BIWN_GPU_GEOMETRY_OK;}}return BIWN_GPU_GEOMETRY_WORK_LIMIT;}
