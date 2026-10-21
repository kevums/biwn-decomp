/* Generated from the pinned GPU4D80 overlay by
 * scripts/generate_biwn_movie_relocation_GPU.py. Analyst static recompilation,
 * not recovered original source. Integer primitive behavior is checked
 * against the pinned Virtual Jaguar core; no core runs on the C side. */
#include "biwn_movie_relocation_GPU.h"
#include <string.h>
static void zn(struct biwn_movie_relocation_GPU_state *s,uint32_t v){s->z=v==0;s->n=v>>31;}
static uint32_t add(struct biwn_movie_relocation_GPU_state *s,uint32_t a,uint32_t b){uint32_t v=a+b;s->c=b>~a;zn(s,v);return v;}
static uint32_t sub(struct biwn_movie_relocation_GPU_state *s,uint32_t a,uint32_t b){uint32_t v=a-b;s->c=b>a;zn(s,v);return v;}
static int condition(struct biwn_movie_relocation_GPU_state *s,unsigned code){unsigned flags=s->z|(s->c<<1)|(s->n<<2);return !((code&1u)&&(flags&1u))&&!((code&2u)&&!(flags&1u))&&!((code&4u)&&(flags&(2u<<(code>>4))))&&!((code&8u)&&!(flags&(2u<<(code>>4))));}
static uint32_t be32(const uint8_t *p){return((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
static void put32(uint8_t *p,uint32_t v){p[0]=(uint8_t)(v>>24);p[1]=(uint8_t)(v>>16);p[2]=(uint8_t)(v>>8);p[3]=(uint8_t)v;}
static int local(uint32_t a){return a>=0xf03000u&&a<=0xf03ffcu;}
static int rd32(struct biwn_movie_relocation_GPU_bus *bus,struct biwn_movie_relocation_GPU_state *s,uint32_t a,uint32_t *v){if(local(a)){*v=be32(s->local_RAM+a-0xf03000u);return 0;}if(a==0xf02114u){*v=s->control;return 0;}if(a==0xf02104u){*v=s->matrix_control;return 0;}if(a==0xf02108u){*v=s->matrix_pointer;return 0;}return bus->read32(bus->context,a,v)?2:0;}
static int wr32(struct biwn_movie_relocation_GPU_bus *bus,struct biwn_movie_relocation_GPU_state *s,uint32_t a,uint32_t v){if(local(a)){put32(s->local_RAM+a-0xf03000u,v);return 0;}if(a==0xf02114u){s->control=(s->control&0xf7c0u)|(v&~0xf7c6u);return bus->write32(bus->context,a,v)?2:0;}if(a==0xf02104u){s->matrix_control=v;return 0;}if(a==0xf02108u){s->matrix_pointer=v&~3u;return 0;}return bus->write32(bus->context,a,v)?2:0;}
#define CHECK(e) do{int status=(e);if(status)return(enum biwn_movie_relocation_GPU_status)status;}while(0)
enum biwn_movie_relocation_GPU_status biwn_movie_relocation_GPU_run(struct biwn_movie_relocation_GPU_bus *bus,struct biwn_movie_relocation_GPU_state *state,uint32_t budget){struct biwn_movie_relocation_GPU_state s;uint32_t v,target=0;unsigned pending=0;if(!bus||!state||!budget||!bus->read8||!bus->read16||!bus->read32||!bus->write32||state->active_bank||state->z>1||state->c>1||state->n>1)return 1;s=*state;while(budget--){unsigned delayed=pending;uint32_t resume=target;pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){
case 0xf03240u: /* movei   $f032c8,r0 */
 s.registers[0][0]=((uint32_t)s.local_RAM[578]<<8)|s.local_RAM[579]|((uint32_t)s.local_RAM[580]<<24)|((uint32_t)s.local_RAM[581]<<16);
 s.pc=0xf03246u;break;
  case 0xf03246u: /* jump    (r0) */
   if(condition(&s,0)){pending=1;target=s.registers[0][0];}
   s.pc=0xf03248u;break;
  case 0xf03248u: /* nop */
   s.pc=0xf0324au;break;
  case 0xf03258u: /* move    pc,r20 */
   s.registers[0][20]=0xf03258u;
   s.pc=0xf0325au;break;
case 0xf0325au: /* movei   $f03000,r0 */
 s.registers[0][0]=((uint32_t)s.local_RAM[604]<<8)|s.local_RAM[605]|((uint32_t)s.local_RAM[606]<<24)|((uint32_t)s.local_RAM[607]<<16);
 s.pc=0xf03260u;break;
  case 0xf03260u: /* sub     r0,r20 */
   s.registers[0][20]=sub(&s,s.registers[0][20],s.registers[0][0]);
   s.pc=0xf03262u;break;
  case 0xf03262u: /* move    r20,r21 */
   s.registers[0][21]=s.registers[0][20];
   s.pc=0xf03264u;break;
case 0xf03264u: /* rorq    $10,r21 */
 v=s.registers[0][21];s.c=v>>31;s.registers[0][21]=(v>>16)|(v<<16);zn(&s,s.registers[0][21]);
 s.pc=0xf03266u;break;
case 0xf03266u: /* movei   $f03020,r25 */
 s.registers[0][25]=((uint32_t)s.local_RAM[616]<<8)|s.local_RAM[617]|((uint32_t)s.local_RAM[618]<<24)|((uint32_t)s.local_RAM[619]<<16);
 s.pc=0xf0326cu;break;
  case 0xf0326cu: /* add     r20,r25 */
   s.registers[0][25]=add(&s,s.registers[0][25],s.registers[0][20]);
   s.pc=0xf0326eu;break;
case 0xf0326eu: /* movei   $f03804,r0 */
 s.registers[0][0]=((uint32_t)s.local_RAM[624]<<8)|s.local_RAM[625]|((uint32_t)s.local_RAM[626]<<24)|((uint32_t)s.local_RAM[627]<<16);
 s.pc=0xf03274u;break;
  case 0xf03274u: /* add     r20,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][20]);
   s.pc=0xf03276u;break;
case 0xf03276u: /* load    (r0),r10 */
 CHECK(rd32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],&v));s.registers[0][10]=v;
 s.pc=0xf03278u;break;
  case 0xf03278u: /* addq    $4,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],4u);
   s.pc=0xf0327au;break;
case 0xf0327au: /* load    (r0),r1 */
 CHECK(rd32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],&v));s.registers[0][1]=v;
 s.pc=0xf0327cu;break;
  case 0xf0327cu: /* add     r20,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],s.registers[0][20]);
   s.pc=0xf0327eu;break;
  case 0xf0327eu: /* btst    $1,r1 */
   s.z=((~s.registers[0][1])>>1)&1u;
   s.pc=0xf03280u;break;
  case 0xf03280u: /* jr      z,00F03290 */
   if(condition(&s,2)){pending=1;target=0xf03290u;}
   s.pc=0xf03282u;break;
  case 0xf03282u: /* nop */
   s.pc=0xf03284u;break;
  case 0xf03284u: /* addq    $2,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],2u);
   s.pc=0xf03286u;break;
case 0xf03286u: /* load    (r1),r2 */
 CHECK(rd32(bus,&s,local(s.registers[0][1])?(s.registers[0][1]&~3u):s.registers[0][1],&v));s.registers[0][2]=v;
 s.pc=0xf03288u;break;
  case 0xf03288u: /* add     r21,r2 */
   s.registers[0][2]=add(&s,s.registers[0][2],s.registers[0][21]);
   s.pc=0xf0328au;break;
  case 0xf0328au: /* store   r2,(r1) */
   CHECK(wr32(bus,&s,local(s.registers[0][1])?(s.registers[0][1]&~3u):s.registers[0][1],s.registers[0][2]));
   s.pc=0xf0328cu;break;
  case 0xf0328cu: /* jr      00F03296 */
   if(condition(&s,0)){pending=1;target=0xf03296u;}
   s.pc=0xf0328eu;break;
  case 0xf0328eu: /* nop */
   s.pc=0xf03290u;break;
case 0xf03290u: /* load    (r1),r2 */
 CHECK(rd32(bus,&s,local(s.registers[0][1])?(s.registers[0][1]&~3u):s.registers[0][1],&v));s.registers[0][2]=v;
 s.pc=0xf03292u;break;
  case 0xf03292u: /* add     r20,r2 */
   s.registers[0][2]=add(&s,s.registers[0][2],s.registers[0][20]);
   s.pc=0xf03294u;break;
  case 0xf03294u: /* store   r2,(r1) */
   CHECK(wr32(bus,&s,local(s.registers[0][1])?(s.registers[0][1]&~3u):s.registers[0][1],s.registers[0][2]));
   s.pc=0xf03296u;break;
  case 0xf03296u: /* subq    $1,r10 */
   s.registers[0][10]=sub(&s,s.registers[0][10],1u);
   s.pc=0xf03298u;break;
  case 0xf03298u: /* jump    nz,(r25) */
   if(condition(&s,1)){pending=1;target=s.registers[0][25];}
   s.pc=0xf0329au;break;
  case 0xf0329au: /* nop */
   s.pc=0xf0329cu;break;
case 0xf0329cu: /* movei   $f0388c,r0 */
 s.registers[0][0]=((uint32_t)s.local_RAM[670]<<8)|s.local_RAM[671]|((uint32_t)s.local_RAM[672]<<24)|((uint32_t)s.local_RAM[673]<<16);
 s.pc=0xf032a2u;break;
  case 0xf032a2u: /* add     r20,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][20]);
   s.pc=0xf032a4u;break;
case 0xf032a4u: /* load    (r0),r10 */
 CHECK(rd32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],&v));s.registers[0][10]=v;
 s.pc=0xf032a6u;break;
  case 0xf032a6u: /* addq    $4,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],4u);
   s.pc=0xf032a8u;break;
case 0xf032a8u: /* load    (r0),r1 */
 CHECK(rd32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],&v));s.registers[0][1]=v;
 s.pc=0xf032aau;break;
  case 0xf032aau: /* add     r20,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],s.registers[0][20]);
   s.pc=0xf032acu;break;
case 0xf032acu: /* load    (r1),r2 */
 CHECK(rd32(bus,&s,local(s.registers[0][1])?(s.registers[0][1]&~3u):s.registers[0][1],&v));s.registers[0][2]=v;
 s.pc=0xf032aeu;break;
  case 0xf032aeu: /* add     r20,r2 */
   s.registers[0][2]=add(&s,s.registers[0][2],s.registers[0][20]);
   s.pc=0xf032b0u;break;
  case 0xf032b0u: /* store   r2,(r1) */
   CHECK(wr32(bus,&s,local(s.registers[0][1])?(s.registers[0][1]&~3u):s.registers[0][1],s.registers[0][2]));
   s.pc=0xf032b2u;break;
  case 0xf032b2u: /* subq    $1,r10 */
   s.registers[0][10]=sub(&s,s.registers[0][10],1u);
   s.pc=0xf032b4u;break;
  case 0xf032b4u: /* jr      nz,00F032A6 */
   if(condition(&s,1)){pending=1;target=0xf032a6u;}
   s.pc=0xf032b6u;break;
  case 0xf032b6u: /* nop */
   s.pc=0xf032b8u;break;
case 0xf032b8u: /* movei   $f03804,r31 */
 s.registers[0][31]=((uint32_t)s.local_RAM[698]<<8)|s.local_RAM[699]|((uint32_t)s.local_RAM[700]<<24)|((uint32_t)s.local_RAM[701]<<16);
 s.pc=0xf032beu;break;
case 0xf032beu: /* movei   $f03794,r0 */
 s.registers[0][0]=((uint32_t)s.local_RAM[704]<<8)|s.local_RAM[705]|((uint32_t)s.local_RAM[706]<<24)|((uint32_t)s.local_RAM[707]<<16);
 s.pc=0xf032c4u;break;
  case 0xf032c4u: /* moveq   1,r1 */
   s.registers[0][1]=1u;
   s.pc=0xf032c6u;break;
  case 0xf032c6u: /* store   r1,(r0) */
   CHECK(wr32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],s.registers[0][1]));
   s.pc=0xf032c8u;break;
default:return BIWN_MOVIE_RELOCATION_GPU_BAD_PC;
}if(delayed){if(pending)return BIWN_MOVIE_RELOCATION_GPU_BAD_DELAY;s.pc=resume;}if(s.pc==0xf032c8u){*state=s;return 0;}}return BIWN_MOVIE_RELOCATION_GPU_WORK_LIMIT;}
