/* Generated from the pinned GPU6E80 overlay by
 * scripts/generate_biwn_gpu_room_consumer6e80.py. Analyst static recompilation,
 * not recovered original source. Integer primitive behavior is checked
 * against the pinned Virtual Jaguar core; no core runs on the C side. */
#include "biwn_gpu_room_consumer6e80.h"
#include <string.h>
static void zn(struct biwn_gpu_room_consumer6e80_state *s,uint32_t v){s->z=v==0;s->n=v>>31;}
static uint32_t add(struct biwn_gpu_room_consumer6e80_state *s,uint32_t a,uint32_t b){uint32_t v=a+b;s->c=b>~a;zn(s,v);return v;}
static uint32_t sub(struct biwn_gpu_room_consumer6e80_state *s,uint32_t a,uint32_t b){uint32_t v=a-b;s->c=b>a;zn(s,v);return v;}
static int condition(struct biwn_gpu_room_consumer6e80_state *s,unsigned code){unsigned flags=s->z|(s->c<<1)|(s->n<<2);return !((code&1u)&&(flags&1u))&&!((code&2u)&&!(flags&1u))&&!((code&4u)&&(flags&(2u<<(code>>4))))&&!((code&8u)&&!(flags&(2u<<(code>>4))));}
static uint32_t be32(const uint8_t *p){return((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
static void put32(uint8_t *p,uint32_t v){p[0]=(uint8_t)(v>>24);p[1]=(uint8_t)(v>>16);p[2]=(uint8_t)(v>>8);p[3]=(uint8_t)v;}
static int local(uint32_t a){return a>=0xf03000u&&a<=0xf03ffcu;}
static int rd32(struct biwn_gpu_room_consumer6e80_bus *bus,struct biwn_gpu_room_consumer6e80_state *s,uint32_t a,uint32_t *v){if(local(a)){*v=be32(s->local_RAM+a-0xf03000u);return 0;}if(a==0xf02104u){*v=s->matrix_control;return 0;}if(a==0xf02108u){*v=s->matrix_pointer;return 0;}return bus->read32(bus->context,a,v)?2:0;}
static int rd16(struct biwn_gpu_room_consumer6e80_bus *bus,struct biwn_gpu_room_consumer6e80_state *s,uint32_t a,uint32_t *v){uint16_t h;if(a>=0xf03000u&&a<=0xf03ffeu){unsigned p=a-0xf03000u;*v=((uint32_t)s->local_RAM[p]<<8)|s->local_RAM[p+1];return 0;}if(bus->read16(bus->context,a,&h))return 2;*v=h;return 0;}
static int loadw(struct biwn_gpu_room_consumer6e80_bus *bus,struct biwn_gpu_room_consumer6e80_state *s,uint32_t a,uint32_t *v){if(a>=0xf03000u&&a<=0xf03fffu)return rd32(bus,s,a&~3u,v);return rd16(bus,s,a,v);}
static int wr32(struct biwn_gpu_room_consumer6e80_bus *bus,struct biwn_gpu_room_consumer6e80_state *s,uint32_t a,uint32_t v){if(local(a)){put32(s->local_RAM+a-0xf03000u,v);return 0;}if(a==0xf02104u){s->matrix_control=v;return 0;}if(a==0xf02108u){s->matrix_pointer=v&~3u;return 0;}return bus->write32(bus->context,a,v)?2:0;}
static int wr16(struct biwn_gpu_room_consumer6e80_bus *bus,struct biwn_gpu_room_consumer6e80_state *s,uint32_t a,uint32_t v){if(a>=0xf03000u&&a<=0xf03fffu)return wr32(bus,s,a&~1u,v&0xffffu);return bus->write16(bus->context,a,(uint16_t)v)?2:0;}
#define CHECK(e) do{int status=(e);if(status)return(enum biwn_gpu_room_consumer6e80_status)status;}while(0)
enum biwn_gpu_room_consumer6e80_status biwn_gpu_room_consumer6e80_run(struct biwn_gpu_room_consumer6e80_bus *bus,struct biwn_gpu_room_consumer6e80_state *state,uint32_t budget){struct biwn_gpu_room_consumer6e80_state s;uint32_t v,target=0;unsigned pending=0;if(!bus||!state||!budget||!bus->read16||!bus->read32||!bus->write16||!bus->write32||state->z>1||state->c>1||state->n>1)return 1;s=*state;while(budget--){unsigned delayed=pending;uint32_t resume=target;pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){
  case 0xf03240u: /* addq    $18,r24 */
   s.registers[0][24]=add(&s,s.registers[0][24],24u);
   s.pc=0xf03242u;break;
  case 0xf03242u: /* addq    $a,r24 */
   s.registers[0][24]=add(&s,s.registers[0][24],10u);
   s.pc=0xf03244u;break;
  case 0xf03244u: /* loadw   (r24),r1 */
   CHECK(loadw(bus,&s,s.registers[0][24],&v));s.registers[0][1]=v;
   s.pc=0xf03246u;break;
  case 0xf03246u: /* addq    $1a,r24 */
   s.registers[0][24]=add(&s,s.registers[0][24],26u);
   s.pc=0xf03248u;break;
  case 0xf03248u: /* moveq   24,r2 */
   s.registers[0][2]=24u;
   s.pc=0xf0324au;break;
  case 0xf0324au: /* load    (r24),r0 */
   CHECK(rd32(bus,&s,s.registers[0][24]&~3u,&v));s.registers[0][0]=v;
   s.pc=0xf0324cu;break;
  case 0xf0324cu: /* mult    r2,r1 */
   s.registers[0][1]=(s.registers[0][1]&0xffffu)*(s.registers[0][2]&0xffffu);
   zn(&s,s.registers[0][1]);
   s.pc=0xf0324eu;break;
  case 0xf0324eu: /* store   r25,(r24) */
   CHECK(wr32(bus,&s,local(s.registers[0][24])?(s.registers[0][24]&~3u):s.registers[0][24],s.registers[0][25]));
   s.pc=0xf03250u;break;
  case 0xf03250u: /* addq    $4,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],4u);
   s.pc=0xf03252u;break;
  case 0xf03252u: /* load    (r0),r18 */
   CHECK(rd32(bus,&s,s.registers[0][0]&~3u,&v));s.registers[0][18]=v;
   s.pc=0xf03254u;break;
  case 0xf03254u: /* addq    $4,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],4u);
   s.pc=0xf03256u;break;
  case 0xf03256u: /* load    (r0),r19 */
   CHECK(rd32(bus,&s,s.registers[0][0]&~3u,&v));s.registers[0][19]=v;
   s.pc=0xf03258u;break;
  case 0xf03258u: /* add     r1,r18 */
   s.registers[0][18]=add(&s,s.registers[0][18],s.registers[0][1]);
   s.pc=0xf0325au;break;
  case 0xf0325au: /* addq    $6,r18 */
   s.registers[0][18]=add(&s,s.registers[0][18],6u);
   s.pc=0xf0325cu;break;
  case 0xf0325cu: /* loadw   (r18),r20 */
   CHECK(loadw(bus,&s,s.registers[0][18],&v));s.registers[0][20]=v;
   s.pc=0xf0325eu;break;
  case 0xf0325eu: /* addq    $2,r18 */
   s.registers[0][18]=add(&s,s.registers[0][18],2u);
   s.pc=0xf03260u;break;
  case 0xf03260u: /* loadw   (r18),r21 */
   CHECK(loadw(bus,&s,s.registers[0][18],&v));s.registers[0][21]=v;
   s.pc=0xf03262u;break;
  case 0xf03262u: /* addq    $e,r18 */
   s.registers[0][18]=add(&s,s.registers[0][18],14u);
   s.pc=0xf03264u;break;
  case 0xf03264u: /* loadw   (r18),r3 */
   CHECK(loadw(bus,&s,s.registers[0][18],&v));s.registers[0][3]=v;
   s.pc=0xf03266u;break;
  case 0xf03266u: /* moveq   6,r4 */
   s.registers[0][4]=6u;
   s.pc=0xf03268u;break;
  case 0xf03268u: /* subq    $16,r18 */
   s.registers[0][18]=sub(&s,s.registers[0][18],22u);
   s.pc=0xf0326au;break;
  case 0xf0326au: /* mult    r4,r3 */
   s.registers[0][3]=(s.registers[0][3]&0xffffu)*(s.registers[0][4]&0xffffu);
   zn(&s,s.registers[0][3]);
   s.pc=0xf0326cu;break;
  case 0xf0326cu: /* add     r3,r19 */
   s.registers[0][19]=add(&s,s.registers[0][19],s.registers[0][3]);
   s.pc=0xf0326eu;break;
  case 0xf0326eu: /* move    r21,r22 */
   s.registers[0][22]=s.registers[0][21];
   s.pc=0xf03270u;break;
  case 0xf03270u: /* movei   $40,r10 */
   s.registers[0][10]=0x40u;
   s.pc=0xf03276u;break;
  case 0xf03276u: /* addq    $1,r22 */
   s.registers[0][22]=add(&s,s.registers[0][22],1u);
   s.pc=0xf03278u;break;
  case 0xf03278u: /* move    r20,r8 */
   s.registers[0][8]=s.registers[0][20];
   s.pc=0xf0327au;break;
  case 0xf0327au: /* move    r21,r9 */
   s.registers[0][9]=s.registers[0][21];
   s.pc=0xf0327cu;break;
  case 0xf0327cu: /* mult    r10,r8 */
   s.registers[0][8]=(s.registers[0][8]&0xffffu)*(s.registers[0][10]&0xffffu);
   zn(&s,s.registers[0][8]);
   s.pc=0xf0327eu;break;
  case 0xf0327eu: /* moveq   0,r6 */
   s.registers[0][6]=0u;
   s.pc=0xf03280u;break;
  case 0xf03280u: /* mult    r10,r9 */
   s.registers[0][9]=(s.registers[0][9]&0xffffu)*(s.registers[0][10]&0xffffu);
   zn(&s,s.registers[0][9]);
   s.pc=0xf03282u;break;
  case 0xf03282u: /* moveq   0,r5 */
   s.registers[0][5]=0u;
   s.pc=0xf03284u;break;
  case 0xf03284u: /* sub     r10,r6 */
   s.registers[0][6]=sub(&s,s.registers[0][6],s.registers[0][10]);
   s.pc=0xf03286u;break;
  case 0xf03286u: /* moveq   0,r7 */
   s.registers[0][7]=0u;
   s.pc=0xf03288u;break;
  case 0xf03288u: /* storew  r5,(r27) */
   CHECK(wr16(bus,&s,s.registers[0][27],s.registers[0][5]));
   s.pc=0xf0328au;break;
  case 0xf0328au: /* addq    $2,r27 */
   s.registers[0][27]=add(&s,s.registers[0][27],2u);
   s.pc=0xf0328cu;break;
  case 0xf0328cu: /* storew  r6,(r27) */
   CHECK(wr16(bus,&s,s.registers[0][27],s.registers[0][6]));
   s.pc=0xf0328eu;break;
  case 0xf0328eu: /* addq    $2,r27 */
   s.registers[0][27]=add(&s,s.registers[0][27],2u);
   s.pc=0xf03290u;break;
  case 0xf03290u: /* storew  r7,(r27) */
   CHECK(wr16(bus,&s,s.registers[0][27],s.registers[0][7]));
   s.pc=0xf03292u;break;
  case 0xf03292u: /* addq    $2,r27 */
   s.registers[0][27]=add(&s,s.registers[0][27],2u);
   s.pc=0xf03294u;break;
  case 0xf03294u: /* cmp     r7,r9 */
   (void)sub(&s,s.registers[0][9],s.registers[0][7]);
   s.pc=0xf03296u;break;
  case 0xf03296u: /* jr      nz,00F03288 */
   if(condition(&s,1)){pending=1;target=0xf03288u;}
   s.pc=0xf03298u;break;
  case 0xf03298u: /* add     r10,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],s.registers[0][10]);
   s.pc=0xf0329au;break;
  case 0xf0329au: /* cmp     r5,r8 */
   (void)sub(&s,s.registers[0][8],s.registers[0][5]);
   s.pc=0xf0329cu;break;
  case 0xf0329cu: /* jr      nz,00F03286 */
   if(condition(&s,1)){pending=1;target=0xf03286u;}
   s.pc=0xf0329eu;break;
  case 0xf0329eu: /* add     r10,r5 */
   s.registers[0][5]=add(&s,s.registers[0][5],s.registers[0][10]);
   s.pc=0xf032a0u;break;
  case 0xf032a0u: /* add     r10,r6 */
   s.registers[0][6]=add(&s,s.registers[0][6],s.registers[0][10]);
   s.pc=0xf032a2u;break;
  case 0xf032a2u: /* jr      z,00F03286 */
   if(condition(&s,2)){pending=1;target=0xf03286u;}
   s.pc=0xf032a4u;break;
  case 0xf032a4u: /* moveq   0,r5 */
   s.registers[0][5]=0u;
   s.pc=0xf032a6u;break;
  case 0xf032a6u: /* addq    $a,r18 */
   s.registers[0][18]=add(&s,s.registers[0][18],10u);
   s.pc=0xf032a8u;break;
  case 0xf032a8u: /* loadw   (r18),r0 */
   CHECK(loadw(bus,&s,s.registers[0][18],&v));s.registers[0][0]=v;
   s.pc=0xf032aau;break;
  case 0xf032aau: /* addq    $2,r18 */
   s.registers[0][18]=add(&s,s.registers[0][18],2u);
   s.pc=0xf032acu;break;
  case 0xf032acu: /* shlq    $10,r0 */
   s.c=s.registers[0][0]>>31;s.registers[0][0]=s.registers[0][0]<<16;zn(&s,s.registers[0][0]);
   s.pc=0xf032aeu;break;
  case 0xf032aeu: /* loadw   (r18),r1 */
   CHECK(loadw(bus,&s,s.registers[0][18],&v));s.registers[0][1]=v;
   s.pc=0xf032b0u;break;
  case 0xf032b0u: /* moveta  r0,r20 */
   s.registers[1][20]=s.registers[0][0];
   s.pc=0xf032b2u;break;
  case 0xf032b2u: /* addq    $2,r18 */
   s.registers[0][18]=add(&s,s.registers[0][18],2u);
   s.pc=0xf032b4u;break;
  case 0xf032b4u: /* shlq    $10,r1 */
   s.c=s.registers[0][1]>>31;s.registers[0][1]=s.registers[0][1]<<16;zn(&s,s.registers[0][1]);
   s.pc=0xf032b6u;break;
  case 0xf032b6u: /* loadw   (r18),r2 */
   CHECK(loadw(bus,&s,s.registers[0][18],&v));s.registers[0][2]=v;
   s.pc=0xf032b8u;break;
  case 0xf032b8u: /* moveta  r1,r21 */
   s.registers[1][21]=s.registers[0][1];
   s.pc=0xf032bau;break;
  case 0xf032bau: /* addq    $2,r18 */
   s.registers[0][18]=add(&s,s.registers[0][18],2u);
   s.pc=0xf032bcu;break;
  case 0xf032bcu: /* shlq    $10,r2 */
   s.c=s.registers[0][2]>>31;s.registers[0][2]=s.registers[0][2]<<16;zn(&s,s.registers[0][2]);
   s.pc=0xf032beu;break;
  case 0xf032beu: /* loadw   (r18),r3 */
   CHECK(loadw(bus,&s,s.registers[0][18],&v));s.registers[0][3]=v;
   s.pc=0xf032c0u;break;
  case 0xf032c0u: /* moveta  r2,r22 */
   s.registers[1][22]=s.registers[0][2];
   s.pc=0xf032c2u;break;
  case 0xf032c2u: /* addq    $2,r18 */
   s.registers[0][18]=add(&s,s.registers[0][18],2u);
   s.pc=0xf032c4u;break;
  case 0xf032c4u: /* shlq    $10,r3 */
   s.c=s.registers[0][3]>>31;s.registers[0][3]=s.registers[0][3]<<16;zn(&s,s.registers[0][3]);
   s.pc=0xf032c6u;break;
  case 0xf032c6u: /* loadw   (r18),r4 */
   CHECK(loadw(bus,&s,s.registers[0][18],&v));s.registers[0][4]=v;
   s.pc=0xf032c8u;break;
  case 0xf032c8u: /* moveta  r3,r23 */
   s.registers[1][23]=s.registers[0][3];
   s.pc=0xf032cau;break;
  case 0xf032cau: /* addq    $2,r18 */
   s.registers[0][18]=add(&s,s.registers[0][18],2u);
   s.pc=0xf032ccu;break;
  case 0xf032ccu: /* shlq    $10,r4 */
   s.c=s.registers[0][4]>>31;s.registers[0][4]=s.registers[0][4]<<16;zn(&s,s.registers[0][4]);
   s.pc=0xf032ceu;break;
  case 0xf032ceu: /* loadw   (r18),r5 */
   CHECK(loadw(bus,&s,s.registers[0][18],&v));s.registers[0][5]=v;
   s.pc=0xf032d0u;break;
  case 0xf032d0u: /* moveta  r4,r24 */
   s.registers[1][24]=s.registers[0][4];
   s.pc=0xf032d2u;break;
  case 0xf032d2u: /* shlq    $10,r5 */
   s.c=s.registers[0][5]>>31;s.registers[0][5]=s.registers[0][5]<<16;zn(&s,s.registers[0][5]);
   s.pc=0xf032d4u;break;
  case 0xf032d4u: /* moveta  r5,r25 */
   s.registers[1][25]=s.registers[0][5];
   s.pc=0xf032d6u;break;
  case 0xf032d6u: /* moveq   0,r23 */
   s.registers[0][23]=0u;
   s.pc=0xf032d8u;break;
  case 0xf032d8u: /* movei   $f03362,r6 */
   s.registers[0][6]=0xf03362u;
   s.pc=0xf032deu;break;
  case 0xf032deu: /* movei   $4ffff,r17 */
   s.registers[0][17]=0x4ffffu;
   s.pc=0xf032e4u;break;
  case 0xf032e4u: /* move    pc,r7 */
   s.registers[0][7]=0xf032e4u;
   s.pc=0xf032e6u;break;
  case 0xf032e6u: /* moveq   0,r0 */
   s.registers[0][0]=0u;
   s.pc=0xf032e8u;break;
  case 0xf032e8u: /* moveq   0,r1 */
   s.registers[0][1]=0u;
   s.pc=0xf032eau;break;
  case 0xf032eau: /* moveq   1,r2 */
   s.registers[0][2]=1u;
   s.pc=0xf032ecu;break;
  case 0xf032ecu: /* moveq   1,r3 */
   s.registers[0][3]=1u;
   s.pc=0xf032eeu;break;
  case 0xf032eeu: /* movefa  r20,r5 */
   s.registers[0][5]=s.registers[1][20];
   s.pc=0xf032f0u;break;
  case 0xf032f0u: /* jump    (r6) */
   if(condition(&s,0)){pending=1;target=s.registers[0][6];}
   s.pc=0xf032f2u;break;
  case 0xf032f2u: /* addq    $10,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],16u);
   s.pc=0xf032f4u;break;
  case 0xf032f4u: /* move    r2,r0 */
   s.registers[0][0]=s.registers[0][2];
   s.pc=0xf032f6u;break;
  case 0xf032f6u: /* move    r1,r3 */
   s.registers[0][3]=s.registers[0][1];
   s.pc=0xf032f8u;break;
  case 0xf032f8u: /* move    r0,r1 */
   s.registers[0][1]=s.registers[0][0];
   s.pc=0xf032fau;break;
  case 0xf032fau: /* move    r3,r2 */
   s.registers[0][2]=s.registers[0][3];
   s.pc=0xf032fcu;break;
  case 0xf032fcu: /* movefa  r21,r5 */
   s.registers[0][5]=s.registers[1][21];
   s.pc=0xf032feu;break;
  case 0xf032feu: /* jump    (r6) */
   if(condition(&s,0)){pending=1;target=s.registers[0][6];}
   s.pc=0xf03300u;break;
  case 0xf03300u: /* addq    $e,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],14u);
   s.pc=0xf03302u;break;
  case 0xf03302u: /* movei   $f033a0,r6 */
   s.registers[0][6]=0xf033a0u;
   s.pc=0xf03308u;break;
  case 0xf03308u: /* movei   $f033aa,r8 */
   s.registers[0][8]=0xf033aau;
   s.pc=0xf0330eu;break;
  case 0xf0330eu: /* movei   $f033e2,r15 */
   s.registers[0][15]=0xf033e2u;
   s.pc=0xf03314u;break;
  case 0xf03314u: /* movei   $40000,r17 */
   s.registers[0][17]=0x40000u;
   s.pc=0xf0331au;break;
  case 0xf0331au: /* moveq   1,r9 */
   s.registers[0][9]=1u;
   s.pc=0xf0331cu;break;
  case 0xf0331cu: /* move    r1,r3 */
   s.registers[0][3]=s.registers[0][1];
   s.pc=0xf0331eu;break;
  case 0xf0331eu: /* neg     r9 */
   s.registers[0][9]=sub(&s,0,s.registers[0][9]);
   s.pc=0xf03320u;break;
  case 0xf03320u: /* moveq   0,r0 */
   s.registers[0][0]=0u;
   s.pc=0xf03322u;break;
  case 0xf03322u: /* move    r9,r11 */
   s.registers[0][11]=s.registers[0][9];
   s.pc=0xf03324u;break;
  case 0xf03324u: /* shrq    $1,r3 */
   s.c=s.registers[0][3]&1u;s.registers[0][3]=s.registers[0][3]>>1;zn(&s,s.registers[0][3]);
   s.pc=0xf03326u;break;
  case 0xf03326u: /* moveq   0,r10 */
   s.registers[0][10]=0u;
   s.pc=0xf03328u;break;
  case 0xf03328u: /* move    pc,r7 */
   s.registers[0][7]=0xf03328u;
   s.pc=0xf0332au;break;
  case 0xf0332au: /* moveq   1,r4 */
   s.registers[0][4]=1u;
   s.pc=0xf0332cu;break;
  case 0xf0332cu: /* move    r21,r14 */
   s.registers[0][14]=s.registers[0][21];
   s.pc=0xf0332eu;break;
  case 0xf0332eu: /* jump    (r6) */
   if(condition(&s,0)){pending=1;target=s.registers[0][6];}
   s.pc=0xf03330u;break;
  case 0xf03330u: /* addq    $a,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],10u);
   s.pc=0xf03332u;break;
  case 0xf03332u: /* move    r22,r4 */
   s.registers[0][4]=s.registers[0][22];
   s.pc=0xf03334u;break;
  case 0xf03334u: /* move    r20,r14 */
   s.registers[0][14]=s.registers[0][20];
   s.pc=0xf03336u;break;
  case 0xf03336u: /* jump    (r6) */
   if(condition(&s,0)){pending=1;target=s.registers[0][6];}
   s.pc=0xf03338u;break;
  case 0xf03338u: /* addq    $8,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],8u);
   s.pc=0xf0333au;break;
  case 0xf0333au: /* move    r9,r4 */
   s.registers[0][4]=s.registers[0][9];
   s.pc=0xf0333cu;break;
  case 0xf0333cu: /* move    r21,r14 */
   s.registers[0][14]=s.registers[0][21];
   s.pc=0xf0333eu;break;
  case 0xf0333eu: /* jump    (r6) */
   if(condition(&s,0)){pending=1;target=s.registers[0][6];}
   s.pc=0xf03340u;break;
  case 0xf03340u: /* addq    $8,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],8u);
   s.pc=0xf03342u;break;
  case 0xf03342u: /* move    r22,r4 */
   s.registers[0][4]=s.registers[0][22];
   s.pc=0xf03344u;break;
  case 0xf03344u: /* neg     r4 */
   s.registers[0][4]=sub(&s,0,s.registers[0][4]);
   s.pc=0xf03346u;break;
  case 0xf03346u: /* move    r20,r14 */
   s.registers[0][14]=s.registers[0][20];
   s.pc=0xf03348u;break;
  case 0xf03348u: /* jump    (r6) */
   if(condition(&s,0)){pending=1;target=s.registers[0][6];}
   s.pc=0xf0334au;break;
  case 0xf0334au: /* addq    $a,r7 */
   s.registers[0][7]=add(&s,s.registers[0][7],10u);
   s.pc=0xf0334cu;break;
  case 0xf0334cu: /* addq    $2,r25 */
   s.registers[0][25]=add(&s,s.registers[0][25],2u);
   s.pc=0xf0334eu;break;
  case 0xf0334eu: /* storew  r23,(r25) */
   CHECK(wr16(bus,&s,s.registers[0][25],s.registers[0][23]));
   s.pc=0xf03350u;break;
  case 0xf03350u: /* addq    $1,r20 */
   s.registers[0][20]=add(&s,s.registers[0][20],1u);
   s.pc=0xf03352u;break;
  case 0xf03352u: /* movei   $f03440,r15 */
   s.registers[0][15]=0xf03440u;
   s.pc=0xf03358u;break;
  case 0xf03358u: /* mult    r22,r20 */
   s.registers[0][20]=(s.registers[0][20]&0xffffu)*(s.registers[0][22]&0xffffu);
   zn(&s,s.registers[0][20]);
   s.pc=0xf0335au;break;
  case 0xf0335au: /* subq    $2,r25 */
   s.registers[0][25]=sub(&s,s.registers[0][25],2u);
   s.pc=0xf0335cu;break;
  case 0xf0335cu: /* shlq    $1,r20 */
   s.c=s.registers[0][20]>>31;s.registers[0][20]=s.registers[0][20]<<1;zn(&s,s.registers[0][20]);
   s.pc=0xf0335eu;break;
  case 0xf0335eu: /* jump    (r15) */
   if(condition(&s,0)){pending=1;target=s.registers[0][15];}
   s.pc=0xf03360u;break;
  case 0xf03360u: /* storew  r20,(r25) */
   CHECK(wr16(bus,&s,s.registers[0][25],s.registers[0][20]));
   s.pc=0xf03362u;break;
  case 0xf03362u: /* add     r22,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],s.registers[0][22]);
   s.pc=0xf03364u;break;
  case 0xf03364u: /* move    r20,r9 */
   s.registers[0][9]=s.registers[0][20];
   s.pc=0xf03366u;break;
  case 0xf03366u: /* add     r22,r2 */
   s.registers[0][2]=add(&s,s.registers[0][2],s.registers[0][22]);
   s.pc=0xf03368u;break;
  case 0xf03368u: /* subq    $1,r9 */
   s.registers[0][9]=sub(&s,s.registers[0][9],1u);
   s.pc=0xf0336au;break;
  case 0xf0336au: /* jump    n,(r7) */
   if(condition(&s,24)){pending=1;target=s.registers[0][7];}
   s.pc=0xf0336cu;break;
  case 0xf0336cu: /* move    r21,r10 */
   s.registers[0][10]=s.registers[0][21];
   s.pc=0xf0336eu;break;
  case 0xf0336eu: /* movei   $f03368,r8 */
   s.registers[0][8]=0xf03368u;
   s.pc=0xf03374u;break;
  case 0xf03374u: /* subq    $1,r10 */
   s.registers[0][10]=sub(&s,s.registers[0][10],1u);
   s.pc=0xf03376u;break;
  case 0xf03376u: /* jr      n,00F03396 */
   if(condition(&s,24)){pending=1;target=0xf03396u;}
   s.pc=0xf03378u;break;
  case 0xf03378u: /* nop */
   s.pc=0xf0337au;break;
  case 0xf0337au: /* store   r5,(r26) */
   CHECK(wr32(bus,&s,local(s.registers[0][26])?(s.registers[0][26]&~3u):s.registers[0][26],s.registers[0][5]));
   s.pc=0xf0337cu;break;
  case 0xf0337cu: /* addq    $4,r26 */
   s.registers[0][26]=add(&s,s.registers[0][26],4u);
   s.pc=0xf0337eu;break;
  case 0xf0337eu: /* store   r17,(r26) */
   CHECK(wr32(bus,&s,local(s.registers[0][26])?(s.registers[0][26]&~3u):s.registers[0][26],s.registers[0][17]));
   s.pc=0xf03380u;break;
  case 0xf03380u: /* addq    $4,r26 */
   s.registers[0][26]=add(&s,s.registers[0][26],4u);
   s.pc=0xf03382u;break;
  case 0xf03382u: /* storew  r0,(r26) */
   CHECK(wr16(bus,&s,s.registers[0][26],s.registers[0][0]));
   s.pc=0xf03384u;break;
  case 0xf03384u: /* addq    $2,r26 */
   s.registers[0][26]=add(&s,s.registers[0][26],2u);
   s.pc=0xf03386u;break;
  case 0xf03386u: /* storew  r1,(r26) */
   CHECK(wr16(bus,&s,s.registers[0][26],s.registers[0][1]));
   s.pc=0xf03388u;break;
  case 0xf03388u: /* addq    $2,r26 */
   s.registers[0][26]=add(&s,s.registers[0][26],2u);
   s.pc=0xf0338au;break;
  case 0xf0338au: /* storew  r2,(r26) */
   CHECK(wr16(bus,&s,s.registers[0][26],s.registers[0][2]));
   s.pc=0xf0338cu;break;
  case 0xf0338cu: /* addq    $2,r26 */
   s.registers[0][26]=add(&s,s.registers[0][26],2u);
   s.pc=0xf0338eu;break;
  case 0xf0338eu: /* storew  r3,(r26) */
   CHECK(wr16(bus,&s,s.registers[0][26],s.registers[0][3]));
   s.pc=0xf03390u;break;
  case 0xf03390u: /* addq    $2,r26 */
   s.registers[0][26]=add(&s,s.registers[0][26],2u);
   s.pc=0xf03392u;break;
  case 0xf03392u: /* addq    $1,r23 */
   s.registers[0][23]=add(&s,s.registers[0][23],1u);
   s.pc=0xf03394u;break;
  case 0xf03394u: /* addq    $6,r8 */
   s.registers[0][8]=add(&s,s.registers[0][8],6u);
   s.pc=0xf03396u;break;
  case 0xf03396u: /* addq    $1,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],1u);
   s.pc=0xf03398u;break;
  case 0xf03398u: /* addq    $1,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],1u);
   s.pc=0xf0339au;break;
  case 0xf0339au: /* addq    $1,r2 */
   s.registers[0][2]=add(&s,s.registers[0][2],1u);
   s.pc=0xf0339cu;break;
  case 0xf0339cu: /* jump    (r8) */
   if(condition(&s,0)){pending=1;target=s.registers[0][8];}
   s.pc=0xf0339eu;break;
  case 0xf0339eu: /* addq    $1,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],1u);
   s.pc=0xf033a0u;break;
  case 0xf033a0u: /* move    r0,r1 */
   s.registers[0][1]=s.registers[0][0];
   s.pc=0xf033a2u;break;
  case 0xf033a2u: /* move    r3,r2 */
   s.registers[0][2]=s.registers[0][3];
   s.pc=0xf033a4u;break;
  case 0xf033a4u: /* add     r4,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],s.registers[0][4]);
   s.pc=0xf033a6u;break;
  case 0xf033a6u: /* moveq   0,r13 */
   s.registers[0][13]=0u;
   s.pc=0xf033a8u;break;
  case 0xf033a8u: /* add     r4,r2 */
   s.registers[0][2]=add(&s,s.registers[0][2],s.registers[0][4]);
   s.pc=0xf033aau;break;
  case 0xf033aau: /* cmp     r13,r14 */
   (void)sub(&s,s.registers[0][14],s.registers[0][13]);
   s.pc=0xf033acu;break;
  case 0xf033acu: /* jump    z,(r7) */
   if(condition(&s,2)){pending=1;target=s.registers[0][7];}
   s.pc=0xf033aeu;break;
  case 0xf033aeu: /* nop */
   s.pc=0xf033b0u;break;
  case 0xf033b0u: /* move    pc,r16 */
   s.registers[0][16]=0xf033b0u;
   s.pc=0xf033b2u;break;
  case 0xf033b2u: /* jump    (r15) */
   if(condition(&s,0)){pending=1;target=s.registers[0][15];}
   s.pc=0xf033b4u;break;
  case 0xf033b4u: /* addq    $6,r16 */
   s.registers[0][16]=add(&s,s.registers[0][16],6u);
   s.pc=0xf033b6u;break;
  case 0xf033b6u: /* cmp     r9,r5 */
   (void)sub(&s,s.registers[0][5],s.registers[0][9]);
   s.pc=0xf033b8u;break;
  case 0xf033b8u: /* jr      z,00F033D6 */
   if(condition(&s,2)){pending=1;target=0xf033d6u;}
   s.pc=0xf033bau;break;
  case 0xf033bau: /* addq    $1,r13 */
   s.registers[0][13]=add(&s,s.registers[0][13],1u);
   s.pc=0xf033bcu;break;
  case 0xf033bcu: /* store   r5,(r26) */
   CHECK(wr32(bus,&s,local(s.registers[0][26])?(s.registers[0][26]&~3u):s.registers[0][26],s.registers[0][5]));
   s.pc=0xf033beu;break;
  case 0xf033beu: /* addq    $4,r26 */
   s.registers[0][26]=add(&s,s.registers[0][26],4u);
   s.pc=0xf033c0u;break;
  case 0xf033c0u: /* store   r17,(r26) */
   CHECK(wr32(bus,&s,local(s.registers[0][26])?(s.registers[0][26]&~3u):s.registers[0][26],s.registers[0][17]));
   s.pc=0xf033c2u;break;
  case 0xf033c2u: /* addq    $4,r26 */
   s.registers[0][26]=add(&s,s.registers[0][26],4u);
   s.pc=0xf033c4u;break;
  case 0xf033c4u: /* storew  r0,(r26) */
   CHECK(wr16(bus,&s,s.registers[0][26],s.registers[0][0]));
   s.pc=0xf033c6u;break;
  case 0xf033c6u: /* addq    $2,r26 */
   s.registers[0][26]=add(&s,s.registers[0][26],2u);
   s.pc=0xf033c8u;break;
  case 0xf033c8u: /* storew  r1,(r26) */
   CHECK(wr16(bus,&s,s.registers[0][26],s.registers[0][1]));
   s.pc=0xf033cau;break;
  case 0xf033cau: /* addq    $2,r26 */
   s.registers[0][26]=add(&s,s.registers[0][26],2u);
   s.pc=0xf033ccu;break;
  case 0xf033ccu: /* storew  r2,(r26) */
   CHECK(wr16(bus,&s,s.registers[0][26],s.registers[0][2]));
   s.pc=0xf033ceu;break;
  case 0xf033ceu: /* addq    $2,r26 */
   s.registers[0][26]=add(&s,s.registers[0][26],2u);
   s.pc=0xf033d0u;break;
  case 0xf033d0u: /* storew  r3,(r26) */
   CHECK(wr16(bus,&s,s.registers[0][26],s.registers[0][3]));
   s.pc=0xf033d2u;break;
  case 0xf033d2u: /* addq    $2,r26 */
   s.registers[0][26]=add(&s,s.registers[0][26],2u);
   s.pc=0xf033d4u;break;
  case 0xf033d4u: /* addq    $1,r23 */
   s.registers[0][23]=add(&s,s.registers[0][23],1u);
   s.pc=0xf033d6u;break;
  case 0xf033d6u: /* add     r4,r0 */
   s.registers[0][0]=add(&s,s.registers[0][0],s.registers[0][4]);
   s.pc=0xf033d8u;break;
  case 0xf033d8u: /* add     r4,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],s.registers[0][4]);
   s.pc=0xf033dau;break;
  case 0xf033dau: /* add     r4,r2 */
   s.registers[0][2]=add(&s,s.registers[0][2],s.registers[0][4]);
   s.pc=0xf033dcu;break;
  case 0xf033dcu: /* add     r4,r3 */
   s.registers[0][3]=add(&s,s.registers[0][3],s.registers[0][4]);
   s.pc=0xf033deu;break;
  case 0xf033deu: /* jump    (r8) */
   if(condition(&s,0)){pending=1;target=s.registers[0][8];}
   s.pc=0xf033e0u;break;
  case 0xf033e0u: /* addq    $1,r10 */
   s.registers[0][10]=add(&s,s.registers[0][10],1u);
   s.pc=0xf033e2u;break;
  case 0xf033e2u: /* cmp     r9,r19 */
   (void)sub(&s,s.registers[0][19],s.registers[0][9]);
   s.pc=0xf033e4u;break;
  case 0xf033e4u: /* jump    z,(r16) */
   if(condition(&s,2)){pending=1;target=s.registers[0][16];}
   s.pc=0xf033e6u;break;
  case 0xf033e6u: /* movefa  r22,r5 */
   s.registers[0][5]=s.registers[1][22];
   s.pc=0xf033e8u;break;
  case 0xf033e8u: /* cmp     r9,r11 */
   (void)sub(&s,s.registers[0][11],s.registers[0][9]);
   s.pc=0xf033eau;break;
  case 0xf033eau: /* jr      nz,00F033F6 */
   if(condition(&s,1)){pending=1;target=0xf033f6u;}
   s.pc=0xf033ecu;break;
  case 0xf033ecu: /* nop */
   s.pc=0xf033eeu;break;
  case 0xf033eeu: /* loadw   (r19),r11 */
   CHECK(loadw(bus,&s,s.registers[0][19],&v));s.registers[0][11]=v;
   s.pc=0xf033f0u;break;
  case 0xf033f0u: /* addq    $2,r19 */
   s.registers[0][19]=add(&s,s.registers[0][19],2u);
   s.pc=0xf033f2u;break;
  case 0xf033f2u: /* loadw   (r19),r12 */
   CHECK(loadw(bus,&s,s.registers[0][19],&v));s.registers[0][12]=v;
   s.pc=0xf033f4u;break;
  case 0xf033f4u: /* addq    $4,r19 */
   s.registers[0][19]=add(&s,s.registers[0][19],4u);
   s.pc=0xf033f6u;break;
  case 0xf033f6u: /* cmp     r10,r11 */
   (void)sub(&s,s.registers[0][11],s.registers[0][10]);
   s.pc=0xf033f8u;break;
  case 0xf033f8u: /* jump    nz,(r16) */
   if(condition(&s,1)){pending=1;target=s.registers[0][16];}
   s.pc=0xf033fau;break;
  case 0xf033fau: /* movefa  r22,r5 */
   s.registers[0][5]=s.registers[1][22];
   s.pc=0xf033fcu;break;
  case 0xf033fcu: /* btst    $f,r12 */
   s.z=((~s.registers[0][12])>>15)&1u;
   s.pc=0xf033feu;break;
  case 0xf033feu: /* jr      z,00F03404 */
   if(condition(&s,2)){pending=1;target=0xf03404u;}
   s.pc=0xf03400u;break;
  case 0xf03400u: /* move    r9,r11 */
   s.registers[0][11]=s.registers[0][9];
   s.pc=0xf03402u;break;
  case 0xf03402u: /* move    r9,r19 */
   s.registers[0][19]=s.registers[0][9];
   s.pc=0xf03404u;break;
  case 0xf03404u: /* btst    $e,r12 */
   s.z=((~s.registers[0][12])>>14)&1u;
   s.pc=0xf03406u;break;
  case 0xf03406u: /* jump    nz,(r16) */
   if(condition(&s,1)){pending=1;target=s.registers[0][16];}
   s.pc=0xf03408u;break;
  case 0xf03408u: /* move    r9,r5 */
   s.registers[0][5]=s.registers[0][9];
   s.pc=0xf0340au;break;
  case 0xf0340au: /* btst    $c,r12 */
   s.z=((~s.registers[0][12])>>12)&1u;
   s.pc=0xf0340cu;break;
  case 0xf0340cu: /* jump    nz,(r16) */
   if(condition(&s,1)){pending=1;target=s.registers[0][16];}
   s.pc=0xf0340eu;break;
  case 0xf0340eu: /* movefa  r24,r5 */
   s.registers[0][5]=s.registers[1][24];
   s.pc=0xf03410u;break;
  case 0xf03410u: /* btst    $b,r12 */
   s.z=((~s.registers[0][12])>>11)&1u;
   s.pc=0xf03412u;break;
  case 0xf03412u: /* jump    nz,(r16) */
   if(condition(&s,1)){pending=1;target=s.registers[0][16];}
   s.pc=0xf03414u;break;
  case 0xf03414u: /* movefa  r23,r5 */
   s.registers[0][5]=s.registers[1][23];
   s.pc=0xf03416u;break;
  case 0xf03416u: /* btst    $d,r12 */
   s.z=((~s.registers[0][12])>>13)&1u;
   s.pc=0xf03418u;break;
  case 0xf03418u: /* jump    nz,(r16) */
   if(condition(&s,1)){pending=1;target=s.registers[0][16];}
   s.pc=0xf0341au;break;
  case 0xf0341au: /* movefa  r25,r5 */
   s.registers[0][5]=s.registers[1][25];
   s.pc=0xf0341cu;break;
  case 0xf0341cu: /* jump    (r16) */
   if(condition(&s,0)){pending=1;target=s.registers[0][16];}
   s.pc=0xf0341eu;break;
  case 0xf0341eu: /* movefa  r22,r5 */
   s.registers[0][5]=s.registers[1][22];
   s.pc=0xf03420u;break;
default:return BIWN_GPU_ROOM_CONSUMER6E80_BAD_PC;
 }if(delayed){if(pending)return BIWN_GPU_ROOM_CONSUMER6E80_BAD_DELAY;s.pc=resume;}if(s.pc==0xf03440u){*state=s;return BIWN_GPU_ROOM_CONSUMER6E80_OK;}}return BIWN_GPU_ROOM_CONSUMER6E80_WORK_LIMIT;}
