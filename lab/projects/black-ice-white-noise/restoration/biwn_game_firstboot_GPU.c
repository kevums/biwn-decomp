/* Generated from the pinned GPU4D80 overlay by
 * scripts/generate_biwn_game_firstboot_GPU.py. Analyst static recompilation,
 * not recovered original source. Integer primitive behavior is checked
 * against the pinned Virtual Jaguar core; no core runs on the C side. */
#include "biwn_game_firstboot_GPU.h"
#include <string.h>
static uint32_t sar(uint32_t v,unsigned n){return n>=32?((v&0x80000000u)?0xffffffffu:0):(v>>n)|((v&0x80000000u)?(0xffffffffu<<(32-n)):0);}
static void zn(struct biwn_game_firstboot_GPU_state *s,uint32_t v){s->z=v==0;s->n=v>>31;}
static uint32_t add(struct biwn_game_firstboot_GPU_state *s,uint32_t a,uint32_t b){uint32_t v=a+b;s->c=b>~a;zn(s,v);return v;}
static uint32_t sub(struct biwn_game_firstboot_GPU_state *s,uint32_t a,uint32_t b){uint32_t v=a-b;s->c=b>a;zn(s,v);return v;}
static int condition(struct biwn_game_firstboot_GPU_state *s,unsigned code){unsigned flags=s->z|(s->c<<1)|(s->n<<2);return !((code&1u)&&(flags&1u))&&!((code&2u)&&!(flags&1u))&&!((code&4u)&&(flags&(2u<<(code>>4))))&&!((code&8u)&&!(flags&(2u<<(code>>4))));}
static uint32_t be32(const uint8_t *p){return((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
static void put32(uint8_t *p,uint32_t v){p[0]=(uint8_t)(v>>24);p[1]=(uint8_t)(v>>16);p[2]=(uint8_t)(v>>8);p[3]=(uint8_t)v;}
static int local(uint32_t a){return a>=0xf03000u&&a<=0xf03ffcu;}
static int rd32(struct biwn_game_firstboot_GPU_bus *bus,struct biwn_game_firstboot_GPU_state *s,uint32_t a,uint32_t *v){if(local(a)){*v=be32(s->local_RAM+a-0xf03000u);return 0;}if(a==0xf02100u){s->flags=(s->flags&~7u)|(s->n<<2)|(s->c<<1)|s->z;*v=s->flags&0xffffc1ffu;return 0;}if(a==0xf02114u){*v=s->control;return 0;}if(a==0xf02104u){*v=s->matrix_control;return 0;}if(a==0xf02108u){*v=s->matrix_pointer;return 0;}return bus->read32(bus->context,a,v)?2:0;}
static int rd16(struct biwn_game_firstboot_GPU_bus *bus,struct biwn_game_firstboot_GPU_state *s,uint32_t a,uint32_t *v){uint16_t h;if(a>=0xf03000u&&a<=0xf03ffeu){unsigned p=a-0xf03000u;*v=((uint32_t)s->local_RAM[p]<<8)|s->local_RAM[p+1];return 0;}if(bus->read16(bus->context,a,&h))return 2;*v=h;return 0;}
static int loadw(struct biwn_game_firstboot_GPU_bus *bus,struct biwn_game_firstboot_GPU_state *s,uint32_t a,uint32_t *v){if(a>=0xf03000u&&a<=0xf03fffu)return rd32(bus,s,a&~3u,v);return rd16(bus,s,a,v);}
static int wr32(struct biwn_game_firstboot_GPU_bus *bus,struct biwn_game_firstboot_GPU_state *s,uint32_t a,uint32_t v){if(local(a)){put32(s->local_RAM+a-0xf03000u,v);return 0;}if(a==0xf02114u){s->control=(s->control&0xf7c0u)|(v&~0xf7c6u);return bus->write32(bus->context,a,v)?2:0;}if(a==0xf02100u){s->flags=(v&~8u)|((v&8u)?(s->flags&8u):0);s->z=s->flags&1u;s->c=(s->flags>>1)&1u;s->n=(s->flags>>2)&1u;s->control&=~((s->flags&0x3e00u)>>3);s->active_bank=(!(s->flags&8u)&&(s->flags&0x4000u))?1u:0u;return bus->write32(bus->context,a,v)?2:0;}if(a==0xf02104u){s->matrix_control=v;return 0;}if(a==0xf02108u){s->matrix_pointer=v&~3u;return 0;}return bus->write32(bus->context,a,v)?2:0;}
static int wr16(struct biwn_game_firstboot_GPU_bus *bus,struct biwn_game_firstboot_GPU_state *s,uint32_t a,uint32_t v){if(a>=0xf03000u&&a<=0xf03fffu)return wr32(bus,s,a&~1u,v&0xffffu);return bus->write16(bus->context,a,(uint16_t)v)?2:0;}
static int rd8(struct biwn_game_firstboot_GPU_bus *bus,struct biwn_game_firstboot_GPU_state *s,uint32_t a,uint32_t *v){uint8_t b;if(local(a))return rd32(bus,s,a&~3u,v);if(bus->read8(bus->context,a,&b))return 2;*v=b;return 0;}
#define CHECK(e) do{int status=(e);if(status)return(enum biwn_game_firstboot_GPU_status)status;}while(0)
enum biwn_game_firstboot_GPU_status biwn_game_firstboot_GPU_run(struct biwn_game_firstboot_GPU_bus *bus,struct biwn_game_firstboot_GPU_state *state,uint32_t budget,uint32_t stopPC){struct biwn_game_firstboot_GPU_state s;uint32_t v,target=0;unsigned pending=0;if(!bus||!state||!budget||!bus->read8||!bus->read16||!bus->read32||!bus->write16||!bus->write32||state->active_bank||state->z>1||state->c>1||state->n>1)return 1;s=*state;while(budget--){unsigned delayed=pending;uint32_t resume=target;pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){
  case 0xf03200u: /* movei   $f0332c,r24 */
   s.registers[0][24]=0xf0332cu;
   s.pc=0xf03206u;break;
  case 0xf03206u: /* movei   $180580,r25 */
   s.registers[0][25]=0x180580u;
   s.pc=0xf0320cu;break;
  case 0xf0320cu: /* movei   $f03ff0,r26 */
   s.registers[0][26]=0xf03ff0u;
   s.pc=0xf03212u;break;
  case 0xf03212u: /* store   r25,(r26) */
   CHECK(wr32(bus,&s,local(s.registers[0][26])?(s.registers[0][26]&~3u):s.registers[0][26],s.registers[0][25]));
   s.pc=0xf03214u;break;
  case 0xf03214u: /* addq    $4,r26 */
   s.registers[0][26]=add(&s,s.registers[0][26],4u);
   s.pc=0xf03216u;break;
  case 0xf03216u: /* moveq   0,r25 */
   s.registers[0][25]=0u;
   s.pc=0xf03218u;break;
  case 0xf03218u: /* store   r25,(r26) */
   CHECK(wr32(bus,&s,local(s.registers[0][26])?(s.registers[0][26]&~3u):s.registers[0][26],s.registers[0][25]));
   s.pc=0xf0321au;break;
  case 0xf0321au: /* addq    $4,r26 */
   s.registers[0][26]=add(&s,s.registers[0][26],4u);
   s.pc=0xf0321cu;break;
  case 0xf0321cu: /* movei   $190000,r25 */
   s.registers[0][25]=0x190000u;
   s.pc=0xf03222u;break;
  case 0xf03222u: /* store   r25,(r26) */
   CHECK(wr32(bus,&s,local(s.registers[0][26])?(s.registers[0][26]&~3u):s.registers[0][26],s.registers[0][25]));
   s.pc=0xf03224u;break;
  case 0xf03224u: /* move    pc,r25 */
   s.registers[0][25]=0xf03224u;
   s.pc=0xf03226u;break;
  case 0xf03226u: /* jump    (r24) */
   if(condition(&s,0)){pending=1;target=s.registers[0][24];}
   s.pc=0xf03228u;break;
  case 0xf03228u: /* addq    $6,r25 */
   s.registers[0][25]=add(&s,s.registers[0][25],6u);
   s.pc=0xf0322au;break;
  case 0xf0322au: /* movei   $180580,r25 */
   s.registers[0][25]=0x180580u;
   s.pc=0xf03230u;break;
  case 0xf03230u: /* movei   $f03ff0,r26 */
   s.registers[0][26]=0xf03ff0u;
   s.pc=0xf03236u;break;
  case 0xf03236u: /* store   r25,(r26) */
   CHECK(wr32(bus,&s,local(s.registers[0][26])?(s.registers[0][26]&~3u):s.registers[0][26],s.registers[0][25]));
   s.pc=0xf03238u;break;
  case 0xf03238u: /* addq    $4,r26 */
   s.registers[0][26]=add(&s,s.registers[0][26],4u);
   s.pc=0xf0323au;break;
  case 0xf0323au: /* moveq   1,r25 */
   s.registers[0][25]=1u;
   s.pc=0xf0323cu;break;
  case 0xf0323cu: /* store   r25,(r26) */
   CHECK(wr32(bus,&s,local(s.registers[0][26])?(s.registers[0][26]&~3u):s.registers[0][26],s.registers[0][25]));
   s.pc=0xf0323eu;break;
  case 0xf0323eu: /* addq    $4,r26 */
   s.registers[0][26]=add(&s,s.registers[0][26],4u);
   s.pc=0xf03240u;break;
  case 0xf03240u: /* movei   $1a4000,r25 */
   s.registers[0][25]=0x1a4000u;
   s.pc=0xf03246u;break;
  case 0xf03246u: /* store   r25,(r26) */
   CHECK(wr32(bus,&s,local(s.registers[0][26])?(s.registers[0][26]&~3u):s.registers[0][26],s.registers[0][25]));
   s.pc=0xf03248u;break;
  case 0xf03248u: /* move    pc,r25 */
   s.registers[0][25]=0xf03248u;
   s.pc=0xf0324au;break;
  case 0xf0324au: /* jump    (r24) */
   if(condition(&s,0)){pending=1;target=s.registers[0][24];}
   s.pc=0xf0324cu;break;
  case 0xf0324cu: /* addq    $6,r25 */
   s.registers[0][25]=add(&s,s.registers[0][25],6u);
   s.pc=0xf0324eu;break;
  case 0xf0324eu: /* movei   $1b8008,r2 */
   s.registers[0][2]=0x1b8008u;
   s.pc=0xf03254u;break;
  case 0xf03254u: /* movei   $180520,r3 */
   s.registers[0][3]=0x180520u;
   s.pc=0xf0325au;break;
  case 0xf0325au: /* movei   $12,r4 */
   s.registers[0][4]=0x12u;
   s.pc=0xf03260u;break;
case 0xf03260u: /* load    (r3),r5 */
 CHECK(rd32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],&v));s.registers[0][5]=v;
 s.pc=0xf03262u;break;
  case 0xf03262u: /* addq    $4,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],4u);
   s.pc=0xf03264u;break;
  case 0xf03264u: /* store   r5,(r2) */
   CHECK(wr32(bus,&s,local(s.registers[0][2])?(s.registers[0][2]&~3u):s.registers[0][2],s.registers[0][5]));
   s.pc=0xf03266u;break;
  case 0xf03266u: /* addq    $4,r2 */
   s.registers[0][2]=add(&s,s.registers[0][2],4u);
   s.pc=0xf03268u;break;
  case 0xf03268u: /* subq    $1,r4 */
   s.registers[0][4]=sub(&s,s.registers[0][4],1u);
   s.pc=0xf0326au;break;
  case 0xf0326au: /* jr      nz,00F03260 */
   if(condition(&s,1)){pending=1;target=0xf03260u;}
   s.pc=0xf0326cu;break;
  case 0xf0326cu: /* or      r4,r4 */
   s.registers[0][4]|=s.registers[0][4];
   zn(&s,s.registers[0][4]);
   s.pc=0xf0326eu;break;
  case 0xf0326eu: /* or      r3,r3 */
   s.registers[0][3]|=s.registers[0][3];
   zn(&s,s.registers[0][3]);
   s.pc=0xf03270u;break;
  case 0xf03270u: /* or      r2,r2 */
   s.registers[0][2]|=s.registers[0][2];
   zn(&s,s.registers[0][2]);
   s.pc=0xf03272u;break;
  case 0xf03272u: /* movei   $8010001b,r0 */
   s.registers[0][0]=0x8010001bu;
   s.pc=0xf03278u;break;
  case 0xf03278u: /* movei   $f00020,r1 */
   s.registers[0][1]=0xf00020u;
   s.pc=0xf0327eu;break;
  case 0xf0327eu: /* store   r0,(r1) */
   CHECK(wr32(bus,&s,local(s.registers[0][1])?(s.registers[0][1]&~3u):s.registers[0][1],s.registers[0][0]));
   s.pc=0xf03280u;break;
  case 0xf03280u: /* movei   $6c1,r0 */
   s.registers[0][0]=0x6c1u;
   s.pc=0xf03286u;break;
  case 0xf03286u: /* movei   $f00028,r1 */
   s.registers[0][1]=0xf00028u;
   s.pc=0xf0328cu;break;
  case 0xf0328cu: /* storew  r0,(r1) */
   CHECK(wr16(bus,&s,s.registers[0][1],s.registers[0][0]));
   s.pc=0xf0328eu;break;
  case 0xf0328eu: /* movei   $f00006,r6 */
   s.registers[0][6]=0xf00006u;
   s.pc=0xf03294u;break;
  case 0xf03294u: /* movei   $f032aa,r7 */
   s.registers[0][7]=0xf032aau;
   s.pc=0xf0329au;break;
  case 0xf0329au: /* movei   $f03800,r0 */
   s.registers[0][0]=0xf03800u;
   s.pc=0xf032a0u;break;
  case 0xf032a0u: /* movei   $f032ce,r8 */
   s.registers[0][8]=0xf032ceu;
   s.pc=0xf032a6u;break;
  case 0xf032a6u: /* jump    (r8) */
   if(condition(&s,0)){pending=1;target=s.registers[0][8];}
   s.pc=0xf032a8u;break;
  case 0xf032a8u: /* nop */
   s.pc=0xf032aau;break;
  case 0xf032aau: /* movei   $1b8008,r2 */
   s.registers[0][2]=0x1b8008u;
   s.pc=0xf032b0u;break;
  case 0xf032b0u: /* movei   $180520,r3 */
   s.registers[0][3]=0x180520u;
   s.pc=0xf032b6u;break;
  case 0xf032b6u: /* movei   $12,r4 */
   s.registers[0][4]=0x12u;
   s.pc=0xf032bcu;break;
case 0xf032bcu: /* load    (r3),r5 */
 CHECK(rd32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],&v));s.registers[0][5]=v;
 s.pc=0xf032beu;break;
  case 0xf032beu: /* addq    $4,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],4u);
   s.pc=0xf032c0u;break;
  case 0xf032c0u: /* store   r5,(r2) */
   CHECK(wr32(bus,&s,local(s.registers[0][2])?(s.registers[0][2]&~3u):s.registers[0][2],s.registers[0][5]));
   s.pc=0xf032c2u;break;
  case 0xf032c2u: /* addq    $4,r2 */
   s.registers[0][2]=add(&s,s.registers[0][2],4u);
   s.pc=0xf032c4u;break;
  case 0xf032c4u: /* subq    $1,r4 */
   s.registers[0][4]=sub(&s,s.registers[0][4],1u);
   s.pc=0xf032c6u;break;
  case 0xf032c6u: /* jr      nz,00F032BC */
   if(condition(&s,1)){pending=1;target=0xf032bcu;}
   s.pc=0xf032c8u;break;
  case 0xf032c8u: /* or      r4,r4 */
   s.registers[0][4]|=s.registers[0][4];
   zn(&s,s.registers[0][4]);
   s.pc=0xf032cau;break;
  case 0xf032cau: /* or      r3,r3 */
   s.registers[0][3]|=s.registers[0][3];
   zn(&s,s.registers[0][3]);
   s.pc=0xf032ccu;break;
  case 0xf032ccu: /* or      r2,r2 */
   s.registers[0][2]|=s.registers[0][2];
   zn(&s,s.registers[0][2]);
   s.pc=0xf032ceu;break;
  case 0xf032ceu: /* loadw   (r6),r1 */
   CHECK(loadw(bus,&s,s.registers[0][6],&v));s.registers[0][1]=v;
   s.pc=0xf032d0u;break;
  case 0xf032d0u: /* shlq    $15,r1 */
   s.c=s.registers[0][1]>>31;s.registers[0][1]=s.registers[0][1]<<21;zn(&s,s.registers[0][1]);
   s.pc=0xf032d2u;break;
  case 0xf032d2u: /* shrq    $15,r1 */
   s.c=s.registers[0][1]&1u;s.registers[0][1]=s.registers[0][1]>>21;zn(&s,s.registers[0][1]);
   s.pc=0xf032d4u;break;
  case 0xf032d4u: /* cmpq    $3,r1 */
   (void)sub(&s,s.registers[0][1],0x3u);
   s.pc=0xf032d6u;break;
  case 0xf032d6u: /* jump    n,(r7) */
   if(condition(&s,24)){pending=1;target=s.registers[0][7];}
   s.pc=0xf032d8u;break;
  case 0xf032d8u: /* nop */
   s.pc=0xf032dau;break;
case 0xf032dau: /* load    (r0),r1 */
 CHECK(rd32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],&v));s.registers[0][1]=v;
 s.pc=0xf032dcu;break;
  case 0xf032dcu: /* cmpq    $0,r1 */
   (void)sub(&s,s.registers[0][1],0x0u);
   s.pc=0xf032deu;break;
  case 0xf032deu: /* jr      z,00F032CE */
   if(condition(&s,2)){pending=1;target=0xf032ceu;}
   s.pc=0xf032e0u;break;
  case 0xf032e0u: /* or      r7,r7 */
   s.registers[0][7]|=s.registers[0][7];
   zn(&s,s.registers[0][7]);
   s.pc=0xf032e2u;break;
  case 0xf032e2u: /* movei   $f02100,r0 */
   s.registers[0][0]=0xf02100u;
   s.pc=0xf032e8u;break;
case 0xf032e8u: /* load    (r0),r1 */
 CHECK(rd32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],&v));s.registers[0][1]=v;
 s.pc=0xf032eau;break;
  case 0xf032eau: /* bclr    $3,r1 */
   s.registers[0][1]&=~(1u<<3);
   zn(&s,s.registers[0][1]);
   s.pc=0xf032ecu;break;
  case 0xf032ecu: /* bset    $a,r1 */
   s.registers[0][1]|=(1u<<10);
   zn(&s,s.registers[0][1]);
   s.pc=0xf032eeu;break;
  case 0xf032eeu: /* store   r1,(r0) */
   CHECK(wr32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],s.registers[0][1]));
   s.pc=0xf032f0u;break;
  case 0xf032f0u: /* movei   $101,r1 */
   s.registers[0][1]=0x101u;
   s.pc=0xf032f6u;break;
  case 0xf032f6u: /* movei   $f10020,r0 */
   s.registers[0][0]=0xf10020u;
   s.pc=0xf032fcu;break;
  case 0xf032fcu: /* store   r1,(r0) */
   CHECK(wr32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],s.registers[0][1]));
   s.pc=0xf032feu;break;
  case 0xf032feu: /* movei   $dfff14,r0 */
   s.registers[0][0]=0xdfff14u;
   s.pc=0xf03304u;break;
case 0xf03304u: /* load    (r0),r1 */
 CHECK(rd32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],&v));s.registers[0][1]=v;
 s.pc=0xf03306u;break;
  case 0xf03306u: /* sub     r1,r1 */
   s.registers[0][1]=sub(&s,s.registers[0][1],s.registers[0][1]);
   s.pc=0xf03308u;break;
  case 0xf03308u: /* movei   $dfff00,r0 */
   s.registers[0][0]=0xdfff00u;
   s.pc=0xf0330eu;break;
  case 0xf0330eu: /* store   r1,(r0) */
   CHECK(wr32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],s.registers[0][1]));
   s.pc=0xf03310u;break;
  case 0xf03310u: /* movei   $0,r1 */
   s.registers[0][1]=0x0u;
   s.pc=0xf03316u;break;
  case 0xf03316u: /* movei   $f10020,r0 */
   s.registers[0][0]=0xf10020u;
   s.pc=0xf0331cu;break;
  case 0xf0331cu: /* store   r1,(r0) */
   CHECK(wr32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],s.registers[0][1]));
   s.pc=0xf0331eu;break;
  case 0xf0331eu: /* movei   $f02114,r0 */
   s.registers[0][0]=0xf02114u;
   s.pc=0xf03324u;break;
  case 0xf03324u: /* moveq   0,r1 */
   s.registers[0][1]=0u;
   s.pc=0xf03326u;break;
  case 0xf03326u: /* store   r1,(r0) */
   CHECK(wr32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],s.registers[0][1]));
   s.pc=0xf03328u;break;
  case 0xf03328u: /* jr      00F03328 */
   if(condition(&s,0)){pending=1;target=0xf03328u;}
   s.pc=0xf0332au;break;
  case 0xf0332au: /* nop */
   s.pc=0xf0332cu;break;
  case 0xf0332cu: /* movei   $f03ff0,r0 */
   s.registers[0][0]=0xf03ff0u;
   s.pc=0xf03332u;break;
case 0xf03332u: /* load    (r0),r1 */
 CHECK(rd32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],&v));s.registers[0][1]=v;
 s.pc=0xf03334u;break;
  case 0xf03334u: /* addq    $4,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],4u);
   s.pc=0xf03336u;break;
case 0xf03336u: /* load    (r0),r2 */
 CHECK(rd32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],&v));s.registers[0][2]=v;
 s.pc=0xf03338u;break;
  case 0xf03338u: /* addq    $4,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],4u);
   s.pc=0xf0333au;break;
case 0xf0333au: /* load    (r0),r3 */
 CHECK(rd32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],&v));s.registers[0][3]=v;
 s.pc=0xf0333cu;break;
  case 0xf0333cu: /* move    r1,r0 */
   s.registers[0][0]=s.registers[0][1];
   s.pc=0xf0333eu;break;
  case 0xf0333eu: /* addq    $4,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],4u);
   s.pc=0xf03340u;break;
case 0xf03340u: /* load    (r0),r4 */
 CHECK(rd32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],&v));s.registers[0][4]=v;
 s.pc=0xf03342u;break;
  case 0xf03342u: /* addq    $8,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],8u);
   s.pc=0xf03344u;break;
  case 0xf03344u: /* add     r1,r4 */
   s.registers[0][4]=add(&s,s.registers[0][4],s.registers[0][1]);
   s.pc=0xf03346u;break;
  case 0xf03346u: /* shlq    $2,r2 */
   s.c=s.registers[0][2]>>31;s.registers[0][2]=s.registers[0][2]<<2;zn(&s,s.registers[0][2]);
   s.pc=0xf03348u;break;
  case 0xf03348u: /* add     r2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][2]);
   s.pc=0xf0334au;break;
case 0xf0334au: /* load    (r0),r2 */
 CHECK(rd32(bus,&s,local(s.registers[0][0])?(s.registers[0][0]&~3u):s.registers[0][0],&v));s.registers[0][2]=v;
 s.pc=0xf0334cu;break;
  case 0xf0334cu: /* add     r2,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],s.registers[0][2]);
   s.pc=0xf0334eu;break;
case 0xf0334eu: /* loadb   (r1),r2 */
 CHECK(rd8(bus,&s,s.registers[0][1],&v));s.registers[0][2]=v;
 s.pc=0xf03350u;break;
  case 0xf03350u: /* addq    $1,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],1u);
   s.pc=0xf03352u;break;
case 0xf03352u: /* loadb   (r1),r5 */
 CHECK(rd8(bus,&s,s.registers[0][1],&v));s.registers[0][5]=v;
 s.pc=0xf03354u;break;
  case 0xf03354u: /* addq    $1,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],1u);
   s.pc=0xf03356u;break;
case 0xf03356u: /* loadb   (r1),r21 */
 CHECK(rd8(bus,&s,s.registers[0][1],&v));s.registers[0][21]=v;
 s.pc=0xf03358u;break;
  case 0xf03358u: /* move    r3,r0 */
   s.registers[0][0]=s.registers[0][3];
   s.pc=0xf0335au;break;
  case 0xf0335au: /* shlq    $18,r21 */
   s.c=s.registers[0][21]>>31;s.registers[0][21]=s.registers[0][21]<<24;zn(&s,s.registers[0][21]);
   s.pc=0xf0335cu;break;
  case 0xf0335cu: /* subq    $c,r0 */
   s.registers[0][0]=sub(&s,s.registers[0][0],12u);
   s.pc=0xf0335eu;break;
  case 0xf0335eu: /* sharq   $18,r21 */
   s.c=s.registers[0][21]&1u;s.registers[0][21]=sar(s.registers[0][21],24);zn(&s,s.registers[0][21]);
   s.pc=0xf03360u;break;
  case 0xf03360u: /* addq    $1,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],1u);
   s.pc=0xf03362u;break;
  case 0xf03362u: /* storew  r21,(r0) */
   CHECK(wr16(bus,&s,s.registers[0][0],s.registers[0][21]));
   s.pc=0xf03364u;break;
case 0xf03364u: /* loadb   (r1),r21 */
 CHECK(rd8(bus,&s,s.registers[0][1],&v));s.registers[0][21]=v;
 s.pc=0xf03366u;break;
  case 0xf03366u: /* shlq    $18,r21 */
   s.c=s.registers[0][21]>>31;s.registers[0][21]=s.registers[0][21]<<24;zn(&s,s.registers[0][21]);
   s.pc=0xf03368u;break;
  case 0xf03368u: /* addq    $2,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],2u);
   s.pc=0xf0336au;break;
  case 0xf0336au: /* sharq   $18,r21 */
   s.c=s.registers[0][21]&1u;s.registers[0][21]=sar(s.registers[0][21],24);zn(&s,s.registers[0][21]);
   s.pc=0xf0336cu;break;
  case 0xf0336cu: /* addq    $1,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],1u);
   s.pc=0xf0336eu;break;
  case 0xf0336eu: /* storew  r21,(r0) */
   CHECK(wr16(bus,&s,s.registers[0][0],s.registers[0][21]));
   s.pc=0xf03370u;break;
  case 0xf03370u: /* mult    r5,r2 */
   s.registers[0][2]=(s.registers[0][2]&0xffffu)*(s.registers[0][5]&0xffffu);
   zn(&s,s.registers[0][2]);
   s.pc=0xf03372u;break;
  case 0xf03372u: /* subq    $1,r2 */
   s.registers[0][2]=sub(&s,s.registers[0][2],1u);
   s.pc=0xf03374u;break;
  case 0xf03374u: /* moveq   0,r5 */
   s.registers[0][5]=0u;
   s.pc=0xf03376u;break;
  case 0xf03376u: /* moveq   0,r6 */
   s.registers[0][6]=0u;
   s.pc=0xf03378u;break;
  case 0xf03378u: /* movei   $f00,r8 */
   s.registers[0][8]=0xf00u;
   s.pc=0xf0337eu;break;
  case 0xf0337eu: /* movei   $700,r19 */
   s.registers[0][19]=0x700u;
   s.pc=0xf03384u;break;
  case 0xf03384u: /* movei   $f00,r20 */
   s.registers[0][20]=0xf00u;
   s.pc=0xf0338au;break;
  case 0xf0338au: /* movei   $f03472,r9 */
   s.registers[0][9]=0xf03472u;
   s.pc=0xf03390u;break;
  case 0xf03390u: /* movei   $f03542,r13 */
   s.registers[0][13]=0xf03542u;
   s.pc=0xf03396u;break;
  case 0xf03396u: /* movei   $f033e8,r11 */
   s.registers[0][11]=0xf033e8u;
   s.pc=0xf0339cu;break;
  case 0xf0339cu: /* movei   $f034b8,r14 */
   s.registers[0][14]=0xf034b8u;
   s.pc=0xf033a2u;break;
  case 0xf033a2u: /* movei   $f033ae,r12 */
   s.registers[0][12]=0xf033aeu;
   s.pc=0xf033a8u;break;
  case 0xf033a8u: /* movei   $f03576,r15 */
   s.registers[0][15]=0xf03576u;
   s.pc=0xf033aeu;break;
  case 0xf033aeu: /* cmpq    $0,r6 */
   (void)sub(&s,s.registers[0][6],0x0u);
   s.pc=0xf033b0u;break;
  case 0xf033b0u: /* jr      nz,00F033BA */
   if(condition(&s,1)){pending=1;target=0xf033bau;}
   s.pc=0xf033b2u;break;
  case 0xf033b2u: /* nop */
   s.pc=0xf033b4u;break;
case 0xf033b4u: /* loadb   (r1),r7 */
 CHECK(rd8(bus,&s,s.registers[0][1],&v));s.registers[0][7]=v;
 s.pc=0xf033b6u;break;
  case 0xf033b6u: /* moveq   8,r6 */
   s.registers[0][6]=8u;
   s.pc=0xf033b8u;break;
  case 0xf033b8u: /* addq    $1,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],1u);
   s.pc=0xf033bau;break;
  case 0xf033bau: /* btst    $7,r7 */
   s.z=((~s.registers[0][7])>>7)&1u;
   s.pc=0xf033bcu;break;
case 0xf033bcu: /* subqt   $1,r6 */
 s.registers[0][6]-=1u;
 s.pc=0xf033beu;break;
  case 0xf033beu: /* jump    z,(r9) */
   if(condition(&s,2)){pending=1;target=s.registers[0][9];}
   s.pc=0xf033c0u;break;
  case 0xf033c0u: /* shlq    $1,r7 */
   s.c=s.registers[0][7]>>31;s.registers[0][7]=s.registers[0][7]<<1;zn(&s,s.registers[0][7]);
   s.pc=0xf033c2u;break;
  case 0xf033c2u: /* subq    $4,r6 */
   s.registers[0][6]=sub(&s,s.registers[0][6],4u);
   s.pc=0xf033c4u;break;
  case 0xf033c4u: /* jr      nn,00F033D2 */
   if(condition(&s,20)){pending=1;target=0xf033d2u;}
   s.pc=0xf033c6u;break;
  case 0xf033c6u: /* shlq    $4,r7 */
   s.c=s.registers[0][7]>>31;s.registers[0][7]=s.registers[0][7]<<4;zn(&s,s.registers[0][7]);
   s.pc=0xf033c8u;break;
case 0xf033c8u: /* loadb   (r1),r0 */
 CHECK(rd8(bus,&s,s.registers[0][1],&v));s.registers[0][0]=v;
 s.pc=0xf033cau;break;
  case 0xf033cau: /* addq    $1,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],1u);
   s.pc=0xf033ccu;break;
case 0xf033ccu: /* sh      r6,r0 */
 if(s.registers[0][6]&0x80000000u){s.c=s.registers[0][0]>>31;s.registers[0][0]=(int32_t)s.registers[0][6]<=-32?0u:s.registers[0][0]<<(0u-s.registers[0][6]);}else{s.c=s.registers[0][0]&1u;s.registers[0][0]=s.registers[0][6]>=32?0u:s.registers[0][0]>>s.registers[0][6];}zn(&s,s.registers[0][0]);
 s.pc=0xf033ceu;break;
  case 0xf033ceu: /* addq    $8,r6 */
   s.registers[0][6]=add(&s,s.registers[0][6],8u);
   s.pc=0xf033d0u;break;
  case 0xf033d0u: /* or      r0,r7 */
   s.registers[0][7]|=s.registers[0][0];
   zn(&s,s.registers[0][7]);
   s.pc=0xf033d2u;break;
  case 0xf033d2u: /* move    r7,r0 */
   s.registers[0][0]=s.registers[0][7];
   s.pc=0xf033d4u;break;
  case 0xf033d4u: /* and     r8,r0 */
   s.registers[0][0]&=s.registers[0][8];
   zn(&s,s.registers[0][0]);
   s.pc=0xf033d6u;break;
  case 0xf033d6u: /* move    r11,r10 */
   s.registers[0][10]=s.registers[0][11];
   s.pc=0xf033d8u;break;
  case 0xf033d8u: /* shrq    $6,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=s.registers[0][0]>>6;zn(&s,s.registers[0][0]);
   s.pc=0xf033dau;break;
  case 0xf033dau: /* add     r0,r10 */
   s.registers[0][10]=add(&s,s.registers[0][10],s.registers[0][0]);
   s.pc=0xf033dcu;break;
  case 0xf033dcu: /* shrq    $2,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=s.registers[0][0]>>2;zn(&s,s.registers[0][0]);
   s.pc=0xf033deu;break;
  case 0xf033deu: /* subq    $2,r2 */
   s.registers[0][2]=sub(&s,s.registers[0][2],2u);
   s.pc=0xf033e0u;break;
  case 0xf033e0u: /* sub     r0,r2 */
   s.registers[0][2]=sub(&s,s.registers[0][2],s.registers[0][0]);
   s.pc=0xf033e2u;break;
case 0xf033e2u: /* load    (r10),r0 */
 CHECK(rd32(bus,&s,local(s.registers[0][10])?(s.registers[0][10]&~3u):s.registers[0][10],&v));s.registers[0][0]=v;
 s.pc=0xf033e4u;break;
  case 0xf033e4u: /* jump    (r0) */
   if(condition(&s,0)){pending=1;target=s.registers[0][0];}
   s.pc=0xf033e6u;break;
  case 0xf033e6u: /* storew  r5,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][5]));
   s.pc=0xf033e8u;break;
  case 0xf03428u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf0342au;break;
  case 0xf0342au: /* storew  r5,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][5]));
   s.pc=0xf0342cu;break;
  case 0xf0342cu: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf0342eu;break;
  case 0xf0342eu: /* storew  r5,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][5]));
   s.pc=0xf03430u;break;
  case 0xf03430u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf03432u;break;
  case 0xf03432u: /* storew  r5,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][5]));
   s.pc=0xf03434u;break;
  case 0xf03434u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf03436u;break;
  case 0xf03436u: /* storew  r5,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][5]));
   s.pc=0xf03438u;break;
  case 0xf03438u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf0343au;break;
  case 0xf0343au: /* storew  r5,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][5]));
   s.pc=0xf0343cu;break;
  case 0xf0343cu: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf0343eu;break;
  case 0xf0343eu: /* storew  r5,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][5]));
   s.pc=0xf03440u;break;
  case 0xf03440u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf03442u;break;
  case 0xf03442u: /* storew  r5,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][5]));
   s.pc=0xf03444u;break;
  case 0xf03444u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf03446u;break;
  case 0xf03446u: /* storew  r5,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][5]));
   s.pc=0xf03448u;break;
  case 0xf03448u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf0344au;break;
  case 0xf0344au: /* storew  r5,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][5]));
   s.pc=0xf0344cu;break;
  case 0xf0344cu: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf0344eu;break;
  case 0xf0344eu: /* storew  r5,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][5]));
   s.pc=0xf03450u;break;
  case 0xf03450u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf03452u;break;
  case 0xf03452u: /* storew  r5,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][5]));
   s.pc=0xf03454u;break;
  case 0xf03454u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf03456u;break;
  case 0xf03456u: /* storew  r5,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][5]));
   s.pc=0xf03458u;break;
  case 0xf03458u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf0345au;break;
  case 0xf0345au: /* storew  r5,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][5]));
   s.pc=0xf0345cu;break;
  case 0xf0345cu: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf0345eu;break;
  case 0xf0345eu: /* storew  r5,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][5]));
   s.pc=0xf03460u;break;
  case 0xf03460u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf03462u;break;
  case 0xf03462u: /* storew  r5,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][5]));
   s.pc=0xf03464u;break;
  case 0xf03464u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf03466u;break;
  case 0xf03466u: /* storew  r5,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][5]));
   s.pc=0xf03468u;break;
  case 0xf03468u: /* cmpq    $0,r2 */
   (void)sub(&s,s.registers[0][2],0x0u);
   s.pc=0xf0346au;break;
  case 0xf0346au: /* jump    nn,(r12) */
   if(condition(&s,20)){pending=1;target=s.registers[0][12];}
   s.pc=0xf0346cu;break;
  case 0xf0346cu: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf0346eu;break;
  case 0xf0346eu: /* jump    (r15) */
   if(condition(&s,0)){pending=1;target=s.registers[0][15];}
   s.pc=0xf03470u;break;
  case 0xf03470u: /* nop */
   s.pc=0xf03472u;break;
  case 0xf03472u: /* cmpq    $0,r6 */
   (void)sub(&s,s.registers[0][6],0x0u);
   s.pc=0xf03474u;break;
  case 0xf03474u: /* jr      nz,00F0347E */
   if(condition(&s,1)){pending=1;target=0xf0347eu;}
   s.pc=0xf03476u;break;
  case 0xf03476u: /* nop */
   s.pc=0xf03478u;break;
case 0xf03478u: /* loadb   (r1),r7 */
 CHECK(rd8(bus,&s,s.registers[0][1],&v));s.registers[0][7]=v;
 s.pc=0xf0347au;break;
  case 0xf0347au: /* moveq   8,r6 */
   s.registers[0][6]=8u;
   s.pc=0xf0347cu;break;
  case 0xf0347cu: /* addq    $1,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],1u);
   s.pc=0xf0347eu;break;
  case 0xf0347eu: /* btst    $7,r7 */
   s.z=((~s.registers[0][7])>>7)&1u;
   s.pc=0xf03480u;break;
case 0xf03480u: /* subqt   $1,r6 */
 s.registers[0][6]-=1u;
 s.pc=0xf03482u;break;
  case 0xf03482u: /* jump    z,(r13) */
   if(condition(&s,2)){pending=1;target=s.registers[0][13];}
   s.pc=0xf03484u;break;
  case 0xf03484u: /* shlq    $1,r7 */
   s.c=s.registers[0][7]>>31;s.registers[0][7]=s.registers[0][7]<<1;zn(&s,s.registers[0][7]);
   s.pc=0xf03486u;break;
  case 0xf03486u: /* subq    $3,r6 */
   s.registers[0][6]=sub(&s,s.registers[0][6],3u);
   s.pc=0xf03488u;break;
  case 0xf03488u: /* jr      nn,00F03496 */
   if(condition(&s,20)){pending=1;target=0xf03496u;}
   s.pc=0xf0348au;break;
  case 0xf0348au: /* shlq    $3,r7 */
   s.c=s.registers[0][7]>>31;s.registers[0][7]=s.registers[0][7]<<3;zn(&s,s.registers[0][7]);
   s.pc=0xf0348cu;break;
case 0xf0348cu: /* loadb   (r1),r0 */
 CHECK(rd8(bus,&s,s.registers[0][1],&v));s.registers[0][0]=v;
 s.pc=0xf0348eu;break;
  case 0xf0348eu: /* addq    $1,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],1u);
   s.pc=0xf03490u;break;
case 0xf03490u: /* sh      r6,r0 */
 if(s.registers[0][6]&0x80000000u){s.c=s.registers[0][0]>>31;s.registers[0][0]=(int32_t)s.registers[0][6]<=-32?0u:s.registers[0][0]<<(0u-s.registers[0][6]);}else{s.c=s.registers[0][0]&1u;s.registers[0][0]=s.registers[0][6]>=32?0u:s.registers[0][0]>>s.registers[0][6];}zn(&s,s.registers[0][0]);
 s.pc=0xf03492u;break;
  case 0xf03492u: /* addq    $8,r6 */
   s.registers[0][6]=add(&s,s.registers[0][6],8u);
   s.pc=0xf03494u;break;
  case 0xf03494u: /* or      r0,r7 */
   s.registers[0][7]|=s.registers[0][0];
   zn(&s,s.registers[0][7]);
   s.pc=0xf03496u;break;
  case 0xf03496u: /* move    r7,r0 */
   s.registers[0][0]=s.registers[0][7];
   s.pc=0xf03498u;break;
  case 0xf03498u: /* and     r19,r0 */
   s.registers[0][0]&=s.registers[0][19];
   zn(&s,s.registers[0][0]);
   s.pc=0xf0349au;break;
  case 0xf0349au: /* move    r14,r10 */
   s.registers[0][10]=s.registers[0][14];
   s.pc=0xf0349cu;break;
  case 0xf0349cu: /* shrq    $6,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=s.registers[0][0]>>6;zn(&s,s.registers[0][0]);
   s.pc=0xf0349eu;break;
  case 0xf0349eu: /* add     r0,r10 */
   s.registers[0][10]=add(&s,s.registers[0][10],s.registers[0][0]);
   s.pc=0xf034a0u;break;
  case 0xf034a0u: /* shrq    $2,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=s.registers[0][0]>>2;zn(&s,s.registers[0][0]);
   s.pc=0xf034a2u;break;
  case 0xf034a2u: /* subq    $2,r2 */
   s.registers[0][2]=sub(&s,s.registers[0][2],2u);
   s.pc=0xf034a4u;break;
  case 0xf034a4u: /* sub     r0,r2 */
   s.registers[0][2]=sub(&s,s.registers[0][2],s.registers[0][0]);
   s.pc=0xf034a6u;break;
case 0xf034a6u: /* loadb   (r1),r0 */
 CHECK(rd8(bus,&s,s.registers[0][1],&v));s.registers[0][0]=v;
 s.pc=0xf034a8u;break;
  case 0xf034a8u: /* addq    $1,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],1u);
   s.pc=0xf034aau;break;
  case 0xf034aau: /* shlq    $1,r0 */
   s.c=s.registers[0][0]>>31;s.registers[0][0]=s.registers[0][0]<<1;zn(&s,s.registers[0][0]);
   s.pc=0xf034acu;break;
  case 0xf034acu: /* add     r4,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][4]);
   s.pc=0xf034aeu;break;
  case 0xf034aeu: /* loadw   (r0),r0 */
   CHECK(loadw(bus,&s,s.registers[0][0],&v));s.registers[0][0]=v;
   s.pc=0xf034b0u;break;
case 0xf034b0u: /* load    (r10),r10 */
 CHECK(rd32(bus,&s,local(s.registers[0][10])?(s.registers[0][10]&~3u):s.registers[0][10],&v));s.registers[0][10]=v;
 s.pc=0xf034b2u;break;
  case 0xf034b2u: /* jump    (r10) */
   if(condition(&s,0)){pending=1;target=s.registers[0][10];}
   s.pc=0xf034b4u;break;
  case 0xf034b4u: /* storew  r0,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][0]));
   s.pc=0xf034b6u;break;
  case 0xf03518u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf0351au;break;
  case 0xf0351au: /* storew  r0,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][0]));
   s.pc=0xf0351cu;break;
  case 0xf0351cu: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf0351eu;break;
  case 0xf0351eu: /* storew  r0,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][0]));
   s.pc=0xf03520u;break;
  case 0xf03520u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf03522u;break;
  case 0xf03522u: /* storew  r0,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][0]));
   s.pc=0xf03524u;break;
  case 0xf03524u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf03526u;break;
  case 0xf03526u: /* storew  r0,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][0]));
   s.pc=0xf03528u;break;
  case 0xf03528u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf0352au;break;
  case 0xf0352au: /* storew  r0,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][0]));
   s.pc=0xf0352cu;break;
  case 0xf0352cu: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf0352eu;break;
  case 0xf0352eu: /* storew  r0,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][0]));
   s.pc=0xf03530u;break;
  case 0xf03530u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf03532u;break;
  case 0xf03532u: /* storew  r0,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][0]));
   s.pc=0xf03534u;break;
  case 0xf03534u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf03536u;break;
  case 0xf03536u: /* storew  r0,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][0]));
   s.pc=0xf03538u;break;
  case 0xf03538u: /* cmpq    $0,r2 */
   (void)sub(&s,s.registers[0][2],0x0u);
   s.pc=0xf0353au;break;
  case 0xf0353au: /* jump    nn,(r12) */
   if(condition(&s,20)){pending=1;target=s.registers[0][12];}
   s.pc=0xf0353cu;break;
  case 0xf0353cu: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf0353eu;break;
  case 0xf03542u: /* subq    $4,r6 */
   s.registers[0][6]=sub(&s,s.registers[0][6],4u);
   s.pc=0xf03544u;break;
  case 0xf03544u: /* jr      nn,00F03552 */
   if(condition(&s,20)){pending=1;target=0xf03552u;}
   s.pc=0xf03546u;break;
  case 0xf03546u: /* shlq    $4,r7 */
   s.c=s.registers[0][7]>>31;s.registers[0][7]=s.registers[0][7]<<4;zn(&s,s.registers[0][7]);
   s.pc=0xf03548u;break;
case 0xf03548u: /* loadb   (r1),r0 */
 CHECK(rd8(bus,&s,s.registers[0][1],&v));s.registers[0][0]=v;
 s.pc=0xf0354au;break;
  case 0xf0354au: /* addq    $1,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],1u);
   s.pc=0xf0354cu;break;
case 0xf0354cu: /* sh      r6,r0 */
 if(s.registers[0][6]&0x80000000u){s.c=s.registers[0][0]>>31;s.registers[0][0]=(int32_t)s.registers[0][6]<=-32?0u:s.registers[0][0]<<(0u-s.registers[0][6]);}else{s.c=s.registers[0][0]&1u;s.registers[0][0]=s.registers[0][6]>=32?0u:s.registers[0][0]>>s.registers[0][6];}zn(&s,s.registers[0][0]);
 s.pc=0xf0354eu;break;
  case 0xf0354eu: /* addq    $8,r6 */
   s.registers[0][6]=add(&s,s.registers[0][6],8u);
   s.pc=0xf03550u;break;
  case 0xf03550u: /* or      r0,r7 */
   s.registers[0][7]|=s.registers[0][0];
   zn(&s,s.registers[0][7]);
   s.pc=0xf03552u;break;
  case 0xf03552u: /* move    r7,r0 */
   s.registers[0][0]=s.registers[0][7];
   s.pc=0xf03554u;break;
  case 0xf03554u: /* and     r20,r0 */
   s.registers[0][0]&=s.registers[0][20];
   zn(&s,s.registers[0][0]);
   s.pc=0xf03556u;break;
  case 0xf03556u: /* shrq    $8,r0 */
   s.c=s.registers[0][0]&1u;s.registers[0][0]=s.registers[0][0]>>8;zn(&s,s.registers[0][0]);
   s.pc=0xf03558u;break;
  case 0xf03558u: /* sub     r0,r2 */
   s.registers[0][2]=sub(&s,s.registers[0][2],s.registers[0][0]);
   s.pc=0xf0355au;break;
  case 0xf0355au: /* subq    $1,r2 */
   s.registers[0][2]=sub(&s,s.registers[0][2],1u);
   s.pc=0xf0355cu;break;
case 0xf0355cu: /* loadb   (r1),r16 */
 CHECK(rd8(bus,&s,s.registers[0][1],&v));s.registers[0][16]=v;
 s.pc=0xf0355eu;break;
  case 0xf0355eu: /* addq    $1,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],1u);
   s.pc=0xf03560u;break;
  case 0xf03560u: /* shlq    $1,r16 */
   s.c=s.registers[0][16]>>31;s.registers[0][16]=s.registers[0][16]<<1;zn(&s,s.registers[0][16]);
   s.pc=0xf03562u;break;
  case 0xf03562u: /* add     r4,r16 */
   s.registers[0][16]=add(&s,s.registers[0][16],s.registers[0][4]);
   s.pc=0xf03564u;break;
  case 0xf03564u: /* loadw   (r16),r16 */
   CHECK(loadw(bus,&s,s.registers[0][16],&v));s.registers[0][16]=v;
   s.pc=0xf03566u;break;
  case 0xf03566u: /* storew  r16,(r3) */
   CHECK(wr16(bus,&s,s.registers[0][3],s.registers[0][16]));
   s.pc=0xf03568u;break;
  case 0xf03568u: /* addq    $2,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],2u);
   s.pc=0xf0356au;break;
  case 0xf0356au: /* subq    $1,r0 */
   s.registers[0][0]=sub(&s,s.registers[0][0],1u);
   s.pc=0xf0356cu;break;
  case 0xf0356cu: /* jr      nn,00F0355E */
   if(condition(&s,20)){pending=1;target=0xf0355eu;}
   s.pc=0xf0356eu;break;
case 0xf0356eu: /* loadb   (r1),r16 */
 CHECK(rd8(bus,&s,s.registers[0][1],&v));s.registers[0][16]=v;
 s.pc=0xf03570u;break;
  case 0xf03570u: /* cmpq    $0,r2 */
   (void)sub(&s,s.registers[0][2],0x0u);
   s.pc=0xf03572u;break;
  case 0xf03572u: /* jump    nn,(r12) */
   if(condition(&s,20)){pending=1;target=s.registers[0][12];}
   s.pc=0xf03574u;break;
  case 0xf03574u: /* nop */
   s.pc=0xf03576u;break;
  case 0xf03576u: /* movei   $f0211c,r18 */
   s.registers[0][18]=0xf0211cu;
   s.pc=0xf0357cu;break;
  case 0xf0357cu: /* moveq   0,r0 */
   s.registers[0][0]=0u;
   s.pc=0xf0357eu;break;
  case 0xf0357eu: /* store   r0,(r18) */
   CHECK(wr32(bus,&s,local(s.registers[0][18])?(s.registers[0][18]&~3u):s.registers[0][18],s.registers[0][0]));
   s.pc=0xf03580u;break;
  case 0xf03580u: /* jump    (r25) */
   if(condition(&s,0)){pending=1;target=s.registers[0][25];}
   s.pc=0xf03582u;break;
  case 0xf03582u: /* nop */
   s.pc=0xf03584u;break;default:return BIWN_GAME_FIRSTBOOT_GPU_BAD_PC;
}if(delayed){if(pending)return BIWN_GAME_FIRSTBOOT_GPU_BAD_DELAY;s.pc=resume;}if(!pending&&s.pc==stopPC){*state=s;return 0;}}return BIWN_GAME_FIRSTBOOT_GPU_WORK_LIMIT;}
