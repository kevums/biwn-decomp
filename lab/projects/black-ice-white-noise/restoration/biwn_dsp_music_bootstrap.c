/* Source-specific static reconstruction by generate_biwn_dsp_music_bootstrap.py.
 * Not recovered original source. See original-DSP comparison evidence. */
#include "biwn_dsp_music_bootstrap.h"
static void zn(struct biwn_dsp_music_bootstrap_state *s,uint32_t v){s->z=v==0;s->n=v>>31;}
static uint32_t add(struct biwn_dsp_music_bootstrap_state *s,uint32_t a,uint32_t b){uint32_t v=a+b;s->c=b>~a;zn(s,v);return v;}
static uint32_t sub(struct biwn_dsp_music_bootstrap_state *s,uint32_t a,uint32_t b){uint32_t v=a-b;s->c=b>a;zn(s,v);return v;}
static int condition(struct biwn_dsp_music_bootstrap_state *s,unsigned code){unsigned f=s->z|(s->c<<1)|(s->n<<2);return !((code&1u)&&(f&1u))&&!((code&2u)&&!(f&1u))&&!((code&4u)&&(f&(2u<<(code>>4))))&&!((code&8u)&&!(f&(2u<<(code>>4))));}
static uint32_t be32(const uint8_t *p){return((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
static void put32(uint8_t *p,uint32_t v){p[0]=(uint8_t)(v>>24);p[1]=(uint8_t)(v>>16);p[2]=(uint8_t)(v>>8);p[3]=(uint8_t)v;}
static int local(uint32_t a){return a>=0xf1b000u&&a<=0xf1cfffu;}
static int rd32(struct biwn_dsp_music_bootstrap_bus *b,struct biwn_dsp_music_bootstrap_state *s,uint32_t a,uint32_t *v){a&=~3u;if(local(a)){*v=be32(s->local_RAM+a-0xf1b000u);return 0;}if(a==0xf1a100u){s->flags=(s->flags&~7u)|s->z|(s->c<<1)|(s->n<<2);*v=s->flags&0xffffc1ffu;return 0;}if(a==0xf1a114u){*v=s->control;return 0;}return b->read32(b->context,a,v)?2:0;}
static int wr32(struct biwn_dsp_music_bootstrap_bus *b,struct biwn_dsp_music_bootstrap_state *s,uint32_t a,uint32_t v){a&=~3u;if(local(a)){put32(s->local_RAM+a-0xf1b000u,v);return 0;}if(a==0xf1a100u){if(v&0x4000u)return 1;s->flags=(v&~8u)|((v&8u)?(s->flags&8u):0);s->z=s->flags&1;s->c=(s->flags>>1)&1;s->n=(s->flags>>2)&1;s->control&=~((s->flags&0x3e00u)>>3);s->control&=~((s->flags&0x20000u)>>1);return 0;}if(a==0xf1a114u){uint32_t mask=0x1f7c0u;s->control=(s->control&mask)|(v&~mask);return 0;}return b->write32(b->context,a,v)?2:0;}
static int wr16(struct biwn_dsp_music_bootstrap_bus *b,struct biwn_dsp_music_bootstrap_state *s,uint32_t a,uint32_t v){(void)s;if(local(a))return 1;return b->write16(b->context,a&~1u,(uint16_t)v)?2:0;}
static int valid(struct biwn_dsp_music_bootstrap_state *s){return s&&s->z<=1&&s->c<=1&&s->n<=1&&!(s->flags&0x4000u);}
#define CHECK(e) do{int status=(e);if(status)return(enum biwn_dsp_music_bootstrap_status)status;}while(0)
enum biwn_dsp_music_bootstrap_status biwn_dsp_music_bootstrap_step(struct biwn_dsp_music_bootstrap_bus *bus,struct biwn_dsp_music_bootstrap_state *state){struct biwn_dsp_music_bootstrap_state s;uint32_t v,target=0;unsigned pending=0,delayed=0;if(!bus||!valid(state)||!bus->read8||!bus->read32||!bus->write32||!bus->write16)return 1;if(!(state->control&1u))return 6;s=*state;
 do{pending=0;if(!delayed&&bus->observe_PC)bus->observe_PC(bus->context,s.pc);s.instructions++;switch(s.pc){
  case 0xf1b000u: /* movei   $f1b030,r29 */
   s.registers[0][29]=0xf1b030u;
   s.pc=0xf1b006u;break;
  case 0xf1b006u: /* jump    (r29) */
   if(condition(&s,0)){pending=1;target=s.registers[0][29];}
   s.pc=0xf1b008u;break;
  case 0xf1b008u: /* nop */
   s.pc=0xf1b00au;break;
  case 0xf1b030u: /* movei   $f1a100,r29 */
   s.registers[0][29]=0xf1a100u;
   s.pc=0xf1b036u;break;
  case 0xf1b036u: /* load    (r29),r30 */
   CHECK(rd32(bus,&s,s.registers[0][29]&~3u,&v));s.registers[0][30]=v;
   s.pc=0xf1b038u;break;
  case 0xf1b038u: /* movei   $f1badc,r25 */
   s.registers[0][25]=0xf1badcu;
   s.pc=0xf1b03eu;break;
  case 0xf1b03eu: /* moveq   0,r0 */
   s.registers[0][0]=0u;
   s.pc=0xf1b040u;break;
  case 0xf1b040u: /* load    (r25),r28 */
   CHECK(rd32(bus,&s,s.registers[0][25]&~3u,&v));s.registers[0][28]=v;
   s.pc=0xf1b042u;break;
  case 0xf1b042u: /* movei   $f1b080,r27 */
   s.registers[0][27]=0xf1b080u;
   s.pc=0xf1b048u;break;
  case 0xf1b048u: /* cmpq    $1,r28 */
   (void)sub(&s,s.registers[0][28],0x1u);
   s.pc=0xf1b04au;break;
  case 0xf1b04au: /* jump    nz,(r27) */
   if(condition(&s,1)){pending=1;target=s.registers[0][27];}
   s.pc=0xf1b04cu;break;
  case 0xf1b04cu: /* nop */
   s.pc=0xf1b04eu;break;
  case 0xf1b080u: /* movei   $f1b04e,r27 */
   s.registers[0][27]=0xf1b04eu;
   s.pc=0xf1b086u;break;
  case 0xf1b086u: /* cmpq    $2,r28 */
   (void)sub(&s,s.registers[0][28],0x2u);
   s.pc=0xf1b088u;break;
  case 0xf1b088u: /* jump    nz,(r27) */
   if(condition(&s,1)){pending=1;target=s.registers[0][27];}
   s.pc=0xf1b08au;break;
  case 0xf1b08au: /* nop */
   s.pc=0xf1b08cu;break;
  case 0xf1b08cu: /* bset    $9,r30 */
   s.registers[0][30]|=(1u<<9);
   zn(&s,s.registers[0][30]);
   s.pc=0xf1b08eu;break;
  case 0xf1b08eu: /* bset    $a,r30 */
   s.registers[0][30]|=(1u<<10);
   zn(&s,s.registers[0][30]);
   s.pc=0xf1b090u;break;
  case 0xf1b090u: /* bset    $b,r30 */
   s.registers[0][30]|=(1u<<11);
   zn(&s,s.registers[0][30]);
   s.pc=0xf1b092u;break;
  case 0xf1b092u: /* bclr    $3,r30 */
   s.registers[0][30]&=~(1u<<3);
   zn(&s,s.registers[0][30]);
   s.pc=0xf1b094u;break;
  case 0xf1b094u: /* bset    $4,r30 */
   s.registers[0][30]|=(1u<<4);
   zn(&s,s.registers[0][30]);
   s.pc=0xf1b096u;break;
  case 0xf1b096u: /* bclr    $5,r30 */
   s.registers[0][30]&=~(1u<<5);
   zn(&s,s.registers[0][30]);
   s.pc=0xf1b098u;break;
  case 0xf1b098u: /* bclr    $6,r30 */
   s.registers[0][30]&=~(1u<<6);
   zn(&s,s.registers[0][30]);
   s.pc=0xf1b09au;break;
  case 0xf1b09au: /* bclr    $e,r30 */
   s.registers[0][30]&=~(1u<<14);
   zn(&s,s.registers[0][30]);
   s.pc=0xf1b09cu;break;
  case 0xf1b09cu: /* addq    $4,r31 */
   s.registers[0][31]=add(&s,s.registers[0][31],4u);
   s.pc=0xf1b09eu;break;
  case 0xf1b09eu: /* store   r30,(r29) */
   CHECK(wr32(bus,&s,local(s.registers[0][29])?(s.registers[0][29]&~3u):s.registers[0][29],s.registers[0][30]));
   s.pc=0xf1b0a0u;break;
  case 0xf1b0a0u: /* nop */
   s.pc=0xf1b0a2u;break;
  case 0xf1b0a2u: /* nop */
   s.pc=0xf1b0a4u;break;
  case 0xf1b0a4u: /* addq    $4,r25 */
   s.registers[0][25]=add(&s,s.registers[0][25],4u);
   s.pc=0xf1b0a6u;break;
  case 0xf1b0a6u: /* load    (r25),r1 */
   CHECK(rd32(bus,&s,s.registers[0][25]&~3u,&v));s.registers[0][1]=v;
   s.pc=0xf1b0a8u;break;
  case 0xf1b0a8u: /* load    (r1),r2 */
   CHECK(rd32(bus,&s,s.registers[0][1]&~3u,&v));s.registers[0][2]=v;
   s.pc=0xf1b0aau;break;
  case 0xf1b0aau: /* addq    $4,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],4u);
   s.pc=0xf1b0acu;break;
  case 0xf1b0acu: /* load    (r1),r3 */
   CHECK(rd32(bus,&s,s.registers[0][1]&~3u,&v));s.registers[0][3]=v;
   s.pc=0xf1b0aeu;break;
  case 0xf1b0aeu: /* addq    $4,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],4u);
   s.pc=0xf1b0b0u;break;
  case 0xf1b0b0u: /* load    (r1),r4 */
   CHECK(rd32(bus,&s,s.registers[0][1]&~3u,&v));s.registers[0][4]=v;
   s.pc=0xf1b0b2u;break;
  case 0xf1b0b2u: /* addq    $4,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],4u);
   s.pc=0xf1b0b4u;break;
  case 0xf1b0b4u: /* shrq    $2,r4 */
   s.c=s.registers[0][4]&1u;s.registers[0][4]=s.registers[0][4]>>2;zn(&s,s.registers[0][4]);
   s.pc=0xf1b0b6u;break;
  case 0xf1b0b6u: /* load    (r2),r5 */
   CHECK(rd32(bus,&s,s.registers[0][2]&~3u,&v));s.registers[0][5]=v;
   s.pc=0xf1b0b8u;break;
  case 0xf1b0b8u: /* subq    $1,r4 */
   s.registers[0][4]=sub(&s,s.registers[0][4],1u);
   s.pc=0xf1b0bau;break;
  case 0xf1b0bau: /* store   r5,(r3) */
   CHECK(wr32(bus,&s,local(s.registers[0][3])?(s.registers[0][3]&~3u):s.registers[0][3],s.registers[0][5]));
   s.pc=0xf1b0bcu;break;
  case 0xf1b0bcu: /* addqt   $4,r2 */
   s.registers[0][2]+=4u;
   s.pc=0xf1b0beu;break;
  case 0xf1b0beu: /* jr      nz,00F1B0B6 */
   if(condition(&s,1)){pending=1;target=0xf1b0b6u;}
   s.pc=0xf1b0c0u;break;
  case 0xf1b0c0u: /* addqt   $4,r3 */
   s.registers[0][3]+=4u;
   s.pc=0xf1b0c2u;break;
  case 0xf1b0c2u: /* movei   $f1bb0c,r6 */
   s.registers[0][6]=0xf1bb0cu;
   s.pc=0xf1b0c8u;break;
  case 0xf1b0c8u: /* load    (r1),r7 */
   CHECK(rd32(bus,&s,s.registers[0][1]&~3u,&v));s.registers[0][7]=v;
   s.pc=0xf1b0cau;break;
  case 0xf1b0cau: /* store   r7,(r6) */
   CHECK(wr32(bus,&s,local(s.registers[0][6])?(s.registers[0][6]&~3u):s.registers[0][6],s.registers[0][7]));
   s.pc=0xf1b0ccu;break;
  case 0xf1b0ccu: /* addq    $4,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],4u);
   s.pc=0xf1b0ceu;break;
  case 0xf1b0ceu: /* movei   $f10002,r8 */
   s.registers[0][8]=0xf10002u;
   s.pc=0xf1b0d4u;break;
  case 0xf1b0d4u: /* load    (r1),r9 */
   CHECK(rd32(bus,&s,s.registers[0][1]&~3u,&v));s.registers[0][9]=v;
   s.pc=0xf1b0d6u;break;
  case 0xf1b0d6u: /* storew  r9,(r8) */
   CHECK(wr16(bus,&s,s.registers[0][8],s.registers[0][9]));
   s.pc=0xf1b0d8u;break;
  case 0xf1b0d8u: /* addq    $4,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],4u);
   s.pc=0xf1b0dau;break;
  case 0xf1b0dau: /* movei   $f10000,r10 */
   s.registers[0][10]=0xf10000u;
   s.pc=0xf1b0e0u;break;
  case 0xf1b0e0u: /* load    (r1),r11 */
   CHECK(rd32(bus,&s,s.registers[0][1]&~3u,&v));s.registers[0][11]=v;
   s.pc=0xf1b0e2u;break;
  case 0xf1b0e2u: /* storew  r11,(r10) */
   CHECK(wr16(bus,&s,s.registers[0][10],s.registers[0][11]));
   s.pc=0xf1b0e4u;break;
  case 0xf1b0e4u: /* addq    $4,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],4u);
   s.pc=0xf1b0e6u;break;
  case 0xf1b0e6u: /* addq    $4,r25 */
   s.registers[0][25]=add(&s,s.registers[0][25],4u);
   s.pc=0xf1b0e8u;break;
  case 0xf1b0e8u: /* addq    $8,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],8u);
   s.pc=0xf1b0eau;break;
  case 0xf1b0eau: /* load    (r25),r12 */
   CHECK(rd32(bus,&s,s.registers[0][25]&~3u,&v));s.registers[0][12]=v;
   s.pc=0xf1b0ecu;break;
  case 0xf1b0ecu: /* shlq    $2,r12 */
   s.c=s.registers[0][12]>>31;s.registers[0][12]=s.registers[0][12]<<2;zn(&s,s.registers[0][12]);
   s.pc=0xf1b0eeu;break;
  case 0xf1b0eeu: /* add     r12,r1 */
   s.registers[0][1]=add(&s,s.registers[0][1],s.registers[0][12]);
   s.pc=0xf1b0f0u;break;
  case 0xf1b0f0u: /* movei   $f1bb08,r13 */
   s.registers[0][13]=0xf1bb08u;
   s.pc=0xf1b0f6u;break;
  case 0xf1b0f6u: /* load    (r1),r14 */
   CHECK(rd32(bus,&s,s.registers[0][1]&~3u,&v));s.registers[0][14]=v;
   s.pc=0xf1b0f8u;break;
  case 0xf1b0f8u: /* store   r14,(r13) */
   CHECK(wr32(bus,&s,local(s.registers[0][13])?(s.registers[0][13]&~3u):s.registers[0][13],s.registers[0][14]));
   s.pc=0xf1b0fau;break;
  case 0xf1b0fau: /* movei   $f1bd10,r15 */
   s.registers[0][15]=0xf1bd10u;
   s.pc=0xf1b100u;break;
  case 0xf1b100u: /* movei   $fffffffc,r16 */
   s.registers[0][16]=0xfffffffcu;
   s.pc=0xf1b106u;break;
  case 0xf1b106u: /* movei   $50,r17 */
   s.registers[0][17]=0x50u;
   s.pc=0xf1b10cu;break;
  case 0xf1b10cu: /* load    (r15),r18 */
   CHECK(rd32(bus,&s,s.registers[0][15]&~3u,&v));s.registers[0][18]=v;
   s.pc=0xf1b10eu;break;
  case 0xf1b10eu: /* cmpq    $0,r18 */
   (void)sub(&s,s.registers[0][18],0x0u);
   s.pc=0xf1b110u;break;
  case 0xf1b110u: /* jr      z,00F1B11A */
   if(condition(&s,2)){pending=1;target=0xf1b11au;}
   s.pc=0xf1b112u;break;
  case 0xf1b112u: /* nop */
   s.pc=0xf1b114u;break;
  case 0xf1b114u: /* store   r16,(r15) */
   CHECK(wr32(bus,&s,local(s.registers[0][15])?(s.registers[0][15]&~3u):s.registers[0][15],s.registers[0][16]));
   s.pc=0xf1b116u;break;
  case 0xf1b116u: /* jr      00F1B10C */
   if(condition(&s,0)){pending=1;target=0xf1b10cu;}
   s.pc=0xf1b118u;break;
  case 0xf1b118u: /* add     r17,r15 */
   s.registers[0][15]=add(&s,s.registers[0][15],s.registers[0][17]);
   s.pc=0xf1b11au;break;
  case 0xf1b11au: /* movei   $f1b148,r27 */
   s.registers[0][27]=0xf1b148u;
   s.pc=0xf1b120u;break;
  case 0xf1b120u: /* subq    $8,r25 */
   s.registers[0][25]=sub(&s,s.registers[0][25],8u);
   s.pc=0xf1b122u;break;
  case 0xf1b122u: /* jump    (r27) */
   if(condition(&s,0)){pending=1;target=s.registers[0][27];}
   s.pc=0xf1b124u;break;
  case 0xf1b124u: /* store   r0,(r25) */
   CHECK(wr32(bus,&s,local(s.registers[0][25])?(s.registers[0][25]&~3u):s.registers[0][25],s.registers[0][0]));
   s.pc=0xf1b126u;break;
  case 0xf1b126u: /* movei   $f1b010,r31 */
   s.registers[0][31]=0xf1b010u;
   s.pc=0xf1b12cu;break;
  case 0xf1b12cu: /* moveta  r31,r31 */
   s.registers[1][31]=s.registers[0][31];
   s.pc=0xf1b12eu;break;
  case 0xf1b12eu: /* movei   $f1a100,r29 */
   s.registers[0][29]=0xf1a100u;
   s.pc=0xf1b134u;break;
  case 0xf1b134u: /* load    (r29),r30 */
   CHECK(rd32(bus,&s,s.registers[0][29]&~3u,&v));s.registers[0][30]=v;
   s.pc=0xf1b136u;break;
  case 0xf1b136u: /* bset    $4,r30 */
   s.registers[0][30]|=(1u<<4);
   zn(&s,s.registers[0][30]);
   s.pc=0xf1b138u;break;
  case 0xf1b138u: /* bclr    $5,r30 */
   s.registers[0][30]&=~(1u<<5);
   zn(&s,s.registers[0][30]);
   s.pc=0xf1b13au;break;
  case 0xf1b13au: /* bclr    $6,r30 */
   s.registers[0][30]&=~(1u<<6);
   zn(&s,s.registers[0][30]);
   s.pc=0xf1b13cu;break;
  case 0xf1b13cu: /* bclr    $e,r30 */
   s.registers[0][30]&=~(1u<<14);
   zn(&s,s.registers[0][30]);
   s.pc=0xf1b13eu;break;
  case 0xf1b13eu: /* store   r30,(r29) */
   CHECK(wr32(bus,&s,local(s.registers[0][29])?(s.registers[0][29]&~3u):s.registers[0][29],s.registers[0][30]));
   s.pc=0xf1b140u;break;
  case 0xf1b140u: /* nop */
   s.pc=0xf1b142u;break;
  case 0xf1b142u: /* nop */
   s.pc=0xf1b144u;break;
default:return BIWN_DSP_MUSIC_BOOTSTRAP_BAD_PC;
 }if(delayed){if(pending)return BIWN_DSP_MUSIC_BOOTSTRAP_BAD_DELAY;s.pc=target;break;}delayed=pending;
 }while(delayed);*state=s;return 0;}
enum biwn_dsp_music_bootstrap_status biwn_dsp_music_bootstrap_run(struct biwn_dsp_music_bootstrap_bus *bus,struct biwn_dsp_music_bootstrap_state *state,uint32_t budget,uint32_t stopPC){struct biwn_dsp_music_bootstrap_state s;int status;if(!bus||!valid(state)||!budget||!bus->read8||!bus->read32||!bus->write32||!bus->write16||(stopPC!=0xf1b144u&&stopPC!=0xf1b148u))return 1;s=*state;while(budget--){if(s.pc==stopPC){*state=s;return 0;}status=biwn_dsp_music_bootstrap_step(bus,&s);if(status)return(enum biwn_dsp_music_bootstrap_status)status;}return 4;}
enum biwn_dsp_music_bootstrap_status biwn_dsp_music_bootstrap_cpu_interrupt(struct biwn_dsp_music_bootstrap_state *state){struct biwn_dsp_music_bootstrap_state s;uint32_t sp;if(!valid(state)||state->pc!=0xf1b144u||!(state->control&1u)||(state->flags&8u)||!(state->flags&0x10u))return 1;s=*state;s.control|=0x40u;s.flags|=8u;sp=s.registers[0][31]-4u;if(!local(sp)||sp>0xf1cffcu)return 1;s.registers[0][31]=sp;s.registers[0][30]=s.pc-2u;put32(s.local_RAM+(sp&~3u)-0xf1b000u,s.pc-2u);s.pc=s.registers[0][30]=0xf1b000u;*state=s;return 0;}
